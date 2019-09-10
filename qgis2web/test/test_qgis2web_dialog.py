# coding=utf-8
"""Dialog test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tom.chadwin@nnpa.org.uk'
__date__ = '2015-03-26'
__copyright__ = 'Copyright 2015, Riccardo Klinger / Geolicious'

import difflib
from collections import OrderedDict

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
from qgis.core import QgsVectorLayer, QgsProject, QgsCoordinateReferenceSystem
from qgis.PyQt import QtCore
from qgis.PyQt.QtCore import Qt

from qgis2web.olwriter import OpenLayersWriter
from qgis2web.leafletWriter import LeafletWriter
from qgis2web.test.utilities import get_test_data_path, load_layer
from qgis2web.configparams import (getDefaultParams)
from qgis.testing import unittest, start_app
from qgis.testing.mocked import get_iface

from qgis2web.maindialog import MainDialog

start_app()


class qgis2web_classDialogTest(unittest.TestCase):

    """Test most common plugin actions"""

    def setUp(self):
        """Runs before each test"""
        QgsProject.instance().clear()
        self.iface = get_iface()
        self.dialog = MainDialog(self.iface)
        self.setTemplate('canvas-size')

    def tearDown(self):
        """Runs after each test"""
        self.dialog = MainDialog(self.iface)
        # self.dialog.ol3.click()
        self.dialog = None
        QgsProject.instance().clear()

    def setTemplate(self, template_name):
        """
        Set template to match desired control output
        """
        combo = self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems('Template', (Qt.MatchExactly | Qt.MatchRecursive))[0], 1)

        index = combo.findText(template_name)
        combo.setCurrentIndex(index)

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
                'Add abstract': 'None',
                'Geolocate user': False,
                'Search layer': None,
                'Add layers list': 'None',
                'Attribute filter': [],
                'Measure tool': 'None',
                'Match project CRS': False,
                'Template': 'full-screen',
                'Widget Background': '#f8f8f8',
                'Widget Icon': '#000000',
                'Layer search': 'None',
                'Highlight on hover': False,
                'Show popups on hover': False
        }}

    def test00_close_dialog(self):
        """Close dialog (OL3)"""
        layer_path = get_test_data_path('layer', 'pipelines.shp')
        layer = load_layer(layer_path)

        QgsProject.instance().addMapLayer(layer)

        self.dialog = MainDialog(self.iface)
        self.dialog.close()

    def test01_preview_default(self):
        """Preview default - no data (OL3)"""
        self.dialog = MainDialog(self.iface)
        self.dialog.buttonPreview.click()

    def test02_toggle_format(self):
        """ test fetching current writer type"""
        self.dialog = MainDialog(self.iface)
        self.dialog.leaflet.click()
        self.assertEqual(self.dialog.currentMapFormat(), LeafletWriter.type())
        self.dialog.ol3.click()
        self.assertEqual(
            self.dialog.currentMapFormat(), OpenLayersWriter.type())

    def test03_toggle_format_factory(self):
        """ test fetching factory for current writer type"""
        self.dialog = MainDialog(self.iface)
        self.dialog.leaflet.click()
        self.assertEqual(self.dialog.getWriterFactory(), LeafletWriter)
        self.dialog.ol3.click()
        self.assertEqual(self.dialog.getWriterFactory(), OpenLayersWriter)

    def test04_toggle_Leaflet(self):
        """Toggle to Leaflet - no data"""
        self.dialog = MainDialog(self.iface)
        self.dialog.leaflet.click()

    def test05_preview_Leaflet(self):
        """Preview Leaflet - no data"""
        self.dialog = MainDialog(self.iface)
        self.dialog.leaflet.click()
        self.dialog.buttonPreview.click()

    def test06_toggle_OL3(self):
        """Toggle to OL3 - no data"""
        self.dialog = MainDialog(self.iface)
        self.dialog.ol3.click()

    def test07_preview_OL3(self):
        """Preview OL3 - no data"""
        self.dialog = MainDialog(self.iface)
        self.dialog.ol3.click()
        self.dialog.buttonPreview.click()

#    def test08_export_OL3(self):
#        """Export OL3 - no data"""
#        self.dialog = MainDialog(self.iface)
#        self.dialog.ol3.click()
#        self.dialog.buttonExport.click()

    def test09_Leaflet_json_pnt_single(self):
        """Dialog test: Leaflet  JSON point single"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')

        layer = load_layer(layer_path)

        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems('Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0], 1).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup, [OrderedDict(
            [('ID', 'no label'), ('fk_region', 'no label'), ('ELEV', 'no label'), ('NAME', 'no label'),
             ('USE', 'no label')])])
        self.assertEqual(writer.json, [False])

#    def test10_Leaflet_wfs_pnt_single(self):
#        """Dialog test: Leaflet  WFS point single"""
#        layer_url = (
#            'http://balleter.nationalparks.gov.uk/geoserver/wfs?SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME=dnpa_inspire:tpo_points&SRSNAME=EPSG:27700&BBOX=233720,53549,297567,96689')
#        layer_style = get_test_data_path('style', 'point_single.qml')
#        layer = load_wfs_layer(layer_url, 'point')
#        layer.loadNamedStyle(layer_style)

#        QgsProject.instance().addMapLayer(layer)

#        self.dialog = MainDialog(self.iface)
#        self.dialog.appearanceParams.itemWidget(
#            self.dialog.appearanceParams.findItems(
#                'Extent',
#                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
#                1).setCurrentIndex(1)
#        self.setTemplate('full-screen')
#        self.dialog.leaflet.click()

#        writer = self.dialog.createWriter()
#        self.assertTrue(isinstance(writer, LeafletWriter))
#        expected_params = self.defaultParams()
#        self.assertEqual(writer.params, expected_params)
#        self.assertEqual(writer.groups, {})
#        self.assertEqual(writer.layers, [layer])
#        self.assertEqual(writer.visible, [True])
#        self.assertEqual(writer.cluster, [False])
#        self.assertEqual(writer.popup, [OrderedDict([(u'ref', u'no label'), (u'tpo_name', u'no label'), (u'area_ha', u'no label'), (u'digitised', u'no label'), (u'objtype', u'no label')])
#                                        ])
#        self.assertEqual(writer.json, [False])

    def test11_Leaflet_json_line_single(self):
        """Dialog test: Leaflet  JSON line single"""
        layer_path = get_test_data_path('layer', 'pipelines.shp')
        style_path = get_test_data_path('style', 'pipelines_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems('Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0], 1
        ).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup, [OrderedDict([(u'cat', u'no label'), (u'LOCDESC', u'no label'), (u'F_CODE', u'no label'), (u'F_CODEDESC', u'no label')])
                                        ])
        self.assertEqual(writer.json, [False])

#    def test12_Leaflet_wfs_line_single(self):
#        """Dialog test: Leaflet  WFS line single"""
#        layer_url = ('http://balleter.nationalparks.gov.uk/geoserver/wfs?'
#                     'SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME'
#                     '=broads_inspire:centreline&SRSNAME=EPSG:27700')
#        layer_style = get_test_data_path('style', 'line_single.qml')
#        layer = load_wfs_layer(layer_url, 'centreline')
#        layer.loadNamedStyle(layer_style)

#        QgsProject.instance().addMapLayer(layer)

#        self.dialog = MainDialog(self.iface)
#        self.dialog.appearanceParams.itemWidget(
#            self.dialog.appearanceParams.findItems(
#                'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
#                1).setCurrentIndex(1)
#        self.setTemplate('full-screen')
#        self.dialog.leaflet.click()

#        writer = self.dialog.createWriter()
#        self.assertTrue(isinstance(writer, LeafletWriter))
#        expected_params = self.defaultParams()
#        self.assertEqual(writer.params, expected_params)
#        self.assertEqual(writer.groups, {})
#        self.assertEqual(writer.layers, [layer])
#        self.assertEqual(writer.visible, [True])
#        self.assertEqual(writer.cluster, [False])
#        self.assertEqual(writer.popup, [OrderedDict([(u'objecttype', u'no label'), (u'name', u'no label'), (u'navigable', u'no label'), (u'responsibleparty', u'no label'), (u'broad', u'no label'), (u'from_', u'no label'), (u'to_', u'no label'), (u'reachid', u'no label'), (u'globalid', u'no label'), (u'route', u'no label'), (u'shape_stlength__', u'no label')])
#                                        ])
#        self.assertEqual(writer.json, [False])

    def test13_Leaflet_json_poly_single(self):
        """Dialog test: Leaflet  JSON polygon single"""
        layer_path = get_test_data_path('layer', 'lakes.shp')
        style_path = get_test_data_path('style', 'lakes_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                (Qt.MatchExactly | Qt.MatchRecursive)
            )[0],
            1
        ).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup, [OrderedDict([(u'cat', u'no label'), (u'NAMES', u'no label'), (u'AREA_MI', u'no label'), (u'xlabel', u'no label'), (u'ylabel', u'no label'), (u'rotation', u'no label')])
                                        ])
        self.assertEqual(writer.json, [False])

    # def test14_Leaflet_wfs_poly_single(self):
        # """Dialog test: Leaflet  WFS polygon single"""
        # layer_url = ('http://balleter.nationalparks.gov.uk/geoserver/wfs?'
        #              'SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME'
        #              '=dnpa_inspire:con_areas&SRSNAME=EPSG:27700')
        # layer_style = get_test_data_path('style', 'polygon_single.qml')
        # control_path = get_test_data_path(
        #     'control', 'leaflet_wfs_polygon_single.html')
        # layer = load_wfs_layer(layer_url, 'polygon')
        # layer.loadNamedStyle(layer_style)

        # QgsProject.instance().addMapLayer(layer)

        # self.dialog = MainDialog(self.iface)
        # self.dialog.appearanceParams.itemWidget(
        #     self.dialog.appearanceParams.findItems(
        #         'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
        #         1).setCurrentIndex(1)
        # self.setTemplate('full-screen')
        # self.dialog.leaflet.click()

        # writer = self.dialog.createWriter()
        # self.assertTrue(isinstance(writer, LeafletWriter))
        # expected_params = self.defaultParams()
        # self.assertEqual(writer.params, expected_params)
        # self.assertEqual(writer.groups, {})
        # self.assertEqual(writer.layers, [layer])
        # self.assertEqual(writer.visible, [True])
        # self.assertEqual(writer.cluster, [False])
        # self.assertEqual(writer.popup, [OrderedDict([(u'name', u'no label'), (u'details', u'no label'), (u'date', u'no label'), (u'area_ha', u'no label'), (u'web_page', u'no label')])
        #                                 ])
        # self.assertEqual(writer.json, [False])

    def test15_Leaflet_json_pnt_categorized(self):
        """Dialog test: Leaflet  JSON point categorized"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_categorized.qml')
        # control_path = get_test_data_path('control', 'leaflet_json_point_categorized.html')

        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems('Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
            1
        ).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup, [OrderedDict(
            [('ID', 'no label'), ('fk_region', 'no label'), ('ELEV', 'no label'), ('NAME', 'no label'),
             ('USE', 'no label')])])
        self.assertEqual(writer.json, [False])

    # def test16_Leaflet_wfs_pnt_categorized(self):
        # """Dialog test: Leaflet  WFS point categorized"""
        # layer_url = (
        #     'http://balleter.nationalparks.gov.uk/geoserver/wfs?SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME=dnpa_inspire:tpo_points&SRSNAME=EPSG:27700&BBOX=233720,53549,297567,96689')
        # layer_style = get_test_data_path('style', 'wfs_point_categorized.qml')
        # control_path = get_test_data_path(
        #     'control', 'leaflet_wfs_point_categorized.html')
        # layer = load_wfs_layer(layer_url, 'point')
        # layer.loadNamedStyle(layer_style)

        # QgsProject.instance().addMapLayer(layer)

        # self.dialog = MainDialog(self.iface)
        # self.dialog.appearanceParams.itemWidget(
        #     self.dialog.appearanceParams.findItems(
        #         'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
        #         1).setCurrentIndex(1)
        # self.setTemplate('full-screen')
        # self.dialog.leaflet.click()

        # writer = self.dialog.createWriter()
        # self.assertTrue(isinstance(writer, LeafletWriter))
        # expected_params = self.defaultParams()
        # self.assertEqual(writer.params, expected_params)
        # self.assertEqual(writer.groups, {})
        # self.assertEqual(writer.layers, [layer])
        # self.assertEqual(writer.visible, [True])
        # self.assertEqual(writer.cluster, [False])
        # self.assertEqual(writer.popup, [OrderedDict([(u'ref', u'no label'), (u'tpo_name', u'no label'), (u'area_ha', u'no label'), (u'digitised', u'no label'), (u'objtype', u'no label')])
        #                                 ])
        # self.assertEqual(writer.json, [False])

    def test17_Leaflet_json_line_categorized(self):
        """Dialog test: Leaflet  JSON line categorized"""
        layer_path = get_test_data_path('layer', 'pipelines.shp')
        style_path = get_test_data_path('style', 'pipelines_categorized.qml')
        # control_path = get_test_data_path('control', 'leaflet_json_line_categorized.html')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent', (Qt.MatchExactly | Qt.MatchRecursive)
            )[0],
            1
        ).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'cat', u'no label'), (u'LOCDESC', u'no label'), (u'F_CODE', u'no label'),
                              (u'F_CODEDESC', u'no label')])])
        self.assertEqual(writer.json, [False])

    def test19_Leaflet_json_poly_categorized(self):
        """Dialog test: Leaflet  JSON polygon categorized"""
        layer_path = get_test_data_path('layer', 'lakes.shp')
        style_path = get_test_data_path('style', 'lakes_categorized.qml')
        # control_path = get_test_data_path('control', 'leaflet_json_polygon_categorized.html')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent', (Qt.MatchExactly | Qt.MatchRecursive)
            )[0],
            1
        ).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'cat', u'no label'), (u'NAMES', u'no label'), (u'AREA_MI', u'no label'),
                              (u'xlabel', u'no label'), (u'ylabel', u'no label'), (u'rotation', u'no label')])])
        self.assertEqual(writer.json, [False])

    # def test20_Leaflet_wfs_poly_categorized(self):
        # """Dialog test: Leaflet  WFS polygon categorized"""
        # layer_url = ('http://balleter.nationalparks.gov.uk/geoserver/wfs?'
                     # 'SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME'
                     # '=dnpa_inspire:con_areas&SRSNAME=EPSG:27700')
        # layer_style = get_test_data_path('style', 'wfs_polygon_categorized.qml')
        # layer = load_wfs_layer(layer_url, 'polygon')
        # layer.loadNamedStyle(layer_style)

        # QgsProject.instance().addMapLayer(layer)

        # self.dialog = MainDialog(self.iface)
        # self.dialog.appearanceParams.itemWidget(
            # self.dialog.appearanceParams.findItems(
                # 'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                # 1).setCurrentIndex(1)
        # self.setTemplate('full-screen')
        # self.dialog.leaflet.click()
        # writer = self.dialog.createWriter()
        # self.assertTrue(isinstance(writer, LeafletWriter))
        # expected_params = self.defaultParams()
        # self.assertEqual(writer.params, expected_params)
        # self.assertEqual(writer.groups, {})
        # self.assertEqual(writer.layers, [layer])
        # self.assertEqual(writer.visible, [True])
        # self.assertEqual(writer.cluster, [False])
        # self.assertEqual(writer.popup,
                         # [OrderedDict([(u'name', u'no label'), (u'details', u'no label'), (u'date', u'no label'), (u'area_ha', u'no label'), (u'web_page', u'no label')])
                          # ])
        # self.assertEqual(writer.json, [False])

    def test21_Leaflet_json_pnt_graduated(self):
        """Dialog test: Leaflet  JSON point graduated"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_graduated.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
                              (u'NAME', u'no label'), (u'USE', u'no label')])]
                         )
        self.assertEqual(writer.json, [False])

    # def test22_Leaflet_wfs_pnt_graduated(self):
        # """Dialog test: Leaflet  WFS point graduated"""
        # layer_url = (
            # 'http://balleter.nationalparks.gov.uk/geoserver/wfs?SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME=dnpa_inspire:tpo_points&SRSNAME=EPSG:27700&BBOX=233720,53549,297567,96689')
        # layer_style = get_test_data_path('style', 'wfs_point_graduated.qml')
        # layer = load_wfs_layer(layer_url, 'point')
        # layer.loadNamedStyle(layer_style)

        # QgsProject.instance().addMapLayer(layer)

        # self.dialog = MainDialog(self.iface)
        # self.dialog.appearanceParams.itemWidget(
            # self.dialog.appearanceParams.findItems(
                # 'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                # 1).setCurrentIndex(1)
        # self.setTemplate('full-screen')
        # self.dialog.leaflet.click()

        # writer = self.dialog.createWriter()
        # self.assertTrue(isinstance(writer, LeafletWriter))
        # expected_params = self.defaultParams()
        # self.assertEqual(writer.params, expected_params)
        # self.assertEqual(writer.groups, {})
        # self.assertEqual(writer.layers, [layer])
        # self.assertEqual(writer.visible, [True])
        # self.assertEqual(writer.cluster, [False])
        # self.assertEqual(writer.popup,
                         # [OrderedDict([(u'ref', u'no label'), (u'tpo_name', u'no label'), (u'area_ha', u'no label'), (u'digitised', u'no label'), (u'objtype', u'no label')])
                          # ])
        # self.assertEqual(writer.json, [False])

    def test23_Leaflet_json_line_graduated(self):
        """Dialog test: Leaflet  JSON line graduated"""
        layer_path = get_test_data_path('layer', 'pipelines.shp')
        layer_style = get_test_data_path('style', 'pipelines_graduated.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(layer_style)

        QgsProject.instance().addMapLayer(layer)

        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict([(u'cat', u'no label'), (u'LOCDESC', u'no label'), (
                             u'F_CODE', u'no label'), (u'F_CODEDESC', u'no label')])]

                         )
        self.assertEqual(writer.json, [False])

    # def test24_Leaflet_wfs_line_graduated(self):
        # """Dialog test: Leaflet  WFS line graduated"""
        # layer_url = ('http://balleter.nationalparks.gov.uk/geoserver/wfs?'
                     # 'SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME'
                     # '=broads_inspire:centreline&SRSNAME=EPSG:27700')
        # layer_style = get_test_data_path('style', 'wfs_line_graduated.qml')
        # layer = load_wfs_layer(layer_url, 'centreline')
        # layer.loadNamedStyle(layer_style)

        # QgsProject.instance().addMapLayer(layer)

        # self.dialog = MainDialog(self.iface)
        # self.dialog.appearanceParams.itemWidget(
            # self.dialog.appearanceParams.findItems(
                # 'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                # 1).setCurrentIndex(1)
        # self.setTemplate('full-screen')
        # self.dialog.leaflet.click()

        # writer = self.dialog.createWriter()
        # self.assertTrue(isinstance(writer, LeafletWriter))
        # expected_params = self.defaultParams()
        # self.assertEqual(writer.params, expected_params)
        # self.assertEqual(writer.groups, {})
        # self.assertEqual(writer.layers, [layer])
        # self.assertEqual(writer.visible, [True])
        # self.assertEqual(writer.cluster, [False])
        # self.assertEqual(writer.popup,
                         # [OrderedDict([(u'objecttype', u'no label'), (u'name', u'no label'), (u'navigable', u'no label'), (u'responsibleparty', u'no label'), (u'broad', u'no label'), (u'from_', u'no label'), (u'to_', u'no label'), (u'reachid', u'no label'), (u'globalid', u'no label'), (u'route', u'no label'), (u'shape_stlength__', u'no label')])
                          # ]
                         # )
        # self.assertEqual(writer.json, [False])

    def test25_Leaflet_json_poly_graduated(self):
        """Dialog test: Leaflet  JSON polygon graduated"""
        layer_path = get_test_data_path('layer', 'lakes.shp')
        layer_style = get_test_data_path('style', 'lakes_graduated.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(layer_style)

        QgsProject.instance().addMapLayer(layer)

        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'cat', u'no label'), (u'NAMES', u'no label'), (u'AREA_MI', u'no label'),
                              (u'xlabel', u'no label'), (u'ylabel', u'no label'), (u'rotation', u'no label')])]
                         )
        self.assertEqual(writer.json, [False])

    # def test26_Leaflet_wfs_poly_graduated(self):
        # """Dialog test: Leaflet  WFS polygon graduated"""
        # layer_url = ('http://balleter.nationalparks.gov.uk/geoserver/wfs?'
                     # 'SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME'
                     # '=dnpa_inspire:con_areas&SRSNAME=EPSG:27700')
        # layer_style = get_test_data_path('style', 'wfs_polygon_graduated.qml')
        # layer = load_wfs_layer(layer_url, 'polygon')
        # layer.loadNamedStyle(layer_style)

        # QgsProject.instance().addMapLayer(layer)

        # self.dialog = MainDialog(self.iface)
        # self.dialog.appearanceParams.itemWidget(
            # self.dialog.appearanceParams.findItems(
                # 'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                # 1).setCurrentIndex(1)
        # self.setTemplate('full-screen')
        # self.dialog.leaflet.click()

        # writer = self.dialog.createWriter()
        # self.assertTrue(isinstance(writer, LeafletWriter))
        # expected_params = self.defaultParams()
        # self.assertEqual(writer.params, expected_params)
        # self.assertEqual(writer.groups, {})
        # self.assertEqual(writer.layers, [layer])
        # self.assertEqual(writer.visible, [True])
        # self.assertEqual(writer.cluster, [False])
        # self.assertEqual(writer.popup,
                         # [OrderedDict(
                          # [(u'name', u'no label'), (u'details', u'no label'), (u'date', u'no label'),
                           # (u'area_ha', u'no label'), (u'web_page', u'no label')])
                          # ])
        # self.assertEqual(writer.json, [False])

    def test27_OL3_pnt_single(self):
        """Dialog test: OL3   point single"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.ol3.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, OpenLayersWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict([(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'), (u'NAME', u'no label'), (u'USE', u'no label')])
                          ]
                         )
        self.assertEqual(writer.json, [False])

    def test28_OL3_line_single(self):
        """Dialog test: OL3   line single"""
        layer_path = get_test_data_path('layer', 'pipelines.shp')
        style_path = get_test_data_path('style', 'pipelines_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.ol3.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, OpenLayersWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'cat', u'no label'), (u'LOCDESC', u'no label'), (u'F_CODE', u'no label'),
                              (u'F_CODEDESC', u'no label')])]
                         )
        self.assertEqual(writer.json, [False])

    def test29_OL3_poly_single(self):
        """Dialog test: OL3   polygon single"""
        layer_path = get_test_data_path('layer', 'lakes.shp')
        style_path = get_test_data_path('style', 'lakes_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems("Extent",
                                               (Qt.MatchExactly |
                                                Qt.MatchRecursive))[0], 1).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.ol3.click()
        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, OpenLayersWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'cat', u'no label'), (u'NAMES', u'no label'), (u'AREA_MI', u'no label'),
                              (u'xlabel', u'no label'), (u'ylabel', u'no label'), (u'rotation', u'no label')])]
                         )
        self.assertEqual(writer.json, [False])

    def test30_OL3_pnt_categorized(self):
        """Dialog test: OL3   point categorized"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_categorized.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                "Extent", (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.ol3.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, OpenLayersWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
                              (u'NAME', u'no label'), (u'USE', u'no label')])]
                         )
        self.assertEqual(writer.json, [False])

    def test31_OL3_line_categorized(self):
        """Dialog test: OL3   line categorized"""
        layer_path = get_test_data_path('layer', 'pipelines.shp')
        style_path = get_test_data_path('style', 'pipelines_categorized.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems("Extent",
                                               (Qt.MatchExactly |
                                                Qt.MatchRecursive))[0], 1).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.ol3.click()
        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, OpenLayersWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'cat', u'no label'), (u'LOCDESC', u'no label'), (u'F_CODE', u'no label'),
                              (u'F_CODEDESC', u'no label')])]
                         )
        self.assertEqual(writer.json, [False])

    def test32_OL3_poly_categorized(self):
        """Dialog test: OL3   polygon categorized"""
        layer_path = get_test_data_path('layer', 'lakes.shp')
        style_path = get_test_data_path('style', 'lakes_categorized.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems("Extent",
                                               (Qt.MatchExactly |
                                                Qt.MatchRecursive))[0], 1).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.ol3.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, OpenLayersWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'cat', u'no label'), (u'NAMES', u'no label'), (u'AREA_MI', u'no label'),
                              (u'xlabel', u'no label'), (u'ylabel', u'no label'), (u'rotation', u'no label')])]
                         )
        self.assertEqual(writer.json, [False])

    def test33_OL3_pnt_graduated(self):
        """Dialog test: OL3   point graduated"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_graduated.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems("Extent",
                                               (Qt.MatchExactly |
                                                Qt.MatchRecursive))[0], 1).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.ol3.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, OpenLayersWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
                              (u'NAME', u'no label'), (u'USE', u'no label')])]
                         )
        self.assertEqual(writer.json, [False])

    def test34_OL3_line_graduated(self):
        """Dialog test: OL3   line graduated"""
        layer_path = get_test_data_path('layer', 'pipelines.shp')
        style_path = get_test_data_path('style', 'pipelines_graduated.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems("Extent",
                                               (Qt.MatchExactly |
                                                Qt.MatchRecursive))[0], 1).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.ol3.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, OpenLayersWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'cat', u'no label'), (u'LOCDESC', u'no label'), (u'F_CODE', u'no label'),
                              (u'F_CODEDESC', u'no label')])]
                         )
        self.assertEqual(writer.json, [False])

    def test35_OL3_poly_graduated(self):
        """Dialog test: OL3   polygon graduated"""
        layer_path = get_test_data_path('layer', 'lakes.shp')
        style_path = get_test_data_path('style', 'lakes_graduated.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems("Extent",
                                               (Qt.MatchExactly |
                                                Qt.MatchRecursive))[0], 1).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.ol3.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, OpenLayersWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'cat', u'no label'), (u'NAMES', u'no label'), (u'AREA_MI', u'no label'),
                              (u'xlabel', u'no label'), (u'ylabel', u'no label'), (u'rotation', u'no label')])]
                         )
        self.assertEqual(writer.json, [False])

    def test36_OL3_layer_list(self):
        """Dialog test: OL3   A layer list is present when selected"""

        layer_path = get_test_data_path('layer', 'airports.shp')
        layer = load_layer(layer_path)

        QgsProject.instance().addMapLayer(layer)

        self.dialog = MainDialog(self.iface)

        # Ensure the OpenLayers 3 option is selected
        self.dialog.ol3.click()

        # Change the 'Add layers list' dropdown
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Add layers list',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('full-screen')

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, OpenLayersWriter))
        expected_params = self.defaultParams()
        expected_params['Appearance']['Add layers list'] = 'Collapsed'
        expected_params['Scale/Zoom']['Extent'] = 'Canvas extent'
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict([(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'), (u'NAME', u'no label'), (u'USE', u'no label')])
                          ])
        self.assertEqual(writer.json, [False])

    def test40_Leaflet_scalebar(self):
        """Dialog test: Leaflet  scale bar"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)

        # Check the 'Add scale bar' checkbox
        QgsProject.instance().writeEntryBool("ScaleBar", "/Enabled", True)
        self.setTemplate('full-screen')
        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()

        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
                              (u'NAME', u'no label'), (u'USE', u'no label')])
                          ])
        self.assertEqual(writer.json, [False])

    def test41_OL3_scalebar(self):
        """Dialog test: OL3   scale bar"""
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

        # Export to web map
        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('canvas-size')

        # Check the 'Add scale bar' checkbox
        QgsProject.instance().writeEntryBool("ScaleBar", "/Enabled", True)
        self.dialog.ol3.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, OpenLayersWriter))
        expected_params = self.defaultParams()
        expected_params['Appearance']['Template'] = 'canvas-size'
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
                              (u'NAME', u'no label'), (u'USE', u'no label')])
                          ])
        self.assertEqual(writer.json, [False])

    def test42_Leaflet_measure(self):
        """Dialog test: Leaflet  measure"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)

        # Set the 'Measure tool' combo
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Measure tool',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()
        expected_params['Appearance']['Measure tool'] = 'Metric'
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
                              (u'NAME', u'no label'), (u'USE', u'no label')])
                          ])
        self.assertEqual(writer.json, [False])

    def test43_OL3_measure(self):
        """Dialog test: OL3   measure control"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('full-screen')

        # Set the 'Measure tool' combo
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Measure tool',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.dialog.ol3.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, OpenLayersWriter))
        expected_params = self.defaultParams()
        expected_params['Appearance']['Measure tool'] = 'Metric'
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
                              (u'NAME', u'no label'), (u'USE', u'no label')])
                          ])
        self.assertEqual(writer.json, [False])

    def test44_Leaflet_address(self):
        """Dialog test: Leaflet  address search"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)

        # Check the 'Add address search' checkbox
        self.dialog.items['Appearance'].get(
            'Add address search').setCheckState(1, QtCore.Qt.Checked)
        self.setTemplate('full-screen')
        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()
        expected_params['Appearance']['Add address search'] = True
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
                              (u'NAME', u'no label'), (u'USE', u'no label')])
                          ])
        self.assertEqual(writer.json, [False])

    def test45_OL3_address(self):
        """Dialog test: OL3   address search"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('full-screen')

        # Check the 'Add address search' checkbox
        self.dialog.items['Appearance'].get(
            'Add address search').setCheckState(1, QtCore.Qt.Checked)
        self.dialog.ol3.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, OpenLayersWriter))
        expected_params = self.defaultParams()
        expected_params['Appearance']['Add address search'] = True
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
                              (u'NAME', u'no label'), (u'USE', u'no label')])
                          ])
        self.assertEqual(writer.json, [False])

    def test46_Leaflet_geolocate(self):
        """Dialog test: Leaflet  geolocate user"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)

        # Check the 'Geolocate user' checkbox
        self.dialog.items['Appearance'].get(
            'Geolocate user').setCheckState(1, QtCore.Qt.Checked)
        self.setTemplate('full-screen')
        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()
        expected_params['Appearance']['Geolocate user'] = True
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
                              (u'NAME', u'no label'), (u'USE', u'no label')])
                          ])
        self.assertEqual(writer.json, [False])

    def test47_OL3_geolocate(self):
        """Dialog test: OL3   geolocate user"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('canvas-size')

        # Check the 'Geolocate user' checkbox
        self.dialog.items['Appearance'].get(
            'Geolocate user').setCheckState(1, QtCore.Qt.Checked)
        self.dialog.ol3.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, OpenLayersWriter))
        expected_params = self.defaultParams()
        expected_params['Appearance']['Geolocate user'] = True
        expected_params['Appearance']['Template'] = 'canvas-size'
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
                              (u'NAME', u'no label'), (u'USE', u'no label')])
                          ])
        self.assertEqual(writer.json, [False])

    def test48_Leaflet_highlight(self):
        """Dialog test: Leaflet  highlight on hover"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)

        # Check the 'Highlight on hover' checkbox
        self.dialog.items['Appearance'].get(
            'Highlight on hover').setCheckState(1, QtCore.Qt.Checked)
        self.setTemplate('full-screen')
        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()
        expected_params['Appearance']['Highlight on hover'] = True
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
                              (u'NAME', u'no label'), (u'USE', u'no label')])
                          ])
        self.assertEqual(writer.json, [False])

    def test49_OL3_highlight(self):
        """Dialog test: OL3   highlight on hover"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('canvas-size')

        # Check the 'Highlight on hover' checkbox
        self.dialog.items['Appearance'].get(
            'Highlight on hover').setCheckState(1, QtCore.Qt.Checked)
        self.dialog.ol3.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, OpenLayersWriter))
        expected_params = self.defaultParams()
        expected_params['Appearance']['Highlight on hover'] = True
        expected_params['Appearance']['Template'] = 'canvas-size'
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
                              (u'NAME', u'no label'), (u'USE', u'no label')])
                          ])
        self.assertEqual(writer.json, [False])

    def test50_Leaflet_CRS(self):
        """Dialog test: Leaflet  match CRS"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)
        crs = QgsCoordinateReferenceSystem("EPSG:2964")
        self.iface.mapCanvas().setDestinationCrs(crs)

        # Export to web map
        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)

        # Check the 'Match project CRS' checkbox
        self.dialog.items['Appearance'].get(
            'Match project CRS').setCheckState(1, QtCore.Qt.Checked)
        self.setTemplate('full-screen')
        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()
        expected_params['Appearance']['Match project CRS'] = True
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
                              (u'NAME', u'no label'), (u'USE', u'no label')])
                          ])
        self.assertEqual(writer.json, [False])

    def test51_OL3_CRS(self):
        """Dialog test: OL3   match CRS"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)
        crs = QgsCoordinateReferenceSystem("EPSG:2964")
        self.iface.mapCanvas().setDestinationCrs(crs)

        # Export to web map
        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('full-screen')

                # Check the 'Match project CRS' checkbox
        self.dialog.items['Appearance'].get(
            'Match project CRS').setCheckState(1, QtCore.Qt.Checked)
        self.dialog.ol3.click()
        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, OpenLayersWriter))
        expected_params = self.defaultParams()
        expected_params['Appearance']['Match project CRS'] = True
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
                              (u'NAME', u'no label'), (u'USE', u'no label')])
                          ])
        self.assertEqual(writer.json, [False])

    def test52_Leaflet_layerslist(self):
        """Dialog test: Leaflet  add layers list"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)

        # Change the 'Add layers list' dropdown
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Add layers list',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()
        expected_params['Appearance']['Add layers list'] = 'Collapsed'
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
                              (u'NAME', u'no label'), (u'USE', u'no label')])
                          ])
        self.assertEqual(writer.json, [False])

    def test53_Leaflet_visible(self):
        """Dialog test: Leaflet  visible"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)

        # Check the 'Visible' checkbox
        self.dialog.layers_item.child(0).visibleCheck.setChecked(False)
        self.setTemplate('full-screen')
        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [False])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
                              (u'NAME', u'no label'), (u'USE', u'no label')])
                          ])
        self.assertEqual(writer.json, [False])

    def test54_OL3_visible(self):
        """Dialog test: OL3   visible"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('canvas-size')

        # Check the 'Visible' checkbox
        self.dialog.layers_item.child(0).visibleCheck.setChecked(False)
        self.dialog.ol3.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, OpenLayersWriter))
        expected_params = self.defaultParams()
        expected_params['Appearance']['Template'] = 'canvas-size'
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [False])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
                              (u'NAME', u'no label'), (u'USE', u'no label')])
                          ])
        self.assertEqual(writer.json, [False])

    def test55_Leaflet_cluster(self):
        """Dialog test: Leaflet  cluster"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)

        # Check the 'Cluster' checkbox
        self.dialog.layers_item.child(0).clusterCheck.setChecked(True)
        self.setTemplate('full-screen')
        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [True])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
                              (u'NAME', u'no label'), (u'USE', u'no label')])
                          ])
        self.assertEqual(writer.json, [False])

    def test56_OL3_cluster(self):
        """Dialog test: OL3   cluster"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('canvas-size')

        # Check the 'Cluster' checkbox
        self.dialog.layers_item.child(0).clusterCheck.setChecked(True)
        self.dialog.ol3.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, OpenLayersWriter))
        expected_params = self.defaultParams()
        expected_params['Appearance']['Template'] = 'canvas-size'
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [True])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
                              (u'NAME', u'no label'), (u'USE', u'no label')])
                          ])
        self.assertEqual(writer.json, [False])

    def test62_leaflet_precision(self):
        """Dialog test: Leaflet  precision"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)

        # Set 'Precision' combo to '3'
        self.dialog.items['Data export'].get(
            'Precision').combo.setCurrentIndex(3)
        self.setTemplate('canvas-size')
        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()
        expected_params['Appearance']['Template'] = 'canvas-size'
        expected_params['Data export']['Precision'] = '3'
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
                              (u'NAME', u'no label'), (u'USE', u'no label')])
                          ])
        self.assertEqual(writer.json, [False])

    def test63_ol3_precision(self):
        """Dialog test: OL3   precision"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('canvas-size')

        # Set 'Precision' combo to '2'
        self.dialog.items['Data export'].get(
            'Precision').combo.setCurrentIndex(2)
        self.dialog.ol3.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, OpenLayersWriter))
        expected_params = self.defaultParams()
        expected_params['Appearance']['Template'] = 'canvas-size'
        expected_params['Data export']['Precision'] = '2'
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
                              (u'NAME', u'no label'), (u'USE', u'no label')])
                          ])
        self.assertEqual(writer.json, [False])

    def test67_leaflet_minify(self):
        """Dialog test: Leaflet  minify"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)

        # Check the 'Minify GeoJSON files' checkbox
        self.dialog.items['Data export'].get(
            'Minify GeoJSON files').setCheckState(1, QtCore.Qt.Checked)

        # Set 'Precision' combo to '6'
        self.dialog.items['Data export'].get(
            'Precision').combo.setCurrentIndex(6)
        self.setTemplate('canvas-size')
        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()
        expected_params['Data export']['Precision'] = '6'
        expected_params['Data export']['Minify GeoJSON files'] = True
        expected_params['Appearance']['Template'] = 'canvas-size'
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
                              (u'NAME', u'no label'), (u'USE', u'no label')])
                          ])
        self.assertEqual(writer.json, [False])

    def test68_ol3_minify(self):
        """Dialog test: OL3   minify"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('canvas-size')

        # Check the 'Minify GeoJSON files' checkbox
        self.dialog.items['Data export'].get(
            'Minify GeoJSON files').setCheckState(1, QtCore.Qt.Checked)

        # Set 'Precision' combo to '2'
        self.dialog.items['Data export'].get(
            'Precision').combo.setCurrentIndex(2)
        self.dialog.ol3.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, OpenLayersWriter))
        expected_params = self.defaultParams()
        expected_params['Data export']['Precision'] = '2'
        expected_params['Data export']['Minify GeoJSON files'] = True
        expected_params['Appearance']['Template'] = 'canvas-size'
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
                              (u'NAME', u'no label'), (u'USE', u'no label')])
                          ])
        self.assertEqual(writer.json, [False])

    def test69_Leaflet_canvasextent(self):
        """Dialog test: Leaflet  canvas extent"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(0)

        self.setTemplate('canvas-size')
        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()
        expected_params['Scale/Zoom']['Extent'] = 'Canvas extent'
        expected_params['Appearance']['Template'] = 'canvas-size'
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
                              (u'NAME', u'no label'), (u'USE', u'no label')])
                          ])
        self.assertEqual(writer.json, [False])

    def test70_Leaflet_maxzoom(self):
        """Dialog test: Leaflet  max zoom"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)

        # Set 'Max zoom' combo to '20'
        self.dialog.items['Scale/Zoom'].get(
            'Max zoom level').combo.setCurrentIndex(19)
        self.setTemplate('full-screen')
        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()
        expected_params['Scale/Zoom']['Max zoom level'] = '20'
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
                              (u'NAME', u'no label'), (u'USE', u'no label')])
                          ])
        self.assertEqual(writer.json, [False])

    def test71_ol3_maxzoom(self):
        """Dialog test: OL3   max zoom"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('canvas-size')

        # Set 'Max zoom level' combo to '20'
        self.dialog.items['Scale/Zoom'].get(
            'Max zoom level').combo.setCurrentIndex(19)
        self.dialog.ol3.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, OpenLayersWriter))
        expected_params = self.defaultParams()
        expected_params['Scale/Zoom']['Max zoom level'] = '20'
        expected_params['Appearance']['Template'] = 'canvas-size'
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
                              (u'NAME', u'no label'), (u'USE', u'no label')])
                          ])
        self.assertEqual(writer.json, [False])

    def test72_Leaflet_minzoom(self):
        """Dialog test: Leaflet  min zoom"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)

        # Set 'Min zoom' combo to '6'
        self.dialog.items['Scale/Zoom'].get(
            'Min zoom level').combo.setCurrentIndex(5)
        self.setTemplate('full-screen')
        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()
        expected_params['Scale/Zoom']['Min zoom level'] = '6'
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
                              (u'NAME', u'no label'), (u'USE', u'no label')])
                          ])
        self.assertEqual(writer.json, [False])

    def test73_ol3_minzoom(self):
        """Dialog test: OL3   min zoom"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('canvas-size')

        # Set 'Min zoom level' combo to '6'
        self.dialog.items['Scale/Zoom'].get(
            'Min zoom level').combo.setCurrentIndex(5)
        self.dialog.ol3.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, OpenLayersWriter))
        expected_params = self.defaultParams()
        expected_params['Scale/Zoom']['Min zoom level'] = '6'
        expected_params['Appearance']['Template'] = 'canvas-size'
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
                              (u'NAME', u'no label'), (u'USE', u'no label')])
                          ])
        self.assertEqual(writer.json, [False])

    def test74_Leaflet_restricttoextent(self):
        """Dialog test: Leaflet  restrict to extent"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)

        # Check the 'Restrict to extent' checkbox
        self.dialog.items['Scale/Zoom'].get(
            'Restrict to extent').setCheckState(1, QtCore.Qt.Checked)
        self.setTemplate('full-screen')
        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()
        expected_params['Scale/Zoom']['Restrict to extent'] = True
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
                              (u'NAME', u'no label'), (u'USE', u'no label')])
                          ])
        self.assertEqual(writer.json, [False])

    def test75_ol3_restricttoextent(self):
        """Dialog test: OL3   restrict to extent"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('canvas-size')

        # Check the 'Restrict to extent' checkbox
        self.dialog.items['Scale/Zoom'].get(
            'Restrict to extent').setCheckState(1, QtCore.Qt.Checked)

        self.dialog.ol3.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, OpenLayersWriter))
        expected_params = self.defaultParams()
        expected_params['Scale/Zoom']['Restrict to extent'] = True
        expected_params['Appearance']['Template'] = 'canvas-size'
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict(
                             [(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'),
                              (u'NAME', u'no label'), (u'USE', u'no label')])
                          ])
        self.assertEqual(writer.json, [False])

    def test78_Leaflet_raster(self):
        """Dialog test: Leaflet  raster"""
        layer_path = get_test_data_path('layer', 'test.png')
        # style_path = get_test_data_path('style', '25d.qml')
        layer = load_layer(layer_path)
        # layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('full-screen')

        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict()])
        self.assertEqual(writer.json, [False])

    def test79_OL3_raster(self):
        """Dialog test: OL3 raster"""
        layer_path = get_test_data_path('layer', 'test.png')
        # style_path = get_test_data_path('style', '25d.qml')
        layer = load_layer(layer_path)
        # layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        # Export to web map
        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('canvas-size')

        self.dialog.ol3.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, OpenLayersWriter))
        expected_params = self.defaultParams()
        expected_params['Appearance']['Template'] = 'canvas-size'
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict()])
        self.assertEqual(writer.json, [False])

    def test81_Leaflet_heatmap(self):
        """Dialog test: Leaflet heatmap"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'heatmap.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict([(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'), (u'NAME', u'no label'), (u'USE', u'no label')])
                          ]
                         )
        self.assertEqual(writer.json, [False])
        self.dialog.ol3.click()

    def test80_OL3_heatmap(self):
        """Dialog test: OL3 heatmap"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'heatmap.qml')
        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.ol3.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, OpenLayersWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup,
                         [OrderedDict([(u'ID', u'no label'), (u'fk_region', u'no label'), (u'ELEV', u'no label'), (u'NAME', u'no label'), (u'USE', u'no label')])
                          ]
                         )
        self.assertEqual(writer.json, [False])
        QgsProject.instance().clear()

    # def test82_OL3_WMS(self):
        # """Dialog test: OL3 WMS"""
        # layer_url = (
            # 'contextualWMSLegend=0&crs=EPSG:3857&dpiMode=all&featureCount=10&format=image/png&layers=GBR_BGS_625k_BLT&styles=&url=http://ogc.bgs.ac.uk/cgi-bin/BGS_Bedrock_and_Superficial_Geology/wms?')
        # layer = load_wms_layer(layer_url, 'wms')

        # QgsProject.instance().addMapLayer(layer)

        # self.dialog = MainDialog(self.iface)
        # self.dialog.appearanceParams.itemWidget(
            # self.dialog.appearanceParams.findItems(
                # 'Extent',
                        # (Qt.MatchExactly | Qt.MatchRecursive))[0],
                # 1).setCurrentIndex(1)
        # self.setTemplate('full-screen')
        # self.dialog.ol3.click()

        # writer = self.dialog.createWriter()
        # self.assertTrue(isinstance(writer, OpenLayersWriter))
        # expected_params = self.defaultParams()
        # self.assertEqual(writer.params, expected_params)
        # self.assertEqual(writer.groups, {})
        # self.assertEqual(writer.layers, [layer])
        # self.assertEqual(writer.visible, [True])
        # self.assertEqual(writer.cluster, [False])
        # self.assertEqual(writer.popup,
                         # [OrderedDict()])
        # self.assertEqual(writer.json, [False])

    # def test83_Leaflet_WMS(self):
        # """Dialog test: Leaflet WMS"""
        # layer_url = (
            # 'contextualWMSLegend=0&crs=EPSG:3857&dpiMode=all&featureCount=10&format=image/png&layers=GBR_BGS_625k_BLT&styles=&url=http://ogc.bgs.ac.uk/cgi-bin/BGS_Bedrock_and_Superficial_Geology/wms?')
        # layer = load_wms_layer(layer_url, 'wms')

        # QgsProject.instance().addMapLayer(layer)

        # self.dialog = MainDialog(self.iface)
        # self.dialog.appearanceParams.itemWidget(
            # self.dialog.appearanceParams.findItems(
                # 'Extent',
                        # (Qt.MatchExactly | Qt.MatchRecursive))[0],
                # 1).setCurrentIndex(1)
        # self.setTemplate('full-screen')
        # self.dialog.leaflet.click()

        # writer = self.dialog.createWriter()
        # self.assertTrue(isinstance(writer, LeafletWriter))
        # expected_params = self.defaultParams()
        # self.assertEqual(writer.params, expected_params)
        # self.assertEqual(writer.groups, {})
        # self.assertEqual(writer.layers, [layer])
        # self.assertEqual(writer.visible, [True])
        # self.assertEqual(writer.cluster, [False])
        # self.assertEqual(writer.popup,
                         # [OrderedDict()])
        # self.assertEqual(writer.json, [False])

    def test84_Leaflet_rulebased(self):
        """Dialog test: Leaflet  rule-based"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_rule-based.qml')
        control_path = get_test_data_path(
            'control', 'leaflet_rule-based.html')

        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup, [OrderedDict(
            [('ID', 'header label'), ('fk_region', 'header label'), ('ELEV', 'header label'), ('NAME', 'header label'),
             ('USE', 'header label')])])
        self.assertEqual(writer.json, [False])

    def test85_OL3_rulebased(self):
        """Dialog test: OL3  rule-based"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_rule-based.qml')
        control_path = get_test_data_path(
            'control', 'ol3_rule-based.html')

        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.ol3.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, OpenLayersWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup, [OrderedDict(
            [('ID', 'header label'), ('fk_region', 'header label'), ('ELEV', 'header label'), ('NAME', 'header label'),
             ('USE', 'header label')])])
        self.assertEqual(writer.json, [False])

    def test86_Leaflet_labels(self):
        """Dialog test: Leaflet  labels"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_labels.qml')
        control_path = get_test_data_path(
            'control', 'leaflet_labels.html')

        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup, [OrderedDict(
            [('ID', 'header label'), ('fk_region', 'header label'), ('ELEV', 'header label'), ('NAME', 'header label'),
             ('USE', 'header label')])])
        self.assertEqual(writer.json, [False])

    def test87_OL3_labels(self):
        """Dialog test: OL3  labels"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_labels.qml')
        control_path = get_test_data_path(
            'control', 'ol3_labels.js')

        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.ol3.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, OpenLayersWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup, [OrderedDict(
            [('ID', 'header label'), ('fk_region', 'header label'), ('ELEV', 'header label'), ('NAME', 'header label'),
             ('USE', 'header label')])])
        self.assertEqual(writer.json, [False])

    # def test88_OL3_WMTS(self):
        # """Dialog test: OL3 WMTS"""
        # layer_url = (
            # 'contextualWMSLegend=0&crs=EPSG:3857&dpiMode=7&featureCount=10&format=image/jpeg&layers=EMAP8&styles=default&tileMatrixSet=GoogleMapsCompatible&url=http://wmts.nlsc.gov.tw/wmts')
        # layer = load_wms_layer(layer_url, 'wms')

        # QgsProject.instance().addMapLayer(layer)

        # self.dialog = MainDialog(self.iface)
        # self.dialog.appearanceParams.itemWidget(
            # self.dialog.appearanceParams.findItems(
                # 'Extent',
                        # (Qt.MatchExactly | Qt.MatchRecursive))[0],
                # 1).setCurrentIndex(1)
        # self.setTemplate('full-screen')
        # self.dialog.ol3.click()

        # writer = self.dialog.createWriter()
        # self.assertTrue(isinstance(writer, OpenLayersWriter))
        # expected_params = self.defaultParams()
        # self.assertEqual(writer.params, expected_params)
        # self.assertEqual(writer.groups, {})
        # self.assertEqual(writer.layers, [layer])
        # self.assertEqual(writer.visible, [True])
        # self.assertEqual(writer.cluster, [False])
        # self.assertEqual(writer.popup,
                         # [OrderedDict()])
        # self.assertEqual(writer.json, [False])

    # def test89_Leaflet_WMTS(self):
        # """Dialog test: Leaflet WMTS"""
        # layer_url = (
            # 'contextualWMSLegend=0&crs=EPSG:3857&dpiMode=7&featureCount=10&format=image/jpeg&layers=EMAP8&styles=default&tileMatrixSet=GoogleMapsCompatible&url=http://wmts.nlsc.gov.tw/wmts')
        # layer = load_wms_layer(layer_url, 'wms')

        # QgsProject.instance().addMapLayer(layer)

        # self.dialog = MainDialog(self.iface)
        # self.dialog.appearanceParams.itemWidget(
            # self.dialog.appearanceParams.findItems(
                # 'Extent',
                        # (Qt.MatchExactly | Qt.MatchRecursive))[0],
                # 1).setCurrentIndex(1)
        # self.setTemplate('full-screen')
        # self.dialog.leaflet.click()

        # writer = self.dialog.createWriter()
        # self.assertTrue(isinstance(writer, LeafletWriter))
        # expected_params = self.defaultParams()
        # self.assertEqual(writer.params, expected_params)
        # self.assertEqual(writer.groups, {})
        # self.assertEqual(writer.layers, [layer])
        # self.assertEqual(writer.visible, [True])
        # self.assertEqual(writer.cluster, [False])
        # self.assertEqual(writer.popup,
                         # [OrderedDict()])
        # self.assertEqual(writer.json, [False])

    def test90_Leaflet_scale_dependent(self):
        """Dialog test: Leaflet scale-dependent"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_scaledependent.qml')

        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup, [OrderedDict(
            [('ID', 'no label'), ('fk_region', 'no label'), ('ELEV', 'no label'), ('NAME', 'no label'),
             ('USE', 'no label')])])
        self.assertEqual(writer.json, [False])

    def test91_Leaflet_categorized_25d(self):
        """Dialog test: Leaflet categorized 2.5d"""
        layer_path = get_test_data_path('layer', 'lakes.shp')
        style_path = get_test_data_path('style', 'categorized_25d.qml')
        control_path = get_test_data_path(
            'control', 'leaflet_categorized_25d.html')

        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup, [OrderedDict([(u'cat', u'inline label'), (u'NAMES', u'no label'), (u'AREA_MI', u'inline label'), (u'xlabel', u'inline label'), (u'ylabel', u'inline label'), (u'rotation', u'inline label')])
                                        ])
        self.assertEqual(writer.json, [False])

    def test92_OL3_categorized_25d(self):
        """Dialog test: OL3 categorized 2.5d"""
        layer_path = get_test_data_path('layer', 'lakes.shp')
        style_path = get_test_data_path('style', 'categorized_25d.qml')
        control_path = get_test_data_path(
            'control', 'leaflet_categorized_25d.html')

        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.ol3.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, OpenLayersWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup, [OrderedDict([(u'cat', u'inline label'), (u'NAMES', u'no label'), (u'AREA_MI', u'inline label'), (u'xlabel', u'inline label'), (u'ylabel', u'inline label'), (u'rotation', u'inline label')])
                                        ])
        self.assertEqual(writer.json, [False])

    def test93_Leaflet_graduated_25d(self):
        """Dialog test: Leaflet graduated 2.5d"""
        layer_path = get_test_data_path('layer', 'lakes.shp')
        style_path = get_test_data_path('style', 'graduated_25d.qml')
        control_path = get_test_data_path(
            'control', 'leaflet_graduated_25d.html')

        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup, [OrderedDict([(u'cat', u'no label'), (u'NAMES', u'no label'), (u'AREA_MI', u'no label'), (u'xlabel', u'no label'), (u'ylabel', u'no label'), (u'rotation', u'no label')])
                                        ])
        self.assertEqual(writer.json, [False])

    def test94_ol3_graduated_25d(self):
        """Dialog test: OL3 graduated 2.5d"""
        layer_path = get_test_data_path('layer', 'lakes.shp')
        style_path = get_test_data_path('style', 'graduated_25d.qml')
        control_path = get_test_data_path(
            'control', 'leaflet_graduated_25d.html')

        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.ol3.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, OpenLayersWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup, [OrderedDict([(u'cat', u'no label'), (u'NAMES', u'no label'), (u'AREA_MI', u'no label'), (u'xlabel', u'no label'), (u'ylabel', u'no label'), (u'rotation', u'no label')])
                                        ])
        self.assertEqual(writer.json, [False])

    def test95_Leaflet_svg(self):
        """Dialog test: Leaflet SVG"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'svg.qml')
        control_path = get_test_data_path(
            'control', 'leaflet_svg.html')

        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup, [OrderedDict(
            [('ID', 'no label'), ('fk_region', 'no label'), ('ELEV', 'no label'), ('NAME', 'no label'),
             ('USE', 'no label')])])
        self.assertEqual(writer.json, [False])

    def test96_OL3_svg(self):
        """Dialog test: OL3  SVG"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'svg.qml')
        control_path = get_test_data_path(
            'control', 'ol3_svg.js')

        layer = load_layer(layer_path)
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent', (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.ol3.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, OpenLayersWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup, [OrderedDict(
            [('ID', 'no label'), ('fk_region', 'no label'), ('ELEV', 'no label'), ('NAME', 'no label'),
             ('USE', 'no label')])])
        self.assertEqual(writer.json, [False])

    def test97_Leaflet_layergroups(self):
        """Dialog test: Leaflet layer groups"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        control_path = get_test_data_path(
            'control', 'leaflet_groups.html')

        root = QgsProject.instance().layerTreeRoot()
        
        lyrGroup = root.addGroup("group1")

        layer = QgsVectorLayer(layer_path, 'airports', 'ogr')
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        cloned_layer = root.children()[0].clone()
        lyrGroup.addChildNode( cloned_layer)
        root.removeChildNode(root.children()[0])

        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.leaflet.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, LeafletWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {'group1': [layer]})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup, [{}])
        self.assertEqual(writer.json, [False])

    def test98_OL3_layergroups(self):
        """Dialog test: OL3 layer groups"""
        layer_path = get_test_data_path('layer', 'airports.shp')
        style_path = get_test_data_path('style', 'airports_single.qml')
        control_path = get_test_data_path(
            'control', 'leaflet_groups.html')

        root = QgsProject.instance().layerTreeRoot()
        
        lyrGroup = root.addGroup("group1")

        layer = QgsVectorLayer(layer_path, 'airports', 'ogr')
        layer.loadNamedStyle(style_path)

        QgsProject.instance().addMapLayer(layer)

        cloned_layer = root.children()[0].clone()
        lyrGroup.addChildNode( cloned_layer)
        root.removeChildNode(root.children()[0])

        self.dialog = MainDialog(self.iface)
        self.dialog.appearanceParams.itemWidget(
            self.dialog.appearanceParams.findItems(
                'Extent',
                        (Qt.MatchExactly | Qt.MatchRecursive))[0],
                1).setCurrentIndex(1)
        self.setTemplate('full-screen')
        self.dialog.ol3.click()

        writer = self.dialog.createWriter()
        self.assertTrue(isinstance(writer, OpenLayersWriter))
        expected_params = self.defaultParams()
        self.assertEqual(writer.params, expected_params)
        self.assertEqual(writer.groups, {'group1': [layer]})
        self.assertEqual(writer.layers, [layer])
        self.assertEqual(writer.visible, [True])
        self.assertEqual(writer.cluster, [False])
        self.assertEqual(writer.popup, [{}])
        self.assertEqual(writer.json, [False])

    def test100_setStateToParams(self):
        """Test that setting state to match parameters works"""
        params=getDefaultParams()
        self.dialog.setStateToParams(params)

        writer = self.dialog.createWriter()
        self.maxDiff = 1000000000
        self.assertEqual(dict(writer.params),params)
        # change some parameters (one of each type)
        params['Appearance']['Add layers list'] = 'Collapsed'
        params['Data export']['Minify GeoJSON files'] = False
        params['Data export']['Precision'] = '4'
        self.dialog.setStateToParams(params)

        writer = self.dialog.createWriter()
        self.assertEqual(writer.params,params)

    def test101_setStateToWriter(self):
        """Test setting state to writer works"""
        writer = LeafletWriter()
        writer.params = getDefaultParams()
        # change some parameters
        writer.params['Appearance']['Add layers list'] = 'Collapsed'
        writer.params['Data export']['Minify GeoJSON files'] = False
        writer.params['Data export']['Precision'] = '4'

        self.dialog.setStateToWriter(writer)

        new_writer = self.dialog.createWriter()
        self.maxDiff = 1000000000
        self.assertTrue( isinstance(new_writer, LeafletWriter))
        self.assertEqual(dict(new_writer.params),writer.params)







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
    suite.addTests(unittest.makeSuite(qgis2web_classDialogTest))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
