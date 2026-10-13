"""離線合成資料測試；不呼叫 niio，也不包含客戶憑證或資料。"""
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/mcp/niio-mcp-app-builder/build/scripts"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


refresh = load("refresh_fields")
sys.path.insert(0, str(SCRIPTS))
fill = load("generate_fill_templates")


class RefreshTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.responses = self.root / "responses"
        self.responses.mkdir()
        self.context = {"appId": "app-test", "worksheetIdByName": {"請購單": "ws-a", "廠商": "ws-b"},
                        "progress": "worksheets_created"}
        self.fields = [
            {"id": "f-name", "name": "名稱", "alias": "title", "type": "Text"},
            {"id": "f-choice", "name": "狀態", "type": "SingleSelect", "options": [
                {"key": "k1", "value": "處理中", "index": 1, "isDelete": False},
                {"key": "k2", "value": "舊值", "index": 2, "isDelete": True}]},
            {"id": "f-rel", "name": "廠商", "alias": "vendor", "type": "Relation",
             "dataSource": "ws-b", "sourceField": "f-back", "relation": {"multiple": False}},
            {"id": "f-formula", "name": "總額", "type": "Formula"},
            {"id": "ctime", "name": "建立時間", "type": "DateTime"}]
        for field in self.fields:
            field["isReadOnly"] = False
            field["isTitle"] = field["id"] == "f-name"
        self.entries = {}
        for ws_id in ("ws-a", "ws-b"):
            self.entries[ws_id] = {"appId": "app-test", "worksheetId": ws_id,
                "response": {"success": True, "data": {"worksheetId": ws_id,
                    "fields": copy.deepcopy(self.fields)}}}
        self.context_path = self.root / "hap-context.json"
        self.output = self.root / "worksheetContext.json"
        self.output.write_text("previous-valid-output")
        self.save()

    def save(self):
        self.context_path.write_text(json.dumps(self.context), encoding="utf-8")
        for ws_id, entry in self.entries.items():
            (self.responses / (ws_id + ".json")).write_text(json.dumps(entry), encoding="utf-8")

    def run_script(self):
        return subprocess.run([sys.executable, str(SCRIPTS / "refresh_fields.py"),
            "--responses-dir", str(self.responses), str(self.context_path)], capture_output=True, text=True)

    def assert_failure_preserves_output(self):
        before = self.context_path.read_bytes()
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.output.read_text(), "previous-valid-output")
        self.assertEqual(self.context_path.read_bytes(), before)

    def test_multiple_worksheets_and_downstream(self):
        before = self.context_path.read_bytes()
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(self.output.read_text())
        self.assertEqual([i["worksheetId"] for i in data], ["ws-a", "ws-b"])
        self.assertEqual([len(i["fields"]) for i in data], [5, 5])
        self.assertEqual(data[0]["fields"][1]["options"], [self.fields[1]["options"][0]])
        self.assertEqual(data[0]["fields"][2]["sourceField"], "f-back")
        self.assertEqual(data[0]["fields"][2]["relation"], {"multiple": False})
        templates = fill.generate_fill_templates(data)
        self.assertEqual(templates[0]["fieldCount"], 3)
        self.assertEqual(templates[0]["fillableFields"][1]["validOptions"], ["處理中"])
        self.assertEqual(templates[0]["relationDeps"], ["廠商"])
        self.assertEqual(self.context_path.read_bytes(), before)

    def test_missing_response(self):
        (self.responses / "ws-b.json").unlink()
        self.assert_failure_preserves_output()

    def test_metadata_preserved_without_defaults(self):
        original = self.entries['ws-a']['response']['data']['fields']
        original[0].update(required=True, subType={'kind': 'date'}, isReadOnly=True)
        del original[1]['isTitle']
        del original[1]['isReadOnly']
        self.save()
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        fields = json.loads(self.output.read_text())[0]['fields']
        for key in ('required', 'subType', 'isTitle', 'isReadOnly'):
            self.assertEqual(fields[0][key], original[0][key])
        self.assertNotIn('isTitle', fields[1])
        self.assertNotIn('isReadOnly', fields[1])

    def test_wrong_application(self):
        self.entries["ws-b"]["appId"] = "other-app"
        self.save()
        self.assert_failure_preserves_output()

    def test_wrong_worksheet(self):
        self.entries["ws-b"]["response"]["data"]["worksheetId"] = "other-sheet"
        self.save()
        self.assert_failure_preserves_output()

    def test_empty_fields(self):
        self.entries["ws-b"]["response"]["data"]["fields"] = []
        self.save()
        self.assert_failure_preserves_output()

    def test_failed_tool_response(self):
        self.entries["ws-b"]["response"] = {"success": False, "message": "sensitive-response-content"}
        self.save()
        self.assert_failure_preserves_output()
        result = self.run_script()
        self.assertNotIn("sensitive-response-content", result.stderr + result.stdout)

    def test_invalid_json(self):
        (self.responses / "ws-b.json").write_text('{"success":')
        self.assert_failure_preserves_output()

    def test_duplicate_field(self):
        self.entries["ws-b"]["response"]["data"]["fields"].append(self.fields[0])
        self.save()
        self.assert_failure_preserves_output()

    def test_numeric_type_rejected(self):
        self.entries["ws-b"]["response"]["data"]["fields"][0]["type"] = 2
        self.save()
        self.assert_failure_preserves_output()

    def test_atomic_replace_failure(self):
        with patch.object(refresh.os, "replace", side_effect=OSError("blocked")):
            with self.assertRaises(OSError):
                refresh.write_atomic(self.output, [{"fields": self.fields}])
        self.assertEqual(self.output.read_text(), "previous-valid-output")
        self.assertFalse(list(self.root.glob(".worksheetContext-*.tmp")))


class FillTests(unittest.TestCase):
    def field(self, id, type='Text', **extra):
        return dict(id=id, name=id, type=type, isTitle=False, isReadOnly=False, **extra)

    def generate(self, fields):
        return fill.generate_fill_templates([{'worksheetId': 'a', 'worksheetName': '單據', 'fields': fields}])[0]

    def test_non_text_title_and_readonly_title(self):
        for kind, readonly in [('Date', False), ('AutoNumber', True)]:
            title = self.field('true-title', kind)
            title.update(isTitle=True, isReadOnly=readonly)
            result = self.generate([self.field('address'), title])
            self.assertEqual([f['id'] for f in result['titleFields']], ['true-title'])
            self.assertFalse(result['fillableFields'][0]['isTitle'])
            self.assertEqual(len(result['fillableFields']), 1 if readonly else 2)
            self.assertFalse(result['requiresReview'])

    def test_aliasless_relations_and_computed_fields(self):
        fields = [self.field(str(i), 'Relation', alias='', dataSource='b', sourceField='back', relation={'multiple': True}) for i in range(13)]
        fields[0]['isTitle'] = True
        readonly = self.field('readonly', 'Relation', alias='vendor', dataSource='c')
        readonly['isReadOnly'] = True
        fields += [readonly] + [self.field('rollup-' + str(i), 'Rollup') for i in range(8)]
        result = self.generate(fields)
        self.assertEqual(result['fieldCount'], 13)
        self.assertEqual([f['fieldKey'] for f in result['fillableFields']], [str(i) for i in range(13)])
        self.assertEqual(result['relationDeps'], ['b'])
        self.assertEqual(result['fillableFields'][0]['sourceField'], 'back')
        self.assertEqual(len(result['excludedFields']), 9)

    def test_unknown_metadata_and_title_review(self):
        field = self.field('unknown')
        del field['isReadOnly']
        del field['isTitle']
        result = self.generate([field])
        self.assertTrue(result['requiresReview'])
        self.assertEqual(result['fillableFields'], [])
        self.assertEqual(result['titleFields'], [])
        field['isReadOnly'] = 'false'
        self.assertEqual(self.generate([field])['fillableFields'], [])
        fields = [self.field('one'), self.field('two')]
        for f in fields:
            f['isTitle'] = True
        self.assertTrue(self.generate(fields)['requiresReview'])

    def test_duplicate_key_failure_preserves_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory)/'input.json', Path(directory)/'fillTemplates.json'
            source.write_text(json.dumps([{'worksheetId': 'a', 'worksheetName': '單據', 'fields': [self.field('one', alias='same'), self.field('two', alias='same')]}]))
            output.write_bytes(b'previous')
            result = subprocess.run([sys.executable, str(SCRIPTS/'generate_fill_templates.py'), str(source)], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(output.read_bytes(), b'previous')


if __name__ == "__main__":
    unittest.main()
