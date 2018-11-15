# -*- coding: utf-8 -*-
"""
/***************************************************************************
 qgis2web
 (c) Tom Chadwin

 leafletWriter.py original by:
                             -------------------
        begin                : 2014-04-29
        copyright            : (C) 2013 by Riccardo Klinger
        email                : riccardo.klinger@geolicious.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.core import (QgsApplication,
                       QgsProject,
                       QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsMapLayer,
                       QgsMessageLog)
import traceback
from PyQt5.QtCore import (Qt,
                          QObject)
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QApplication
import os
from datetime import datetime
import re
from qgis2web.leafletFileScripts import (writeFoldersAndFiles,
                                         writeCSS,
                                         writeHTMLstart)
from qgis2web.leafletLayerScripts import writeVectorLayer
from qgis2web.leafletScriptStrings import (jsonScript,
                                           scaleDependentLabelScript,
                                           mapScript,
                                           featureGroupsScript,
                                           extentScript,
                                           rasterScript,
                                           wmsScript,
                                           scaleDependentLayerScript,
                                           addressSearchScript,
                                           endHTMLscript,
                                           addLayersList,
                                           highlightScript,
                                           crsScript,
                                           scaleBar,
                                           scaleDependentScript,
                                           titleSubScript,
                                           getVTStyles,
                                           getVTLabels)
from qgis2web.utils import (ALL_ATTRIBUTES, PLACEMENT, exportVector,
                            exportRaster, safeName)
from qgis2web.writer import (Writer,
                             WriterResult,
                             translator)
from qgis2web.feedbackDialog import Feedback


class LeafletWriter(Writer):
    """
    Writer for creation of web maps based on the Leaflet
    JavaScript library.
    """

    def __init__(self):
        super(LeafletWriter, self).__init__()

    @classmethod
    def type(cls):
        return 'leaflet'

    @classmethod
    def name(cls):
        return QObject.tr(translator, 'Leaflet')

    def write(self, iface, dest_folder, feedback=None):
        if not feedback:
            feedback = Feedback()

        feedback.showFeedback('Creating Leaflet map...')
        self.preview_file = self.writeLeaflet(
            iface,
            feedback,
            layer_list=self.layers,
            popup=self.popup,
            visible=self.visible,
            json=self.json,
            cluster=self.cluster,
            getFeatureInfo=self.getFeatureInfo,
            params=self.params,
            folder=dest_folder)
        result = WriterResult()
        result.index_file = self.preview_file
        result.folder = os.path.dirname(self.preview_file)
        for dirpath, dirnames, filenames in os.walk(result.folder):
            result.files.extend([os.path.join(dirpath, f) for f in filenames])
        return result

    @classmethod
    def writeLeaflet(
            cls, iface, feedback, folder,
            layer_list, visible, cluster,
            json, getFeatureInfo, params, popup):
        outputProjectFileName = folder
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        legends = {}
        mapUnitLayers = []
        canvas = iface.mapCanvas()
        project = QgsProject.instance()
        mapSettings = canvas.mapSettings()
        title = project.title()
        pluginDir = os.path.dirname(os.path.realpath(__file__))
        stamp = datetime.now().strftime("%Y_%m_%d-%H_%M_%S_%f")
        outputProjectFileName = os.path.join(outputProjectFileName,
                                             'qgis2web_' + unicode(stamp))
        outputIndex = os.path.join(outputProjectFileName, 'index.html')

        minify = params["Data export"]["Minify GeoJSON files"]
        precision = params["Data export"]["Precision"]
        extent = params["Scale/Zoom"]["Extent"]
        minZoom = params["Scale/Zoom"]["Min zoom level"]
        maxZoom = params["Scale/Zoom"]["Max zoom level"]
        restrictToExtent = params["Scale/Zoom"]["Restrict to extent"]
        matchCRS = params["Appearance"]["Match project CRS"]
        addressSearch = params["Appearance"]["Add address search"]
        locate = params["Appearance"]["Geolocate user"]
        measure = params["Appearance"]["Measure tool"]
        highlight = params["Appearance"]["Highlight on hover"]
        layerSearch = params["Appearance"]["Layer search"]
        popupsOnHover = params["Appearance"]["Show popups on hover"]
        template = params["Appearance"]["Template"]
        widgetAccent = params["Appearance"]["Widget Icon"]
        widgetBackground = params["Appearance"]["Widget Background"]

        usedFields = [ALL_ATTRIBUTES] * len(popup)

        QgsApplication.initQgis()

        dataStore, cssStore = writeFoldersAndFiles(pluginDir, feedback,
                                                   outputProjectFileName,
                                                   cluster, measure,
                                                   matchCRS, layerSearch,
                                                   canvas, addressSearch,
                                                   locate)
        writeCSS(cssStore, mapSettings.backgroundColor().name(), feedback,
                 widgetAccent, widgetBackground)

        wfsLayers = ""
        labelCode = ""
        vtLabels = {}
        vtStyles = {}
        useMultiStyle = False
        useHeat = False
        useVT = False
        useShapes = False
        useOSMB = False
        useWMS = False
        useWMTS = False
        useRaster = False
        scaleDependentLayers = ""
        labelVisibility = ""
        new_src = ""
        jsons = ""
        crs = QgsCoordinateReferenceSystem.EpsgCrsId
        exp_crs = QgsCoordinateReferenceSystem(4326, crs)
        lyrCount = 0
        for layer, jsonEncode, eachPopup, clst in zip(layer_list, json,
                                                      popup, cluster):
            rawLayerName = layer.name()
            safeLayerName = safeName(rawLayerName) + "_" + unicode(lyrCount)
            vts = layer.customProperty("VectorTilesReader/vector_tile_url")
            if layer.providerType() != 'WFS' or jsonEncode is True:
                if layer.type() == QgsMapLayer.VectorLayer and vts is None:
                    feedback.showFeedback('Exporting %s to JSON...' %
                                          layer.name())
                    exportVector(layer, safeLayerName, dataStore,
                                 restrictToExtent, iface, extent, precision,
                                 exp_crs, minify)
                    jsons += jsonScript(safeLayerName)
                    scaleDependentLabels = \
                        scaleDependentLabelScript(layer, safeLayerName)
                    labelVisibility += scaleDependentLabels
                    feedback.completeStep()

                elif layer.type() == QgsMapLayer.RasterLayer:
                    if layer.dataProvider().name() != "wms":
                        layersFolder = os.path.join(outputProjectFileName,
                                                    "data")
                        exportRaster(layer, lyrCount, layersFolder,
                                     feedback, iface, matchCRS)
            if layer.hasScaleBasedVisibility():
                scaleDependentLayers += scaleDependentLayerScript(
                    layer, safeLayerName, clst)
            lyrCount += 1
        if scaleDependentLayers != "":
            scaleDependentLayers = scaleDependentScript(scaleDependentLayers)

        crsSrc = mapSettings.destinationCrs()
        crsAuthId = crsSrc.authid()
        crsProj4 = crsSrc.toProj4()
        middle = """
        """
        if highlight or popupsOnHover:
            selectionColor = mapSettings.selectionColor().name()
            middle += highlightScript(highlight, popupsOnHover, selectionColor)
        if extent == "Canvas extent":
            pt0 = canvas.extent()
            crsDest = QgsCoordinateReferenceSystem(4326)
            try:
                xform = QgsCoordinateTransform(crsSrc, crsDest,
                                               QgsProject.instance())
            except:
                xform = QgsCoordinateTransform(crsSrc, crsDest)
            pt1 = xform.transformBoundingBox(pt0)
            bbox_canvas = [pt1.yMinimum(), pt1.yMaximum(),
                           pt1.xMinimum(), pt1.xMaximum()]
            bounds = '[[' + unicode(pt1.yMinimum()) + ','
            bounds += unicode(pt1.xMinimum()) + '],['
            bounds += unicode(pt1.yMaximum()) + ','
            bounds += unicode(pt1.xMaximum()) + ']]'
            if matchCRS and crsAuthId != 'EPSG:4326':
                middle += crsScript(crsAuthId, crsProj4)
        else:
            bounds = 0
            if matchCRS and crsAuthId != 'EPSG:4326':
                middle += crsScript(crsAuthId, crsProj4)
        middle += mapScript(extent, matchCRS, crsAuthId, measure, maxZoom,
                            minZoom, bounds, locate)
        middle += featureGroupsScript()
        extentCode = extentScript(extent, restrictToExtent)
        new_src += middle
        new_src += extentCode

        for count, layer in enumerate(layer_list):
            rawLayerName = layer.name()
            safeLayerName = safeName(rawLayerName) + "_" + unicode(count)
            if layer.type() == QgsMapLayer.VectorLayer:
                (new_src,
                 legends,
                 wfsLayers,
                 labelCode,
                 vtLabels,
                 vtStyles,
                 useMapUnits,
                 useMultiStyle,
                 useHeat,
                 useVT,
                 useShapes,
                 useOSMB) = writeVectorLayer(layer, safeLayerName,
                                             usedFields[count], highlight,
                                             popupsOnHover, popup[count],
                                             outputProjectFileName,
                                             wfsLayers, cluster[count],
                                             visible[count], json[count],
                                             legends, new_src, canvas, count,
                                             restrictToExtent, extent,
                                             feedback, labelCode, vtLabels,
                                             vtStyles, useMultiStyle, useHeat,
                                             useVT, useShapes, useOSMB)
                if useMapUnits:
                    mapUnitLayers.append(safeLayerName)
            elif layer.type() == QgsMapLayer.RasterLayer:
                if layer.dataProvider().name() == "wms":
                    feedback.showFeedback('Writing %s as WMS layer...' %
                                          layer.name())
                    new_obj, useWMS, useWMTS = wmsScript(layer, safeLayerName,
                                                         useWMS, useWMTS,
                                                         getFeatureInfo[count])
                    feedback.completeStep()
                else:
                    useRaster = True
                    feedback.showFeedback('Writing %s as raster layer...' %
                                          layer.name())
                    new_obj = rasterScript(layer, safeLayerName)
                    feedback.completeStep()
                if visible[count]:
                    new_obj += """
        map.addLayer(layer_""" + safeLayerName + """);"""
                new_src += new_obj
        the_src = new_src
        new_src = jsons + """
        <script>"""
        if len(mapUnitLayers) > 0:
            new_src += """
        var m2px = 1;
        function newM2px() {
            var centerLatLng = map.getCenter();
            var pointC = map.latLngToContainerPoint(centerLatLng);
            var pointX = [pointC.x + 100, pointC.y];

            var latLngC = map.containerPointToLatLng(pointC);
            var latLngX = map.containerPointToLatLng(pointX);

            var distanceX = latLngC.distanceTo(latLngX)/100;

            reciprocal = 1 / distanceX;
            m2px = reciprocal;
        }
        function geoStyle(m) {
            return Math.ceil(m * m2px);
        }"""
        new_src += getVTStyles(vtStyles)
        new_src += getVTLabels(vtLabels)
        new_src += the_src + scaleDependentLayers
        if title != "":
            titleStart = unicode(titleSubScript(title))
            new_src += unicode(titleStart)
        if addressSearch:
            address_text = addressSearchScript()
            new_src += address_text

        if (params["Appearance"]["Add layers list"] and
                params["Appearance"]["Add layers list"] != "" and
                params["Appearance"]["Add layers list"] != "None"):
            new_src += addLayersList(
                [], matchCRS, layer_list, cluster, legends,
                params["Appearance"]["Add layers list"] == "Expanded")
        if project.readBoolEntry("ScaleBar", "/Enabled", False)[0]:
            # placement = project.readNumEntry("ScaleBar", "/Placement", 0)[0]
            # placement = PLACEMENT[placement]
            # end = scaleBar(placement)
            end = scaleBar()
        else:
            end = ''
        layerType = "layer"
        try:
            if cluster[count]:
                layerType = "cluster"
        except:
            pass
        searchLayer = "%s_%s" % (layerType,
                                 params["Appearance"]["Search layer"])
        labelList = []
        for count, layer in enumerate(layer_list):
            vts = layer.customProperty("VectorTilesReader/vector_tile_url")
            safeLayerName = re.sub(r'[\W_]+', '',
                                   layer.name()) + "_" + unicode(count)
            if (layer.type() == QgsMapLayer.VectorLayer and vts is None):
                labelling = layer.labeling()
                if labelling is not None:
                    palyr = labelling.settings()
                    if palyr.fieldName and palyr.fieldName != "":
                        labelList.append("layer_%s" % safeLayerName)
        labelsList = ",".join(labelList)
        end += endHTMLscript(wfsLayers, layerSearch, labelCode,
                             labelVisibility, searchLayer, useHeat, useRaster,
                             labelsList, mapUnitLayers)
        new_src += end
        try:
            writeHTMLstart(outputIndex, title, cluster, addressSearch,
                           measure, matchCRS, layerSearch, canvas,
                           locate, new_src, template, feedback, useMultiStyle,
                           useHeat, useShapes, useOSMB, useWMS, useWMTS, useVT)
        except Exception as e:
            QgsMessageLog.logMessage(traceback.format_exc(), "qgis2web",
                                     level=QgsMessageLog.CRITICAL)
            QApplication.restoreOverrideCursor()
        finally:
            QApplication.restoreOverrideCursor()
        return outputIndex
