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

from qgis.PyQt.QtCore import QObject

translator = QObject()


class WriterResult(object):
    """
    Stores results of a writer operation
    """

    def __init__(self):
        self.index_file = None
        self.folder = None
        self.files = []


class Writer(object):

    """
    Generic base class for web map writers. Writers generate the
    HTML, JavaScript and collect other assets required for
    creation of a standalone web map.
    """

    def __init__(self):
        self.written_files = []
        self.preview_file = None
        # layer groups
        self.groups = {}
        # list of layers to write
        self.layers = []
        # list of whether each layer is visible
        self.visible = []
        # list of whether each layer is interactive
        self.interactive = []
        # list of whether each layer should be clustered
        self.cluster = []
        # popup content
        self.popup = None
        # json content
        self.json = None
        # queryable WMS
        self.getFeatureInfo = []
        # configuration dictionary (TODO - standardise
        # between writers!)
        self.params = {}

    @classmethod
    def type(cls):
        """
        :return: Unique string for writer type
        """
        return ''

    @classmethod
    def name(cls):
        """
        :return: Translated, user friendly name for writer
        """
        return ''

    def write(self, iface, dest_folder, feedback=None):
        """
        Writes the web map output for a specified configuation.
        :param iface: QGIS interface
        :param dest_folder destination folder for writing
        :param feedback optional feedback object
        :return: WriterResult object
        """
        return WriterResult()
