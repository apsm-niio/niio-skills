#!/usr/bin/env python3
"""固定上游的隔離生成驗證；不修改正式技能或遠端資料。"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml
from audit_brand import audit
from verify_install import compare

ROOT = Path(__file__).resolve().parents[1]


def files(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()
            and '__pycache__' not in p.parts and p.suffix not in ('.pyc', '.pyo')}


def validate(source):
    state = json.loads((ROOT / 'localization/upstream-state.json').read_text(encoding='utf-8'))
    # Source identity is supplied by the caller's pinned checkout/archive, not inferred from folder name.
    with tempfile.TemporaryDirectory(prefix='niio-release-') as tmp:
        stage = Path(tmp)
        for directory in ('scripts', 'localization', 'assets'):
            shutil.copytree(ROOT / directory, stage / directory)
        subprocess.run([sys.executable, str(ROOT / 'scripts/localize.py'), '--source', str(source),
                        '--output', str(stage), '--terms', str(ROOT / 'localization/terms.json')], check=True)
        # Same repository metadata as the existing manual sync workflow.
        version_path = stage / 'skills/mcp/niio-mcp-app-builder/version.json'
        version = json.loads(version_path.read_text(encoding='utf-8'))
        version.update(repository='https://github.com/apsm-niio/niio-skills', branch='main')
        version_path.write_bytes((json.dumps(version, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
        expected, actual = files(ROOT / 'skills'), files(stage / 'skills')
        differences = sorted(k for k in expected.keys() | actual.keys() if expected.get(k) != actual.get(k))
        if differences:
            raise ValueError('生成產物與儲存庫不一致：' + json.dumps(differences, ensure_ascii=False))
        brand = audit(stage / 'skills')
        if brand['issues']:
            raise ValueError('品牌檢查失敗：' + str(brand['issues']))
        skills = list((stage / 'skills').rglob('SKILL.md'))
        for path in skills:
            text = path.read_text(encoding='utf-8')
            parts = text.split('---', 2)
            if len(parts) != 3 or parts[0].strip():
                raise ValueError('缺少技能 frontmatter：' + str(path))
            meta = yaml.safe_load(parts[1])
            if not all(isinstance(meta.get(key), str) and meta[key].strip() for key in ('name', 'description')):
                raise ValueError('缺少技能名稱／說明：' + str(path))
        if (stage / 'THIRD_PARTY_LICENSE.txt').read_bytes() != (ROOT / 'THIRD_PARTY_LICENSE.txt').read_bytes():
            raise ValueError('授權與來源不符')
        builder = stage / 'skills/mcp/niio-mcp-app-builder'
        installed = stage / 'isolated-install/niio-mcp-app-builder'
        shutil.copytree(builder, installed, copy_function=shutil.copy2)
        result = compare(builder, installed)
        if any(result[k] for k in ('missing', 'extra', 'changed')):
            raise ValueError('隔離安裝不一致')
        print(json.dumps({'upstreamCommit': state['upstreamCommit'], 'generatedFiles': len(actual),
                          'skillDocuments': len(skills), 'brandIssues': 0,
                          'licenseMatches': True, 'isolatedInstall': result,
                          'sessionLoad': 'not tested', 'MCP': 'not called'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream-source', required=True, type=Path)
    args = parser.parse_args()
    validate(args.upstream_source.resolve())
