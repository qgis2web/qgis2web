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
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry
from PyQt4 import QtCore, QtTest
from PyQt4.QtCore import *
from PyQt4.QtGui import QDialogButtonBox, QDialog

from maindialog import MainDialog
from utilities import get_qgis_app, test_data_path, load_layer, load_wfs_layer

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class qgis2web_classDialogTest(unittest.TestCase):
    """Test most common plugin actions"""

    def setUp(self):
        """Runs before each test"""
        self.dialog = MainDialog(IFACE)
        self.dialog.paramsTreeOL.itemWidget(self.dialog.paramsTreeOL.findItems("Template",
                                                (Qt.MatchExactly |
                                                 Qt.MatchRecursive))[0], 1).setCurrentIndex(1)

    def tearDown(self):
        """Runs after each test"""
        registry = QgsMapLayerRegistry.instance()
        registry.removeAllMapLayers()
        self.dialog = MainDialog(IFACE)
        self.dialog.ol3.click()
        self.dialog = None

    def test01_preview_default(self):
        """Preview default - no data (OL3) (test_qgis2web_dialog.test_preview_default)"""
        self.dialog = MainDialog(IFACE)
        self.dialog.buttonPreview.click()

#    def test02_save_default(self):
#        """Save default - no data (OL3) (test_qgis2web_dialog.test_save_default)"""
#        self.dialog = MainDialog(IFACE)
#        self.dialog.buttonExport.click()

    def test03_toggle_Leaflet(self):
        """Toggle to Leaflet (test_qgis2web_dialog.test_toggle_Leaflet)"""
        self.dialog = MainDialog(IFACE)
        self.dialog.leaflet.click()

    def test04_preview_Leaflet(self):
        """Preview Leaflet - no data (test_qgis2web_dialog.test_preview_Leaflet)"""
        self.dialog = MainDialog(IFACE)
        self.dialog.leaflet.click()
        self.dialog.buttonPreview.click()

#    def test05_export_Leaflet(self):
#        """Export Leaflet - no data (test_qgis2web_dialog.test_export_Leaflet)"""
#        self.dialog = MainDialog(IFACE)
#        self.dialog.leaflet.click()
#        self.dialog.buttonExport.click()

    def test06_toggle_OL3(self):
        """Toggle to OL3 (test_qgis2web_dialog.test_toggle_OL3)"""
        self.dialog = MainDialog(IFACE)
        self.dialog.ol3.click()

    def test07_preview_OL3(self):
        """Preview OL3 - no data (test_qgis2web_dialog.test_preview_OL3)"""
        self.dialog = MainDialog(IFACE)
        self.dialog.ol3.click()
        self.dialog.buttonPreview.click()

#    def test08_export_OL3(self):
#        """Export OL3 - no data (test_qgis2web_dialog.test_export_OL3)"""
#        self.dialog = MainDialog(IFACE)
#        self.dialog.ol3.click()
#        self.dialog.buttonExport.click()

    def test09_Leaflet_json_pnt_single(self):
        """Leaflet JSON point single (test_qgis2web_dialog.test_Leaflet_json_pnt_single)"""
        layer_path = test_data_path('layer', 'point.shp')
        style_path = test_data_path('style', 'point_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)

        control_file = open(
                test_data_path(
                        'control', 'leaflet_json_point_single.html'), 'r')
        control_output = control_file.read()

        # Export to web map
        self.dialog = MainDialog(IFACE)
        self.dialog.paramsTreeOL.itemWidget(
                self.dialog.paramsTreeOL.findItems(
                        'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.dialog.leaflet.click()

        # Open the test file
        test_file = open(
                self.dialog.preview.url().toString().replace('file://', ''))
        test_output = test_file.read()

        # Compare with control file
        self.assertEqual(test_output, control_output)

    def test10_Leaflet_wfs_pnt_single(self):
        """Leaflet WFS point single (test_qgis2web_dialog.test_Leaflet_wfs_pnt_single)"""
        layer_url = ('http://maps.nationalparks.gov.uk/geoserver/wfs?SERVICE'
                     '=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME=dartmoor'
                     ':dnpa-tpo-point&SRSNAME=EPSG:27700')
        layer_style = test_data_path('style', 'point_single.qml')
        layer = load_wfs_layer(layer_url, 'point')
        layer.loadNamedStyle(layer_style)

        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)

        control_file = open(
                test_data_path('control', 'leaflet_wfs_point_single.html'), 'r')
        control_output = control_file.read()

        self.dialog = MainDialog(IFACE)
        self.dialog.paramsTreeOL.itemWidget(
                self.dialog.paramsTreeOL.findItems(
                        'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.dialog.leaflet.click()

        test_file = open(
                self.dialog.preview.url().toString().replace('file://', ''))
        test_output = test_file.read()
        self.assertEqual(test_output, control_output)

    def test11_Leaflet_json_line_single(self):
        """Leaflet JSON line single (test_qgis2web_dialog.test_Leaflet_json_line_single)"""
        layer_path = test_data_path('layer', 'line.shp')
        style_path = test_data_path('style', 'line_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)

        control_file = open(
                test_data_path('control', 'leaflet_json_line_single.html'), 'r')
        control_output = control_file.read()

        self.dialog = MainDialog(IFACE)
        self.dialog.paramsTreeOL.itemWidget(
                self.dialog.paramsTreeOL.findItems(
                        'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.dialog.leaflet.click()

        test_file = open(
                self.dialog.preview.url().toString().replace('file://', ''))
        test_output = test_file.read()
        self.assertEqual(test_output, control_output)

    def test12_Leaflet_wfs_line_single(self):
        """Leaflet WFS line single (test_qgis2web_dialog.test_Leaflet_wfs_line_single)"""
        layer_url = ('http://maps.nationalparks.gov.uk/geoserver/wfs?SERVICE'
                     '=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME'
                     '=yorkshire_dales:ydnpa_route_accessibility&SRSNAME=EPSG'
                     ':27700')
        layer_style = test_data_path('style', 'line_single.qml')
        layer = load_wfs_layer(layer_url, 'line')
        layer.loadNamedStyle(layer_style)

        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)

        control_file = open(
                test_data_path('control', 'leaflet_wfs_line_single.html'), 'r')
        control_output = control_file.read()
        self.dialog = MainDialog(IFACE)
        self.dialog.paramsTreeOL.itemWidget(
                self.dialog.paramsTreeOL.findItems(
                        'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.dialog.leaflet.click()
        test_file = open(
                self.dialog.preview.url().toString().replace('file://', ''))
        test_output = test_file.read()
        self.assertEqual(test_output, control_output)

    def test13_Leaflet_json_poly_single(self):
        """Leaflet JSON polygon single (test_qgis2web_dialog.test_Leaflet_json_poly_single)"""
        layer_path = test_data_path('layer', 'polygon.shp')
        style_path = test_data_path('style', 'polygon_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)

        control_file = open(
                test_data_path(
                        'control', 'leaflet_json_polygon_single.html'), 'r')
        control_output = control_file.read()
        self.dialog = MainDialog(IFACE)
        self.dialog.paramsTreeOL.itemWidget(
                self.dialog.paramsTreeOL.findItems(
                        'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.dialog.leaflet.click()

        test_file = open(
                self.dialog.preview.url().toString().replace('file://', ''))
        test_output = test_file.read()
        self.assertEqual(test_output, control_output)

    def test14_Leaflet_wfs_poly_single(self):
        """Leaflet WFS polygon single (test_qgis2web_dialog.test_Leaflet_wfs_poly_single)"""
        layer_url = ('http://maps.nationalparks.gov.uk/geoserver/wfs?SERVICE'
                     '=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME'
                     '=yorkshire_dales:ydnpa_conservationareas&SRSNAME=EPSG'
                     ':27700')
        layer_style = test_data_path('style', 'polygon_single.qml')
        control_path = test_data_path(
                'control', 'leaflet_wfs_polygon_single.html')
        layer = load_wfs_layer(layer_url, 'polygon')
        layer.loadNamedStyle(layer_style)

        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()

        self.dialog = MainDialog(IFACE)
        self.dialog.paramsTreeOL.itemWidget(
                self.dialog.paramsTreeOL.findItems(
                        'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.dialog.leaflet.click()

        test_file = open(
                self.dialog.preview.url().toString().replace('file://', ''))
        test_output = test_file.read()
        self.assertEqual(test_output, control_output)

    def test15_Leaflet_json_pnt_categorized(self):
        """Leaflet JSON point categorized (test_qgis2web_dialog.test_Leaflet_json_pnt_categorized)"""
        layer_path = test_data_path('layer', 'point.shp')
        style_path = test_data_path('style', 'json_point_categorized.qml')
        control_path = test_data_path(
                'control', 'leaflet_json_point_categorized.html')

        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()

        self.dialog = MainDialog(IFACE)
        self.dialog.paramsTreeOL.itemWidget(
                self.dialog.paramsTreeOL.findItems(
                        'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.dialog.leaflet.click()

        test_file = open(self.dialog.preview.url().toString().replace("file://",""))
        test_output = test_file.read()
        self.assertEqual(test_output, control_output)

    def test16_Leaflet_wfs_pnt_categorized(self):
        """Leaflet WFS point categorized (test_qgis2web_dialog.test_Leaflet_wfs_pnt_categorized)"""
        layer_url = ('http://maps.nationalparks.gov.uk/geoserver/wfs?SERVICE'
                     '=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME=dartmoor'
                     ':dnpa-tpo-point&SRSNAME=EPSG:27700')
        layer_style = test_data_path('style', 'wfs_point_categorized.qml')
        control_path = test_data_path(
                'control', 'leaflet_wfs_point_categorized.html')
        layer = load_wfs_layer(layer_url, 'point')
        layer.loadNamedStyle(layer_style)

        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()
        self.dialog = MainDialog(IFACE)
        self.dialog.paramsTreeOL.itemWidget(
                self.dialog.paramsTreeOL.findItems(
                        'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.dialog.leaflet.click()
        test_file = open(self.dialog.preview.url().toString().replace("file://",""))
        test_output = test_file.read()
        self.assertEqual(test_output, control_output)

    def test17_Leaflet_json_line_categorized(self):
        """Leaflet JSON line categorized (test_qgis2web_dialog.test_Leaflet_json_line_categorized)"""
        layer_path = test_data_path('layer', 'line.shp')
        style_path = test_data_path('style', 'json_line_categorized.qml')
        control_path = test_data_path(
                'control', 'leaflet_json_line_categorized.html')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()

        self.dialog = MainDialog(IFACE)
        self.dialog.paramsTreeOL.itemWidget(
                self.dialog.paramsTreeOL.findItems(
                        'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.dialog.leaflet.click()
        test_file = open(
                self.dialog.preview.url().toString().replace('file://', ''))
        test_output = test_file.read()
        self.assertEqual(test_output, control_output)

    def test18_Leaflet_wfs_line_categorized(self):
        """Leaflet WFS line categorized (test_qgis2web_dialog.test_Leaflet_wfs_line_categorized)"""
        layer_url = ('http://maps.nationalparks.gov.uk/geoserver/wfs?SERVICE'
                     '=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME'
                     '=yorkshire_dales:ydnpa_route_accessibility&SRSNAME=EPSG'
                     ':27700')
        layer_style = test_data_path('style', 'wfs_line_categorized.qml')
        control_path = test_data_path(
                'control', 'leaflet_wfs_line_categorized.html')
        layer = load_wfs_layer(layer_url, 'line')
        layer.loadNamedStyle(layer_style)

        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()
        self.dialog = MainDialog(IFACE)
        self.dialog.paramsTreeOL.itemWidget(
                self.dialog.paramsTreeOL.findItems(
                        'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.dialog.leaflet.click()

        test_file = open(
                self.dialog.preview.url().toString().replace('file://', ''))
        test_output = test_file.read()
        self.assertEqual(test_output, control_output)

    def test19_Leaflet_json_poly_categorized(self):
        """Leaflet JSON polygon categorized (test_qgis2web_dialog.test_Leaflet_json_poly_categorized)"""
        layer_path = test_data_path('layer', 'polygon.shp')
        style_path = test_data_path('style', 'json_polygon_categorized.qml')
        control_path = test_data_path(
                'control', 'leaflet_json_polygon_categorized.html')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()

        self.dialog = MainDialog(IFACE)
        self.dialog.paramsTreeOL.itemWidget(
                self.dialog.paramsTreeOL.findItems(
                        'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.dialog.leaflet.click()

        test_file = open(
                self.dialog.preview.url().toString().replace('file://', ''))
        test_output = test_file.read()
        self.assertEqual(test_output, control_output)

    def test20_Leaflet_wfs_poly_categorized(self):
        """Leaflet WFS polygon categorized (test_qgis2web_dialog.test_Leaflet_wfs_poly_categorized)"""
        layer_url = ('http://maps.nationalparks.gov.uk/geoserver/wfs?SERVICE'
                     '=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME'
                     '=yorkshire_dales:ydnpa_conservationareas&SRSNAME=EPSG'
                     ':27700')
        layer_style = test_data_path('style', 'wfs_polygon_categorized.qml')
        control_path = test_data_path(
                'control', 'leaflet_wfs_polygon_categorized.html')
        layer = load_wfs_layer(layer_url, 'polygon')
        layer.loadNamedStyle(layer_style)

        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()

        self.dialog = MainDialog(IFACE)
        self.dialog.paramsTreeOL.itemWidget(
                self.dialog.paramsTreeOL.findItems(
                        'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.dialog.leaflet.click()
        test_file = open(
                self.dialog.preview.url().toString().replace('file://', ''))
        test_output = test_file.read()
        self.assertEqual(test_output, control_output)

    def test21_Leaflet_json_pnt_graduated(self):
        """Leaflet JSON point graduated (test_qgis2web_dialog.test_Leaflet_json_pnt_graduated)"""
        layer_path = test_data_path('layer', 'point.shp')
        style_path = test_data_path('style', 'json_point_graduated.qml')
        control_path = test_data_path(
                'control', 'leaflet_json_point_graduated.html')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()

        self.dialog = MainDialog(IFACE)
        self.dialog.paramsTreeOL.itemWidget(
                self.dialog.paramsTreeOL.findItems(
                        'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.dialog.leaflet.click()

        test_file = open(
                self.dialog.preview.url().toString().replace('file://', ''))
        test_output = test_file.read()
        self.assertEqual(test_output, control_output)

    def test22_Leaflet_wfs_pnt_graduated(self):
        """Leaflet WFS point graduated (test_qgis2web_dialog.test_Leaflet_wfs_pnt_graduated)"""
        layer_url = ('http://maps.nationalparks.gov.uk/geoserver/wfs?SERVICE'
                     '=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME=dartmoor'
                     ':dnpa-tpo-point&SRSNAME=EPSG:27700')
        layer_style = test_data_path('style', 'wfs_point_graduated.qml')
        control_path = test_data_path(
                'control', 'leaflet_wfs_point_graduated.html')
        layer = load_wfs_layer(layer_url, 'point')
        layer.loadNamedStyle(layer_style)

        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()

        self.dialog = MainDialog(IFACE)
        self.dialog.paramsTreeOL.itemWidget(
                self.dialog.paramsTreeOL.findItems(
                        'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.dialog.leaflet.click()

        test_file = open(
                self.dialog.preview.url().toString().replace('file://', ''))
        test_output = test_file.read()
        self.assertEqual(test_output, control_output)

    def test23_Leaflet_json_line_graduated(self):
        """Leaflet JSON line graduated (test_qgis2web_dialog.test_Leaflet_json_line_graduated)"""
        layer_path = test_data_path('layer', 'line.shp')
        layer_style = test_data_path('style', 'json_line_graduated.qml')
        control_path = test_data_path(
                'control', 'leaflet_json_line_graduated.html')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(layer_style)

        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()

        self.dialog = MainDialog(IFACE)
        self.dialog.paramsTreeOL.itemWidget(
                self.dialog.paramsTreeOL.findItems(
                        'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.dialog.leaflet.click()

        test_file = open(self.dialog.preview.url().toString().replace(
                "file://",""))
        test_output = test_file.read()
        self.assertEqual(test_output, control_output)

    def test24_Leaflet_wfs_line_graduated(self):
        """Leaflet WFS line graduated (test_qgis2web_dialog.test_Leaflet_wfs_line_graduated)"""
        layer_url = ('http://maps.nationalparks.gov.uk/geoserver/wfs?SERVICE'
                     '=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME'
                     '=yorkshire_dales:ydnpa_route_accessibility&SRSNAME=EPSG'
                     ':27700')
        layer_style = test_data_path('style', 'wfs_line_graduated.qml')
        control_path = test_data_path(
                'control', 'leaflet_wfs_line_graduated.html')
        layer = load_wfs_layer(layer_url, 'line')
        layer.loadNamedStyle(layer_style)

        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()

        self.dialog = MainDialog(IFACE)
        self.dialog.paramsTreeOL.itemWidget(
                self.dialog.paramsTreeOL.findItems(
                        'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.dialog.leaflet.click()

        test_file = open(self.dialog.preview.url().toString().replace(
                "file://", ""))
        test_output = test_file.read()
        self.assertEqual(test_output, control_output)

    def test25_Leaflet_json_poly_graduated(self):
        """Leaflet JSON polygon graduated (test_qgis2web_dialog.test_Leaflet_json_poly_graduated)"""
        layer_path = test_data_path('layer', 'polygon.shp')
        layer_style = test_data_path('style', 'json_polygon_graduated.qml')
        control_path = test_data_path(
                'control', 'leaflet_json_polygon_graduated.html')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(layer_style)

        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()

        self.dialog = MainDialog(IFACE)
        self.dialog.paramsTreeOL.itemWidget(
                self.dialog.paramsTreeOL.findItems(
                        'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.dialog.leaflet.click()

        test_file = open(self.dialog.preview.url().toString().replace(
                "file://", ""))
        test_output = test_file.read()
        self.assertEqual(test_output, control_output)

    def test26_Leaflet_wfs_poly_graduated(self):
        """Leaflet WFS polygon graduated (test_qgis2web_dialog.test_Leaflet_wfs_poly_graduated)"""
        layer_url = ('http://maps.nationalparks.gov.uk/geoserver/wfs?SERVICE'
                     '=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME'
                     '=yorkshire_dales:ydnpa_conservationareas&SRSNAME=EPSG'
                     ':27700')
        layer_style = test_data_path('style', 'wfs_polygon_graduated.qml')
        control_path = test_data_path(
                'control', 'leaflet_wfs_polygon_graduated.html')
        layer = load_wfs_layer(layer_url, 'polygon')
        layer.loadNamedStyle(layer_style)

        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()

        self.dialog = MainDialog(IFACE)
        self.dialog.paramsTreeOL.itemWidget(
                self.dialog.paramsTreeOL.findItems(
                        'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.dialog.leaflet.click()

        test_file = open(self.dialog.preview.url().toString().replace(
                "file://", ""))
        test_output = test_file.read()
        self.assertEqual(test_output, control_output)

    def test27_OL3_pnt_single(self):
        """OL3 point single (test_qgis2web_dialog.test_OL3_pnt_single)"""
        layer_path = test_data_path('layer', 'point.shp')
        style_path = test_data_path('style', 'point_single.qml')
        control_path = test_data_path(
                'control', 'ol3_json_point_single.html')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()

        self.dialog = MainDialog(IFACE)
        self.dialog.paramsTreeOL.itemWidget(
                self.dialog.paramsTreeOL.findItems(
                        'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.dialog.ol3.click()

        test_file = open(
                self.dialog.preview.url().toString().replace('file://', ''))
        test_output = test_file.read()

        test_style_file = open(
                self.dialog.preview.url().toString().replace(
                        'file://', '').replace(
                        'index.html', 'styles/point_style.js'))
        test_style_output = test_style_file.read()
        test_output += test_style_output
        self.assertEqual(test_output, control_output)

    def test28_OL3_line_single(self):
        """OL3 line single (test_qgis2web_dialog.test_OL3_line_single)"""
        layer_path = test_data_path('layer', 'line.shp')
        style_path = test_data_path('style', 'line_single.qml')
        control_path = test_data_path(
                'control', 'ol3_json_line_single.html')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()

        self.dialog = MainDialog(IFACE)
        self.dialog.paramsTreeOL.itemWidget(
                self.dialog.paramsTreeOL.findItems(
                        'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.dialog.ol3.click()

        test_file = open(
                self.dialog.preview.url().toString().replace('file://', ''))
        test_output = test_file.read()

        test_style_file = open(
                self.dialog.preview.url().toString().replace(
                        'file://', '').replace(
                        'index.html', 'styles/line_style.js'))
        test_style_output = test_style_file.read()
        test_output += test_style_output
        self.assertEqual(test_output, control_output)

    def test29_OL3_poly_single(self):
        """OL3 polygon single (test_qgis2web_dialog.test_OL3_poly_single)"""
        layer_path = test_data_path('layer', 'polygon.shp')
        style_path = test_data_path('style', 'polygon_single.qml')
        control_path = test_data_path(
                'control', 'ol3_json_polygon_single.html')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()

        self.dialog = MainDialog(IFACE)
        self.dialog.paramsTreeOL.itemWidget(self.dialog.paramsTreeOL.findItems("Extent",
                                                (Qt.MatchExactly |
                                                 Qt.MatchRecursive))[0], 1).setCurrentIndex(1)
        self.dialog.ol3.click()

        test_file = open(
                self.dialog.preview.url().toString().replace('file://', ''))
        test_output = test_file.read()

        test_style_file = open(
                self.dialog.preview.url().toString().replace(
                        'file://', '').replace(
                        'index.html', 'styles/polygon_style.js'))
        test_style_output = test_style_file.read()
        test_output += test_style_output
        self.assertEqual(test_output, control_output)

    def test30_OL3_pnt_categorized(self):
        """OL3 point categorized (test_qgis2web_dialog.test_OL3_pnt_categorized)"""
        layer_path = test_data_path('layer', 'point.shp')
        style_path = test_data_path('style', 'json_point_categorized.qml')
        control_path = test_data_path(
                'control', 'ol3_json_point_categorized.html')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()

        self.dialog = MainDialog(IFACE)
        self.dialog.paramsTreeOL.itemWidget(
                self.dialog.paramsTreeOL.findItems(
                        "Extent", (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.dialog.ol3.click()

        test_file = open(
                self.dialog.preview.url().toString().replace('file://', ''))
        test_output = test_file.read()

        test_style_file = open(
                self.dialog.preview.url().toString().replace(
                        'file://', '').replace(
                        'index.html', 'styles/point_style.js'))
        test_style_output = test_style_file.read()
        test_output += test_style_output
        self.assertEqual(test_output, control_output)

    def test31_OL3_line_categorized(self):
        """OL3 line categorized (test_qgis2web_dialog.test_OL3_line_categorized)"""
        layer_path = test_data_path('layer', 'line.shp')
        style_path = test_data_path('style', 'json_line_categorized.qml')
        control_path = test_data_path(
                'control', 'ol3_json_line_categorized.html')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()

        self.dialog = MainDialog(IFACE)
        self.dialog.paramsTreeOL.itemWidget(self.dialog.paramsTreeOL.findItems("Extent",
                                                (Qt.MatchExactly |
                                                 Qt.MatchRecursive))[0], 1).setCurrentIndex(1)
        self.dialog.ol3.click()

        test_file = open(
                self.dialog.preview.url().toString().replace('file://', ''))
        test_output = test_file.read()

        test_style_file = open(
                self.dialog.preview.url().toString().replace(
                        'file://', '').replace(
                        'index.html', 'styles/line_style.js'))
        test_style_output = test_style_file.read()
        test_output += test_style_output
        self.assertEqual(test_output, control_output)

    def test32_OL3_poly_categorized(self):
        """OL3 polygon categorized (test_qgis2web_dialog.test_OL3_poly_categorized)"""
        layer_path = test_data_path('layer', 'polygon.shp')
        style_path = test_data_path('style', 'json_polygon_categorized.qml')
        control_path = test_data_path(
                'control', 'ol3_json_polygon_categorized.html')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()

        self.dialog = MainDialog(IFACE)
        self.dialog.paramsTreeOL.itemWidget(self.dialog.paramsTreeOL.findItems("Extent",
                                                (Qt.MatchExactly |
                                                 Qt.MatchRecursive))[0], 1).setCurrentIndex(1)
        self.dialog.ol3.click()

        test_file = open(
                self.dialog.preview.url().toString().replace('file://', ''))
        test_output = test_file.read()

        test_style_file = open(
                self.dialog.preview.url().toString().replace(
                        'file://', '').replace(
                        'index.html', 'styles/polygon_style.js'))
        test_style_output = test_style_file.read()
        test_output += test_style_output
        self.assertEqual(test_output, control_output)

    def test33_OL3_pnt_graduated(self):
        """OL3 point graduated (test_qgis2web_dialog.test_OL3_pnt_graduated)"""
        layer_path = test_data_path('layer', 'point.shp')
        style_path = test_data_path('style', 'json_point_graduated.qml')
        control_path = test_data_path(
                'control', 'ol3_json_point_graduated.html')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()

        self.dialog = MainDialog(IFACE)
        self.dialog.paramsTreeOL.itemWidget(self.dialog.paramsTreeOL.findItems("Extent",
                                                (Qt.MatchExactly |
                                                 Qt.MatchRecursive))[0], 1).setCurrentIndex(1)
        self.dialog.ol3.click()

        test_file = open(
                self.dialog.preview.url().toString().replace('file://', ''))
        test_output = test_file.read()

        test_style_file = open(
                self.dialog.preview.url().toString().replace(
                        'file://', '').replace(
                        'index.html', 'styles/point_style.js'))
        test_style_output = test_style_file.read()
        test_output += test_style_output
        self.assertEqual(test_output, control_output)

    def test34_OL3_line_graduated(self):
        """OL3 line graduated (test_qgis2web_dialog.test_OL3_line_graduated)"""
        layer_path = test_data_path('layer', 'line.shp')
        style_path = test_data_path('style', 'json_line_graduated.qml')
        control_path = test_data_path(
                'control', 'ol3_json_line_graduated.html')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()

        self.dialog = MainDialog(IFACE)
        self.dialog.paramsTreeOL.itemWidget(self.dialog.paramsTreeOL.findItems("Extent",
                                                (Qt.MatchExactly |
                                                 Qt.MatchRecursive))[0], 1).setCurrentIndex(1)
        self.dialog.ol3.click()

        test_file = open(
                self.dialog.preview.url().toString().replace('file://', ''))
        test_output = test_file.read()

        test_style_file = open(
                self.dialog.preview.url().toString().replace(
                        'file://', '').replace(
                        'index.html', 'styles/line_style.js'))
        test_style_output = test_style_file.read()
        test_output += test_style_output
        self.assertEqual(test_output, control_output)

    def test35_OL3_poly_graduated(self):
        """OL3 polygon graduated (test_qgis2web_dialog.test_OL3_poly_graduated)"""
        layer_path = test_data_path('layer', 'polygon.shp')
        style_path = test_data_path('style', 'json_polygon_graduated.qml')
        control_path = test_data_path(
                'control', 'ol3_json_polygon_graduated.html')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        registry = QgsMapLayerRegistry.instance()
        registry.addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()

        self.dialog = MainDialog(IFACE)
        self.dialog.paramsTreeOL.itemWidget(self.dialog.paramsTreeOL.findItems("Extent",
                                                (Qt.MatchExactly |
                                                 Qt.MatchRecursive))[0], 1).setCurrentIndex(1)
        self.dialog.ol3.click()

        test_file = open(
                self.dialog.preview.url().toString().replace('file://', ''))
        test_output = test_file.read()

        test_style_file = open(
                self.dialog.preview.url().toString().replace(
                        'file://', '').replace(
                        'index.html', 'styles/polygon_style.js'))
        test_style_output = test_style_file.read()
        test_output += test_style_output
        self.assertEqual(test_output, control_output)

if __name__ == "__main__":
    suite = unittest.makeSuite(qgis2web_classDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

