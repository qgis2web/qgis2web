# -*- coding: utf-8 -*-

# Copyright (C) 2017 Nyall Dawson (nyall.dawson@gmail.com)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import ftplib
import os
import shutil
from datetime import datetime

from qgis.core import QgsProject
from qgis.PyQt.QtCore import QObject, QCoreApplication, Qt
from qgis.PyQt.QtWidgets import (QApplication, QFileDialog, QInputDialog, QDialog,
                                 QDialogButtonBox, QLabel, QLineEdit,
                                 QMessageBox, QPlainTextEdit, QVBoxLayout)
from .utils import tempFolder
from .feedbackDialog import Feedback
from .folder_sync import (HISTORY_DIR, apply_sync, is_no_backup, plan_sync,
                          report_plan)
from .cloudapi import (DEFAULT_SITE_URL, CloudClient, CloudError,
                       ensure_allowed_site, load_credentials, remove_credentials,
                       store_credentials)
from .cloudzip import (ZipBuildError, build_project_zip, compare_with_manifest,
                       merge_preserved_remote_files)
from .layer_manifest import (MANIFEST_NAME, empty_manifest, load_manifest,
                            normalize_manifest)
from .ftp_transport import (FTP_AUTH_ANONYMOUS, FTP_AUTH_USER,
                            FTP_MODE_FTPS_EXPLICIT, FTP_MODE_FTPS_IMPLICIT,
                            FTP_MODE_PLAIN, FTPLoginCancelled,
                            default_port_for_mode, ensure_remote_directory,
                            open_ftp_connection, security_mode_label,
                            upload_directory)
from .ui_ftp_configuration import Ui_FtpConfiguration


def _human_size(num_bytes):
    """Format bytes for cloud-export feedback messages."""
    if num_bytes >= 1024 * 1024:
        return '{:.1f} MB'.format(num_bytes / (1024 * 1024))
    if num_bytes >= 1024:
        return '{:.0f} KB'.format(num_bytes / 1024)
    return '{:.0f} B'.format(num_bytes)


def _staging_parent():
    return os.path.join(tempFolder(), 'qgis2web_staging')


def _remove_staging(folder):
    root = os.path.abspath(_staging_parent())
    target = os.path.abspath(folder or '')
    try:
        if os.path.commonpath([root, target]) == root and target != root:
            shutil.rmtree(target, ignore_errors=True)
    except (ValueError, OSError):
        pass


def _is_temporary_export(path):
    """Avoid persisting plugin staging paths as a project's export destination."""
    try:
        root = os.path.abspath(tempFolder())
        target = os.path.abspath(path or '')
        return os.path.commonpath([root, target]) == root
    except (ValueError, OSError):
        return False


def _remove_empty_staging_parent():
    try:
        os.rmdir(_staging_parent())
    except OSError:
        pass


def _confirm_update(title, summary, detail_groups):
    details = []
    for entries, heading in detail_groups:
        if entries:
            if details:
                details.append('')
            details.append('{}:'.format(heading))
            details.extend('  {}'.format(path) for path in entries)

    confirmation = QDialog()
    confirmation.setWindowTitle(title)
    confirmation.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint,
                                False)
    confirmation.setSizeGripEnabled(True)
    layout = QVBoxLayout(confirmation)
    summary_label = QLabel(summary, confirmation)
    summary_label.setWordWrap(True)
    layout.addWidget(summary_label)

    details_view = QPlainTextEdit(confirmation)
    details_view.setReadOnly(True)
    details_view.setPlainText('\n'.join(details) or 'No file changes.')
    layout.addWidget(details_view, 1)

    buttons = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Yes |
        QDialogButtonBox.StandardButton.No,
        parent=confirmation)
    buttons.accepted.connect(confirmation.accept)
    buttons.rejected.connect(confirmation.reject)
    yes_button = buttons.button(QDialogButtonBox.StandardButton.Yes)
    if yes_button is not None:
        yes_button.setDefault(True)
    layout.addWidget(buttons)

    screen = QApplication.primaryScreen()
    if screen is not None:
        available = screen.availableGeometry()
        max_width = min(900, max(240, available.width() - 32))
        max_height = max(200, available.height() - 48)
        initial_height = min(
            max_height, min(720, max(360, int(available.height() * 0.72))))
        confirmation.setMinimumSize(min(520, max_width), min(360, max_height))
        confirmation.setMaximumSize(max_width, max_height)
        confirmation.resize(min(720, max_width), initial_height)
    answer = confirmation.exec() if hasattr(confirmation, 'exec') else confirmation.exec_()
    return answer == QDialog.DialogCode.Accepted


class Exporter(QObject):
    """Generic base class for web map exporters."""

    def __init__(self):
        super(QObject, self).__init__()

    @classmethod
    def type(cls):
        return ''

    @classmethod
    def name(cls):
        return ''

    def configure(self, parent_widget=None):
        pass

    def exportDirectory(self):
        return ''

    def postProcess(self, results, feedback=None):
        pass

    def prepareWriter(self, writer, feedback=None):
        return True

    def destinationUrl(self):
        return ''

    def writeToProject(self):
        pass

    def readFromProject(self):
        pass

    def newTempFolder(self, base):
        stamp = datetime.now().strftime('%Y_%m_%d-%H_%M_%S_%f')
        return os.path.join(base, 'qgis2web_' + stamp)


class FolderExporter(Exporter):
    """Exporter for writing a web map to a selected folder."""

    def __init__(self):
        super(Exporter, self).__init__()
        self.folder = tempFolder()
        self.export_file = None

    @classmethod
    def type(cls):
        return 'folder'

    @classmethod
    def name(cls):
        return QCoreApplication.translate('FolderExporter', 'Export to folder')

    def configure(self, parent_widget=None):
        start_folder = (self.folder if os.path.isdir(self.folder)
                        and not _is_temporary_export(self.folder) else '')
        new_folder = QFileDialog.getExistingDirectory(
            parent_widget, self.tr('Choose export folder'), start_folder,
            QFileDialog.Option.ShowDirsOnly)
        if new_folder:
            self.folder = new_folder
            return True
        return False

    def prepareWriter(self, writer, feedback=None):
        writer.layer_manifest_options = {'map_format': writer.type()}
        return True

    def exportDirectory(self):
        return self.folder

    def postProcess(self, results, feedback=None):
        feedback = feedback or Feedback()
        self.export_file = results.index_file
        feedback.setCompleted('Exported to {}'.format(self.folder))
        return True

    def destinationUrl(self):
        return self.export_file

    def writeToProject(self):
        if not _is_temporary_export(self.folder):
            QgsProject.instance().writeEntry('qgis2web', 'Exportfolder', self.folder)

    def readFromProject(self):
        folder, ok = QgsProject.instance().readEntry('qgis2web', 'Exportfolder')
        if ok and folder and not _is_temporary_export(folder):
            self.folder = folder


class FolderSyncExporter(Exporter):
    """Incrementally update a previously exported qgis2web project."""

    def __init__(self):
        super(Exporter, self).__init__()
        self.workspace = tempFolder()
        self.export_file = None
        self.staging = ''

    @classmethod
    def type(cls):
        return 'folder_sync'

    @classmethod
    def name(cls):
        return QCoreApplication.translate('FolderSyncExporter', 'Update existing export folder')

    def configure(self, parent_widget=None):
        folder = QFileDialog.getExistingDirectory(
            parent_widget, self.tr('Choose the existing qgis2web export to update'),
            self._suggest_update_folder(), QFileDialog.Option.ShowDirsOnly)
        if not folder:
            return False
        if not os.path.isfile(os.path.join(folder, 'index.html')):
            QMessageBox.warning(parent_widget, self.tr('Invalid export'),
                                self.tr('The selected folder must contain index.html.'))
            return False
        self.workspace = folder
        return True

    def prepareWriter(self, writer, feedback=None):
        manifest_path = os.path.join(
            self.workspace, 'layers', MANIFEST_NAME)
        try:
            previous_manifest = load_manifest(manifest_path)
        except (OSError, ValueError) as error:
            previous_manifest = empty_manifest()
            if feedback:
                feedback.showFeedback(
                    'The previous layer manifest cannot be reused; '
                    'exporting layer data again: {}'.format(error))
        writer.layer_manifest_options = {
            'map_format': writer.type(),
            'previous_manifest': previous_manifest,
            'previous_root': self.workspace,
        }
        return True

    def _suggest_update_folder(self):
        project = QgsProject.instance()
        candidates = []
        last_parent, ok = project.readEntry('qgis2web', 'LastUpdateParent')
        if ok and last_parent:
            candidates.append(last_parent)
        workspace, ok = project.readEntry('qgis2web', 'SyncWorkspace')
        if ok and workspace:
            candidates.append(os.path.dirname(os.path.normpath(workspace)))
        export_folder, ok = project.readEntry('qgis2web', 'Exportfolder')
        if ok and export_folder:
            candidates.append(export_folder)
        candidates.append(project.homePath())
        for candidate in candidates:
            if (candidate and os.path.isdir(candidate)
                    and not _is_temporary_export(candidate)):
                return candidate
        return self.workspace

    def exportDirectory(self):
        self.staging = self.newTempFolder(_staging_parent())
        os.makedirs(self.staging, exist_ok=True)
        return self.staging

    def postProcess(self, results, feedback=None):
        staging = results.folder
        try:
            plan = plan_sync(
                staging, self.workspace, getattr(results, 'preserved_files', ()))
            report_plan(plan, self.workspace)
            tiles = [path for path in plan['removed'] if is_no_backup(path)]
            summary = [
                'The existing export will be updated.', '',
                'Added: {}'.format(len(plan['added'])),
                'Updated: {}'.format(len(plan['updated'])),
                'Unchanged: {}'.format(len(plan['unchanged'])),
                'Removed generated files: {}'.format(
                    len(plan['removed']) - len(tiles)),
                'Preserved custom/unknown files: {}'.format(len(plan['preserved'])),
            ]
            if tiles:
                summary.append('Removed vector tiles (no backup): {}'.format(len(tiles)))
            summary.extend([
                '',
                'Review the file lists below.',
                '',
                'The custom_code folder is never checked or modified by an update.',
                'Changed and removed files are backed up under {}/<timestamp>.'.format(
                    HISTORY_DIR),
            ])
            if tiles:
                summary.append(
                    'Vector tiles are deleted without a backup and rebuilt from source data.')
            confirmed = _confirm_update(
                self.tr('Confirm local update'), '\n'.join(summary),
                ((plan['added'], 'New files'),
                 (plan['updated'], 'Changed files'),
                 (plan['removed'], 'Removed generated files'),
                 (plan['preserved'], 'Preserved custom/unknown files')))
            if not confirmed:
                if feedback:
                    feedback.setFatalError('Update cancelled by user')
                return False
            history = apply_sync(staging, self.workspace, plan)
            self.export_file = os.path.join(self.workspace, 'index.html')
            if feedback:
                feedback.setCompleted('Local export updated. History: {}'.format(
                    history or 'not needed'))
            return True
        except (OSError, ValueError) as error:
            if feedback:
                feedback.setFatalError('Could not update the local export: {}'.format(error))
            return False
        finally:
            _remove_staging(staging)
            _remove_empty_staging_parent()

    def destinationUrl(self):
        return self.export_file

    def writeToProject(self):
        if self.workspace and not _is_temporary_export(self.workspace):
            QgsProject.instance().writeEntry('qgis2web', 'SyncWorkspace', self.workspace)
            QgsProject.instance().writeEntry(
                'qgis2web', 'LastUpdateParent',
                os.path.dirname(os.path.normpath(self.workspace)))

    def readFromProject(self):
        folder, ok = QgsProject.instance().readEntry('qgis2web', 'SyncWorkspace')
        if ok and folder and not _is_temporary_export(folder):
            self.workspace = folder


class FtpConfigurationDialog(QDialog, Ui_FtpConfiguration):
    """Dialog for configuring FTP and FTPS connection details."""

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.securityComboBox.addItem(
            self.tr('FTPS - explicit TLS (recommended)'),
            FTP_MODE_FTPS_EXPLICIT)
        self.securityComboBox.addItem(
            self.tr('FTPS - implicit TLS'),
            FTP_MODE_FTPS_IMPLICIT)
        self.securityComboBox.addItem(
            self.tr('FTP - no encryption (insecure)'),
            FTP_MODE_PLAIN)
        self.authenticationComboBox.addItem(
            self.tr('Username and password'),
            FTP_AUTH_USER)
        self.authenticationComboBox.addItem(
            self.tr('Anonymous (public FTP)'),
            FTP_AUTH_ANONYMOUS)
        self._port_is_custom = False
        self.securityComboBox.currentIndexChanged.connect(
            self._security_mode_changed)
        self.authenticationComboBox.currentIndexChanged.connect(
            self._authentication_mode_changed)
        self.portSpinBox.valueChanged.connect(self._port_changed)
        self._update_security_description()
        self._update_authentication_description()

    def setHost(self, host):
        self.hostLineEdit.setText(host)

    def setPort(self, port):
        try:
            value = int(port)
        except (TypeError, ValueError):
            value = default_port_for_mode(self.securityMode())
        if not 1 <= value <= 65535:
            value = default_port_for_mode(self.securityMode())
        self.portSpinBox.blockSignals(True)
        self.portSpinBox.setValue(value)
        self.portSpinBox.blockSignals(False)
        self._port_is_custom = (
            self.portSpinBox.value() !=
            default_port_for_mode(self.securityMode()))
        self._update_port_description()

    def setUsername(self, username):
        self.usernameLineEdit.setText(username)

    def setFolder(self, folder):
        self.folderLineEdit.setText(folder)

    def setSecurityMode(self, security_mode):
        index = self.securityComboBox.findData(security_mode)
        if index < 0:
            index = self.securityComboBox.findData(FTP_MODE_FTPS_EXPLICIT)
        self.securityComboBox.setCurrentIndex(index)

    def setAuthenticationMode(self, authentication_mode):
        index = self.authenticationComboBox.findData(authentication_mode)
        if index < 0:
            index = self.authenticationComboBox.findData(FTP_AUTH_USER)
        self.authenticationComboBox.setCurrentIndex(index)

    def host(self):
        return self.hostLineEdit.text().strip()

    def username(self):
        return self.usernameLineEdit.text().strip()

    def folder(self):
        return self.folderLineEdit.text()

    def port(self):
        return self.portSpinBox.value()

    def securityMode(self):
        return self.securityComboBox.currentData()

    def authenticationMode(self):
        return self.authenticationComboBox.currentData()

    def _security_mode_changed(self):
        if not self._port_is_custom:
            self.setPort(default_port_for_mode(self.securityMode()))
        self._update_security_description()
        self._update_port_description()

    def _authentication_mode_changed(self):
        use_account = self.authenticationMode() == FTP_AUTH_USER
        self.usernameLabel.setEnabled(use_account)
        self.usernameLineEdit.setEnabled(use_account)
        self._update_authentication_description()

    def _port_changed(self, value):
        self._port_is_custom = (
            value != default_port_for_mode(self.securityMode()))
        self._update_port_description()

    def _update_security_description(self):
        descriptions = {
            FTP_MODE_FTPS_EXPLICIT: self.tr(
                'TLS is required before login and for uploaded files. '
                'Usually uses port 21. Recommended for most servers.'),
            FTP_MODE_FTPS_IMPLICIT: self.tr(
                'TLS starts immediately when connecting. Usually uses port 990. '
                'Choose this only if your hosting provider specifies implicit FTPS.'),
            FTP_MODE_PLAIN: self.tr(
                'No encryption: your username, password and map files can be read '
                'in transit. Use only if your server requires plain FTP.'),
        }
        self.securityDescriptionLabel.setText(
            descriptions[self.securityMode()])

    def _update_authentication_description(self):
        descriptions = {
            FTP_AUTH_USER: self.tr(
                'The password is requested only if the server needs it and is '
                'never saved in the QGIS project. A blank password is allowed '
                'if the server accepts it.'),
            FTP_AUTH_ANONYMOUS: self.tr(
                'Connect as the public anonymous user. If the server asks for a '
                'password, you can enter an email or leave it blank.'),
        }
        self.authenticationDescriptionLabel.setText(
            descriptions[self.authenticationMode()])

    def _update_port_description(self):
        default_port = default_port_for_mode(self.securityMode())
        self.portHelpLabel.setText(self.tr(
            'Default for this connection type: {}. Change only if your provider '
            'specifies a custom port.').format(default_port))

    def accept(self):
        if not self.host():
            QMessageBox.warning(
                self, self.tr('Server required'),
                self.tr('Enter the FTP/FTPS server hostname.'))
            self.hostLineEdit.setFocus()
            return
        if (self.authenticationMode() == FTP_AUTH_USER and
                not self.username()):
            QMessageBox.warning(
                self, self.tr('Username required'),
                self.tr('Enter the FTP account username, or choose anonymous access.'))
            self.usernameLineEdit.setFocus()
            return
        QDialog.accept(self)

class FtpExporter(Exporter):
    """Exporter for uploading a web map to an FTP or FTPS site."""

    def __init__(self):
        super(Exporter, self).__init__()
        self.host = ''
        self.username = ''
        self.remote_folder = 'public_html/'
        self.security_mode = FTP_MODE_FTPS_EXPLICIT
        self.authentication_mode = FTP_AUTH_USER
        self.port = default_port_for_mode(self.security_mode)
        self.export_file = None
        self.temp_folder = self.newTempFolder(_staging_parent())

    @classmethod
    def type(cls):
        return 'ftp'

    @classmethod
    def name(cls):
        return QCoreApplication.translate(
            'FtpExporter', 'Export to FTP / FTPS site')

    def configure(self, parent_widget=None):
        dialog = FtpConfigurationDialog(parent_widget)
        dialog.setHost(self.host)
        dialog.setSecurityMode(self.security_mode)
        dialog.setAuthenticationMode(self.authentication_mode)
        dialog.setUsername(self.username)
        dialog.setPort(self.port)
        dialog.setFolder(self.remote_folder)
        accepted = dialog.exec() if hasattr(dialog, 'exec') else dialog.exec_()
        if not accepted:
            return False
        self.host = dialog.host()
        self.security_mode = dialog.securityMode()
        self.authentication_mode = dialog.authenticationMode()
        self.username = dialog.username()
        self.port = dialog.port()
        self.remote_folder = dialog.folder()
        return True

    def exportDirectory(self):
        return self.temp_folder

    def postProcess(self, results, feedback=None):
        feedback = feedback or Feedback()
        self.export_file = ''
        file_count = max(len(results.files), 1)
        source_folder = results.folder
        ftp = None
        try:
            if not self.host.strip() or not 1 <= int(self.port) <= 65535:
                raise ValueError('Enter a valid FTP/FTPS server and port.')
            if (self.authentication_mode == FTP_AUTH_USER and
                    not self.username.strip()):
                raise ValueError('Enter the FTP account username.')
            feedback.showFeedback(
                'Connecting to {}:{} using {}...'.format(
                    self.host, self.port,
                    security_mode_label(self.security_mode)))

            def request_password():
                if feedback.cancelled():
                    return None
                if self.authentication_mode == FTP_AUTH_ANONYMOUS:
                    title = 'Anonymous FTP login'
                    label = 'Optional password or email:'
                    default_password = 'anonymous@'
                else:
                    title = 'FTP account password'
                    label = 'Password for {} (leave blank only if allowed):'.format(
                        self.username)
                    default_password = ''
                password, accepted = QInputDialog.getText(
                    None, title, label, QLineEdit.EchoMode.Password,
                    default_password)
                return password if accepted else None

            ftp = open_ftp_connection(
                self.host, self.port, self.security_mode,
                self.authentication_mode, self.username, request_password)
            if feedback.cancelled():
                feedback.setFatalError('Upload cancelled by user.')
                return False

            ensure_remote_directory(ftp, self.remote_folder)
            if not upload_directory(
                    ftp, source_folder, feedback, file_count):
                feedback.setFatalError('Upload cancelled by user.')
                return False

            ftp.quit()
            ftp = None
            feedback.setCompleted('Upload complete!')
            return True
        except FTPLoginCancelled:
            feedback.setFatalError('Upload cancelled by user.')
            return False
        except (ftplib.Error, OSError, EOFError, ValueError) as error:
            feedback.setFatalError(
                'FTP/FTPS upload failed: {}'.format(error))
            return False
        finally:
            if ftp is not None:
                ftp.close()
            _remove_staging(source_folder)
            _remove_empty_staging_parent()

    def destinationUrl(self):
        return ''

    def writeToProject(self):
        project = QgsProject.instance()
        project.writeEntry('qgis2web', 'FtpHost', self.host)
        project.writeEntry('qgis2web', 'FtpUser', self.username)
        project.writeEntry('qgis2web', 'FtpFolder', self.remote_folder)
        project.writeEntry('qgis2web', 'FtpPort', self.port)
        project.writeEntry(
            'qgis2web', 'FtpSecurityMode', self.security_mode)
        project.writeEntry(
            'qgis2web', 'FtpAuthenticationMode',
            self.authentication_mode)

    def readFromProject(self):
        project = QgsProject.instance()
        self.host = project.readEntry('qgis2web', 'FtpHost')[0] or self.host
        self.username = project.readEntry('qgis2web', 'FtpUser')[0] or self.username
        self.remote_folder = project.readEntry('qgis2web', 'FtpFolder')[0] or self.remote_folder
        saved_security_mode, has_security_mode = project.readEntry(
            'qgis2web', 'FtpSecurityMode')
        valid_security_modes = (
            FTP_MODE_FTPS_EXPLICIT, FTP_MODE_FTPS_IMPLICIT, FTP_MODE_PLAIN)
        if saved_security_mode in valid_security_modes:
            self.security_mode = saved_security_mode
        else:
            self.security_mode = FTP_MODE_FTPS_EXPLICIT
            has_security_mode = False

        saved_authentication_mode, _ = project.readEntry(
            'qgis2web', 'FtpAuthenticationMode')
        if saved_authentication_mode in (FTP_AUTH_USER, FTP_AUTH_ANONYMOUS):
            self.authentication_mode = saved_authentication_mode
        else:
            self.authentication_mode = FTP_AUTH_USER

        saved_port, has_port = project.readNumEntry(
            'qgis2web', 'FtpPort')
        if has_port and saved_port > 0:
            if not has_security_mode and saved_port == 22:
                saved_port = default_port_for_mode(self.security_mode)
            self.port = saved_port
        else:
            self.port = default_port_for_mode(self.security_mode)


class CloudPublishExporter(Exporter):
    """Base exporter for publishing qgis2web maps to O.GIS Cloud."""

    mode = 'create'

    def __init__(self):
        super(CloudPublishExporter, self).__init__()
        self.site_url = DEFAULT_SITE_URL
        self.username = self.password = self.authcfg_id = ''
        self.slug = self.display_name = self.target_slug = ''
        self.project_id = self.target_project_id = ''
        self.selected_project_id = None
        self.policy, self.consents = {}, []
        self.staging = self.export_file = None
        self.remember_credentials = True
        self._preflight_manifest = None
        self._preflight_revision = None
        self._preflight_project_id = ''
        self._layer_cache_enabled = False

    @classmethod
    def type(cls):
        return 'cloud' if cls.mode == 'create' else 'cloud_sync'

    @classmethod
    def name(cls):
        return QCoreApplication.translate(
            'CloudExporter',
            'Cloud Export (O.GIS)' if cls.mode == 'create' else 'Cloud Update (O.GIS)')

    def readFromProject(self):
        project = QgsProject.instance()
        remember, ok = project.readEntry('qgis2web', 'CloudRememberCredentials')
        if ok:
            self.remember_credentials = remember.strip().lower() not in (
                'false', '0', 'no', 'off')
        self.site_url = project.readEntry('qgis2web', 'CloudSiteUrl')[0] or DEFAULT_SITE_URL
        self.username = project.readEntry('qgis2web', 'CloudUser')[0] or ''
        self.authcfg_id = project.readEntry('qgis2web', 'CloudAuthConfigId')[0] or ''
        self.slug = project.readEntry('qgis2web', 'CloudProjectSlug')[0] or ''
        self.target_slug = project.readEntry('qgis2web', 'CloudUpdateSlug')[0] or self.slug
        self.project_id = project.readEntry('qgis2web', 'CloudProjectId')[0] or ''
        self.target_project_id = project.readEntry(
            'qgis2web', 'CloudUpdateProjectId')[0] or (
                self.project_id if self.target_slug == self.slug else '')
        self.display_name = project.readEntry('qgis2web', 'CloudDisplayName')[0] or ''

    def prepareWriter(self, writer, feedback=None):
        writer.layer_manifest_options = {'map_format': writer.type()}
        self._layer_cache_enabled = False
        self._preflight_manifest = None
        self._preflight_revision = None
        self._preflight_project_id = ''
        if self.mode != 'update':
            return True
        try:
            client = self.client()
            if not self.policy:
                self.policy = client.policy()
            slug = self.target_slug or self.slug
            manifest = client.manifest(slug)
            remote_project_id = str(manifest.get('project_id') or '')
            expected_project_id = (
                self.selected_project_id
                if self.selected_project_id is not None
                else self.target_project_id)
            if expected_project_id and remote_project_id != expected_project_id:
                raise CloudError(
                    'The selected remote project is no longer the project linked to this QGIS file. Reload the project list and confirm the update again.',
                    code='project_id_conflict')

            revision = int(manifest.get('revision') or 0)
            self._preflight_manifest = manifest
            self._preflight_revision = revision
            self._preflight_project_id = remote_project_id
            features = self.policy.get('features') or {}
            layer_manifest = manifest.get('layer_manifest')
            remote_files = manifest.get('files')
            try:
                layer_manifest = normalize_manifest(layer_manifest)
            except ValueError as error:
                layer_manifest = None
                if feedback:
                    feedback.showFeedback(
                        'The remote layer manifest cannot be reused; '
                        'exporting layer data again: {}'.format(error))
            if (features.get('delta_updates')
                    and features.get('project_identity')
                    and remote_project_id
                    and expected_project_id == remote_project_id
                    and revision > 0
                    and isinstance(layer_manifest, dict)
                    and layer_manifest.get('generator') == 'qgis2web'
                    and layer_manifest.get('mapFormat') == writer.type()
                    and isinstance(remote_files, dict)):
                writer.layer_manifest_options = {
                    'map_format': writer.type(),
                    'previous_manifest': layer_manifest,
                    'remote_files': remote_files,
                }
                self._layer_cache_enabled = True
            return True
        except CloudError as error:
            if feedback:
                feedback.setFatalError(error.message)
            return False
        except (TypeError, ValueError) as error:
            if feedback:
                feedback.setFatalError(
                    'The remote project manifest is invalid: {}'.format(error))
            return False

    def configure(self, parent_widget=None):
        from .clouddialog import CloudPublishDialog

        try:
            ensure_allowed_site(self.site_url)
        except CloudError as error:
            QMessageBox.warning(parent_widget, self.name(), error.message)
            return False
        user, password = self.username, self.password
        if not password and self.authcfg_id:
            saved_user, password = load_credentials(self.authcfg_id)
            user = user or saved_user
        dialog = CloudPublishDialog(parent_widget, self.mode, {
            'site_url': self.site_url,
            'username': user,
            'password': password,
            'remember': self.remember_credentials,
            'slug': self.slug,
            'display_name': self.display_name,
            'target_slug': self.target_slug,
            'target_project_id': self.target_project_id,
        })
        accepted = dialog.exec() if hasattr(dialog, 'exec') else dialog.exec_()
        if not accepted:
            return False

        old_auth = self.authcfg_id
        self.site_url = dialog.site_url
        self.username = dialog.username
        self.password = dialog.password
        self.slug = dialog.slug
        self.display_name = dialog.display_name
        self.target_slug = dialog.target_slug
        self.selected_project_id = dialog.target_project_id
        self.policy = dict(dialog.policy or {})
        self.consents = list(dialog.consents)
        self.remember_credentials = dialog.remember
        if self.remember_credentials:
            try:
                self.authcfg_id = store_credentials(
                    self.site_url, self.username, self.password)
            except CloudError as error:
                self.authcfg_id = ''
                QMessageBox.warning(
                    parent_widget, self.name(),
                    '{}\n\nThe credentials will be asked again at every publish.'.format(
                        error.message))
        else:
            self.authcfg_id = ''
        if old_auth and old_auth != self.authcfg_id:
            remove_credentials(old_auth)
        if self.remember_credentials and self.authcfg_id:
            self.password = ''
        return True

    def client(self):
        ensure_allowed_site(self.site_url)
        if not self.username or not self.password:
            if self.authcfg_id:
                self.username, self.password = load_credentials(self.authcfg_id)
        if not self.username or not self.password:
            raise CloudError(
                'Enter the Cloud account credentials before publishing.',
                'missing_credentials')
        return CloudClient(self.site_url, self.username, self.password)

    def exportDirectory(self):
        self.staging = self.newTempFolder(_staging_parent())
        os.makedirs(self.staging, exist_ok=True)
        return self.staging

    def opensMapLocally(self):
        return False

    def postProcess(self, results, feedback=None):
        feedback = feedback or Feedback()
        staging = results.folder
        slug = self.target_slug if self.mode == 'update' else self.slug
        zip_path = None
        try:
            client = self.client()
            if not self.policy:
                self.policy = client.policy()
            if not self.consents:
                self.consents = self._ask_consents(client, feedback)
                if self.consents is None:
                    return False
            zip_path = os.path.join(
                _staging_parent(), 'qgis2web-{}.zip'.format(slug or 'project'))

            def zip_progress(done, total):
                feedback.showFeedback(
                    '{}: {} of {} files'.format(
                        'Validating the export' if self.mode == 'update'
                        else 'Building the archive of the export', done, total))

            built = build_project_zip(staging, zip_path, slug, self.policy,
                                      progress=zip_progress,
                                      create_archive=self.mode != 'update')
            built.preserved_paths = list(
                getattr(results, 'preserved_files', ()))
            if self.mode == 'update':
                feedback.showFeedback(
                    'Comparing the export with the remote project...')
            else:
                feedback.showFeedback(
                    'Sending {} files (uncompressed export: {}, ZIP: {}) to {}...'.format(
                        len(built), _human_size(built.uncompressed_bytes),
                        _human_size(built.archive_bytes), self.site_url))
            response = self._publish(client, built, feedback, staging)
            if response is None:
                feedback.setFatalError('Publication cancelled by user')
                return False
            self.export_file = response.get('url') or ''
            self.consents = []
            remote_project_id = str(response.get('project_id') or '')
            if remote_project_id:
                self.project_id = remote_project_id
                self.target_project_id = remote_project_id
                self.target_slug = response.get('slug') or built.slug
                self.slug = built.slug
                self.writeToProject()
            if response.get('up_to_date'):
                feedback.setCompleted(
                    'Nothing to publish: the project on {} already contains exactly these '
                    'files (revision {}). {}'.format(
                        self.site_url, response.get('revision', 0), self.export_file))
                return True

            self.target_slug = built.slug
            self.slug = built.slug
            self.project_id = str(response.get('project_id') or self.project_id)
            self.target_project_id = str(response.get('project_id') or
                                         self.target_project_id)
            project = QgsProject.instance()
            project.writeEntry('qgis2web', 'CloudSiteUrl', self.site_url)
            project.writeEntry('qgis2web', 'CloudUser', self.username)
            project.writeEntry('qgis2web', 'CloudAuthConfigId', self.authcfg_id)
            project.writeEntry('qgis2web', 'CloudProjectSlug', built.slug)
            project.writeEntry('qgis2web', 'CloudUpdateSlug', built.slug)
            project.writeEntry('qgis2web', 'CloudProjectId', self.project_id)
            project.writeEntry('qgis2web', 'CloudUpdateProjectId',
                               self.target_project_id)
            project.writeEntry('qgis2web', 'CloudDisplayName', self.display_name)
            project.writeEntry('qgis2web', 'CloudRememberCredentials',
                               self.remember_credentials)
            applied = response.get('applied') or {}
            feedback.setCompleted(
                'Published {} (revision {}; {} added, {} updated, {} removed).'.format(
                    self.export_file or built.slug, response.get('revision', 1),
                    applied.get('added', len(built)), applied.get('updated', 0),
                    applied.get('removed', 0)))
            return True
        except CloudError as error:
            feedback.setFatalError(error.message)
            return False
        except ZipBuildError as error:
            message = error.message
            if error.details:
                message = '{}\n\n{}'.format(message, '\n'.join(error.details[:20]))
            feedback.setFatalError(message)
            return False
        except (OSError, ValueError) as error:
            feedback.setFatalError(str(error))
            return False
        finally:
            _remove_staging(staging)
            if zip_path and os.path.isfile(zip_path):
                try:
                    os.remove(zip_path)
                except OSError:
                    pass
            _remove_empty_staging_parent()

    def _ask_consents(self, client, feedback):
        try:
            account = client.ping()
        except CloudError as error:
            feedback.setFatalError(error.message)
            return None
        required = [consent for consent in (account.get('consents') or [])
                    if consent.get('required')]
        if not required:
            return []
        text = '\n'.join('\u2022 {}'.format(consent.get('label', ''))
                         for consent in required)
        answer = QMessageBox.question(
            None, self.tr('Confirmations required by the site'),
            self.tr('The site requires these confirmations before publishing:\n\n{}'
                    '\n\nAccept and publish?').format(text),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes)
        if answer != QMessageBox.StandardButton.Yes:
            return None
        return [consent.get('key') for consent in required]

    def _upload_progress(self, feedback):
        def report(sent, total):
            if total:
                feedback.setProgress(int(100.0 * sent / total))
        return report

    def _publish(self, client, built, feedback, staging):
        if self.mode == 'update':
            return self._publish_update(client, built, feedback, staging)
        try:
            return client.upload_zip(
                built.path, mode='create', consents=self.consents,
                display_name=self.display_name,
                progress=self._upload_progress(feedback))
        except CloudError as error:
            if error.code != 'project_exists':
                raise

        answer = QMessageBox.question(
            None, self.tr('Project already on the site'),
            self.tr('A project named "{}" is already published on {}.\n\nReplace it '
                    'with this export (update it) instead of uploading a copy?').format(
                built.slug, self.site_url),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes)
        if answer != QMessageBox.StandardButton.Yes:
            return None
        return self._publish_update(client, built, feedback, staging)

    def _publish_update(self, client, built, feedback, staging):
        manifest = client.manifest(built.slug)
        remote_project_id = str(manifest.get('project_id') or '')
        expected_project_id = (self.selected_project_id
                       if self.selected_project_id is not None
                       else self.target_project_id)
        if expected_project_id and remote_project_id != expected_project_id:
            raise CloudError(
                'The selected remote project is no longer the project linked to this QGIS file. Reload the project list and confirm the update again.',
                code='project_id_conflict')
        revision = int(manifest.get('revision') or 0)
        if (self._layer_cache_enabled
                and (remote_project_id != self._preflight_project_id
                     or revision != self._preflight_revision)):
            raise CloudError(
                'The remote project changed while the local data was being prepared. '
                'Retry the update to compare against the latest revision.',
                code='revision_conflict')
        if not self.target_project_id and remote_project_id:
            answer = QMessageBox.question(
                None, self.tr('Confirm remote project'),
                self.tr('This QGIS project is not yet linked to a remote project identity. Link it to "{}" ({}) and continue?').format(
                    manifest.get('display_name') or built.slug, built.slug),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)
            if answer != QMessageBox.StandardButton.Yes:
                return None
        remote_files = manifest.get('files') or {}
        preserved_paths = list(getattr(built, 'preserved_paths', ()))
        built.preserved_paths = preserved_paths
        built.files = merge_preserved_remote_files(
            built.files, preserved_paths, remote_files)
        diff = compare_with_manifest(built.files, remote_files)
        if not diff['added'] and not diff['updated'] and not diff['removed']:
            answer = QMessageBox.question(
                None, self.tr('Nothing to publish'),
                self.tr('The published revision {} of "{}" contains exactly the same {} '
                        'files as this export.\n\nPublish it again anyway (the revision '
                        'number increases, no file changes)?').format(
                    manifest.get('revision', 0), built.slug, diff['unchanged']),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)
            if answer != QMessageBox.StandardButton.Yes:
                return {'ok': True, 'up_to_date': True, 'slug': built.slug,
                        'revision': int(manifest.get('revision') or 0),
                    'url': manifest.get('url') or self.export_file or '',
                    'project_id': remote_project_id}

        summary = [
            'The published project "{}" will be replaced.'.format(built.slug), '',
            'Added: {}'.format(len(diff['added'])),
            'Updated: {}'.format(len(diff['updated'])),
            'Unchanged: {}'.format(diff['unchanged']),
            'Removed from the site: {}'.format(len(diff['removed'])), '',
            'Review the file lists below.', '',
            'The previous files are kept in the history of the project on the site, '
            'while the password protection, the CORS settings and the branding banner '
            'stay as they are.', '',
            'Revision on the site: {} -> {}'.format(
                manifest.get('revision', 0), int(manifest.get('revision', 0)) + 1),
        ]
        confirmed = _confirm_update(
            self.tr('Confirm the update of the published project'),
            '\n'.join(summary),
            ((diff['added'], 'New files'),
             (diff['updated'], 'Changed files'),
             (diff['removed'], 'Files removed from the site')))
        if not confirmed:
            return None
        features = self.policy.get('features') or {}
        use_delta = bool(features.get('delta_updates')
                 and features.get('project_identity')
                 and remote_project_id and revision > 0
                         and remote_project_id == expected_project_id)
        if preserved_paths and not use_delta:
            raise CloudError(
                'This update reused files stored on the site, but the site no longer '
                'supports incremental updates. Retry after refreshing the Cloud settings.',
                code='incremental_update_unavailable')
        sent_full_fallback = False
        if use_delta:
            try:
                built = build_project_zip(
                    staging, built.path, built.slug, self.policy,
                    include_paths=diff['added'] + diff['updated'],
                    removed_paths=diff['removed'])
            except ZipBuildError as error:
                if (preserved_paths
                        or 'ZIP-entry limit' not in error.message):
                    raise
                built = build_project_zip(
                    staging, built.path, built.slug, self.policy)
                use_delta = False
                sent_full_fallback = True
        if not use_delta:
            if preserved_paths:
                raise CloudError(
                    'A complete Cloud update cannot be built from remote-only '
                    'preserved files. Retry with incremental updates enabled.',
                    code='incomplete_full_archive')
            if not sent_full_fallback:
                built = build_project_zip(
                    staging, built.path, built.slug, self.policy)
            feedback.showFeedback(
                ('The delta archive exceeded the entry limit; sending the complete '
                 'local export. ' if sent_full_fallback else '') +
                'Sending full export ({} files, {}, ZIP {}) to {}...'.format(
                    len(built), _human_size(built.uncompressed_bytes),
                    _human_size(built.archive_bytes), self.site_url))
        else:
            feedback.showFeedback(
                'Sending {} changed files (uncompressed delta: {}, ZIP: {}) to {}...'.format(
                    len(built), _human_size(built.uncompressed_bytes),
                    _human_size(built.archive_bytes), self.site_url))
        return client.upload_zip(
            built.path, mode='update', slug=built.slug, consents=self.consents,
            display_name=self.display_name,
            base_revision=revision, delta=use_delta,
            expected_project_id=remote_project_id,
            progress=self._upload_progress(feedback))

    def destinationUrl(self):
        return self.export_file or ''

    def writeToProject(self):
        project = QgsProject.instance()
        for key, value in (
                ('CloudSiteUrl', self.site_url), ('CloudUser', self.username),
                ('CloudAuthConfigId', self.authcfg_id), ('CloudProjectSlug', self.slug),
                ('CloudUpdateSlug', self.target_slug),
                ('CloudProjectId', self.project_id),
                ('CloudUpdateProjectId', self.target_project_id),
                ('CloudDisplayName', self.display_name),
                ('CloudRememberCredentials', self.remember_credentials)):
            project.writeEntry('qgis2web', key, value)


class CloudExporter(CloudPublishExporter):
    mode = 'create'

    @classmethod
    def type(cls):
        return 'cloud'

    @classmethod
    def name(cls):
        return QCoreApplication.translate('CloudExporter', 'Cloud Export (O.GIS)')


class CloudSyncExporter(CloudPublishExporter):
    mode = 'update'

    @classmethod
    def type(cls):
        return 'cloud_sync'

    @classmethod
    def name(cls):
        return QCoreApplication.translate('CloudSyncExporter', 'Cloud Update (O.GIS)')


class ExporterRegistry(QObject):
    """Registry for managing available export destinations."""

    def __init__(self, parent=None):
        super(ExporterRegistry, self).__init__(parent)
        self.exporters = {exporter.type(): exporter for exporter in (
            FolderExporter, FolderSyncExporter, CloudExporter,
            CloudSyncExporter, FtpExporter)}

    def getExporters(self):
        return self.exporters.values()

    def createFromProject(self):
        exporter_type, ok = QgsProject.instance().readEntry('qgis2web', 'Exporter')
        exporter = None
        if ok and exporter_type:
            exporter = self.exporters.get(exporter_type)
        instance = exporter() if exporter else FolderExporter()
        instance.readFromProject()
        return instance

    def writeToProject(self, exporter):
        QgsProject.instance().writeEntry('qgis2web', 'Exporter', exporter.type())
        exporter.writeToProject()

    def getOptions(self):
        return tuple(exporter.name() for exporter in self.exporters.values())


EXPORTER_REGISTRY = ExporterRegistry()
