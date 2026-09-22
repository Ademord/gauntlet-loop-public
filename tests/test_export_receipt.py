"""Synthetic transport-result qualification; no renderer or external calls."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from export_receipt import check_export_receipt


class ExportReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent)
        self.addCleanup(self.temp.cleanup)
        self.target = Path(self.temp.name) / 'result.pdf'
        self.artifact = b'synthetic transport bytes; deliberately not a valid PDF'
        self.target.write_bytes(self.artifact)
        self.html = '<p>Grüsse, data & evidence</p>'.encode('utf-8')
        self.options = {'path': str(self.target), 'format': 'A4',
                        'margin': {'top': '10mm'}, 'print_background': True}
        self.receipt = {'html_sha256': hashlib.sha256(self.html).hexdigest(),
                        'html_utf8_bytes': len(self.html),
                        'pdf_sha256': hashlib.sha256(self.artifact).hexdigest(),
                        'pdf_bytes': len(self.artifact), 'pdf_options_python': self.options,
                        'transport': 'synthetic control'}

    def check(self, receipt=None, **changes):
        arguments = {'returncode': 0, 'stdout': json.dumps(self.receipt if receipt is None else receipt).encode(),
                     'target': self.target, 'html_raw': self.html, 'options': self.options}
        arguments.update(changes)
        return check_export_receipt(**arguments)

    def test_clean_pretty_json_and_utf8_bom(self):
        raw = json.dumps(self.receipt, indent=2)
        for stdout in (raw, raw.encode(), b'\xef\xbb\xbf'+raw.encode(), '\ufeff'+raw):
            with self.subTest(kind=type(stdout).__name__):
                self.assertEqual(self.check(stdout=stdout), self.receipt)

    def test_mixed_logs_json_lines_and_unrelated_records(self):
        stale = dict(self.receipt, html_sha256='0'*64)
        raw = '\n'.join(['starting export', json.dumps({'progress': 1}), '[1, 2]',
                         json.dumps(stale), json.dumps(self.receipt), 'done'])
        self.assertEqual(self.check(stdout=raw), self.receipt)

    def test_nonzero_cannot_be_rescued_by_success_receipt(self):
        for code in (1, -1, 7, False, None, '0'):
            with self.subTest(returncode=code), self.assertRaisesRegex(ValueError, 'did not exit successfully'):
                self.check(returncode=code)

    def test_exit_zero_without_usable_stdout_is_rejected(self):
        for stdout in (b'', b' \r\n', b'not a receipt', b'{}', b'[]', b'null', b'\xff'):
            with self.subTest(stdout=stdout), self.assertRaises(ValueError):
                self.check(stdout=stdout)

    def test_expected_artifact_must_exist_and_be_nonempty_file(self):
        for target in (self.target.parent/'absent.pdf', self.target.parent):
            with self.subTest(target=target.name), self.assertRaises(ValueError):
                self.check(target=target)
        self.target.write_bytes(b'')
        empty_receipt = dict(self.receipt, pdf_sha256=hashlib.sha256(b'').hexdigest(), pdf_bytes=0)
        with self.assertRaisesRegex(ValueError, 'empty'):
            self.check(empty_receipt)

    def test_each_current_identity_and_options_must_match(self):
        mutations = {
            'html_sha256': '0'*64, 'html_utf8_bytes': len(self.html)+1,
            'pdf_sha256': '0'*64, 'pdf_bytes': len(self.artifact)+1,
            'pdf_options_python': dict(self.options, format='Letter'),
        }
        for key, value in mutations.items():
            with self.subTest(field=key), self.assertRaisesRegex(ValueError, 'found 0'):
                self.check(dict(self.receipt, **{key: value}))
        with self.assertRaises(ValueError):
            self.check(html_raw=self.html+b'changed')
        self.target.write_bytes(self.artifact+b'changed')
        with self.assertRaises(ValueError):
            self.check()

    def test_duplicate_matching_receipts_are_rejected(self):
        line = json.dumps(self.receipt)
        with self.assertRaisesRegex(ValueError, 'found 2'):
            self.check(stdout='log\n'+line+'\n'+line+'\nfinished')

    def test_wrong_boolean_and_count_types_do_not_alias(self):
        for field in ('html_utf8_bytes', 'pdf_bytes'):
            for value in (True, str(self.receipt[field]), float(self.receipt[field])):
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    self.check(dict(self.receipt, **{field: value}))
        modified = dict(self.options, print_background=1)
        with self.assertRaises(ValueError):
            self.check(dict(self.receipt, pdf_options_python=modified))

    def test_missing_fields_duplicate_keys_and_nonfinite_options_rejected(self):
        for field in ('html_sha256', 'html_utf8_bytes', 'pdf_sha256', 'pdf_bytes', 'pdf_options_python'):
            receipt = dict(self.receipt)
            del receipt[field]
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.check(receipt)
        raw = json.dumps(self.receipt)
        with self.assertRaises(ValueError):
            self.check(stdout=raw[:-1]+', "pdf_bytes": '+str(len(self.artifact))+'}')
        options = dict(self.options, scale=float('nan'))
        with self.assertRaises(ValueError):
            self.check(dict(self.receipt, pdf_options_python=options), options=options)

    def test_json_numeric_value_and_key_order_compatibility(self):
        options = dict(self.options, scale=1.0, allowed_sizes=[1, 2])
        equivalent = dict(reversed(list(dict(options, scale=1).items())))
        self.assertEqual(self.check(dict(self.receipt, pdf_options_python=equivalent), options=options)
                         ['pdf_options_python'], equivalent)
        with self.assertRaises(ValueError):
            self.check(dict(self.receipt, pdf_options_python=dict(equivalent, allowed_sizes=[2, 1])), options=options)

    def test_checker_does_not_modify_inputs_or_artifact(self):
        options = copy.deepcopy(self.options)
        receipt = copy.deepcopy(self.receipt)
        files = set(self.target.parent.iterdir())
        self.check()
        self.assertEqual(self.target.read_bytes(), self.artifact)
        self.assertEqual(self.options, options)
        self.assertEqual(self.receipt, receipt)
        self.assertEqual(set(self.target.parent.iterdir()), files)

    def test_matching_receipt_is_not_pdf_validity_or_fresh_execution(self):
        self.assertFalse(self.artifact.startswith(b'%PDF'))
        self.assertEqual(self.check(), self.receipt)
        # Reusing the same receipt/artifact still passes; freshness is a separate
        # controller obligation, not something this narrow checker can infer.
        self.assertEqual(self.check(), self.receipt)


if __name__ == '__main__':
    unittest.main()
