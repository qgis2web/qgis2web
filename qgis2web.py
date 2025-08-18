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


from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsApplication

#import sip
import os
# from . import resources_rc
from qgis2web.maindialog import MainDialog
from qgis2web.qgis2webProvider import qgis2webProvider


class Qgis2Web(object):
    """Class abstraction for managing Qgis2Web plugin in QGIS."""

    def __init__(self, iface):
        self.provider = qgis2webProvider()
        self.iface = iface
        self.dlg = None

    def initGui(self):
        QgsApplication.processingRegistry().addProvider(self.provider)
        icon = os.path.join(os.path.dirname(__file__), "icons", "qgis2web.png")
        self.action = QAction(
            QIcon(icon),
            u"Create web map", self.iface.mainWindow())
        self.action.triggered.connect(self.run)

        self.iface.addPluginToWebMenu(u"&qgis2web", self.action)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)
        self.iface.removePluginWebMenu(u"&qgis2web", self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        if self.dlg is None:
            self.dlg = MainDialog(self.iface)
            self.dlg.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            self.dlg.destroyed.connect(lambda: setattr(self, 'dlg', None))
        self.dlg.show()
        self.dlg.raise_()
