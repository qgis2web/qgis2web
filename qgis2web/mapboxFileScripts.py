# -*- coding: utf-8 -*-

import re
import os
import shutil
import codecs
from qgis2web.utils import replaceInTemplate


def writeFoldersAndFiles(pluginDir, feedback, outputProjectFileName,
                         cluster_set, measure, matchCRS, layerSearch, canvas,
                         address, locate):
    feedback.showFeedback("Exporting libraries...")
    jsStore = os.path.join(outputProjectFileName, 'js')
    os.makedirs(jsStore)
    jsStore += os.sep
    jsDir = pluginDir + os.sep + 'js' + os.sep
    dataStore = os.path.join(outputProjectFileName, 'data')
    os.makedirs(dataStore)
    imageDir = pluginDir + os.sep + 'images' + os.sep
    imageStore = os.path.join(outputProjectFileName, 'images')
    legendStore = os.path.join(outputProjectFileName, 'legend')
    os.makedirs(legendStore)
    cssStore = os.path.join(outputProjectFileName, 'css')
    os.makedirs(cssStore)
    cssStore += os.sep
    cssDir = pluginDir + os.sep + 'css' + os.sep
    fontDir = pluginDir + os.sep + 'webfonts' + os.sep
    fontStore = os.path.join(outputProjectFileName, 'webfonts')
    os.makedirs(fontStore)
    fontStore += os.sep
    markerStore = os.path.join(outputProjectFileName, 'markers')
    os.makedirs(markerStore)
    shutil.copyfile(jsDir + 'qgis2web_expressions.js',
                    jsStore + 'qgis2web_expressions.js')
    shutil.copyfile(jsDir + 'Autolinker.min.js',
                    jsStore + 'Autolinker.min.js')
    shutil.copytree(cssDir + 'images', cssStore + 'images')
    feedback.completeStep()
    return dataStore, cssStore


def writeHTMLstart(outputIndex, webpage_name, cluster_set, address, measure,
                   matchCRS, layerSearch, canvas, locate, qgis2webJS, template,
                   feedback, useMultiStyle, useHeat, useShapes,
                   useOSMB, useWMS, useWMTS, useVT):
    useCluster = False
    for cluster in cluster_set:
        if cluster:
            useCluster = True
    feedback.showFeedback("Writing HTML...")
    if webpage_name == "":
        pass
    else:
        webpage_name = unicode(webpage_name)
    cssAddress = '<link rel="stylesheet" href="mapbox/mapbox-gl.css">'
    jsAddress = '<script src="./mapbox/mapbox-gl.js">'
    jsAddress += '</script>'
    extracss = '<link rel="stylesheet" href="css/qgis2web.css">'
    if useCluster:
        clusterCSS = """<link rel="stylesheet" href="css/MarkerCluster.css">
        <link rel="stylesheet" href="css/MarkerCluster.Default.css">"""
        clusterJS = '<script src="js/leaflet.markercluster.js">'
        clusterJS += "</script>"
    else:
        clusterCSS = ""
        clusterJS = ""
    if layerSearch != "None":
        layerSearchCSS = '<link rel="stylesheet" '
        layerSearchCSS += 'href="css/leaflet-search.css">'
        layerSearchJS = '<script src="js/leaflet-search.js"></script>'
    else:
        layerSearchCSS = ""
        layerSearchJS = ""
    if address:
        addressCSS = """
        <link rel="stylesheet" href="css/"""
        addressCSS += """leaflet-control-geocoder.Geocoder.css">"""
        addressJS = """
        <script src="js/leaflet-control-geocoder.Geocoder.js"></script>"""
    else:
        addressCSS = ""
        addressJS = ""
    if measure != "None":
        measureCSS = """
        <link rel="stylesheet" href="css/leaflet-measure.css">"""
        measureJS = """
        <script src="js/leaflet-measure.js"></script>"""
    else:
        measureCSS = ""
        measureJS = ""
    extraJS = ""
    if useWMS:
        extraJS += """
        <script src="js/leaflet.wms.js"></script>"""
    if useWMTS:
        extraJS += """
        <script src="js/leaflet-tilelayer-wmts.js"></script>"""
    if (matchCRS and
            canvas.mapSettings().destinationCrs().authid() != 'EPSG:4326'):
        crsJS = """
        <script src="js/proj4.js"></script>
        <script src="js/proj4leaflet.js"></script>"""
    else:
        crsJS = ""
    exp_js = """
        <script src="js/qgis2web_expressions.js"></script>"""

    canvasSize = canvas.size()
    values = {"@PAGETITLE@": webpage_name,
              "@CSSADDRESS@": cssAddress,
              "@EXTRACSS@": extracss,
              "@JSADDRESS@": jsAddress,
              "@LEAFLET_CLUSTERCSS@": clusterCSS,
              "@LEAFLET_CLUSTERJS@": clusterJS,
              "@LEAFLET_LAYERSEARCHCSS@": layerSearchCSS,
              "@LEAFLET_LAYERSEARCHJS@": layerSearchJS,
              "@LEAFLET_ADDRESSCSS@": addressCSS,
              "@LEAFLET_MEASURECSS@": measureCSS,
              "@LEAFLET_EXTRAJS@": extraJS,
              "@LEAFLET_ADDRESSJS@": addressJS,
              "@LEAFLET_MEASUREJS@": measureJS,
              "@LEAFLET_CRSJS@": crsJS,
              "@LEAFLET_LAYERFILTERCSS@": "",
              "@LEAFLET_LAYERFILTERJS@": "",
              "@QGIS2WEBJS@": qgis2webJS,
              "@MAP_WIDTH@": unicode(canvasSize.width()) + "px",
              "@MAP_HEIGHT@": unicode(canvasSize.height()) + "px",
              "@EXP_JS@": exp_js,
              "@OL3_BACKGROUNDCOLOR@": "",
              "@OL3_STYLEVARS@": "",
              "@OL3_POPUP@": "",
              "@OL3_GEOJSONVARS@": "",
              "@OL3_WFSVARS@": "",
              "@OL3_PROJ4@": "",
              "@OL3_PROJDEF@": "",
              "@OL3_GEOCODINGLINKS@": "",
              "@OL3_GEOCODINGJS@": "",
              "@OL3_LAYERSWITCHER@": "",
              "@OL3_LAYERS@": "",
              "@OL3_MEASURESTYLE@": ""}

    with codecs.open(outputIndex, 'w', encoding='utf-8') as f:
        base = replaceInTemplate(template + ".html", values)
        base = re.sub(r'\n[\s_]+\n', '\n', base)
        f.write(unicode(base))
        f.close()
    feedback.completeStep()


def writeCSS(cssStore, backgroundColor, feedback, widgetAccent,
             widgetBackground):
    feedback.showFeedback("Writing CSS...")
    with open(cssStore + 'qgis2web.css', 'w') as f_css:
        text = """
        #map {
            background-color: """ + backgroundColor + """
        }
        th {
            text-align: left;
            vertical-align: top;
        }
        .info {
            padding: 6px 8px;
            font: 14px/16px Arial, Helvetica, sans-serif;
            background: white;
            background: rgba(255,255,255,0.8);
            box-shadow: 0 0 15px rgba(0,0,0,0.2);
            border-radius: 5px;
        }
        .info h2 {
            margin: 0 0 5px;
            color: #777;
        }
        .leaflet-container {
            background: #fff;
            padding-right: 10px;
        }
        .leaflet-popup-content {
            width:auto !important;
            padding-right:10px;
        }
        .leaflet-tooltip {
            background: none;
            box-shadow: none;
            border: none;
        }
        .leaflet-tooltip-left:before, .leaflet-tooltip-right:before {
            border: 0px;
        }
        }
        .fa, .leaflet-container, a {
            color: """ + widgetAccent + """ !important;
        }
        .leaflet-control-zoom-in, .leaflet-control-zoom-out,
        .leaflet-control-locate a,
        .leaflet-touch .leaflet-control-geocoder-icon,
        .leaflet-control-search .search-button,
         .leaflet-control-measure {
            background-color: """ + widgetBackground + """ !important;
            border-radius: 0px !important;
            color: """ + widgetAccent + """ !important;
        }
        .leaflet-touch .leaflet-control-layers,
        .leaflet-touch .leaflet-bar,
        .leaflet-control-search,
        .leaflet-control-measure {
            border: 3px solid rgba(255,255,255,.4) !important;
        }
        .leaflet-control-attribution a {
            color: #0078A8 !important;
        }
        .leaflet-control-scale-line {
            border: 2px solid """ + widgetBackground + """ !important;
            border-top: none !important;
            color: black !important;
        }
        .leaflet-control-search .search-button,
        .leaflet-container .leaflet-control-search,
        .leaflet-control-measure {
            box-shadow: none !important;
        }
        .leaflet-control-search .search-button {
            width: 30px !important;
            height: 30px !important;
            font-size: 13px !important;
            text-align: center !important;
            line-height: 30px !important;
        }
        .leaflet-control-measure .leaflet-control {
            width: 30px !important;
            height: 30px !important;
        }
        .leaflet-container .leaflet-control-search{
            background: none !important;
        }
        .leaflet-control-search .search-input {
            margin: 0px 0px 0px 0px !important;
            height: 30px !important;
        }
        .leaflet-control-measure {
            background: none!important;
            border-radius: 4px !important;
        }
        .leaflet-control-measure .leaflet-control-measure-interaction {
            background-color: """ + widgetBackground + """ !important;
        }
        .leaflet-touch .leaflet-control-measure
        .leaflet-control-measure-toggle,
        .leaflet-touch .leaflet-control-measure
        .leaflet-control-measure-toggle:hover {
            width: 30px !important;
            height: 30px !important;
            border-radius: 0px !important;
            background-color: """ + widgetBackground + """ !important;
            color: """ + widgetAccent + """ !important;
            font-size: 13px;
            line-height: 30px;
            text-align: center;
            text-indent: 0%;
        }
        .leaflet-control-layers-toggle {
            background-color: """ + widgetBackground + """ !important;
        }"""
        f_css.write(text)
        f_css.close()
    feedback.completeStep()
