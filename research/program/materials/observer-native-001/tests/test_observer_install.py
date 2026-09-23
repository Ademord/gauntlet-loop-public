"""Installer tests touch temporary settings and stub runtimes only."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools import observer_install as installer


class ObserverInstallTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = self.root / 'source'
        self.source.mkdir()
        self.module_bytes = {name: ('# frozen fixture: ' + name + '\n').encode()
                             for name in installer.MODULES}
        for name, content in self.module_bytes.items():
            (self.source / name).write_bytes(content)
        self.private = self.root / 'private space'
        self.database = self.private / 'observer.sqlite3'
        self.backups = self.root / 'backups'
        self.targets = {'codex': self.root / 'codex' / 'hooks.json',
                        'claude': self.root / 'claude' / 'settings.json'}
        self.settings = {
            'permissions': {'allow': ['Read'], 'deny': ['Bash(rm:*)']},
            'model': 'user-selected-model',
            'custom': {'keep': True},
            'hooks': {
                'PreToolUse': [{'matcher': 'Read', 'hooks': [
                    {'type': 'command', 'command': 'existing-tool', 'args': ['--keep', 'space value'], 'timeout': 17}]}],
                'UnrelatedEvent': [{'hooks': [{'type': 'command', 'command': 'preserve-this'}]}],
            },
        }
        self.before = {}
        for host, target in self.targets.items():
            target.parent.mkdir()
            content = b'\xef\xbb\xbf' + json.dumps(self.settings, indent=4).replace('\n', '\r\n').encode() + b'\r\n'
            target.write_bytes(content)
            self.before[host] = content

    def prepare(self, targets=None):
        with patch.object(installer, '__file__', str(self.source / 'observer_install.py')):
            return installer.prepare(self.private, self.database, targets or self.targets, python=sys.executable)

    def assert_original_settings(self):
        for host, target in self.targets.items():
            self.assertEqual(target.read_bytes(), self.before[host])

    def test_merge_preserves_existing_settings_and_hook_arguments(self):
        original = copy.deepcopy(self.settings)
        args = ['-B', 'observer-script.py', '--db', 'database with spaces.sqlite3', 'hook']
        merged = installer.merge_hooks(self.settings, 'claude', 'python-executable', args)
        self.assertEqual(self.settings, original)
        for key in ('permissions', 'model', 'custom'):
            self.assertEqual(merged[key], original[key])
        self.assertEqual(merged['hooks']['PreToolUse'][0], original['hooks']['PreToolUse'][0])
        self.assertEqual(merged['hooks']['UnrelatedEvent'], original['hooks']['UnrelatedEvent'])
        self.assertEqual(merged['hooks']['PreToolUse'][-1]['hooks'][0]['args'], args)

    def test_matching_command_and_args_are_not_duplicated(self):
        for host, args in (('codex', None), ('claude', ['-B', 'observer-script.py', 'hook'])):
            with self.subTest(host=host):
                merged = installer.merge_hooks(self.settings, host, 'python-or-command', args)
                second = installer.merge_hooks(merged, host, 'python-or-command', args)
                self.assertEqual(second, merged)
                for event in installer.EVENTS[host]:
                    matches = [hook for entry in second['hooks'][event] for hook in entry['hooks']
                               if hook.get('command') == 'python-or-command' and hook.get('args') == args]
                    self.assertEqual(len(matches), 1)

    def test_same_executable_with_different_arguments_remains_distinct(self):
        existing = {'hooks': {'Stop': [{'hooks': [
            {'type': 'command', 'command': 'python-executable', 'args': ['existing-script.py']}]}]}}
        merged = installer.merge_hooks(existing, 'claude', 'python-executable', ['observer-script.py'])
        hooks = [hook for entry in merged['hooks']['Stop'] for hook in entry['hooks']]
        self.assertEqual([hook['args'] for hook in hooks], [['existing-script.py'], ['observer-script.py']])

    def test_prepare_freezes_runtime_without_applying_settings(self):
        first = self.prepare()
        self.assert_original_settings()
        runtime = Path(first['runtime'])
        self.assertEqual(runtime.name, first['runtime_sha256'])
        for name, content in self.module_bytes.items():
            self.assertEqual((runtime / name).read_bytes(), content)
        (self.source / 'observer.py').write_bytes(b'# changed source after preparation\n')
        second = self.prepare()
        self.assertNotEqual(second['runtime_sha256'], first['runtime_sha256'])
        self.assertEqual((runtime / 'observer.py').read_bytes(), self.module_bytes['observer.py'])
        # Applying the earlier plan uses its saved runtime, not later source edits.
        results = installer.apply(first, self.backups)
        self.assertTrue(all(row['status'] == 'installed' for row in results))

    def test_apply_preserves_exact_backups_and_existing_settings(self):
        plan = self.prepare()
        installer.apply(plan, self.backups)
        for change in plan['changes']:
            host = change['host']
            backup = self.backups / (host + '-' + change['before_sha256'] + '.json')
            self.assertEqual(backup.read_bytes(), self.before[host])
            self.assertEqual(change['before_sha256'], hashlib.sha256(self.before[host]).hexdigest())
            after_bytes = self.targets[host].read_bytes()
            self.assertEqual(hashlib.sha256(after_bytes).hexdigest(), change['after_sha256'])
            after = json.loads(after_bytes)
            for key in ('permissions', 'model', 'custom'):
                self.assertEqual(after[key], self.settings[key])
            self.assertEqual(after['hooks']['PreToolUse'][0], self.settings['hooks']['PreToolUse'][0])
            added = after['hooks']['PreToolUse'][-1]['hooks'][0]
            if host == 'claude':
                self.assertEqual(Path(added['command']).resolve(), Path(sys.executable).resolve())
                self.assertEqual(added['args'][0], '-B')
                self.assertEqual(Path(added['args'][1]).resolve(), Path(plan['runtime']) / 'observer_host.py')
                self.assertEqual(added['args'][2], '--db')
                self.assertEqual(Path(added['args'][3]).resolve(), self.database.resolve())
                self.assertEqual(added['args'][4:], ['--host', 'claude', 'hook'])
            else:
                self.assertNotIn('args', added)
                self.assertIn('--host codex hook', added['command'])

    def test_reprepare_and_apply_does_not_duplicate_hooks_or_backups(self):
        installer.apply(self.prepare(), self.backups)
        settings_before = {host: path.read_bytes() for host, path in self.targets.items()}
        backups_before = {path.name: path.read_bytes() for path in self.backups.iterdir()}
        results = installer.apply(self.prepare(), self.backups)
        self.assertTrue(all(row['status'] == 'unchanged' for row in results))
        self.assertEqual({host: path.read_bytes() for host, path in self.targets.items()}, settings_before)
        self.assertEqual({path.name: path.read_bytes() for path in self.backups.iterdir()}, backups_before)

    def test_stale_second_target_rejects_all_changes_before_apply(self):
        plan = self.prepare()
        concurrent = b'{"user_changed":true}\n'
        self.targets['claude'].write_bytes(concurrent)
        with self.assertRaises(ValueError):
            installer.apply(plan, self.backups)
        self.assertEqual(self.targets['codex'].read_bytes(), self.before['codex'])
        self.assertEqual(self.targets['claude'].read_bytes(), concurrent)
        self.assertFalse(self.backups.exists())

    def test_changed_prepared_content_or_runtime_cannot_be_installed(self):
        for changed in ('prepared-content', 'runtime'):
            with self.subTest(changed=changed):
                plan = self.prepare()
                if changed == 'prepared-content':
                    plan['changes'][0]['after_utf8'] += ' '
                else:
                    (Path(plan['runtime']) / 'observer_host.py').write_bytes(b'# modified frozen adapter\n')
                with self.assertRaises(ValueError):
                    installer.apply(plan, self.backups)
                self.assert_original_settings()
                self.assertFalse(self.backups.exists())

    def test_preparing_over_modified_frozen_runtime_is_rejected(self):
        plan = self.prepare()
        (Path(plan['runtime']) / 'observer.py').write_bytes(b'# altered runtime\n')
        with self.assertRaises(ValueError):
            self.prepare()
        self.assert_original_settings()

    def test_existing_backup_is_never_overwritten(self):
        plan = self.prepare({'codex': self.targets['codex']})
        change = plan['changes'][0]
        self.backups.mkdir()
        backup = self.backups / ('codex-' + change['before_sha256'] + '.json')
        backup.write_bytes(b'preexisting backup with wrong identity')
        with self.assertRaises(ValueError):
            installer.apply(plan, self.backups)
        self.assertEqual(backup.read_bytes(), b'preexisting backup with wrong identity')
        self.assert_original_settings()

    def test_invalid_second_backup_is_rejected_before_any_target_changes(self):
        plan = self.prepare()
        second = plan['changes'][1]
        self.backups.mkdir()
        backup = self.backups / (second['host'] + '-' + second['before_sha256'] + '.json')
        backup.write_bytes(b'preexisting second-host backup with wrong identity')
        with self.assertRaises(ValueError):
            installer.apply(plan, self.backups)
        self.assert_original_settings()
        self.assertEqual(backup.read_bytes(), b'preexisting second-host backup with wrong identity')


if __name__ == '__main__':
    unittest.main()
