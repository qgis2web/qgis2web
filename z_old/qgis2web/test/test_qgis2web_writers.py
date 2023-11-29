# coding=utf-8
"""Writers test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'riccardo.klinger@geolicious.de'
__date__ = '2015-03-26'
__copyright__ = 'Copyright 2015, Riccardo Klinger / Geolicious'

import os
import difflib
from collections import OrderedDict

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
from qgis.core import QgsProject, QgsCoordinateReferenceSystem
from qgis2web.olwriter import OpenLayersWriter
from qgis2web.leafletWriter import LeafletWriter
from qgis2web.utils import tempFolder

from osgeo import gdal
from qgis2web.test.utilities import get_test_data_path, load_layer
from qgis.testing import unittest, start_app
from qgis.testing.mocked import get_iface

print("test_qgis2web_writers")
start_app()


def GDAL_COMPUTE_VERSION(maj, min, rev):
    return maj * 1000000 + min * 10000 + rev * 100


def isLtrRepo():
    """
    Returns true if using the LTR repository
    """
    return 'QGIS_REPO' in os.environ and os.environ["QGIS_REPO"] == "http://qgis.org/debian-ltr"


class qgis2web_WriterTest(unittest.TestCase):

    """Test writers"""
    maxDiff = None

    def setUp(self):
        """Runs before each test"""
        QgsProject.instance().writeEntryBool("ScaleBar", "/Enabled", False)
        self.iface = get_iface()

    def tearDown(self):
        """Runs after each test"""
        QgsProject.instance().removeAllMapLayers()

    def defaultParams(self):
        return {'Data export': {'Minify GeoJSON files': True,
                                'Exporter': 'Export to folder',
                                'Precision': 'maintain'},
                'Scale/Zoom': {'Min zoom level': '1',
                               'Restrict to extent': False,
                               'Extent': 'Fit to layers extent',
                               'Max zoom level': '28'},
                'Appearance': {
                'Add address search': False,
                'Geolocate user': False,
                'Base layer': [],
                'Search layer': None,
                'Add layers list': 'None',
                'Attribute filter': [],
                'Add abstract': 'None',
                'Measure tool': 'None',
                'Match project CRS': False,
                'Template': 'full-screen',
                'Widget Background': '#000000',
                'Widget Icon': '#ffffff',
                'Layer search': 'None',
                'Highlight on hover': False,
                'Show popups on hover': False
        }}

    def test01_LeafletWriterResults(self):
        """ Test writer results from a leaflet writer"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        layer = load_layer(layer_path)
        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [('ID', 'no label'), ('fk_region', 'no label'), ('ELEV', 'no label'), ('NAME', 'no label'),
             ('USE', 'no label')])]
        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder())
        self.assertTrue(result.index_file)
        self.assertTrue(len(result.files) > 1)
        self.assertTrue(result.folder)

    def test02_OpenLayersWriterResults(self):
        """ Test writer results from a OL writer"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        layer = load_layer(layer_path)
        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        writer = OpenLayersWriter()
        writer.params = self.defaultParams()
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [('ID', 'no label'), ('fk_region', 'no label'), ('ELEV', 'no label'), ('NAME', 'no label'),
             ('USE', 'no label')])]
        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder())
        self.assertTrue(result.index_file)
        self.assertTrue(len(result.files) > 1)
        self.assertTrue(result.folder)

    def test09_Leaflet_json_pnt_single(self):
        """Leaflet JSON point single"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')

        layer = load_layer(layer_path)

        _, _ = layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(
            get_test_data_path('control', 'leaflet_json_point_single.html'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [('ID', 'no label'), ('fk_region', 'no label'), ('ELEV', 'no label'), ('NAME', 'no label'),
             ('USE', 'no label')])]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        # Open the test file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        # Compare with control file
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    # def test10_Leaflet_wfs_pnt_single(self):
        # """Leaflet WFS point single"""
        # layer_url = (
        #     'http://balleter.nationalparks.gov.uk/geoserver/wfs?SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME=dnpa_inspire:tpo_points&SRSNAME=EPSG:27700&BBOX=233720,53549,297567,96689')
        # layer_style = get_test_data_path('style', 'point_single.qml')
        # layer = load_wfs_layer(layer_url, 'point')
        # layer.loadNamedStyle(layer_style)

        # QgsProject.instance().addMapLayer(layer)

        # control_file = open(
        #     get_test_data_path('control', 'leaflet_wfs_point_single.html'), 'r')
        # control_output = control_file.read()
        # control_file.close()

        # # Export to web map
        # writer = LeafletWriter()
        # writer.params = self.defaultParams()
        # writer.groups = {}
        # writer.layers = [layer]
        # writer.visible = [True]
        # writer.cluster = [False]
        # writer.popup = [OrderedDict([(u'ref', u'no label'), (u'tpo_name', u'no label'), (u'area_ha', u'no label'), (u'digitised', u'no label'), (u'objtype', u'no label')])
        #                 ]
        # writer.json = [False]

        # result = writer.write(self.iface, tempFolder()).index_file

        # # Open the test file
        # test_file = open(result)
        # test_output = test_file.read()
        # test_file.close()

        # self.assertEqual(
        #     test_output, control_output, diff(control_output, test_output))

    def test11_Leaflet_json_line_single(self):
        """Leaflet JSON line single"""
        layer_path = get_test_data_path('layer', 'pipelines.shp')
        style_path = get_test_data_path('style', 'pipelines_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(
            get_test_data_path('control', 'leaflet_json_line_single.html'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict([(u'cat', u'no label'), (u'LOCDESC', u'no label'), (u'F_CODE', u'no label'), (u'F_CODEDESC', u'no label')])
                        ]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    # def test12_Leaflet_wfs_line_single(self):
        # """Leaflet WFS line single"""
        # layer_url = ('http://balleter.nationalparks.gov.uk/geoserver/wfs?'
        #              'SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME'
        #              '=broads_inspire:centreline&SRSNAME=EPSG:27700')
        # layer_style = get_test_data_path('style', 'line_single.qml')
        # layer = load_wfs_layer(layer_url, 'centreline')
        # layer.loadNamedStyle(layer_style)

        # QgsProject.instance().addMapLayer(layer)

        # control_file = open(
        #     get_test_data_path('control', 'leaflet_wfs_line_single.html'), 'r')
        # control_output = control_file.read()
        # control_file.close()

        # # Export to web map
        # writer = LeafletWriter()
        # writer.params = self.defaultParams()
        # writer.groups = {}
        # writer.layers = [layer]
        # writer.visible = [True]
        # writer.cluster = [False]
        # writer.popup = [OrderedDict([(u'objecttype', u'no label'), (u'name', u'no label'), (u'navigable', u'no label'), (u'responsibleparty', u'no label'), (u'broad', u'no label'), (u'from_', u'no label'), (u'to_', u'no label'), (u'reachid', u'no label'), (u'globalid', u'no label'), (u'route', u'no label'), (u'shape_stlength__', u'no label')])
        #                 ]
        # writer.json = [False]

        # result = writer.write(self.iface, tempFolder()).index_file
        # test_file = open(result)
        # test_output = test_file.read()
        # test_file.close()

        # self.assertEqual(
        #     test_output, control_output, diff(control_output, test_output))

    def test13_Leaflet_json_poly_single(self):
        """Leaflet JSON polygon single"""
        layer_path = get_test_data_path('layer', 'lakes.shp')
        style_path = get_test_data_path('style', 'lakes_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(
            get_test_data_path('control', 'leaflet_json_polygon_single.html'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict([(u'cat', u'no label'), (u'NAMES', u'no label'), (u'AREA_MI', u'no label'), (u'xlabel', u'no label'), (u'ylabel', u'no label'), (u'rotation', u'no label')])
                        ]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    # def test14_Leaflet_wfs_poly_single(self):
        # """Leaflet WFS polygon single"""
        # layer_url = ('http://balleter.nationalparks.gov.uk/geoserver/wfs?'
        #              'SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME'
        #              '=dnpa_inspire:con_areas&SRSNAME=EPSG:27700')
        # layer_style = get_test_data_path('style', 'polygon_single.qml')
        # control_path = get_test_data_path(
        #     'control', 'leaflet_wfs_polygon_single.html')
        # layer = load_wfs_layer(layer_url, 'polygon')
        # layer.loadNamedStyle(layer_style)

        # QgsProject.instance().addMapLayer(layer)

        # control_file = open(control_path, 'r')
        # control_output = control_file.read()
        # control_file.close()

        # # Export to web map
        # writer = LeafletWriter()
        # writer.params = self.defaultParams()
        # writer.groups = {}
        # writer.layers = [layer]
        # writer.visible = [True]
        # writer.cluster = [False]
        # writer.popup = [OrderedDict([(u'name', u'no label'), (u'details', u'no label'), (u'date', u'no label'), (u'area_ha', u'no label'), (u'web_page', u'no label')])
        #                 ]
        # writer.json = [False]

        # result = writer.write(self.iface, tempFolder()).index_file
        # test_file = open(result)
        # test_output = test_file.read()
        # test_file.close()

        # self.assertEqual(
        #     test_output, control_output, diff(control_output, test_output))

    def test15_Leaflet_json_pnt_categorized(self):
        """Leaflet JSON point categorized"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_categorized.qml')
        control_path = get_test_data_path(
            'control', 'leaflet_json_point_categorized.html')

        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [('ID', 'no label'), ('fk_region', 'no label'), ('ELEV', 'no label'), ('NAME', 'no label'),
             ('USE', 'no label')])]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    # def test16_Leaflet_wfs_pnt_categorized(self):
        # """Leaflet WFS point categorized"""
        # layer_url = (
        #     'http://balleter.nationalparks.gov.uk/geoserver/wfs?SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME=dnpa_inspire:tpo_points&SRSNAME=EPSG:27700&BBOX=233720,53549,297567,96689')
        # layer_style = get_test_data_path('style', 'wfs_point_categorized.qml')
        # control_path = get_test_data_path(
        #     'control', 'leaflet_wfs_point_categorized.html')
        # layer = load_wfs_layer(layer_url, 'point')
        # layer.loadNamedStyle(layer_style)

        # QgsProject.instance().addMapLayer(layer)

        # control_file = open(control_path, 'r')
        # control_output = control_file.read()
        # control_file.close()

        # # Export to web map
        # writer = LeafletWriter()
        # writer.params = self.defaultParams()
        # writer.groups = {}
        # writer.layers = [layer]
        # writer.visible = [True]
        # writer.cluster = [False]
        # writer.popup = [OrderedDict([(u'ref', u'no label'), (u'tpo_name', u'no label'), (u'area_ha', u'no label'), (u'digitised', u'no label'), (u'objtype', u'no label')])
        #                 ]
        # writer.json = [False]

        # result = writer.write(self.iface, tempFolder()).index_file
        # test_file = open(result)
        # test_output = test_file.read()
        # test_file.close()

        # self.assertEqual(
        #     test_output, control_output, diff(control_output, test_output))

    def test17_Leaflet_json_line_categorized(self):
        """Leaflet JSON line categorized"""
        layer_path = get_test_data_path('layer', 'pipelines.shp')
        style_path = get_test_data_path('style', 'pipelines_categorized.qml')
        control_path = get_test_data_path(
            'control', 'leaflet_json_line_categorized.html')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'cat', u'no label'), (u'LOCDESC', u'no label'), (u'F_CODE', u'no label'),
             (u'F_CODEDESC', u'no label')])]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test19_Leaflet_json_poly_categorized(self):
        """Leaflet JSON polygon categorized"""
        layer_path = get_test_data_path('layer', 'lakes.shp')
        style_path = get_test_data_path('style', 'lakes_categorized.qml')
        control_path = get_test_data_path(
            'control', 'leaflet_json_polygon_categorized.html')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'cat', u'no label'), (u'NAMES', u'no label'), (u'AREA_MI', u'no label'),
             (u'xlabel', u'no label'), (u'ylabel', u'no label'), (u'rotation', u'no label')])]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    # def test20_Leaflet_wfs_poly_categorized(self):
        # """Leaflet WFS polygon categorized"""
        # layer_url = ('http://balleter.nationalparks.gov.uk/geoserver/wfs?'
        #              'SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME'
        #              '=dnpa_inspire:con_areas&SRSNAME=EPSG:27700')
        # layer_style = get_test_data_path('style', 'wfs_polygon_categorized.qml')
        # control_path = get_test_data_path(
        #     'control', 'leaflet_wfs_polygon_categorized.html')
        # layer = load_wfs_layer(layer_url, 'polygon')
        # layer.loadNamedStyle(layer_style)

        # QgsProject.instance().addMapLayer(layer)

        # control_file = open(control_path, 'r')
        # control_output = control_file.read()
        # control_file.close()

        # # Export to web map
        # writer = LeafletWriter()
        # writer.params = self.defaultParams()
        # writer.groups = {}
        # writer.layers = [layer]
        # writer.visible = [True]
        # writer.cluster = [False]
        # writer.popup = [OrderedDict([(u'name', u'no label'), (u'details', u'no label'), (
        #     u'date', u'no label'), (u'area_ha', u'no label'), (u'web_page', u'no label')])]
        # writer.json = [False]

        # result = writer.write(self.iface, tempFolder()).index_file
        # test_file = open(result)
        # test_output = test_file.read()
        # test_file.close()

        # self.assertEqual(
        #     test_output, control_output, diff(control_output, test_output))

    def test21_Leaflet_json_pnt_graduated(self):
        """Leaflet JSON point graduated"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_graduated.qml')
        control_path = get_test_data_path(
            'control', 'leaflet_json_point_graduated.html')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
             (u'NAME', u'no label'), (u'USE', u'no label')])]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    # def test22_Leaflet_wfs_pnt_graduated(self):
        # """Leaflet WFS point graduated"""
        # layer_url = (
        #     'http://balleter.nationalparks.gov.uk/geoserver/wfs?SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME=dnpa_inspire:tpo_points&SRSNAME=EPSG:27700&BBOX=233720,53549,297567,96689')
        # layer_style = get_test_data_path('style', 'wfs_point_graduated.qml')
        # control_path = get_test_data_path(
        #     'control', 'leaflet_wfs_point_graduated.html')
        # layer = load_wfs_layer(layer_url, 'point')
        # layer.loadNamedStyle(layer_style)

        # QgsProject.instance().addMapLayer(layer)

        # control_file = open(control_path, 'r')
        # control_output = control_file.read()
        # control_file.close()

        # # Export to web map
        # writer = LeafletWriter()
        # writer.params = self.defaultParams()
        # writer.groups = {}
        # writer.layers = [layer]
        # writer.visible = [True]
        # writer.cluster = [False]
        # writer.popup = [OrderedDict([(u'ref', u'no label'), (u'tpo_name', u'no label'), (u'area_ha', u'no label'), (u'digitised', u'no label'), (u'objtype', u'no label')])
        #                 ]
        # writer.json = [False]

        # result = writer.write(self.iface, tempFolder()).index_file
        # test_file = open(result)
        # test_output = test_file.read()
        # test_file.close()

        # self.assertEqual(
        #     test_output, control_output, diff(control_output, test_output))

    def test23_Leaflet_json_line_graduated(self):
        """Leaflet JSON line graduated"""
        layer_path = get_test_data_path('layer', 'pipelines.shp')
        layer_style = get_test_data_path('style', 'pipelines_graduated.qml')
        control_path = get_test_data_path(
            'control', 'leaflet_json_line_graduated.html')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(layer_style)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [
            OrderedDict([(u'cat', u'no label'), (u'LOCDESC', u'no label'), (u'F_CODE', u'no label'), (u'F_CODEDESC', u'no label')])]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    # def test24_Leaflet_wfs_line_graduated(self):
        # """Leaflet WFS line graduated"""
        # layer_url = ('http://balleter.nationalparks.gov.uk/geoserver/wfs?'
        #              'SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME'
        #              '=broads_inspire:centreline&SRSNAME=EPSG:27700')
        # layer_style = get_test_data_path('style', 'wfs_line_graduated.qml')
        # control_path = get_test_data_path(
        #     'control', 'leaflet_wfs_line_graduated.html')
        # layer = load_wfs_layer(layer_url, 'centreline')
        # layer.loadNamedStyle(layer_style)

        # QgsProject.instance().addMapLayer(layer)

        # control_file = open(control_path, 'r')
        # control_output = control_file.read()
        # control_file.close()

        # # Export to web map
        # writer = LeafletWriter()
        # writer.params = self.defaultParams()
        # writer.groups = {}
        # writer.layers = [layer]
        # writer.visible = [True]
        # writer.cluster = [False]
        # writer.popup = [OrderedDict([(u'objecttype', u'no label'), (u'name', u'no label'), (u'navigable', u'no label'), (u'responsibleparty', u'no label'), (u'broad', u'no label'), (u'from_', u'no label'), (u'to_', u'no label'), (u'reachid', u'no label'), (u'globalid', u'no label'), (u'route', u'no label'), (u'shape_stlength__', u'no label')])
        #                 ]
        # writer.json = [False]

        # result = writer.write(self.iface, tempFolder()).index_file
        # test_file = open(result)
        # test_output = test_file.read()
        # test_file.close()

        # self.assertEqual(
        #     test_output, control_output, diff(control_output, test_output))

    def test25_Leaflet_json_poly_graduated(self):
        """Leaflet JSON polygon graduated"""
        layer_path = get_test_data_path('layer', 'lakes.shp')
        layer_style = get_test_data_path('style', 'lakes_graduated.qml')
        control_path = get_test_data_path(
            'control', 'leaflet_json_polygon_graduated.html')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(layer_style)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'cat', u'no label'), (u'NAMES', u'no label'), (u'AREA_MI', u'no label'),
             (u'xlabel', u'no label'), (u'ylabel', u'no label'), (u'rotation', u'no label')])]

        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    # def test26_Leaflet_wfs_poly_graduated(self):
        # """Leaflet WFS polygon graduated"""
        # layer_url = ('http://balleter.nationalparks.gov.uk/geoserver/wfs?'
        #              'SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME'
        #              '=dnpa_inspire:con_areas&SRSNAME=EPSG:27700')
        # layer_style = get_test_data_path('style', 'wfs_polygon_graduated.qml')
        # control_path = get_test_data_path(
        #     'control', 'leaflet_wfs_polygon_graduated.html')
        # layer = load_wfs_layer(layer_url, 'polygon')
        # layer.loadNamedStyle(layer_style)

        # QgsProject.instance().addMapLayer(layer)

        # control_file = open(control_path, 'r')
        # control_output = control_file.read()
        # control_file.close()

        # # Export to web map
        # writer = LeafletWriter()
        # writer.params = self.defaultParams()
        # writer.groups = {}
        # writer.layers = [layer]
        # writer.visible = [True]
        # writer.cluster = [False]
        # writer.popup = [OrderedDict(
        #     [(u'name', u'no label'), (u'details', u'no label'), (u'date', u'no label'),
        #      (u'area_ha', u'no label'), (u'web_page', u'no label')])
        # ]
        # writer.json = [False]

        # result = writer.write(self.iface, tempFolder()).index_file
        # test_file = open(result)
        # test_output = test_file.read()
        # test_file.close()
        # self.assertEqual(
        #     test_output, control_output, diff(control_output, test_output))

    def test27_OL3_pnt_single(self):
        """OL3 point single"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        control_path = get_test_data_path(
            'control', 'ol3_json_point_single.html')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = OpenLayersWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict([(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'), (u'NAME', u'no label'), (u'USE', u'no label')])
                        ]
        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder()).index_file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        test_style_file = open(
            result.replace(
                'file://', '').replace(
                    'index.html', 'styles/airports_0_style.js'))
        test_style_output = test_style_file.read()
        test_style_file.close()
        test_output += test_style_output

        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test28_OL3_line_single(self):
        """OL3 line single"""
        layer_path = get_test_data_path('layer', 'pipelines.shp')
        style_path = get_test_data_path('style', 'pipelines_single.qml')
        control_path = get_test_data_path(
            'control', 'ol3_json_line_single.html')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = OpenLayersWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'cat', u'no label'), (u'LOCDESC', u'no label'), (u'F_CODE', u'no label'),
             (u'F_CODEDESC', u'no label')])]
        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder()).index_file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        test_style_file = open(
            result.replace(
                'file://', '').replace(
                    'index.html', 'styles/pipelines_0_style.js'))
        test_style_output = test_style_file.read()
        test_style_file.close()
        test_output += test_style_output

        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test29_OL3_poly_single(self):
        """OL3 polygon single"""
        layer_path = get_test_data_path('layer', 'lakes.shp')
        style_path = get_test_data_path('style', 'lakes_single.qml')
        control_path = get_test_data_path(
            'control', 'ol3_json_polygon_single.html')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = OpenLayersWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'cat', u'no label'), (u'NAMES', u'no label'), (u'AREA_MI', u'no label'),
             (u'xlabel', u'no label'), (u'ylabel', u'no label'), (u'rotation', u'no label')])]

        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder()).index_file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        test_style_file = open(
            result.replace(
                'file://', '').replace(
                    'index.html', 'styles/lakes_0_style.js'))
        test_style_output = test_style_file.read()
        test_style_file.close()
        test_output += test_style_output

        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test30_OL3_pnt_categorized(self):
        """OL3 point categorized"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_categorized.qml')
        control_path = get_test_data_path(
            'control', 'ol3_json_point_categorized.html')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = OpenLayersWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
             (u'NAME', u'no label'), (u'USE', u'no label')])]

        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder()).index_file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        test_style_file = open(
            result.replace(
                'file://', '').replace(
                    'index.html', 'styles/airports_0_style.js'))
        test_style_output = test_style_file.read()
        test_style_file.close()
        test_output += test_style_output

        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test31_OL3_line_categorized(self):
        """OL3 line categorized"""
        layer_path = get_test_data_path('layer', 'pipelines.shp')
        style_path = get_test_data_path('style', 'pipelines_categorized.qml')
        control_path = get_test_data_path(
            'control', 'ol3_json_line_categorized.html')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = OpenLayersWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'cat', u'no label'), (u'LOCDESC', u'no label'), (u'F_CODE', u'no label'),
             (u'F_CODEDESC', u'no label')])]

        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder()).index_file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        test_style_file = open(
            result.replace(
                'index.html', 'styles/pipelines_0_style.js'))
        test_style_output = test_style_file.read()
        test_style_file.close()
        test_output += test_style_output

        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test32_OL3_poly_categorized(self):
        """OL3 polygon categorized"""
        layer_path = get_test_data_path('layer', 'lakes.shp')
        style_path = get_test_data_path('style', 'lakes_categorized.qml')
        control_path = get_test_data_path(
            'control', 'ol3_json_polygon_categorized.html')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = OpenLayersWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'cat', u'no label'), (u'NAMES', u'no label'), (u'AREA_MI', u'no label'),
             (u'xlabel', u'no label'), (u'ylabel', u'no label'), (u'rotation', u'no label')])]

        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder()).index_file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        test_style_file = open(result.replace(
            'index.html', 'styles/lakes_0_style.js'))
        test_style_output = test_style_file.read()
        test_style_file.close()
        test_output += test_style_output

        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test33_OL3_pnt_graduated(self):
        """OL3 point graduated"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_graduated.qml')
        control_path = get_test_data_path(
            'control', 'ol3_json_point_graduated.html')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = OpenLayersWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
             (u'NAME', u'no label'), (u'USE', u'no label')])]

        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder()).index_file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        test_style_file = open(result.replace(
            'index.html', 'styles/airports_0_style.js'))
        test_style_output = test_style_file.read()
        test_style_file.close()
        test_output += test_style_output

        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test34_OL3_line_graduated(self):
        """OL3 line graduated"""
        layer_path = get_test_data_path('layer', 'pipelines.shp')
        style_path = get_test_data_path('style', 'pipelines_graduated.qml')
        control_path = get_test_data_path(
            'control', 'ol3_json_line_graduated.html')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = OpenLayersWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'cat', u'no label'), (u'LOCDESC', u'no label'), (u'F_CODE', u'no label'),
             (u'F_CODEDESC', u'no label')])]

        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder()).index_file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        test_style_file = open(result.replace(
            'index.html', 'styles/pipelines_0_style.js'))
        test_style_output = test_style_file.read()
        test_style_file.close()
        test_output += test_style_output

        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test35_OL3_poly_graduated(self):
        """OL3 polygon graduated"""
        layer_path = get_test_data_path('layer', 'lakes.shp')
        style_path = get_test_data_path('style', 'lakes_graduated.qml')
        control_path = get_test_data_path(
            'control', 'ol3_json_polygon_graduated.html')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = OpenLayersWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'cat', u'no label'), (u'NAMES', u'no label'), (u'AREA_MI', u'no label'),
             (u'xlabel', u'no label'), (u'ylabel', u'no label'), (u'rotation', u'no label')])]

        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder()).index_file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        test_style_file = open(result.replace(
            'index.html', 'styles/lakes_0_style.js'))
        test_style_output = test_style_file.read()
        test_style_file.close()
        test_output += test_style_output

        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test36_OL3_layer_list(self):
        """OL3 A layer list is present when selected"""

        layer_path = get_test_data_path('layer', 'airports.shp')
        layer = load_layer(layer_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        writer = OpenLayersWriter()
        writer.params = self.defaultParams()
        writer.params['Appearance']['Add layers list'] = 'Collapsed'
        writer.params['Appearance']['Template'] = 'canvas-size'
        writer.params['Scale/Zoom']['Extent'] = 'Canvas extent'
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict([(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'), (u'NAME', u'no label'), (u'USE', u'no label')])
                        ]
        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder()).index_file
        test_qgis2web_output = read_output(result, 'resources/qgis2web.js')
        assert 'new ol.control.LayerSwitcher' in test_qgis2web_output

        test_layers_output = read_output(result, 'layers/layers.js')
        assert """title: '<img src="styles/legend/airports_0.png" /> airports'""" in test_layers_output

    def test40_Leaflet_scalebar(self):
        """Leaflet scale bar"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(
            get_test_data_path(
                'control', 'leaflet_scalebar.html'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Check the 'Add scale bar' checkbox
        QgsProject.instance().writeEntryBool("ScaleBar", "/Enabled", True)

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
             (u'NAME', u'no label'), (u'USE', u'no label')])
        ]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        # Open the test file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        # Compare with control file

        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test41_OL3_scalebar(self):
        """OL3 scale bar"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(
            get_test_data_path(
                'control', 'ol3_scalebar.js'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Check the 'Add scale bar' checkbox
        QgsProject.instance().writeEntryBool("ScaleBar", "/Enabled", True)

        # Export to web map
        writer = OpenLayersWriter()
        writer.params = self.defaultParams()
        writer.params['Appearance']['Template'] = 'canvas-size'
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
             (u'NAME', u'no label'), (u'USE', u'no label')])
        ]
        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        # Reset scale bar setting
        QgsProject.instance().writeEntryBool("ScaleBar", "/Enabled", False)

        # Open the test file
        test_output = read_output(result, 'resources/qgis2web.js')

        # Compare with control file
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test42_Leaflet_measure(self):
        """Leaflet measure"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(
            get_test_data_path(
                'control', 'leaflet_measure.html'), 'r')
        control_output = control_file.read()
        control_file.close()
        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.params['Appearance']['Measure tool'] = 'Metric'
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
             (u'NAME', u'no label'), (u'USE', u'no label')])
        ]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        # Open the test file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        # Compare with control file
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test43_OL3_measure(self):
        """OL3 measure control"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        writer = OpenLayersWriter()
        writer.params = self.defaultParams()
        writer.params['Appearance']['Measure tool'] = 'Metric'
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
             (u'NAME', u'no label'), (u'USE', u'no label')])
        ]
        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        control_file = open(
            get_test_data_path(
                'control', 'ol3_measure.html'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Open the test file
        test_output = read_output(result, 'index.html')

        # Compare with control file
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

        control_file = open(
            get_test_data_path(
                'control', 'ol3_measure.js'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Open the test file
        test_output = read_output(result, 'resources/qgis2web.js')

        # Compare with control file
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test44_Leaflet_address(self):
        """Leaflet address search"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(
            get_test_data_path(
                'control', 'leaflet_address.html'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.params['Appearance']['Add address search'] = True
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
             (u'NAME', u'no label'), (u'USE', u'no label')])
        ]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        # Open the test file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        # Compare with control file
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test45_OL3_address(self):
        """OL3 address search"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        writer = OpenLayersWriter()
        writer.params = self.defaultParams()
        writer.params['Appearance']['Add address search'] = True
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
             (u'NAME', u'no label'), (u'USE', u'no label')])
        ]
        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        control_file = open(
            get_test_data_path(
                'control', 'ol3_address.html'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Open the test file
        test_output = read_output(result, 'index.html')

        # Compare with control file
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))
        control_file = open(
            get_test_data_path(
                'control', 'ol3_address.js'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Open the test file
        test_output = read_output(result, 'resources/qgis2web.js')

        # Compare with control file
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test46_Leaflet_geolocate(self):
        """Leaflet geolocate user"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(
            get_test_data_path(
                'control', 'leaflet_geolocate.html'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.params['Appearance']['Geolocate user'] = True
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
             (u'NAME', u'no label'), (u'USE', u'no label')])
        ]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        # Open the test file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        # Compare with control file
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test47_OL3_geolocate(self):
        """OL3 geolocate user"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        writer = OpenLayersWriter()
        writer.params = self.defaultParams()
        writer.params['Appearance']['Geolocate user'] = True
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
             (u'NAME', u'no label'), (u'USE', u'no label')])
        ]
        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        control_file = open(
            get_test_data_path(
                'control', 'ol3_geolocate.js'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Open the test file
        test_output = read_output(result, 'resources/qgis2web.js')

        # Compare with control file
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test48_Leaflet_highlight(self):
        """Leaflet highlight on hover"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(
            get_test_data_path(
                'control', 'leaflet_highlight.html'), 'r')
        control_output = control_file.read()
        control_file.close()
        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.params['Appearance']['Highlight on hover'] = True
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
             (u'NAME', u'no label'), (u'USE', u'no label')])
        ]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        # Open the test file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        # Compare with control file
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test49_OL3_highlight(self):
        """OL3 highlight on hover"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        writer = OpenLayersWriter()
        writer.params = self.defaultParams()
        writer.params['Appearance']['Highlight on hover'] = True
        writer.params['Appearance']['Template'] = 'canvas-size'
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
             (u'NAME', u'no label'), (u'USE', u'no label')])
        ]
        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        control_file = open(
            get_test_data_path(
                'control', 'ol3_highlight.js'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Open the test file
        test_output = read_output(result, 'resources/qgis2web.js')

        # Compare with control file
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test50_Leaflet_CRS(self):
        """Leaflet match CRS"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)
        crs = QgsCoordinateReferenceSystem("EPSG:2964")
        self.iface.mapCanvas().setDestinationCrs(crs)

        control_file = open(
            get_test_data_path(
                'control', 'leaflet_crs.html'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.params['Appearance']['Match project CRS'] = True
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
             (u'NAME', u'no label'), (u'USE', u'no label')])
        ]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        # Open the test file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        # Compare with control file
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test51_OL3_CRS(self):
        """OL3 match CRS"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)
        crs = QgsCoordinateReferenceSystem("EPSG:2964")
        self.iface.mapCanvas().setDestinationCrs(crs)

        # Export to web map
        writer = OpenLayersWriter()
        writer.params = self.defaultParams()
        writer.params['Appearance']['Match project CRS'] = True
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
             (u'NAME', u'no label'), (u'USE', u'no label')])
        ]
        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        control_file = open(
            get_test_data_path(
                'control', 'ol3_crs.html'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Open the test file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        # Compare with control file
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

        control_file = open(
            get_test_data_path(
                'control', 'ol3_crs.js'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Open the test file
        test_output = read_output(result, 'layers/layers.js')

        # Compare with control file
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test52_Leaflet_layerslist(self):
        """Leaflet add layers list"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(
            get_test_data_path(
                'control', 'leaflet_layerslist.html'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.params['Appearance']['Add layers list'] = 'Collapsed'
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
             (u'NAME', u'no label'), (u'USE', u'no label')])
        ]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        # Open the test file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        # Compare with control file
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test53_Leaflet_visible(self):
        """Leaflet visible"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(
            get_test_data_path(
                'control', 'leaflet_visible.html'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [False]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
             (u'NAME', u'no label'), (u'USE', u'no label')])
        ]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        # Open the test file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        # Compare with control file
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test54_OL3_visible(self):
        """OL3 visible"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        writer = OpenLayersWriter()
        writer.params = self.defaultParams()
        writer.params['Appearance']['Template'] = 'canvas-size'
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [False]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
             (u'NAME', u'no label'), (u'USE', u'no label')])
        ]
        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        control_file = open(
            get_test_data_path(
                'control', 'ol3_visible.js'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Open the test file
        test_output = read_output(result, 'layers/layers.js')

        # Compare with control file
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test55_Leaflet_cluster(self):
        """Leaflet cluster"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(
            get_test_data_path(
                'control', 'leaflet_cluster.html'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [True]
        writer.popup = [OrderedDict(
            [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
             (u'NAME', u'no label'), (u'USE', u'no label')])
        ]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        # Open the test file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        # Compare with control file
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test56_OL3_cluster(self):
        """OL3 cluster"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        writer = OpenLayersWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [True]
        writer.popup = [OrderedDict(
            [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
             (u'NAME', u'no label'), (u'USE', u'no label')])
        ]
        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        control_file = open(
            get_test_data_path(
                'control', 'ol3_cluster.js'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Open the test file
        test_output = read_output(result, 'layers/layers.js')

        # Compare with control file
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    @unittest.skipIf(int(gdal.VersionInfo('VERSION_NUM')) >= GDAL_COMPUTE_VERSION(2, 0, 0), 'Test requires updating for GDAL 2.0')
    def test62_leaflet_precision(self):
        """Leaflet precision"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.params['Appearance']['Template'] = 'canvas-size'
        writer.params['Data export']['Precision'] = '3'
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [True]
        writer.popup = [OrderedDict(
            [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
             (u'NAME', u'no label'), (u'USE', u'no label')])
        ]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        control_file = open(
            get_test_data_path(
                'control', 'leaflet_precision.js'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Open the test file
        test_output = read_output(result, 'data/airports_0.js')

        # Compare with control file
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    @unittest.skipIf(int(gdal.VersionInfo('VERSION_NUM')) >= GDAL_COMPUTE_VERSION(2, 0, 0), 'Test requires updating for GDAL 2.0')
    def test63_ol3_precision(self):
        """OL3 precision"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        writer = OpenLayersWriter()
        writer.params = self.defaultParams()
        writer.params['Appearance']['Template'] = 'canvas-size'
        writer.params['Data export']['Precision'] = '2'
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [True]
        writer.popup = [OrderedDict(
            [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
             (u'NAME', u'no label'), (u'USE', u'no label')])
        ]
        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        control_file = open(
            get_test_data_path(
                'control', 'ol3_precision.js'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Open the test file
        test_output = read_output(result, 'layers/airports_0.js')

        # Compare with control file
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    @unittest.skipIf(int(gdal.VersionInfo('VERSION_NUM')) >= GDAL_COMPUTE_VERSION(2, 0, 0), 'Test requires updating for GDAL 2.0')
    def test67_leaflet_minify(self):
        """Leaflet minify"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.params['Data export']['Precision'] = '6'
        writer.params['Data export']['Minify GeoJSON files'] = True
        writer.params['Appearance']['Template'] = 'canvas-size'
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
             (u'NAME', u'no label'), (u'USE', u'no label')])
        ]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        control_file = open(
            get_test_data_path(
                'control', 'leaflet_minify.js'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Open the test file
        test_output = read_output(result, 'data/airports_0.js')

        # Compare with control file
        self.assertEqual(test_output, control_output)

    @unittest.skipIf(int(gdal.VersionInfo('VERSION_NUM')) >= GDAL_COMPUTE_VERSION(2, 0, 0), 'Test requires updating for GDAL 2.0')
    def test68_ol3_minify(self):
        """OL3 minify"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        writer = OpenLayersWriter()
        writer.params = self.defaultParams()
        writer.params['Data export']['Precision'] = '2'
        writer.params['Data export']['Minify GeoJSON files'] = True
        writer.params['Appearance']['Template'] = 'canvas-size'
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
             (u'NAME', u'no label'), (u'USE', u'no label')])
        ]
        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        control_file = open(
            get_test_data_path(
                'control', 'ol3_minify.js'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Open the test file
        test_output = read_output(result, 'layers/airports_0.js')
        # Compare with control file
        self.assertEqual(test_output, control_output)

    def test69_Leaflet_canvasextent(self):
        """Leaflet canvas extent"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.params['Scale/Zoom']['Extent'] = 'Canvas extent'
        writer.params['Appearance']['Template'] = 'canvas-size'
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
             (u'NAME', u'no label'), (u'USE', u'no label')])
        ]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        # Open the test file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        # Test for expected output
        assert "}).fitBounds([[" in test_output

    def test70_Leaflet_maxzoom(self):
        """Leaflet max zoom"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.params['Scale/Zoom']['Max zoom level'] = '20'
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
             (u'NAME', u'no label'), (u'USE', u'no label')])
        ]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        control_file = open(
            get_test_data_path(
                'control', 'leaflet_maxzoom.html'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Open the test file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        # Test for expected output
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test71_ol3_maxzoom(self):
        """OL3 max zoom"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        writer = OpenLayersWriter()
        writer.params = self.defaultParams()
        writer.params['Scale/Zoom']['Max zoom level'] = '20'
        writer.params['Appearance']['Template'] = 'canvas-size'
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
             (u'NAME', u'no label'), (u'USE', u'no label')])
        ]
        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        control_file = open(
            get_test_data_path(
                'control', 'ol3_maxzoom.js'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Open the test file
        test_output = read_output(result, 'resources/qgis2web.js')

        # Compare with control file
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test72_Leaflet_minzoom(self):
        """Leaflet min zoom"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.params['Scale/Zoom']['Min zoom level'] = '6'
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
             (u'NAME', u'no label'), (u'USE', u'no label')])
        ]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        control_file = open(
            get_test_data_path(
                'control', 'leaflet_minzoom.html'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Open the test file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        # Test for expected output
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test73_ol3_minzoom(self):
        """OL3 min zoom"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        writer = OpenLayersWriter()
        writer.params = self.defaultParams()
        writer.params['Scale/Zoom']['Min zoom level'] = '6'
        writer.params['Appearance']['Template'] = 'canvas-size'
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
             (u'NAME', u'no label'), (u'USE', u'no label')])
        ]
        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        control_file = open(
            get_test_data_path(
                'control', 'ol3_minzoom.js'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Open the test file
        test_output = read_output(result, 'resources/qgis2web.js')

        # Compare with control file
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test74_Leaflet_restricttoextent(self):
        """Leaflet restrict to extent"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.params['Scale/Zoom']['Restrict to extent'] = True
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
             (u'NAME', u'no label'), (u'USE', u'no label')])
        ]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        control_file = open(
            get_test_data_path(
                'control', 'leaflet_restricttoextent.html'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Open the test file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        # Test for expected output
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test75_ol3_restricttoextent(self):
        """OL3 restrict to extent"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        writer = OpenLayersWriter()
        writer.params = self.defaultParams()
        writer.params['Scale/Zoom']['Restrict to extent'] = True
        writer.params['Appearance']['Template'] = 'canvas-size'
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
             (u'NAME', u'no label'), (u'USE', u'no label')])
        ]
        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        # Open the test file
        test_output = read_output(result, 'resources/qgis2web.js')

        # Test for expected output
        assert "extent: [" in test_output

    def test76_Leaflet_25d(self):
        """Leaflet 2.5d"""
        layer_path = get_test_data_path('layer', 'lakes.shp')
        style_path = get_test_data_path('style', '25d.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict([(u'cat', u'no label'), (u'NAMES', u'no label'), (u'AREA_MI', u'no label'), (u'xlabel', u'no label'), (u'ylabel', u'no label'), (u'rotation', u'no label')])
                        ]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        control_file = open(
            get_test_data_path(
                'control', 'leaflet_25d.html'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Open the test file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        # Test for expected output
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test77_OL3_25d(self):
        """OL3 2.5d"""
        layer_path = get_test_data_path('layer', 'lakes.shp')
        style_path = get_test_data_path('style', '25d.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        writer = OpenLayersWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'cat', u'no label'), (u'NAMES', u'no label'), (u'AREA_MI', u'no label'),
             (u'xlabel', u'no label'), (u'ylabel', u'no label'), (u'rotation', u'no label')])
        ]
        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        control_file = open(
            get_test_data_path(
                'control', 'ol3_25d.html'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Open the test file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        # Test for expected output
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test78_Leaflet_raster(self):
        """Leaflet raster"""
        layer_path = get_test_data_path('layer', 'test.png')
        # style_path = get_test_data_path('style', '25d.qml')
        layer = load_layer(layer_path)
        # layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict()]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        control_file = open(
            get_test_data_path(
                'control', 'leaflet_raster.html'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Open the test file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        # Test for expected output
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

        # test for exported raster file
        assert os.path.exists(result.replace('index.html', 'data/test_0.png'))

    def test79_OL3_raster(self):
        """OL3 raster"""
        layer_path = get_test_data_path('layer', 'test.png')
        # style_path = get_test_data_path('style', '25d.qml')
        layer = load_layer(layer_path)
        # layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        writer = OpenLayersWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict()]
        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        control_file = open(
            get_test_data_path(
                'control', 'ol3_raster.js'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Open the test file
        test_output = read_output(result, 'layers/layers.js')

        # Test for expected output
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

        # test for exported raster file
        assert os.path.exists(result.replace('index.html', 'layers/test_0.png'))

    def test80_OL3_heatmap(self):
        """OL3 heatmap"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'heatmap.qml')
        control_path = get_test_data_path(
            'control', 'ol3_heatmap.js')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = OpenLayersWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict([(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'), (u'NAME', u'no label'), (u'USE', u'no label')])
                        ]
        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        test_style_file = open(
            result.replace(
                'file://', '').replace(
                    'index.html', 'layers/layers.js'))
        test_style_output = test_style_file.read()
        test_style_file.close()
        test_output = test_style_output

        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test81_Leaflet_heatmap(self):
        """Leaflet heatmap"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'heatmap.qml')
        control_path = get_test_data_path(
            'control', 'leaflet_heatmap.html')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict([(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'), (u'NAME', u'no label'), (u'USE', u'no label')])
                        ]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    # def test83_OL3_WMS(self):
        # """OL3 WMS"""
        # layer_url = (
        #     'contextualWMSLegend=0&crs=EPSG:3857&dpiMode=all&featureCount=10&format=image/png&layers=GBR_BGS_625k_BLT&styles=&url=http://ogc.bgs.ac.uk/cgi-bin/BGS_Bedrock_and_Superficial_Geology/wms?')
        # layer = load_wms_layer(layer_url, 'wms')

        # QgsProject.instance().addMapLayer(layer)

        # control_file = open(
        #     get_test_data_path('control', 'ol3_wms.js'), 'r')
        # control_output = control_file.read()
        # control_file.close()

        # # Export to web map
        # writer = OpenLayersWriter()
        # writer.params = self.defaultParams()
        # writer.groups = {}
        # writer.layers = [layer]
        # writer.visible = [True]
        # writer.cluster = [False]
        # writer.popup = [OrderedDict([(u'ref', u'no label'), (u'tpo_name', u'no label'), (u'area_ha', u'no label'), (u'digitised', u'no label'), (u'objtype', u'no label')])
        #                 ]
        # writer.json = [False]
        # writer.getFeatureInfo = [False]

        # result = writer.write(self.iface, tempFolder()).index_file

        # # Open the test file
        # test_style_file = open(
        #     result.replace(
        #         'file://', '').replace(
        #             'index.html', 'layers/layers.js'))
        # test_style_output = test_style_file.read()
        # test_style_file.close()
        # test_output = test_style_output

        # self.assertEqual(
        #     test_output, control_output, diff(control_output, test_output))

    # def test84_Leaflet_WMS(self):
        # """Leaflet WMS"""
        # layer_url = (
        #     'contextualWMSLegend=0&crs=EPSG:3857&dpiMode=all&featureCount=10&format=image/png&layers=GBR_BGS_625k_BLT&styles=&url=http://ogc.bgs.ac.uk/cgi-bin/BGS_Bedrock_and_Superficial_Geology/wms?')
        # layer = load_wms_layer(layer_url, 'wms')

        # QgsProject.instance().addMapLayer(layer)

        # control_file = open(
        #     get_test_data_path('control', 'leaflet_wms.html'), 'r')
        # control_output = control_file.read()
        # control_file.close()

        #   Export to web map
        # writer = LeafletWriter()
        # writer.params = self.defaultParams()
        # writer.groups = {}
        # writer.layers = [layer]
        # writer.visible = [True]
        # writer.cluster = [False]
        # writer.popup = [OrderedDict([(u'ref', u'no label'), (u'tpo_name', u'no label'), (u'area_ha', u'no label'), (u'digitised', u'no label'), (u'objtype', u'no label')])
        #                 ]
        # writer.json = [False]
        # writer.getFeatureInfo = [False]

        # result = writer.write(self.iface, tempFolder()).index_file

        #   Open the test file
        # test_style_file = open(
        #     result.replace(
        #         'file://', ''))
        # test_style_output = test_style_file.read()
        # test_style_file.close()
        # test_output = test_style_output

        # self.assertEqual(
        #     test_output, control_output, diff(control_output, test_output))

    def test85_Leaflet_rulebased(self):
        """Leaflet rule-based"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_rule-based.qml')
        control_path = get_test_data_path(
            'control', 'leaflet_rule-based.html')

        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [('ID', 'no label'), ('fk_region', 'no label'), ('ELEV', 'no label'), ('NAME', 'no label'),
             ('USE', 'no label')])]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test86_OL3_rulebased(self):
        """OL3 rule-based"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_rule-based.qml')
        control_path = get_test_data_path(
            'control', 'ol3_rule-based.js')

        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = OpenLayersWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [('ID', 'no label'), ('fk_region', 'no label'), ('ELEV', 'no label'), ('NAME', 'no label'),
             ('USE', 'no label')])]
        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder()).index_file
        test_style_file = open(
            result.replace(
                'file://', '').replace(
                    'index.html', 'styles/airports_0_style.js'))
        test_style_output = test_style_file.read()
        test_style_file.close()
        test_output = test_style_output
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test87_Leaflet_labels(self):
        """Leaflet labels"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_labels.qml')
        control_path = get_test_data_path(
            'control', 'leaflet_labels.html')

        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [('ID', 'no label'), ('fk_region', 'no label'), ('ELEV', 'no label'), ('NAME', 'no label'),
             ('USE', 'no label')])]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test88_OL3_labels(self):
        """OL3 labels"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_labels.qml')
        control_path = get_test_data_path(
            'control', 'ol3_labels.js')

        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = OpenLayersWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [('ID', 'no label'), ('fk_region', 'no label'), ('ELEV', 'no label'), ('NAME', 'no label'),
             ('USE', 'no label')])]
        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder()).index_file
        test_style_file = open(
            result.replace(
                'file://', '').replace(
                    'index.html', 'styles/airports_0_style.js'))
        test_style_output = test_style_file.read()
        test_style_file.close()
        test_output = test_style_output
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    # def test89_OL3_WMTS(self):
        # """OL3 WMTS"""
        # layer_url = (
        #     'contextualWMSLegend=0&crs=EPSG:3857&dpiMode=7&featureCount=10&format=image/jpeg&layers=EMAP8&styles=default&tileMatrixSet=GoogleMapsCompatible&url=http://wmts.nlsc.gov.tw/wmts')
        # layer = load_wms_layer(layer_url, 'wms')

        # QgsProject.instance().addMapLayer(layer)

        # control_file = open(
        #     get_test_data_path('control', 'ol3_wmts.js'), 'r')
        # control_output = control_file.read()
        # control_file.close()

        #   Export to web map
        # writer = OpenLayersWriter()
        # writer.params = self.defaultParams()
        # writer.groups = {}
        # writer.layers = [layer]
        # writer.visible = [True]
        # writer.cluster = [False]
        # writer.popup = [OrderedDict([(u'ref', u'no label'), (u'tpo_name', u'no label'), (u'area_ha', u'no label'), (u'digitised', u'no label'), (u'objtype', u'no label')])
        #                 ]
        # writer.json = [False]
        # writer.getFeatureInfo = [False]

        # result = writer.write(self.iface, tempFolder()).index_file

        #   Open the test file
        # test_style_file = open(
        #     result.replace(
        #         'file://', '').replace(
        #             'index.html', 'layers/layers.js'))
        # test_style_output = test_style_file.read()
        # test_style_file.close()
        # test_output = test_style_output

        # self.assertEqual(
        #     test_output, control_output, diff(control_output, test_output))

    # def test90_Leaflet_WMTS(self):
        # """Leaflet WMTS"""
        # layer_url = (
        #     'contextualWMSLegend=0&crs=EPSG:3857&dpiMode=7&featureCount=10&format=image/jpeg&layers=EMAP8&styles=default&tileMatrixSet=GoogleMapsCompatible&url=http://wmts.nlsc.gov.tw/wmts')
        # layer = load_wms_layer(layer_url, 'wms')

        # QgsProject.instance().addMapLayer(layer)

        # control_file = open(
        #     get_test_data_path('control', 'leaflet_wmts.html'), 'r')
        # control_output = control_file.read()
        # control_file.close()

        #   Export to web map
        # writer = LeafletWriter()
        # writer.params = self.defaultParams()
        # writer.groups = {}
        # writer.layers = [layer]
        # writer.visible = [True]
        # writer.cluster = [False]
        # writer.popup = [OrderedDict([(u'ref', u'no label'), (u'tpo_name', u'no label'), (u'area_ha', u'no label'), (u'digitised', u'no label'), (u'objtype', u'no label')])
        #                 ]
        # writer.json = [False]
        # writer.getFeatureInfo = [False]

        # result = writer.write(self.iface, tempFolder()).index_file

        #   Open the test file
        # test_style_file = open(
        #     result.replace(
        #         'file://', ''))
        # test_style_output = test_style_file.read()
        # test_style_file.close()
        # test_output = test_style_output

        # self.assertEqual(
        #     test_output, control_output, diff(control_output, test_output))

    def test91_Leaflet_scaledependent(self):
        """Leaflet scale-dependent"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_scaledependent.qml')
        control_path = get_test_data_path(
            'control', 'leaflet_scaledependent.html')

        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [('ID', 'no label'), ('fk_region', 'no label'), ('ELEV', 'no label'), ('NAME', 'no label'),
             ('USE', 'no label')])]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test92_Leaflet_categorized_25d(self):
        """Leaflet categorized 2.5D"""
        layer_path = get_test_data_path('layer', 'lakes.shp')
        style_path = get_test_data_path('style', 'categorized_25d.qml')
        control_path = get_test_data_path(
            'control', 'leaflet_categorized_25d.html')

        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict([(u'cat', u'no label'), (u'NAMES', u'no label'), (u'AREA_MI', u'no label'), (u'xlabel', u'no label'), (u'ylabel', u'no label'), (u'rotation', u'no label')])
                        ]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test93_Leaflet_graduated_25d(self):
        """Leaflet graduated 2.5D"""
        layer_path = get_test_data_path('layer', 'lakes.shp')
        style_path = get_test_data_path('style', 'graduated_25d.qml')
        control_path = get_test_data_path(
            'control', 'leaflet_graduated_25d.html')

        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict([(u'cat', u'no label'), (u'NAMES', u'no label'), (u'AREA_MI', u'no label'), (u'xlabel', u'no label'), (u'ylabel', u'no label'), (u'rotation', u'no label')])
                        ]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test94_Leaflet_svg(self):
        """Leaflet SVG"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'svg.qml')
        control_path = get_test_data_path(
            'control', 'leaflet_svg.html')

        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [('ID', 'no label'), ('fk_region', 'no label'), ('ELEV', 'no label'), ('NAME', 'no label'),
             ('USE', 'no label')])]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

        # test for exported marker file
        assert os.path.exists(result.replace('index.html', 'markers/qgis2web.svg'))

    def test95_OL3_svg(self):
        """OL3 SVG"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'svg.qml')
        control_path = get_test_data_path(
            'control', 'ol3_svg.js')

        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = OpenLayersWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [('ID', 'no label'), ('fk_region', 'no label'), ('ELEV', 'no label'), ('NAME', 'no label'),
             ('USE', 'no label')])]
        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder()).index_file
        test_style_file = open(
            result.replace(
                'file://', '').replace(
                    'index.html', 'styles/airports_0_style.js'))
        test_style_output = test_style_file.read()
        test_style_file.close()
        test_output = test_style_output
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

        # test for exported marker file
        assert os.path.exists(result.replace('index.html', 'styles/qgis2web.svg'))

    def test96_Leaflet_layer_groups(self):
        """Leaflet layer groups"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        control_path = get_test_data_path(
            'control', 'leaflet_groups.html')

        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.groups = {'group1': [layer]}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [{}]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test97_OL3_layergroups(self):
        """OL3 layer groups"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        control_path = get_test_data_path(
            'control', 'ol3_groups.js')

        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(control_path, 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = OpenLayersWriter()
        writer.params = self.defaultParams()
        writer.groups = {'group1': [layer]}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [{}]
        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        # Open the test file
        test_style_file = open(
            result.replace(
                'file://', '').replace(
                    'index.html', 'layers/layers.js'))
        test_style_output = test_style_file.read()
        test_style_file.close()
        test_output = test_style_output

        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test98_Leaflet_shapes(self):
        """Leaflet shapes"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_shapes.qml')

        layer = load_layer(layer_path)

        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(
            get_test_data_path(
                'control', 'leaflet_shapes.html'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [('ID', 'no label'), ('fk_region', 'no label'), ('ELEV', 'no label'), ('NAME', 'no label'),
             ('USE', 'no label')])]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        # Open the test file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        # Compare with control file
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test99_OL3_shapes(self):
        """OL3 shapes"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_shapes.qml')

        layer = load_layer(layer_path)

        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(
            get_test_data_path(
                'control', 'ol3_shapes.js'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = OpenLayersWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [('ID', 'no label'), ('fk_region', 'no label'), ('ELEV', 'no label'), ('NAME', 'no label'),
             ('USE', 'no label')])]
        writer.json = [False]
        writer.getFeatureInfo = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        # Open the test file
        test_style_file = open(
            result.replace(
                'file://', '').replace(
                    'index.html', 'styles/airports_0_style.js'))
        test_style_output = test_style_file.read()
        test_style_file.close()
        test_output = test_style_output

        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test100_Leaflet_line_pattern_fill(self):
        """Leaflet line pattern fill"""
        layer_path = get_test_data_path('layer', 'lakes.shp')
        style_path = get_test_data_path('style', 'lakes_linepatternfill.qml')

        layer = load_layer(layer_path)

        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(
            get_test_data_path(
                'control', 'leaflet_linepatternfill.html'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'cat', u'no label'), (u'NAMES', u'no label'), (u'AREA_MI', u'no label'),
             (u'xlabel', u'no label'), (u'ylabel', u'no label'), (u'rotation', u'no label')])]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        # Open the test file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        # Compare with control file
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

    def test101_Leaflet_raster_crs(self):
        """Leaflet raster with original CRS"""
        layer_path = get_test_data_path('layer', 'test.png')
        # style_path = get_test_data_path('style', '25d.qml')
        layer = load_layer(layer_path)
        # layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)
        crs = QgsCoordinateReferenceSystem("EPSG:27700")
        self.iface.mapCanvas().setDestinationCrs(crs)

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.params['Appearance']['Match project CRS'] = True
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [True]
        writer.cluster = [False]
        writer.popup = [OrderedDict()]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        control_file = open(
            get_test_data_path(
                'control', 'leaflet_raster_crs.html'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Open the test file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        # Test for expected output
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

        # test for exported raster file
        assert os.path.exists(result.replace('index.html', 'data/test_0.png'))
        
    def test102_Leaflet_interactive(self):
        """Leaflet interactive"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        control_file = open(
            get_test_data_path(
                'control', 'leaflet_interactive.html'), 'r')
        control_output = control_file.read()
        control_file.close()

        # Export to web map
        writer = LeafletWriter()
        writer.params = self.defaultParams()
        writer.groups = {}
        writer.layers = [layer]
        writer.visible = [True]
        writer.interactive = [False]
        writer.cluster = [False]
        writer.popup = [OrderedDict(
            [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
             (u'NAME', u'no label'), (u'USE', u'no label')])
        ]
        writer.json = [False]

        result = writer.write(self.iface, tempFolder()).index_file

        # Open the test file
        test_file = open(result)
        test_output = test_file.read()
        test_file.close()

        # Compare with control file
        self.assertEqual(
            test_output, control_output, diff(control_output, test_output))

def read_output(url, path):
    """ Given a url for the index.html file of a preview or export and the
    relative path to an output file open the file and return it's contents as a
    string """
    abs_path = url.replace('file://', '').replace('index.html', path)
    with open(abs_path) as f:
        return f.read()


def diff(control_output, test_output):
    """ Produce a unified diff given two strings splitting on newline """
    return '\n'.join(list(difflib.unified_diff(control_output.split('\n'), test_output.split('\n'), lineterm='')))


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(qgis2web_WriterTest))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
