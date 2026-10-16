#!/usr/bin/env python3
"""Install/update all eight skills with an explicit baseline; restore from receipt.

Only the named skill directories are touched. Unknown/custom files block updates.
Renames preserve backups; no hardlink fallback, elevation, or global configuration.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile


def inventory(root):
    root = Path(root)
    result = {}
    for p in [root, *root.rglob('*')]:
        if p.is_symlink() or (hasattr(p, 'is_junction') and p.is_junction()):
            raise ValueError('Linked paths are not supported: ' + str(p))
        # Windows junction/reparse points also on Python 3.10.
        if p.exists() and getattr(p.lstat(), 'st_file_attributes', 0) & 0x400:
            raise ValueError('Reparse point rejected: ' + str(p))
        if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc', '.pyo'):
            result[p.relative_to(root).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return result


def skills(source):
    found = {p.parent.name: p.parent for p in Path(source).glob('skills/*/*/SKILL.md')}
    if len(found) != 8:
        raise ValueError('Expected eight top-level skills')
    return found


def write_receipt(path, data):
    # A failed replace must not leave a fixed .tmp that blocks every retry.
    fd, name = tempfile.mkstemp(prefix='.receipt-', suffix='.tmp', dir=path.parent)
    temp = Path(name)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def install(source, target, baseline=None):
    target = Path(target).absolute()
    # Reject linked ancestors before resolve could hide their identity.
    for p in [target, *target.parents]:
        if p.exists() and (p.is_symlink() or getattr(p.lstat(), 'st_file_attributes', 0) & 0x400):
            raise ValueError('Linked installation parent rejected')
    target.mkdir(parents=True, exist_ok=True)
    incoming = skills(source)
    previous = skills(baseline) if baseline else {}
    lock = target / '.niio-install.lock'
    with lock.open('x'):
        pass
    receipt = None
    try:
        for name, path in incoming.items():
            inventory(path)
            dest = target / name
            if dest.exists():
                if name not in previous or inventory(dest) != inventory(previous[name]):
                    raise ValueError('Existing skill differs from baseline; preserve custom files: ' + name)
        backup = Path(tempfile.mkdtemp(prefix='.niio-backup-', dir=target.parent))
        receipt = backup / 'receipt.json'
        data = {'target': str(target), 'state': 'installing', 'entries': []}
        for name, path in incoming.items():
            staged = backup / (name + '.new')
            shutil.copytree(path, staged, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.pyo'))
            if inventory(staged) != inventory(path):
                raise ValueError('Staged copy mismatch: ' + name)
            data['entries'].append({'name': name, 'old': (target / name).exists(),
                                    'oldHashes': inventory(target / name) if (target / name).exists() else None,
                                    'hashes': inventory(path)})
        write_receipt(receipt, data)
        for entry in data['entries']:
            name = entry['name']
            if entry['old']:
                (target / name).rename(backup / name)
            (backup / (name + '.new')).rename(target / name)
        data['state'] = 'installed'
        write_receipt(receipt, data)
        return receipt
    except Exception as install_error:
        if receipt and receipt.exists():
            try:
                restore(receipt, locked=True)
            except Exception as restore_error:
                raise OSError(
                    f'Install failed: {install_error}; automatic restore failed: {restore_error}. '
                    f'Resume restore with --receipt "{receipt}"; preserve all directories.'
                ) from restore_error
        raise
    finally:
        lock.unlink()


def restore_stage(entry, target, backup):
    """Reconcile the journal with rename artifacts, including a stale checkpoint.

    Never identify an old installation solely by its contents: old/new hashes
    can be equal. Directory locations prove which move has completed.
    """
    name = entry['name']
    paths = [target / name, backup / name, backup / (name + '.new'),
             backup / (name + '.restored-new')]
    present = tuple(os.path.lexists(p) for p in paths)
    # (destination, old backup, unconsumed staging, evacuated new version)
    layouts = ({
        (True, True, False, False): ('pending', entry['hashes']),
        (False, True, False, True): ('new-saved', None),
        (True, False, False, True): ('restored', entry['oldHashes']),
        (True, False, True, False): ('restored', entry['oldHashes']),
        (False, True, True, False): ('new-saved', None),
    } if entry['old'] else {
        (True, False, False, False): ('pending', entry['hashes']),
        (False, False, False, True): ('restored', None),
        (False, False, True, False): ('restored', None),
    })
    if present not in layouts:
        raise ValueError('Missing/conflicting restore artifacts; preserve files: ' + name)
    stage, dest_hashes = layouts[present]
    for path, exists, expected in zip(paths, present,
                                     [dest_hashes, entry['oldHashes'], entry['hashes'], entry['hashes']]):
        if exists and (not path.is_dir() or inventory(path) != expected):
            raise ValueError('Modified installation/backup blocks restore: ' + name)
    if entry.get('restoreState') == 'restored' and stage != 'restored':
        raise ValueError('Completed restore has conflicting artifacts: ' + name)
    return stage


def restore(receipt, locked=False):
    receipt = Path(receipt).absolute()
    data = json.loads(receipt.read_text(encoding='utf-8'))
    target, backup = Path(data['target']), receipt.parent
    if backup.parent != target.parent or not backup.name.startswith('.niio-backup-'):
        raise ValueError('Receipt outside expected target')
    for p in [receipt, backup, target, *target.parents]:
        if p.exists() and (p.is_symlink() or getattr(p.lstat(), 'st_file_attributes', 0) & 0x400):
            raise ValueError('Linked restore path rejected')
    if data['state'] not in ('installed', 'installing', 'restoring', 'restored'):
        raise ValueError('Invalid receipt state')
    lock = target / '.niio-install.lock'
    if not locked:
        with lock.open('x'):
            pass
    try:
        names = set()
        for entry in data['entries']:
            name = entry['name']
            if Path(name).name != name or name in ('.', '..') or not name.startswith('niio-') or name in names:
                raise ValueError('Invalid receipt skill name')
            names.add(name)
            stage = restore_stage(entry, target, backup)
            if data['state'] == 'restored' and stage != 'restored':
                raise ValueError('Completed receipt has conflicting artifacts: ' + name)
            entry['restoreState'] = stage
        if data['state'] == 'restored':
            return
        data['state'] = 'restoring'
        write_receipt(receipt, data)
        for entry in reversed(data['entries']):
            name = entry['name']
            dest = target / name
            stage = restore_stage(entry, target, backup)
            if stage == 'pending':
                entry['restoreState'] = 'saving-new'
                write_receipt(receipt, data)
                dest.rename(backup / (name + '.restored-new'))
                entry['restoreState'] = 'new-saved'
                write_receipt(receipt, data)
                stage = restore_stage(entry, target, backup)
            if stage == 'new-saved':
                entry['restoreState'] = 'restoring-old'
                write_receipt(receipt, data)
                (backup / name).rename(dest)
            if restore_stage(entry, target, backup) != 'restored':
                raise ValueError('Restore did not reach expected layout: ' + name)
            entry['restoreState'] = 'restored'
            write_receipt(receipt, data)
        data['state'] = 'restored'
        write_receipt(receipt, data)
    finally:
        if not locked:
            lock.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    p = sub.add_parser('install')
    p.add_argument('--source', required=True, type=Path)
    p.add_argument('--target', required=True, type=Path)
    p.add_argument('--baseline', type=Path)
    p = sub.add_parser('restore')
    p.add_argument('--receipt', required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.action == 'install':
            print(install(args.source, args.target, args.baseline))
        else:
            restore(args.receipt)
            print('Restored; backups retained')
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, 'Installation/restore blocked: ' + str(exc) + '\n')


if __name__ == '__main__':
    main()
