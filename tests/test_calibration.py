"""No-model tests for accounting, immutable runs, and checkpoint branch control."""
import contextlib
import copy
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1] / 'tools/paired_study'
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
from tools.paired_study import run_calibration as calibration
from tools.paired_study import index_calibration_evidence as evidence


def result(tokens=100, cost=0.1, session='session-build'):
    return {'type': 'result', 'session_id': session, 'subtype': 'success', 'is_error': False,
            'total_cost_usd': cost, 'result': 'No additional issue found.',
            'modelUsage': {'model': {'inputTokens': tokens, 'outputTokens': 0, 'cacheReadInputTokens': 0,
                                    'cacheCreationInputTokens': 0, 'costUSD': cost}}}


def write_fixture(root, name='task1'):
    task = root / name
    for directory in ('base/tests', 'heldout', 'oracle'):
        (task / directory).mkdir(parents=True)
    spec = {'description': 'Repair value.', 'requirements': ['Return one.'], 'allowed_paths': ['answer.py']}
    (task / 'task.json').write_text(json.dumps(spec), encoding='utf-8')
    (task / 'base/answer.py').write_text('value = 0\n', encoding='utf-8')
    (task / 'oracle/answer.py').write_text('value = 1\n', encoding='utf-8')
    (task / 'base/tests/test_visible.py').write_text(
        'import unittest\nfrom answer import value\nclass Visible(unittest.TestCase):\n'
        '    def test_value(self): self.assertIn(value, (0, 1))\n', encoding='utf-8')
    (task / 'heldout/test_hidden.py').write_text(
        'import unittest\nfrom answer import value\nclass Hidden(unittest.TestCase):\n'
        '    def test_value(self): self.assertEqual(value, 1)\n', encoding='utf-8')
    return task, spec


class IncrementalAccountingTest(unittest.TestCase):
    def test_fork_charges_only_increment_over_parent(self):
        delta = calibration.incremental_usage(result(160, .16), result(100, .1))
        self.assertEqual(delta['total_tokens'], 60)
        self.assertAlmostEqual(delta['cost_usd'], .06)
        self.assertEqual(calibration.incremental_usage(result())['total_tokens'], 100)

    def test_added_model_is_charged_and_parent_models_are_subtracted(self):
        parent = result()
        child = result(150, .2)
        child['modelUsage']['model']['costUSD'] = .15
        child['modelUsage']['new-model'] = {'inputTokens': 20, 'outputTokens': 10,
                                          'cacheReadInputTokens': 5, 'cacheCreationInputTokens': 5, 'costUSD': .05}
        delta = calibration.incremental_usage(child, parent)
        self.assertEqual(delta['total_tokens'], 90)
        self.assertAlmostEqual(delta['cost_usd'], .1)

    def test_negative_counters_cost_or_missing_current_categories_fail(self):
        cases = [result(90, .11), result(110, .09)]
        missing = result(110, .11)
        del missing['modelUsage']['model']['outputTokens']
        cases.append(missing)
        missing = result(110, .11)
        del missing['modelUsage']
        cases.append(missing)
        for event in cases:
            with self.subTest(event=event), self.assertRaises(ValueError):
                calibration.incremental_usage(event, result())

    def test_incomplete_parent_is_unknown_not_zero(self):
        parents = []
        missing_models = result()
        del missing_models['modelUsage']
        parents.append(missing_models)
        missing_category = result()
        del missing_category['modelUsage']['model']['inputTokens']
        parents.append(missing_category)
        missing_cost = result()
        del missing_cost['modelUsage']['model']['costUSD']
        parents.append(missing_cost)
        for parent in parents:
            with self.subTest(parent=parent), self.assertRaises(ValueError):
                calibration.incremental_usage(result(150, .15), parent)

    def test_malformed_token_values_and_nonfinite_costs_fail(self):
        for bad in (True, 1.5, float('nan'), float('inf')):
            event = result()
            event['modelUsage']['model']['inputTokens'] = bad
            with self.subTest(tokens=bad), self.assertRaises(ValueError):
                calibration.incremental_usage(event)
        event = result()
        event['total_cost_usd'] = float('nan')
        with self.assertRaises(ValueError):
            calibration.incremental_usage(event)

    def test_cost_mismatch_cannot_be_used_as_a_valid_stage(self):
        event = result(150, .2)
        event['modelUsage']['model']['costUSD'] = .15
        with self.assertRaisesRegex(ValueError, 'reconcile'):
            calibration.incremental_usage(event, result())


class FreezeAndGraderTest(unittest.TestCase):
    def test_frozen_code_protocol_tasks_and_caps_are_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tasks = root / 'tasks'
            for index in range(6):
                write_fixture(tasks, 'task' + str(index))
            protocol = root / 'PROTOCOL.md'
            protocol.write_text('Frozen protocol.', encoding='utf-8')
            run = root / 'run'
            with patch.object(calibration, 'TASKS', tasks), patch.object(calibration, 'PROTOCOL', protocol), \
                    patch.object(calibration, 'validate_fixture', return_value={'valid': True}), contextlib.redirect_stdout(io.StringIO()):
                calibration.prepare(run, 'model', 0)
                manifest = json.loads((run / 'manifest.json').read_text())
                calibration.verify_manifest(manifest)
                for field in ('runner_sha256', 'telemetry_sha256', 'protocol_sha256'):
                    mutated = copy.deepcopy(manifest)
                    mutated[field] = 'incorrect'
                    with self.subTest(field=field), self.assertRaises(ValueError):
                        calibration.verify_manifest(mutated)
                mutated = copy.deepcopy(manifest)
                mutated['stage_caps']['build'] += .01
                with self.assertRaises(ValueError):
                    calibration.verify_manifest(mutated)
                target = tasks / 'task0/base/answer.py'
                target.write_text('value = 999\n')
                with self.assertRaisesRegex(ValueError, 'Task changed'):
                    calibration.verify_manifest(manifest)

    def test_bad_fixture_prevents_preparation_and_calls_no_model(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tasks = root / 'tasks'
            for index in range(6):
                write_fixture(tasks, 'task' + str(index))
            with patch.object(calibration, 'TASKS', tasks), \
                    patch.object(calibration, 'validate_fixture', return_value={'valid': False}), \
                    patch.object(calibration.subprocess, 'run') as backend:
                with self.assertRaisesRegex(ValueError, 'Fixture validation failed'):
                    calibration.prepare(root / 'run', 'model', 0)
                backend.assert_not_called()
                self.assertFalse((root / 'run/manifest.json').exists())

    def test_hidden_failure_survives_visible_pass_and_candidate_test_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            task, _ = write_fixture(root / 'tasks')
            candidate = root / 'candidate'
            (candidate / 'tests').mkdir(parents=True)
            (candidate / 'answer.py').write_text('value = 0\n')
            (candidate / 'tests/test_visible.py').write_text('raise RuntimeError("candidate test must not run")\n')
            outcome = calibration.grade(task, candidate)
            self.assertTrue(outcome['visible_passed'])
            self.assertFalse(outcome['hidden_passed'])
            (candidate / 'answer.py').write_text('value = 1\n')
            outcome = calibration.grade(task, candidate)
            self.assertTrue(outcome['visible_passed'])
            self.assertTrue(outcome['hidden_passed'])

    def test_runtime_hidden_test_rewrite_fails_grader_integrity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            task, _ = write_fixture(root / 'tasks')
            original_hidden = (task / 'heldout/test_hidden.py').read_bytes()
            candidate = root / 'candidate'
            candidate.mkdir()
            # Both test assertions would pass with value=1. The grader must
            # still fail this source because importing it rewrites a test.
            (candidate / 'answer.py').write_text(
                'from pathlib import Path\nvalue = 1\n'
                'target = Path("heldout/test_hidden.py")\n'
                'if target.exists():\n'
                '    target.write_text("# test removed at import time\\n")\n', encoding='utf-8')
            outcome = calibration.grade(task, candidate)
            self.assertTrue(outcome['visible_passed'])
            self.assertFalse(outcome['hidden_passed'])
            self.assertIn('heldout/test_hidden.py', outcome['hidden_integrity_changes'])
            self.assertEqual((task / 'heldout/test_hidden.py').read_bytes(), original_hidden)


class ControllerTest(unittest.TestCase):
    def make_controller(self, root):
        run, work = root / 'run', root / 'work'
        run.mkdir()
        work.mkdir()
        (work / 'answer.py').write_text('value = 0\n')
        manifest = {'diagnostic_cost_usd': 0, 'max_usd': 15, 'model': 'model'}
        return calibration.Controller(run, manifest, 'mock-claude'), work

    def test_transcript_identity_hashes_saved_bytes_after_newline_translation(self):
        with tempfile.TemporaryDirectory() as directory:
            controller, work = self.make_controller(Path(directory))
            response = subprocess.CompletedProcess([], 0, json.dumps(result()) + '\n', '')
            original_write = Path.write_text
            def translated_write(path, data, *args, **kwargs):
                if path.name.endswith('.transcript.jsonl'):
                    return path.write_bytes(data.replace('\n', '\r\n').encode('utf-8'))
                return original_write(path, data, *args, **kwargs)
            with patch.object(calibration.subprocess, 'run', return_value=response), \
                    patch.object(Path, 'write_text', translated_write), contextlib.redirect_stdout(io.StringIO()):
                controller.call('task1', 'build', 'Build.', work)
            saved = (controller.run_dir / 'private/task1-build.transcript.jsonl').read_bytes()
            self.assertNotEqual(calibration.digest(saved), calibration.digest(response.stdout.encode()))
            self.assertEqual(controller.calls[0]['transcript_sha256'], calibration.digest(saved))
            self.assertEqual(controller.calls[0]['transcript_sha256_encoding'], 'file-bytes')

    def test_reviewer_write_is_detected_and_not_retried(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            controller, work = self.make_controller(root)
            def mutate(command, **kwargs):
                (work / 'answer.py').write_text('value = 999\n')
                return subprocess.CompletedProcess(command, 0, json.dumps(result(50, .05)), '')
            with patch.object(calibration.subprocess, 'run', side_effect=mutate) as backend, contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaisesRegex(RuntimeError, 'Reviewer changed candidate'):
                    controller.call('task1', 'reviewer', 'Review read-only.', work)
                self.assertEqual(backend.call_count, 1)
            self.assertAlmostEqual(controller.spent, .05)

    def test_delegation_and_backend_error_stop_after_recording_cost(self):
        for kind in ('delegation', 'error'):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                controller, work = self.make_controller(Path(directory))
                event = result()
                prefix = ''
                if kind == 'delegation':
                    prefix = json.dumps({'type': 'assistant', 'parent_tool_use_id': None,
                                         'message': {'content': [{'type': 'tool_use', 'id': 'a', 'name': 'Agent'}]}}) + '\n'
                else:
                    event['is_error'] = True
                response = subprocess.CompletedProcess([], 0, prefix + json.dumps(event), '')
                with patch.object(calibration.subprocess, 'run', return_value=response) as backend, contextlib.redirect_stdout(io.StringIO()):
                    with self.assertRaises(RuntimeError):
                        controller.call('task1', 'build', 'Build.', work)
                    self.assertEqual(backend.call_count, 1)
                self.assertAlmostEqual(controller.spent, .1)

    def test_insufficient_reservation_spends_nothing(self):
        with tempfile.TemporaryDirectory() as directory:
            controller, work = self.make_controller(Path(directory))
            controller.manifest['max_usd'] = .01
            with patch.object(calibration.subprocess, 'run') as backend:
                with self.assertRaisesRegex(RuntimeError, 'Insufficient'):
                    controller.call('task1', 'build', 'Build.', work)
                backend.assert_not_called()

    def test_started_run_cannot_spend_again(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            (run / 'manifest.json').write_text('{}')
            (run / 'execution.started').write_text('Earlier attempt.')
            with patch.object(calibration, 'verify_manifest'), patch.object(calibration.subprocess, 'run') as backend:
                with self.assertRaises(FileExistsError):
                    calibration.execute(run, 'mock-claude')
                backend.assert_not_called()

    def test_shared_checkpoint_branches_and_grades_are_isolated(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            task, _ = write_fixture(root / 'tasks')
            run = root / 'run'
            run.mkdir()
            manifest = {'diagnostic_cost_usd': 0, 'max_usd': 15, 'model': 'model', 'task_hashes': {'task1': {}}}
            (run / 'manifest.json').write_text(json.dumps(manifest))
            seen = []
            def backend(command, **kwargs):
                if '--version' in command:
                    return subprocess.CompletedProcess(command, 0, 'mock-version', '')
                if '-m' in command:
                    return subprocess.CompletedProcess(command, 0, 'visible tests passed', '')
                stage = json.loads((run / 'events.jsonl').read_text().splitlines()[-1])['stage']
                work = Path(kwargs['cwd'])
                before = (work / 'answer.py').read_text()
                seen.append((stage, before, list(command), kwargs['input']))
                value, tokens, cost = {'build': (1, 100, .1), 'self_check': (2, 160, .16),
                                       'reviewer': (1, 30, .03), 'repair': (3, 150, .15)}[stage]
                if stage != 'reviewer':
                    (work / 'answer.py').write_text(f'value = {value}\n')
                return subprocess.CompletedProcess(command, 0, json.dumps(result(tokens, cost, 'session-' + stage)), '')
            def grader(task_path, candidate):
                self.assertEqual(len(seen), 4, 'Hidden grades must wait until every branch has finished')
                hidden = (candidate / 'answer.py').read_text() == 'value = 2\n'
                return {'visible_passed': True, 'hidden_passed': hidden,
                        'hidden_output': 'HIDDEN_SENTINEL', 'visible_output': 'visible'}
            with patch.object(calibration, 'TASKS', task.parent), patch.object(calibration, 'verify_manifest'), \
                    patch.object(calibration.subprocess, 'run', side_effect=backend), \
                    patch.object(calibration, 'grade', side_effect=grader), contextlib.redirect_stdout(io.StringIO()):
                calibration.execute(run, 'mock-claude')
            self.assertEqual({s[0] for s in seen}, {'build', 'self_check', 'reviewer', 'repair'})
            self.assertEqual(len(seen), 4)
            by_stage = {s[0]: s for s in seen}
            for stage in ('self_check', 'reviewer', 'repair'):
                self.assertEqual(by_stage[stage][1], 'value = 1\n', 'Each continuation starts from the shared build')
            for stage in ('self_check', 'repair'):
                command = by_stage[stage][2]
                self.assertEqual(command[command.index('--resume') + 1], 'session-build')
                self.assertIn('--fork-session', command)
            self.assertNotIn('--resume', by_stage['reviewer'][2])
            self.assertTrue(all('HIDDEN_SENTINEL' not in s[3] for s in seen))
            rows = [json.loads(line) for line in (run / 'results.jsonl').read_text().splitlines()]
            self.assertEqual({row['arm']: row['accepted'] for row in rows},
                             {'baseline': False, 'self_check': True, 'review': False})
            completion = json.loads((run / 'completion.json').read_text())
            self.assertAlmostEqual(completion['cost_usd'], .24)
            self.assertEqual(completion['calls'], 4)


class ReportingTest(unittest.TestCase):
    def test_partial_grades_and_pending_cost_render_as_incomplete(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            calibration.append(run / 'results.jsonl', {'task_id': 'task1', 'arm': 'baseline',
                                                       'functional_passed': False, 'accepted': False})
            for event in (
                {'event': 'reserved', 'task_id': 'task1', 'stage': 'build', 'cap_usd': .75},
                {'event': 'completed', 'task_id': 'task1', 'stage': 'build', 'cost_usd': .1},
                {'event': 'reserved', 'task_id': 'task1', 'stage': 'reviewer', 'cap_usd': .25},
            ):
                calibration.append(run / 'events.jsonl', event)
            calibration.dump(run / 'completion.json', {'state': 'stopped', 'known_cost_usd': .1,
                                                       'reason': 'Reviewer timed out; its final cost is unavailable.'})
            calibration.report(run)
            text = (run / 'REPORT.md').read_text(encoding='utf-8')
            self.assertIn('not evaluated', text)
            self.assertIn('lower bound', text.lower())
            self.assertIn('total is unknown', text.lower())
            self.assertIn('task1/reviewer', text)

    def test_scope_cleanup_is_not_reported_as_a_functional_rescue(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            for arm in ('baseline', 'self_check', 'review'):
                calibration.append(run / 'results.jsonl', {
                    'task_id': 'task1', 'arm': arm, 'visible_passed': True, 'hidden_passed': True,
                    'functional_passed': True, 'accepted': arm != 'baseline',
                    'out_of_scope': ['notes.txt'] if arm == 'baseline' else [],
                })
            calibration.dump(run / 'completion.json', {'state': 'completed', 'cost_usd': 0})
            calibration.report(run)
            text = (run / 'REPORT.md').read_text(encoding='utf-8')
            lines = text.splitlines()
            header = next(line for line in lines if line.startswith('| Arm |'))
            labels = [cell.strip().lower() for cell in header.strip('|').split('|')]
            rescue_index = next(index for index, label in enumerate(labels) if 'rescue' in label)
            spoil_index = next(index for index, label in enumerate(labels) if 'spoil' in label)
            for arm in ('self_check', 'review'):
                row = next(line for line in lines if line.startswith('| ' + arm + ' |'))
                cells = [cell.strip() for cell in row.strip('|').split('|')]
                self.assertEqual(cells[rescue_index], '0', 'Fixing scope without changing function is not a performance rescue')
                self.assertEqual(cells[spoil_index], '0')


class EvidenceIndexTest(unittest.TestCase):
    def test_crlf_file_retains_legacy_text_hash_and_records_actual_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            (run / 'private').mkdir()
            path = run / 'private/task1-build.transcript.jsonl'
            path.write_bytes(b'{"type":"result"}\r\n')
            event = {'event': 'completed', 'task_id': 'task1', 'stage': 'build',
                     'transcript_sha256': evidence.sha(b'{"type":"result"}\n')}
            calibration.append(run / 'events.jsonl', event)
            original = (run / 'events.jsonl').read_bytes()
            row = evidence.build_index(run)['transcripts'][0]
            self.assertNotEqual(row['file_bytes_sha256'], row['recorded_sha256'])
            self.assertEqual(row['file_bytes_sha256'], evidence.sha(path.read_bytes()))
            self.assertTrue(row['recorded_hash_verified'])
            self.assertEqual((run / 'events.jsonl').read_bytes(), original)
            path.write_bytes(b'{"type":"altered"}\r\n')
            with self.assertRaisesRegex(ValueError, 'does not match'):
                evidence.build_index(run)

    def test_explicit_file_byte_encoding_is_verified(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            (run / 'private').mkdir()
            data = b'{"type":"result"}\r\n'
            (run / 'private/task1-build.transcript.jsonl').write_bytes(data)
            calibration.append(run / 'events.jsonl', {
                'event': 'completed', 'task_id': 'task1', 'stage': 'build',
                'transcript_sha256': evidence.sha(data), 'transcript_sha256_encoding': 'file-bytes',
            })
            row = evidence.build_index(run)['transcripts'][0]
            self.assertEqual(row['recorded_sha256'], row['file_bytes_sha256'])


if __name__ == '__main__':
    unittest.main()
