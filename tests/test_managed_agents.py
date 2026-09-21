import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('managed_agents', Path(__file__).parents[1] / 'tools/managed_agents.py')
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class ManagedQualificationTests(unittest.TestCase):
    def fixtures(self):
        observed = {name: {'allowed': False, 'error': 'PermissionError', 'errno': 13}
                    for name in ('outside_write', 'outside_read', 'controller_read', 'loopback_connect', 'external_connect')}
        observed.update(workspace_write={'allowed': True}, workspace_read={'allowed': True})
        controls = dict(files_exist=True, outside_unchanged=True, loopback_connect=True, external_connect=True)
        return observed, controls, dict(exit_code=0, timed_out=False)

    def test_complete_canaries_pass(self):
        self.assertTrue(all(m.assess(*self.fixtures()).values()))

    def test_reachable_loopback_blocks_qualification(self):
        observed, controls, process = self.fixtures()
        observed['loopback_connect'] = {'allowed': True}
        checks = m.assess(observed, controls, process)
        self.assertFalse(checks['loopback_connect_denied'])
        self.assertTrue(checks['external_connect_denied'])

    def test_missing_file_is_not_isolation(self):
        observed, controls, process = self.fixtures()
        observed['outside_read'] = {'allowed': False, 'error': 'FileNotFoundError', 'errno': 2}
        self.assertFalse(m.assess(observed, controls, process)['outside_read_denied'])

    def test_host_network_failure_cannot_prove_blocking(self):
        observed, controls, process = self.fixtures()
        controls['external_connect'] = False
        self.assertFalse(m.assess(observed, controls, process)['external_connect_denied'])

    def test_timeout_cannot_pass_with_stale_success_output(self):
        observed, controls, process = self.fixtures()
        process['timed_out'] = True
        checks = m.assess(observed, controls, process)
        self.assertFalse(checks['probe_completed'])
        self.assertFalse(checks['workspace_write'])

    def test_launch_failure_keeps_missing_observations_failed(self):
        _, controls, process = self.fixtures()
        process['exit_code'] = 1
        self.assertFalse(any(v for k, v in m.assess({}, controls, process).items() if k != 'outside_unchanged'))

    def test_profile_rejects_unknown_widening_knob(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'profile.json'
            path.write_text(json.dumps({'schema': m.SCHEMA, 'unsafe_fallback': True}))
            with self.assertRaises(ValueError):
                m.read_profile(path)

    def test_exact_profile_includes_managed_requirements(self):
        with tempfile.TemporaryDirectory() as d:
            profile = {'codex': str(Path(d)/'codex.exe'), 'python': str(Path(d)/'python/python.exe')}
            argv = m.sandbox_argv(profile, Path(d)/'work', Path(d)/'control', ['python', '-B', 'test.py'])
            self.assertIn('--include-managed-config', argv)
            self.assertIn('permissions.gauntlet_qualification.network.enabled=false', argv)
            fs = next(x for x in argv if '.filesystem=' in x)
            self.assertIn('\":root\"=\"deny\"', fs)
            self.assertNotIn('danger-full-access', ' '.join(argv))

    def test_credentials_not_inherited(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as d, patch.dict(m.os.environ, {'OPENAI_API_KEY': 'synthetic', 'ANTHROPIC_API_KEY': 'synthetic', 'CUSTOM_SECRET': 'synthetic'}):
            env = m.clean_environment(d)
            self.assertNotIn('OPENAI_API_KEY', env)
            self.assertNotIn('ANTHROPIC_API_KEY', env)
            self.assertNotIn('CUSTOM_SECRET', env)

    @unittest.skipUnless(m.os.name == 'nt', 'Windows cleanup adapter')
    def test_cleanup_timeout_preserves_failure_and_attempts_parent_stop(self):
        from unittest.mock import MagicMock, patch
        p = MagicMock(pid=123, returncode=-1)
        p.communicate.side_effect = [m.subprocess.TimeoutExpired('probe', 1), ('partial', 'stopped')]
        with patch.object(m.subprocess, 'Popen', return_value=p), patch.object(
                m.subprocess, 'run', side_effect=m.subprocess.TimeoutExpired('taskkill', 10)):
            result = m.run_bounded(['probe'], '.', {}, 1)
        p.kill.assert_called_once()
        self.assertTrue(result['timed_out'])
        self.assertEqual(result['cleanup_exit'], -1)
        self.assertEqual(result['cleanup_error'], 'TimeoutExpired')
        self.assertEqual(result['stdout'], 'partial')


if __name__ == '__main__':
    unittest.main()
