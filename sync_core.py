"""QGIS-independent file planning and application for local export updates."""

import os
import shutil
from datetime import datetime


def relative_files(folder, excluded_dirs=(), excluded_top_level_dirs=(),
                   excluded_top_level_files=(), skip_symlinks=False):
    files = {}
    if not os.path.isdir(folder):
        return files
    top = os.path.abspath(folder)
    for root, dirs, names in os.walk(folder):
        dirs[:] = [name for name in dirs if name not in excluded_dirs]
        if os.path.abspath(root) == top:
            dirs[:] = [name for name in dirs
                       if name not in excluded_top_level_dirs]
        for name in names:
            if (os.path.abspath(root) == top and
                    name in excluded_top_level_files):
                continue
            path = os.path.join(root, name)
            if skip_symlinks and os.path.islink(path):
                continue
            files[os.path.relpath(path, folder).replace(os.sep, '/')] = path
    return files


def same_file(first, second):
    if not os.path.isfile(first) or not os.path.isfile(second):
        return False
    if os.path.getsize(first) != os.path.getsize(second):
        return False
    with open(first, 'rb') as file_a, open(second, 'rb') as file_b:
        while True:
            chunk_a = file_a.read(1024 * 1024)
            if chunk_a != file_b.read(1024 * 1024):
                return False
            if not chunk_a:
                return True


def plan_sync(staging, workspace, collect_files, is_generated,
              preserved_paths=()):
    new_files = collect_files(staging)
    old_files = collect_files(workspace)
    preserved_paths = {
        path.replace('\\', '/') for path in preserved_paths
    }
    added = []
    updated = []
    unchanged = []
    preserved = []
    removed = []

    for relative_path, new_path in sorted(new_files.items()):
        old_path = old_files.get(relative_path)
        if old_path and same_file(old_path, new_path):
            unchanged.append(relative_path)
        elif old_path:
            updated.append(relative_path)
        else:
            added.append(relative_path)

    unchanged.extend(
        relative_path for relative_path in sorted(preserved_paths)
        if relative_path not in new_files and relative_path in old_files)
    for relative_path in sorted(old_files):
        if (relative_path not in new_files
                and relative_path not in preserved_paths):
            (removed if is_generated(relative_path) else preserved).append(
                relative_path)

    return {
        'added': added,
        'updated': updated,
        'unchanged': sorted(set(unchanged)),
        'preserved': sorted(set(preserved)),
        'removed': removed,
    }


def apply_sync(staging, workspace, plan, history_dir, collect_files,
               is_no_backup):
    os.makedirs(workspace, exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    history = os.path.join(workspace, history_dir, stamp)
    old_files = collect_files(workspace)

    for relative_path in plan['updated'] + plan['removed']:
        if is_no_backup(relative_path):
            continue
        old_path = old_files.get(relative_path)
        if old_path:
            backup_path = os.path.join(history, *relative_path.split('/'))
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            shutil.copy2(old_path, backup_path)

    for relative_path in plan['added'] + plan['updated']:
        source = os.path.join(staging, *relative_path.split('/'))
        destination = os.path.join(workspace, *relative_path.split('/'))
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        shutil.copy2(source, destination)

    for relative_path in plan['removed']:
        destination = os.path.join(workspace, *relative_path.split('/'))
        if os.path.isfile(destination):
            os.remove(destination)

    return history if os.path.isdir(history) else None