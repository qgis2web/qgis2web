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

import os
from datetime import datetime

from qgis.core import QgsProject
from qgis.PyQt.QtCore import QObject, QCoreApplication
from qgis.PyQt.QtWidgets import QFileDialog, QInputDialog, QDialog, QLineEdit
from .utils import tempFolder
from .feedbackDialog import Feedback

from .ui_ftp_configuration import Ui_FtpConfiguration


class Exporter(QObject):

    """
    Generic base class for web map exporters
    """

    def __init__(self):
        super(QObject, self).__init__()

    @classmethod
    def type(cls):
        """
        :return: Unique string for exporter type
        """
        return ''

    @classmethod
    def name(cls):
        """
        :return: Translated, user friendly name for exporter
        """
        return ''

    def configure(self):
        """
        Opens a dialog allowing users to configure the exporter's settings
        """
        pass

    def exportDirectory(self):
        """
        :return: Directory to create output HTML and associated
        files in. For some exporters this will indicate the final
        destination of the output, for others this will be a temporary
        folder which is later copied to a final destination.
        """
        return ''

    def postProcess(self, results, feedback=None):
        """
        Called after HTML output is created and written
        to the exportDirectory(). Can be used to perform
        steps such as uploading the exported files to a remote
        location.
        :param results: WriterResults from Writer generation
        :param feedback: optional feedback object for progress reports
        Returns True if processing was successful
        """
        pass

    def destinationUrl(self):
        """
        :return: URL corresponding to final location for exported
        web map. This URL should be accessible in a web browser.
        """
        return ''

    def writeToProject(self):
        """
        Writes the exporter's settings to the current project.
        """
        pass

    def readFromProject(self):
        """
        Reads the exporter's settings from the current project.
        """
        pass


class FolderExporter(Exporter):

    """
    Exporter for writing web map to a folder
    """

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
        new_folder = \
            QFileDialog.getExistingDirectory(parent_widget,
                                             self.tr("Choose export folder"),
                                             self.folder,
                                             QFileDialog.Option.ShowDirsOnly)
        if new_folder:
            self.folder = new_folder

    def exportDirectory(self):
        return self.folder

    def postProcess(self, results, feedback=None):
        if not feedback:
            feedback = Feedback()
        self.export_file = results.index_file
        feedback.setCompleted('Exported to {}'.format(self.folder))
        return True

    def destinationUrl(self):
        return self.export_file

    def writeToProject(self):
        QgsProject.instance().writeEntry("qgis2web",
                                         "Exportfolder",
                                         self.folder)

    def readFromProject(self):
        folder, ok = QgsProject.instance().readEntry("qgis2web",
                                                     "Exportfolder")
        if ok and folder:
            self.folder = folder


class FtpConfigurationDialog(QDialog, Ui_FtpConfiguration):

    """
    A dialog for configuring FTP connection details such as host
    and username
    """

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

    def setHost(self, host):
        """
        Sets the host name to initially show in the dialog
        """
        self.hostLineEdit.setText(host)

    def setPort(self, port):
        """
        Sets the port to initially show in the dialog
        """
        try:
            port_number = int(port)
            self.portSpinBox.setValue(port_number)
        except Exception:
            pass

    def setUsername(self, username):
        """
        Sets the username to initially show in the dialog
        """
        self.usernameLineEdit.setText(username)

    def setFolder(self, folder):
        """
        Sets the folder to initially show in the dialog
        """
        self.folderLineEdit.setText(folder)

    def host(self):
        """
        Returns the current host name from the dialog
        """
        return self.hostLineEdit.text()

    def username(self):
        """
        Returns the current user name from the dialog
        """
        return self.usernameLineEdit.text()

    def folder(self):
        """
        Returns the current folder from the dialog
        """
        return self.folderLineEdit.text()

    def port(self):
        """
        Returns the current port from the dialog
        """
        return self.portSpinBox.value()


class FtpExporter(Exporter):

    """
    Exporter for writing web map to an FTP site
    """

    def __init__(self):
        super(Exporter, self).__init__()
        # some default values
        self.host = 'myhost.com'
        self.username = 'user'
        self.remote_folder = 'public_html/'
        self.port = 22
        # if none, user will be prompted for password
        self.password = None
        self.temp_folder = self.newTempFolder(tempFolder())

    def newTempFolder(self, base):
        stamp = datetime.now().strftime("%Y_%m_%d-%H_%M_%S_%f")
        return os.path.join(base, 'qgis2web_' + stamp)

    @classmethod
    def type(cls):
        return 'ftp'

    @classmethod
    def name(cls):
        return QCoreApplication.translate('FtpExporter', 'Export to SFTP site')

    def configure(self, parent_widget=None):
        dialog = FtpConfigurationDialog(parent_widget)
        dialog.setHost(self.host)
        dialog.setUsername(self.username)
        dialog.setPort(self.port)
        dialog.setFolder(self.remote_folder)
        if dialog.exec_():
            self.host = dialog.host()
            self.username = dialog.username()
            self.port = dialog.port()
            self.remote_folder = dialog.folder()

    def exportDirectory(self):
        return self.temp_folder

    def postProcess(self, results, feedback=None):
        if not feedback:
            feedback = Feedback()

        self.export_file = results.index_file
        file_count = max(len(results.files), 1)

        # generate a new temp_folder for next export
        self.temp_folder = self.newTempFolder(tempFolder())

        source_folder = results.folder

        if not self.host or not self.username or not self.port:
            return False

        # get password
        password = self.password
        if password is None:
            password, ok = QInputDialog.getText(
                None, 'Enter SFTP password', 'Password', QLineEdit.Password)
            if not password or not ok:
                feedback.setFatalError('User cancelled')
                return False

        feedback.showFeedback(
            'Connecting to {} on port {}...'.format(self.host, self.port))

        try:
            import paramiko
        except ImportError:
            feedback.setFatalError(
                'The paramiko library is required for SFTP export. '
                'Please install it via: pip install paramiko')
            return False

        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
        try:
            ssh.connect(self.host, port=self.port,
                        username=self.username, password=password)
        except Exception:
            feedback.setFatalError('Could not connect to server!')
            return False

        feedback.showFeedback('Connected!')
        if feedback.cancelled():
            feedback.acceptCancel()
            ssh.close()
            return False

        try:
            sftp = ssh.open_sftp()
        except Exception:
            feedback.setFatalError('Could not open SFTP channel!')
            ssh.close()
            return False

        feedback.showFeedback('Logged in to {}'.format(self.host))

        def sftp_makedirs(remote_path):
            parts = [p for p in remote_path.replace('\\', '/').split('/') if p]
            prefix = '/' if remote_path.startswith('/') else ''
            current = prefix
            for part in parts:
                current = (current + part if not current or current == '/'
                           else current + '/' + part)
                try:
                    sftp.stat(current)
                except OSError:
                    feedback.showFeedback('Creating {}'.format(current))
                    sftp.mkdir(current)

        sftp_makedirs(self.remote_folder)

        uploaded_count = 0.0

        def uploadPath(local_path, remote_path):
            nonlocal uploaded_count
            if feedback.cancelled():
                feedback.acceptCancel()
                return False
            for item in os.listdir(local_path):
                if feedback.cancelled():
                    feedback.acceptCancel()
                    return False
                local_item = os.path.join(local_path, item)
                remote_item = remote_path.rstrip('/') + '/' + item
                if os.path.isfile(local_item):
                    feedback.showFeedback('Uploading {}'.format(item))
                    sftp.put(local_item, remote_item)
                    uploaded_count += 1
                    feedback.setProgress(100 * uploaded_count / file_count)
                elif os.path.isdir(local_item):
                    feedback.showFeedback('Creating folder {}'.format(item))
                    try:
                        sftp.mkdir(remote_item)
                    except Exception:
                        pass
                    if not uploadPath(local_item, remote_item):
                        return False
            return True

        remote_base = self.remote_folder.rstrip('/')
        if not uploadPath(source_folder, remote_base):
            sftp.close()
            ssh.close()
            return False

        feedback.setCompleted('Upload complete!')
        sftp.close()
        ssh.close()
        return True

    def destinationUrl(self):
        return self.export_file

    def writeToProject(self):
        QgsProject.instance().writeEntry("qgis2web",
                                         "FtpHost",
                                         self.host)
        QgsProject.instance().writeEntry("qgis2web",
                                         "FtpUser",
                                         self.username)
        QgsProject.instance().writeEntry("qgis2web",
                                         "FtpFolder",
                                         self.remote_folder)
        QgsProject.instance().writeEntry("qgis2web",
                                         "FtpPort",
                                         self.port)

    def readFromProject(self):
        host, ok = QgsProject.instance().readEntry("qgis2web",
                                                   "FtpHost")
        if ok and host:
            self.host = host
        user, ok = QgsProject.instance().readEntry("qgis2web",
                                                   "FtpUser")
        if ok and user:
            self.username = user
        folder, ok = QgsProject.instance().readEntry("qgis2web",
                                                     "FtpFolder")
        if ok and user:
            self.remote_folder = folder
        port, ok = QgsProject.instance().readNumEntry("qgis2web",
                                                      "FtpPort")
        if ok and port:
            self.port = port


class ExporterRegistry(QObject):

    """
    Registry for managing the available exporter options.
    This is not usually created directly but instead accessed
    through to canonical EXPORTER_REGISTRY instance.
    """

    def __init__(self, parent=None):
        super(ExporterRegistry, self).__init__(parent)

        self.exporters = {e.type(): e for e in
                          [FolderExporter, FtpExporter]}

    def getExporters(self):
        """
        :return: List of available exporters
        """
        return self.exporters.values()

    def createFromProject(self):
        """
        Creates a new exporter by reading the corresponding exporter type
        and settings from the current project.
        :return: new exporter
        """
        type, ok = QgsProject.instance().readEntry("qgis2web",
                                                   "Exporter")
        exporter = None
        if ok and type:
            try:
                exporter = self.exporters[type]()
            except Exception:
                pass

        if not exporter:
            exporter = FolderExporter()  # default

        exporter.readFromProject()
        return exporter

    def writeToProject(self, exporter):
        """
        Writes an exporters settings to the current project and stores the
        exporter type as the active exporter.
        """
        QgsProject.instance().writeEntry("qgis2web",
                                         "Exporter", exporter.type())
        exporter.writeToProject()

    def getOptions(self):
        """
        :return: tuple for use within getParams call
        """
        return tuple([e.name() for e in self.exporters.values()])


# canonical instance.
EXPORTER_REGISTRY = ExporterRegistry()
