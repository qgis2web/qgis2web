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
import qgis.utils
from PyQt4.QtCore import (Qt,
                          QObject)
from PyQt4.QtGui import QApplication, QCursor
import os
from datetime import datetime
import re
from basemaps import basemapLeaflet
from leafletFileScripts import (writeFoldersAndFiles,
                                writeCSS,
                                writeHTMLstart)
from leafletLayerScripts import (exportJSONLayer,
                                 writeVectorLayer)
from leafletScriptStrings import (jsonScript,
                                  scaleDependentLabelScript,
                                  mapScript,
                                  featureGroupsScript,
                                  extentScript,
                                  rasterScript,
                                  wmsScript,
                                  basemapsScript,
                                  scaleDependentLayerScript,
                                  addressSearchScript,
                                  endHTMLscript,
                                  addLayersList,
                                  highlightScript,
                                  crsScript,
                                  scaleBar,
                                  scaleDependentScript,
                                  titleSubScript)
from utils import ALL_ATTRIBUTES, PLACEMENT, removeSpaces, exportRaster
from writer import (Writer,
                    WriterResult,
                    translator)
from feedbackDialog import Feedback


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
        self.preview_file = self.writeLeaflet(iface, feedback,
                                              layer_list=self.layers,
                                              popup=self.popup,
                                              visible=self.visible,
                                              json=self.json,
                                              cluster=self.cluster,
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
            json, params, popup):
        outputProjectFileName = folder
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        legends = {}
        canvas = iface.mapCanvas()
        project = QgsProject.instance()
        mapSettings = canvas.mapSettings()
        title = project.title()
        pluginDir = os.path.dirname(os.path.realpath(__file__))
        stamp = datetime.now().strftime("%Y_%m_%d-%H_%M_%S_%f")
        outputProjectFileName = os.path.join(outputProjectFileName,
                                             'qgis2web_' + unicode(stamp))
        outputIndex = os.path.join(outputProjectFileName, 'index.html')

        mapLibLocation = params["Data export"]["Mapping library location"]
        minify = params["Data export"]["Minify GeoJSON files"]
        precision = params["Data export"]["Precision"]
        extent = params["Scale/Zoom"]["Extent"]
        minZoom = params["Scale/Zoom"]["Min zoom level"]
        maxZoom = params["Scale/Zoom"]["Max zoom level"]
        restrictToExtent = params["Scale/Zoom"]["Restrict to extent"]
        basemapList = params["Appearance"]["Base layer"]
        matchCRS = params["Appearance"]["Match project CRS"]
        addressSearch = params["Appearance"]["Add address search"]
        locate = params["Appearance"]["Geolocate user"]
        measure = params["Appearance"]["Measure tool"]
        highlight = params["Appearance"]["Highlight on hover"]
        layerSearch = params["Appearance"]["Layer search"]
        popupsOnHover = params["Appearance"]["Show popups on hover"]
        template = params["Appearance"]["Template"]

        usedFields = [ALL_ATTRIBUTES] * len(popup)

        QgsApplication.initQgis()

        dataStore, cssStore = writeFoldersAndFiles(pluginDir, feedback,
                                                   outputProjectFileName,
                                                   cluster, measure,
                                                   matchCRS, layerSearch,
                                                   canvas, mapLibLocation,
                                                   addressSearch, locate)
        writeCSS(cssStore, mapSettings.backgroundColor().name(), feedback)

        wfsLayers = ""
        scaleDependentLayers = ""
        labelVisibility = ""
        new_src = ""
        crs = QgsCoordinateReferenceSystem.EpsgCrsId
        exp_crs = QgsCoordinateReferenceSystem(4326, crs)
        lyrCount = 0
        for layer, jsonEncode, eachPopup in zip(layer_list, json, popup):
            rawLayerName = layer.name()
            safeLayerName = re.sub(
                '[\W_]+', '', rawLayerName) + unicode(lyrCount)
            dataPath = os.path.join(dataStore, safeLayerName)
            tmpFileName = dataPath + '.json'
            layerFileName = dataPath + '.js'
            if layer.providerType() != 'WFS' or jsonEncode is True and layer:
                if layer.type() == QgsMapLayer.VectorLayer:
                    feedback.showFeedback('Exporting %s to JSON...' %
                                          layer.name())
                    exportJSONLayer(layer, eachPopup, precision, tmpFileName,
                                    exp_crs, layerFileName,
                                    safeLayerName, minify, canvas,
                                    restrictToExtent, iface, extent)
                    new_src += jsonScript(safeLayerName)
                    scaleDependentLabels =\
                        scaleDependentLabelScript(layer, safeLayerName)
                    labelVisibility += scaleDependentLabels
                    feedback.completeStep()

                elif layer.type() == QgsMapLayer.RasterLayer:
                    if layer.dataProvider().name() != "wms":
                        layersFolder = os.path.join(outputProjectFileName,
                                                    "data")
                        exportRaster(layer, lyrCount, layersFolder, feedback)
            if layer.hasScaleBasedVisibility():
                scaleDependentLayers += scaleDependentLayerScript(
                    layer, safeLayerName)
            lyrCount += 1
        if scaleDependentLayers != "":
            scaleDependentLayers = scaleDependentScript(scaleDependentLayers)

        crsSrc = mapSettings.destinationCrs()
        crsAuthId = crsSrc.authid()
        crsProj4 = crsSrc.toProj4()
        middle = """
        <script>"""
        if highlight or popupsOnHover:
            selectionColor = mapSettings.selectionColor().name()
            middle += highlightScript(highlight, popupsOnHover, selectionColor)
        if extent == "Canvas extent":
            pt0 = canvas.extent()
            crsDest = QgsCoordinateReferenceSystem(4326)
            xform = QgsCoordinateTransform(crsSrc, crsDest)
            pt1 = xform.transform(pt0)
            bbox_canvas = [pt1.yMinimum(), pt1.yMaximum(),
                           pt1.xMinimum(), pt1.xMaximum()]
            bounds = '[[' + unicode(pt1.yMinimum()) + ','
            bounds += unicode(pt1.xMinimum()) + '],['
            bounds += unicode(pt1.yMaximum()) + ','
            bounds += unicode(pt1.xMaximum()) + ']]'
            if matchCRS and crsAuthId != 'EPSG:4326':
                middle += crsScript(crsAuthId, crsProj4)
            middle += mapScript(extent, matchCRS, crsAuthId, measure, maxZoom,
                                minZoom, bounds, locate)
        else:
            bounds = ""
            if matchCRS and crsAuthId != 'EPSG:4326':
                middle += crsScript(crsAuthId, crsProj4)
            middle += mapScript(extent, matchCRS, crsAuthId, measure, maxZoom,
                                minZoom, 0, locate)
        middle += featureGroupsScript()
        if (len(basemapList) == 0 or matchCRS):
            basemapText = ""
        else:
            basemapText = basemapsScript(basemapList, maxZoom)
        extentCode = extentScript(extent, restrictToExtent)
        new_src += middle
        new_src += basemapText
        new_src += extentCode

        for count, layer in enumerate(layer_list):
            rawLayerName = layer.name()
            safeLayerName = re.sub('[\W_]+', '', rawLayerName) + unicode(count)
            if layer.type() == QgsMapLayer.VectorLayer:
                (new_src,
                 legends,
                 wfsLayers) = writeVectorLayer(layer, safeLayerName,
                                               usedFields[count], highlight,
                                               popupsOnHover, popup[count],
                                               outputProjectFileName,
                                               wfsLayers, cluster[count],
                                               visible[count], json[count],
                                               legends, new_src,
                                               canvas, count, restrictToExtent,
                                               extent, feedback)
            elif layer.type() == QgsMapLayer.RasterLayer:
                if layer.dataProvider().name() == "wms":
                    feedback.showFeedback('Writing %s as WMS layer...' %
                                          layer.name())
                    new_obj = wmsScript(layer, safeLayerName)
                    feedback.completeStep()
                else:
                    feedback.showFeedback('Writing %s as raster layer...' %
                                          layer.name())
                    new_obj = rasterScript(layer, safeLayerName)
                    feedback.completeStep()
                if visible[count]:
                    new_obj += """
        map.addLayer(overlay_""" + safeLayerName + """);"""
                    new_src += new_obj
        new_src += scaleDependentLayers
        if title != "":
            titleStart = unicode(titleSubScript(title).decode("utf-8"))
            new_src += unicode(titleStart)
        if addressSearch:
            address_text = addressSearchScript()
            new_src += address_text

        if (params["Appearance"]["Add layers list"] and
                params["Appearance"]["Add layers list"] != "" and
                params["Appearance"]["Add layers list"] != "None"):
            new_src += addLayersList(
                basemapList, matchCRS, layer_list, cluster, legends,
                params["Appearance"]["Add layers list"] == "Expanded")
        if project.readBoolEntry("ScaleBar", "/Enabled", False)[0]:
            placement = project.readNumEntry("ScaleBar", "/Placement", 0)[0]
            placement = PLACEMENT[placement]
            end = scaleBar(placement)
        else:
            end = ''
        searchLayer = "layer_%s" % params["Appearance"]["Search layer"]
        end += endHTMLscript(
            wfsLayers, layerSearch, labelVisibility, searchLayer)
        new_src += end
        try:
            writeHTMLstart(outputIndex, title, cluster, addressSearch,
                           measure, matchCRS, layerSearch, canvas,
                           mapLibLocation, locate, new_src, template, feedback)
        except Exception as e:
            QgsMessageLog.logMessage(traceback.format_exc(), "qgis2web",
                                     level=QgsMessageLog.CRITICAL)
        finally:
            QApplication.restoreOverrideCursor()
        return outputIndex
