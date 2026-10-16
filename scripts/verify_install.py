#!/usr/bin/env python3
"""唯讀比對技能副本；不載入技能、不連線 MCP、不修改安裝目錄。"""
import argparse
import hashlib
import json
from pathlib import Path


def manifest(root):
    root = Path(root)
    if not root.is_dir() or not (root / 'SKILL.md').is_file():
        raise ValueError('技能目錄必須存在且含 SKILL.md')
    result = {}
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError('不接受符號連結')
        rel = path.relative_to(root)
        if '__pycache__' in rel.parts or path.suffix in ('.pyc', '.pyo'):
            continue
        if path.is_file():
            result[rel.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def compare(source, installed):
    expected, actual = manifest(source), manifest(installed)
    return {
        'expectedFiles': len(expected), 'actualFiles': len(actual),
        'missing': sorted(expected.keys() - actual.keys()),
        'extra': sorted(actual.keys() - expected.keys()),
        'changed': sorted(k for k in expected.keys() & actual.keys() if expected[k] != actual[k]),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('installed', type=Path)
    args = parser.parse_args()
    result = compare(args.source, args.installed)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return int(any(result[k] for k in ('missing', 'extra', 'changed')))


if __name__ == '__main__':
    raise SystemExit(main())
