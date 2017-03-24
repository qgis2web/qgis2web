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

import os
import re
from datetime import datetime
import traceback
import xml.etree.ElementTree
from qgis.core import (QgsProject,
                       QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsRectangle,
                       QgsCsException)
from utils import (exportLayers, replaceInTemplate)
from qgis.utils import iface
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QObject
from PyQt4.QtGui import (QApplication,
                         QCursor)
from olFileScripts import writeFiles, writeHTMLstart, writeScriptIncludes
from olLayerScripts import writeLayersAndGroups
from olScriptStrings import (measureScript,
                             measuringScript,
                             measureControlScript,
                             measureUnitMetricScript,
                             measureUnitFeetScript,
                             measureStyleScript,
                             geolocation,
                             geolocateStyle,
                             geolocationHead,
                             geocodeLinks,
                             geocodeJS,
                             geocodeScript)
from olStyleScripts import exportStyles
from writer import (Writer,
                    WriterResult,
                    translator)
from feedbackDialog import Feedback


class OpenLayersWriter(Writer):

    """
    Writer for creation of web maps based on the OpenLayers
    JavaScript library.
    """

    def __init__(self):
        super(OpenLayersWriter, self).__init__()

    @classmethod
    def type(cls):
        return 'openlayers'

    @classmethod
    def name(cls):
        return QObject.tr(translator, 'OpenLayers')

    def write(self, iface, dest_folder, feedback=None):
        if not feedback:
            feedback = Feedback()

        feedback.showFeedback('Creating OpenLayers map...')

        self.preview_file = self.writeOL(iface,
                                         feedback,
                                         layers=self.layers,
                                         groups=self.groups,
                                         popup=self.popup,
                                         visible=self.visible,
                                         json=self.json,
                                         clustered=self.cluster,
                                         settings=self.params,
                                         folder=dest_folder)
        result = WriterResult()
        result.index_file = self.preview_file
        result.folder = os.path.dirname(self.preview_file)
        for dirpath, dirnames, filenames in os.walk(result.folder):
            result.files.extend([os.path.join(dirpath, f) for f in filenames])
        return result

    @classmethod
    def writeOL(cls, iface, feedback, layers, groups, popup, visible,
                json, clustered, settings, folder):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        controlCount = 0
        stamp = datetime.now().strftime("%Y_%m_%d-%H_%M_%S_%f")
        folder = os.path.join(folder, 'qgis2web_' + unicode(stamp))
        restrictToExtent = settings["Scale/Zoom"]["Restrict to extent"]
        matchCRS = settings["Appearance"]["Match project CRS"]
        precision = settings["Data export"]["Precision"]
        optimize = settings["Data export"]["Minify GeoJSON files"]
        extent = settings["Scale/Zoom"]["Extent"]
        geolocateUser = settings["Appearance"]["Geolocate user"]
        maxZoom = int(settings["Scale/Zoom"]["Max zoom level"])
        minZoom = int(settings["Scale/Zoom"]["Min zoom level"])
        popupsOnHover = settings["Appearance"]["Show popups on hover"]
        highlightFeatures = settings["Appearance"]["Highlight on hover"]
        geocode = settings["Appearance"]["Add address search"]
        measureTool = settings["Appearance"]["Measure tool"]
        addLayersList = settings["Appearance"]["Add layers list"]
        htmlTemplate = settings["Appearance"]["Template"]
        layerSearch = unicode(settings["Appearance"]["Layer search"])
        searchLayer = settings["Appearance"]["Search layer"]
        mapLibLocn = settings["Data export"]["Mapping library location"]

        writeFiles(folder, restrictToExtent)
        exportLayers(iface, feedback, layers, folder, precision,
                     optimize, popup, json, restrictToExtent, extent)
        exportStyles(layers, folder, clustered)
        osmb = writeLayersAndGroups(layers, groups, visible, folder, popup,
                                    settings, json, matchCRS, clustered,
                                    iface, restrictToExtent, extent)
        (jsAddress, cssAddress, layerSearch,
         controlCount) = writeHTMLstart(settings, controlCount, osmb,
                                        mapLibLocn, layerSearch, searchLayer)
        (geojsonVars, wfsVars, styleVars) = writeScriptIncludes(layers,
                                                                json)
        popupLayers = "popupLayers = [%s];" % ",".join(
            ['1' for field in popup])
        controls = ['expandedAttribution']
        project = QgsProject.instance()
        if project.readBoolEntry("ScaleBar", "/Enabled", False)[0]:
            controls.append("new ol.control.ScaleLine({})")
        if measureTool != "None":
            controls.append(
                'new measureControl()')
        if geolocateUser:
            controls.append(
                'new geolocateControl()')
        if (addLayersList and addLayersList != "" and addLayersList != "None"):
            layersList = """
var layerSwitcher = new ol.control.LayerSwitcher({tipLabel: "Layers"});
map.addControl(layerSwitcher);"""
            if addLayersList == "Expanded":
                layersList += """
layerSwitcher.hidePanel = function() {};
layerSwitcher.showPanel();
"""
        else:
            layersList = ""
        pageTitle = project.title()
        mapSettings = iface.mapCanvas().mapSettings()
        backgroundColor = """
        <style>
        html, body {{
            background-color: {bgcol};
        }}
        </style>
""".format(bgcol=mapSettings.backgroundColor().name())
        (geolocateCode, controlCount) = geolocateStyle(geolocateUser,
                                                       controlCount)
        backgroundColor += geolocateCode
        mapbounds = bounds(iface, extent == "Canvas extent", layers, matchCRS)
        mapextent = "extent: %s," % mapbounds if restrictToExtent else ""
        onHover = unicode(popupsOnHover).lower()
        highlight = unicode(highlightFeatures).lower()
        highlightFill = mapSettings.selectionColor().name()
        proj4 = ""
        proj = ""
        view = "%s maxZoom: %d, minZoom: %d" % (
            mapextent, maxZoom, minZoom)
        if matchCRS:
            proj4 = """
<script src="http://cdnjs.cloudflare.com/ajax/libs/proj4js/2.3.6/proj4.js">"""
            proj4 += "</script>"
            proj = "<script>proj4.defs('{epsg}','{defn}');</script>"\
                .format(
                    epsg=mapSettings.destinationCrs().authid(),
                    defn=mapSettings.destinationCrs().toProj4())
            view += ", projection: '%s'" % (
                mapSettings.destinationCrs().authid())
        if measureTool != "None":
            measureControl = measureControlScript()
            measuring = measuringScript()
            measure = measureScript()
            if measureTool == "Imperial":
                measureUnit = measureUnitFeetScript()
            else:
                measureUnit = measureUnitMetricScript()
            measureStyle = measureStyleScript(controlCount)
            controlCount = controlCount + 1
        else:
            measureControl = ""
            measuring = ""
            measure = ""
            measureUnit = ""
            measureStyle = ""
        geolocateHead = geolocationHead(geolocateUser)
        geolocate = geolocation(geolocateUser)
        geocodingLinks = geocodeLinks(geocode)
        geocodingJS = geocodeJS(geocode)
        geocodingScript = geocodeScript(geocode)
        extracss = """
        <link rel="stylesheet" href="./resources/ol3-layerswitcher.css">
        <link rel="stylesheet" href="./resources/qgis2web.css">"""
        if geocode:
            geocodePos = 65 + (controlCount * 35)
            extracss += """
        <style>
        .ol-geocoder.gcd-gl-container {
            top: %dpx!important;
        }
        .ol-geocoder .gcd-gl-btn {
            width: 21px!important;
            height: 21px!important;
        }
        </style>""" % geocodePos
        if geolocateUser:
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
        exp_js = """
        <script src="resources/qgis2web_expressions.js"></script>"""
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
                  "@EXP_JS@": exp_js,
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
            htmlTemplate = htmlTemplate
            if htmlTemplate == "":
                htmlTemplate = "basic"
            templateOutput = replaceInTemplate(
                htmlTemplate + ".html", values)
            templateOutput = re.sub('\n[\s_]+\n', '\n', templateOutput)
            f.write(templateOutput)
        values = {"@GEOLOCATEHEAD@": geolocateHead,
                  "@BOUNDS@": mapbounds,
                  "@CONTROLS@": ",".join(controls),
                  "@LAYERSLIST@": layersList,
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
        with open(os.path.join(folder, "resources", "qgis2web.js"),
                  "w") as f:
            out = replaceInScript("qgis2web.js", values)
            f.write(out.encode("utf-8"))
        QApplication.restoreOverrideCursor()
        return os.path.join(folder, "index.html")


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
