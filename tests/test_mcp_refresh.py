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


if __name__ == "__main__":
    unittest.main()
