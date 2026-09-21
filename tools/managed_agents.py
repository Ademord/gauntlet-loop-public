"""No-model qualification of a managed-agent execution boundary.

This is a readiness tool, not a worker dispatcher. It never turns a failed
sandbox check into an unsandboxed run or changes machine-wide settings.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import uuid

SCHEMA = 'gauntlet-managed-profile/v1'
REQUIRED = {'schema', 'codex', 'python', 'external_probe', 'timeout_seconds'}
PROBE_CODE = r'''import json,pathlib,socket,sys
work,control,outside=map(pathlib.Path,sys.argv[1:4])
port=int(sys.argv[4]); host=sys.argv[5]; external_port=int(sys.argv[6])
result={}
actions=[
 ('workspace_write',lambda:(work/'inside.txt').write_text('ok')),
 ('workspace_read',lambda:(work/'inside.txt').read_text()),
 ('outside_write',lambda:(outside/'write-canary.txt').write_text('probe')),
 ('outside_read',lambda:(outside/'read-canary.txt').read_text()),
 ('controller_read',lambda:(control/'read-canary.txt').read_text()),
 ('loopback_connect',lambda:socket.create_connection(('127.0.0.1',port),timeout=2).close()),
 ('external_connect',lambda:socket.create_connection((host,external_port),timeout=2).close())]
for name,action in actions:
 try: action(); result[name]={'allowed':True}
 except OSError as exc:
  result[name]={'allowed':False,'error':type(exc).__name__,'errno':exc.errno,'winerror':getattr(exc,'winerror',None)}
print(json.dumps(result))
'''


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read_profile(path):
    value = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(value, dict) or set(value) != REQUIRED:
        raise ValueError('Profile must contain exactly: ' + ', '.join(sorted(REQUIRED)))
    if value['schema'] != SCHEMA:
        raise ValueError('Unknown profile schema')
    for key in ('codex', 'python'):
        if not isinstance(value[key], str):
            raise ValueError(key + ' must be an executable path string')
        p = Path(value[key]).expanduser()
        if not p.is_absolute() or not p.is_file():
            raise ValueError(key + ' must name an existing absolute executable path')
        value[key] = str(p.resolve())
    endpoint = value['external_probe']
    if not isinstance(endpoint, dict) or set(endpoint) != {'host', 'port'}:
        raise ValueError('external_probe needs host and port')
    # A numeric endpoint avoids DNS availability masquerading as network isolation.
    import ipaddress
    address = ipaddress.ip_address(endpoint['host'])
    if not address.is_global:
        raise ValueError('external_probe.host must be a public numeric IP')
    if type(endpoint['port']) is not int or not 1 <= endpoint['port'] <= 65535:
        raise ValueError('Invalid external port')
    if type(value['timeout_seconds']) is not int or not 5 <= value['timeout_seconds'] <= 60:
        raise ValueError('timeout_seconds must be between 5 and 60')
    return value


def toml(value):
    if isinstance(value, dict):
        return '{' + ','.join(json.dumps(k) + '=' + toml(v) for k, v in value.items()) + '}'
    return json.dumps(value)


def sandbox_argv(profile, workspace, controller, command):
    """Explicit profile; inherited project configuration cannot supply the boundary."""
    filesystem = {
        ':root': 'deny', ':minimal': 'read',
        ':workspace_roots': {'.': 'write', '.codex': 'read', '.git': 'read'},
        Path(profile['python']).parent.as_posix(): 'read',
        Path(controller).resolve().as_posix(): 'deny',
    }
    return [profile['codex'], 'sandbox', '-P', 'gauntlet_qualification',
            '--include-managed-config', '-c', 'windows.sandbox="elevated"',
            '-c', 'permissions.gauntlet_qualification.filesystem=' + toml(filesystem),
            '-c', 'permissions.gauntlet_qualification.network.enabled=false',
            '-C', str(workspace), '--', *map(str, command)]


def clean_environment(workspace):
    # The probe neither needs nor inherits model/API credentials. Codex still
    # resolves its normal user/managed policy; no alternative credential home.
    permitted = {'SYSTEMROOT', 'WINDIR', 'COMSPEC', 'PATH', 'PATHEXT', 'USERPROFILE',
                 'APPDATA', 'LOCALAPPDATA', 'PROGRAMDATA', 'PROGRAMFILES',
                 'PROGRAMFILES(X86)', 'HOMEDRIVE', 'HOMEPATH', 'CODEX_HOME'}
    env = {k: v for k, v in os.environ.items() if k.upper() in permitted}
    scratch = Path(workspace) / 'temp'
    scratch.mkdir(exist_ok=True)
    env.update(TEMP=str(scratch), TMP=str(scratch), TMPDIR=str(scratch),
               PYTHONIOENCODING='utf-8', PYTHONNOUSERSITE='1')
    return env


def run_bounded(argv, cwd, env, seconds):
    start = time.monotonic()
    creation = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
    p = subprocess.Popen(argv, cwd=cwd, env=env, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, text=True, encoding='utf-8',
                         errors='replace', creationflags=creation,
                         start_new_session=os.name != 'nt')
    timed_out = False
    cleanup = None
    cleanup_error = None
    try:
        out, err = p.communicate(timeout=seconds)
    except subprocess.TimeoutExpired:
        timed_out = True
        try:
            if os.name == 'nt':
                kill = Path(os.environ['SystemRoot']) / 'System32/taskkill.exe'
                stopped = subprocess.run([str(kill), '/PID', str(p.pid), '/T', '/F'],
                                         capture_output=True, timeout=10)
                cleanup = stopped.returncode
            else:
                import signal
                os.killpg(p.pid, signal.SIGKILL)
                cleanup = 0
        except (OSError, subprocess.TimeoutExpired) as exc:
            cleanup, cleanup_error = -1, type(exc).__name__
        if cleanup != 0:
            try:
                p.kill()
            except OSError as exc:
                cleanup_error = (cleanup_error or '') + '; parent kill: ' + type(exc).__name__
        try:
            out, err = p.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            # Only our owned probe process; retained pipes are not evidence of
            # descendant shutdown, so the qualification remains blocked.
            try:
                p.kill()
            except OSError as exc:
                cleanup_error = (cleanup_error or '') + '; parent kill: ' + type(exc).__name__
            p.stdout.close()
            p.stderr.close()
            out, err = '', 'Process tree did not close its output pipes.'
            cleanup = -1
    return {'exit_code': p.returncode, 'timed_out': timed_out,
            'cleanup_exit': cleanup, 'cleanup_error': cleanup_error, 'stdout': out, 'stderr': err,
            'elapsed_seconds': round(time.monotonic() - start, 3)}


def permission_denied(record):
    # Missing paths, parser failures and connection timeouts do not prove policy.
    return (isinstance(record, dict) and record.get('allowed') is False and
            (record.get('error') == 'PermissionError' or record.get('winerror') in {5, 10013}))


def assess(observed, controls, process):
    checks = {}
    healthy = process.get('exit_code') == 0 and not process.get('timed_out')
    checks['probe_completed'] = healthy
    for key in ('workspace_write', 'workspace_read'):
        checks[key] = healthy and observed.get(key, {}).get('allowed') is True
    for key in ('outside_write', 'outside_read', 'controller_read'):
        checks[key + '_denied'] = healthy and controls.get('files_exist') is True and permission_denied(observed.get(key))
    checks['outside_unchanged'] = controls.get('outside_unchanged') is True
    for key in ('loopback_connect', 'external_connect'):
        checks[key + '_denied'] = healthy and controls.get(key) is True and permission_denied(observed.get(key))
    return checks


def probe(profile, output_parent):
    if os.name != 'nt':
        raise ValueError('This adapter qualifies the native Windows backend only')
    parent = Path(output_parent).resolve()
    parent.mkdir(parents=True, exist_ok=True)
    root = parent / ('qualification-' + uuid.uuid4().hex)
    root.mkdir()
    workspace, controller, outside = [root / n for n in ('workspace', 'controller', 'outside')]
    for folder in (workspace, controller, outside):
        folder.mkdir()
    for folder in (controller, outside):
        (folder / 'read-canary.txt').write_text('Synthetic probe data only.', encoding='utf-8')
    before = digest(outside / 'read-canary.txt')
    probe_file = workspace / 'probe.py'
    probe_file.write_text(PROBE_CODE, encoding='utf-8')
    controls = {'files_exist': True}
    endpoint = profile['external_probe']
    with socket.socket() as server:
        server.bind(('127.0.0.1', 0))
        server.listen(4)
        port = server.getsockname()[1]
        for key, address in [('loopback_connect', ('127.0.0.1', port)),
                             ('external_connect', (endpoint['host'], endpoint['port']))]:
            try:
                with socket.create_connection(address, timeout=3):
                    controls[key] = True
            except OSError as exc:
                controls[key] = False
                controls[key + '_error'] = type(exc).__name__
        command = [profile['python'], '-I', '-B', str(probe_file), str(workspace),
                   str(controller), str(outside), str(port), endpoint['host'], str(endpoint['port'])]
        argv = sandbox_argv(profile, workspace, controller, command)
        try:
            process = run_bounded(argv, workspace, clean_environment(workspace), profile['timeout_seconds'])
        except OSError as exc:
            process = {'exit_code': None, 'timed_out': False, 'stdout': '', 'stderr': str(exc)}
    try:
        observed = json.loads(process['stdout'])
        if not isinstance(observed, dict):
            observed = {}
    except ValueError:
        observed = {}
    controls['outside_unchanged'] = (not (outside / 'write-canary.txt').exists() and
                                     digest(outside / 'read-canary.txt') == before)
    checks = assess(observed, controls, process)
    report = {
        'schema': 'gauntlet-managed-qualification/v1',
        'checked_utc': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
        'profile': profile,
        'profile_sha256': hashlib.sha256(json.dumps(profile, sort_keys=True).encode()).hexdigest(),
        'tool_sha256': digest(__file__),
        'executables': {k: {'sha256': digest(profile[k]), 'path': profile[k]} for k in ('codex', 'python')},
        'process': process, 'observed': observed, 'controls': controls, 'checks': checks,
        'boundary_status': 'passed_probes' if all(checks.values()) else 'blocked',
        'dispatch_allowed': False,
        'qualification_scope': 'Finite synthetic read/write and direct TCP probes only.',
        'not_yet_qualified': ['descendant cancellation', 'worker-accessible validation',
                              'host adapter and observer integration', 'resource limits',
                              'alternate IPC or filesystem escape paths'],
        'model_calls': 0, 'performance_claim': None,
        'note': 'No general worker execution is enabled by this tool. No unsandboxed fallback.',
    }
    output = root / 'qualification.json'
    output.write_text(json.dumps(report, indent=2), encoding='utf-8')
    return output, report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    doctor = subs.add_parser('doctor', help='Run no-model canary probes; preserve a private report')
    doctor.add_argument('--profile', required=True)
    doctor.add_argument('--output', required=True, help='Private report parent, outside public tracked files')
    args = parser.parse_args(argv)
    try:
        path, report = probe(read_profile(args.profile), args.output)
        print(json.dumps({'report': str(path), 'boundary_status': report['boundary_status'],
                          'checks': report['checks'], 'dispatch_allowed': False, 'model_calls': 0}))
        return 0 if report['boundary_status'] == 'passed_probes' else 3
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
