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
from qgis.core import (QgsProject,
                       QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsRectangle,
                       QgsCsException)
from qgis.PyQt.QtCore import Qt, QObject
from qgis.PyQt.QtGui import QCursor
from qgis.PyQt.QtWidgets import QApplication
from qgis2web.utils import exportLayers, replaceInTemplate
from qgis2web.olFileScripts import (writeFiles,
                                    writeHTMLstart,
                                    writeLayerSearch,
                                    writeScriptIncludes)
from qgis2web.olLayerScripts import writeLayersAndGroups
from qgis2web.olScriptStrings import (measureScript,
                                      measuringScript,
                                      measureControlScript,
                                      measureUnitMetricScript,
                                      measureUnitFeetScript,
                                      measureStyleScript,
                                      #layerSearchStyleScript,
                                      geolocation,
                                      #geolocateStyle,
                                      geolocationHead,
                                      geocodeLinks,
                                      geocodeJS,
                                      geocodeScript,
                                      getGrid,
                                      getM2px,
                                      getMapUnitLayers,
                                      #titleControlScript,
                                      #abstractControlScript
                                      )
from qgis2web.olStyleScripts import exportStyles
from qgis2web.writer import (Writer,
                             WriterResult,
                             translator)
from qgis2web.feedbackDialog import Feedback


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

        self.preview_file = self.writeOL(iface, feedback,
                                         layers=self.layers,
                                         groups=self.groups,
                                         popup=self.popup,
                                         visible=self.visible,
                                         interactive=self.interactive,
                                         json=self.json,
                                         clustered=self.cluster,
                                         getFeatureInfo=self.getFeatureInfo,
                                         baseMap=self.baseMap,
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
                interactive, json, clustered, getFeatureInfo, baseMap, settings,
                folder):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        mapSettings = iface.mapCanvas().mapSettings()
        controlCount = 0
        stamp = datetime.now().strftime("%Y_%m_%d-%H_%M_%S_%f")
        folder = os.path.join(folder, 'qgis2web_' + stamp)
        restrictToExtent = settings["Scale/Zoom"]["Restrict to extent"]
        matchCRS = settings["Appearance"]["Match project CRS"]
        precision = settings["Data export"]["Precision"]
        optimize = settings["Data export"]["Minify GeoJSON files"]
        extent = settings["Scale/Zoom"]["Extent"]
        mapbounds = bounds(iface, extent == "Canvas extent", layers, matchCRS)
        fullextent = bounds(iface, False, layers, matchCRS)
        geolocateUser = settings["Appearance"]["Geolocate user"]
        maxZoom = int(settings["Scale/Zoom"]["Max zoom level"])
        minZoom = int(settings["Scale/Zoom"]["Min zoom level"])
        popupsOnHover = settings["Appearance"]["Show popups on hover"]
        highlightFeatures = settings["Appearance"]["Highlight on hover"]
        geocode = settings["Appearance"]["Address search"]
        measureTool = settings["Appearance"]["Measure tool"]
        addLayersList = settings["Appearance"]["Layers list"]
        htmlTemplate = settings["Appearance"]["Template"]
        layerSearch = settings["Appearance"]["Layer search"]
        searchLayer = settings["Appearance"]["Search layer"]
        widgetAccent = settings["Appearance"]["Widget Icon"]
        widgetBackground = settings["Appearance"]["Widget Background"]
        titleOption = settings["Appearance"]["Title"]
        abstractOption = settings["Appearance"]["Abstract"]

        writeFiles(folder, restrictToExtent, feedback)
        exportLayers(iface, layers, folder, precision, optimize,
                     popup, json, restrictToExtent, extent, feedback, matchCRS)
        mapUnitsLayers = exportStyles(layers, folder, clustered, feedback)
        mapUnitLayers = getMapUnitLayers(mapUnitsLayers)
        osmb = writeLayersAndGroups(layers, groups, visible, interactive,
                                    folder, popup, settings, json, matchCRS,
                                    clustered, getFeatureInfo, baseMap, iface,
                                    restrictToExtent, extent, mapbounds,
                                    mapSettings.destinationCrs().authid())
        (jsAddress,
         cssAddress, controlCount) = writeHTMLstart(settings, controlCount,
                                                    osmb, feedback)
        (geojsonVars, wfsVars, styleVars) = writeScriptIncludes(layers,
                                                                json, matchCRS)
        popupLayers = "popupLayers = [%s];" % ",".join(
            ['1' for field in popup])
        project = QgsProject.instance()
        #controls = getControls(project, measureTool, geolocateUser)
        layersList = getLayersList(addLayersList)
        projectTitle = project.title()
        projectAbstract = project.metadata().abstract()
        title = titleControlScript(projectTitle, titleOption)
        abstract = abstractControlScript(projectAbstract, abstractOption)

        backgroundColor = getBackground(mapSettings, widgetAccent,
                                        widgetBackground)
        # (geolocateCode, controlCount) = geolocateStyle(geolocateUser,
        #                                                controlCount)
        #backgroundColor += geolocateCode
        mapextent = "extent: %s," % mapbounds if restrictToExtent else ""
        onHover = str(popupsOnHover).lower()
        highlight = str(highlightFeatures).lower()
        highlightFill = mapSettings.selectionColor().name()
        (proj, proj4, view) = getCRSView(mapextent, fullextent, maxZoom,
                                         minZoom, matchCRS, mapSettings)
        (measureControl, measuring, measure, measureUnit, measureStyle,
         controlCount) = getMeasure(measureTool, controlCount)
        geolocateHead = geolocationHead(geolocateUser)
        geolocate = geolocation(geolocateUser)
        geocodingLinks = geocodeLinks(geocode)
        geocodingJS = geocodeJS(geocode)
        geocodingScript = geocodeScript(geocode)
        scaleBar = scaleBarScript(project)
        m2px = getM2px(mapUnitsLayers)
        (extracss, controlCount) = getCSS(geocode, geolocateUser, layerSearch,
                                          controlCount)
        (jsAddress, cssAddress,
         layerSearch, controlCount) = writeLayerSearch(cssAddress, jsAddress,
                                                       controlCount,
                                                       layerSearch,
                                                       searchLayer, feedback)
        ol3layerswitcher = getLayerSwitcher()
        ol3popup = getPopup()
        ol3qgis2webjs = getJS(osmb)
        ol3layers = getLayers()
        mapSize = iface.mapCanvas().size()
        exp_js = getExpJS()
        grid = getGrid(project)
        values = {"@PAGETITLE@": projectTitle,
                  "@CSSADDRESS@": cssAddress,
                  "@EXTRACSS@": extracss,
                  "@JSADDRESS@": jsAddress,
                  "@MAP_WIDTH@": str(mapSize.width()) + "px",
                  "@MAP_HEIGHT@": str(mapSize.height()) + "px",
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
                  "@LEAFLET_LAYERFILTERCSS@": "",
                  "@LEAFLET_EXTRAJS@": "",
                  "@LEAFLET_ADDRESSJS@": "",
                  "@LEAFLET_MEASUREJS@": "",
                  "@LEAFLET_CRSJS@": "",
                  "@LEAFLET_LAYERSEARCHCSS@": "",
                  "@LEAFLET_LAYERSEARCHJS@": "",
                  "@LEAFLET_LAYERFILTERJS@": "",
                  "@LEAFLET_CLUSTERCSS@": "",
                  "@LEAFLET_CLUSTERJS@": "",
                  "@MBGLJS_MEASURE@": "",
                  "@MBGLJS_LOCATE@": ""}
        with open(os.path.join(folder, "index.html"), "w") as f:
            htmlTemplate = htmlTemplate
            if htmlTemplate == "":
                htmlTemplate = "full-screen"
            templateOutput = replaceInTemplate(
                htmlTemplate + ".html", values)
            templateOutput = re.sub(r'\n[\s_]+\n', '\n', templateOutput)
            f.write(templateOutput)
        values = {"@GEOLOCATEHEAD@": geolocateHead,
                  "@BOUNDS@": mapbounds,
                  #"@CONTROLS@": ",".join(controls),
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
                  "@MEASUREUNIT@": measureUnit,
                  "@GRID@": grid,
                  "@M2PX@": m2px,
                  "@MAPUNITLAYERS@": mapUnitLayers,
                  "@TITLE@": title,
                  "@ABSTRACT@": abstract,
                  "@SCALEBAR@": scaleBar}
        with open(os.path.join(folder, "resources", "qgis2web.js"),
                  "w") as f:
            out = replaceInScript("qgis2web.js", values)
            f.write(out)
        QApplication.restoreOverrideCursor()
        return os.path.join(folder, "index.html")


def replaceInScript(template, values):
    path = os.path.join(os.path.dirname(__file__), "openlayers", template)
    with open(path) as f:
        lines = f.readlines()
    s = "".join(lines)
    for name, value in values.items():
        s = s.replace(name, value)
    return s


def bounds(iface, useCanvas, layers, matchCRS):
    if useCanvas:
        canvas = iface.mapCanvas()
        canvasCrs = canvas.mapSettings().destinationCrs()
        if not matchCRS:
            epsg3857 = QgsCoordinateReferenceSystem("EPSG:3857")
            try:
                transform = QgsCoordinateTransform(canvasCrs, epsg3857,
                                                   QgsProject.instance())
            except Exception:
                transform = QgsCoordinateTransform(canvasCrs, epsg3857)

            try:
                extent = transform.transformBoundingBox(canvas.extent())
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
                try:
                    transform = QgsCoordinateTransform(layer.crs(), epsg3857,
                                                       QgsProject.instance())
                except Exception:
                    transform = QgsCoordinateTransform(layer.crs(), epsg3857)

                try:
                    layerExtent = transform.transformBoundingBox(
                        layer.extent())
                except QgsCsException:
                    layerExtent = QgsRectangle(-20026376.39, -20048966.10,
                                               20026376.39, 20048966.10)
            else:
                layerExtent = layer.extent()
            if extent is None:
                extent = layerExtent
            else:
                extent.combineExtentWith(layerExtent)

    if extent is None:
        extent = QgsRectangle(-20026376.39, -20048966.10,
                              20026376.39, 20048966.10)

    return "[%f, %f, %f, %f]" % (extent.xMinimum(), extent.yMinimum(),
                                 extent.xMaximum(), extent.yMaximum())


# def getControls(project, measureTool, geolocateUser):
    #controls = ['expandedAttribution']
    # controls =[]
    # if project.readBoolEntry("ScaleBar", "/Enabled", False)[0]:
    #     controls.append("new ol.control.ScaleLine({})")
    # if measureTool != "None":
    #     controls.append('new measureControl()')
    # if geolocateUser:
    #     controls.append('new geolocateControl()')
    # return controls


def getLayersList(addLayersList):
    if (addLayersList and addLayersList != "" and addLayersList != "None"):
        if addLayersList == "Collapsed":
            layersList = """
var layerSwitcher = new ol.control.LayerSwitcher({
    tipLabel: "Layers",
    target: 'top-right-container'
});
map.addControl(layerSwitcher);
    """
        if addLayersList == "Expanded":
            layersList = """
var layerSwitcher = new ol.control.LayerSwitcher({
    activationMode: 'click',
	startActive: true,
	tipLabel: "Layers",
    target: 'top-right-container',
	collapseLabel: '»',
	collapseTipLabel: 'Close'
    });
map.addControl(layerSwitcher);
if (hasTouchScreen || isSmallScreen) {
	document.addEventListener('DOMContentLoaded', function() {
		setTimeout(function() {
			layerSwitcher.hidePanel();
		}, 500);
	});	
}
"""     
    else:
        layersList = ""
    return layersList

def hex_to_rgba(hex_color, alpha):
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"

def getBackground(mapSettings, widgetAccent, widgetBackground):
    hover_focus_color = hex_to_rgba(widgetBackground.lstrip('#'), 0.7)
    return """
        <style>
        html, body {{
            background-color: {bgcol};
        }}
        .ol-control > * {{
            background-color: {widgetBackground}!important;
            color: {widgetAccent}!important;
            border-radius: 0px;
        }}
        .ol-attribution a, .gcd-gl-input::placeholder, .search-layer-input-search::placeholder {{
            color: {widgetAccent}!important;
        }}
        .search-layer-input-search {{
            background-color: {widgetBackground}!important;
        }}
        .ol-control > *:focus, .ol-control >*:hover {{
            background-color: {hover_focus_color}!important;
        }} 
        .ol-control {{
            background-color: rgba(255,255,255,.4) !important;
            padding: 2px !important;
        }} 
        </style>
""".format(bgcol=mapSettings.backgroundColor().name(),
           widgetBackground=widgetBackground,
           widgetAccent=widgetAccent,
           hover_focus_color=hover_focus_color)


def getCRSView(mapextent, fullextent, maxZoom, minZoom, matchCRS, mapSettings):
    units = ['m', 'km', 'ft', '', '', '', 'degrees', '', 'cm', 'mm', '']
    proj4 = ""
    proj = ""
    view = "%s maxZoom: %d, minZoom: %d" % (mapextent, maxZoom, minZoom)
    if matchCRS:
        proj4 = """
<script src="resources/proj4.js">"""
        proj4 += "</script>"
        proj = "<script>proj4.defs('{epsg}','{defn}');</script>".format(
            epsg=mapSettings.destinationCrs().authid(),
            defn=mapSettings.destinationCrs().toProj4())
        unit = mapSettings.destinationCrs().mapUnits()
        view += """, projection: new ol.proj.Projection({
            code: '%s',
            //extent: %s,
            units: '%s'})""" % (mapSettings.destinationCrs().authid(),
                                fullextent, units[unit])
    return (proj, proj4, view)


def getMeasure(measureTool, controlCount):
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
    return (measureControl, measuring, measure, measureUnit, measureStyle,
            controlCount)


def getCSS(geocode, geolocateUser, layerSearch, controlCount):
    extracss = """
        <link rel="stylesheet" """
    extracss += """href="./resources/ol-layerswitcher.css">
        <link rel="stylesheet" """
    extracss += """href="./resources/qgis2web.css">"""
    # if geocode:
    #     geocodePos = 65 + (controlCount * 35)
    #     touchPos = 80 + (controlCount * 50)
    #     controlCount += 1
    #     extracss += """
    #     <style>
    #     .ol-geocoder.gcd-gl-container {
    #         top: %dpx!important;
    #         left: 8px!important;
    #     }
    #     .ol-touch .ol-geocoder.gcd-gl-container{
    #         top: %dpx!important;
    #     }
    #     .ol-geocoder .gcd-gl-btn:after{
    #         display:none;
    #     }
    #     </style>""" % (geocodePos, touchPos)
    # if layerSearch:
    #     (layerSearchStyle, controlCount) = layerSearchStyleScript(controlCount)
    #     extracss += layerSearchStyle
    return (extracss, controlCount)


def getLayerSwitcher():
    return """
        <script src="./resources/ol-layerswitcher.js"></script>"""


def getPopup():
    return """<div id="popup" class="ol-popup">
                <a href="#" id="popup-closer" class="ol-popup-closer"></a>
                <div id="popup-content"></div>
            </div>"""


def getJS(osmb):
    ol3qgis2webjs = """<script src="./resources/Autolinker.min.js"></script>
        <script src="./resources/qgis2web.js"></script>"""
    if osmb != "":
        ol3qgis2webjs += """
        <script>{osmb}</script>""".format(osmb=osmb)
    return ol3qgis2webjs


def getLayers():
    return """
        <script src="./layers/layers.js" type="text/javascript"></script>"""


def getExpJS():
    return """
        <script src="resources/qgis2web_expressions.js"></script>"""



def titleControlScript(pTitle, pOption):
    if pOption == "None" or not pTitle:
        return ""
    
    title_classes = {
        "upper right": "top-right-title",
        "upper left": "top-left-title",
        "lower right": "bottom-right-title",
        "lower left": "bottom-left-title"
    }
    target_containers = {
        "upper right": "top-right-container",
        "upper left": "top-left-container",
        "lower right": "bottom-right-container",
        "lower left": "bottom-left-container"
    }
    title_class = title_classes.get(pOption)
    target_container = target_containers.get(pOption)
    
    titleControl = """
var Title = new ol.control.Control({
    element: (() => {
        var titleElement = document.createElement('div');
        titleElement.className = '%TITLE_CLASS% ol-control';
        titleElement.innerHTML = '<h2 class="project-title">%PTITLE%</h2>';
        return titleElement;
    })(),
    target: '%TARGET_CONTAINER%'
});
map.addControl(Title)
    """.replace("%PTITLE%", pTitle).replace("%TITLE_CLASS%", title_class).replace("%TARGET_CONTAINER%", target_container)
    return titleControl


def abstractControlScript(pAbstract, pOption):
    if pOption == "None" or not pAbstract:
        return ""
    
    abstract_classes = {
        "upper right": "top-right-abstract",
        "upper left": "top-left-abstract",
        "lower right": "bottom-right-abstract",
        "lower left": "bottom-left-abstract"
    }

    target_containers = {
        "upper right": "top-right-container",
        "upper left": "top-left-container",
        "lower right": "bottom-right-container",
        "lower left": "bottom-left-container"
    }

    abstract_class = abstract_classes.get(pOption)
    target_container = target_containers.get(pOption)

    if not abstract_class or not target_container:
        return
    
    abstractControl = """
var Abstract = new ol.control.Control({
    element: (() => {
        var titleElement = document.createElement('div');
        titleElement.className = '%ABSTRACT_CLASS% ol-control';
        titleElement.id = 'abstract';

        var linkElement = document.createElement('a');

        if (%PABSTRACT_LEN% > 240) {
            linkElement.setAttribute("onmouseenter", "showAbstract()");
            linkElement.setAttribute("onmouseleave", "hideAbstract()");
            linkElement.innerHTML = 'i';

            window.hideAbstract = function() {
                linkElement.classList.add("project-abstract");
                linkElement.classList.remove("project-abstract-uncollapsed");
                linkElement.innerHTML = 'i';
            }

            window.showAbstract = function() {
                linkElement.classList.remove("project-abstract");
                linkElement.classList.add("project-abstract-uncollapsed");
                linkElement.innerHTML = '%PABSTRACT%';
            }

            hideAbstract();
        } else {
            linkElement.classList.add("project-abstract-uncollapsed");
            linkElement.innerHTML = '%PABSTRACT%';
        }

        titleElement.appendChild(linkElement);
        return titleElement;
    })(),
    target: '%TARGET_CONTAINER%'
});
map.addControl(Abstract);
""".replace("%ABSTRACT_CLASS%", abstract_class)\
   .replace("%PABSTRACT%", pAbstract.replace("'", "\\'").replace("\n", "<br />"))\
   .replace("%TARGET_CONTAINER%", target_container)\
   .replace("%PABSTRACT_LEN%", str(len(pAbstract)))

    return abstractControl


def scaleBarScript(project):
    if project.readBoolEntry("ScaleBar", "/Enabled", False)[0]:
        return """
map.addControl(new ol.control.ScaleLine({}));"""
    else:
        return ""
