import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / 'skills/mcp/niio-mcp-app-builder/scripts/mcp_preflight.py'
spec = importlib.util.spec_from_file_location('mcp_preflight', HELPER)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.structure = {'worksheetId': 'tasks', 'appId': 'app', 'views': [{'id': 'approved'}], 'fields': [
            {'id': 'title', 'alias': 'name', 'type': 'Text', 'required': True},
            {'id': 'amount', 'type': 'Number'},
            {'id': 'readonly', 'type': 'Text', 'isReadOnly': True},
        ]}
        self.request = {'appId': 'app', 'worksheet_id': 'tasks', 'fields': [
            {'id': 'name', 'value': 'Synthetic task'}, {'id': 'amount', 'value': 30}]}

    def test_valid_record_and_original_payload_preserved(self):
        before = copy.deepcopy(self.request)
        self.assertEqual(guard.record_issues(self.structure, self.request, 'create'), [])
        self.assertEqual(self.request, before)

    def test_invalid_numbers_blocked_including_bool_nan_and_infinity(self):
        for value in ('30abc', '30', True, float('nan'), float('inf'), None, [], ''):
            with self.subTest(value=value):
                self.request['fields'][1]['value'] = value
                self.assertTrue(guard.record_issues(self.structure, self.request, 'update'))

    def test_zero_negative_and_fraction_are_valid(self):
        for value in (0, -30, 1.5):
            self.request['fields'][1]['value'] = value
            self.assertEqual(guard.record_issues(self.structure, self.request, 'update'), [])

    def test_explicit_clear_is_distinct_from_invalid_input(self):
        self.request['fields'][1]['value'] = ''
        self.assertTrue(guard.record_issues(self.structure, self.request, 'update'))
        self.assertEqual(guard.record_issues(self.structure, self.request, 'update', ['amount']), [])

    def test_required_create_and_partial_update(self):
        self.request['fields'] = [{'id': 'amount', 'value': 30}]
        self.assertTrue(guard.record_issues(self.structure, self.request, 'create'))
        self.assertEqual(guard.record_issues(self.structure, self.request, 'update'), [])
        self.request['fields'] = [{'id': 'name', 'value': '  '}]
        self.assertTrue(guard.record_issues(self.structure, self.request, 'update'))

    def test_wrong_scope_unknown_readonly_and_duplicate_fields_blocked(self):
        for field in ({'id': 'missing', 'value': 1}, {'id': 'readonly', 'value': 'x'}, {'id': 'title', 'value': 'duplicate'}):
            with self.subTest(field=field):
                request = copy.deepcopy(self.request)
                request['fields'].append(field)
                self.assertTrue(guard.record_issues(self.structure, request, 'update'))
        self.request['worksheet_id'] = 'other'
        self.assertTrue(guard.record_issues(self.structure, self.request, 'update'))

    def test_list_requires_matching_explicit_view_and_fields(self):
        request = {'appId': 'app', 'worksheet_id': 'tasks', 'viewId': 'approved',
                   'fields': ['title', 'amount'], 'useFieldIdAsKey': True, 'pageIndex': 1, 'pageSize': 3}
        self.assertEqual(guard.list_issues(self.structure, request), [])
        for change in ({'viewId': None}, {'viewId': 'other'}, {'fields': ['madeup']}, {'pageSize': True}):
            self.assertTrue(guard.list_issues(self.structure, {**request, **change}))

    def test_corrupt_snapshot_in_nested_mcp_text_is_rejected(self):
        corrupt = json.dumps({'_children': [{'_value': 'option-key'}], '_nodeFactory': {}})
        snapshot = {'content': [{'type': 'text', 'text': json.dumps({'data': {'value': corrupt}})}]}
        self.assertTrue(guard.snapshot_issues(snapshot))
        self.assertEqual(guard.snapshot_issues({'value': 'option-key'}), [])
        self.assertEqual(guard.snapshot_issues({'value': ['valid', 'array']}), [])

    def test_cli_invalid_input_nonzero_without_echoing_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'structure.json').write_text(json.dumps(self.structure), encoding='utf-8')
            self.request['fields'][1]['value'] = 'private-invalid-text'
            (root / 'request.json').write_text(json.dumps(self.request), encoding='utf-8')
            result = subprocess.run([sys.executable, str(HELPER), 'record', '--mode', 'update',
                                     '--structure', str(root / 'structure.json'), '--request', str(root / 'request.json')],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertFalse(json.loads(result.stdout)['valid'])
            self.assertNotIn('private-invalid-text', result.stdout)


if __name__ == '__main__':
    unittest.main()
