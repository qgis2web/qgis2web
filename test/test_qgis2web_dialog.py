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
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry
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
#        self.dialog = MainDialog(IFACE)

    def tearDown(self):
        """Runs after each test."""
        registry = QgsMapLayerRegistry.instance()
        registry.removeAllMapLayers()
        self.dialog = MainDialog(IFACE)
        self.dialog.ol3.click()
        self.dialog = None

    def test01_preview_default(self):
        """Preview default - no data (OL3) (test_qgis2web_dialog.test_preview_default)."""
        self.dialog = MainDialog(IFACE)
        self.dialog.buttonPreview.click()

    def test02_save_default(self):
        """Save default - no data (OL3) (test_qgis2web_dialog.test_save_default)."""
        self.dialog = MainDialog(IFACE)
        self.dialog.buttonExport.click()

    def test03_toggle_Leaflet(self):
        """Toggle to Leaflet (test_qgis2web_dialog.test_toggle_Leaflet)."""
        self.dialog = MainDialog(IFACE)
        self.dialog.leaflet.click()

    def test04_preview_Leaflet(self):
        """Preview Leaflet - no data (test_qgis2web_dialog.test_preview_Leaflet)."""
        self.dialog = MainDialog(IFACE)
        self.dialog.leaflet.click()
        self.dialog.buttonPreview.click()

    def test05_export_Leaflet(self):
        """Export Leaflet - no data (test_qgis2web_dialog.test_export_Leaflet)."""
        self.dialog = MainDialog(IFACE)
        self.dialog.leaflet.click()
        self.dialog.buttonExport.click()

    def test06_toggle_OL3(self):
        """Toggle to OL3 (test_qgis2web_dialog.test_toggle_OL3)."""
        self.dialog = MainDialog(IFACE)
        self.dialog.ol3.click()

    def test07_preview_OL3(self):
        """Preview OL3 - no data (test_qgis2web_dialog.test_preview_OL3)."""
        self.dialog = MainDialog(IFACE)
        self.dialog.ol3.click()
        self.dialog.buttonPreview.click()

    def test08_export_OL3(self):
        """Export OL3 - no data (test_qgis2web_dialog.test_export_OL3)."""
        self.dialog = MainDialog(IFACE)
        self.dialog.ol3.click()
        self.dialog.buttonExport.click()

    def test09_Leaflet_json_pnt_single(self):
        """Leaflet JSON point single (test_qgis2web_dialog.test_Leaflet_json_pnt_single)."""
        layer = QgsVectorLayer("/home/travis/build/tomchadwin/qgis2web/test_data/point.shp", "point feature", "ogr")
        if not layer:
            print "Layer failed to load!"
        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)
        layer.loadNamedStyle("/home/travis/build/tomchadwin/qgis2web/test_data/point_single.qml")
        testFile = open('/home/travis/build/tomchadwin/qgis2web/test_data/leaflet_json_point_single.html', 'r')
        goodOutput = testFile.read()
        self.dialog = MainDialog(IFACE)
        self.dialog.leaflet.click()
        outputFile = open(self.dialog.preview.url())
        outputCode = outputFile.read()
        print outputCode

    def test10_Leaflet_wfs_pnt_single(self):
        """Leaflet WFS point single (test_qgis2web_dialog.test_Leaflet_wfs_pnt_single)."""
        layer = QgsVectorLayer("http://maps.nationalparks.gov.uk/geoserver/wfs?SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME=dartmoor:dnpa-tpo-point&SRSNAME=EPSG:27700", "pointfeature", "WFS")
        if not layer:
            print "Layer failed to load!"
        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)
        layer.loadNamedStyle("/home/travis/build/tomchadwin/qgis2web/test_data/point_single.qml")
        testFile = open('/home/travis/build/tomchadwin/qgis2web/test_data/leaflet_json_point_single.html', 'r')
        goodOutput = testFile.read()
        self.dialog = MainDialog(IFACE)
        self.dialog.leaflet.click()

    def test11_Leaflet_json_line_single(self):
        """Leaflet JSON line single (test_qgis2web_dialog.test_Leaflet_json_line_single)."""
        layer = QgsVectorLayer("/home/travis/build/tomchadwin/qgis2web/test_data/line.shp", "line feature", "ogr")
        if not layer:
            print "Layer failed to load!"
        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)
        layer.loadNamedStyle("/home/travis/build/tomchadwin/qgis2web/test_data/line_single.qml")
        self.dialog = MainDialog(IFACE)
        self.dialog.leaflet.click()

    def test12_Leaflet_wfs_line_single(self):
        """Leaflet WFS line single (test_qgis2web_dialog.test_Leaflet_wfs_line_single)."""
        layer = QgsVectorLayer("http://maps.nationalparks.gov.uk/geoserver/wfs?SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME=yorkshire_dales:ydnpa_route_accessibility&SRSNAME=EPSG:27700", "linefeature", "WFS")
        if not layer:
            print "Layer failed to load!"
        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)
        layer.loadNamedStyle("/home/travis/build/tomchadwin/qgis2web/test_data/line_single.qml")
        self.dialog = MainDialog(IFACE)
        self.dialog.leaflet.click()

    def test13_Leaflet_json_poly_single(self):
        """Leaflet JSON polygon single (test_qgis2web_dialog.test_Leaflet_json_poly_single)."""
        layer = QgsVectorLayer("/home/travis/build/tomchadwin/qgis2web/test_data/polygon.shp", "polygon feature", "ogr")
        if not layer:
            print "Layer failed to load!"
        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)
        layer.loadNamedStyle("/home/travis/build/tomchadwin/qgis2web/test_data/polygon_single.qml")
        self.dialog = MainDialog(IFACE)
        self.dialog.leaflet.click()

    def test14_Leaflet_wfs_poly_single(self):
        """Leaflet WFS polygon single (test_qgis2web_dialog.test_Leaflet_wfs_poly_single)."""
        layer = QgsVectorLayer("http://maps.nationalparks.gov.uk/geoserver/wfs?SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME=yorkshire_dales:ydnpa_conservationareas&SRSNAME=EPSG:27700", "polygonfeature", "WFS")
        if not layer:
            print "Layer failed to load!"
        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)
        layer.loadNamedStyle("/home/travis/build/tomchadwin/qgis2web/test_data/polygon_single.qml")
        self.dialog = MainDialog(IFACE)
        self.dialog.leaflet.click()

    def test15_Leaflet_json_pnt_categorized(self):
        """Leaflet JSON point categorized (test_qgis2web_dialog.test_Leaflet_json_pnt_categorized)."""
        layer = QgsVectorLayer("/home/travis/build/tomchadwin/qgis2web/test_data/point.shp", "point feature", "ogr")
        if not layer:
            print "Layer failed to load!"
        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)
        layer.loadNamedStyle("/home/travis/build/tomchadwin/qgis2web/test_data/point_categorized.qml")
        testFile = open('/home/travis/build/tomchadwin/qgis2web/test_data/leaflet_json_point_single.html', 'r')
        goodOutput = testFile.read()
        self.dialog = MainDialog(IFACE)
        self.dialog.leaflet.click()

    def test16_Leaflet_wfs_pnt_categorized(self):
        """Leaflet WFS point categorized (test_qgis2web_dialog.test_Leaflet_wfs_pnt_categorized)."""
        layer = QgsVectorLayer("http://maps.nationalparks.gov.uk/geoserver/wfs?SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME=dartmoor:dnpa-tpo-point&SRSNAME=EPSG:27700", "pointfeature", "WFS")
        if not layer:
            print "Layer failed to load!"
        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)
        layer.loadNamedStyle("/home/travis/build/tomchadwin/qgis2web/test_data/point_categorized.qml")
        testFile = open('/home/travis/build/tomchadwin/qgis2web/test_data/leaflet_json_point_single.html', 'r')
        goodOutput = testFile.read()
        self.dialog = MainDialog(IFACE)
        self.dialog.leaflet.click()

    def test17_Leaflet_json_line_categorized(self):
        """Leaflet JSON line categorized (test_qgis2web_dialog.test_Leaflet_json_line_categorized)."""
        layer = QgsVectorLayer("/home/travis/build/tomchadwin/qgis2web/test_data/line.shp", "line feature", "ogr")
        if not layer:
            print "Layer failed to load!"
        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)
        layer.loadNamedStyle("/home/travis/build/tomchadwin/qgis2web/test_data/line_categorized.qml")
        testFile = open('/home/travis/build/tomchadwin/qgis2web/test_data/leaflet_json_point_single.html', 'r')
        goodOutput = testFile.read()
        self.dialog = MainDialog(IFACE)
        self.dialog.leaflet.click()

    def test18_Leaflet_wfs_line_categorized(self):
        """Leaflet WFS line categorized (test_qgis2web_dialog.test_Leaflet_wfs_line_categorized)."""
        layer = QgsVectorLayer("http://maps.nationalparks.gov.uk/geoserver/wfs?SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME=yorkshire_dales:ydnpa_route_accessibility&SRSNAME=EPSG:27700", "linefeature", "WFS")
        if not layer:
            print "Layer failed to load!"
        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)
        layer.loadNamedStyle("/home/travis/build/tomchadwin/qgis2web/test_data/line_categorized.qml")
        testFile = open('/home/travis/build/tomchadwin/qgis2web/test_data/leaflet_json_point_single.html', 'r')
        goodOutput = testFile.read()
        self.dialog = MainDialog(IFACE)
        self.dialog.leaflet.click()

    def test19_Leaflet_json_poly_categorized(self):
        """Leaflet JSON polygon categorized (test_qgis2web_dialog.test_Leaflet_json_poly_categorized)."""
        layer = QgsVectorLayer("/home/travis/build/tomchadwin/qgis2web/test_data/polygon.shp", "polygon feature", "ogr")
        if not layer:
            print "Layer failed to load!"
        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)
        layer.loadNamedStyle("/home/travis/build/tomchadwin/qgis2web/test_data/polygon_categorized.qml")
        testFile = open('/home/travis/build/tomchadwin/qgis2web/test_data/leaflet_json_point_single.html', 'r')
        goodOutput = testFile.read()
        self.dialog = MainDialog(IFACE)
        self.dialog.leaflet.click()

    def test20_Leaflet_wfs_poly_categorized(self):
        """Leaflet WFS polygon categorized (test_qgis2web_dialog.test_Leaflet_wfs_poly_categorized)."""
        layer = QgsVectorLayer("http://maps.nationalparks.gov.uk/geoserver/wfs?SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME=yorkshire_dales:ydnpa_conservationareas&SRSNAME=EPSG:27700", "polygonfeature", "WFS")
        if not layer:
            print "Layer failed to load!"
        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)
        layer.loadNamedStyle("/home/travis/build/tomchadwin/qgis2web/test_data/polygon_categorized.qml")
        testFile = open('/home/travis/build/tomchadwin/qgis2web/test_data/leaflet_json_point_single.html', 'r')
        goodOutput = testFile.read()
        self.dialog = MainDialog(IFACE)
        self.dialog.leaflet.click()

    def test21_Leaflet_json_pnt_graduated(self):
        """Leaflet JSON point graduated (test_qgis2web_dialog.test_Leaflet_json_pnt_graduated)."""
        layer = QgsVectorLayer("/home/travis/build/tomchadwin/qgis2web/test_data/point.shp", "point feature", "ogr")
        if not layer:
            print "Layer failed to load!"
        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)
        layer.loadNamedStyle("/home/travis/build/tomchadwin/qgis2web/test_data/point_graduated.qml")
        testFile = open('/home/travis/build/tomchadwin/qgis2web/test_data/leaflet_json_point_single.html', 'r')
        goodOutput = testFile.read()
        self.dialog = MainDialog(IFACE)
        self.dialog.leaflet.click()

    def test22_Leaflet_wfs_pnt_graduated(self):
        """Leaflet WFS point graduated (test_qgis2web_dialog.test_Leaflet_wfs_pnt_graduated)."""
        layer = QgsVectorLayer("http://maps.nationalparks.gov.uk/geoserver/wfs?SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME=dartmoor:dnpa-tpo-point&SRSNAME=EPSG:27700", "pointfeature", "WFS")
        if not layer:
            print "Layer failed to load!"
        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)
        layer.loadNamedStyle("/home/travis/build/tomchadwin/qgis2web/test_data/point_graduated.qml")
        testFile = open('/home/travis/build/tomchadwin/qgis2web/test_data/leaflet_json_point_single.html', 'r')
        goodOutput = testFile.read()
        self.dialog = MainDialog(IFACE)
        self.dialog.leaflet.click()

    def test23_Leaflet_json_line_graduated(self):
        """Leaflet JSON line graduated (test_qgis2web_dialog.test_Leaflet_json_line_graduated)."""
        layer = QgsVectorLayer("/home/travis/build/tomchadwin/qgis2web/test_data/line.shp", "line feature", "ogr")
        if not layer:
            print "Layer failed to load!"
        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)
        layer.loadNamedStyle("/home/travis/build/tomchadwin/qgis2web/test_data/line_graduated.qml")
        testFile = open('/home/travis/build/tomchadwin/qgis2web/test_data/leaflet_json_point_single.html', 'r')
        goodOutput = testFile.read()
        self.dialog = MainDialog(IFACE)
        self.dialog.leaflet.click()

    def test24_Leaflet_wfs_line_graduated(self):
        """Leaflet WFS line graduated (test_qgis2web_dialog.test_Leaflet_wfs_line_graduated)."""
        layer = QgsVectorLayer("http://maps.nationalparks.gov.uk/geoserver/wfs?SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME=yorkshire_dales:ydnpa_route_accessibility&SRSNAME=EPSG:27700", "linefeature", "WFS")
        if not layer:
            print "Layer failed to load!"
        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)
        layer.loadNamedStyle("/home/travis/build/tomchadwin/qgis2web/test_data/line_graduated.qml")
        testFile = open('/home/travis/build/tomchadwin/qgis2web/test_data/leaflet_json_point_single.html', 'r')
        goodOutput = testFile.read()
        self.dialog = MainDialog(IFACE)
        self.dialog.leaflet.click()

    def test25_Leaflet_json_poly_graduated(self):
        """Leaflet JSON polygon graduated (test_qgis2web_dialog.test_Leaflet_json_poly_graduated)."""
        layer = QgsVectorLayer("/home/travis/build/tomchadwin/qgis2web/test_data/polygon.shp", "polygon feature", "ogr")
        if not layer:
            print "Layer failed to load!"
        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)
        layer.loadNamedStyle("/home/travis/build/tomchadwin/qgis2web/test_data/polygon_graduated.qml")
        testFile = open('/home/travis/build/tomchadwin/qgis2web/test_data/leaflet_json_point_single.html', 'r')
        goodOutput = testFile.read()
        self.dialog = MainDialog(IFACE)
        self.dialog.leaflet.click()

    def test26_Leaflet_wfs_poly_graduated(self):
        """Leaflet WFS polygon graduated (test_qgis2web_dialog.test_Leaflet_wfs_poly_graduated)."""
        layer = QgsVectorLayer("http://maps.nationalparks.gov.uk/geoserver/wfs?SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME=yorkshire_dales:ydnpa_conservationareas&SRSNAME=EPSG:27700", "polygonfeature", "WFS")
        if not layer:
            print "Layer failed to load!"
        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)
        layer.loadNamedStyle("/home/travis/build/tomchadwin/qgis2web/test_data/polygon_graduated.qml")
        testFile = open('/home/travis/build/tomchadwin/qgis2web/test_data/leaflet_json_point_single.html', 'r')
        goodOutput = testFile.read()
        self.dialog = MainDialog(IFACE)
        self.dialog.leaflet.click()

    def test27_OL3_pnt_single(self):
        """OL3 point single (test_qgis2web_dialog.test_OL3_pnt_single)."""
        layer = QgsVectorLayer("/home/travis/build/tomchadwin/qgis2web/test_data/point.shp", "point feature", "ogr")
        if not layer:
            print "Layer failed to load!"
        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)
        layer.loadNamedStyle("/home/travis/build/tomchadwin/qgis2web/test_data/point_single.qml")
        testFile = open('/home/travis/build/tomchadwin/qgis2web/test_data/leaflet_json_point_single.html', 'r')
        goodOutput = testFile.read()
        self.dialog = MainDialog(IFACE)
        self.dialog.ol3.click()

    def test28_OL3_line_single(self):
        """OL3 line single (test_qgis2web_dialog.test_OL3_line_single)."""
        layer = QgsVectorLayer("/home/travis/build/tomchadwin/qgis2web/test_data/line.shp", "line feature", "ogr")
        if not layer:
            print "Layer failed to load!"
        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)
        layer.loadNamedStyle("/home/travis/build/tomchadwin/qgis2web/test_data/line_single.qml")
        self.dialog = MainDialog(IFACE)
        self.dialog.ol3.click()

    def test29_OL3_poly_single(self):
        """OL3 polygon single (test_qgis2web_dialog.test_OL3_poly_single)."""
        layer = QgsVectorLayer("/home/travis/build/tomchadwin/qgis2web/test_data/polygon.shp", "polygon feature", "ogr")
        if not layer:
            print "Layer failed to load!"
        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)
        layer.loadNamedStyle("/home/travis/build/tomchadwin/qgis2web/test_data/polygon_single.qml")
        self.dialog = MainDialog(IFACE)
        self.dialog.ol3.click()

    def test30_OL3_pnt_categorized(self):
        """OL3 point categorized (test_qgis2web_dialog.test_OL3_pnt_categorized)."""
        layer = QgsVectorLayer("/home/travis/build/tomchadwin/qgis2web/test_data/point.shp", "point feature", "ogr")
        if not layer:
            print "Layer failed to load!"
        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)
        layer.loadNamedStyle("/home/travis/build/tomchadwin/qgis2web/test_data/point_categorized.qml")
        testFile = open('/home/travis/build/tomchadwin/qgis2web/test_data/leaflet_json_point_single.html', 'r')
        goodOutput = testFile.read()
        self.dialog = MainDialog(IFACE)
        self.dialog.ol3.click()

    def test31_OL3_line_categorized(self):
        """OL3 line categorized (test_qgis2web_dialog.test_OL3_line_categorized)."""
        layer = QgsVectorLayer("/home/travis/build/tomchadwin/qgis2web/test_data/line.shp", "line feature", "ogr")
        if not layer:
            print "Layer failed to load!"
        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)
        layer.loadNamedStyle("/home/travis/build/tomchadwin/qgis2web/test_data/line_categorized.qml")
        testFile = open('/home/travis/build/tomchadwin/qgis2web/test_data/leaflet_json_point_single.html', 'r')
        goodOutput = testFile.read()
        self.dialog = MainDialog(IFACE)
        self.dialog.ol3.click()

    def test32_OL3_poly_categorized(self):
        """OL3 polygon categorized (test_qgis2web_dialog.test_OL3_poly_categorized)."""
        layer = QgsVectorLayer("/home/travis/build/tomchadwin/qgis2web/test_data/polygon.shp", "polygon feature", "ogr")
        if not layer:
            print "Layer failed to load!"
        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)
        layer.loadNamedStyle("/home/travis/build/tomchadwin/qgis2web/test_data/polygon_categorized.qml")
        testFile = open('/home/travis/build/tomchadwin/qgis2web/test_data/leaflet_json_point_single.html', 'r')
        goodOutput = testFile.read()
        self.dialog = MainDialog(IFACE)
        self.dialog.ol3.click()

    def test33_OL3_pnt_graduated(self):
        """OL3 point graduated (test_qgis2web_dialog.test_OL3_pnt_graduated)."""
        layer = QgsVectorLayer("/home/travis/build/tomchadwin/qgis2web/test_data/point.shp", "point feature", "ogr")
        if not layer:
            print "Layer failed to load!"
        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)
        layer.loadNamedStyle("/home/travis/build/tomchadwin/qgis2web/test_data/point_graduated.qml")
        testFile = open('/home/travis/build/tomchadwin/qgis2web/test_data/leaflet_json_point_single.html', 'r')
        goodOutput = testFile.read()
        self.dialog = MainDialog(IFACE)
        self.dialog.ol3.click()

    def test34_OL3_line_graduated(self):
        """OL3 line graduated (test_qgis2web_dialog.test_OL3_line_graduated)."""
        layer = QgsVectorLayer("/home/travis/build/tomchadwin/qgis2web/test_data/line.shp", "line feature", "ogr")
        if not layer:
            print "Layer failed to load!"
        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)
        layer.loadNamedStyle("/home/travis/build/tomchadwin/qgis2web/test_data/line_graduated.qml")
        testFile = open('/home/travis/build/tomchadwin/qgis2web/test_data/leaflet_json_point_single.html', 'r')
        goodOutput = testFile.read()
        self.dialog = MainDialog(IFACE)
        self.dialog.ol3.click()

    def test35_OL3_poly_graduated(self):
        """OL3 polygon graduated (test_qgis2web_dialog.test_OL3_poly_graduated)."""
        layer = QgsVectorLayer("/home/travis/build/tomchadwin/qgis2web/test_data/polygon.shp", "polygon feature", "ogr")
        if not layer:
            print "Layer failed to load!"
        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)
        layer.loadNamedStyle("/home/travis/build/tomchadwin/qgis2web/test_data/polygon_graduated.qml")
        testFile = open('/home/travis/build/tomchadwin/qgis2web/test_data/leaflet_json_point_single.html', 'r')
        goodOutput = testFile.read()
        self.dialog = MainDialog(IFACE)
        self.dialog.ol3.click()

if __name__ == "__main__":
    suite = unittest.makeSuite(qgis2web_classDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

