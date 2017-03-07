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

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import

from utilities import get_qgis_app
from qgis.core import (QgsProject)
from writerRegistry import (WRITER_REGISTRY)
from olwriter import (OpenLayersWriter)
from leafletWriter import (LeafletWriter)
from configparams import (getDefaultParams)

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class qgis2web_writerRegistryTest(unittest.TestCase):

    """Test writer registry"""

    def setUp(self):
        """Runs before each test"""
        pass

    def test01_RegistryHasExporters(self):
        """test that writer registry is populated with writers"""
        self.assertTrue(OpenLayersWriter in WRITER_REGISTRY.getWriters())

    def test02_SaveRestoreWriterTypeFromProject(self):
        """Test saving and restoring writer type from project"""
        WRITER_REGISTRY.saveTypeToProject(OpenLayersWriter.type())
        self.assertEqual(
            WRITER_REGISTRY.getWriterFactoryFromProject(), OpenLayersWriter)
        WRITER_REGISTRY.saveTypeToProject(LeafletWriter.type())
        self.assertEqual(
            WRITER_REGISTRY.getWriterFactoryFromProject(), LeafletWriter)

        # no existing settings
        QgsProject.instance().removeEntry("qgis2web", "/")
        self.assertEqual(
            WRITER_REGISTRY.getWriterFactoryFromProject(), OpenLayersWriter)

    def test03_SaveRestoreBasemapsFromProject(self):
        """Test saving and restoring enabled basemaps from project"""
        self.assertEqual(WRITER_REGISTRY.getBasemapsFromProject(),[])
        WRITER_REGISTRY.saveBasemapsToProject(['a','b c d'])
        self.assertEqual(WRITER_REGISTRY.getBasemapsFromProject(),['a','b c d'])

        # no existing settings
        QgsProject.instance().removeEntry("qgis2web", "/")
        self.assertEqual(WRITER_REGISTRY.getBasemapsFromProject(), [])

    def test04_SanitiseKey(self):
        """Test sanitising param key for storage"""
        self.assertEqual(WRITER_REGISTRY.sanitiseKey('a'),'a')
        self.assertEqual(WRITER_REGISTRY.sanitiseKey('a b'),'ab')

    def test05_SaveRestoreParamsFromProject(self):
        """Test saving and restoring parameters from project"""

        # no settings in project, should match defaults
        QgsProject.instance().removeEntry("qgis2web", "/")

        params = WRITER_REGISTRY.readParamsFromProject()
        self.maxDiff = 1000000000
        self.assertEqual(params, getDefaultParams() )

        # change some parameters (one of each type)

        params['Appearance']['Add layers list'] = True
        params['Data export']['Minify GeoJSON files'] = False
        # no ints in config yet!
        # params['Test']['test int'] = 5
        params['Data export']['Precision'] = '4'
        params['Data export']['Mapping library location'] = 'CDN'
        # no strings in config yet!
        # params['Test']['test string'] ='test'

        WRITER_REGISTRY.saveParamsToProject(params)
        restored_params = WRITER_REGISTRY.readParamsFromProject()
        self.assertEqual(restored_params,params)

    def test06_SaveRestoreWriterFromProject(self):
        """Test saving and restoring writer state to project"""

        writer = LeafletWriter()
        writer.params = getDefaultParams()
        # change some parameters
        writer.params['Appearance']['Add layers list'] = True
        writer.params['Data export']['Minify GeoJSON files'] = False
        writer.params['Data export']['Precision'] = '4'
        writer.params['Data export']['Mapping library location'] = 'CDN'
        writer.params['Appearance']['Base layer'] = ['a','b','c']

        WRITER_REGISTRY.saveWriterToProject(writer)

        new_writer = WRITER_REGISTRY.createWriterFromProject()
        self.assertTrue( isinstance(new_writer, LeafletWriter))
        self.assertEqual(new_writer.params,writer.params)



if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(qgis2web_writerRegistryTest))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
