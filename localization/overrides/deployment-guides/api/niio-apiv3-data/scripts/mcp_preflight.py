#!/usr/bin/env python3
"""Validate an explicit MCP request locally; never connects or writes remote data."""
import argparse
import json
import math
from pathlib import Path


def structure_data(raw):
    while isinstance(raw, dict) and 'data' in raw and 'fields' not in raw:
        raw = raw['data']
    if not isinstance(raw, dict) or not raw.get('worksheetId') or not isinstance(raw.get('fields'), list):
        raise ValueError('Expected one current DSL worksheet structure with worksheetId and fields')
    return raw


def scope_issues(structure, request):
    issues = []
    if request.get('worksheet_id') != structure['worksheetId']:
        issues.append('worksheet_id does not match the supplied structure')
    if structure.get('appId') and request.get('appId') != structure['appId']:
        issues.append('appId does not match the supplied structure')
    return issues


def record_issues(structure, request, mode, allow_clear=()):
    """Check the field types behind the union-typed MCP value parameter."""
    structure = structure_data(structure)
    issues = scope_issues(structure, request)
    by_key = {}
    for field in structure['fields']:
        for key in (field.get('id'), field.get('alias')):
            if key:
                if key in by_key and by_key[key]['id'] != field['id']:
                    raise ValueError('Ambiguous field ID or alias in structure')
                by_key[key] = field
    fields = request.get('fields')
    if not isinstance(fields, list) or not fields:
        return issues + ['fields must be a non-empty array']
    seen = set()
    for patch in fields:
        if not isinstance(patch, dict) or patch.get('id') not in by_key:
            issues.append('Unknown or missing field ID/alias')
            continue
        field = by_key[patch['id']]
        key = field['id']
        if key in seen:
            issues.append('Duplicate field: ' + key)
        seen.add(key)
        if field.get('isReadOnly'):
            issues.append('Read-only field: ' + key)
        if 'value' not in patch:
            issues.append('Missing value: ' + key)
            continue
        value = patch['value']
        empty = value is None or value == '' or value == [] or (isinstance(value, str) and not value.strip())
        if field.get('required') and empty:
            issues.append('Required field is empty: ' + key)
        if field.get('type') == 'Number':
            if empty and not field.get('required') and (key in allow_clear or patch['id'] in allow_clear):
                # Current MCP value union permits an empty string, not JSON null/arrays.
                if value != '':
                    issues.append('Explicit numeric clear must use an empty string: ' + key)
            elif isinstance(value, bool) or not isinstance(value, (int, float)) or (isinstance(value, float) and not math.isfinite(value)):
                issues.append('Number requires a finite JSON number; no implicit coercion: ' + key)
    if mode == 'create':
        for field in structure['fields']:
            default = field.get('defaultValue')
            has_default = bool(default) and default not in ([''], [None])
            if field.get('required') and not field.get('isReadOnly') and field['id'] not in seen and not has_default:
                issues.append('Missing required field: ' + field['id'])
    return issues


def list_issues(structure, request):
    """An explicit view must be authorized/selected by the caller, never guessed here."""
    structure = structure_data(structure)
    issues = scope_issues(structure, request)
    views = {v['id'] for v in structure.get('views', [])}
    if not request.get('viewId') or request['viewId'] not in views:
        issues.append('Provide an authorized viewId belonging to this worksheet')
    ids = {f['id'] for f in structure['fields']}
    if request.get('useFieldIdAsKey') is not True:
        issues.append('Use useFieldIdAsKey=true for deterministic field readback')
    fields = request.get('fields')
    if not isinstance(fields, list) or not fields or any(f not in ids for f in fields):
        issues.append('Provide explicit physical field IDs from this worksheet')
    for name in ('pageIndex', 'pageSize'):
        value = request.get(name)
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            issues.append(name + ' must be a positive integer')
    return issues


def snapshot_issues(raw):
    issues = []

    def walk(value, path):
        if isinstance(value, dict):
            if '_nodeFactory' in value and ('_children' in value or '_value' in value):
                issues.append('Internal JSON tree serialization at ' + path)
                return
            for key, child in value.items():
                walk(child, path + '.' + str(key))
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, path + '[' + str(index) + ']')
        elif isinstance(value, str) and value.lstrip().startswith(('{', '[')):
            try:
                child = json.loads(value)
            except (ValueError, TypeError):
                return
            walk(child, path + '<json>')
    walk(raw, '$')
    return issues


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('record', 'list', 'snapshot'))
    parser.add_argument('--structure', type=Path)
    parser.add_argument('--request', required=True, type=Path)
    parser.add_argument('--mode', choices=('create', 'update'))
    parser.add_argument('--allow-clear', action='append', default=[])
    args = parser.parse_args()
    try:
        request = json.loads(args.request.read_text(encoding='utf-8-sig'))
        if args.operation == 'snapshot':
            issues = snapshot_issues(request)
        else:
            if args.structure is None:
                raise ValueError('--structure is required')
            structure = json.loads(args.structure.read_text(encoding='utf-8-sig'))
            if not isinstance(request, dict):
                raise ValueError('Request must be an object')
            if args.operation == 'record':
                if args.mode is None:
                    raise ValueError('--mode is required for record validation')
                issues = record_issues(structure, request, args.mode, args.allow_clear)
            else:
                issues = list_issues(structure, request)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        issues = [str(exc)]
    # Do not echo request values into logs. No output file or remote side effects.
    print(json.dumps({'valid': not issues, 'issues': issues}, ensure_ascii=True))
    return 1 if issues else 0


if __name__ == '__main__':
    raise SystemExit(main())
