"""Regression checks for measurement errors found in the September study."""
import contextlib
import copy
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.paired_study import replay_measurements, run_pair, telemetry


def result_event():
    return {'type': 'result', 'num_turns': 3, 'total_cost_usd': 0.3,
            'usage': {'input_tokens': 1, 'output_tokens': 2, 'cache_read_input_tokens': 3, 'cache_creation_input_tokens': 4},
            'modelUsage': {
                'model-a': {'inputTokens': 10, 'outputTokens': 20, 'cacheReadInputTokens': 30, 'cacheCreationInputTokens': 40, 'costUSD': 0.1},
                'model-b': {'inputTokens': 5, 'outputTokens': 15, 'cacheReadInputTokens': 25, 'cacheCreationInputTokens': 45, 'costUSD': 0.2}}}


def dispatch(identifier, name='Agent', parent=None):
    return {'type': 'assistant', 'parent_tool_use_id': parent,
            'message': {'content': [{'type': 'tool_use', 'id': identifier, 'name': name,
                                     'input': {'description': 'builder, not a critic'}}]}}


class MeasurementsTest(unittest.TestCase):
    def test_model_usage_is_not_the_smaller_result_usage_sum(self):
        measured = telemetry.measure_result(result_event())
        self.assertEqual(measured['total_tokens'], 190)
        self.assertEqual(measured['result_usage_tokens'], 10)
        self.assertEqual(measured['total_tokens_source'], 'result.modelUsage')
        self.assertTrue(measured['cost_reconciles'])

    def test_missing_or_partial_model_usage_does_not_become_a_total(self):
        for alteration in ('missing', 'empty', 'partial', 'boolean', 'negative'):
            event = result_event()
            if alteration == 'missing':
                del event['modelUsage']
            elif alteration == 'empty':
                event['modelUsage'] = {}
            elif alteration == 'partial':
                del event['modelUsage']['model-b']['cacheReadInputTokens']
            else:
                event['modelUsage']['model-b']['inputTokens'] = True if alteration == 'boolean' else -1
            with self.subTest(alteration=alteration):
                measured = telemetry.measure_result(event)
                self.assertIsNone(measured['total_tokens'])
                self.assertEqual(measured['result_usage_tokens'], 10)

    def test_zero_tokens_are_observed_zero_not_unknown(self):
        event = result_event()
        for model in event['modelUsage'].values():
            for key in telemetry.MODEL_TOKEN_KEYS:
                model[key] = 0
        self.assertEqual(telemetry.measure_result(event)['total_tokens'], 0)

    def test_cost_disagreement_is_explicit_and_does_not_rescale_tokens(self):
        event = result_event()
        event['total_cost_usd'] = 0.8
        measured = telemetry.measure_result(event)
        self.assertFalse(measured['cost_reconciles'])
        self.assertEqual(measured['cost_usd'], 0.8)
        self.assertEqual(measured['total_tokens'], 190)
        del event['modelUsage']['model-b']['costUSD']
        self.assertIsNone(telemetry.measure_result(event)['cost_reconciles'])

    def test_dispatch_counts_are_unique_top_level_calls_not_critic_verdicts(self):
        events = [dispatch('a'), dispatch('a'), dispatch('b', 'Task'), dispatch('nested', parent='a'),
                  {'type': 'assistant', 'message': 'non-object message'}, 'ignored-json-string', result_event()]
        result, count, tools = telemetry.parse_stream('not json\n' + '\n'.join(json.dumps(e) for e in events))
        self.assertEqual(count, 2)
        self.assertEqual(tools, {'Agent': 1, 'Task': 1})
        self.assertEqual(result['total_cost_usd'], 0.3)

    def test_failed_or_unknown_held_out_prevents_acceptance(self):
        base = {'suite_rc': 0, 'out_of_scope': [], 'held_out_passed': True}
        self.assertTrue(telemetry.accepted_checks(base))
        self.assertTrue(telemetry.accepted_checks(dict(base, held_out_passed='not applicable')))
        for held in (False, None, 'unknown'):
            self.assertFalse(telemetry.accepted_checks(dict(base, held_out_passed=held)))
        self.assertFalse(telemetry.accepted_checks(dict(base, out_of_scope=['extra.py'])))
        self.assertFalse(telemetry.accepted_checks(dict(base, suite_rc=1)))


class PromptBindingTest(unittest.TestCase):
    def make_pair(self, root):
        prompt = 'Frozen task\nSecond line.'
        spec = b'repo: unused\n'
        spec_path = root / 'spec.yaml'
        spec_path.write_bytes(spec)
        manifest = {'spec_path': str(spec_path), 'spec_sha256': hashlib.sha256(spec).hexdigest(),
                    'order': ['A', 'B'], 'arm_prompt_sha256': {arm: hashlib.sha256(prompt.encode()).hexdigest() for arm in ('A', 'B')}}
        for arm in ('A', 'B'):
            (root / f'arm{arm}.prompt.md').write_bytes((prompt + '\n').replace('\n', '\r\n').encode())
        (root / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
        return manifest

    def test_existing_generator_hash_convention_accepts_crlf_but_not_edits(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self.make_pair(root)
            prompts = telemetry.validate_arm_prompts(root, manifest)
            self.assertEqual(prompts['A']['canonical_sha256'], manifest['arm_prompt_sha256']['A'])
            with (root / 'armB.prompt.md').open('ab') as stream:
                stream.write(b'\n')
            with self.assertRaisesRegex(ValueError, 'arm B prompt changed'):
                telemetry.validate_arm_prompts(root, manifest)

    def test_tampered_prompt_refuses_before_paid_preflight(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_pair(root)
            (root / 'armA.prompt.md').write_text('Changed task\n', encoding='utf-8')
            with patch('sys.argv', ['run_pair.py', '--pair', directory, '--execute']), \
                    patch.object(run_pair, 'preflight') as preflight, \
                    patch.object(run_pair, 'build_task_base') as build:
                with self.assertRaisesRegex(SystemExit, 'before preflight'):
                    run_pair.main()
                preflight.assert_not_called()
                build.assert_not_called()


class ReplayTest(unittest.TestCase):
    def fixture(self, root):
        event = result_event()
        row = {'task_id': 'task1', 'flag': 'F1', 'arm': 'A', 'usage': event['usage'], 'num_turns': 3,
               'total_tokens': 10, 'cost_usd': 0.3, 'reviews_used': 1, 'critic_dispatches': 1,
               'accepted': True, 'suite_rc': 0, 'out_of_scope': [], 'held_out_passed': False}
        results = root / 'results.jsonl'
        results.write_text(json.dumps(row) + '\n', encoding='utf-8')
        transcript = root / 'pairs/task1/F1/armA.transcript.jsonl'
        transcript.parent.mkdir(parents=True)
        transcript.write_text(json.dumps(dispatch('a')) + '\n' + json.dumps(event) + '\n', encoding='utf-8')
        return results, transcript, row

    def test_replay_preserves_original_and_corrects_held_out_and_tokens(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            results, transcript, original = self.fixture(root)
            before = results.read_bytes()
            with contextlib.redirect_stdout(io.StringIO()):
                code = replay_measurements.main(['--results', str(results), '--output', str(root / 'derived.jsonl'), '--report', str(root / 'report.md')])
            self.assertEqual(code, 0)
            self.assertEqual(results.read_bytes(), before)
            row = json.loads((root / 'derived.jsonl').read_text(encoding='utf-8'))
            self.assertEqual(row['total_tokens'], 190)
            self.assertFalse(row['accepted'])
            self.assertEqual(row['original_measurements']['total_tokens'], 10)
            self.assertTrue(row['original_measurements']['accepted'])
            self.assertEqual(row['replay_provenance']['transcript_sha256'], hashlib.sha256(transcript.read_bytes()).hexdigest())
            self.assertEqual(row['agent_task_dispatches'], 1)
            self.assertFalse(row['reviews_used_is_verified'])

    def test_old_rows_are_not_rebound_to_rerun_transcripts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            results, transcript, row = self.fixture(root)
            pilot = dict(row, pilot=True, cost_usd=99)
            mismatched = copy.deepcopy(row)
            mismatched['usage']['output_tokens'] = 999
            results.write_text(json.dumps(pilot) + '\n' + json.dumps(mismatched) + '\n', encoding='utf-8')
            rows, _ = replay_measurements.derive_rows(results, root / 'pairs')
            self.assertEqual(rows[0]['replay_status'], 'excluded_original_record')
            self.assertEqual(rows[1]['replay_status'], 'unmatched_transcript')
            self.assertTrue(all(r['total_tokens'] is None for r in rows))

    def test_missing_transcript_stays_unknown(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            results, transcript, row = self.fixture(root)
            transcript.unlink()
            rows, _ = replay_measurements.derive_rows(results, root / 'pairs')
            self.assertEqual(rows[0]['replay_status'], 'missing_transcript')
            self.assertIsNone(rows[0]['total_tokens'])

    def test_replay_cannot_overwrite_source_or_pair_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            results, transcript, row = self.fixture(root)
            before = results.read_bytes()
            for target in (results, transcript):
                with self.subTest(target=target), contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit):
                        replay_measurements.main(['--results', str(results), '--output', str(target), '--report', str(root / 'report.md')])
            self.assertEqual(results.read_bytes(), before)

    def test_new_hash_binding_rejects_modified_transcript_even_with_same_usage(self):
        event = result_event()
        data = json.dumps(event).encode()
        row = {'transcript_sha256': hashlib.sha256(data).hexdigest()}
        self.assertTrue(replay_measurements.bind_transcript(row, event, data)[0])
        self.assertFalse(replay_measurements.bind_transcript(row, event, data + b'\n')[0])


if __name__ == '__main__':
    unittest.main()
