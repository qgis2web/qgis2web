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

from qgis.core import QgsProject
from qgis.PyQt.QtCore import QObject

from qgis2web.olwriter import OpenLayersWriter
from qgis2web.leafletWriter import LeafletWriter
from qgis2web.configparams import getDefaultParams

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

        except Exception:
            pass

        return OpenLayersWriter  # default to OpenLayersWriter

    @staticmethod
    def sanitiseKey(key):
        """
        Sanitises a parameter key to make it safe to store in settings
        """
        return key.replace(' ', '')

    def saveParamsToProject(self, params):
        """
        Saves writer parameters to the current project
        :param params: writer parameter dictionary
        """
        for group, settings in params.items():
            for param, value in settings.items():
                if param == "Attribute filter":
                    continue
                if isinstance(value, bool):
                    QgsProject.instance().writeEntryBool("qgis2web",
                                                         self.sanitiseKey(
                                                             param),
                                                         value)
                else:
                    QgsProject.instance().writeEntry("qgis2web",
                                                     self.sanitiseKey(param),
                                                     value)

    def readParamFromProject(self, parameter, default_value):
        """
        Reads the value of a single parameter from the current
        project.
        :param parameter: parameter key
        :param default_value: default value for parameter
        """
        project = QgsProject.instance()
        key_string = self.sanitiseKey(parameter)

        value = default_value
        if isinstance(default_value, bool):
            if project.readBoolEntry(
                    "qgis2web", key_string)[1]:
                value = project.readBoolEntry("qgis2web",
                                              key_string)[0]
        elif isinstance(default_value, int):
            if project.readNumEntry(
                    "qgis2web", key_string)[1]:
                value = project.readNumEntry("qgis2web",
                                             key_string)[0]
        else:
            if (isinstance(project.readEntry("qgis2web",
                                             key_string)[0], str) and
                    project.readEntry("qgis2web", key_string)[0] != ""):
                value = project.readEntry("qgis2web", key_string)[0]

        return value

    def readParamsFromProject(self):
        """
        Reads all writer parameters from the current project
        :return: default writer parameters within parameters replaced
        by any matching settings in the current projects
        """

        default_params = getDefaultParams()
        read_params = default_params
        for group, settings in default_params.items():
            for param, default_value in settings.items():
                value = self.readParamFromProject(param, default_value)
                read_params[group][param] = value

        return read_params

    def createWriterFromProject(self):
        """
        Creates a writer matching the state from the current project
        """
        writer = self.getWriterFactoryFromProject()()
        writer.params = self.readParamsFromProject()
        return writer

    def saveWriterToProject(self, writer):
        """
        Saves the settings from a writer to the current project
        """
        QgsProject.instance().removeEntry("qgis2web", "/")

        self.saveTypeToProject(writer.type())
        self.saveParamsToProject(writer.params)


# canonical instance.
WRITER_REGISTRY = WriterRegistry()
