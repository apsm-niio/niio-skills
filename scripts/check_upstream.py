#!/usr/bin/env python3
"""每月比對上游版本；有更新才建立通知 Issue，不修改技能或觸發同步。"""
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

UPSTREAM = "mingdaocom/hap-skills"


def valid_sha(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{40}", value):
        raise ValueError("版本必須是完整 40 位小寫 commit SHA")
    return value


def plain(value):
    text = str(value).splitlines()[0] if str(value).splitlines() else ""
    text = text.replace("@", "＠")
    return re.sub(r"([\\`*_{}\[\]<>()#!|])", r"\\\1", text)[:250]


def github_api(path, body=None):
    request = Request("https://api.github.com" + path,
        data=None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": "Bearer " + os.environ["GH_TOKEN"],
                 "Accept": "application/vnd.github+json", "Content-Type": "application/json",
                 "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "niio-upstream-check"},
        method="GET" if body is None else "POST")
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def notification_body(repository, base, head, comparison, login):
    compare_url = f"https://github.com/{UPSTREAM}/compare/{base}...{head}"
    lines = [f"<!-- niio-upstream-review:{head} -->", f"@{login} 上游有更新，請先確認變更，再決定是否同步。", "",
             "**本通知沒有更新技能，也沒有啟動同步。**", "",
             f"- 目前已同步版本：`{base}`", f"- 本次待確認版本：`{head}`",
             f"- [查看完整變更比較]({compare_url})",
             f"- 比較狀態：{plain(comparison.get('status', 'unknown'))}；"
             f"差異提交數：{comparison.get('total_commits', len(comparison.get('commits', [])))}", "",
             "### 提交紀錄（最多列 30 筆，標題為上游原文）", ""]
    if comparison.get("status") not in ("ahead", "identical"):
        lines += ["⚠️ 上游與已同步版本不是單純向前更新，請先檢查分支歷史，不要直接同步。", ""]
    for commit in comparison.get("commits", [])[:30]:
        sha = valid_sha(commit["sha"])
        title = plain(commit.get("commit", {}).get("message", ""))
        lines.append(f"- `{sha[:8]}` {title}")
    lines += ["", "### 異動檔案（最多列 50 個）", ""]
    for item in comparison.get("files", [])[:50]:
        lines.append(f"- {plain(item.get('status', ''))}：{plain(item.get('filename', ''))}")
    lines += ["", "清單可能因顯示上限或 GitHub API 上限而省略；完整內容請開啟上方比較連結。", "",
              "### 確認後如何同步", "",
              f"1. 開啟 [確認後同步並產生繁中技能](https://github.com/{repository}/actions/workflows/sync-upstream.yml)。",
              "2. 選擇 **Run workflow**，分支選 `main`。",
              f"3. 在 `upstream_commit` 貼入：`{head}`。",
              "4. 再按 **Run workflow**。只同步此版本，不會自動改用較新的上游版本。",
              "5. 等待轉換、品牌檢查與測試通過；若因上游結構變更而停止，先修正规則，不繞過檢查。", "",
              "不想更新時不執行即可；關閉此 Issue 不會觸發同步。同一待確認版本不重複通知。",
              "通知完成後可自行關閉此 Issue。Email 是否寄送依 GitHub 個人通知設定。"]
    return "\n".join(lines) + "\n"


def check(repository, base, login, api=github_api):
    valid_sha(base)
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("儲存庫名稱格式錯誤")
    if not re.fullmatch(r"[A-Za-z0-9-]+", login):
        raise ValueError("通知帳號格式錯誤")
    head = valid_sha(api(f"/repos/{UPSTREAM}/commits/main")["sha"])
    if head == base:
        return "上游沒有新版本；未建立通知，也未同步。"
    marker = f"<!-- niio-upstream-review:{head} -->"
    page = 1
    while True:
        issues = api(f"/repos/{repository}/issues?state=all&per_page=100&page={page}")
        for issue in issues:
            if not issue.get("pull_request") and marker in (issue.get("body") or ""):
                return f"此上游版本已通知，不重複建立：{issue['html_url']}；未同步。"
        if len(issues) < 100:
            break
        page += 1
    comparison = api(f"/repos/{UPSTREAM}/compare/{base}...{head}")
    body = notification_body(repository, base, head, comparison, login)
    date = datetime.now(ZoneInfo("Asia/Taipei")).strftime("%Y-%m-%d")
    issue = api(f"/repos/{repository}/issues", {
        "title": f"上游更新待確認：{date}（{head[:8]}）", "body": body})
    return f"已建立更新通知：{issue['html_url']}；等待確認，未同步。"


def main():
    try:
        state = json.loads(Path("localization/upstream-state.json").read_text(encoding="utf-8"))
        message = check(os.environ["GITHUB_REPOSITORY"], state["upstreamCommit"], os.environ["NOTIFY_LOGIN"])
    except HTTPError as error:
        print(f"GitHub API 檢查失敗：HTTP {error.code}；未執行同步。", file=sys.stderr)
        return 1
    except (OSError, ValueError, KeyError, TypeError):
        print("上游檢查失敗：請檢查來源版本、權限與網路；未執行同步。", file=sys.stderr)
        return 1
    print(message)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as handle:
            handle.write(message + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
