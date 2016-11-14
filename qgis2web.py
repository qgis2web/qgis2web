# -*- coding: utf-8 -*-

# qgis-ol3 Creates OpenLayers map from QGIS layers
# Copyright (C) 2014 Victor Olaya (volayaf@gmail.com)
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


from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import resources_rc
from maindialog import MainDialog


class Qgis2Web(object):
    """Class abstraction for managing Qgis2Web plugin in QGIS."""
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        self.action = QAction(
            QIcon(":/plugins/qgis2web/icons/qgis2web.png"),
            u"Create web map", self.iface.mainWindow())
        self.action.triggered.connect(self.run)

        self.iface.addPluginToWebMenu(u"&qgis2web", self.action)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removePluginWebMenu(u"&qgis2web", self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        dlg = MainDialog(self.iface)
        dlg.show()
