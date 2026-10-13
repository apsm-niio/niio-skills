#!/usr/bin/env python3
"""根據 MCP 明確中繼資訊生成填值候選；不猜測標題或可寫入性，不連線。"""
import json
import sys
from pathlib import Path
from refresh_fields import write_atomic

SKIP_TYPES = {'Divider', 'Formula', 'AutoNumber', 'AutoID', 'Lookup', 'Rollup'}
SYSTEM_FIELD_IDS = {'rowid', 'ownerid', 'caid', 'ctime', 'utime', 'uaid'}


def generate_fill_templates(worksheet_context):
    id_to_name = {ws['worksheetId']: ws['worksheetName'] for ws in worksheet_context}
    templates = []
    for ws in worksheet_context:
        fillable, excluded, titles, issues, deps = [], [], [], [], []
        keys = set()
        fields = ws.get('fields', [])
        for field in fields:
            field_id = field['id']
            field_type = field['type']
            alias = field.get('alias') or ''
            item = {'fieldKey': alias or field_id, 'name': field['name'], 'type': field_type}
            for key in ('isTitle', 'isReadOnly', 'required', 'subType'):
                if key in field:
                    item[key] = field[key]
            if field.get('isTitle') is True:
                titles.append({'id': field_id, **item})
            if type(field.get('isTitle')) is not bool:
                issues.append({'id': field_id, 'reason': 'missing_or_invalid_isTitle'})
            reason = None
            if field_id in SYSTEM_FIELD_IDS or alias.startswith('_'):
                reason = 'system_field'
            elif field_type in SKIP_TYPES:
                reason = 'computed_or_non_input_type'
            elif field.get('isReadOnly') is True:
                reason = 'read_only'
            elif field.get('isReadOnly') is not False:
                reason = 'unknown_writability'
                issues.append({'id': field_id, 'reason': reason})
            elif field_type == 'Relation' and not field.get('dataSource'):
                reason = 'missing_relation_target'
                issues.append({'id': field_id, 'reason': reason})
            if reason:
                excluded.append({'id': field_id, **item, 'reason': reason})
                continue
            if item['fieldKey'] in keys:
                raise ValueError('模板 fieldKey 重複，停止產生')
            keys.add(item['fieldKey'])
            if field_type in ('SingleSelect', 'MultipleSelect', 'Dropdown'):
                item['validOptions'] = [option['value'] for option in field.get('options', [])
                                        if not option.get('isDelete', False)]
            if field_type == 'Relation':
                for key in ('dataSource', 'sourceField', 'relation'):
                    if key in field:
                        item[key] = field[key]
                if field['dataSource'] == ws['worksheetId']:
                    item['isSelfRelation'] = True
                else:
                    deps.append(field['dataSource'])
            fillable.append(item)
        if len(titles) != 1:
            issues.append({'reason': 'title_not_uniquely_identified'})
        templates.append({'worksheetId': ws['worksheetId'], 'worksheetName': ws['worksheetName'],
                          'fieldCount': len(fillable), 'fillableFields': fillable,
                          'relationDeps': sorted({id_to_name.get(dep, dep) for dep in deps}),
                          'titleFields': titles, 'excludedFields': excluded,
                          'metadataIssues': issues, 'requiresReview': bool(issues)})
    return templates


def main():
    if len(sys.argv) not in (2, 3):
        print('用法：generate_fill_templates.py <worksheetContext.json> [輸出路徑]', file=sys.stderr)
        return 1
    source = Path(sys.argv[1])
    output = Path(sys.argv[2]) if len(sys.argv) == 3 else source.parent / 'fillTemplates.json'
    try:
        templates = generate_fill_templates(json.loads(source.read_text(encoding='utf-8')))
        write_atomic(output, templates)
    except (OSError, ValueError, TypeError, KeyError):
        print('模板產生失敗：請重新整理 MCP 結構並檢查欄位中繼資訊；既有輸出未變更。', file=sys.stderr)
        return 1
    print(json.dumps({'success': True, 'worksheetCount': len(templates),
                      'requiresReview': any(t['requiresReview'] for t in templates)}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
