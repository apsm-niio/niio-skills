#!/usr/bin/env python3
"""Read-only source inventory, keyed by skill name; no installation or network."""
import argparse
import codecs
import json
import re
from pathlib import Path
from verify_install import manifest


def inventory(root):
    root = Path(root)
    result = {}
    for skill_file in sorted(root.glob('skills/*/*/SKILL.md')):
        name = skill_file.parent.name
        if name in result:
            raise ValueError('Duplicate skill name: ' + name)
        text = skill_file.read_text(encoding='utf-8-sig')
        header = text.split('---', 2)
        match = re.search(r'^name:\s*[\"\']?([^\s\"\']+)[\"\']?\s*$', header[1], re.M) if len(header) == 3 and not header[0].strip() else None
        if not match or match.group(1) != name:
            raise ValueError('SKILL.md name does not match directory: ' + name)
        files = manifest(skill_file.parent)
        result[name] = {'source': skill_file.parent.relative_to(root).as_posix(),
                        'fileCount': len(files), 'sha256': files}
    if len(result) != 8:
        raise ValueError('Expected eight unique top-level skills')
    ps = []
    for path in sorted(root.rglob('*')):
        if '.git' in path.parts or path.suffix.lower() not in ('.ps1', '.psm1', '.psd1') or not path.is_file():
            continue
        raw = path.read_bytes()
        ps.append({'path': path.relative_to(root).as_posix(),
                   'nonAsciiWithoutUtf8Bom': any(b > 127 for b in raw) and not raw.startswith(codecs.BOM_UTF8)})
    return {'skills': result, 'totalFiles': sum(x['fileCount'] for x in result.values()),
            'powershell': ps, 'scope': 'source-only; does not verify installed files, receipt, parser or remote access'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    result = inventory(args.source)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return int(any(x['nonAsciiWithoutUtf8Bom'] for x in result['powershell']))


if __name__ == '__main__':
    raise SystemExit(main())
