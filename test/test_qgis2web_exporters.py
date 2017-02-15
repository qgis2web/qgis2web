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

__author__ = 'nyall.dawson@gmail.com'
__date__ = '2017-02-15'
__copyright__ = 'Copyright 2017, Nyall Dawson'

import unittest
import os
import difflib

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
from qgis.core import QgsProject
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry, QgsCoordinateReferenceSystem
from PyQt4 import QtCore, QtTest

from utilities import get_qgis_app, test_data_path, load_layer, load_wfs_layer
from exporter import (FolderExporter,
                      FtpExporter,
                      EXPORTER_REGISTRY)

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

class qgis2web_exporterTest(unittest.TestCase):
    """Test exporters and exporter registry"""

    def setUp(self):
        """Runs before each test"""
        pass

    def tearDown(self):
        """Runs after each test"""
        pass

    def test01_FolderExporterDefaultsToTemp(self):
        """Test that folder exporter defaults to a temporary folder"""
        e = FolderExporter()
        self.assertTrue(e.exportDirectory())

    def test02_FolderExporterPostProcess(self):
        """Test folder exporter post processing"""
        e = FolderExporter()
        e.postProcess('/tmp/file.htm')
        self.assertEqual(e.destinationUrl(),'/tmp/file.htm')

    def test03_FolderExporterSaveReadFromProject(self):
        """Test saving and restoring folder exporter settings in project"""
        e = FolderExporter()
        e.folder = '/my_folder'
        e.writeToProject()

        restored = FolderExporter()
        restored.readFromProject()

        self.assertEqual(restored.exportDirectory(),'/my_folder')

    def test04_RegistryHasExporters(self):
        """test that exporter registry is populated with exporters"""
        self.assertTrue(FolderExporter in EXPORTER_REGISTRY.getExporters())

    def test05_RegistrySaveReadFromProject(self):
        """ test saving and restoring current exporter in project"""
        e = FolderExporter()
        e.folder = '/my_folder'
        EXPORTER_REGISTRY.writeToProject(e)

        restored = EXPORTER_REGISTRY.createFromProject()
        self.assertEqual(type(restored),FolderExporter)
        self.assertEqual(restored.exportDirectory(), '/my_folder')

        # try with a non-folder exporter
        f = FtpExporter()
        EXPORTER_REGISTRY.writeToProject(f)
        restored = EXPORTER_REGISTRY.createFromProject()
        self.assertEqual(type(restored),FtpExporter)


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(qgis2web_exporterTest))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
