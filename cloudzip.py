# -*- coding: utf-8 -*-
"""ZIP packaging and manifests for projects published to O.GIS Cloud."""

import hashlib
import json
import os
import re
import zipfile

SLUG_RE = re.compile(r'^[a-zA-Z0-9_-]{1,100}$')
LOCAL_ONLY = ('start_server.py',)
LOCAL_PREFIXES = ('show_map_with_server-',)
LOCAL_SUFFIXES = ('.pbf.lock',)
MAX_UNCOMPRESSED_BYTES = 2 * 1024 * 1024 * 1024
HISTORY_DIRS = {'.history'}
OPENLAYERS_DIRS = {'resources'}
LEAFLET_DIRS = {'css', 'js'}


class ZipBuildError(Exception):
    def __init__(self, message, details=None):
        super(ZipBuildError, self).__init__(message)
        self.message = message
        self.details = list(details or [])


class ZipBuildResult:
    def __init__(self, path, slug):
        self.path = path
        self.slug = slug
        self.files = {}
        self.skipped = []
        self.archive_bytes = 0
        self.uncompressed_bytes = 0

    def __len__(self):
        return len(self.files)


def normalize_slug(text):
    text = re.sub(r'[^a-z0-9_-]+', '-', (text or '').strip().lower())
    return re.sub(r'-+', '-', text).strip('-_')[:100]


def _hash(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _collect_directories(source_folder, allowed_dirs, limits):
    """List safe project directories so empty folders survive ZIP extraction."""
    max_depth = int(limits.get('max_path_depth', 30))
    max_segment = int(limits.get('max_segment_length', 255))
    directories = []
    invalid = []

    for current, folders, _ in os.walk(source_folder):
        folders[:] = sorted(folder for folder in folders
                            if not folder.startswith('.')
                            and not os.path.islink(os.path.join(current, folder)))
        for folder in folders:
            path = os.path.join(current, folder)
            relative = os.path.relpath(path, source_folder).replace(os.sep, '/')
            segments = relative.split('/')
            if len(segments) > max_depth or any(len(part) > max_segment for part in segments):
                invalid.append(relative)
            elif segments[0] in allowed_dirs:
                directories.append(relative)

    if invalid:
        raise ZipBuildError('The export includes directories outside the website path limits.',
                            invalid[:100])
    return directories


def build_project_zip(source_folder, zip_path, slug, policy, progress=None,
                      include_paths=None, create_archive=True, removed_paths=None):
    if not SLUG_RE.match(slug or ''):
        raise ZipBuildError('Project name must contain only letters, numbers, underscores or hyphens (1-100 characters).')
    if not os.path.isdir(source_folder):
        raise ZipBuildError('The export folder does not exist: {}'.format(source_folder))
    rules = policy.get('rules', policy) if isinstance(policy, dict) else {}
    allowed_dirs = set(rules.get('allowed_top_level_dirs', ()))
    allowed_files = set(rules.get('allowed_root_files', ('index.html', 'README.txt')))
    extensions = {ext.lower() for ext in rules.get('allowed_extensions', ())}
    required = rules.get('required_entry_file', 'index.html')
    limits = policy.get('limits', {}) if isinstance(policy, dict) else {}
    max_depth = int(limits.get('max_path_depth', 30))
    max_entries = int(limits.get('max_entries', 50000))
    max_segment = int(limits.get('max_segment_length', 255))
    max_archive_bytes = int(limits.get('max_archive_bytes', 0) or 0)
    max_post_bytes = int(limits.get('max_post_bytes', 0) or 0)
    publish, skipped, refused = [], [], []
    uncompressed_bytes = 0
    for root, folders, names in os.walk(source_folder):
        folders[:] = sorted(folder for folder in folders
                            if not folder.startswith('.') and folder not in HISTORY_DIRS)
        for name in sorted(names):
            path = os.path.join(root, name)
            rel = os.path.relpath(path, source_folder).replace(os.sep, '/')
            if os.path.islink(path) or name.startswith('.') or name in HISTORY_DIRS:
                skipped.append(rel)
                continue
            low = name.lower()
            if low in LOCAL_ONLY or low.startswith(LOCAL_PREFIXES) or low.endswith(LOCAL_SUFFIXES) or name.endswith('~'):
                skipped.append(rel)
                continue
            segments = rel.split('/')
            ext = os.path.splitext(name)[1].lower().lstrip('.')
            if len(segments) > max_depth or any(len(part) > max_segment for part in segments):
                refused.append(rel)
            elif len(segments) == 1 and name not in allowed_files:
                refused.append(rel)
            elif len(segments) > 1 and segments[0] not in allowed_dirs:
                refused.append(rel)
            elif ext not in extensions:
                refused.append(rel)
            else:
                publish.append((path, rel))
                uncompressed_bytes += os.path.getsize(path)
    if refused:
        raise ZipBuildError('The export includes files or folders not accepted by the website.', refused[:100])

    top_directories = {entry for entry in os.listdir(source_folder)
                       if os.path.isdir(os.path.join(source_folder, entry))
                       and not entry.startswith('.') and entry not in HISTORY_DIRS}
    index_path = os.path.join(source_folder, required)
    try:
        with open(index_path, encoding='utf-8', errors='replace') as stream:
            index_html = stream.read(1024 * 1024)
    except OSError:
        index_html = ''
    leaflet_signature = (
        os.path.isfile(os.path.join(source_folder, 'js', 'leaflet.js')) and
        os.path.isfile(os.path.join(source_folder, 'css', 'leaflet.css')) and
        re.search(r'''(?:src|href)\s*=\s*["'](?:\./)?js/leaflet\.js["']''',
                  index_html, re.IGNORECASE) and
        re.search(r'''(?:src|href)\s*=\s*["'](?:\./)?css/leaflet\.css["']''',
                  index_html, re.IGNORECASE)
    )
    openlayers_script = next((filename for filename in ('qgis2web.js', 'qgis2ogis.js')
                              if os.path.isfile(os.path.join(source_folder,
                                                             'resources', filename))
                              and re.search(
                                  r'''(?:src|href)\s*=\s*["'](?:\./)?resources/{}["']'''
                                  .format(re.escape(filename)), index_html,
                                  re.IGNORECASE)), None)
    if not leaflet_signature and not openlayers_script:
        raise ZipBuildError('The folder does not have the expected qgis2web Leaflet or OpenLayers export structure.')
    unexpected_directories = sorted(top_directories - allowed_dirs)
    if unexpected_directories:
        raise ZipBuildError(
            'The export includes folders that the website does not allow.',
            unexpected_directories)

    directories = _collect_directories(source_folder, allowed_dirs, limits)
    if len(publish) > max_entries:
        raise ZipBuildError('The export exceeds the website file-count limit ({}).'.format(max_entries))
    if len(publish) + len(directories) > max_entries:
        raise ZipBuildError('The export exceeds the website ZIP-entry limit ({}).'.format(max_entries))
    if uncompressed_bytes > MAX_UNCOMPRESSED_BYTES:
        raise ZipBuildError('The export exceeds the safe local packaging limit ({} bytes).'.format(
            MAX_UNCOMPRESSED_BYTES))
    if required not in {rel for _, rel in publish}:
        raise ZipBuildError('The export does not contain the required {} file.'.format(required))

    if include_paths is not None:
        selected_paths = set(include_paths)
        available_paths = {relative for _, relative in publish}
        missing_paths = sorted(selected_paths - available_paths)
        if missing_paths:
            raise ZipBuildError('The update contains paths not found in the validated export.',
                                missing_paths[:100])
        publish = [(path, relative) for path, relative in publish
                   if relative in selected_paths]
        directories = []
    removed_paths = list(removed_paths or [])
    if removed_paths and include_paths is None:
        raise ZipBuildError('Removed paths can only be included in a delta update.')
    if include_paths is not None and len(publish) + len(removed_paths) + 2 > max_entries:
        raise ZipBuildError('The update exceeds the website ZIP-entry limit ({}).'.format(
            max_entries))

    result = ZipBuildResult(zip_path, slug)
    result.skipped = skipped
    result.uncompressed_bytes = uncompressed_bytes
    if create_archive:
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as archive:
                if include_paths is not None:
                    archive.writestr('{}/'.format(slug), '')
                for relative in directories:
                    archive.writestr('{}/{}/'.format(slug, relative), '')
                for index, (path, rel) in enumerate(publish, 1):
                    archive.write(path, '{}/{}'.format(slug, rel))
                    result.files[rel] = {'sha256': _hash(path), 'size': os.path.getsize(path)}
                    if progress and (index % 25 == 0 or index == len(publish)):
                        progress(index, len(publish))
                if include_paths is not None:
                    metadata = json.dumps(
                        {'schema': 1, 'removed_paths': removed_paths},
                        separators=(',', ':')).encode('utf-8')
                    archive.writestr('{}/__ogis_delta__.json'.format(slug), metadata)
                    result.uncompressed_bytes += len(metadata)
            result.archive_bytes = os.path.getsize(zip_path)
            if max_archive_bytes and result.archive_bytes > max_archive_bytes:
                raise ZipBuildError('The ZIP archive exceeds the site upload limit ({} bytes).'.format(
                    max_archive_bytes))
            if max_post_bytes and result.archive_bytes > max_post_bytes:
                raise ZipBuildError('The ZIP archive exceeds the server upload limit ({} bytes).'.format(max_post_bytes))
        except Exception:
            try:
                os.remove(zip_path)
            except OSError:
                pass
            raise
    else:
        for index, (path, rel) in enumerate(publish, 1):
            result.files[rel] = {'sha256': _hash(path), 'size': os.path.getsize(path)}
            if progress and (index % 25 == 0 or index == len(publish)):
                progress(index, len(publish))
    return result


def compare_with_manifest(local_files, remote_files):
    remote_files = remote_files or {}
    local_files = local_files or {}
    added, updated, unchanged = [], [], 0
    for path, local in (local_files or {}).items():
        remote = remote_files.get(path)
        if remote is None:
            added.append(path)
        elif remote.get('sha256') == local.get('sha256'):
            unchanged += 1
        else:
            updated.append(path)
    removed = sorted(set(remote_files) - set(local_files))
    return {'added': sorted(added), 'updated': sorted(updated),
            'removed': removed, 'unchanged': unchanged}


def merge_preserved_remote_files(local_files, preserved_paths, remote_files):
    """Include remote-only files omitted from an incremental staging folder."""
    merged = dict(local_files or {})
    remote_files = remote_files or {}
    for path in sorted(set(preserved_paths or ())):
        relative = str(path).replace('\\', '/')
        parts = relative.split('/')
        if (not relative or relative.startswith('/')
                or any(part in ('', '.', '..') for part in parts)):
            raise ZipBuildError(
                'The incremental export contains an invalid preserved path.',
                [relative])
        if relative in merged:
            continue
        remote = remote_files.get(relative)
        if not isinstance(remote, dict):
            raise ZipBuildError(
                'The remote manifest is missing a preserved export file.',
                [relative])
        sha256 = remote.get('sha256')
        size = remote.get('size')
        if (not isinstance(sha256, str) or not sha256
                or isinstance(size, bool) or not isinstance(size, int)
                or size < 0):
            raise ZipBuildError(
                'The remote manifest is missing a preserved export file.',
                [relative])
        merged[relative] = {
            'sha256': sha256,
            'size': size,
        }
    return merged
