"""Portable P011 audit probes. Uses synthetic SQLite data; never real task transcripts."""
from __future__ import annotations
import argparse
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

SCHEMA = """
CREATE TABLE sessions(session_id TEXT PRIMARY KEY,task_id TEXT NOT NULL,enrolled_utc TEXT NOT NULL,collection_mode TEXT NOT NULL,config_json TEXT NOT NULL,collector_sha256 TEXT NOT NULL);
CREATE TABLE events(id INTEGER PRIMARY KEY,session_id TEXT,event_name TEXT,received_utc TEXT,event_identity TEXT UNIQUE,dedupe_status TEXT,metadata_json TEXT,payload_sha256 TEXT);
CREATE TABLE measurements(session_id TEXT,name TEXT,value REAL,reason TEXT,PRIMARY KEY(session_id,name));
CREATE TABLE outcomes(id INTEGER PRIMARY KEY,session_id TEXT,recorded_utc TEXT,artifact_hash TEXT,check_hash TEXT,evaluator TEXT,evidence TEXT,outcome TEXT);
"""
CONTACTS = """
CREATE TABLE contact_labels(id INTEGER PRIMARY KEY,session_id TEXT,event_id INTEGER,revision INTEGER,label TEXT,actor TEXT,source TEXT,recorded_utc TEXT,human_minutes REAL,minutes_basis TEXT,UNIQUE(event_id,revision));
CREATE TABLE contact_resolutions(id INTEGER PRIMARY KEY,session_id TEXT,state TEXT,basis TEXT,actor TEXT,source TEXT,event_id INTEGER,evidence TEXT,recorded_utc TEXT);
"""
STAMP = '2026-01-01T00:00:00Z'
SECRET = 'PRIVATE_FIXTURE_MARKER'
ARGS = None

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='p011-probe-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.db = self.root / 'observations.sqlite3'
        self.selection = self.root / 'selection.json'
        with closing(sqlite3.connect(self.db)) as conn, conn:
            conn.executescript(SCHEMA + CONTACTS)

    def sql(self, statement, values=()):
        with closing(sqlite3.connect(self.db)) as conn, conn:
            return conn.execute(statement, values).lastrowid

    def sid(self, number):
        return 'codex:' + SECRET + '-session-' + str(number)

    def enroll(self, number):
        sid = self.sid(number)
        self.sql('INSERT INTO sessions VALUES (?,?,?,?,?,?)',
                 (sid, SECRET+'-task', STAMP, 'observational', json.dumps({'workflow': SECRET}), 'a'*64))
        return sid

    def measure(self, sid, value=None):
        for name in ('tokens', 'cost_usd', 'human_minutes'):
            self.sql('INSERT INTO measurements VALUES (?,?,?,?)', (sid, name, value, 'scope not established'))

    def event(self, sid, name='UserPromptSubmit'):
        return self.sql('INSERT INTO events(session_id,event_name,received_utc,event_identity,dedupe_status,metadata_json,payload_sha256) VALUES (?,?,?,?,?,?,?)',
                        (sid, name, STAMP, None, 'unknown', json.dumps({'source':SECRET}), 'b'*64))

    def label(self, sid, event, label, revision=1, minutes=None):
        return self.sql('INSERT INTO contact_labels(session_id,event_id,revision,label,actor,source,recorded_utc,human_minutes,minutes_basis) VALUES (?,?,?,?,?,?,?,?,?)',
                        (sid, event, revision, label, 'auditor', SECRET+'-controller-attestation', STAMP, minutes, 'reported' if minutes is not None else None))

    def resolution(self, sid, event, state):
        return self.sql('INSERT INTO contact_resolutions(session_id,state,basis,actor,source,event_id,evidence,recorded_utc) VALUES (?,?,?,?,?,?,?,?)',
                        (sid, state, 'user_reported', 'auditor', SECRET, event, SECRET+'-user-confirmation', STAMP))

    def run_audit(self, ids, controller=None, extra=(), expected=0, db=None):
        selection = {'sessions':[{'session_id':sid,'title':SECRET+'-title','status':SECRET+'-status'} for sid in ids]}
        if controller is not None:
            selection['controller_session_id'] = controller
        self.selection.write_text(json.dumps(selection), encoding='utf-8')
        db = db or self.db
        before_db = db.read_bytes() if db.exists() else None
        before_selection = self.selection.read_bytes()
        proc = subprocess.run([sys.executable,'-B',str(ARGS.candidate),'--db',str(db),'--selection',str(self.selection),*map(str,extra)],capture_output=True,timeout=15)
        self.assertEqual(proc.returncode,expected,proc.stderr.decode('utf-8','replace'))
        self.assertEqual(db.read_bytes() if db.exists() else None,before_db,'Source database changed or was created')
        self.assertEqual(self.selection.read_bytes(),before_selection,'Selection changed')
        if expected:
            self.assertNotIn(b'"kind": "observer_coverage_audit"',proc.stdout)
            return proc
        result = json.loads(proc.stdout)
        self.assertEqual(result['kind'],'observer_coverage_audit')
        self.assertEqual(result['selection_count'],len(ids))
        self.assertFalse(result['whole_task_accounting_complete'])
        self.assertIsNone(result['whole_task_cost_usd'])
        self.assertNotIn(SECRET,proc.stdout.decode('utf-8'))
        self.assertNotIn(str(self.root),proc.stdout.decode('utf-8'))
        self.assertEqual([item['alias'] for item in result['selected']],['task-%02d'%(i+1) for i in range(len(ids))])
        for item in result['selected']+([result['controller']] if controller is not None else []):
            self.assertFalse(item['capture_complete'])
            self.assertIsNone(item['whole_task_cost_usd'])
            if item.get('contacts') is not None:
                self.assertIsNone(item['contacts']['human_corrections'])
                self.assertEqual(item['contacts']['human_origin'],'not_established')
        return result

    def test_C01_unregistered(self):
        r=self.run_audit([self.sid(1),self.sid(2)],self.sid(3))
        self.assertEqual(r['database_summary']['sessions'],0)
        for item in r['selected']+[r['controller']]:
            self.assertEqual(item['status'],'not_enrolled')
        self.assertEqual(r['controller']['alias'],'controller')

    def test_C02_enrolled_zero_events(self):
        sid=self.enroll(1); self.measure(sid)
        item=self.run_audit([sid])['selected'][0]
        self.assertEqual(item['status'],'enrolled_no_events')
        self.assertEqual(sum(item['event_counts'].values()),0)
        for name in ('tokens','cost_usd','human_minutes'):
            self.assertIsNone(item['reported_measurements'][name]['value'])

    def test_C03_observed_partial(self):
        sid=self.enroll(1); self.measure(sid)
        names=['UserPromptSubmit','PreToolUse','PostToolUse','SubagentStart','SubagentStop','Stop']
        for name in names: self.event(sid,name)
        self.sql('INSERT INTO outcomes(session_id,recorded_utc,artifact_hash,check_hash,evaluator,evidence,outcome) VALUES (?,?,?,?,?,?,?)',(sid,STAMP,'c'*64,'d'*64,SECRET,SECRET,'passed'))
        r=self.run_audit([sid]); item=r['selected'][0]
        self.assertEqual(item['status'],'observed_partial')
        self.assertEqual(item['event_counts'],dict.fromkeys(names,1))
        self.assertEqual(r['database_summary']['outcomes'],1)
        self.assertEqual(item['contacts']['resolution_records'],0)
        self.assertIsNone(item['contacts'].get('latest_resolution_state'))

    def test_C04_measurements_unknown_distinct_zero(self):
        ids=[self.enroll(i) for i in range(1,4)]
        self.measure(ids[1]); self.measure(ids[2],0)
        r=self.run_audit(ids)
        for name in ('tokens','cost_usd','human_minutes'):
            self.assertIsNone(r['selected'][0]['reported_measurements'][name]['value'])
            self.assertIsNone(r['selected'][1]['reported_measurements'][name]['value'])
            self.assertEqual(r['selected'][2]['reported_measurements'][name]['value'],0)
        self.assertEqual(r['database_summary']['measurement_rows'],{'known':3,'unknown':3})

    def test_C05_current_revisions_and_unclassified(self):
        sid=self.enroll(1)
        events=[self.event(sid) for _ in range(4)]
        self.label(sid,events[0],'initial_request',minutes=0)
        self.label(sid,events[1],'correction')
        self.label(sid,events[1],'approval',revision=2)
        self.label(sid,events[2],'correction')
        nonprompt=self.event(sid,'Stop')
        self.label(sid,nonprompt,'correction')
        contacts=self.run_audit([sid])['selected'][0]['contacts']
        self.assertEqual(contacts['captured_prompts'],4)
        self.assertEqual(contacts['latest_label_counts'].get('correction'),1)
        self.assertEqual(contacts['latest_label_counts'].get('approval'),1)
        self.assertEqual(contacts['latest_label_counts'].get('initial_request'),1)
        self.assertEqual(contacts['unclassified_prompts'],1)
        self.assertIsNone(contacts.get('correction_total'))

    def test_C06_explicit_latest_resolution(self):
        sid=self.enroll(1)
        initial=self.event(sid); confirmation=self.event(sid)
        self.label(sid,initial,'initial_request'); self.label(sid,confirmation,'confirmation')
        self.resolution(sid,confirmation,'resolved')
        contacts=self.run_audit([sid])['selected'][0]['contacts']
        self.assertEqual(contacts['resolution_records'],1)
        if 'latest_resolution_state' in contacts: self.assertEqual(contacts['latest_resolution_state'],'resolved')
        self.resolution(sid,confirmation,'reopened')
        contacts=self.run_audit([sid])['selected'][0]['contacts']
        self.assertEqual(contacts['resolution_records'],2)
        if 'latest_resolution_state' in contacts: self.assertEqual(contacts['latest_resolution_state'],'reopened')
        self.assertNotEqual(contacts.get('first_pass_resolution'),True)

    def test_C07_controller_not_human_correction(self):
        worker=self.enroll(1); controller=self.enroll(2)
        first=self.event(worker); second=self.event(worker)
        self.label(worker,first,'initial_request'); self.label(worker,second,'correction')
        self.event(controller)
        r=self.run_audit([worker],controller)
        self.assertEqual(r['selected'][0]['contacts']['latest_label_counts'].get('correction'),1)
        self.assertEqual(r['controller']['contacts']['captured_prompts'],1)

    def test_C08_missing_tables_invalid_inputs_and_preservation(self):
        sid=self.enroll(1); self.event(sid)
        self.sql('DROP TABLE contact_labels'); self.sql('DROP TABLE contact_resolutions')
        self.assertIsNone(self.run_audit([sid])['selected'][0]['contacts'])
        self.run_audit([sid],db=self.root/'missing.sqlite3',expected=2)
        self.run_audit([sid,sid],expected=2)
        self.run_audit([],expected=2)
        self.run_audit(['not-host-prefixed'],expected=2)
        occupied=self.root/'occupied.json'; occupied.write_bytes(b'previous-output')
        self.run_audit([sid],extra=['--output',occupied],expected=2)
        self.assertEqual(occupied.read_bytes(),b'previous-output')
        self.run_audit([sid],extra=['--output',self.db],expected=2)
        self.run_audit([sid],extra=['--output',self.selection],expected=2)

def main():
    global ARGS
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',required=True,type=Path)
    parser.add_argument('--result',required=True,type=Path)
    parser.add_argument('--private-log',required=True,type=Path)
    ARGS=parser.parse_args()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(AuditTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    failures={test.id().rsplit('.',1)[-1]:trace for test,trace in result.failures+result.errors}
    payload={'schema_version':1,'kind':'independent_recorder_audit_fixture_result','accepted':result.wasSuccessful(),'total':result.testsRun,'passed':result.testsRun-len(result.failures)-len(result.errors),'failures':len(result.failures),'errors':len(result.errors),'cases':[{'case':name.split('_',2)[1],'passed':name not in failures} for name in unittest.defaultTestLoader.getTestCaseNames(AuditTests)],'candidate_sha256':digest(ARGS.candidate),'probe_sha256':digest(Path(__file__)),'scope':'Eight synthetic fixture groups; actual audit CLI, no model calls, no real recorder or transcripts. Source database and selection bytes checked unchanged. No whole-task measurement or complete-coverage claim.'}
    ARGS.result.write_text(json.dumps(payload,indent=2)+'\n',encoding='utf-8')
    ARGS.private_log.write_text(json.dumps({'failures':failures},indent=2)+'\n',encoding='utf-8')
    print(json.dumps(payload))
    return 0 if result.wasSuccessful() else 1

if __name__=='__main__':
    raise SystemExit(main())
