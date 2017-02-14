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

from qgis.core import (QgsProject)
from PyQt4.QtCore import (QObject)
from PyQt4.QtGui import (QFileDialog)
from utils import (tempFolder)

translator = QObject()


class Exporter(QObject):
    """
    Generic base class for web map exporters
    """

    def __init__(self):
        pass

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
        :return: Directory to create output HTML and associated files in. For some
        exporters this will indicate the final destination of the output, for others
        this will be a temporary folder which is later copied to a final destination.
        """
        return ''

    def postProcess(self, export_file):
        """
        Called after HTML output is created and written to the exportDirectory(). Can
        be used to perform steps such as uploading the exported files to a remote
        location.
        :param export_file: index file created for web map
        """
        pass

    def destinationUrl(self):
        """
        :return: URL corresponding to final location for exported web map. This URL
        should be accessible in a web browser.
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
        return QObject.tr(translator, 'Export to folder')

    def configure(self, parent_widget=None):
        new_folder = QFileDialog.getExistingDirectory(parent_widget,
                                                      self.tr("Choose export folder"),
                                                      self.folder,
                                                      QFileDialog.ShowDirsOnly)
        if new_folder:
            self.folder = new_folder

    def exportDirectory(self):
        return self.folder

    def postProcess(self, export_file):
        self.export_file = export_file

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


class FtpExporter(Exporter):
    """
    Exporter for writing web map to an FTP site
    """

    def __init__(self):
        super(Exporter, self).__init__()
        self.folder = tempFolder()
        self.export_file = None

    @classmethod
    def type(cls):
        return 'ftp'

    @classmethod
    def name(cls):
        return QObject.tr(translator, 'Export to FTP site')

    def configure(self, parent_widget=None):
        new_folder = QFileDialog.getExistingDirectory(parent_widget,
                                                      self.tr("Choose FTP folder"),
                                                      self.folder,
                                                      QFileDialog.ShowDirsOnly)
        if new_folder:
            self.folder = new_folder

    def exportDirectory(self):
        return self.folder

    def postProcess(self, export_file):
        self.export_file = export_file

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


class ExporterRegistry(QObject):
    """
    Registry for managing the available exporter options. This is not usually
    created directly but instead accessed through to canonical EXPORTER_REGISTRY
    instance.
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
            except:
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
