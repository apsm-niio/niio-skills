#!/usr/bin/env python3
"""Local checkpoint bookkeeping only; never calls niio or verifies remote effects."""
import argparse
import json
import os
from pathlib import Path
from refresh_fields import write_atomic

PHASES = [('app_created', ['1']), ('worksheets_created', ['2']),
          ('fields_refreshed', ['3']), ('actions_created', ['4']),
          ('views_created', ['5']), ('sample_data_created', ['6']),
          ('page_shells_created', ['5b']), ('config_completed', ['7', '8', '9']),
          ('workflows_deployed', ['10', '11']), ('completed', ['12'])]
STEPS = [step for _, steps in PHASES for step in steps]


def inspect(context):
    state = context.get('buildState')
    if not isinstance(state, dict) or state.get('version') != 1:
        raise ValueError('缺少檢查點；既有專案先唯讀核對，禁止按 progress 直接重跑')
    records = state.get('steps')
    if not isinstance(records, dict) or set(records) != set(STEPS):
        raise ValueError('檢查點結構錯誤')
    for record in records.values():
        if not isinstance(record, dict) or record.get('status') not in ('pending', 'running', 'done'):
            raise ValueError('檢查點狀態錯誤')
        if record['status'] == 'done' and not record.get('evidence'):
            raise ValueError('完成步驟缺少驗證證據')
    unfinished = False
    for step in STEPS:
        status = records[step]['status']
        if unfinished and status != 'pending':
            raise ValueError('序列步驟順序不一致')
        if status != 'done':
            unfinished = True
    progress, next_steps, gap = None, [], False
    for value, steps in PHASES:
        complete = all(records[s]['status'] == 'done' for s in steps)
        if not gap and complete:
            progress = value
        elif not gap:
            gap = True
            next_steps = [s for s in steps if records[s]['status'] == 'pending'][:1]
        elif any(records[s]['status'] != 'pending' for s in steps):
            raise ValueError('步驟順序不一致，停止續跑')
    if context.get('progress') != progress:
        raise ValueError('progress 與檢查點不一致，停止續跑')
    running = [s for s in STEPS if records[s]['status'] == 'running']
    return {'progress': progress, 'blocked': bool(running), 'needsReconciliation': running,
            'nextSteps': [] if running else next_steps}


def change(context, command, step=None, evidence=None):
    if command == 'init':
        if context.get('buildState') is not None:
            inspect(context)
            return
        if any(value for key, value in context.items() if key not in ('cliAvailable', 'org_id')):
            raise ValueError('既有專案不能初始化為新建；先唯讀核對實際產物')
        context['progress'] = None
        context['buildState'] = {'version': 1, 'steps': {s: {'status': 'pending'} for s in STEPS}}
        return
    result = inspect(context)
    record = context['buildState']['steps'].get(step)
    if record is None:
        raise ValueError('未知步驟')
    if command == 'begin':
        if step not in result['nextSteps']:
            raise ValueError('步驟不可開始；已完成或未核對的步驟禁止重跑')
        record['status'] = 'running'
    elif command == 'finish':
        if record['status'] != 'running' or not isinstance(evidence, str) or not evidence.strip():
            raise ValueError('須先開始步驟，並提供已驗證的產物／對帳證據')
        record.update(status='done', evidence=evidence)
        progress = None
        for value, steps in PHASES:
            if not all(context['buildState']['steps'][s]['status'] == 'done' for s in steps):
                break
            progress = value
        context['progress'] = progress
    else:
        raise ValueError('未知命令')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['check', 'init', 'begin', 'finish'])
    parser.add_argument('context', type=Path)
    parser.add_argument('--step')
    parser.add_argument('--evidence')
    args = parser.parse_args()
    lock = args.context.with_name('.niio-build.lock')
    acquired = False
    try:
        if args.context.is_symlink():
            raise ValueError('不接受符號連結')
        if args.command != 'check':
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            acquired = True
            os.close(fd)
        context = json.loads(args.context.read_text(encoding='utf-8'))
        if not isinstance(context, dict):
            raise ValueError('context 必須是物件')
        if args.command != 'check':
            change(context, args.command, args.step, args.evidence)
            write_atomic(args.context, context)
        result = inspect(context)
        print(json.dumps(result, ensure_ascii=False))
        return 2 if args.command == 'check' and result['blocked'] else 0
    except (OSError, ValueError, TypeError) as error:
        print(json.dumps({'blocked': True, 'error': str(error)}, ensure_ascii=False))
        return 1
    finally:
        if acquired:
            lock.unlink()


if __name__ == '__main__':
    raise SystemExit(main())
