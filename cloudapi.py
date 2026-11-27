# -*- coding: utf-8 -*-
"""Client for the O.GIS Cloud WordPress publishing API."""

import base64
import hashlib
import ipaddress
import json
import os
import re
import urllib.parse
import urllib.request
import urllib.error
import uuid

DEFAULT_SITE_URL = 'https://www.opengis.cloud'
DEV_SITE_SETTING = 'qgis2web/allowDevSite'
DEV_SITE_ENV_VAR = 'QGIS2WEB_DEV_SITE'
LEGACY_UPLOAD_FALLBACK_LIMIT = 32 * 1024 * 1024


class CloudError(Exception):
    def __init__(self, message, code='', status=0, payload=None):
        super(CloudError, self).__init__(message)
        self.message = message
        self.code = code
        self.status = status
        self.payload = payload or {}


def normalize_site_url(site_url):
    url = (site_url or '').strip()
    if not url:
        return DEFAULT_SITE_URL
    if '://' not in url:
        url = ('http://' if is_local_address(url) else 'https://') + url
    url = url.rstrip('/')
    official_host = re.match(r'^https?://(?:www\.)?opengis\.cloud(?=/|$)', url, re.I)
    if official_host:
        url = 'https://www.opengis.cloud' + url[official_host.end():]
    return url


def site_root_url(site_url):
    url = normalize_site_url(site_url)
    for suffix in ('/wp-json/ogis/v1', '/wp-json', '/ogis/v1'):
        if url.endswith(suffix):
            return url[:-len(suffix)] or DEFAULT_SITE_URL
    return url


def is_default_site(site_url):
    return site_root_url(site_url).lower() == DEFAULT_SITE_URL.rstrip('/').lower()


def is_local_address(site_url):
    try:
        parsed = urllib.parse.urlsplit(site_url if '://' in site_url else '//' + site_url)
        host = (parsed.hostname or '').lower().rstrip('.')
    except (TypeError, ValueError):
        return False
    if host == 'localhost' or host.endswith('.localhost') or host.endswith('.local'):
        return True
    try:
        return ipaddress.ip_address(host).is_private or ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def allow_dev_site():
    value = os.environ.get(DEV_SITE_ENV_VAR, '').strip().lower()
    if value in ('1', 'true', 'yes', 'on'):
        return True
    try:
        from qgis.core import QgsSettings
        value = QgsSettings().value(DEV_SITE_SETTING, False)
    except Exception:
        return False
    return value.strip().lower() in ('1', 'true', 'yes', 'on') if isinstance(value, str) else bool(value)


def ensure_allowed_site(site_url):
    normalized = normalize_site_url(site_url)
    try:
        parsed = urllib.parse.urlsplit(normalized)
        parsed.port
    except ValueError as error:
        raise CloudError(
            'Cloud site URL is invalid or contains an invalid port.',
            'invalid_site_url') from error
    if parsed.scheme.lower() not in ('http', 'https') or not parsed.hostname:
        raise CloudError(
            'Cloud site URLs must use HTTP or HTTPS and include a hostname.',
            'invalid_site_url')

    if not allow_dev_site() and not is_default_site(site_url):
        raise CloudError(
            'Publishing is locked to {}. To use a development site, explicitly enable '
            'the {} environment variable or the {} QGIS setting.'.format(
                DEFAULT_SITE_URL, DEV_SITE_ENV_VAR, DEV_SITE_SETTING),
            'site_locked')
    if parsed.scheme.lower() != 'https' and not is_local_address(normalized):
        raise CloudError('Cloud credentials may only be sent over HTTPS.', 'insecure_site')


def _root(url):
    url = normalize_site_url(url).rstrip('/')
    for suffix in ('/wp-json/ogis/v1', '/wp-json'):
        if url.endswith(suffix):
            url = url[:-len(suffix)]
    return url


def store_credentials(site_url, username, password):
    """Store secrets in QgsAuthManager; only the auth-config id goes in a project."""
    from qgis.core import QgsApplication, QgsAuthMethodConfig
    manager = QgsApplication.authManager()
    if manager is None:
        raise CloudError('QGIS authentication storage is unavailable.')
    if not manager.masterPasswordIsSet():
        manager.setMasterPassword()
    if not manager.masterPasswordIsSet():
        raise CloudError('Set a QGIS authentication database master password first.')
    config = QgsAuthMethodConfig()
    config.setMethod('Basic')
    config.setName('qgis2web Cloud - {}'.format(_root(site_url)))
    config.setConfig('username', username)
    config.setConfig('password', password)
    manager.storeAuthenticationConfig(config)
    if not config.id():
        raise CloudError('Could not save Cloud credentials in QGIS authentication storage.')
    return config.id()


def load_credentials(config_id):
    if not config_id:
        return '', ''
    try:
        from qgis.core import QgsApplication, QgsAuthMethodConfig
        config = QgsAuthMethodConfig()
        QgsApplication.authManager().loadAuthenticationConfig(config_id, config, True)
        if config.isValid():
            return config.config('username') or '', config.config('password') or ''
    except Exception:
        pass
    return '', ''


def remove_credentials(config_id):
    if config_id:
        try:
            from qgis.core import QgsApplication
            QgsApplication.authManager().removeAuthenticationConfig(config_id)
        except Exception:
            pass


class _HTTPRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers,
                         new_url):
        current = urllib.parse.urlsplit(request.full_url)
        destination = urllib.parse.urlsplit(new_url)
        if (destination.scheme.lower() != current.scheme.lower()
                or destination.hostname != current.hostname
                or destination.port != current.port):
            raise urllib.error.URLError(
                'Cloud API redirects must stay on the same HTTP(S) origin.')
        return super(_HTTPRedirectHandler, self).redirect_request(
            request, response, code, message, headers, new_url)


def _open_http_request(request, timeout):
    scheme = urllib.parse.urlsplit(request.full_url).scheme.lower()
    if scheme not in ('http', 'https'):
        raise urllib.error.URLError('Only HTTP and HTTPS requests are allowed.')

    opener = urllib.request.OpenerDirector()
    for handler in (
            urllib.request.ProxyHandler(),
            urllib.request.UnknownHandler(),
            urllib.request.HTTPHandler(),
            urllib.request.HTTPSHandler(),
            urllib.request.HTTPDefaultErrorHandler(),
            _HTTPRedirectHandler(),
            urllib.request.HTTPErrorProcessor()):
        opener.add_handler(handler)
    return opener.open(request, timeout=timeout)


class CloudClient:
    """Small client implementing the site's policy, manifest and ZIP upload API."""

    def __init__(self, site_url=DEFAULT_SITE_URL, username='', password=None, timeout=600):
        ensure_allowed_site(site_url)
        self.site_url = _root(normalize_site_url(site_url))
        self.username = username or ''
        self.password = password or ''
        self.timeout = timeout

    def request(self, method, path, params=None, body=None, content_type=None,
                progress=None):
        ensure_allowed_site(self.site_url)
        url = '{}/wp-json/ogis/v1/{}'.format(self.site_url, path.lstrip('/'))
        if params:
            url += '?' + urllib.parse.urlencode(params, doseq=True)
        raw = '{}:{}'.format(self.username, self.password).encode('utf-8')
        headers = {
            'Authorization': 'Basic ' + base64.b64encode(raw).decode('ascii'),
            'Accept': 'application/json',
            'User-Agent': 'qgis2web/5.0.0 (QGIS) publishing client',
        }
        if content_type:
            headers['Content-Type'] = content_type
        request = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            # Prefer QGIS' network stack so the configured QGIS proxy is respected.
            from qgis.core import QgsBlockingNetworkRequest
            from qgis.PyQt.QtCore import QByteArray, QUrl
            from qgis.PyQt.QtNetwork import QNetworkRequest
            qt_request = QNetworkRequest(QUrl(url))
            for key, value in headers.items():
                qt_request.setRawHeader(key.encode('utf-8'), value.encode('utf-8'))
            blocker = QgsBlockingNetworkRequest()
            if progress is not None:
                try:
                    blocker.uploadProgressChanged.connect(progress)
                except Exception:
                    pass
            if method == 'GET':
                code = blocker.get(qt_request)
            elif method == 'PUT':
                code = blocker.put(qt_request, QByteArray(body or b''))
            else:
                code = blocker.post(qt_request, QByteArray(body or b''))
            reply = blocker.reply()
            status = int(reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute) or 0)
            response = bytes(reply.content())
            if status == 0 and code:
                raise CloudError('Could not connect to {}.'.format(self.site_url),
                                 status=status)
        except ImportError:
            try:
                with _open_http_request(request, self.timeout) as response_obj:
                    status, response = response_obj.status, response_obj.read()
            except urllib.error.HTTPError as error:
                status, response = error.code, error.read()
            except Exception as error:
                raise CloudError('Could not connect to {}: {}'.format(self.site_url, error),
                                 status=0)
        except CloudError:
            raise
        except Exception as error:
            # Do not retry a possibly-sent publication request through another transport.
            raise CloudError('Could not connect to {}: {}'.format(self.site_url, error),
                             status=0)
        try:
            payload = json.loads(response.decode('utf-8')) if response else {}
        except (ValueError, UnicodeDecodeError) as error:
            if status < 400:
                raise CloudError(
                    'Cloud site returned an invalid response.',
                    code='invalid_response', status=status) from error
            payload = {}
        if not isinstance(payload, dict):
            if status < 400:
                raise CloudError(
                    'Cloud site returned an invalid response.',
                    code='invalid_response', status=status)
            payload = {}
        if status >= 400:
            message = payload.get('message', 'Cloud site returned HTTP {}.'.format(status))
            raise CloudError(message, payload.get('code', ''), status, payload)
        return payload

    def policy(self):
        return self.request('GET', 'policy')

    def ping(self):
        return self.request('GET', 'ping')

    def projects(self):
        response = self.request('GET', 'projects')
        return response.get('projects', [])

    def manifest(self, slug):
        return self.request('GET', 'projects/{}/manifest'.format(urllib.parse.quote(slug, safe='')))

    def account(self):
        return self.ping()

    def upload_zip(self, zip_path, mode='create', slug='', consents=(),
                   display_name='', base_revision=0, progress=None, delta=False,
                   expected_project_id=''):
        size = os.path.getsize(zip_path)
        if size < 1:
            raise CloudError('The export ZIP is empty.', 'empty_archive')
        archive_hash = hashlib.sha256()
        with open(zip_path, 'rb') as archive:
            for chunk in iter(lambda: archive.read(1024 * 1024), b''):
                archive_hash.update(chunk)
        archive_sha256 = archive_hash.hexdigest()
        params = {}
        if mode == 'create' and not consents:
            raise CloudError('Accept the required site confirmations before publishing.',
                             'consents_required')
        if consents:
            params['consent[]'] = list(consents)
        if display_name:
            params['display_name'] = display_name
        if base_revision:
            params['base_revision'] = base_revision
        if expected_project_id:
            params['expected_project_id'] = expected_project_id
        if delta:
            if mode != 'update':
                raise ValueError('Delta uploads are only valid for project updates.')
            params['delta'] = '1'
        if mode == 'update':
            path = 'projects/{}'.format(urllib.parse.quote(slug, safe=''))
            method = 'PUT'
        else:
            path, method = 'projects', 'POST'
        upload_progress = None
        if method == 'PUT' and delta and not base_revision:
            raise CloudError('The published project revision is missing; refresh the project list and retry.',
                             'missing_base_revision')
        session_params = dict(params)
        session_params.update({
            'mode': mode,
            'slug': slug,
            'archive_size': size,
            'archive_sha256': archive_sha256,
            'client_upload_id': str(uuid.uuid5(
                uuid.NAMESPACE_URL,
                '|'.join([self.site_url, mode, slug, str(base_revision),
                          str(expected_project_id or ''), archive_sha256]))),
        })
        fallback_to_legacy = False
        try:
            session = self.request('POST', 'uploads', params=session_params)
        except CloudError as error:
            if error.status == 404:
                fallback_to_legacy = True
                session = None
            elif error.status in (0, 408, 425) or error.status >= 500:
                session = self.request('POST', 'uploads', params=session_params)
            else:
                raise

        resume_processing = False
        if isinstance(session, dict) and session.get('recovery_available'):
            try:
                from qgis.PyQt.QtWidgets import QMessageBox
            except ImportError:
                raise CloudError(
                    'The server has an unfinished upload that can be recovered, but this '
                    'QGIS session cannot ask for confirmation. Open the Cloud export dialog '
                    'in QGIS to resume it.',
                    code='recovery_confirmation_required')
            if session.get('recovery_type') == 'processing':
                prompt = (
                    'A previous upload for "{}" stopped during {}. Resume processing '
                    'the exact archive already stored on the server? The current local '
                    'export will not be sent by this retry.'
                ).format(session.get('project_name') or slug or 'project',
                         session.get('phase') or 'processing')
            else:
                prompt = (
                    'The server has a complete extracted upload for "{}", but the original '
                    'ZIP is no longer available. Resume processing that saved server copy?'
                ).format(session.get('project_name') or slug or 'project')
            answer = QMessageBox.question(
                None, 'Recover interrupted upload', prompt,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)
            if answer != QMessageBox.StandardButton.Yes:
                raise CloudError('Recovery of the interrupted upload was cancelled.',
                                 code='recovery_cancelled')
            upload_id = str(session.get('upload_id') or '')
            if not upload_id:
                raise CloudError('The recoverable upload session is invalid.',
                                 code='invalid_upload_session')
            session = self.request('POST', 'uploads/{}/complete'.format(upload_id))
            resume_processing = bool(
                isinstance(session, dict) and session.get('processing'))

        if fallback_to_legacy:
            if size > LEGACY_UPLOAD_FALLBACK_LIMIT:
                raise CloudError(
                    'This server does not support resumable uploads. Update the '
                    'O.GIS publishing plugin before uploading archives larger than 32 MiB.',
                    code='chunked_upload_unsupported')
            with open(zip_path, 'rb') as archive:
                body = archive.read()
            if progress:
                progress(0, size)

                def report_upload(sent, total):
                    progress(sent, total or size)

                upload_progress = report_upload
            result = self.request(method, path, params, body, 'application/zip',
                                  progress=upload_progress)
            if progress:
                progress(size, size)
            return result

        if not isinstance(session, dict):
            raise CloudError('The server returned an invalid upload session.',
                             code='invalid_upload_session')
        if resume_processing:
            upload_id = str(session.get('upload_id') or '')
            payload = session
        else:
            upload_id = str(session.get('upload_id') or '')
            chunk_size = int(session.get('chunk_size') or 0)
            chunk_count = int(session.get('chunk_count') or 0)
            next_chunk = int(session.get('next_chunk') or 0)
            if (not upload_id or chunk_size < 1 or chunk_count < 1
                    or next_chunk < 0 or next_chunk > chunk_count):
                if upload_id:
                    try:
                        session = self.request('GET', 'uploads/{}'.format(upload_id))
                    except CloudError as error:
                        raise CloudError(
                            'The server returned an incomplete upload session and '
                            'its status could not be recovered: {}.'.format(error.message),
                            code='invalid_upload_session',
                            status=error.status, payload=error.payload)
                    chunk_size = int(session.get('chunk_size') or 0)
                    chunk_count = int(session.get('chunk_count') or 0)
                    next_chunk = int(session.get('next_chunk') or 0)
                if (not upload_id or chunk_size < 1 or chunk_count < 1
                        or next_chunk < 0 or next_chunk > chunk_count):
                    raise CloudError(
                        'The server returned an invalid upload session '
                        '(upload_id: {}; chunk_size: {}; chunk_count: {}; '
                        'next_chunk: {}).'.format(
                            'present' if upload_id else 'missing',
                            chunk_size, chunk_count, next_chunk),
                        code='invalid_upload_session')

            if progress:
                progress(min(size, next_chunk * chunk_size), size)
            with open(zip_path, 'rb') as archive:
                for index in range(next_chunk, chunk_count):
                    offset = index * chunk_size
                    archive.seek(offset)
                    expected_size = min(chunk_size, size - offset)
                    body = archive.read(expected_size)
                    if len(body) != expected_size:
                        raise CloudError(
                            'The archive changed while it was being uploaded.',
                            code='archive_changed')
                    chunk_path = 'uploads/{}/chunks/{}'.format(upload_id, index)
                    for attempt in range(2):
                        upload_progress = None
                        if progress:
                            def report_chunk(sent, total, _offset=offset,
                                             _size=len(body)):
                                progress(min(size, _offset + min(_size, sent)),
                                         size)

                            upload_progress = report_chunk
                        try:
                            self.request(
                                'PUT', chunk_path, body=body,
                                content_type='application/octet-stream',
                                progress=upload_progress)
                            break
                        except CloudError as error:
                            retryable = (
                                error.status in (0, 408, 425, 429)
                                or error.status >= 500)
                            if attempt != 0 or not retryable:
                                raise
                            state = self.request('GET', 'uploads/{}'.format(upload_id))
                            accepted = int(state.get('next_chunk') or 0)
                            if accepted > index:
                                break
                            if accepted != index:
                                raise
                    if progress:
                        progress(min(size, offset + len(body)), size)
            payload = self.request('POST', 'uploads/{}/complete'.format(upload_id))

        process_requests = 0
        while isinstance(payload, dict) and payload.get('processing'):
            process_requests += 1
            if process_requests > 50000:
                raise CloudError(
                    'The server did not finish processing this project. The upload '
                    'session is still available and can be resumed.',
                    code='upload_processing_stalled')
            try:
                payload = self.request(
                    'POST', 'uploads/{}/process'.format(upload_id))
            except CloudError as error:
                if not (error.status == 0 or error.status in (408, 425)
                        or error.status >= 500):
                    raise
                state = self.request('GET', 'uploads/{}'.format(upload_id))
                phase = str(state.get('phase') or '')
                if phase == 'failed':
                    raise CloudError(
                        state.get('error_message') or
                        'The server could not process the uploaded project.',
                        code=state.get('error_code') or 'processing_failed')
                if phase not in ('indexing', 'extracting', 'finalizing'):
                    raise
                payload = {'ok': True, 'processing': True, **state}
            if progress:
                progress(size, size)
        if progress:
            progress(size, size)
        return payload
