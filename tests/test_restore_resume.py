"""Fault injection uses real, distinct old/new files and real directory renames."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('resume_installer', ROOT/'scripts/install_bundle.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class RestoreResumeTests(unittest.TestCase):
    def fixture(self, root, old_count=8, identical=False):
        old, new, target = root/'old', root/'new', root/'target'
        target.mkdir()
        for i in range(8):
            name = f'niio-skill-{i}'
            for directory, version in ((old, 'old'), (new, 'old' if identical else 'new')):
                skill = directory/'skills'/'category'/name
                skill.mkdir(parents=True)
                (skill/'SKILL.md').write_text(f'{version}-{i}', encoding='utf-8')
            if i < old_count:
                shutil.copytree(old/'skills'/'category'/name, target/name)
        return old, new, target

    def assert_restored(self, receipt, old, target, old_count):
        for i in range(8):
            name = f'niio-skill-{i}'
            if i < old_count:
                self.assertEqual(installer.inventory(target/name),
                                 installer.inventory(old/'skills'/'category'/name))
            else:
                self.assertFalse((target/name).exists())
        data = json.loads(receipt.read_text(encoding='utf-8'))
        self.assertEqual(data['state'], 'restored')
        self.assertTrue(all(e['restoreState'] == 'restored' for e in data['entries']))
        self.assertFalse((target/'.niio-install.lock').exists())

    def fail_move(self, fail_at, after=False):
        original = Path.rename
        calls = [0]
        def rename(source, destination):
            calls[0] += 1
            if calls[0] == fail_at:
                if after:
                    original(source, destination)
                raise OSError('injected rename failure')
            return original(source, destination)
        return patch.object(Path, 'rename', rename)

    def test_every_restore_move_before_and_after_then_resume_twice(self):
        # Both move phases at every skill; fresh, mixed and full updates.
        for old_count in (0, 4, 8):
            for move in range(1, 9 + old_count):
                for after in (False, True):
                    with self.subTest(old_count=old_count, move=move, after=after), tempfile.TemporaryDirectory() as tmp:
                        old, new, target = self.fixture(Path(tmp), old_count)
                        receipt = installer.install(new, target, old)
                        with self.fail_move(move, after), self.assertRaises(OSError):
                            installer.restore(receipt)
                        self.assertEqual(json.loads(receipt.read_text())['state'], 'restoring')
                        installer.restore(receipt)
                        self.assert_restored(receipt, old, target, old_count)
                        with patch.object(Path, 'rename', side_effect=AssertionError('Repeated restore moved files')):
                            installer.restore(receipt)
                        self.assert_restored(receipt, old, target, old_count)

    def test_receipt_replace_failures_at_checkpoint_boundaries(self):
        # Before/after the start, each move checkpoint, a completed item, and final state.
        for checkpoint in (1, 2, 3, 4, 5, 6, 34):
            for after in (False, True):
                with self.subTest(checkpoint=checkpoint, after=after), tempfile.TemporaryDirectory() as tmp:
                    old, new, target = self.fixture(Path(tmp))
                    receipt = installer.install(new, target, old)
                    original, calls = installer.os.replace, [0]
                    def replace(source, destination):
                        calls[0] += 1
                        if calls[0] == checkpoint:
                            if after:
                                original(source, destination)
                            raise OSError('injected receipt replace failure')
                        return original(source, destination)
                    with patch.object(installer.os, 'replace', replace), self.assertRaises(OSError):
                        installer.restore(receipt)
                    self.assertEqual(list(receipt.parent.glob('.receipt-*.tmp')), [])
                    installer.restore(receipt)
                    installer.restore(receipt)
                    self.assert_restored(receipt, old, target, 8)

    def test_identical_versions_and_legacy_partial_receipt(self):
        for identical in (False, True):
            with self.subTest(identical=identical), tempfile.TemporaryDirectory() as tmp:
                old, new, target = self.fixture(Path(tmp), identical=identical)
                receipt = installer.install(new, target, old)
                # Simulate the previous implementation: some renames, no per-item journal.
                data = json.loads(receipt.read_text())
                for entry in list(reversed(data['entries']))[:2]:
                    name = entry['name']
                    (target/name).rename(receipt.parent/(name+'.restored-new'))
                    (receipt.parent/name).rename(target/name)
                installer.restore(receipt)
                installer.restore(receipt)
                self.assert_restored(receipt, old, target, 8)

    def test_custom_changes_remain_blocked_in_all_restore_locations(self):
        for location in ('pending', 'restored', 'backup', 'saved', 'completed'):
            with self.subTest(location=location), tempfile.TemporaryDirectory() as tmp:
                old, new, target = self.fixture(Path(tmp))
                receipt = installer.install(new, target, old)
                names = [e['name'] for e in reversed(json.loads(receipt.read_text())['entries'])]
                if location == 'completed':
                    installer.restore(receipt)
                else:
                    with self.fail_move(3), self.assertRaises(OSError):
                        installer.restore(receipt)
                places = {'pending':target/names[1], 'restored':target/names[0],
                          'backup':receipt.parent/names[1],
                          'saved':receipt.parent/(names[0]+'.restored-new'), 'completed':target/names[0]}
                custom = places[location]/'custom.txt'
                custom.write_text('keep custom bytes', encoding='utf-8')
                with patch.object(Path, 'rename', side_effect=AssertionError('Preflight mutated files')):
                    with self.assertRaises(ValueError):
                        installer.restore(receipt)
                self.assertEqual(custom.read_text(), 'keep custom bytes')
                custom.unlink()  # Remove only this test's injected change, then resume.
                installer.restore(receipt)
                self.assert_restored(receipt, old, target, 8)

    def test_install_and_automatic_restore_failures_can_resume(self):
        for install_move in (1, 2, 7, 8, 16):
            for restore_move in (1, 2):
                with self.subTest(install_move=install_move, restore_move=restore_move), tempfile.TemporaryDirectory() as tmp:
                    old, new, target = self.fixture(Path(tmp))
                    original, calls = Path.rename, [0]
                    def rename(source, destination):
                        calls[0] += 1
                        if calls[0] in (install_move, install_move + restore_move):
                            raise OSError('failure-' + str(calls[0]))
                        return original(source, destination)
                    with patch.object(Path, 'rename', rename), self.assertRaises(OSError) as error:
                        installer.install(new, target, old)
                    receipt = next(Path(tmp).glob('.niio-backup-*/receipt.json'))
                    # Early install failures may require no rollback moves at all.
                    if calls[0] >= install_move + restore_move:
                        self.assertIn('automatic restore failed', str(error.exception))
                        self.assertIn(str(receipt), str(error.exception))
                        self.assertIn('failure-' + str(install_move), str(error.exception))
                    installer.restore(receipt)
                    installer.restore(receipt)
                    self.assert_restored(receipt, old, target, 8)


if __name__ == '__main__':
    unittest.main()
