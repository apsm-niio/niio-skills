import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/mcp/niio-mcp-app-builder'
spec = importlib.util.spec_from_file_location('project_files_test', SKILL / 'scripts/project_files.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class ProjectFilesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def put(self, name, value):
        p = self.root / name
        p.write_text(json.dumps(value, ensure_ascii=False))
        return p

    def legacy(self):
        self.put('hap-plan.json', {'appName': '測試', 'org_id': 'org-test'})
        self.put('hap-context.json', {'appId': 'app-test', 'progress': 'fields_refreshed'})

    def test_old_pair_migrates_with_exact_backups_and_idempotence(self):
        self.legacy()
        old = {p.name: p.read_bytes() for p in self.root.glob('*.json')}
        self.assertTrue(m.inspect_project(self.root)['plan']['needsMigration'])
        m.migrate_project(self.root)
        for name, raw in old.items():
            self.assertEqual((self.root / name.replace('hap-', 'niio-')).read_bytes(), raw)
            self.assertFalse((self.root / name).exists())
        self.assertEqual(sorted(p.read_bytes() for p in (self.root / '.niio-legacy').iterdir()), sorted(old.values()))
        self.assertFalse(m.migrate_project(self.root)['context']['needsMigration'])

    def test_conflict_preflight_changes_neither_pair(self):
        self.legacy()
        self.put('niio-context.json', {'appId': 'other'})
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        with self.assertRaises(m.ProjectFileError): m.migrate_project(self.root)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.iterdir()})

    def test_equal_json_with_different_format_keeps_current_bytes(self):
        self.legacy()
        current = self.root / 'niio-plan.json'
        current.write_text('{ "org_id": "org-test", "appName": "測試" }\n')
        raw = current.read_bytes()
        m.migrate_project(self.root)
        self.assertEqual(current.read_bytes(), raw)

    def test_invalid_and_duplicate_json_and_type_conflict_block(self):
        for raw in ['[]', '{', '{"a":1,"a":2}', '{"a":NaN}']:
            (self.root / 'hap-plan.json').write_text(raw)
            with self.assertRaises(m.ProjectFileError): m.migrate_project(self.root)
        self.put('hap-plan.json', {'a': True})
        self.put('niio-plan.json', {'a': 1})
        with self.assertRaises(m.ProjectFileError): m.migrate_project(self.root)

    def test_partial_migration_retries_without_overwrite(self):
        self.legacy()
        original = m._create_once
        def stop(path, raw):
            if path.name == 'niio-context.json': raise OSError('simulated interruption')
            return original(path, raw)
        with patch.object(m, '_create_once', side_effect=stop):
            with self.assertRaises(OSError): m.migrate_project(self.root)
        self.assertTrue((self.root / 'niio-plan.json').exists())
        self.assertTrue((self.root / 'hap-context.json').exists())
        m.migrate_project(self.root)
        self.assertEqual(json.loads((self.root / 'niio-context.json').read_text())['appId'], 'app-test')

    def test_symlink_lock_and_orphan_block(self):
        self.put('hap-context.json', {'progress': 'completed'})
        with self.assertRaises(m.ProjectFileError): m.migrate_project(self.root)
        self.put('hap-plan.json', {})
        (self.root / '.niio-migration.lock').touch()
        with self.assertRaises(m.ProjectFileError): m.migrate_project(self.root)
        (self.root / '.niio-migration.lock').unlink()
        (self.root / 'niio-plan.json').symlink_to(self.root / 'hap-plan.json')
        with self.assertRaises(m.ProjectFileError): m.migrate_project(self.root)

    def test_new_project_no_backup_needed(self):
        self.assertIsNone(m.migrate_project(self.root)['plan']['path'])
        self.assertFalse((self.root / '.niio-legacy').exists())
        self.put('niio-plan.json', {'org_id': 'org-test'})
        self.assertFalse(m.migrate_project(self.root)['plan']['needsMigration'])

    def test_context_resolution_old_new_and_conflict(self):
        self.legacy()
        self.assertEqual(m.resolve_context(self.root / 'niio-context.json').name, 'hap-context.json')
        m.migrate_project(self.root)
        self.assertEqual(m.resolve_context(self.root / 'hap-context.json').name, 'niio-context.json')
        self.put('hap-context.json', {'appId': 'other'})
        with self.assertRaises(m.ProjectFileError): m.resolve_context(self.root / 'niio-context.json')

    def test_scanner_is_read_only_and_reports_blocked(self):
        self.legacy()
        spec = importlib.util.spec_from_file_location('scan_test', SKILL / 'plan/scripts/scan_apps.py')
        scanner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(scanner)
        scanner.apps_dir = str(self.root.parent)
        rows = scanner.scan_apps()
        row = next(row for row in rows if row['dir'] == self.root.name)
        self.assertEqual(row['status'], 'in_progress')
        self.assertTrue(row['needsMigration'])
        self.assertFalse((self.root / 'niio-plan.json').exists())
        self.put('niio-context.json', {'appId': 'other'})
        row = next(row for row in scanner.scan_apps() if row['dir'] == self.root.name)
        self.assertEqual(row['status'], 'blocked')

if __name__ == '__main__': unittest.main()
