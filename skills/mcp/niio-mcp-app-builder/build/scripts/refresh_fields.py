#!/usr/bin/env python3
"""將本次 MCP 欄位回應轉成 worksheetContext.json；不連線、不讀取憑證。"""

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path


class ValidationError(ValueError):
    """僅包含程式定義的檢查訊息，不附上原始回應。"""


def read_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def required_text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{label} 缺少有效文字")
    return value


def normalize_field(field):
    if not isinstance(field, dict):
        raise ValidationError("欄位必須是物件")
    result = {
        "id": required_text(field.get("id"), "欄位 ID"),
        "alias": field.get("alias") or "",
        "name": required_text(field.get("name"), "欄位名稱"),
        "type": required_text(field.get("type"), "欄位型別（須為 MCP 文字型別）"),
    }
    if not isinstance(result["alias"], str):
        raise ValidationError("欄位 alias 必須是文字")
    options = field.get("options", [])
    if not isinstance(options, list):
        raise ValidationError("欄位 options 必須是陣列")
    if options:
        result["options"] = []
        for option in options:
            if not isinstance(option, dict):
                raise ValidationError("選項必須是物件")
            if option.get("isDelete", False):
                continue
            if "key" not in option or "value" not in option:
                raise ValidationError("選項缺少 key 或 value")
            result["options"].append(dict(option))
    for key in ("dataSource", "sourceField", "relation"):
        if key in field:
            result[key] = field[key]
    return result


def build_context(context, responses_dir):
    if not isinstance(context, dict):
        raise ValidationError("hap-context.json 必須是物件")
    app_id = required_text(context.get("appId"), "應用 ID")
    worksheets = context.get("worksheetIdByName")
    if not isinstance(worksheets, dict) or not worksheets:
        raise ValidationError("缺少 worksheetIdByName")
    ids = []
    for name, ws_id in worksheets.items():
        required_text(name, "工作表名稱")
        required_text(ws_id, "工作表 ID")
        if not re.fullmatch(r"[A-Za-z0-9_-]+", ws_id):
            raise ValidationError("工作表 ID 含不支援的字元")
        ids.append(ws_id)
    if len(set(ids)) != len(ids):
        raise ValidationError("工作表 ID 重複")
    if not responses_dir.is_dir():
        raise ValidationError("MCP 回應資料夾不存在")
    if {p.name for p in responses_dir.glob("*.json")} != {i + ".json" for i in ids}:
        raise ValidationError("MCP 回應檔案與本次工作表清單不一致")
    result = []
    for name, ws_id in worksheets.items():
        try:
            entry = read_json(responses_dir / (ws_id + ".json"))
            if not isinstance(entry, dict) or entry.get("appId") != app_id or entry.get("worksheetId") != ws_id:
                raise ValidationError("MCP 回應的應用或工作表 ID 不一致")
            response = entry.get("response")
            if not isinstance(response, dict) or response.get("success") is not True:
                raise ValidationError("MCP 回應未成功")
            data = response.get("data")
            if not isinstance(data, dict):
                raise ValidationError("MCP 回應缺少 data 物件")
            if "worksheetId" in data and data["worksheetId"] != ws_id:
                raise ValidationError("MCP data.worksheetId 不一致")
            fields = data.get("fields")
            if not isinstance(fields, list) or not fields:
                raise ValidationError("MCP 回應缺少非空 data.fields")
            normalized = [normalize_field(field) for field in fields]
            if len({field["id"] for field in normalized}) != len(normalized):
                raise ValidationError("工作表內有重複欄位 ID")
            result.append({"worksheetId": ws_id, "worksheetName": name, "fields": normalized})
        except ValidationError as error:
            raise ValidationError(f"工作表 {ws_id}：{error}") from None
    return result


def write_atomic(path, value):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".worksheetContext-", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def main():
    parser = argparse.ArgumentParser(description="將 MCP 欄位回應驗證並整理成本機欄位結構")
    parser.add_argument("--responses-dir", required=True, type=Path, help="本次完整 MCP JSON 回應資料夾")
    parser.add_argument("context", type=Path, help="hap-context.json 路徑")
    args = parser.parse_args()
    try:
        result = build_context(read_json(args.context), args.responses_dir)
        write_atomic(args.context.parent / "worksheetContext.json", result)
    except ValidationError as error:
        print(f"欄位整理失敗：{error}；既有輸出未變更。", file=sys.stderr)
        return 1
    except (OSError, ValueError, TypeError):
        # 不輸出原始回應或例外內容，避免意外洩漏回應中的敏感資料。
        print("欄位整理失敗：請檢查本次回應完整性、ID、欄位與檔案權限；既有輸出未變更。", file=sys.stderr)
        return 1
    print(json.dumps({"success": True, "worksheetCount": len(result),
                      "fieldCounts": {item["worksheetId"]: len(item["fields"]) for item in result}}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
