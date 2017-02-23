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

from PyQt4.QtCore import (QObject)

translator = QObject()


class Writer(object):

    """
    Generic base class for web map writers. Writers generate the
    HTML, JavaScript and collect other assets required for
    creation of a standalone web map.
    """

    def __init__(self):
        self.written_files = []
        self.preview_file = None

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

    def write(self, iface, groups, layers, visible, cluster, popup,
              json, params, dest_folder):
        """
        Writes the web map output for a specified configuation.
        :param iface: QGIS interface
        :param groups: layer groups
        :param layers: list of layers to write
        :param visible: list of whether each layer is visible
        :param cluster: list of whether each layer should be clustered
        :param popup: popup content
        :param json: json content
        :param params: configuration dictionary (TODO - standardise
        between writers!)
        :param dest_folder destination folder for writing
        :return: True if writing was successful
        """
        return False
