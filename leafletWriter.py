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

from PyQt4.QtCore import QSize
import processing
from qgis.core import *
import qgis.utils
import os
from urlparse import parse_qs
import time
import tempfile
import re
from basemaps import basemapLeaflet, basemapAttributions
from leafletFileScripts import *
from leafletLayerScripts import *
from leafletScriptStrings import *
from utils import ALL_ATTRIBUTES, removeSpaces, writeTmpLayer, getUsedFields

basemapAddresses = basemapLeaflet()
basemapAttributions = basemapAttributions()


def writeLeaflet(iface, outputProjectFileName, width, height, full, layer_list,
                 visible, opacity_raster, cluster, labelhover, selected, json,
                 params, popup):
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
    scaleDependent = (params["Scale/Zoom"]
                            ["Use layer scale dependent visibility"])
    basemapName = params["Appearance"]["Base layer"]
    matchCRS = params["Appearance"]["Match project CRS"]
    addressSearch = params["Appearance"]["Add address search"]
    locate = params["Appearance"]["Geolocate user"]
    measure = params["Appearance"]["Add measure tool"]
    highlight = params["Appearance"]["Highlight features"]
    popupsOnHover = params["Appearance"]["Show popups on hover"]
    template = params["Appearance"]["Template"]

    if not cleanUnusedFields:
        usedFields = [ALL_ATTRIBUTES] * len(popup)
    else:
        usedFields = popup

    QgsApplication.initQgis()

    dataStore, cssStore = writeFoldersAndFiles(pluginDir,
                                               outputProjectFileName, cluster,
                                               measure, matchCRS,
                                               canvas, mapLibLocation, locate)
    writeCSS(cssStore, full, height, width,
             mapSettings.backgroundColor().name())

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
            precision = params["Data export"]["Precision"]
            if i.type() == QgsMapLayer.VectorLayer:
                cleanedLayer = writeTmpLayer(i, eachPopup)
                writer = qgis.core.QgsVectorFileWriter
                options = "COORDINATE_PRECISION=" + unicode(precision)
                writer.writeAsVectorFormat(cleanedLayer, tmpFileName, 'utf-8',
                                           exp_crs, 'GeoJson', selected,
                                           layerOptions=[options])

                with open(layerFileName, "w") as f2:
                    f2.write("var json_" + unicode(safeLayerName) + "=")
                    with open(tmpFileName, "r") as tmpFile:
                        for line in tmpFile:
                            if minify:
                                line = line.strip("\n\t ")
                                line = removeSpaces(line)
                            f2.write(line)
                    os.remove(tmpFileName)
                    f2.close

                new_src += jsonScript(safeLayerName)

            elif i.type() == QgsMapLayer.RasterLayer:
                if i.dataProvider().name() != "wms":
                    in_raster = unicode(i.dataProvider().dataSourceUri())
                    prov_raster = os.path.join(tempfile.gettempdir(),
                                               'json_' + safeLayerName +
                                               '_prov.tif')
                    out_raster = dataPath + '.png'
                    crsSrc = i.crs()
                    crsDest = QgsCoordinateReferenceSystem(4326)
                    xform = QgsCoordinateTransform(crsSrc, crsDest)
                    extentRep = xform.transform(i.extent())
                    extentRepNew = ','.join([unicode(extentRep.xMinimum()),
                                             unicode(extentRep.xMaximum()),
                                             unicode(extentRep.yMinimum()),
                                             unicode(extentRep.yMaximum())])
                    processing.runalg("gdalogr:warpreproject", in_raster,
                                      i.crs().authid(), "EPSG:4326", "", 0, 1,
                                      0, -1, 75, 6, 1, False, 0, False, "",
                                      prov_raster)
                    processing.runalg("gdalogr:translate", prov_raster, 100,
                                      True, "", 0, "", extentRepNew, False, 0,
                                      0, 75, 6, 1, False, 0, False, "",
                                      out_raster)
        if scaleDependent and i.hasScaleBasedVisibility():
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
    if (basemapName == 0 or basemapName == "" or
            basemapName == "None" or matchCRS):
        basemapText = ""
    else:
        basemapText = basemapsScript(basemapAddresses[basemapName],
                                     basemapAttributions[basemapName], maxZoom)
    layerOrder = layerOrderScript(extent)
    new_src += middle
    new_src += basemapText
    new_src += layerOrder

    for count, i in enumerate(layer_list):
        rawLayerName = i.name()
        safeLayerName = re.sub('[\W_]+', '', rawLayerName)
        if i.type() == QgsMapLayer.VectorLayer:
            (new_pop,
             labeltext, popFuncs) = labelsAndPopups(i, safeLayerName,
                                                    usedFields,
                                                    labelhover, highlight,
                                                    popupsOnHover, popup,
                                                    count)
            layerName = safeLayerName
            renderer = i.rendererV2()
            layer_transp = 1 - (float(i.layerTransparency()) / 100)
            new_obj = ""

            if (isinstance(renderer, QgsSingleSymbolRendererV2) or
                    isinstance(renderer, QgsRuleBasedRendererV2)):
                (new_obj,
                 legends,
                 wfsLayers) = singleLayer(renderer, outputProjectFileName,
                                          layerName, safeLayerName,
                                          wfsLayers, i, layer_transp,
                                          labeltext, cluster, cluster_num,
                                          visible, json, usedFields,
                                          legends, count, popFuncs)
            elif isinstance(renderer, QgsCategorizedSymbolRendererV2):
                (new_obj,
                 legends,
                 wfsLayers) = categorizedLayer(i, renderer, layerName,
                                               safeLayerName,
                                               outputProjectFileName,
                                               layer_transp, usedFields,
                                               count, legends, labeltext,
                                               cluster, cluster_num,
                                               popFuncs, visible,
                                               json, wfsLayers)
            elif isinstance(renderer, QgsGraduatedSymbolRendererV2):
                (new_obj,
                 legends,
                 wfsLayers) = graduatedLayer(i, layerName, safeLayerName,
                                             renderer,
                                             outputProjectFileName,
                                             layer_transp, labeltext,
                                             popFuncs, cluster,
                                             cluster_num, visible, json,
                                             usedFields, count,
                                             legends, wfsLayers)
            else:
                print "No renderer"

            if usedFields[count] != 0:
                new_src += new_pop
            new_src += """
""" + new_obj
            new_src += """
        bounds_group.addLayer(json_""" + safeLayerName + """JSON);"""
            if visible[count]:
                if cluster[count] == False:
                    new_src += """
        feature_group.addLayer(json_""" + safeLayerName + """JSON);"""
                else:
                    new_src += """
        cluster_group""" + safeLayerName + """JSON.addTo(map);"""
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
        if len(basemapName) == 0 or basemapName == "None" or matchCRS:
            controlStart = """
        var baseMaps = {};"""
        else:
            controlStart = """
        var baseMaps = {
            '""" + unicode(basemapName) + """': basemap
        };"""
        if len(basemapName) == 0 or basemapName == "None":
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
    if opacity_raster:
        opacityStart = """
        function updateOpacity(value) {
        """
        new_src += opacityStart

        for i in layer_list:
            rawLayerName = i.name()
            safeLayerName = re.sub('[\W_]+', '', rawLayerName)
            if i.type() == QgsMapLayer.RasterLayer:
                new_opc = """
                overlay_""" + safeLayerName + """.setOpacity(value);"""
                new_src += new_opc
        opacityEnd = """}"""
        new_src += opacityEnd

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
                   matchCRS, canvas, full, mapLibLocation, new_src,
                   template)
    return outputIndex


def labelsAndPopups(i, safeLayerName, usedFields, labelhover,
                    highlight, popupsOnHover, popup, count):
    fields = i.pendingFields()
    field_names = [field.name() for field in fields]
    usedFields = getUsedFields(i)
    if popup[count] != 0 and popup[count] != 1:
        usedFields.append(popup[count])
        new_field_names = []
        for field in usedFields:
            new_field_names.append(field)
        field_names = new_field_names
    html_prov = False
    label_exp = ''
    labeltext = ""
    f = ''
    palyr = QgsPalLayerSettings()
    palyr.readFromLayer(i)
    f = palyr.fieldName
    label_exp = False
    labeltext = ".bindLabel(feature.properties." + unicode(f)
    if not labelhover:
        labeltext += ", {noHide: true, offset: [-0, -16]}"
    labeltext += ")"
    for field in field_names:
        if unicode(field) == 'html_exp':
            html_prov = True
            table = 'feature.properties.html_exp'
        if (unicode(f) != "" and unicode(f) == unicode(field) and
                f and palyr.enabled):
            label_exp = True
        if not html_prov:
            tablestart = "'<table>"
            row = ""
            for field in field_names:
                fieldIndex = fields.indexFromName(unicode(field))
                editorWidget = i.editorWidgetV2(fieldIndex)
                if (editorWidget != QgsVectorLayer.Hidden and
                        editorWidget != 'Hidden'):
                    row += '<tr><th scope="row">'
                    row += i.attributeDisplayName(fieldIndex)
                    row += "</th><td>' + "
                    row += "(feature.properties['" + unicode(field) + "'] "
                    row += "!== null ? Autolinker.link("
                    row += "String(feature.properties['" + unicode(field)
                    row += "'])) : '') + '</td></tr>"
            tableend = "</table>'"
            table = tablestart + row + tableend
    if not label_exp:
        labeltext = ""
    if popup[count] != 0:
        popFuncs = popFuncsScript(table)
    else:
        popFuncs = ""
    new_pop = popupScript(safeLayerName, popFuncs, highlight, popupsOnHover)
    return new_pop, labeltext, popFuncs


def singleLayer(renderer, outputProjectFileName, layerName, safeLayerName,
                wfsLayers, i, layer_transp, labeltext, cluster,
                cluster_num, visible, json, usedFields, legends, count,
                popFuncs):
    if isinstance(renderer, QgsRuleBasedRendererV2):
        symbol = renderer.rootRule().children()[0].symbol()
    else:
        symbol = renderer.symbol()
    symbolLayer = symbol.symbolLayer(0)
    legendIcon = QgsSymbolLayerV2Utils.symbolPreviewPixmap(symbol,
                                                           QSize(16, 16))
    legendIcon.save(os.path.join(outputProjectFileName,
                                 "legend", layerName + ".png"))
    legends[layerName] = '<img src="legend/' + layerName + '.png" /> '
    legends[layerName] += i.name()
    colorName = symbol.color().name()
    symbol_transp = symbol.alpha()
    fill_transp = float(symbol.color().alpha()) / 255
    fill_opacity = unicode(layer_transp * symbol_transp * fill_transp)
    if i.geometryType() == QGis.Point:
        (new_obj, cluster_num,
         wfsLayers) = singlePoint(symbol, symbolLayer, layer_transp,
                                  symbol_transp, layerName, safeLayerName,
                                  colorName, fill_opacity, labeltext, i,
                                  cluster, cluster_num, visible, json,
                                  usedFields, wfsLayers, count,
                                  outputProjectFileName)
    elif i.geometryType() == QGis.Line:
        new_obj, wfsLayers = singleLine(symbol, colorName, fill_opacity, i,
                                        json, layerName, safeLayerName,
                                        wfsLayers, popFuncs, visible,
                                        usedFields, count)
    elif i.geometryType() == QGis.Polygon:
        new_obj, wfsLayers = singlePolygon(i, layerName, safeLayerName, symbol,
                                           symbolLayer, colorName,
                                           layer_transp, symbol_transp,
                                           fill_opacity, visible, json,
                                           usedFields, wfsLayers, count)
    return new_obj, legends, wfsLayers


def singlePoint(symbol, symbolLayer, layer_transp, symbol_transp, layerName,
                safeLayerName, colorName, fill_opacity, labeltext, i, cluster,
                cluster_num, visible, json, usedFields, wfsLayers, count,
                outputProjectFileName):
    radius = unicode(symbol.size())
    if isinstance(symbolLayer, QgsSvgMarkerSymbolLayerV2):
        pointStyleLabel = svgScript(safeLayerName, symbolLayer,
                                    outputProjectFileName, labeltext)
    else:
        try:
            borderStyle = symbolLayer.outlineStyle()
            border = symbolLayer.borderColor()
            borderColor = unicode(border.name())
            border_transp = float(border.alpha()) / 255
            borderWidth = symbolLayer.outlineWidth()
        except:
            borderStyle = ""
            borderColor = ""
            border_transp = 0
            borderWidth = 1
        borderOpacity = unicode(layer_transp * symbol_transp * border_transp)
        pointStyleLabel = pointStyleLabelScript(safeLayerName, radius,
                                                borderWidth, borderStyle,
                                                colorName, borderColor,
                                                borderOpacity, fill_opacity,
                                                labeltext)
    pointToLayer = pointToLayerScript(safeLayerName)
    if i.providerType() == 'WFS' and json[count] == False:
        (new_obj, scriptTag,
         cluster_num) = buildPointWFS(pointStyleLabel, layerName, i.source(),
                                      "", cluster[count], cluster_num,
                                      visible[count])
        wfsLayers += wfsScript(scriptTag)
    else:
        new_obj = jsonPointScript(pointStyleLabel, safeLayerName,
                                  pointToLayer, usedFields[count])
        if cluster[count]:
            new_obj += clusterScript(safeLayerName)
            cluster_num += 1
    return new_obj, cluster_num, wfsLayers


def singleLine(symbol, colorName, fill_opacity, i, json, layerName,
               safeLayerName, wfsLayers, popFuncs, visible, usedFields, count):
    radius = symbol.width()
    try:
        penStyle = getLineStyle(symbol.symbolLayer(0).penStyle(), radius)
    except:
        penStyle = ""
    lineStyle = simpleLineStyleScript(radius, colorName,
                                      penStyle, fill_opacity)
    if i.providerType() == 'WFS' and json[count] == False:
        stylestr = nonPointStylePopupsScript(safeLayerName)
        new_obj, scriptTag = buildNonPointWFS(layerName, i.source(), "",
                                              stylestr, visible[count])
        new_obj += nonPointStyleFunctionScript(safeLayerName, lineStyle)
        wfsLayers += wfsScript(scriptTag)
    else:
        new_obj = nonPointStyleFunctionScript(safeLayerName, lineStyle)
        new_obj += buildNonPointJSON("", safeLayerName, usedFields[count])
        # new_obj += stackLayers(layerName, visible[count])
    return new_obj, wfsLayers


def singlePolygon(i, layerName, safeLayerName, symbol, symbolLayer, colorName,
                  layer_transp, symbol_transp, fill_opacity, visible, json,
                  usedFields, wfsLayers, count):
    borderStyle = ""
    if (symbolLayer.layerType() == 'SimpleLine' or
            isinstance(symbolLayer, QgsSimpleLineSymbolLayerV2)):
        radius = symbolLayer.width()
        colorName = 'none'
        borderColor = unicode(symbol.color().name())
        border_transp = float(symbol.color().alpha()) / 255
    else:
        try:
            radius = symbolLayer.borderWidth()
            border = symbolLayer.borderColor()
            borderColor = unicode(border.name())
            borderStyle = getLineStyle(symbolLayer.borderStyle(), radius)
            border_transp = float(border.alpha()) / 255
            if symbolLayer.borderStyle() == 0:
                radius = "0"
            if symbolLayer.brushStyle() == 0:
                colorName = "none"
        except:
            radius = 1
            borderColor = "#000000"
            borderStyle = ""
            border_transp = 1
            colorName = "#ffffff"
    borderOpacity = unicode(layer_transp * symbol_transp * border_transp)
    polyStyle = singlePolyStyleScript(radius * 4, borderColor, borderOpacity,
                                      colorName, borderStyle, fill_opacity)
    if i.providerType() == 'WFS' and json[count] == False:
        stylestr = nonPointStylePopupsScript(safeLayerName)
        new_obj, scriptTag = buildNonPointWFS(layerName, i.source(), "",
                                              stylestr, visible[count])
        new_obj += nonPointStyleFunctionScript(safeLayerName, polyStyle)
        wfsLayers += wfsScript(scriptTag)
    else:
        new_obj = nonPointStyleFunctionScript(safeLayerName, polyStyle)
        new_obj += buildNonPointJSON("", safeLayerName, usedFields[count])
        # new_obj += stackLayers(layerName, visible[count])
    return new_obj, wfsLayers


def categorizedLayer(i, renderer, layerName, safeLayerName,
                     outputProjectFileName, layer_transp, usedFields, count,
                     legends, labeltext, cluster, cluster_num, popFuncs,
                     visible, json, wfsLayers):
    catLegend = i.name() + "<br />"
    if i.geometryType() == QGis.Point:
        (new_obj,
         wfsLayers) = categorizedPoint(outputProjectFileName, i, renderer,
                                       layerName, safeLayerName, layer_transp,
                                       labeltext, cluster, cluster_num,
                                       usedFields, visible, json, count,
                                       wfsLayers, catLegend)
    elif i.geometryType() == QGis.Line:
        (new_obj, wfsLayers,
         catLegend) = categorizedLine(outputProjectFileName, i, layerName,
                                      safeLayerName, renderer, catLegend,
                                      layer_transp, popFuncs, usedFields, json,
                                      visible, count, wfsLayers)
    elif i.geometryType() == QGis.Polygon:
        (new_obj,
         catLegend,
         wfsLayers) = categorizedPolygon(outputProjectFileName, i, renderer,
                                         layerName, safeLayerName, catLegend,
                                         layer_transp, usedFields, visible,
                                         json, count, popFuncs, wfsLayers)
    legends[layerName] = catLegend
    return new_obj, legends, wfsLayers


def categorizedPoint(outputProjectFileName, i, renderer, layerName,
                     safeLayerName, layer_transp, labeltext, cluster,
                     cluster_num, usedFields, visible, json, count,
                     wfsLayers, catLegend):
    categories = renderer.categories()
    valueAttr = renderer.classAttribute()
    categoryStr = categoryScript(layerName, valueAttr)
    for cat in categories:
        if not cat.value():
            categoryStr += defaultCategoryScript()
        else:
            categoryStr += eachCategoryScript(cat.value())
        symbol = cat.symbol()
        catLegend = iconLegend(symbol, cat, outputProjectFileName,
                               layerName, catLegend)
        symbol_transp = symbol.alpha()
        fill_transp = float(symbol.color().alpha()) / 255
        fill_opacity = unicode(layer_transp * symbol_transp * fill_transp)
        symbolLayer = symbol.symbolLayer(0)
        border_transp = float(symbolLayer.borderColor().alpha()) / 255
        borderOpacity = unicode(layer_transp * symbol_transp * border_transp)
        categoryStr += categorizedPointStylesScript(symbol, fill_opacity,
                                                    borderOpacity)
    categoryStr += endCategoryScript()
    if i.providerType() == 'WFS' and json[count] == False:
        stylestr = categorizedPointWFSscript(layerName, labeltext)
        (new_obj, scriptTag,
         cluster_num) = buildPointWFS(stylestr, layerName, i.source(),
                                      categoryStr, cluster[count], cluster_num,
                                      visible[count])
        wfsLayers += wfsScript(scriptTag)
    else:
        new_obj = categoryStr + categorizedPointJSONscript(safeLayerName,
                                                           labeltext,
                                                           usedFields[count])
        if cluster[count] == True:
            new_obj += clusterScript(safeLayerName)
        cluster_num += 1
    return new_obj, wfsLayers


def categorizedLine(outputProjectFileName, i, layerName, safeLayerName,
                    renderer, catLegend, layer_transp, popFuncs, usedFields,
                    json, visible, count, wfsLayers):
    categories = renderer.categories()
    valueAttr = renderer.classAttribute()
    categoryStr = categoryScript(layerName, valueAttr)
    for cat in categories:
        if not cat.value():
            categoryStr += defaultCategoryScript()
        else:
            categoryStr += eachCategoryScript(cat.value())
        symbol = cat.symbol()
        catLegend = iconLegend(symbol, cat, outputProjectFileName,
                               layerName, catLegend)
        symbol_transp = symbol.alpha()
        fill_transp = float(symbol.color().alpha()) / 255
        fill_opacity = unicode(layer_transp * symbol_transp * fill_transp)
        categoryStr += categorizedLineStylesScript(symbol, fill_opacity)
    categoryStr += endCategoryScript()
    stylestr = categorizedNonPointStyleFunctionScript(layerName, popFuncs)
    if i.providerType() == 'WFS' and json[count] == False:
        new_obj, scriptTag = buildNonPointWFS(layerName, i.source(),
                                              categoryStr, stylestr,
                                              visible[count])
        wfsLayers += wfsScript(scriptTag)
    else:
        new_obj = buildNonPointJSON(categoryStr, safeLayerName,
                                    usedFields[count])
    return new_obj, wfsLayers, catLegend


def categorizedPolygon(outputProjectFileName, i, renderer, layerName,
                       safeLayerName, catLegend, layer_transp, usedFields,
                       visible, json, count, popFuncs, wfsLayers):
    categories = renderer.categories()
    valueAttr = renderer.classAttribute()
    categoryStr = categoryScript(layerName, valueAttr)
    for cat in categories:
        if not cat.value():
            categoryStr += defaultCategoryScript()
        else:
            categoryStr += eachCategoryScript(cat.value())
        symbol = cat.symbol()
        catLegend = iconLegend(symbol, cat, outputProjectFileName,
                               layerName, catLegend)
        symbol_transp = symbol.alpha()
        symbolLayer = symbol.symbolLayer(0)
        border_transp = float(symbolLayer.borderColor().alpha()) / 255
        borderOpacity = unicode(layer_transp * symbol_transp * border_transp)
        fill_transp = float(symbol.color().alpha()) / 255
        fill_opacity = unicode(layer_transp * symbol_transp * fill_transp)
        categoryStr += categorizedPolygonStylesScript(symbol, fill_opacity,
                                                      borderOpacity)
    categoryStr += endCategoryScript()
    if i.providerType() == 'WFS' and json[count] == False:
        stylestr = categorizedNonPointStyleFunctionScript(layerName, popFuncs)
        new_obj, scriptTag = buildNonPointWFS(layerName, i.source(),
                                              categoryStr, stylestr,
                                              visible[count])
        wfsLayers += wfsScript(scriptTag)
    else:
        new_obj = buildNonPointJSON(categoryStr, safeLayerName,
                                    usedFields[count])
    return new_obj, catLegend, wfsLayers


def graduatedLayer(i, layerName, safeLayerName, renderer,
                   outputProjectFileName, layer_transp, labeltext, popFuncs,
                   cluster, cluster_num, visible, json, usedFields, count,
                   legends, wfsLayers):
    catLegend = i.name() + "<br />"
    categoryStr = graduatedStyleScript(layerName)
    if i.geometryType() == QGis.Point:
        (new_obj,
         catLegend,
         wfsLayers,
         cluster_num) = graduatedPoint(outputProjectFileName, i, layerName,
                                       safeLayerName, renderer, catLegend,
                                       layer_transp, json, count, labeltext,
                                       usedFields, cluster, cluster_num,
                                       visible, wfsLayers, categoryStr)
    elif i.geometryType() == QGis.Line:
        (new_obj, wfsLayers,
         catLegend) = graduatedLine(outputProjectFileName, i, layerName,
                                    safeLayerName, renderer, catLegend,
                                    layer_transp, popFuncs, usedFields, json,
                                    visible, count, wfsLayers, categoryStr)
    elif i.geometryType() == QGis.Polygon:
        (new_obj, catLegend,
         wfsLayers) = graduatedPolygon(outputProjectFileName, i, renderer,
                                       layerName, safeLayerName, catLegend,
                                       layer_transp, usedFields, visible,
                                       json, count, popFuncs, wfsLayers,
                                       categoryStr)
    legends[layerName] = catLegend
    return new_obj, legends, wfsLayers


def graduatedPoint(outputProjectFileName, i, layerName, safeLayerName,
                   renderer, catLegend, layer_transp, json, count, labeltext,
                   usedFields, cluster, cluster_num, visible,
                   wfsLayers, categoryStr):
    valueAttr = renderer.classAttribute()
    for r in renderer.ranges():
        symbol = r.symbol()
        catLegend = iconLegend(symbol, r, outputProjectFileName,
                               layerName, catLegend)
        symbol_transp = symbol.alpha()
        symbolLayer = symbol.symbolLayer(0)
        border_transp = float(symbolLayer.borderColor().alpha()) / 255
        borderOpacity = unicode(layer_transp * symbol_transp * border_transp)
        fill_transp = float(symbol.color().alpha()) / 255
        fill_opacity = unicode(layer_transp * symbol_transp * fill_transp)
        categoryStr += graduatedPointStylesScript(valueAttr, r, symbol,
                                                  fill_opacity, borderOpacity)
    categoryStr += endGraduatedStyleScript()
    if i.providerType() == 'WFS' and json[count] == False:
        stylestr = categorizedPointWFSscript(layerName, labeltext)
        (new_obj, scriptTag,
         cluster_num) = buildPointWFS(stylestr, layerName, i.source(),
                                      categoryStr, cluster[count], cluster_num,
                                      visible[count])
        wfsLayers += wfsScript(scriptTag)
    else:
        new_obj = categoryStr + categorizedPointJSONscript(safeLayerName,
                                                           labeltext,
                                                           usedFields[count])
        if cluster[count] == True:
            new_obj += clusterScript(safeLayerName)
            cluster_num += 1
    return new_obj, catLegend, wfsLayers, cluster_num


def graduatedLine(outputProjectFileName, i, layerName, safeLayerName, renderer,
                  catLegend, layer_transp, popFuncs, usedFields, json, visible,
                  count, wfsLayers, categoryStr):
    valueAttr = renderer.classAttribute()
    for r in renderer.ranges():
        symbol = r.symbol()
        catLegend = iconLegend(symbol, r, outputProjectFileName,
                               layerName, catLegend)
        symbol_transp = symbol.alpha()
        fill_transp = float(symbol.color().alpha()) / 255
        fill_opacity = unicode(layer_transp * symbol_transp * fill_transp)
        categoryStr += graduatedLineStylesScript(valueAttr, r,
                                                 symbol, fill_opacity)
    categoryStr += endGraduatedStyleScript()
    if i.providerType() == 'WFS' and json[count] == False:
        stylestr = categorizedNonPointStyleFunctionScript(layerName, popFuncs)
        new_obj, scriptTag = buildNonPointWFS(layerName, i.source(),
                                              categoryStr, stylestr,
                                              visible[count])
        wfsLayers += wfsScript(scriptTag)
    else:
        new_obj = buildNonPointJSON(categoryStr, safeLayerName,
                                    usedFields[count])
    return new_obj, wfsLayers, catLegend


def graduatedPolygon(outputProjectFileName, i, renderer, layerName,
                     safeLayerName, catLegend, layer_transp, usedFields,
                     visible, json, count, popFuncs, wfsLayers, categoryStr):
    valueAttr = renderer.classAttribute()
    for r in renderer.ranges():
        symbol = r.symbol()
        catLegend = iconLegend(symbol, r, outputProjectFileName,
                               layerName, catLegend)
        symbol_transp = symbol.alpha()
        symbolLayer = symbol.symbolLayer(0)
        border_transp = float(symbolLayer.borderColor().alpha()) / 255
        borderOpacity = unicode(layer_transp * symbol_transp * border_transp)
        fill_transp = float(symbol.color().alpha()) / 255
        fill_opacity = unicode(layer_transp * symbol_transp * fill_transp)
        categoryStr += graduatedPolygonStylesScript(valueAttr, r, symbol,
                                                    fill_opacity,
                                                    borderOpacity)
    categoryStr += endGraduatedStyleScript()
    if i.providerType() == 'WFS' and json[count] == False:
        stylestr = categorizedNonPointStyleFunctionScript(layerName, popFuncs)
        new_obj, scriptTag = buildNonPointWFS(layerName, i.source(),
                                              categoryStr, stylestr,
                                              visible[count])
        wfsLayers += wfsScript(scriptTag)
    else:
        new_obj = buildNonPointJSON(categoryStr, safeLayerName,
                                    usedFields[count])
    return new_obj, catLegend, wfsLayers


def iconLegend(symbol, catr, outputProjectFileName, layerName, catLegend):
    legendIcon = QgsSymbolLayerV2Utils.symbolPreviewPixmap(symbol,
                                                           QSize(16, 16))
    safeLabel = re.sub('[\W_]+', '', catr.label())
    legendIcon.save(os.path.join(outputProjectFileName, "legend",
                                 layerName + "_" + safeLabel + ".png"))
    catLegend += """&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<img src="legend/"""
    catLegend += layerName + "_" + safeLabel + """.png" /> """
    catLegend += catr.label() + "<br />"
    return catLegend
