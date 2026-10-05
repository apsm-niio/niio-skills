#!/usr/bin/env python3
"""
Step 3 全指令碼方案：直接呼叫niio REST API 取得工作表結構並生成 worksheetContext.json。

用法:
  python3 refresh_fields.py --token "md_pss_id xxx" ./apps/图书借阅/hap-context.json

輸入:
  --token     niio認證 token（Authorization header 值）
  context     hap-context.json 的路徑（從中讀取 appId 和 worksheetIdByName）

輸出:
  與 hap-context.json 同目錄下的 worksheetContext.json
"""

import argparse
import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

API_BASE = "https://api2.mingdao.com"


def fetch_worksheet_structure(worksheet_id, token, app_id):
    """呼叫 REST API 取得單張工作表結構。"""
    url = f"{API_BASE}/v3/app/worksheets/{worksheet_id}"
    headers = {
        "Authorization": token,
        "HAP-Appid": app_id,
    }
    req = Request(url, headers=headers, method="GET")
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"  ❌ HTTP {e.code}: {body[:200]}", file=sys.stderr)
        return None
    except URLError as e:
        print(f"  ❌ 網路錯誤: {e.reason}", file=sys.stderr)
        return None


def extract_fields(raw_data):
    """從 API 響應中提取欄位清單。"""
    if not isinstance(raw_data, dict):
        return []
    data = raw_data.get("data", raw_data)
    if isinstance(data, dict):
        return data.get("fields", data.get("controls", []))
    return []


def normalize_field(field):
    """標準化單個欄位為 worksheetContext 格式。"""
    result = {
        "id": field.get("id", field.get("controlId", "")),
        "alias": field.get("alias", ""),
        "name": field.get("name", field.get("controlName", "")),
        "type": field.get("type", ""),
    }

    # 選項欄位
    options = field.get("options", [])
    if options:
        result["options"] = [
            {"key": opt.get("key", opt.get("value", "")), "value": opt.get("value", "")}
            for opt in options
            if not opt.get("isDelete", False)
        ]

    # 關聯欄位
    data_source = field.get("dataSource", "")
    if data_source:
        result["dataSource"] = data_source

    # 來源欄位（反向關聯）
    source_field = field.get("sourceField", "")
    if source_field:
        result["sourceField"] = source_field

    return result


def main():
    parser = argparse.ArgumentParser(description="重新整理工作表欄位結構")
    parser.add_argument("--token", required=True, help="niio認證 token（如 md_pss_id xxx）")
    parser.add_argument("context", help="hap-context.json 檔案路徑")
    args = parser.parse_args()

    context_path = Path(args.context)
    if not context_path.exists():
        print(f"❌ 檔案不存在: {context_path}", file=sys.stderr)
        sys.exit(1)

    with open(context_path, "r", encoding="utf-8") as f:
        context = json.load(f)

    app_id = context.get("appId", "")
    worksheet_id_by_name = context.get("worksheetIdByName", {})

    if not app_id:
        print("❌ hap-context.json 中缺少 appId", file=sys.stderr)
        sys.exit(1)
    if not worksheet_id_by_name:
        print("❌ hap-context.json 中缺少 worksheetIdByName", file=sys.stderr)
        sys.exit(1)

    print(f"📋 開始重新整理欄位結構（共 {len(worksheet_id_by_name)} 張表）", file=sys.stderr)

    worksheet_context = []
    errors = []

    for ws_name, ws_id in worksheet_id_by_name.items():
        print(f"  ⏳ {ws_name} ({ws_id})...", file=sys.stderr, end="")
        raw = fetch_worksheet_structure(ws_id, args.token, app_id)
        if raw is None:
            errors.append(ws_name)
            continue

        fields = extract_fields(raw)
        normalized = [normalize_field(f) for f in fields]

        worksheet_context.append({
            "worksheetId": ws_id,
            "worksheetName": ws_name,
            "fields": normalized,
        })
        print(f" ✅ {len(normalized)} 個欄位", file=sys.stderr)

    # 寫入輸出
    output_path = context_path.parent / "worksheetContext.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(worksheet_context, f, ensure_ascii=False, indent=2)

    # 摘要
    print(f"\n{'=' * 40}", file=sys.stderr)
    print(f"✅ worksheetContext 建置完成（{len(worksheet_context)}/{len(worksheet_id_by_name)} 張表）", file=sys.stderr)
    for ws in worksheet_context:
        print(f"  • {ws['worksheetName']}: {len(ws['fields'])} 個欄位", file=sys.stderr)

    if errors:
        print(f"\n⚠️ 失敗 {len(errors)} 張: {', '.join(errors)}", file=sys.stderr)
        sys.exit(1)

    print(f"\n📁 輸出: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
