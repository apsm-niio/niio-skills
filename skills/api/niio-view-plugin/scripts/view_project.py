#!/usr/bin/env python3
"""Validate explicit mdye initialization inputs, or preflight an existing project.
Outputs an argv plan only; never logs in, installs dependencies, or makes requests.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
from urllib.parse import urlsplit


def url(value):
    parsed = urlsplit(value)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError('Use a confirmed HTTPS URL without embedded credentials/query/fragment')
    if parsed.hostname.endswith('.invalid'):
        raise ValueError('Placeholder URLs cannot be used')
    return value


def plan(identifier, template, host, webui):
    if not re.fullmatch(r'[A-Za-z0-9_]+-[A-Za-z0-9_]+', identifier):
        raise ValueError('Copy the actual worksheetId-viewId from the development panel; never generate IDs')
    if template not in ('React', 'Vue', 'JavaScript'):
        raise ValueError('Confirm supported template from the deployment panel')
    return ['mdye', 'init', 'view', '--id', identifier, '--template', template,
            '--host', url(host), '--webui', url(webui)]


def preflight(project):
    root = Path(project).resolve(strict=True)
    config = json.loads((root / 'mdye.json').read_text(encoding='utf-8'))
    package = json.loads((root / 'package.json').read_text(encoding='utf-8'))
    if not isinstance(config, dict) or not isinstance(package, dict):
        raise ValueError('Project JSON must be objects')
    plan(config.get('id', ''), config.get('template', ''), config.get('host', ''), config.get('webui', ''))
    if not (root / 'src').is_dir():
        raise ValueError('Missing src directory')
    if not (root / 'node_modules').is_dir():
        raise ValueError('Dependencies absent; review lockfile and install in this project explicitly')
    return {'cwd': str(root), 'argv': ['mdye', 'start'], 'status': 'preflight-only',
            'note': 'Use the actual startup URL; exit code alone is not evidence of successful serving'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='action', required=True)
    init = sub.add_parser('init-plan')
    for key in ('id', 'template', 'host', 'webui'):
        init.add_argument('--' + key, required=True)
    start = sub.add_parser('preflight')
    start.add_argument('project', type=Path)
    sub.add_parser('check')
    args = p.parse_args()
    try:
        if args.action == 'init-plan':
            result = {'argv': plan(args.id, args.template, args.host, args.webui), 'executed': False}
        elif args.action == 'preflight':
            result = preflight(args.project)
        else:
            result = {name: shutil.which(name) for name in ('node', 'mdye')}
            if not all(result.values()):
                raise ValueError('node/mdye missing from PATH; no automatic installation')
            result['status'] = 'PATH presence only; version and deployment compatibility untested'
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError, TypeError) as exc:
        p.exit(1, 'Preflight failed: ' + str(exc) + '\n')


if __name__ == '__main__':
    main()
