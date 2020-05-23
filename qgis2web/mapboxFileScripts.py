# -*- coding: utf-8 -*-

import re
import os
import shutil
import codecs
from qgis2web.utils import replaceInTemplate


def writeFoldersAndFiles(pluginDir, feedback, outputProjectFileName,
                         cluster_set, layerSearch, canvas, address):
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
                   layerSearch, canvas, locate, qgis2webJS, template,
                   feedback):
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
        <link rel="stylesheet" href="mapbox/"""
        addressCSS += """mapbox-gl-generic-geocoder.css">"""
        addressJS = """
        <script src="mapbox/mapbox-gl-generic-geocoder.min.js"></script>"""
    else:
        addressCSS = ""
        addressJS = ""
    if measure == "Metric":
        measureCSS = """
        <link rel="stylesheet" href="./mapbox/measure.css">"""
        measureJS = """
        <script src="./mapbox/measureMetric.js"></script>
        <script src="./mapbox/turf.min.js"></script>"""
    elif measure == "Imperial":
        measureCSS = """
        <link rel="stylesheet" href="./mapbox/measure.css">"""
        measureJS = """
        <script src="./mapbox/measureImperial.js"></script>
        <script src="./mapbox/turf.min.js"></script>"""
    else:
        measureCSS = ""
        measureJS = ""
    if locate:
        locateJS = """
        <script>
        map.addControl(
            new mapboxgl.GeolocateControl({
                positionOptions: {
                    enableHighAccuracy: true
                },
                trackUserLocation: true
            })
        );
        </script>"""
    else:
        locateJS = ""
    extraJS = ""
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
              "@LEAFLET_MEASUREJS@": "",
              "@LEAFLET_CRSJS@": "",
              "@LEAFLET_LAYERFILTERCSS@": "",
              "@LEAFLET_LAYERFILTERJS@": "",
              "@QGIS2WEBJS@": qgis2webJS,
              "@MAP_WIDTH@": unicode(canvasSize.width()) + "px",
              "@MAP_HEIGHT@": unicode(canvasSize.height()) + "px",
              "@EXP_JS@": exp_js,
              "@OL3_BACKGROUNDCOLOR@": "",
              "@OL3_STYLEVARS@": "",
              "@OL3_POPUP@": """<nav id="menu"></nav>
              <div id="distance" class="distance-container"></div>""",
              "@OL3_GEOJSONVARS@": "",
              "@OL3_WFSVARS@": "",
              "@OL3_PROJ4@": "",
              "@OL3_PROJDEF@": "",
              "@OL3_GEOCODINGLINKS@": "",
              "@OL3_GEOCODINGJS@": "",
              "@OL3_LAYERSWITCHER@": "",
              "@OL3_LAYERS@": "",
              "@OL3_MEASURESTYLE@": "",
              "@MBGLJS_MEASURE@": measureJS,
              "@MBGLJS_LOCATE@": locateJS}

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
         #menu {
            background: #fff;
            position: absolute;
            z-index: 1;
            top: 10px;
            right: 10px;
            border-radius: 3px;
            border: 1px solid rgba(50, 50, 50, 0.4);
            font-family: 'Open Sans',
            sans-serif;
        }

         #menu a {
            font-size: 13px;
            color: #999;
            background-color: #e8e8e8;
            display: block;
            margin: 0;
            padding: 0;
            padding: 10px;
            text-decoration: none;
            border-bottom: 1px solid rgba(0, 0, 0, 0.25);
        }

         #menu a:last-child {
            border: none;
        }

         #menu a:hover {
            background-color: #f8f8f8;
            color: #404040;
        }

         #menu a.active {
            background-color: #f8f8f8;
            color: #404040;
        }

         #menu a.active:hover {
            color: #999;
            background-color: #e8e8e8;
        }
        """
        f_css.write(text)
        f_css.close()
    feedback.completeStep()
