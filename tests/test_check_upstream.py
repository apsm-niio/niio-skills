import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_upstream", ROOT / "scripts/check_upstream.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
BASE, HEAD = "a" * 40, "b" * 40


class CheckTests(unittest.TestCase):
    def test_no_update_does_not_notify(self):
        calls = []
        def api(path, body=None):
            calls.append((path, body))
            return {"sha": BASE}
        result = module.check("owner/repo", BASE, "reviewer", api)
        self.assertEqual(len(calls), 1)
        self.assertIn("沒有新版本", result)

    def test_update_creates_only_issue_with_reviewed_sha(self):
        writes = []
        def api(path, body=None):
            if body is not None:
                writes.append((path, body))
                return {"html_url": "https://github.com/owner/repo/issues/1"}
            if path.endswith("commits/main"):
                return {"sha": HEAD}
            if "/issues?" in path:
                return []
            return {"status": "ahead", "total_commits": 1,
                    "commits": [{"sha": HEAD, "commit": {"message": "fix @someone\nextra"}}],
                    "files": [{"status": "modified", "filename": "skills/test.md"}]}
        module.check("owner/repo", BASE, "reviewer", api)
        self.assertEqual(len(writes), 1)
        self.assertEqual(writes[0][0], "/repos/owner/repo/issues")
        body = writes[0][1]["body"]
        self.assertIn("@reviewer", body)
        self.assertNotIn("@someone", body)
        self.assertIn(HEAD, body)
        self.assertIn("upstream_commit", body)
        self.assertIn("沒有啟動同步", body)

    def test_already_notified_even_if_closed(self):
        def api(path, body=None):
            self.assertIsNone(body)
            if path.endswith("commits/main"):
                return {"sha": HEAD}
            return [{"state": "closed", "body": f"<!-- niio-upstream-review:{HEAD} -->",
                     "html_url": "https://github.com/owner/repo/issues/1"}]
        self.assertIn("不重複", module.check("owner/repo", BASE, "reviewer", api))

    def test_compare_failure_does_not_write(self):
        def api(path, body=None):
            self.assertIsNone(body)
            if path.endswith("commits/main"):
                return {"sha": HEAD}
            if "/issues?" in path:
                return []
            raise ValueError("compare failed")
        with self.assertRaises(ValueError):
            module.check("owner/repo", BASE, "reviewer", api)

    def test_invalid_sha_rejected_before_network(self):
        def api(*args):
            self.fail("Should not call API")
        with self.assertRaises(ValueError):
            module.check("owner/repo", "main; anything", "reviewer", api)

    def test_diverged_history_warns(self):
        body = module.notification_body("owner/repo", BASE, HEAD, {"status": "diverged"}, "reviewer")
        self.assertIn("不要直接同步", body)


if __name__ == "__main__":
    unittest.main()
