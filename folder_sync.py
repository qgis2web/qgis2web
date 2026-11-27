# -*- coding: utf-8 -*-
"""Incremental updates for local qgis2web exports."""

import os

try:
    from .customcode import ensure_custom_code
    from .sync_core import apply_sync as _apply_sync
    from .sync_core import plan_sync as _plan_sync
    from .sync_core import relative_files
except ImportError:
    from customcode import ensure_custom_code
    from sync_core import apply_sync as _apply_sync
    from sync_core import plan_sync as _plan_sync
    from sync_core import relative_files

GENERATED_ROOTS = {
    'css', 'data', 'images', 'js', 'layers', 'legend', 'markers',
    'resources', 'styles', 'webfonts',
}
GENERATED_FILES = {
    'index.html', 'README.txt', 'start_server.py',
    'show_map_with_server-linux.sh', 'show_map_with_server-mac.command',
    'show_map_with_server-win.bat',
}
HISTORY_DIR = '.history'
NO_BACKUP_ROOTS = ('layers/layers_tiles',)
NO_BACKUP_SUFFIXES = ('.pbf', '.pbf.lock')
HISTORY_DIRS = {HISTORY_DIR}


def _files(folder):
    return relative_files(
        folder, excluded_dirs=HISTORY_DIRS,
        excluded_top_level_dirs={'custom_code'},
        excluded_top_level_files={'custom_code'}, skip_symlinks=True)


def _generated(path):
    parts = path.split('/')
    return parts[0] in GENERATED_ROOTS or path in GENERATED_FILES


def is_no_backup(relative_path):
    normalized = relative_path.replace(os.sep, '/')
    if normalized.endswith(NO_BACKUP_SUFFIXES):
        return True
    return any(normalized == root or normalized.startswith(root + '/')
               for root in NO_BACKUP_ROOTS)


def _native_path(folder, relative_path):
    return os.path.join(folder, relative_path.replace('/', os.sep))


def _console(message):
    try:
        print(message)
    except UnicodeEncodeError:
        print(message.encode('ascii', 'replace').decode('ascii'))


def _tile_roots(relative_paths):
    roots = {}
    for relative_path in relative_paths:
        parts = relative_path.split('/')
        root = relative_path
        for index, part in enumerate(parts[1:-1], start=1):
            if part.isdigit():
                root = '/'.join(parts[:index])
                break
        roots[root] = roots.get(root, 0) + 1
    return roots


def report_plan(plan, workspace, limit=12, console_limit=200):
    removed = plan.get('removed') or []
    groups = (
        ('Preserved, not touched', plan.get('preserved') or []),
        ('Removed generated files',
         [path for path in removed if not is_no_backup(path)]),
    )
    _console('[qgis2web] Local Update plan for {}'.format(workspace))
    for label, entries in groups:
        if not entries:
            continue
        _console('[qgis2web] {}: {}'.format(label, len(entries)))
        for relative_path in entries[:console_limit]:
            _console('[qgis2web]     {}'.format(
                _native_path(workspace, relative_path)))
        if len(entries) > console_limit:
            _console('[qgis2web]     ... and {} more'.format(
                len(entries) - console_limit))

    tiles = [path for path in removed if is_no_backup(path)]
    if tiles:
        _console('[qgis2web] Vector tiles deleted without backup: {}'.format(len(tiles)))
        for root, count in _tile_roots(tiles).items():
            _console('[qgis2web]     {}  ({} files)'.format(
                _native_path(workspace, root), count))

    preserved = plan.get('preserved') or []
    if not preserved:
        return ''
    detail = '\n'.join('    {}'.format(name) for name in preserved[:limit])
    if len(preserved) > limit:
        detail += ('\n    ... and {} more (full list in the Python '
                   'console)').format(len(preserved) - limit)
    return detail


def plan_sync(staging, workspace, preserved_paths=()):
    return _plan_sync(staging, workspace, _files, _generated, preserved_paths)


def apply_sync(staging, workspace, plan):
    """Apply a reviewed sync plan and return the history folder, if created."""
    history = _apply_sync(staging, workspace, plan, HISTORY_DIR, _files,
                          is_no_backup)
    ensure_custom_code(workspace)
    return history
