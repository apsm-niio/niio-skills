#!/usr/bin/env python3
"""niio 專案狀態檔案檢查與可續跑遷移；不連線、不改 JSON 內容。"""
import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

NAMES = {'plan': ('niio-plan.json', 'hap-plan.json'),
         'context': ('niio-context.json', 'hap-context.json')}


class ProjectFileError(ValueError):
    pass


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ProjectFileError('JSON 有重複鍵，請先確認內容')
        result[key] = value
    return result


def _read(path):
    if path.is_symlink():
        raise ProjectFileError('狀態檔案不可為符號連結')
    if not path.exists():
        return None
    if not path.is_file():
        raise ProjectFileError('狀態路徑不是一般檔案')
    raw = path.read_bytes()
    try:
        value = json.loads(raw, object_pairs_hook=_pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
        if not isinstance(value, dict):
            raise ValueError()
        canonical = json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)
    except (ValueError, UnicodeError, RecursionError):
        raise ProjectFileError('狀態檔案不是有效 JSON 物件，停止以免重建或覆蓋') from None
    return raw, canonical


def inspect_project(directory, require_plan=True):
    root = Path(directory)
    if root.is_symlink() or not root.is_dir():
        raise ProjectFileError('專案目錄不存在或為符號連結')
    result = {}
    for kind, (current, legacy) in NAMES.items():
        new, old = _read(root / current), _read(root / legacy)
        if new and old and new[1] != old[1]:
            raise ProjectFileError(f'{kind} 新舊檔案內容不同，請人工確認；未修改任何狀態檔案')
        selected = current if new else legacy if old else None
        result[kind] = {'path': str(root / selected) if selected else None,
                        'needsMigration': old is not None}
    if require_plan and result['context']['path'] and not result['plan']['path']:
        raise ProjectFileError('有進度但缺少方案，停止以免重建既有應用')
    return result


def _create_once(path, raw):
    """先完成暫存內容，再以不覆蓋目的檔的原子 link 公開。"""
    temp = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.niio-state-', delete=False) as handle:
            temp = Path(handle.name)
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temp, path)
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)


def migrate_project(directory):
    root = Path(directory)
    # 先確認目錄，避免跟隨使用者指定的符號連結。
    inspect_project(root)
    lock = root / '.niio-migration.lock'
    try:
        descriptor = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise ProjectFileError('遷移鎖存在，請確認沒有其他程序執行；不要自動刪鎖') from None
    os.close(descriptor)
    try:
        state = inspect_project(root)  # 所有衝突先檢查完，再搬移任何一組檔案。
        pending = [(kind, root / names[0], root / names[1]) for kind, names in NAMES.items()
                   if state[kind]['needsMigration']]
        if not pending:
            return state
        backup_dir = root / '.niio-legacy'
        if backup_dir.is_symlink():
            raise ProjectFileError('備份目錄不可為符號連結')
        backup_dir.mkdir(exist_ok=True, mode=0o700)
        for kind, current, legacy in pending:
            old = _read(legacy)
            if old is None:
                raise ProjectFileError('遷移期間檔案改變，請停止其他寫入後重試')
            raw = old[0]
            backup = backup_dir / (legacy.stem + '-' + hashlib.sha256(raw).hexdigest() + '.json')
            existing = _read(backup)
            if existing is None:
                _create_once(backup, raw)
            elif existing[0] != raw:
                raise ProjectFileError('備份內容不符，停止遷移')
            new = _read(current)
            if new is None:
                _create_once(current, raw)
            elif new[1] != old[1]:
                raise ProjectFileError('遷移期間發現新舊衝突，停止遷移')
            # 此時新檔及備份均已存在；中斷後可重新檢查並續跑。
            if _read(legacy) != old or _read(current)[1] != old[1]:
                raise ProjectFileError('遷移期間檔案改變，保留舊檔並停止')
            legacy.unlink()
        return inspect_project(root)
    finally:
        lock.unlink()


def resolve_context(path):
    path = Path(path)
    if path.name not in NAMES['context']:
        return path
    state = inspect_project(path.parent, require_plan=False)
    if not state['context']['path']:
        raise ProjectFileError('缺少進度檔案')
    return Path(state['context']['path'])


def main():
    parser = argparse.ArgumentParser(description='檢查或遷移 niio 專案檔名')
    parser.add_argument('action', choices=['check', 'migrate'])
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    try:
        state = (migrate_project if args.action == 'migrate' else inspect_project)(args.directory)
        print(json.dumps({'success': True, 'files': state}, ensure_ascii=False))
        return 0
    except ProjectFileError as error:
        print(f'專案檔案檢查或遷移失敗：{error}；停止建置。', file=sys.stderr)
        return 1
    except OSError:
        print('專案檔案檢查或遷移失敗：請確認目錄權限與檔案狀態；停止建置，不自動覆蓋或重建。', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
