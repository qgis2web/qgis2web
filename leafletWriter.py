# -*- coding: utf-8 -*-
"""
/***************************************************************************
 qgis2leaf
                                 A QGIS plugin
 QGIS to Leaflet creation program
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

from qgis.core import *
import qgis.utils
import os
from urlparse import parse_qs
import time
import re
from basemaps import basemapLeaflet, basemapAttributions
from leafletFileScripts import *
from leafletLayerScripts import *
from leafletScriptStrings import *
from utils import ALL_ATTRIBUTES, removeSpaces


def writeLeaflet(iface, outputProjectFileName, layer_list, visible,
                 cluster, json, params, popup):
    legends = {}
    canvas = iface.mapCanvas()
    project = QgsProject.instance()
    mapSettings = canvas.mapSettings()
    title = project.title()
    pluginDir = os.path.dirname(os.path.realpath(__file__))
    outputProjectFileName = os.path.join(outputProjectFileName,
                                         'qgis2web_' + unicode(time.time()))
    outputIndex = os.path.join(outputProjectFileName, 'index.html')
    cluster_num = 1

    cleanUnusedFields = params["Data export"]["Delete unused fields"]
    mapLibLocation = params["Data export"]["Mapping library location"]
    minify = params["Data export"]["Minify GeoJSON files"]
    extent = params["Scale/Zoom"]["Extent"]
    minZoom = params["Scale/Zoom"]["Min zoom level"]
    maxZoom = params["Scale/Zoom"]["Max zoom level"]
    basemapList = params["Appearance"]["Base layer"]
    matchCRS = params["Appearance"]["Match project CRS"]
    addressSearch = params["Appearance"]["Add address search"]
    locate = params["Appearance"]["Geolocate user"]
    measure = params["Appearance"]["Add measure tool"]
    highlight = params["Appearance"]["Highlight features"]
    popupsOnHover = params["Appearance"]["Show popups on hover"]
    template = params["Appearance"]["Template"]
    precision = params["Data export"]["Precision"]

    if not cleanUnusedFields:
        usedFields = [ALL_ATTRIBUTES] * len(popup)
    else:
        usedFields = popup

    QgsApplication.initQgis()

    dataStore, cssStore = writeFoldersAndFiles(pluginDir,
                                               outputProjectFileName, cluster,
                                               measure, matchCRS,
                                               canvas, mapLibLocation, locate)
    writeCSS(cssStore, mapSettings.backgroundColor().name())

    wfsLayers = ""
    scaleDependentLayers = ""
    new_src = ""
    crs = QgsCoordinateReferenceSystem.EpsgCrsId
    exp_crs = QgsCoordinateReferenceSystem(4326,
                                           crs)
    for i, jsonEncode, eachPopup in zip(layer_list, json, popup):
        rawLayerName = i.name()
        safeLayerName = re.sub('[\W_]+', '', rawLayerName)
        dataPath = os.path.join(dataStore, 'json_' + safeLayerName)
        tmpFileName = dataPath + '.json'
        layerFileName = dataPath + '.js'
        if i.providerType() != 'WFS' or jsonEncode is True and i:
            if i.type() == QgsMapLayer.VectorLayer:
                exportJSONLayer(i, eachPopup, precision, tmpFileName, exp_crs,
                                layerFileName, safeLayerName, minify)
                new_src += jsonScript(safeLayerName)

            elif i.type() == QgsMapLayer.RasterLayer:
                if i.dataProvider().name() != "wms":
                    exportRasterLayer(i, safeLayerName, dataPath)
        if i.hasScaleBasedVisibility():
            scaleDependentLayers += scaleDependentLayerScript(i, safeLayerName)
    if scaleDependentLayers != "":
        scaleDependentLayers = scaleDependentScript(scaleDependentLayers)

    try:
        crsSrc = mapSettings.destinationCrs()
    except:
        crsSrc = canvas.mapRenderer().destinationCrs()
    crsAuthId = crsSrc.authid()
    crsProj4 = crsSrc.toProj4()
    middle = openScript()
    if highlight or popupsOnHover:
        middle += highlightScript(highlight, popupsOnHover,
                                  mapSettings.selectionColor().name())
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
        middle += mapScript(extent, matchCRS, crsAuthId, measure,
                            maxZoom, minZoom, bounds)
    else:
        if matchCRS and crsAuthId != 'EPSG:4326':
            middle += crsScript(crsAuthId, crsProj4)
        middle += mapScript(extent, matchCRS, crsAuthId, measure,
                            maxZoom, minZoom, 0)
    middle += featureGroupsScript()
    if (len(basemapList) == 0 or matchCRS):
        basemapText = ""
    else:
        basemapText = basemapsScript(basemapList, maxZoom)
    layerOrder = layerOrderScript(extent)
    new_src += middle
    new_src += basemapText
    new_src += layerOrder

    for count, i in enumerate(layer_list):
        rawLayerName = i.name()
        safeLayerName = re.sub('[\W_]+', '', rawLayerName)
        if i.type() == QgsMapLayer.VectorLayer:
            (new_src,
             legends,
             wfsLayers) = writeVectorLayer(i, safeLayerName, usedFields,
                                           highlight, popupsOnHover, popup,
                                           count, outputProjectFileName,
                                           wfsLayers, cluster, cluster_num,
                                           visible, json, legends, new_src)
        elif i.type() == QgsMapLayer.RasterLayer:
            if i.dataProvider().name() == "wms":
                d = parse_qs(i.source())
                wms_url = d['url'][0]
                wms_layer = d['layers'][0]
                wms_format = d['format'][0]
                wms_crs = d['crs'][0]
                new_obj = wmsScript(safeLayerName, wms_url,
                                    wms_layer, wms_format)
            else:
                out_raster_name = 'data/' + 'json_' + safeLayerName + '.png'
                pt2 = i.extent()
                crsSrc = i.crs()
                crsDest = QgsCoordinateReferenceSystem(4326)
                xform = QgsCoordinateTransform(crsSrc, crsDest)
                pt3 = xform.transform(pt2)
                bbox_canvas2 = [pt3.yMinimum(), pt3.yMaximum(),
                                pt3.xMinimum(), pt3.xMaximum()]
                bounds2 = '[[' + unicode(pt3.yMinimum()) + ','
                bounds2 += unicode(pt3.xMinimum()) + '],['
                bounds2 += unicode(pt3.yMaximum()) + ','
                bounds2 += unicode(pt3.xMaximum()) + ']]'
                new_obj = rasterScript(safeLayerName, out_raster_name, bounds2)
            if visible[count]:
                new_obj += """
        raster_group.addLayer(overlay_""" + safeLayerName + """);"""
            new_src += new_obj
    new_src += """
        raster_group.addTo(map);
        feature_group.addTo(map);"""
    new_src += scaleDependentLayers
    if title != "":
        titleStart = titleSubScript(title)
        new_src += titleStart
    if addressSearch:
        address_text = addressSearchScript()
        new_src += address_text

    if params["Appearance"]["Add layers list"]:
        if len(basemapList) == 0 or matchCRS:
            controlStart = """
        var baseMaps = {};"""
        else:
            comma = ""
            controlStart = """
        var baseMaps = {"""
            for count, basemap in enumerate(basemapList):
                controlStart += comma + "'" + unicode(basemap.text())
                controlStart += "': basemap" + unicode(count)
                comma = ", "
            controlStart += "};"
        if len(basemapList) == 0:
            controlStart += """
            L.control.layers({},{"""
        else:
            controlStart += """
            L.control.layers(baseMaps,{"""
        new_src += controlStart

        for i, clustered in zip(reversed(layer_list), reversed(cluster)):
            try:
                testDump = i.rendererV2().dump()
                rawLayerName = i.name()
                safeLayerName = re.sub('[\W_]+', '', rawLayerName)
                if i.type() == QgsMapLayer.VectorLayer:
                    if (clustered and
                            i.geometryType() == QGis.Point):
                        new_layer = "'" + legends[safeLayerName] + "'"
                        + ": cluster_group""" + safeLayerName + "JSON,"
                    else:
                        new_layer = "'" + legends[safeLayerName] + "':"
                        new_layer += " json_" + safeLayerName + "JSON,"
                    new_src += new_layer
                elif i.type() == QgsMapLayer.RasterLayer:
                    new_layer = '"' + rawLayerName + '"' + ": overlay_"
                    new_layer += safeLayerName + ""","""
                    new_src += new_layer
            except:
                pass
        controlEnd = "},{collapsed:false}).addTo(map);"

        new_src += controlEnd

    if locate:
        end = locateScript()
    else:
        end = ''
    if params["Appearance"]["Add scale bar"]:
        end += """
        L.control.scale({options: {position: 'bottomleft', """
        end += "maxWidth: 100, metric: true, imperial: false, "
        end += "updateWhenIdle: false}}).addTo(map);"
    end += endHTMLscript(wfsLayers)
    new_src += end
    writeHTMLstart(outputIndex, title, cluster, addressSearch, measure,
                   matchCRS, canvas, mapLibLocation, new_src, template)
    return outputIndex
