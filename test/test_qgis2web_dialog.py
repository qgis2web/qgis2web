# coding=utf-8
"""Dialog test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'riccardo.klinger@geolicious.de'
__date__ = '2015-03-26'
__copyright__ = 'Copyright 2015, Riccardo Klinger / Geolicious'

import unittest

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
# from qgis.core import QgsProject
from PyQt4 import QtCore, QtTest
from PyQt4.QtCore import QFileInfo
# from PyQt4.QtGui import QDialogButtonBox, QDialog
from utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from maindialog import MainDialog

class qgis2web_classDialogTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""
        # self.dialog = MainDialog(IFACE)

    def tearDown(self):
        """Runs after each test."""
        self.dialog = None

    def test01_preview_default(self):
        """Preview default - no data (OL3) (test_qgis2web_dialog.test_preview_default)."""
        self.dialog.buttonPreview.click()

    def test02_save_default(self):
        """Save default - no data (OL3) (test_qgis2web_dialog.test_save_default)."""
        self.dialog.buttonExport.click()

    def test03_toggle_Leaflet(self):
        """Toggle to Leaflet (test_qgis2web_dialog.test_toggle_Leaflet)."""
        self.dialog.leaflet.click()

    def test04_preview_Leaflet(self):
        """Preview Leaflet - no data (test_qgis2web_dialog.test_preview_Leaflet)."""
        self.dialog.leaflet.click()
        self.dialog.buttonPreview.click()

    def test05_export_Leaflet(self):
        """Export Leaflet - no data (test_qgis2web_dialog.test_export_Leaflet)."""
        self.dialog.leaflet.click()
        self.dialog.buttonExport.click()

    def test06_toggle_OL3(self):
        """Toggle to OL3 (test_qgis2web_dialog.test_toggle_OL3)."""
        self.dialog.ol3.click()

    def test07_preview_OL3(self):
        """Preview OL3 - no data (test_qgis2web_dialog.test_preview_OL3)."""
        self.dialog.ol3.click()
        self.dialog.buttonPreview.click()

    def test08_export_OL3(self):
        """Export OL3 - no data (test_qgis2web_dialog.test_export_OL3)."""
        self.dialog.ol3.click()
        self.dialog.buttonExport.click()

    def test09_Leaflet_shp_pnt_simple(self):
        """Leaflet shape point simple (test_qgis2web_dialog.test_Leaflet_shp_pnt_simple)."""
        layer = IFACE.addVectorLayer("/home/travis/build/tomchadwin/qgis2web/test_data/line_feature.shp", "line feature", "ogr")
        QgsMapLayerRegistry.instance().addMapLayers(layer)
        if not layer:
            print "Layer failed to load!"
        self.dialog = MainDialog(IFACE)
        testFile = open('/home/travis/build/tomchadwin/qgis2web/test_data/shp_point_simple.html', 'r')
        goodOutput = testFile.read()
        print "test09_Leaflet_shp_pnt_simple()"
        self.dialog.leaflet.click()
        self.dialog.buttonExport.click()

if __name__ == "__main__":
    suite = unittest.makeSuite(qgis2web_classDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

