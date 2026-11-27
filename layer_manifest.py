# -*- coding: utf-8 -*-
"""Layer-data hashes and reuse plans for incremental qgis2web exports."""

import hashlib
import json
import os
from xml.parsers.expat import ExpatError

if __package__:
    from . import xmltodict
else:
    import xmltodict


MANIFEST_NAME = 'layers_manifest.js'
MANIFEST_PREFIX = 'window.OGIS_LAYER_MANIFEST = '
PBF_CACHE_SCHEMA = 2


def empty_manifest():
    return {'version': 1, 'nextPermalink': 1, 'layers': []}


def _xml_elements(document, local_name):
    if isinstance(document, dict):
        for name, value in document.items():
            if name.rsplit(':', 1)[-1] == local_name:
                yield value
            else:
                yield from _xml_elements(value, local_name)
    elif isinstance(document, list):
        for value in document:
            yield from _xml_elements(value, local_name)


def parse_manifest(text):
    text = (text or '').strip()
    if not text.startswith(MANIFEST_PREFIX) or not text.endswith(';'):
        raise ValueError('The layer manifest has an unsupported format.')
    try:
        manifest = json.loads(text[len(MANIFEST_PREFIX):-1].strip())
    except (TypeError, ValueError) as error:
        raise ValueError('The layer manifest contains invalid JSON.') from error
    if (not isinstance(manifest, dict)
            or manifest.get('version') != 1
            or not isinstance(manifest.get('layers'), list)):
        raise ValueError('The layer manifest has an unsupported schema.')

    next_permalink = manifest.get('nextPermalink', 1)
    if (isinstance(next_permalink, bool)
            or not isinstance(next_permalink, int)
            or next_permalink < 1):
        raise ValueError('The layer manifest has an invalid next permalink.')
    manifest['nextPermalink'] = next_permalink
    qgis_ids, permalinks = set(), set()
    for record in manifest['layers']:
        if not isinstance(record, dict):
            raise ValueError('The layer manifest contains an invalid layer record.')
        qgis_id = record.get('qgisId')
        permalink = record.get('permalink')
        pbf_options = record.get('pbfOptions')
        if (not isinstance(qgis_id, str) or not qgis_id
                or not isinstance(permalink, str) or not permalink.isdigit()
                or int(permalink) < 1
                or (record.get('dataHash') is not None
                    and not isinstance(record.get('dataHash'), str))
                or (record.get('pbfHash') is not None
                    and not isinstance(record.get('pbfHash'), str))
                or (record.get('outputKey') is not None
                    and not isinstance(record.get('outputKey'), str))
                or (pbf_options is not None
                    and pbf_options != 'layer-deleted'
                    and not isinstance(pbf_options, dict))
                or qgis_id in qgis_ids or permalink in permalinks):
            raise ValueError('The layer manifest contains an invalid layer record.')
        qgis_ids.add(qgis_id)
        permalinks.add(permalink)
        manifest['nextPermalink'] = max(
            manifest['nextPermalink'], int(permalink) + 1)
    if ('mapFormat' in manifest
            and manifest['mapFormat'] is not None
            and not isinstance(manifest['mapFormat'], str)):
        raise ValueError('The layer manifest has an invalid map format.')
    return manifest


def load_manifest(path):
    if not os.path.isfile(path):
        return empty_manifest()
    with open(path, 'r', encoding='utf-8') as stream:
        return parse_manifest(stream.read())


def normalize_manifest(manifest):
    if isinstance(manifest, str):
        return parse_manifest(manifest)
    if not isinstance(manifest, dict):
        raise ValueError('The layer manifest has an unsupported format.')
    payload = json.dumps(manifest, ensure_ascii=True, separators=(',', ':'))
    return parse_manifest(MANIFEST_PREFIX + payload + ';')


def write_manifest(path, manifest):
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    temporary_path = path + '.tmp'
    payload = json.dumps(manifest, ensure_ascii=True, separators=(',', ':'))
    try:
        with open(temporary_path, 'w', encoding='utf-8', newline='\n') as stream:
            stream.write(MANIFEST_PREFIX + payload + ';\n')
        os.replace(temporary_path, path)
    finally:
        if os.path.exists(temporary_path):
            os.remove(temporary_path)


def layer_data_hash(layer, options=None):
    """Hash vector features and every export option that affects their data."""
    digest = hashlib.sha256()
    fields = list(layer.fields())
    field_names = [field.name() for field in fields]
    editor_widgets = [
        (field.name(), layer.editorWidgetSetup(index).type())
        for index, field in enumerate(fields)
    ]
    renderer = layer.renderer()
    try:
        renderer_field = renderer.classAttribute() if renderer else ''
    except AttributeError:
        renderer_field = ''
    header = {
        'crs': layer.crs().authid(),
        'fields': [
            (field.name(), field.typeName(), field.length(), field.precision())
            for field in fields
        ],
        'editorWidgets': editor_widgets,
        'rendererField': renderer_field,
        'labelField': layer.customProperty('labeling/fieldName'),
        'geometryType': str(layer.wkbType()),
        'subsetString': layer.subsetString(),
        'options': options or {},
    }
    digest.update(json.dumps(
        header, sort_keys=True, ensure_ascii=True, default=str,
        separators=(',', ':')).encode('utf-8'))
    digest.update(b'\n')

    for feature in layer.getFeatures():
        geometry = feature.geometry()
        try:
            geometry_wkb = (bytes(geometry.asWkb())
                            if geometry is not None and not geometry.isNull()
                            else b'')
        except (AttributeError, TypeError, ValueError):
            geometry_wkb = b''
        attributes = [feature.attribute(name) for name in field_names]
        record = json.dumps(
            [feature.id(), attributes], sort_keys=True, ensure_ascii=True,
            default=str, separators=(',', ':')).encode('utf-8')
        for part in (record, geometry_wkb):
            digest.update(len(part).to_bytes(8, byteorder='big'))
            digest.update(part)
    return 'sha256:' + digest.hexdigest()


def raster_data_hash(layer, options=None):
    """Hash a local raster, its sidecars/VRT dependencies and rendering options."""
    source_uri = str(layer.source() or '')
    source_path = source_uri.split('|', 1)[0].strip('"')
    if (not source_path or '://' in source_path
            or not os.path.isabs(source_path)):
        return None

    source_path = os.path.abspath(source_path)
    files, pending = set(), [source_path]
    while pending:
        path = os.path.abspath(pending.pop())
        normalized = os.path.normcase(os.path.realpath(path))
        if normalized in files:
            continue
        if os.path.islink(path) or not os.path.isfile(path):
            return None
        files.add(normalized)

        root, extension = os.path.splitext(path)
        world_file = ('.' + extension[1] + extension[-1] + 'w'
                      if len(extension) >= 3 else '')
        sidecars = [path + '.aux.xml', path + '.ovr', root + '.wld',
                    root + '.prj']
        if world_file:
            sidecars.append(root + world_file)
        pending.extend(sidecar for sidecar in sidecars
                       if os.path.isfile(sidecar))

        if extension.lower() == '.vrt':
            try:
                with open(path, 'rb') as vrt_file:
                    vrt_document = xmltodict.parse(
                        vrt_file, disable_entities=True)
            except (ExpatError, OSError, ValueError):
                return None
            for source_filenames in _xml_elements(
                    vrt_document, 'SourceFilename'):
                if not isinstance(source_filenames, list):
                    source_filenames = [source_filenames]
                for source in source_filenames:
                    if isinstance(source, dict):
                        dependency = source.get('#text') or ''
                        relative_to_vrt = source.get('@relativeToVRT') == '1'
                    else:
                        dependency = source or ''
                        relative_to_vrt = False
                    dependency = dependency.strip()
                    if (not dependency or '://' in dependency
                            or dependency.startswith('/vsi')):
                        return None
                    if relative_to_vrt:
                        dependency = os.path.join(
                            os.path.dirname(path), dependency)
                    elif not os.path.isabs(dependency):
                        return None
                    pending.append(dependency)

    renderer = layer.renderer()
    header = {
        'sourceUri': source_uri,
        'renderer': renderer.dump() if renderer else '',
        'extent': layer.extent().toString(),
        'crs': layer.crs().authid(),
        'options': options or {},
    }
    digest = hashlib.sha256()
    digest.update(json.dumps(
        header, sort_keys=True, ensure_ascii=True, default=str,
        separators=(',', ':')).encode('utf-8'))
    digest.update(b'\n')
    for path in sorted(files):
        digest.update(path.encode('utf-8', errors='surrogatepass'))
        digest.update(b'\0')
        try:
            before = os.stat(path)
            with open(path, 'rb') as stream:
                while True:
                    chunk = stream.read(1024 * 1024)
                    if not chunk:
                        break
                    digest.update(chunk)
            after = os.stat(path)
        except OSError:
            return None
        if (before.st_size != after.st_size
                or before.st_mtime_ns != after.st_mtime_ns):
            return None
    return 'sha256:' + digest.hexdigest()


def pbf_options_hash(data_hash, pbf_options):
    payload = json.dumps(
        {'dataHash': data_hash, 'pbfOptions': pbf_options,
         'schema': PBF_CACHE_SCHEMA},
        sort_keys=True, ensure_ascii=True, default=str,
        separators=(',', ':')).encode('utf-8')
    return 'sha256:' + hashlib.sha256(payload).hexdigest()


def pbf_zoom_update_plan(previous_record, data_hash, pbf_options):
    """Return missing zoom ranges and retained overlap, or None if unsafe."""
    previous_options = previous_record.get('pbfOptions')
    if (not data_hash
            or previous_record.get('dataHash') != data_hash
            or not isinstance(previous_options, dict)
            or not isinstance(pbf_options, dict)
            or previous_options.get('schema') != PBF_CACHE_SCHEMA
            or pbf_options.get('schema') != PBF_CACHE_SCHEMA):
        return None

    previous_min = previous_options.get('zmin')
    previous_max = previous_options.get('zmax')
    current_min = pbf_options.get('zmin')
    current_max = pbf_options.get('zmax')
    if (isinstance(previous_min, bool) or not isinstance(previous_min, int)
            or isinstance(previous_max, bool) or not isinstance(previous_max, int)
            or isinstance(current_min, bool) or not isinstance(current_min, int)
            or isinstance(current_max, bool) or not isinstance(current_max, int)):
        return None
    if (previous_min < 0 or current_min < 0
            or previous_min > previous_max or current_min > current_max):
        return None

    previous_base = {key: value for key, value in previous_options.items()
                     if key not in ('zmin', 'zmax')}
    current_base = {key: value for key, value in pbf_options.items()
                    if key not in ('zmin', 'zmax')}
    if previous_base != current_base:
        return None

    export_ranges = []
    if current_min < previous_min:
        export_ranges.append(
            (current_min, min(current_max, previous_min - 1)))
    if current_max > previous_max:
        export_ranges.append(
            (max(current_min, previous_max + 1), current_max))
    retained_min = max(previous_min, current_min)
    retained_max = min(previous_max, current_max)
    retained_range = ((retained_min, retained_max)
                      if retained_min <= retained_max else None)
    return {'exportRanges': export_ranges, 'retainedRange': retained_range}


class LayerExportCache:
    """Track compatible previous layer data and files retained by an update."""

    def __init__(self, map_format, previous_manifest=None, previous_root=None,
                 remote_files=None):
        self.map_format = map_format
        self.previous_root = previous_root
        self.remote_files = remote_files if isinstance(remote_files, dict) else None
        self.remote_paths = {
            path.replace('\\', '/') for path in self.remote_files
        } if self.remote_files is not None else set()
        previous_manifest = previous_manifest or empty_manifest()
        if (previous_manifest.get('generator') != 'qgis2web'
                or previous_manifest.get('mapFormat') != map_format):
            previous_manifest = empty_manifest()
        self.previous_records = {
            record.get('qgisId'): record
            for record in previous_manifest.get('layers', [])
            if isinstance(record, dict) and record.get('qgisId')
        }
        next_permalink = previous_manifest.get('nextPermalink', 1)
        if (isinstance(next_permalink, bool)
                or not isinstance(next_permalink, int)
                or next_permalink < 1):
            next_permalink = 1
        self.next_permalink = max(
            [next_permalink] +
            [int(record['permalink']) + 1
             for record in self.previous_records.values()
             if isinstance(record.get('permalink'), str)
             and record['permalink'].isdigit()])
        self.records = []
        self.preserved_paths = set()

    def _file_available(self, relative_path):
        relative_path = relative_path.replace('\\', '/')
        if self.remote_files is not None:
            return relative_path in self.remote_paths
        if not self.previous_root:
            return False
        path = os.path.join(self.previous_root, *relative_path.split('/'))
        return os.path.isfile(path) and not os.path.islink(path)

    def _paths_under(self, relative_root):
        relative_root = relative_root.rstrip('/').replace('\\', '/')
        prefix = relative_root + '/'
        if self.remote_files is not None:
            return sorted(path for path in self.remote_paths
                          if path.startswith(prefix)
                          and path.lower().endswith('.pbf'))
        if not self.previous_root:
            return []
        root = os.path.join(self.previous_root, *relative_root.split('/'))
        paths = []
        if not os.path.isdir(root) or os.path.islink(root):
            return paths
        for current, dirs, names in os.walk(root):
            dirs[:] = [name for name in dirs
                       if not os.path.islink(os.path.join(current, name))]
            for name in names:
                path = os.path.join(current, name)
                if os.path.islink(path):
                    continue
                relative = os.path.relpath(path, self.previous_root).replace(
                    os.sep, '/')
                if relative.lower().endswith('.pbf'):
                    paths.append(relative)
        return sorted(paths)

    def inspect(self, layer, output_key, data_hash, data_path=None,
                pbf_options=None, pbf_root=None):
        qgis_id = str(layer.id())
        previous = self.previous_records.get(qgis_id, {})
        same_data = bool(
            data_hash and previous.get('dataHash') == data_hash
            and previous.get('outputKey') == output_key)
        available = not data_path or self._file_available(data_path)
        reuse_data = same_data and available
        if data_path and reuse_data:
            self.preserved_paths.add(data_path.replace('\\', '/'))

        pbf_ranges = None
        if pbf_options is not None:
            pbf_options = dict(pbf_options)
            pbf_ranges = [(pbf_options['zmin'], pbf_options['zmax'])]
            if same_data:
                plan = pbf_zoom_update_plan(previous, data_hash, pbf_options)
                old_paths = self._paths_under(pbf_root or '')
                if plan and old_paths:
                    retained_range = plan['retainedRange']
                    retained = []
                    if retained_range:
                        retained_min, retained_max = retained_range
                        prefix = (pbf_root or '').rstrip('/') + '/'
                        for path in old_paths:
                            relative = path[len(prefix):]
                            zoom = relative.split('/', 1)[0]
                            if (zoom.isdigit()
                                    and retained_min <= int(zoom) <= retained_max):
                                retained.append(path)
                    if not retained_range or retained:
                        pbf_ranges = plan['exportRanges']
                        self.preserved_paths.update(retained)

        permalink = previous.get('permalink')
        if not isinstance(permalink, str) or not permalink.isdigit():
            permalink = '{:03d}'.format(self.next_permalink)
            self.next_permalink += 1
        pbf_hash = (pbf_options_hash(data_hash, pbf_options)
                    if pbf_options is not None and data_hash else None)
        self.records.append({
            'qgisId': qgis_id,
            'permalink': permalink,
            'dataHash': data_hash,
            'pbfHash': pbf_hash,
            'pbfOptions': pbf_options,
            'outputKey': output_key,
        })
        return {'reuse_data': reuse_data and pbf_options is None,
                'pbf_ranges': pbf_ranges}

    def manifest(self, project_title=''):
        return {
            'version': 1,
            'generator': 'qgis2web',
            'mapFormat': self.map_format,
            'projectTitle': str(project_title or '').strip() or 'project',
            'nextPermalink': self.next_permalink,
            'layers': self.records,
        }
