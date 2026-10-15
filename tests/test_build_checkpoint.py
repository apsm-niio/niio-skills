"""Synthetic offline crash/restart scenarios; no remote API calls."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]/'skills/mcp/niio-mcp-app-builder/build/scripts'
sys.path.insert(0, str(SCRIPTS))
import build_checkpoint as checkpoint


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.context = {}
        checkpoint.change(self.context, 'init')

    def finish(self, step):
        checkpoint.change(self.context, 'begin', step)
        checkpoint.change(self.context, 'finish', step, 'synthetic verified artifact')

    def test_restart_after_every_step_and_join(self):
        for step in checkpoint.STEPS:
            self.assertIn(step, checkpoint.inspect(self.context)['nextSteps'])
            self.finish(step)
            self.context = json.loads(json.dumps(self.context))
            self.assertNotIn(step, checkpoint.inspect(self.context)['nextSteps'])
        self.assertEqual(self.context['progress'], 'completed')
        self.assertEqual(checkpoint.inspect(self.context)['nextSteps'], [])

    def test_unknown_remote_outcome_never_replayed(self):
        for target in checkpoint.STEPS:
            context = {}
            checkpoint.change(context, 'init')
            for step in checkpoint.STEPS:
                checkpoint.change(context, 'begin', step)
                if step == target:
                    restored = json.loads(json.dumps(context))
                    result = checkpoint.inspect(restored)
                    self.assertTrue(result['blocked'])
                    self.assertEqual(result['nextSteps'], [])
                    with self.assertRaises(ValueError):
                        checkpoint.change(restored, 'begin', step)
                    break
                checkpoint.change(context, 'finish', step, 'verified')

    def test_group_steps_remain_serial(self):
        for step in checkpoint.STEPS[:10]:
            self.finish(step)
        self.assertEqual(checkpoint.inspect(self.context)['nextSteps'], ['10'])
        with self.assertRaises(ValueError):
            checkpoint.change(self.context, 'begin', '11')

    def test_views_created_routes_to_sample_data(self):
        for step in ['1', '2', '3', '4', '5']:
            self.finish(step)
        self.assertEqual(self.context['progress'], 'views_created')
        self.assertEqual(checkpoint.inspect(self.context)['nextSteps'], ['6'])

    def test_legacy_failed_unknown_and_inconsistent_block(self):
        for context in [{'progress':'views_created'}, {'progress':'failed'}, {'progress':'surprise'}, {'appId':'exists'}]:
            with self.assertRaises(ValueError):
                checkpoint.inspect(context)
            with self.assertRaises(ValueError):
                checkpoint.change(context, 'init')
        self.context['progress'] = 'completed'
        with self.assertRaises(ValueError):
            checkpoint.inspect(self.context)

    def test_skipping_and_missing_evidence_rejected(self):
        with self.assertRaises(ValueError):
            checkpoint.change(self.context, 'begin', '6')
        checkpoint.change(self.context, 'begin', '1')
        with self.assertRaises(ValueError):
            checkpoint.change(self.context, 'finish', '1', '')
        self.assertTrue(checkpoint.inspect(self.context)['blocked'])

    def test_cli_readonly_locks_and_atomic_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'niio-context.json'
            path.write_text(json.dumps(self.context))
            before = path.read_bytes()
            script = str(SCRIPTS/'build_checkpoint.py')
            result = subprocess.run([sys.executable, script, 'check', str(path)], capture_output=True)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(path.read_bytes(), before)
            (path.parent/'.niio-build.lock').write_text('other-process')
            result = subprocess.run([sys.executable, script, 'begin', str(path), '--step', '1'], capture_output=True)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual((path.parent/'.niio-build.lock').read_text(), 'other-process')
            from unittest.mock import patch
            with patch('refresh_fields.os.replace', side_effect=OSError('simulated crash')):
                with self.assertRaises(OSError):
                    checkpoint.write_atomic(path, {'progress':'completed'})
            self.assertEqual(path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
