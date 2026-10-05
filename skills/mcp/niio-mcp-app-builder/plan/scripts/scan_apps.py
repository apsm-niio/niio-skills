#!/usr/bin/env python3
"""
scan_apps.py — 掃描 apps/ 目錄，輸出每個應用的名稱和建置狀態。
               同時檢查 GitHub 遠端版本是否有更新（2 秒超時，失敗靜默跳過）。

用法：python scan_apps.py <projectRoot>
示例：python scan_apps.py /Users/user/应用搭建测试
輸出：JSON 物件 { apps: [...], update?: { available, local, remote, notes } }
"""

import json
import os
import re
import sys
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 優先從命令列參數取得專案根目錄，否則 fallback 到指令碼目錄向上 4 級
project_root = (
    os.path.abspath(sys.argv[1])
    if len(sys.argv) > 1
    else os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "..", ".."))
)
apps_dir = os.path.join(project_root, "apps")


def find_version_file(start_dir):
    """向上逐級搜尋版本檔案（相容完整倉庫和僅 skills/ 目錄兩種安裝方式）
    優先查詢 plugin.json，其次 version.json"""
    d = start_dir
    for _ in range(6):
        for name in ("plugin.json", "version.json"):
            candidate = os.path.join(d, name)
            if os.path.isfile(candidate):
                return candidate
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return None


def scan_apps():
    """掃描 apps/ 目錄下的應用"""
    results = []
    if not os.path.isdir(apps_dir):
        return results

    for entry in sorted(os.listdir(apps_dir)):
        entry_path = os.path.join(apps_dir, entry)
        if not os.path.isdir(entry_path):
            continue

        plan_path = os.path.join(entry_path, "hap-plan.json")
        if not os.path.isfile(plan_path):
            continue

        # 讀取應用名
        app_name = entry
        try:
            with open(plan_path, "r", encoding="utf-8") as f:
                plan = json.load(f)
            if plan.get("appName"):
                app_name = plan["appName"]
        except Exception:
            pass

        # 讀取建置進度
        ctx_path = os.path.join(entry_path, "hap-context.json")
        progress = None
        status = "planned"

        if os.path.isfile(ctx_path):
            try:
                with open(ctx_path, "r", encoding="utf-8") as f:
                    ctx = json.load(f)
                progress = ctx.get("progress")
                status = "completed" if progress == "completed" else "in_progress"
            except Exception:
                pass

        results.append({"dir": entry, "appName": app_name, "progress": progress, "status": status})

    return results


def find_git_root(start_dir):
    """向上查詢 .git 目錄，回傳倉庫根目錄路徑，找不到回傳 None"""
    d = start_dir
    for _ in range(10):
        if os.path.isdir(os.path.join(d, ".git")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return None


def check_update():
    """檢查 GitHub 遠端版本（2 秒超時，失敗靜默跳過）"""
    plugin_path = find_version_file(SCRIPT_DIR)
    if not plugin_path:
        return None

    try:
        with open(plugin_path, "r", encoding="utf-8") as f:
            pkg = json.load(f)
        local_version = pkg.get("version")
        repo_url = pkg.get("repository")
        branch = pkg.get("branch", "main")
        skill_path = pkg.get("skillPath", "")
    except Exception:
        return None

    if not local_version or not repo_url:
        return None

    match = re.search(r"github\.com/([^/]+/[^/]+)", repo_url)
    if not match:
        return None

    # 計算版本檔案在倉庫中的相對路徑
    git_root = find_git_root(os.path.dirname(plugin_path))
    if git_root:
        remote_file = os.path.relpath(plugin_path, git_root)
    else:
        # 非 git 安裝方式，用 skillPath 拼接路徑
        if skill_path:
            remote_file = f"{skill_path}/{os.path.basename(plugin_path)}"
        else:
            remote_file = os.path.basename(plugin_path)

    raw_url = f"https://raw.githubusercontent.com/{match.group(1)}/{branch}/{remote_file}"

    try:
        with urllib.request.urlopen(raw_url, timeout=2) as resp:
            remote = json.loads(resp.read())
        if remote.get("version") and remote["version"] != local_version:
            return {
                "available": True,
                "local": local_version,
                "remote": remote["version"],
                "notes": remote.get("releaseNotes"),
                "repository": repo_url,
                "branch": branch,
                "skillPath": skill_path,
            }
    except Exception:
        pass

    return None


if __name__ == "__main__":
    output = {"apps": scan_apps()}
    update = check_update()
    if update:
        output["update"] = update
    print(json.dumps(output, ensure_ascii=False, indent=2))
