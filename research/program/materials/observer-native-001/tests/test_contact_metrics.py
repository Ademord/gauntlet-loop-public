"""Contact accounting tests use captured fixture events, never real conversations."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest

from tools import contact_metrics as contacts
from tools import observer


SESSION = 'codex:contact-fixture'
PROVENANCE = {'actor': 'human', 'source': 'fixture-user-classification'}


class ContactMetricsTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.db = Path(temporary.name) / 'observer.sqlite3'
        observer.register_session(self.db, SESSION, 'fixture-task', {'host': 'fixture'})

    def event(self, name='UserPromptSubmit', session=SESSION):
        return observer.ingest_hook(self.db, {'session_id': session, 'hook_event_name': name,
                                              'prompt': 'PRIVATE_MESSAGE_NEVER_NEEDED'})['event_id']

    def label(self, event_id, label, **kwargs):
        return contacts.label_contact(self.db, SESSION, event_id, label, **dict(PROVENANCE, **kwargs))

    def resolution(self, state, event_id=None, **kwargs):
        return contacts.record_resolution(self.db, SESSION, state, event_id=event_id,
                                          **dict(PROVENANCE, **kwargs))

    def report(self):
        return contacts.session_report(self.db, SESSION)

    def test_unclassified_or_explicit_unknown_is_not_zero_corrections(self):
        initial, followup = self.event(), self.event()
        self.label(initial, 'initial_request')
        self.resolution('resolved', followup)
        for classify_unknown in (False, True):
            if classify_unknown:
                self.label(followup, 'unknown')
            report = self.report()
            self.assertEqual(report['observed_user_messages'], 2)
            self.assertEqual(report['observed_followups_after_first_contact'], 1)
            self.assertEqual(report['known_correction_count'], 0)
            self.assertEqual(report['unclassified_count'], 1)
            self.assertIsNone(report['correction_total'])
            self.assertIsNone(report['first_pass_resolution'])
            self.assertEqual(report['coverage']['status'], 'partial')
            self.assertEqual(report['metric_scope'], 'captured_contact_records_only')

    def test_relabeling_changes_current_count_without_rewriting_history(self):
        event_id = self.event()
        self.label(event_id, 'correction', source='initial-auditor-label', actor='auditor')
        before = self.report()['label_history'][0]
        revised = self.label(event_id, 'scope_change', source='user-correction-of-label')
        report = self.report()
        self.assertEqual(revised['revision'], 2)
        self.assertEqual(report['label_history'][0], before)
        self.assertEqual(len(report['label_history']), 2)
        self.assertEqual(len(report['current_labels']), 1)
        self.assertEqual(report['current_labels'][0]['label'], 'scope_change')
        self.assertEqual(report['correction_total'], 0)
        self.assertEqual(report['known_separate_request_count'], 1)

    def test_labels_reject_wrong_event_session_kind_and_unsupported_classification(self):
        valid = self.event()
        stop = self.event('Stop')
        observer.register_session(self.db, 'other-session', 'other-task', {'host': 'fixture'})
        other = self.event(session='other-session')
        for event_id in (stop, other, 999999, True):
            with self.subTest(event_id=event_id), self.assertRaises(ValueError):
                self.label(event_id, 'correction')
        for label in ('accepted', 'repair_inferred_from_stop'):
            with self.subTest(label=label), self.assertRaises(ValueError):
                self.label(valid, label)
        with self.assertRaises(ValueError):
            contacts.label_contact(self.db, 'missing-session', valid, 'correction', **PROVENANCE)
        self.assertEqual(self.report()['label_history'], [])

    def test_provenance_is_required_and_does_not_accept_worker_as_classifier(self):
        event_id = self.event()
        for kwargs in ({'actor': 'worker'}, {'source': ''}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.label(event_id, 'correction', **kwargs)
        self.assertEqual(self.report()['label_history'], [])

    def test_confirmation_and_approval_do_not_inflate_work_contacts(self):
        initial, approval, confirmation = self.event(), self.event(), self.event()
        for event_id, label in ((initial, 'initial_request'), (approval, 'approval'), (confirmation, 'confirmation')):
            self.label(event_id, label)
        self.resolution('resolved', confirmation)
        report = self.report()
        self.assertEqual(report['contacts_to_resolution'], 3)
        self.assertEqual(report['work_contacts_to_resolution'], 1)
        self.assertEqual(report['work_contact_total'], 1)
        self.assertEqual(report['correction_total'], 0)
        self.assertTrue(report['first_pass_resolution'])

    def test_correction_and_clarification_are_distinct_additional_work(self):
        initial, clarification, correction, confirmation = [self.event() for _ in range(4)]
        for event_id, label in zip((initial, clarification, correction, confirmation),
                                   ('initial_request', 'clarification_response', 'correction', 'confirmation')):
            self.label(event_id, label)
        self.resolution('resolved', confirmation)
        report = self.report()
        self.assertEqual(report['correction_total'], 1)
        self.assertEqual(report['work_contacts_to_resolution'], 3)
        self.assertFalse(report['first_pass_resolution'])

    def test_changed_scope_and_new_request_do_not_become_original_repairs(self):
        initial, changed, new, confirmation = [self.event() for _ in range(4)]
        for event_id, label in zip((initial, changed, new, confirmation),
                                   ('initial_request', 'scope_change', 'new_request', 'confirmation')):
            self.label(event_id, label)
        self.resolution('resolved', confirmation)
        report = self.report()
        self.assertEqual(report['correction_total'], 0)
        self.assertEqual(report['known_separate_request_count'], 2)
        self.assertEqual(report['work_contact_total'], 3)
        self.assertIsNone(report['first_pass_resolution'])

    def test_stop_and_independent_outcome_do_not_create_user_resolution(self):
        initial = self.event()
        self.label(initial, 'initial_request')
        self.event('Stop')
        observer.record_outcome(self.db, SESSION, artifact_hash='a' * 64, check_hash='b' * 64,
                                evaluator='fixture-checker', evidence='fixture-check-log', outcome='passed')
        report = self.report()
        self.assertIsNone(report['resolution'])
        self.assertIsNone(report['first_pass_resolution'])
        self.assertIsNone(report['contacts_to_resolution'])
        self.assertEqual(report['observed_user_messages'], 1)

    def test_resolution_history_is_user_reported_and_reopening_is_retained(self):
        initial, confirmation = self.event(), self.event()
        self.label(initial, 'initial_request')
        self.label(confirmation, 'confirmation')
        self.resolution('resolved', confirmation)
        before = self.report()['resolution_history'][0]
        self.resolution('reopened', confirmation, source='user-reopened')
        self.assertEqual(self.report()['resolution']['state'], 'reopened')
        self.assertIsNone(self.report()['contacts_to_resolution'])
        self.resolution('resolved', confirmation, source='user-resolved-again')
        report = self.report()
        self.assertEqual(report['resolution_history'][0], before)
        self.assertEqual(len(report['resolution_history']), 3)
        self.assertTrue(all(row['basis'] == 'user_reported' for row in report['resolution_history']))
        self.assertFalse(report['first_pass_resolution'])

    def test_resolution_requires_valid_contact_or_evidence_without_guessing_cutoff(self):
        initial = self.event()
        stop = self.event('Stop')
        self.label(initial, 'initial_request')
        with self.assertRaises(ValueError):
            self.resolution('resolved')
        with self.assertRaises(ValueError):
            self.resolution('resolved', stop)
        with self.assertRaises(ValueError):
            self.resolution('accepted', initial)
        self.resolution('resolved', evidence='user-confirmation-reference')
        report = self.report()
        self.assertEqual(report['resolution']['state'], 'resolved')
        self.assertIsNone(report['contacts_to_resolution'])
        self.assertIsNone(report['first_pass_resolution'])

    def test_auditor_resolution_requires_explicit_user_evidence_even_with_contact(self):
        event_id = self.event()
        for kwargs in ({}, {'evidence': ''}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.resolution('resolved', event_id, actor='auditor', source='auditor-inspection', **kwargs)
        self.assertEqual(self.report()['resolution_history'], [])
        self.resolution('resolved', event_id, actor='auditor', source='auditor-inspection',
                        evidence='user-resolution-statement-reference')
        reported = self.report()['resolution']
        self.assertEqual(reported['actor'], 'auditor')
        self.assertEqual(reported['basis'], 'user_reported')
        self.assertEqual(reported['evidence'], 'user-resolution-statement-reference')

    def test_active_minutes_need_explicit_finite_reported_values_and_basis(self):
        first, second = self.event(), self.event()
        for value in (True, -1, float('nan'), float('inf'), 10 ** 1000):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.label(first, 'initial_request', human_minutes=value, minutes_basis='user-timed')
        with self.assertRaises(ValueError):
            self.label(first, 'initial_request', human_minutes=1)
        self.label(first, 'initial_request', human_minutes=1.5, minutes_basis='user-timed')
        self.label(second, 'confirmation')
        report = self.report()
        self.assertEqual(report['known_reported_human_minutes'], 1.5)
        self.assertIsNone(report['human_minutes'])
        self.label(second, 'confirmation', human_minutes=0, minutes_basis='user-reported-zero')
        self.assertEqual(self.report()['human_minutes'], 1.5)

    def test_overflowing_reported_minute_total_stays_unknown_and_serializable(self):
        for label in ('initial_request', 'confirmation'):
            self.label(self.event(), label, human_minutes=1e308, minutes_basis='fixture-reported')
        report = self.report()
        self.assertIsNone(report['human_minutes'])
        self.assertIsNone(report['known_reported_human_minutes'])
        self.assertEqual(report['human_minutes_status'], 'overflow')
        json.dumps(report, allow_nan=False)

    def test_no_observations_or_missing_database_does_not_manufacture_zero_totals(self):
        report = self.report()
        self.assertEqual(report['observed_user_messages'], 0)
        self.assertIsNone(report['correction_total'])
        self.assertIsNone(report['human_minutes'])
        self.assertIsNone(report['first_pass_resolution'])
        missing = self.db.parent / 'missing.sqlite3'
        with self.assertRaises(ValueError):
            contacts.init_tables(missing)
        self.assertFalse(missing.exists())

    def test_cli_labels_and_reports_without_message_text(self):
        event_id = self.event()
        output = io.StringIO()
        with redirect_stdout(output):
            rc = contacts.main(['--db', str(self.db), 'label', SESSION, str(event_id), 'initial_request',
                                '--actor', 'auditor', '--source', 'fixture-classification'])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(output.getvalue())['revision'], 1)
        output = io.StringIO()
        with redirect_stdout(output):
            rc = contacts.main(['--db', str(self.db), 'report', SESSION])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(output.getvalue())['observed_user_messages'], 1)
        self.assertNotIn('PRIVATE_MESSAGE_NEVER_NEEDED', output.getvalue())


if __name__ == '__main__':
    unittest.main()
