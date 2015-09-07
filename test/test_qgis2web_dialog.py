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
from qgis.core import QgsProject
from PyQt4 import QtCore, QtTest
from PyQt4.QtCore import QFileInfo
from PyQt4.QtGui import QDialogButtonBox, QDialog
from utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from maindialog import MainDialog

class qgis2web_classDialogTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""
        self.dialog = MainDialog(IFACE)

    def tearDown(self):
        """Runs after each test."""
        self.dialog = None

    def test_preview_default(self):
        """Preview default - no data (OL3) (test_qgis2web_dialog.test_preview_default)."""
        self.dialog.buttonPreview.click()

    def test_save_default(self):
        """Save default - no data (OL3) (test_qgis2web_dialog.test_save_default)."""
        self.dialog.buttonExport.click()

    def test_toggle_Leaflet(self):
        """Toggle to Leaflet (test_qgis2web_dialog.test_toggle_Leaflet)."""
        self.dialog.leaflet.click()

    def test_preview_Leaflet(self):
        """Preview Leaflet - no data (test_qgis2web_dialog.test_preview_Leaflet)."""
        self.dialog.leaflet.click()
        self.dialog.buttonPreview.click()

    def test_export_Leaflet(self):
        """Export Leaflet - no data (test_qgis2web_dialog.test_export_Leaflet)."""
        self.dialog.leaflet.click()
        self.dialog.buttonExport.click()

    def test_toggle_OL3(self):
        """Toggle to OL3 (test_qgis2web_dialog.test_toggle_OL3)."""
        self.dialog.ol3.click()

    def test_preview_OL3(self):
        """Preview OL3 - no data (test_qgis2web_dialog.test_preview_OL3)."""
        self.dialog.ol3.click()
        self.dialog.buttonPreview.click()

    def test_export_OL3(self):
        """Export OL3 - no data (test_qgis2web_dialog.test_export_OL3)."""
        self.dialog.ol3.click()
        self.dialog.buttonExport.click()

    def test_Leaflet_shp_pnt_simple(self):
        """Leaflet shape point simple (test_qgis2web_dialog.test_Leaflet_shp_pnt_simple)."""
        project = QgsProject.instance()
        project.read(QFileInfo('/share/qgis/python/plugins/qgis2web/test_data/shp_point_simple.qgs'))
        self.dialog.leaflet.click()
        self.dialog.buttonExport.click()

    def test_OL3_shp_pnt_simple(self):
        """OL3 shape point simple (test_qgis2web_dialog.test_OL3_shp_pnt_simple)."""
        project = QgsProject.instance()
        project.read(QFileInfo('/share/qgis/python/plugins/qgis2web/test_data/shp_point_simple.qgs'))
        self.dialog.ol3.click()
        self.dialog.buttonExport.click()

    def test_Leaflet_shp_pnt_categorized(self):
        """Leaflet shape point categorized (test_qgis2web_dialog.test_Leaflet_shp_pnt_categorized)."""
        project = QgsProject.instance()
        project.read(QFileInfo('/share/qgis/python/plugins/qgis2web/test_data/shp_point_categorized.qgs'))
        self.dialog.leaflet.click()
        self.dialog.buttonExport.click()

    def test_OL3_shp_pnt_categorized(self):
        """OL3 shape point categorized (test_qgis2web_dialog.test_OL3_shp_pnt_categorized)."""
        project = QgsProject.instance()
        project.read(QFileInfo('/share/qgis/python/plugins/qgis2web/test_data/shp_point_categorized.qgs'))
        self.dialog.ol3.click()
        self.dialog.buttonExport.click()

    def test_Leaflet_shp_pnt_graduated(self):
        """Leaflet shape point graduated (test_qgis2web_dialog.test_Leaflet_shp_pnt_graduated)."""
        project = QgsProject.instance()
        project.read(QFileInfo('/share/qgis/python/plugins/qgis2web/test_data/shp_point_graduateded.qgs'))
        self.dialog.leaflet.click()
        self.dialog.buttonExport.click()

    def test_OL3_shp_pnt_graduated(self):
        """OL3 shape point graduated (test_qgis2web_dialog.test_OL3_shp_pnt_graduated)."""
        project = QgsProject.instance()
        project.read(QFileInfo('/share/qgis/python/plugins/qgis2web/test_data/shp_point_graduated.qgs'))
        self.dialog.ol3.click()
        self.dialog.buttonExport.click()

    def test_Leaflet_shp_line_simple(self):
        """Leaflet shape line simple (test_qgis2web_dialog.test_Leaflet_shp_line_simple)."""
        project = QgsProject.instance()
        project.read(QFileInfo('/share/qgis/python/plugins/qgis2web/test_data/shp_line_simple.qgs'))
        self.dialog.leaflet.click()
        self.dialog.buttonExport.click()

    def test_OL3_shp_line_simple(self):
        """OL3 shape line simple (test_qgis2web_dialog.test_OL3_shp_line_simple)."""
        project = QgsProject.instance()
        project.read(QFileInfo('/share/qgis/python/plugins/qgis2web/test_data/shp_line_simple.qgs'))
        self.dialog.ol3.click()
        self.dialog.buttonExport.click()

    def test_Leaflet_shp_line_categorized(self):
        """Leaflet shape line categorized (test_qgis2web_dialog.test_Leaflet_shp_line_categorized)."""
        project = QgsProject.instance()
        project.read(QFileInfo('/share/qgis/python/plugins/qgis2web/test_data/shp_line_categorized.qgs'))
        self.dialog.leaflet.click()
        self.dialog.buttonExport.click()

    def test_OL3_shp_line_categorized(self):
        """OL3 shape line categorized (test_qgis2web_dialog.test_OL3_shp_line_categorized)."""
        project = QgsProject.instance()
        project.read(QFileInfo('/share/qgis/python/plugins/qgis2web/test_data/shp_line_categorized.qgs'))
        self.dialog.ol3.click()
        self.dialog.buttonExport.click()

    def test_Leaflet_shp_line_graduated(self):
        """Leaflet shape line graduated (test_qgis2web_dialog.test_Leaflet_shp_line_graduated)."""
        project = QgsProject.instance()
        project.read(QFileInfo('/share/qgis/python/plugins/qgis2web/test_data/shp_line_graduateded.qgs'))
        self.dialog.leaflet.click()
        self.dialog.buttonExport.click()

    def test_OL3_shp_line_graduated(self):
        """OL3 shape line graduated (test_qgis2web_dialog.test_OL3_shp_line_graduated)."""
        project = QgsProject.instance()
        project.read(QFileInfo('/share/qgis/python/plugins/qgis2web/test_data/shp_line_graduated.qgs'))
        self.dialog.ol3.click()
        self.dialog.buttonExport.click()

    def test_Leaflet_shp_polygon_simple(self):
        """Leaflet shape polygon simple (test_qgis2web_dialog.test_Leaflet_shp_polygon_simple)."""
        project = QgsProject.instance()
        project.read(QFileInfo('/share/qgis/python/plugins/qgis2web/test_data/shp_polygon_simple.qgs'))
        self.dialog.leaflet.click()
        self.dialog.buttonExport.click()

    def test_OL3_shp_polygon_simple(self):
        """OL3 shape polygon simple (test_qgis2web_dialog.test_OL3_shp_polygon_simple)."""
        project = QgsProject.instance()
        project.read(QFileInfo('/share/qgis/python/plugins/qgis2web/test_data/shp_polygon_simple.qgs'))
        self.dialog.ol3.click()
        self.dialog.buttonExport.click()

    def test_Leaflet_shp_polygon_categorized(self):
        """Leaflet shape polygon categorized (test_qgis2web_dialog.test_Leaflet_shp_polygon_categorized)."""
        project = QgsProject.instance()
        project.read(QFileInfo('/share/qgis/python/plugins/qgis2web/test_data/shp_polygon_categorized.qgs'))
        self.dialog.leaflet.click()
        self.dialog.buttonExport.click()

    def test_OL3_shp_polygon_categorized(self):
        """OL3 shape polygon categorized (test_qgis2web_dialog.test_OL3_shp_polygon_categorized)."""
        project = QgsProject.instance()
        project.read(QFileInfo('/share/qgis/python/plugins/qgis2web/test_data/shp_polygon_categorized.qgs'))
        self.dialog.ol3.click()
        self.dialog.buttonExport.click()

    def test_Leaflet_shp_polygon_graduated(self):
        """Leaflet shape polygon graduated (test_qgis2web_dialog.test_Leaflet_shp_polygon_graduated)."""
        project = QgsProject.instance()
        project.read(QFileInfo('/share/qgis/python/plugins/qgis2web/test_data/shp_polygon_graduateded.qgs'))
        self.dialog.leaflet.click()
        self.dialog.buttonExport.click()

    def test_OL3_shp_polygon_graduated(self):
        """OL3 shape polygon graduated (test_qgis2web_dialog.test_OL3_shp_polygon_graduated)."""
        project = QgsProject.instance()
        project.read(QFileInfo('/share/qgis/python/plugins/qgis2web/test_data/shp_polygon_graduated.qgs'))
        self.dialog.ol3.click()
        self.dialog.buttonExport.click()

if __name__ == "__main__":
    suite = unittest.makeSuite(qgis2web_classDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

