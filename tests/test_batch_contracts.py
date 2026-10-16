"""回歸：失敗不可降級成成功，固定版本副本能偵測缺漏與自訂變更。"""
import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / 'skills/mcp/niio-mcp-app-builder'
spec = importlib.util.spec_from_file_location('verify_install', ROOT / 'scripts/verify_install.py')
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class BatchContracts(unittest.TestCase):
    def test_no_silent_workflow_degradation(self):
        for name in ('10_create_workflows.md', '11_create_action_workflows.md'):
            text = (BUILDER / 'build/steps' / name).read_text(encoding='utf-8')
            self.assertNotIn('跳過該節點，繼續', text)
            self.assertIn('停止該流程', text)
            self.assertIn('發布成功只代表設定已發布', text)
            self.assertIn('禁止重送整批', text)
        rules = (BUILDER / 'build/steps/workflow_rules.md').read_text(encoding='utf-8')
        self.assertNotIn('語義最接近', rules)
        self.assertNotIn('使用該工作表的第一個檢視', rules)

    def test_cli_and_update_contracts(self):
        context = (BUILDER / 'build/CONTEXT.md').read_text(encoding='utf-8')
        self.assertNotIn('會在自檢階段自動瀏覽器登入', context)
        refinement = (BUILDER / 'build/steps/12_cli_refinement.md').read_text(encoding='utf-8')
        self.assertNotIn('仍算建置成功', refinement)
        entry = (BUILDER / 'SKILL.md').read_text(encoding='utf-8')
        self.assertIn('先備份現有技能', entry)
        self.assertIn('來源不明的自訂變更保留', entry)

    def test_clean_install_and_detect_damage(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'builder'
            shutil.copytree(BUILDER, target)
            self.assertEqual(verify.manifest(BUILDER), verify.manifest(target))
            (target / 'SKILL.md').write_text('custom', encoding='utf-8')
            (target / 'local-notes.txt').write_text('keep', encoding='utf-8')
            (target / 'build/CONTEXT.md').unlink()
            result = verify.compare(BUILDER, target)
            self.assertEqual(result['changed'], ['SKILL.md'])
            self.assertEqual(result['extra'], ['local-notes.txt'])
            self.assertEqual(result['missing'], ['build/CONTEXT.md'])
            self.assertEqual((target / 'local-notes.txt').read_text(), 'keep')


if __name__ == '__main__':
    unittest.main()
