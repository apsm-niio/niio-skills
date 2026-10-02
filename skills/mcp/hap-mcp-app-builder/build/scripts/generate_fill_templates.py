#!/usr/bin/env python3
"""
從 worksheetContext.json 生成確定性的填值模板 (fillTemplates.json)。

用法:
  python3 generate_fill_templates.py <worksheetContext.json路徑> [輸出路徑]

輸出:
  fillTemplates.json — 每張工作表的可填欄位清單，包含：
    - fieldKey: 直接用於 batch_create_records 的 fields[].id（已從 alias/id 中確定性提取）
    - name: 欄位中文名（供 LLM 理解語義）
    - type: 欄位型別
    - validOptions: 選項欄位的合法選項值清單（僅限選項型別欄位）
    - dataSource: 關聯欄位的目標工作表 ID（僅限 Relation 型別）
    - isTitle: 標題欄位標記
    - isSelfRelation: 自關聯標記
"""

import json
import sys
from pathlib import Path

# 不可填值的欄位型別 — 這些欄位在 batch_create_records 中不傳
SKIP_TYPES = {"Divider", "Formula", "AutoNumber", "AutoID", "Lookup"}

# 系統欄位的固定 ID — 所有表都有，不應由使用者寫入
SYSTEM_FIELD_IDS = {"rowid", "ownerid", "caid", "ctime", "utime", "uaid"}


def generate_fill_templates(worksheet_context):
    """從 worksheetContext 生成填值模板清單。"""

    # 全域 worksheetId → worksheetName 對映（用於關聯依賴的人類可讀翻譯）
    id_to_name = {ws["worksheetId"]: ws["worksheetName"] for ws in worksheet_context}

    templates = []

    for ws in worksheet_context:
        worksheet_id = ws["worksheetId"]
        worksheet_name = ws["worksheetName"]
        fillable_fields = []
        relation_deps = []
        title_field_found = False

        for field in ws.get("fields", []):
            field_id = field.get("id", "")
            field_alias = field.get("alias", "")
            field_name = field.get("name", "")
            field_type = field.get("type", "")
            data_source = field.get("dataSource", "")
            source_field = field.get("sourceField", "")
            options = field.get("options", [])

            # ── 跳過系統欄位 ──
            if field_id in SYSTEM_FIELD_IDS:
                continue
            if field_alias.startswith("_"):
                continue

            # ── 跳過不可填值的型別 ──
            if field_type in SKIP_TYPES:
                continue

            # ── 跳過反向關聯欄位（alias 為空的 Relation = 系統自動建立的反向欄位，只讀） ──
            # 注意：niio的正向和反向關聯都有 sourceField，不能用 sourceField 判斷
            if field_type == "Relation" and not field_alias:
                continue

            # ── 確定 fieldKey（alias 優先，為空則用 id） ──
            field_key = field_alias if field_alias else field_id

            # ── 建置欄位模板 ──
            field_template = {
                "fieldKey": field_key,
                "name": field_name,
                "type": field_type,
            }

            # ── 標記標題欄位（啟發式：第一個 Text 型別欄位） ──
            if not title_field_found and field_type == "Text":
                field_template["isTitle"] = True
                title_field_found = True

            # ── 提取有效選項（選項型別欄位） ──
            if options and field_type in ("SingleSelect", "MultipleSelect", "Dropdown"):
                valid_options = [
                    opt["value"]
                    for opt in options
                    if not opt.get("isDelete", False)
                ]
                field_template["validOptions"] = valid_options

            # ── 提取關聯資訊 ──
            if field_type == "Relation" and data_source:
                field_template["dataSource"] = data_source
                if data_source == worksheet_id:
                    field_template["isSelfRelation"] = True
                else:
                    relation_deps.append(data_source)

            fillable_fields.append(field_template)

        # ── 將關聯依賴的 ID 翻譯為表名 ──
        relation_dep_names = sorted(set(
            id_to_name.get(dep_id, dep_id) for dep_id in relation_deps
        ))

        template = {
            "worksheetId": worksheet_id,
            "worksheetName": worksheet_name,
            "fieldCount": len(fillable_fields),
            "fillableFields": fillable_fields,
            "relationDeps": relation_dep_names,
        }

        templates.append(template)

    return templates


def main():
    if len(sys.argv) < 2:
        print(
            "用法: python3 generate_fill_templates.py <worksheetContext.json路徑> [輸出路徑]",
            file=sys.stderr,
        )
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"❌ 檔案不存在: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_path = (
        Path(sys.argv[2]) if len(sys.argv) > 2 else input_path.parent / "fillTemplates.json"
    )

    with open(input_path, "r", encoding="utf-8") as f:
        worksheet_context = json.load(f)

    templates = generate_fill_templates(worksheet_context)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(templates, f, ensure_ascii=False, indent=2)

    # 輸出摘要
    print(f"\n📋 填值模板生成完成（共 {len(templates)} 張表）：", file=sys.stderr)
    for t in templates:
        deps = f"，依賴: {', '.join(t['relationDeps'])}" if t["relationDeps"] else ""
        print(f"  • {t['worksheetName']}: {t['fieldCount']} 個可填欄位{deps}", file=sys.stderr)
    print(f"\n✅ 輸出: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
