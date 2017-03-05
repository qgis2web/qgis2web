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

from olwriter import (OpenLayersWriter)
from leafletWriter import (LeafletWriter)

translator = QObject()


class WriterRegistry(object):

    """
    A registry for known writer types.
    """

    def __init__(self):
        self.writers = {e.type(): e for e in
                        [OpenLayersWriter, LeafletWriter]}

    def getWriters(self):
        """
        :return: List of available writers
        """
        return self.writers.values()

    def saveTypeToProject(self, type):
        """
        Stores a writer type as the type associated with the loaded project
        :param type: type string for associated writer class
        """
        assert QgsProject.instance().writeEntry("qgis2web", "mapFormat", type)

    def getWriterFactoryFromProject(self):
        """
        Returns the factory for the writer type associated with the
        load project.
        :return:
        """
        try:
            type = QgsProject.instance().readEntry("qgis2web",
                                                   "mapFormat")[0]
            for w in self.writers.values():
                if type.lower() == w.type().lower():
                    return w

        except:
            pass

        return OpenLayersWriter  # default to OpenLayersWriter

    def saveBasemapsToProject(self, basemaps):
        """
        Stores a list of enabled basemaps for the writer
        in the current project.
        :param basemaps: list of basemap names
        """
        basemaplist = ",".join(basemaps)
        QgsProject.instance().writeEntry("qgis2web", "Basemaps", basemaplist)

    def getBasemapsFromProject(self):
        """
        Returns a list of enabled basemaps for the writer stored
        in the current project.
        """
        try:
            basemaps = QgsProject.instance().readEntry(
                "qgis2web", "Basemaps")[0]
            if basemaps.strip() == '':
                return []
            return basemaps.split(",")
        except:
            return []

# canonical instance.
WRITER_REGISTRY = WriterRegistry()
