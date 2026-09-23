"""P012 independent synthetic qualification; never points at live host settings."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

ARGS = HOST = INSTALLER = BASELINE_INSTALLER = None
SECRET = 'SYNTHETIC_RAW_CONTENT_NOT_FOR_STORAGE'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def module(name, path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

class Qualification(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='p012-independent-')
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.db=self.root/'observer.sqlite3'
        HOST.init_db(self.db)
        self.install_number=0

    def rows(self,sql,values=()):
        with closing(sqlite3.connect(self.db)) as conn:
            return conn.execute(sql,values).fetchall()

    def counts(self):
        return tuple(self.rows('SELECT COUNT(*) FROM '+name)[0][0] for name in ('sessions','events','measurements'))

    def ingest(self,host,raw,event='UserPromptSubmit',**values):
        payload=dict(session_id=raw,hook_event_name=event,**values)
        return HOST.ingest_hook(self.db,host,payload,auto_enroll=True)

    def runtime_hashes(self,plan):
        return {name:sha(Path(plan['runtime'])/name) for name in INSTALLER.MODULES}

    def setup_installation(self):
        self.install_number+=1
        base=self.root/('installation-'+str(self.install_number));base.mkdir()
        targets={host:base/(host+'.json') for host in ('codex','claude')}
        initial={'unrelated_option':{'preserve':[1,'value']},'hooks':{'IndependentEvent':[{'hooks':[{'type':'command','command':'unrelated-command'}]}],'PreToolUse':[{'matcher':'special-tool','hooks':[{'type':'command','command':'other-command','timeout':7}]}]}}
        for path in targets.values():path.write_text(json.dumps(initial),encoding='utf-8')
        private=base/'private'
        previous=BASELINE_INSTALLER.prepare(private,self.db,targets,python=sys.executable)
        BASELINE_INSTALLER.apply(previous,base/'old-backups')
        # Real unrelated additions may share a wrapper with the prior handler.
        for host,path in targets.items():
            settings=json.loads(path.read_text(encoding='utf-8'))
            for entry in settings['hooks']['SessionStart']:
                if any(h.get('command')==next(c['command'] for c in previous['changes'] if c['host']==host) for h in entry['hooks']):
                    entry['hooks'].append({'type':'command','command':'shared-unrelated-command','timeout':11})
            path.write_text(json.dumps(settings,indent=2)+'\n',encoding='utf-8')
        return base,private,targets,previous

    def prepare_upgrade(self,private,targets,previous):
        return INSTALLER.prepare(private,self.db,targets,python=sys.executable,auto_enroll=True,previous_plan=previous)

    def test_C01_ongoing_event_namespaces_unknown_measurements(self):
        for host in ('codex','claude'):
            self.assertEqual(self.ingest(host,'same-id','PostToolUse',tool_use_id='tool-1')['status'],'recorded')
        self.assertEqual(self.counts(),(2,2,6))
        self.assertEqual({row[0] for row in self.rows('SELECT session_id FROM sessions')},{'codex:same-id','claude:same-id'})
        self.assertTrue(all(value is None for (value,) in self.rows('SELECT value FROM measurements')))
        for host in ('codex','claude'):
            report=HOST.report(self.db,host,'same-id')
            self.assertIsNone(report['cost_usd']);self.assertIsNone(report['tokens']);self.assertIsNone(report['human_minutes'])
            self.assertEqual(report['coverage']['status'],'incomplete')
            self.assertEqual(report['config']['capture_scope'],'all-local-from-first-observed-event')

    def test_C02_concurrent_idempotence(self):
        def arrival(_):
            return self.ingest('codex','concurrent',prompt_id='stable-prompt')['status']
        with ThreadPoolExecutor(max_workers=6) as pool:
            states=list(pool.map(arrival,range(12)))
        self.assertEqual(states.count('recorded'),1)
        self.assertEqual(states.count('duplicate'),11)
        self.assertEqual(self.counts(),(1,1,3))

    def test_C03_explicit_and_one_shot_precedence(self):
        config={'host':'codex','workflow':'explicit-fixture'}
        HOST.register(self.db,'codex','existing','explicit-task',config)
        before=self.rows('SELECT * FROM sessions WHERE session_id=?',('codex:existing',))
        self.ingest('codex','existing',prompt_id='existing-event')
        self.assertEqual(before,self.rows('SELECT * FROM sessions WHERE session_id=?',('codex:existing',)))
        cwd=str(self.root/'exact-cwd')
        HOST.arm(self.db,'codex',cwd,'armed-task',config)
        self.ingest('claude','wrong-host','SessionStart',cwd=cwd)
        self.ingest('codex','wrong-directory','SessionStart',cwd=str(self.root/'other-cwd'))
        self.assertEqual(self.rows('SELECT consumed_session_id FROM pending_enrollments'),[(None,)])
        self.ingest('codex','armed','SessionStart',cwd=cwd)
        self.assertEqual(self.rows('SELECT consumed_session_id FROM pending_enrollments'),[('codex:armed',)])
        task,stored=self.rows('SELECT task_id,config_json FROM sessions WHERE session_id=?',('codex:armed',))[0]
        self.assertEqual(task,'armed-task');self.assertEqual(json.loads(stored)['workflow'],'explicit-fixture')
        self.assertEqual(json.loads(stored)['capture_scope'],'next-session-from-enrollment')
        self.ingest('codex','later','SessionStart',cwd=cwd)
        self.assertNotEqual(self.rows('SELECT task_id FROM sessions WHERE session_id=?',('codex:later',))[0][0],'armed-task')
        self.assertEqual(self.rows('SELECT COUNT(*) FROM pending_enrollments WHERE consumed_session_id IS NOT NULL')[0][0],1)

    def test_C04_reject_before_enrollment_and_privacy(self):
        invalid=[{'session_id':'unsupported','hook_event_name':'UnknownEvent'}, {'session_id':'bad\nidentity','hook_event_name':'SessionStart'}, {'session_id':'bad-meta','hook_event_name':'SessionStart','tool_name':{'not':'text'}}, {'session_id':'oversize','hook_event_name':'SessionStart','prompt':'x'*(HOST.observer.MAX_PAYLOAD+1)}, {'session_id':'nonfinite','hook_event_name':'SessionStart','tool_input':float('nan')}]
        for payload in invalid:
            with self.subTest(kind=payload['session_id']):
                before=self.counts()
                try: HOST.ingest_hook(self.db,'codex',payload,auto_enroll=True)
                except (ValueError,TypeError): pass
                self.assertEqual(self.counts(),before)
        payload={'session_id':'private-fields','hook_event_name':'UserPromptSubmit','prompt_id':'privacy-prompt','prompt':SECRET,'tool_input':{'raw':SECRET},'tool_response':SECRET,'cwd':str(self.root/SECRET)}
        HOST.ingest_hook(self.db,'codex',payload,auto_enroll=True)
        serialized=json.dumps(self.rows('SELECT task_id,config_json FROM sessions')+self.rows('SELECT metadata_json FROM events'))
        self.assertNotIn(SECRET,serialized)
        self.assertNotIn(str(self.root),serialized)
        self.assertEqual(self.counts(),(1,1,3))

    def test_C05_manual_mode_core_identity_and_silent_cli(self):
        self.assertEqual(sha(ARGS.candidate_tools/'observer.py'),sha(ARGS.baseline_tools/'observer.py'))
        payload={'session_id':'manual-unregistered','hook_event_name':'UserPromptSubmit','prompt_id':'manual-prompt'}
        self.assertEqual(HOST.ingest_hook(self.db,'codex',payload)['status'],'ignored')
        self.assertEqual(self.counts(),(0,0,0))
        command=[sys.executable,'-B',str(ARGS.candidate_tools/'observer_host.py'),'--db',str(self.db),'--host','codex','hook']
        for enabled in (False,True):
            proc=subprocess.run(command+(['--auto-enroll'] if enabled else []),input=json.dumps(payload).encode(),capture_output=True,timeout=15)
            self.assertEqual(proc.returncode,0);self.assertEqual(proc.stdout,b'');self.assertEqual(proc.stderr,b'')
            self.assertEqual(self.counts(),(1,1,3) if enabled else (0,0,0))

    def test_C06_exact_upgrade_and_preservation(self):
        base,private,targets,previous=self.setup_installation()
        old=self.runtime_hashes(previous);db_hash=sha(self.db)
        before={host:path.read_bytes() for host,path in targets.items()}
        plan=self.prepare_upgrade(private,targets,previous)
        self.assertNotEqual(plan['runtime'],previous['runtime'])
        for change in plan['changes']:
            host=change['host']; prior=next(c for c in previous['changes'] if c['host']==host)
            before_json=json.loads(before[host]); after=json.loads(change['after_utf8'])
            self.assertEqual(before_json['unrelated_option'],after['unrelated_option'])
            self.assertEqual(before_json['hooks']['IndependentEvent'],after['hooks']['IndependentEvent'])
            self.assertEqual(before_json['hooks']['PreToolUse'][0],after['hooks']['PreToolUse'][0])
            for event in INSTALLER.EVENTS[host]:
                handlers=[h for entry in after['hooks'][event] for h in entry['hooks']]
                old_args=None if host=='codex' else next(h.get('args') for entry in json.loads(prior['after_utf8'])['hooks'][event] for h in entry['hooks'] if h['command']==prior['command'])
                self.assertFalse(any(h.get('command')==prior['command'] and h.get('args')==old_args for h in handlers))
                enabled=[h for h in handlers if '--auto-enroll' in h.get('command','') or '--auto-enroll' in h.get('args',[])]
                self.assertEqual(len(enabled),1)
            shared=next(entry for entry in after['hooks']['SessionStart'] if any(h.get('command')=='shared-unrelated-command' for h in entry['hooks']))
            self.assertIn({'type':'command','command':'shared-unrelated-command','timeout':11},shared['hooks'])
        INSTALLER.apply(plan,base/'new-backups')
        for change in plan['changes']:
            self.assertEqual(targets[change['host']].read_bytes(),change['after_utf8'].encode())
            backup=base/'new-backups'/(change['host']+'-'+change['before_sha256']+'.json')
            self.assertEqual(backup.read_bytes(),before[change['host']])
        self.assertEqual(self.runtime_hashes(previous),old);self.assertEqual(sha(self.db),db_hash)
        fresh={host:base/('manual-'+host+'.json') for host in targets}
        manual=INSTALLER.prepare(private,self.db,fresh,python=sys.executable)
        self.assertTrue(all('--auto-enroll' not in c['after_utf8'] for c in manual['changes']))

    def test_C07_unsafe_prior_replacement_refused(self):
        for alteration in ('missing','modified','duplicate','matcher','wrapper_note'):
            with self.subTest(alteration=alteration):
                base,private,targets,previous=self.setup_installation()
                path=targets['codex']; settings=json.loads(path.read_text(encoding='utf-8'))
                event='PreToolUse' if alteration=='matcher' else 'SessionStart'
                entry=next(e for e in settings['hooks'][event] if any(h.get('command')==previous['changes'][0]['command'] for h in e['hooks']))
                index=next(i for i,h in enumerate(entry['hooks']) if h.get('command')==previous['changes'][0]['command'])
                if alteration=='missing': del entry['hooks'][index]
                elif alteration=='modified': entry['hooks'][index]['command']+=' --unrecognized-change'
                elif alteration=='duplicate': entry['hooks'].append(copy.deepcopy(entry['hooks'][index]))
                elif alteration=='matcher': entry['matcher']='changed-restriction'
                else: entry['preserve_wrapper_note']='unsupported-wrapper-value'
                path.write_text(json.dumps(settings),encoding='utf-8')
                before={host:p.read_bytes() for host,p in targets.items()};old=self.runtime_hashes(previous)
                with self.assertRaises((ValueError,TypeError)):self.prepare_upgrade(private,targets,previous)
                self.assertEqual({host:p.read_bytes() for host,p in targets.items()},before)
                self.assertEqual(self.runtime_hashes(previous),old)

    def test_C08_apply_preconditions_and_frozen_runtime(self):
        for alteration in ('settings','prepared','runtime','backup'):
            with self.subTest(alteration=alteration):
                base,private,targets,previous=self.setup_installation()
                old=self.runtime_hashes(previous);plan=self.prepare_upgrade(private,targets,previous)
                backups=base/'new-backups'
                if alteration=='settings': targets['claude'].write_text('{"concurrent_change":true}',encoding='utf-8')
                elif alteration=='prepared': plan['changes'][-1]['after_utf8']+=' '
                elif alteration=='runtime': (Path(plan['runtime'])/'observer_host.py').write_text('# tampered fixture\n',encoding='utf-8')
                else:
                    backups.mkdir();change=plan['changes'][-1]
                    (backups/(change['host']+'-'+change['before_sha256']+'.json')).write_bytes(b'incorrect prior backup')
                before={host:p.read_bytes() for host,p in targets.items()}
                with self.assertRaises((ValueError,TypeError)):INSTALLER.apply(plan,backups)
                self.assertEqual({host:p.read_bytes() for host,p in targets.items()},before)
                self.assertEqual(self.runtime_hashes(previous),old)

def main():
    global ARGS,HOST,INSTALLER,BASELINE_INSTALLER
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate-tools',required=True,type=Path)
    parser.add_argument('--baseline-tools',required=True,type=Path)
    parser.add_argument('--result',required=True,type=Path)
    parser.add_argument('--private-log',required=True,type=Path)
    ARGS=parser.parse_args()
    ARGS.candidate_tools=ARGS.candidate_tools.resolve();ARGS.baseline_tools=ARGS.baseline_tools.resolve()
    HOST=module('candidate_observer_host',ARGS.candidate_tools/'observer_host.py')
    INSTALLER=module('candidate_observer_install',ARGS.candidate_tools/'observer_install.py')
    BASELINE_INSTALLER=module('baseline_observer_install',ARGS.baseline_tools/'observer_install.py')
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Qualification))
    traces=[{'case':test.id(),'trace':trace} for test,trace in result.failures+result.errors]
    failed={test.id().split('.')[-1].split(' ')[0] for test,_ in result.failures+result.errors}
    cases=[{'case':name.split('_',2)[1],'passed':name not in failed} for name in unittest.defaultTestLoader.getTestCaseNames(Qualification)]
    summary={'schema_version':1,'kind':'independent_auto_enrollment_qualification','accepted':result.wasSuccessful(),'groups':len(cases),'passed_groups':sum(c['passed'] for c in cases),'failures':len(result.failures),'errors':len(result.errors),'cases':cases,'candidate_hashes':{name:sha(ARGS.candidate_tools/name) for name in ('observer.py','observer_host.py','observer_install.py','contact_metrics.py')},'probe_sha256':sha(Path(__file__)),'scope':'Synthetic temporary databases and host settings only; actual host CLI and installer functions. No live installation, host trust approval, native application reload, model call or completeness claim.'}
    ARGS.result.write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    ARGS.private_log.write_text(json.dumps({'traces':traces},indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary))
    return 0 if result.wasSuccessful() else 1

if __name__=='__main__':
    raise SystemExit(main())
