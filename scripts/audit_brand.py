#!/usr/bin/env python3
"""Audit installable text; keep reviewed wire identifiers, reject unknown brand tokens."""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

TOKENS = re.compile(r'[A-Za-z_][A-Za-z0-9_.-]*')
BRAND = re.compile(r'^(?:hap(?:$|[-_.])|mingdao|nocoly|mingo)', re.I)
FORBIDDEN = re.compile(r'明道[雲云]?|high[\s‐‑–-]*performance\s+application\s+platform', re.I)
ALLOW = {
    'HAP-Appid': 'protocol-header', 'HAP-Appkey': 'protocol-header',
    'HAP-Sign': 'protocol-header', 'hap': 'cli-command',
    'hap-cli': 'package', 'hap_cli': 'python-module', 'HAP_PROFILE': 'cli-environment',
}
LEGACY = {'hap-plan.json', 'hap-context.json'}
MIGRATION = 'mcp/niio-mcp-app-builder/scripts/project_files.py'

def audit(root):
    root = Path(root)
    counts, issues = Counter(), []
    for p in sorted(root.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts:
            continue
        rel = p.relative_to(root).as_posix()
        if re.search(r'(?i)(?:hap|mingdao|nocoly|mingo)(?:[-_.]|$)', p.name):
            issues.append({'path': rel, 'line': 0, 'reason': 'legacy-filename'})
        # Legal provenance is retained verbatim, not used as display branding.
        if p.stem.upper() in {'LICENSE', 'LICENCE', 'COPYING', 'NOTICE'}:
            counts['legal-provenance-file'] += 1
            continue
        try:
            text = p.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            continue  # Images require the separate visual acceptance task.
        for n, line in enumerate(text.splitlines(), 1):
            if FORBIDDEN.search(line):
                issues.append({'path': rel, 'line': n, 'reason': 'display-brand'})
            for token in TOKENS.findall(line):
                if not BRAND.search(token):
                    continue
                category = ALLOW.get(token)
                if token in LEGACY and rel == MIGRATION:
                    category = 'migration-compatibility'
                if category:
                    counts[category + ':' + token] += 1
                else:
                    issues.append({'path': rel, 'line': n, 'reason': 'unclassified-brand', 'token': token})
    return {'counts': dict(sorted(counts.items())), 'issues': issues}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    result = audit(args.root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(bool(result['issues']))
