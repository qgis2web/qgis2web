# qgis-ol3 Creates OpenLayers map from QGIS layers
# Copyright (C) 2014 Victor Olaya (volayaf@gmail.com)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import codecs
import os
import re
import math
import time
import shutil
import traceback
import xml.etree.ElementTree
from qgis.core import *
from utils import (exportLayers, safeName, replaceInTemplate,
                   is25d, getRGBAColor, ALL_ATTRIBUTES, BLEND_MODES)
from qgis.utils import iface
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from olScriptStrings import *
from basemaps import basemapOL


def writeOL(iface, layers, groups, popup, visible,
            json, clustered, settings, folder):
    QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
    stamp = time.strftime("%Y_%m_%d-%H_%M_%S")
    folder = os.path.join(folder, 'qgis2web_' + unicode(stamp))
    imagesFolder = os.path.join(folder, "images")
    QDir().mkpath(imagesFolder)
    try:
        dst = os.path.join(folder, "resources")
        if not os.path.exists(dst):
            shutil.copytree(os.path.join(os.path.dirname(__file__),
                                         "resources"),
                            dst)
        matchCRS = settings["Appearance"]["Match project CRS"]
        precision = settings["Data export"]["Precision"]
        optimize = settings["Data export"]["Minify GeoJSON files"]
        exportLayers(iface, layers, folder, precision,
                     optimize, popup, json)
        exportStyles(layers, folder, clustered)
        osmb = writeLayersAndGroups(layers, groups, visible, folder, popup,
                                    settings, json, matchCRS, clustered, iface)
        jsAddress = '<script src="resources/polyfills.js"></script>'
        if settings["Data export"]["Mapping library location"] == "Local":
            cssAddress = """<link rel="stylesheet" """
            cssAddress += """href="./resources/ol.css" />"""
            jsAddress += """
        <script src="./resources/ol.js"></script>"""
        else:
            cssAddress = """<link rel="stylesheet" href="http://"""
            cssAddress += """openlayers.org/en/v3.20.1/css/ol.css" />"""
            jsAddress += """
        <script src="http://openlayers.org/en/v3.20.1/"""
            jsAddress += """build/ol.js"></script>"""
        layerSearch = settings["Appearance"]["Layer search"]
        if layerSearch != "None" and layerSearch != "":
            cssAddress += """
        <link rel="stylesheet" href="resources/horsey.min.css">
        <link rel="stylesheet" href="resources/ol3-search-layer.min.css">"""
            jsAddress += """
        <script src="http://cdn.polyfill.io/v2/polyfill.min.js?features="""
            jsAddress += """Element.prototype.classList,URL"></script>
        <script src="resources/horsey.min.js"></script>
        <script src="resources/ol3-search-layer.min.js"></script>"""
            searchVals = layerSearch.split(": ")
            layerSearch = """
    var searchLayer = new ol.SearchLayer({{
      layer: lyr_{layer},
      colName: '{field}',
      zoom: 10,
      collapsed: true,
      map: map
    }});

    map.addControl(searchLayer);""".format(layer=searchVals[0],
                                           field=searchVals[1])
        else:
            layerSearch = ""
        if osmb != "":
            jsAddress += """
        <script src="resources/OSMBuildings-OL3.js"></script>"""
        geojsonVars = ""
        wfsVars = ""
        styleVars = ""
        for layer, encode2json in zip(layers, json):
            if layer.type() == layer.VectorLayer:
                if layer.providerType() != "WFS" or encode2json:
                    geojsonVars += ('<script src="layers/%s"></script>' %
                                    (safeName(layer.name()) + ".js"))
                else:
                    layerSource = layer.source()
                    if ("retrictToRequestBBOX" in layerSource or
                            "restrictToRequestBBOX" in layerSource):
                        provider = layer.dataProvider()
                        uri = QgsDataSourceURI(provider.dataSourceUri())
                        wfsURL = uri.param("url")
                        wfsTypename = uri.param("typename")
                        wfsSRS = uri.param("srsname")
                        layerSource = wfsURL
                        layerSource += "?SERVICE=WFS&VERSION=1.0.0&"
                        layerSource += "REQUEST=GetFeature&TYPENAME="
                        layerSource += wfsTypename
                        layerSource += "&SRSNAME="
                        layerSource += wfsSRS
                    if not matchCRS:
                        layerSource = re.sub('SRSNAME\=EPSG\:\d+',
                                             'SRSNAME=EPSG:3857', layerSource)
                    layerSource += "&outputFormat=text%2Fjavascript&"
                    layerSource += "format_options=callback%3A"
                    layerSource += "get" + safeName(layer.name()) + "Json"
                    wfsVars += ('<script src="%s"></script>' % layerSource)
                styleVars += ('<script src="styles/%s_style.js"></script>' %
                              (safeName(layer.name())))
        popupLayers = "popupLayers = [%s];" % ",".join(
                ['1' for field in popup])
        controls = ['expandedAttribution']
        project = QgsProject.instance()
        if project.readBoolEntry("ScaleBar", "/Enabled", False)[0]:
            controls.append("new ol.control.ScaleLine({})")
        if settings["Appearance"]["Add layers list"]:
            controls.append(
                'new ol.control.LayerSwitcher({tipLabel: "Layers"})')
        if settings["Appearance"]["Measure tool"] != "None":
            controls.append(
                'new measureControl()')
        if settings["Appearance"]["Geolocate user"]:
            controls.append(
                'new geolocateControl()')
        pageTitle = project.title()
        mapSettings = iface.mapCanvas().mapSettings()
        backgroundColor = """
        <style>
        html, body {{
            background-color: {bgcol};
        }}
        </style>
""".format(bgcol=mapSettings.backgroundColor().name())
        geolocateUser = settings["Appearance"]["Geolocate user"]
        backgroundColor += geolocateStyle(geolocateUser)
        mapbounds = bounds(iface,
                           settings["Scale/Zoom"]["Extent"] == "Canvas extent",
                           layers,
                           settings["Appearance"]["Match project CRS"])
        mapextent = "extent: %s," % mapbounds if (
            settings["Scale/Zoom"]["Restrict to extent"]) else ""
        maxZoom = int(settings["Scale/Zoom"]["Max zoom level"])
        minZoom = int(settings["Scale/Zoom"]["Min zoom level"])
        popupsOnHover = settings["Appearance"]["Show popups on hover"]
        highlightFeatures = settings["Appearance"]["Highlight on hover"]
        onHover = unicode(popupsOnHover).lower()
        highlight = unicode(highlightFeatures).lower()
        highlightFill = mapSettings.selectionColor().name()
        proj4 = ""
        proj = ""
        view = "%s maxZoom: %d, minZoom: %d" % (mapextent, maxZoom, minZoom)
        if settings["Appearance"]["Match project CRS"]:
            proj4 = """
<script src="http://cdnjs.cloudflare.com/ajax/libs/proj4js/2.3.6/proj4.js">"""
            proj4 += "</script>"
            proj = "<script>proj4.defs('{epsg}','{defn}');</script>".format(
                epsg=mapSettings.destinationCrs().authid(),
                defn=mapSettings.destinationCrs().toProj4())
            view += ", projection: '%s'" % (
                mapSettings.destinationCrs().authid())
        if settings["Appearance"]["Measure tool"] != "None":
            measureControl = measureControlScript()
            measuring = measuringScript()
            measure = measureScript()
            if settings["Appearance"]["Measure tool"] == "Imperial":
                measureUnit = measureUnitFeetScript()
            else:
                measureUnit = measureUnitMetricScript()
            measureStyle = measureStyleScript()
        else:
            measureControl = ""
            measuring = ""
            measure = ""
            measureUnit = ""
            measureStyle = ""
        geolocateHead = geolocationHead(geolocateUser)
        geolocate = geolocation(geolocateUser)
        geocode = settings["Appearance"]["Add address search"]
        geocodingLinks = geocodeLinks(geocode)
        geocodingJS = geocodeJS(geocode)
        geocodingScript = geocodeScript(geocode)
        extracss = """
        <link rel="stylesheet" href="./resources/ol3-layerswitcher.css">
        <link rel="stylesheet" href="./resources/qgis2web.css">"""
        if settings["Appearance"]["Geolocate user"]:
            extracss += """
        <link rel="stylesheet" href="http://maxcdn.bootstrapcdn.com/"""
            extracss += """font-awesome/4.6.3/css/font-awesome.min.css">"""
        ol3layerswitcher = """
        <script src="./resources/ol3-layerswitcher.js"></script>"""
        ol3popup = """<div id="popup" class="ol-popup">
                <a href="#" id="popup-closer" class="ol-popup-closer"></a>
                <div id="popup-content"></div>
            </div>"""
        ol3qgis2webjs = """<script src="./resources/qgis2web.js"></script>
        <script src="./resources/Autolinker.min.js"></script>"""
        if osmb != "":
            ol3qgis2webjs += """
        <script>{osmb}</script>""".format(osmb=osmb)
        ol3layers = """
        <script src="./layers/layers.js" type="text/javascript"></script>"""
        mapSize = iface.mapCanvas().size()
        values = {"@PAGETITLE@": pageTitle,
                  "@CSSADDRESS@": cssAddress,
                  "@EXTRACSS@": extracss,
                  "@JSADDRESS@": jsAddress,
                  "@MAP_WIDTH@": unicode(mapSize.width()) + "px",
                  "@MAP_HEIGHT@": unicode(mapSize.height()) + "px",
                  "@OL3_STYLEVARS@": styleVars,
                  "@OL3_BACKGROUNDCOLOR@": backgroundColor,
                  "@OL3_POPUP@": ol3popup,
                  "@OL3_GEOJSONVARS@": geojsonVars,
                  "@OL3_WFSVARS@": wfsVars,
                  "@OL3_PROJ4@": proj4,
                  "@OL3_PROJDEF@": proj,
                  "@OL3_GEOCODINGLINKS@": geocodingLinks,
                  "@OL3_GEOCODINGJS@": geocodingJS,
                  "@QGIS2WEBJS@": ol3qgis2webjs,
                  "@OL3_LAYERSWITCHER@": ol3layerswitcher,
                  "@OL3_LAYERS@": ol3layers,
                  "@OL3_MEASURESTYLE@": measureStyle,
                  "@LEAFLET_ADDRESSCSS@": "",
                  "@LEAFLET_MEASURECSS@": "",
                  "@LEAFLET_EXTRAJS@": "",
                  "@LEAFLET_ADDRESSJS@": "",
                  "@LEAFLET_MEASUREJS@": "",
                  "@LEAFLET_CRSJS@": "",
                  "@LEAFLET_LAYERSEARCHCSS@": "",
                  "@LEAFLET_LAYERSEARCHJS@": "",
                  "@LEAFLET_CLUSTERCSS@": "",
                  "@LEAFLET_CLUSTERJS@": ""}
        with open(os.path.join(folder, "index.html"), "w") as f:
            htmlTemplate = settings["Appearance"]["Template"]
            if htmlTemplate == "":
                htmlTemplate = "basic"
            templateOutput = replaceInTemplate(htmlTemplate + ".html", values)
            templateOutput = re.sub('\n[\s_]+\n', '\n', templateOutput)
            f.write(templateOutput)
        values = {"@GEOLOCATEHEAD@": geolocateHead,
                  "@BOUNDS@": mapbounds,
                  "@CONTROLS@": ",".join(controls),
                  "@POPUPLAYERS@": popupLayers,
                  "@VIEW@": view,
                  "@LAYERSEARCH@": layerSearch,
                  "@ONHOVER@": onHover,
                  "@DOHIGHLIGHT@": highlight,
                  "@HIGHLIGHTFILL@": highlightFill,
                  "@GEOLOCATE@": geolocate,
                  "@GEOCODINGSCRIPT@": geocodingScript,
                  "@MEASURECONTROL@": measureControl,
                  "@MEASURING@": measuring,
                  "@MEASURE@": measure,
                  "@MEASUREUNIT@": measureUnit}
        with open(os.path.join(folder, "resources", "qgis2web.js"), "w") as f:
            f.write(replaceInScript("qgis2web.js", values))
    except Exception as e:
        print "FAIL"
        print traceback.format_exc()
    finally:
        QApplication.restoreOverrideCursor()
    return os.path.join(folder, "index.html")


def writeLayersAndGroups(layers, groups, visible, folder, popup,
                         settings, json, matchCRS, clustered, iface):

    canvas = iface.mapCanvas()
    basemapList = settings["Appearance"]["Base layer"]
    basemaps = [basemapOL()[item.text()] for _, item in enumerate(basemapList)]

    baseLayer = """var baseLayer = new ol.layer.Group({
    'title': 'Base maps',
    layers: [%s\n]
});""" % ','.join(basemaps)

    layerVars = ""
    for layer, encode2json, cluster in zip(layers, json, clustered):
        try:
            if is25d(layer, canvas):
                pass
            else:
                layerVars += "\n".join([layerToJavascript(iface, layer,
                                                          encode2json,
                                                          matchCRS, cluster)])
        except:
            layerVars += "\n".join([layerToJavascript(iface, layer,
                                                      encode2json, matchCRS,
                                                      cluster)])
    groupVars = ""
    groupedLayers = {}
    for group, groupLayers in groups.iteritems():
        groupVars += ('''var %s = new ol.layer.Group({
                                layers: [%s],
                                title: "%s"});\n''' %
                      ("group_" + safeName(group),
                       ",".join(["lyr_" + safeName(layer.name())
                                for layer in groupLayers]),
                       group))
        for layer in groupLayers:
            groupedLayers[layer.id()] = safeName(group)
    mapLayers = ["baseLayer"]
    usedGroups = []
    osmb = ""
    for layer in layers:
        try:
            renderer = layer.rendererV2()
            if is25d(layer, canvas):
                shadows = ""
                renderer = layer.rendererV2()
                renderContext = QgsRenderContext.fromMapSettings(
                        canvas.mapSettings())
                fields = layer.pendingFields()
                renderer.startRender(renderContext, fields)
                for feat in layer.getFeatures():
                    if isinstance(renderer, QgsCategorizedSymbolRendererV2):
                        classAttribute = renderer.classAttribute()
                        attrValue = feat.attribute(classAttribute)
                        catIndex = renderer.categoryIndexForValue(attrValue)
                        categories = renderer.categories()
                        symbol = categories[catIndex].symbol()
                    elif isinstance(renderer, QgsGraduatedSymbolRendererV2):
                        classAttribute = renderer.classAttribute()
                        attrValue = feat.attribute(classAttribute)
                        ranges = renderer.ranges()
                        for range in ranges:
                            if (attrValue >= range.lowerValue() and
                                    attrValue <= range.upperValue()):
                                symbol = range.symbol().clone()
                    else:
                        symbol = renderer.symbolForFeature2(feat,
                                                            renderContext)
                    symbolLayer = symbol.symbolLayer(0)
                    if not symbolLayer.paintEffect().effectList()[0].enabled():
                        shadows = "'2015-07-15 10:00:00'"
                renderer.stopRender(renderContext)
                osmb = """
var osmb = new OSMBuildings(map).date(new Date({shadows}));
osmb.set(geojson_{sln});""".format(shadows=shadows, sln=safeName(layer.name()))
            else:
                mapLayers.append("lyr_" + safeName(layer.name()))
        except:
            mapLayers.append("lyr_" + safeName(layer.name()))
    visibility = ""
    for layer, v in zip(mapLayers[1:], visible):
        visibility += "\n".join(["%s.setVisible(%s);" % (layer,
                                                         unicode(v).lower())])

    group_list = ["baseLayer"] if len(basemapList) else []
    no_group_list = []
    for layer in layers:
        try:
            if is25d(layer, canvas):
                pass
            else:
                if layer.id() in groupedLayers:
                    groupName = groupedLayers[layer.id()]
                    if groupName not in usedGroups:
                        group_list.append("group_" + safeName(groupName))
                        usedGroups.append(groupName)
                else:
                    no_group_list.append("lyr_" + safeName(layer.name()))
        except:
            if layer.id() in groupedLayers:
                groupName = groupedLayers[layer.id()]
                if groupName not in usedGroups:
                    group_list.append("group_" + safeName(groupName))
                    usedGroups.append(groupName)
            else:
                no_group_list.append("lyr_" + safeName(layer.name()))

    layersList = []
    for layer in (group_list + no_group_list):
        layersList.append(layer)
    layersListString = "var layersList = [" + ",".join(layersList) + "];"

    fieldAliases = ""
    fieldImages = ""
    fieldLabels = ""
    blend_mode = ""
    for layer, labels in zip(layers, popup):
        if layer.type() == layer.VectorLayer and not is25d(layer, canvas):
            fieldList = layer.pendingFields()
            aliasFields = ""
            imageFields = ""
            labelFields = ""
            for field, label in zip(labels.keys(), labels.values()):
                labelFields += "'%(field)s': '%(label)s', " % (
                        {"field": field, "label": label})
            labelFields = "{%(labelFields)s});\n" % (
                    {"labelFields": labelFields})
            labelFields = "lyr_%(name)s.set('fieldLabels', " % (
                        {"name": safeName(layer.name())}) + labelFields
            fieldLabels += labelFields
            for f in fieldList:
                fieldIndex = fieldList.indexFromName(unicode(f.name()))
                aliasFields += "'%(field)s': '%(alias)s', " % (
                        {"field": f.name(),
                         "alias": layer.attributeDisplayName(fieldIndex)})
                try:
                    widget = layer.editFormConfig().widgetType(fieldIndex)
                except:
                    widget = layer.editorWidgetV2(fieldIndex)
                imageFields += "'%(field)s': '%(image)s', " % (
                        {"field": f.name(),
                         "image": widget})
            aliasFields = "{%(aliasFields)s});\n" % (
                        {"aliasFields": aliasFields})
            aliasFields = "lyr_%(name)s.set('fieldAliases', " % (
                        {"name": safeName(layer.name())}) + aliasFields
            fieldAliases += aliasFields
            imageFields = "{%(imageFields)s});\n" % (
                        {"imageFields": imageFields})
            imageFields = "lyr_%(name)s.set('fieldImages', " % (
                        {"name": safeName(layer.name())}) + imageFields
            fieldImages += imageFields
            blend_mode = """lyr_%(name)s.on('precompose', function(evt) {
    evt.context.globalCompositeOperation = '%(blend)s';
});""" % (
                        {"name": safeName(layer.name()),
                         "blend": BLEND_MODES[layer.blendMode()]})

    path = os.path.join(folder, "layers", "layers.js")
    with codecs.open(path, "w", "utf-8") as f:
        if basemapList:
            f.write(baseLayer + "\n")
        f.write(layerVars + "\n")
        f.write(groupVars + "\n")
        f.write(visibility + "\n")
        f.write(layersListString + "\n")
        f.write(fieldAliases)
        f.write(fieldImages)
        f.write(fieldLabels)
        f.write(blend_mode)
    return osmb


def replaceInScript(template, values):
    path = os.path.join(os.path.dirname(__file__), "resources", template)
    with open(path) as f:
        lines = f.readlines()
    s = "".join(lines)
    for name, value in values.iteritems():
        s = s.replace(name, value)
    return s


def bounds(iface, useCanvas, layers, matchCRS):
    if useCanvas:
        canvas = iface.mapCanvas()
        try:
            canvasCrs = canvas.mapSettings().destinationCrs()
        except:
            canvasCrs = canvas.mapRenderer().destinationCrs()
        if not matchCRS:
            transform = QgsCoordinateTransform(canvasCrs,
                                               QgsCoordinateReferenceSystem(
                                                   "EPSG:3857"))
            try:
                extent = transform.transform(canvas.extent())
            except QgsCsException:
                extent = QgsRectangle(-20026376.39, -20048966.10,
                                      20026376.39, 20048966.10)
        else:
            extent = canvas.extent()
    else:
        extent = None
        for layer in layers:
            if not matchCRS:
                epsg3857 = QgsCoordinateReferenceSystem("EPSG:3857")
                transform = QgsCoordinateTransform(layer.crs(), epsg3857)
                try:
                    layerExtent = transform.transform(layer.extent())
                except QgsCsException:
                    layerExtent = QgsRectangle(-20026376.39, -20048966.10,
                                               20026376.39, 20048966.10)
            else:
                layerExtent = layer.extent()
            if extent is None:
                extent = layerExtent
            else:
                extent.combineExtentWith(layerExtent)

    return "[%f, %f, %f, %f]" % (extent.xMinimum(), extent.yMinimum(),
                                 extent.xMaximum(), extent.yMaximum())


def layerToJavascript(iface, layer, encode2json, matchCRS, cluster):
    if layer.hasScaleBasedVisibility():
        minRes = 1 / ((1 / layer.minimumScale()) * 39.37 * 90.7)
        maxRes = 1 / ((1 / layer.maximumScale()) * 39.37 * 90.7)
        minResolution = "\nminResolution:%s,\n" % unicode(minRes)
        maxResolution = "maxResolution:%s,\n" % unicode(maxRes)
    else:
        minResolution = ""
        maxResolution = ""
    layerName = safeName(layer.name())
    if layer.type() == layer.VectorLayer and not is25d(layer,
                                                       iface.mapCanvas()):
        renderer = layer.rendererV2()
        if cluster and (isinstance(renderer, QgsSingleSymbolRendererV2) or
                        isinstance(renderer, QgsRuleBasedRendererV2)):
            cluster = True
        else:
            cluster = False
        if isinstance(renderer, QgsHeatmapRenderer):
            pointLayerType = "Heatmap"
            hmRadius = renderer.radius()
            colorRamp = renderer.colorRamp()
            hmStart = colorRamp.color1().name()
            hmEnd = colorRamp.color2().name()
            hmRamp = "['" + hmStart + "', "
            hmStops = colorRamp.stops()
            for stop in hmStops:
                hmRamp += "'" + stop.color.name() + "', "
            hmRamp += "'" + hmEnd + "']"
            hmWeight = renderer.weightExpression()
            hmWeightId = layer.fieldNameIndex(hmWeight)
            hmWeightMax = layer.maximumValue(hmWeightId)
        else:
            pointLayerType = "Vector"
        if matchCRS:
            mapCRS = iface.mapCanvas().mapSettings().destinationCrs().authid()
            crsConvert = """
            {dataProjection: 'EPSG:4326', featureProjection: '%(d)s'}""" % {
                "d": mapCRS}
        else:
            crsConvert = """
            {dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857'}"""
        if layer.providerType() == "WFS" and not encode2json:
            layerCode = '''var format_%(n)s = new ol.format.GeoJSON();
var jsonSource_%(n)s = new ol.source.Vector({
    format: format_%(n)s
});''' % {"n": layerName}
            if cluster:
                layerCode += '''cluster_%(n)s = new ol.source.Cluster({
  distance: 10,
  source: jsonSource_%(n)s
});''' % {"n": layerName}
            layerCode += '''var lyr_%(n)s = new ol.layer.Vector({
    source: ''' % {"n": layerName}
            if cluster:
                layerCode += 'cluster_%(n)s,' % {"n": layerName}
            else:
                layerCode += 'jsonSource_%(n)s,' % {"n": layerName}
            layerCode += '''%(min)s %(max)s
    style: style_%(n)s,
    title: "%(name)s"
});

function get%(n)sJson(geojson) {
    var features_%(n)s = format_%(n)s.readFeatures(geojson);
    jsonSource_%(n)s.addFeatures(features_%(n)s);
}''' % {
                        "name": layer.name(), "n": layerName,
                        "min": minResolution, "max": maxResolution}
            return layerCode
        else:
            layerCode = '''var format_%(n)s = new ol.format.GeoJSON();
var features_%(n)s = format_%(n)s.readFeatures(geojson_%(n)s, %(crs)s);
var jsonSource_%(n)s = new ol.source.Vector();
jsonSource_%(n)s.addFeatures(features_%(n)s);''' % {"n": layerName,
                                                    "crs": crsConvert}
            if cluster:
                layerCode += '''cluster_%(n)s = new ol.source.Cluster({
  distance: 10,
  source: jsonSource_%(n)s
});''' % {"n": layerName}
            layerCode += '''var lyr_%(n)s = new ol.layer.%(t)s({
                source:''' % {"n": layerName, "t": pointLayerType}
            if cluster:
                layerCode += 'cluster_%(n)s,' % {"n": layerName}
            else:
                layerCode += 'jsonSource_%(n)s,' % {"n": layerName}
            layerCode += '''%(min)s %(max)s''' % {"min": minResolution,
                                                  "max": maxResolution}
            if pointLayerType == "Vector":
                layerCode += '''
                style: style_%(n)s,''' % {"n": layerName}
            else:
                layerCode += '''
                radius: %(hmRadius)d * 2,
                gradient: %(hmRamp)s,
                blur: 15,
                shadow: 250,''' % {"hmRadius": hmRadius, "hmRamp": hmRamp}
                if hmWeight != "":
                    layerCode += '''
                weight: function(feature){
                    var weightField = '%(hmWeight)s';
                    var featureWeight = feature.get(weightField);
                    var maxWeight = %(hmWeightMax)d;
                    var calibratedWeight = featureWeight/maxWeight;
                    return calibratedWeight;
                },''' % {"hmWeight": hmWeight, "hmWeightMax": hmWeightMax}
            layerCode += '''
                title: "%(name)s"
            });''' % {"name": layer.name()}
            return layerCode
    elif layer.type() == layer.RasterLayer:
        if layer.providerType().lower() == "wms":
            source = layer.source()
            layers = re.search(r"layers=(.*?)(?:&|$)", source).groups(0)[0]
            url = re.search(r"url=(.*?)(?:&|$)", source).groups(0)[0]
            return '''var lyr_%(n)s = new ol.layer.Tile({
                        source: new ol.source.TileWMS(({
                          url: "%(url)s",
                          params: {"LAYERS": "%(layers)s", "TILED": "true"},
                        })),
                        title: "%(name)s",
                        %(minRes)s
                        %(maxRes)s
                      });''' % {"layers": layers, "url": url,
                                "n": layerName, "name": layer.name(),
                                "minRes": minResolution,
                                "maxRes": maxResolution}
        elif layer.providerType().lower() == "gdal":
            provider = layer.dataProvider()

            crsSrc = layer.crs()
            crsDest = QgsCoordinateReferenceSystem(3857)

            xform = QgsCoordinateTransform(crsSrc, crsDest)
            extentRep = xform.transform(layer.extent())

            sExtent = "[%f, %f, %f, %f]" % (extentRep.xMinimum(),
                                            extentRep.yMinimum(),
                                            extentRep.xMaximum(),
                                            extentRep.yMaximum())

            return '''var lyr_%(n)s = new ol.layer.Image({
                            opacity: 1,
                            title: "%(name)s",
                            %(minRes)s
                            %(maxRes)s
                            source: new ol.source.ImageStatic({
                               url: "./layers/%(n)s.png",
                                projection: 'EPSG:3857',
                                alwaysInRange: true,
                                //imageSize: [%(col)d, %(row)d],
                                imageExtent: %(extent)s
                            })
                        });''' % {"n": layerName,
                                  "extent": sExtent,
                                  "col": provider.xSize(),
                                  "name": layer.name(),
                                  "minRes": minResolution,
                                  "maxRes": maxResolution,
                                  "row": provider.ySize()}


def exportStyles(layers, folder, clustered):
    stylesFolder = os.path.join(folder, "styles")
    QDir().mkpath(stylesFolder)
    for layer, cluster in zip(layers, clustered):
        if layer.type() != layer.VectorLayer:
            continue
        labelsEnabled = unicode(
            layer.customProperty("labeling/enabled")).lower() == "true"
        if (labelsEnabled):
            labelField = layer.customProperty("labeling/fieldName")
            if labelField != "":
                fieldIndex = layer.pendingFields().indexFromName(labelField)
                try:
                    editFormConfig = layer.editFormConfig()
                    editorWidget = editFormConfig.widgetType(fieldIndex)
                except:
                    editorWidget = layer.editorWidgetV2(fieldIndex)
                if (editorWidget == QgsVectorLayer.Hidden or
                        editorWidget == 'Hidden'):
                    labelField = "q2wHide_" + labelField
                labelText = ('feature.get("%s")' %
                             labelField.replace('"', '\\"'))
            else:
                labelText = '""'
        else:
            labelText = '""'
        defs = "var size = 0;\n"
        try:
            renderer = layer.rendererV2()
            layer_alpha = layer.layerTransparency()
            if (isinstance(renderer, QgsSingleSymbolRendererV2) or
                    isinstance(renderer, QgsRuleBasedRendererV2)):
                if isinstance(renderer, QgsRuleBasedRendererV2):
                    symbol = renderer.rootRule().children()[0].symbol()
                else:
                    symbol = renderer.symbol()
                if cluster:
                    style = "var size = feature.get('features').length;\n"
                else:
                    style = "var size = 0;\n"
                style += "    var style = " + getSymbolAsStyle(symbol,
                                                               stylesFolder,
                                                               layer_alpha)
                value = 'var value = ""'
            elif isinstance(renderer, QgsCategorizedSymbolRendererV2):
                defs += """function categories_%s(feature, value) {
                switch(value) {""" % safeName(layer.name())
                cats = []
                for cat in renderer.categories():
                    cats.append('''case "%s":
                    return %s;
                    break;''' %
                                (cat.value(), getSymbolAsStyle(
                                    cat.symbol(),
                                    stylesFolder,
                                    layer_alpha)))
                defs += "\n".join(cats) + "}};"
                classAttr = renderer.classAttribute()
                fieldIndex = layer.pendingFields().indexFromName(classAttr)
                try:
                    editFormConfig = layer.editFormConfig()
                    editorWidget = editFormConfig.widgetType(fieldIndex)
                except:
                    editorWidget = layer.editorWidgetV2(fieldIndex)
                if (editorWidget == QgsVectorLayer.Hidden or
                        editorWidget == 'Hidden'):
                    classAttr = "q2wHide_" + classAttr
                value = ('var value = feature.get("%s");' % classAttr)
                style = ('''var style = categories_%s(feature, value)''' %
                         (safeName(layer.name())))
            elif isinstance(renderer, QgsGraduatedSymbolRendererV2):
                varName = "ranges_" + safeName(layer.name())
                defs += "var %s = [" % varName
                ranges = []
                for ran in renderer.ranges():
                    symbolstyle = getSymbolAsStyle(ran.symbol(), stylesFolder,
                                                   layer_alpha)
                    ranges.append('[%f, %f, %s]' % (ran.lowerValue(),
                                                    ran.upperValue(),
                                                    symbolstyle))
                defs += ",\n".join(ranges) + "];"
                classAttr = renderer.classAttribute()
                fieldIndex = layer.pendingFields().indexFromName(classAttr)
                try:
                    editFormConfig = layer.editFormConfig()
                    editorWidget = editFormConfig.widgetType(fieldIndex)
                except:
                    editorWidget = layer.editorWidgetV2(fieldIndex)
                if (editorWidget == QgsVectorLayer.Hidden or
                        editorWidget == 'Hidden'):
                    classAttr = "q2wHide_" + classAttr
                value = ('var value = feature.get("%s");' % classAttr)
                style = '''var style = %(v)s[0][2];
    for (i = 0; i < %(v)s.length; i++){
        var range = %(v)s[i];
        if (value > range[0] && value<=range[1]){
            style =  range[2];
        }
    }''' % {"v": varName}
            else:
                style = ""
            if layer.customProperty("labeling/fontSize"):
                size = float(layer.customProperty("labeling/fontSize")) * 1.3
            else:
                size = 10
            italic = layer.customProperty("labeling/fontItalic")
            bold = layer.customProperty("labeling/fontWeight")
            r = layer.customProperty("labeling/textColorR")
            g = layer.customProperty("labeling/textColorG")
            b = layer.customProperty("labeling/textColorB")
            color = "rgba(%s, %s, %s, 255)" % (r, g, b)
            face = layer.customProperty("labeling/fontFamily")
            palyr = QgsPalLayerSettings()
            palyr.readFromLayer(layer)
            sv = palyr.scaleVisibility
            if sv:
                min = float(palyr.scaleMin)
                max = float(palyr.scaleMax)
                min = 1 / ((1 / min) * 39.37 * 90.7)
                max = 1 / ((1 / max) * 39.37 * 90.7)
                labelRes = " && resolution > %(min)d " % {"min": min}
                labelRes += "&& resolution < %(max)d" % {"max": max}
            else:
                labelRes = ""
            buffer = palyr.bufferDraw
            if buffer:
                bufferColor = palyr.bufferColor.name()
                bufferWidth = palyr.bufferSize
                stroke = """
              stroke: new ol.style.Stroke({
                color: "%s",
                width: %d
              }),""" % (bufferColor, bufferWidth)
            else:
                stroke = ""
            if style != "":
                style = '''function(feature, resolution){
    %(value)s
    %(style)s;
    if (%(label)s !== null%(labelRes)s) {
        var labelText = String(%(label)s);
    } else {
        var labelText = ""
    }
    var key = value + "_" + labelText

    if (!%(cache)s[key]){
        var text = new ol.style.Text({
              font: '%(size)spx \\'%(face)s\\', sans-serif',
              text: labelText,
              textBaseline: "center",
              textAlign: "left",
              offsetX: 5,
              offsetY: 3,
              fill: new ol.style.Fill({
                color: '%(color)s'
              }),%(stroke)s
            });
        %(cache)s[key] = new ol.style.Style({"text": text})
    }
    var allStyles = [%(cache)s[key]];
    allStyles.push.apply(allStyles, style);
    return allStyles;
}''' % {
                    "style": style, "labelRes": labelRes, "label": labelText,
                    "cache": "styleCache_" + safeName(layer.name()),
                    "size": size, "face": face, "color": color,
                    "stroke": stroke, "value": value}
            else:
                style = "''"
        except Exception, e:
            style = """{
            /* """ + traceback.format_exc() + " */}"
            print traceback.format_exc()

        path = os.path.join(stylesFolder, safeName(layer.name()) + "_style.js")

        with codecs.open(path, "w", "utf-8") as f:
            f.write('''%(defs)s
var styleCache_%(name)s={}
var style_%(name)s = %(style)s;''' %
                    {"defs": defs, "name": safeName(layer.name()),
                     "style": style})


def getSymbolAsStyle(symbol, stylesFolder, layer_transparency):
    styles = []
    if layer_transparency == 0:
        alpha = symbol.alpha()
    else:
        alpha = 1-(layer_transparency / float(100))
    for i in xrange(symbol.symbolLayerCount()):
        sl = symbol.symbolLayer(i)
        props = sl.properties()
        if isinstance(sl, QgsSimpleMarkerSymbolLayerV2):
            color = getRGBAColor(props["color"], alpha)
            borderColor = getRGBAColor(props["outline_color"], alpha)
            borderWidth = props["outline_width"]
            size = symbol.size() * 2
            style = "image: %s" % getCircle(color, borderColor, borderWidth,
                                            size, props)
        elif isinstance(sl, QgsSvgMarkerSymbolLayerV2):
            path = os.path.join(stylesFolder, os.path.basename(sl.path()))
            svg = xml.etree.ElementTree.parse(sl.path()).getroot()
            svgWidth = svg.attrib["width"]
            svgWidth = re.sub("px", "", svgWidth)
            svgHeight = svg.attrib["height"]
            svgHeight = re.sub("px", "", svgHeight)
            if symbol.dataDefinedAngle().isActive():
                if symbol.dataDefinedAngle().useExpression():
                    rot = "0"
                else:
                    rot = "feature.get("
                    rot += symbol.dataDefinedAngle().expressionOrField()
                    rot += ") * 0.0174533"
            else:
                rot = unicode(sl.angle() * 0.0174533)
            shutil.copy(sl.path(), path)
            style = ("image: %s" %
                     getIcon("styles/" + os.path.basename(sl.path()),
                             sl.size(), svgWidth, svgHeight, rot))
        elif isinstance(sl, QgsSimpleLineSymbolLayerV2):

            # Check for old version
            if 'color' in props:
                color = getRGBAColor(props["color"], alpha)
            else:
                color = getRGBAColor(props["line_color"], alpha)

            if 'width' in props:
                line_width = props["width"]
            else:
                line_width = props["line_width"]

            if 'penstyle' in props:
                line_style = props["penstyle"]
            else:
                line_style = props["line_style"]

            lineCap = sl.penCapStyle()
            lineJoin = sl.penJoinStyle()

            style = getStrokeStyle(color, line_style, line_width,
                                   lineCap, lineJoin)
        elif isinstance(sl, QgsSimpleFillSymbolLayerV2):
            fillColor = getRGBAColor(props["color"], alpha)

            # for old version
            if 'color_border' in props:
                borderColor = getRGBAColor(props["color_border"], alpha)
            else:
                borderColor = getRGBAColor(props["outline_color"], alpha)

            if 'style_border' in props:
                borderStyle = props["style_border"]
            else:
                borderStyle = props["outline_style"]

            if 'width_border' in props:
                borderWidth = props["width_border"]
            else:
                borderWidth = props["outline_width"]

            try:
                lineCap = sl.penCapStyle()
                lineJoin = sl.penJoinStyle()
            except:
                lineCap = 0
                lineJoin = 0

            style = ('''%s %s''' %
                     (getStrokeStyle(borderColor, borderStyle, borderWidth,
                                     lineCap, lineJoin),
                      getFillStyle(fillColor, props)))
        else:
            style = ""
        styles.append('''new ol.style.Style({
        %s
    })''' % style)
    return "[ %s]" % ",".join(styles)


def getCircle(color, borderColor, borderWidth, size, props):
    return ("""new ol.style.Circle({radius: %s + size,
            %s %s})""" %
            (size,
             getStrokeStyle(borderColor, "", borderWidth, 0, 0),
             getFillStyle(color, props)))


def getIcon(path, size, svgWidth, svgHeight, rot):
    size = math.floor(float(size) * 3.8)
    anchor = size / 2
    scale = unicode(float(size)/float(svgWidth))
    return '''new ol.style.Icon({
                  imgSize: [%(w)s, %(h)s],
                  scale: %(scale)s,
                  anchor: [%(a)d, %(a)d],
                  anchorXUnits: "pixels",
                  anchorYUnits: "pixels",
                  rotation: %(rot)s,
                  src: "%(path)s"
            })''' % {"w": svgWidth, "h": svgHeight,
                     "scale": scale, "rot": rot,
                     "s": size, "a": anchor,
                     "path": path.replace("\\", "\\\\")}


def getStrokeStyle(color, dashed, width, linecap, linejoin):
    if dashed == "no":
        return ""
    width = math.floor(float(width) * 3.8)
    dash = dashed.replace("dash", "10,5")
    dash = dash.replace("dot", "1,5")
    dash = dash.replace("solid", "")
    dash = dash.replace(" ", ",")
    dash = "[%s]" % dash
    if dash == "[]" or dash == "[no]":
        dash = "null"
    capString = "round"
    if linecap == 0:
        capString = "butt"
    if linecap == 16:
        capString = "square"
    joinString = "round"
    if linejoin == 0:
        joinString = "miter"
    if linejoin == 64:
        joinString = "bevel"
    strokeString = ("stroke: new ol.style.Stroke({color: %s, lineDash: %s, " %
                    (color, dash))
    strokeString += ("lineCap: '%s', lineJoin: '%s', width: %d})," %
                     (capString, joinString, width))
    return strokeString


def getFillStyle(color, props):
    try:
        if props["style"] == "no":
            return ""
    except:
        pass
    return "fill: new ol.style.Fill({color: %s})" % color


def geolocation(geolocate):
    if geolocate:
        return """
      var geolocation = new ol.Geolocation({
  projection: map.getView().getProjection()
});


var accuracyFeature = new ol.Feature();
geolocation.on('change:accuracyGeometry', function() {
  accuracyFeature.setGeometry(geolocation.getAccuracyGeometry());
});

var positionFeature = new ol.Feature();
positionFeature.setStyle(new ol.style.Style({
  image: new ol.style.Circle({
    radius: 6,
    fill: new ol.style.Fill({
      color: '#3399CC'
    }),
    stroke: new ol.style.Stroke({
      color: '#fff',
      width: 2
    })
  })
}));

geolocation.on('change:position', function() {
  var coordinates = geolocation.getPosition();
  positionFeature.setGeometry(coordinates ?
      new ol.geom.Point(coordinates) : null);
});

var geolocateOverlay = new ol.layer.Vector({
  source: new ol.source.Vector({
    features: [accuracyFeature, positionFeature]
  })
});

geolocation.setTracking(true);
"""
    else:
        return ""


def geolocationHead(geolocate):
    if geolocate:
        return """
isTracking = false;
geolocateControl = function(opt_options) {
    var options = opt_options || {};
    var button = document.createElement('button');
    button.className += ' fa fa-map-marker';
    var handleGeolocate = function() {
        if (isTracking) {
            map.removeLayer(geolocateOverlay);
            isTracking = false;
      } else if (geolocation.getTracking()) {
            map.addLayer(geolocateOverlay);
            map.getView().setCenter(geolocation.getPosition());
            isTracking = true;
      }
    };
    button.addEventListener('click', handleGeolocate, false);
    button.addEventListener('touchstart', handleGeolocate, false);
    var element = document.createElement('div');
    element.className = 'geolocate ol-unselectable ol-control';
    element.appendChild(button);
    ol.control.Control.call(this, {
        element: element,
        target: options.target
    });
};
ol.inherits(geolocateControl, ol.control.Control);"""
    else:
        return ""


def geolocateStyle(geolocate):
    if geolocate:
        return """
        <style>
        .geolocate {
            top: 65px;
            left: .5em;
        }
        .ol-touch .geolocate {
            top: 80px;
        }
        </style>"""
    else:
        return ""


def geocodeLinks(geocode):
    if geocode:
        returnVal = """
    <link href="http://cdn.jsdelivr.net/openlayers.geocoder/latest/"""
        returnVal += """ol3-geocoder.min.css" rel="stylesheet">"""
        return returnVal
    else:
        return ""


def geocodeJS(geocode):
    if geocode:
        returnVal = """
    <script src="http://cdn.jsdelivr.net/openlayers.geocoder/latest/"""
        returnVal += """ol3-geocoder.js"></script>"""
        return returnVal
    else:
        return ""


def geocodeScript(geocode):
    if geocode:
        return """
var geocoder = new Geocoder('nominatim', {
  provider: 'osm',
  lang: 'en-US',
  placeholder: 'Search for ...',
  limit: 5,
  keepOpen: true
});
map.addControl(geocoder);"""
    else:
        return ""
