#!/usr/bin/env python3
"""Offline validation of sanitized HTTP/CLI/SDK captures; no network or subprocess.
Use --fixture for bundled mock cases. Real captures need a deployment-approved contract.
"""
import argparse
import json
from pathlib import Path


def check(contract, capture):
    if contract.get('channel') not in ('api', 'cli', 'website', 'view'):
        raise ValueError('Unknown channel')
    if capture.get('status') != 200 or 'application/json' not in capture.get('contentType', '').lower():
        raise ValueError('Expected successful JSON; HTTP/HTML failures are not accepted')
    value = capture.get('body')
    success = value
    for key in contract['successPath']:
        if not isinstance(success, dict) or key not in success:
            raise ValueError('Missing business success marker')
        success = success[key]
    if type(success) is not type(contract['successValue']) or success != contract['successValue']:
        raise ValueError('Business response indicates failure')
    for key in contract['rowsPath']:
        if not isinstance(value, dict) or key not in value:
            raise ValueError('Response shape differs from approved contract')
        value = value[key]
    if not isinstance(value, list):
        raise ValueError('Rows must be an array')
    if not contract['minRows'] <= len(value) <= contract['maxRows']:
        raise ValueError('Unexpected row count')
    for row in value:
        if not isinstance(row, dict) or set(row) != set(contract['allowedFields']):
            raise ValueError('Unexpected/missing fields; redact before retaining evidence')
        if not all(isinstance(row[k], str) for k in contract['allowedFields']):
            raise ValueError('Expected sanitized string fields')
    if capture.get('target') != contract['target']:
        raise ValueError('Wrong application/worksheet/view target')
    return {'channel': contract['channel'], 'rows': len(value),
            'status': 'capture-contract-passed', 'remoteRequestPerformed': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--contract', required=True, type=Path)
    p.add_argument('--capture', required=True, type=Path)
    p.add_argument('--fixture', action='store_true')
    args = p.parse_args()
    try:
        contract = json.loads(args.contract.read_text(encoding='utf-8'))
        if not args.fixture and contract.get('deploymentApproved') is not True:
            raise ValueError('Deployment contract not approved; use mocks only')
        result = check(contract, json.loads(args.capture.read_text(encoding='utf-8')))
        result['evidenceKind'] = 'mock' if args.fixture else 'supplied-capture; provenance requires human review'
        print(json.dumps(result, ensure_ascii=False))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        p.exit(1, 'Acceptance failed: ' + str(exc) + '\n')


if __name__ == '__main__':
    main()
