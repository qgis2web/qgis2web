# -*- coding: utf-8 -*-

import re
import os
import shutil
import codecs
from qgis2web.utils import replaceInTemplate


def writeFoldersAndFiles(pluginDir, feedback, outputProjectFileName,
                         cluster_set, measure, matchCRS, layerSearch,
                         filterItems, canvas, address, locate, layersList):
    feedback.showFeedback("Exporting libraries...")
    jsStore = os.path.join(outputProjectFileName, 'js')
    os.makedirs(jsStore)
    jsStore += os.sep
    jsDir = pluginDir + os.sep + 'leaflet' + os.sep + 'js' + os.sep
    dataStore = os.path.join(outputProjectFileName, 'data')
    os.makedirs(dataStore)
    imageDir = pluginDir + os.sep + 'leaflet' + os.sep + 'images' + os.sep
    imageStore = os.path.join(outputProjectFileName, 'images')
    legendStore = os.path.join(outputProjectFileName, 'legend')
    os.makedirs(legendStore)
    cssStore = os.path.join(outputProjectFileName, 'css')
    os.makedirs(cssStore)
    cssStore += os.sep
    cssDir = pluginDir + os.sep + 'leaflet' + os.sep + 'css' + os.sep
    fontDir = pluginDir + os.sep + 'webfonts' + os.sep
    fontStore = os.path.join(outputProjectFileName, 'webfonts')
    os.makedirs(fontStore)
    fontStore += os.sep
    markerStore = os.path.join(outputProjectFileName, 'markers')
    os.makedirs(markerStore)
    shutil.copyfile(jsDir + 'qgis2web_expressions.js',
                    jsStore + 'qgis2web_expressions.js')
    shutil.copyfile(jsDir + 'leaflet.wms.js',
                    jsStore + 'leaflet.wms.js')
    shutil.copyfile(jsDir + 'leaflet-tilelayer-wmts.js',
                    jsStore + 'leaflet-tilelayer-wmts.js')
    shutil.copyfile(jsDir + 'leaflet-svg-shape-markers.min.js',
                    jsStore + 'leaflet-svg-shape-markers.min.js')
    shutil.copyfile(jsDir + 'leaflet.pattern.js',
                    jsStore + 'leaflet.pattern.js')
    shutil.copyfile(jsDir + 'rbush.min.js',
                    jsStore + 'rbush.min.js')
    shutil.copyfile(jsDir + 'labelgun.min.js',
                    jsStore + 'labelgun.min.js')
    shutil.copyfile(jsDir + 'labels.js',
                    jsStore + 'labels.js')
    shutil.copyfile(jsDir + 'leaflet.js', jsStore + 'leaflet.js')
    shutil.copyfile(jsDir + 'leaflet.js.map', jsStore + 'leaflet.js.map')
    shutil.copyfile(cssDir + 'leaflet.css', cssStore + 'leaflet.css')
    if layersList != "None":
        shutil.copyfile(jsDir + 'L.Control.Layers.Tree.min.js',
                        jsStore + 'L.Control.Layers.Tree.min.js')
        shutil.copyfile(cssDir + 'L.Control.Layers.Tree.css',
                        cssStore + 'L.Control.Layers.Tree.css')
    if address:
        shutil.copyfile(jsDir + 'leaflet-control-geocoder.Geocoder.js',
                        jsStore + 'leaflet-control-geocoder.Geocoder.js')
        shutil.copyfile(cssDir + 'leaflet-control-geocoder.Geocoder.css',
                        cssStore + 'leaflet-control-geocoder.Geocoder.css')
    if locate:
        shutil.copyfile(jsDir + 'L.Control.Locate.min.js',
                        jsStore + 'L.Control.Locate.min.js')
        shutil.copyfile(cssDir + 'L.Control.Locate.min.css',
                        cssStore + 'L.Control.Locate.min.css')
    shutil.copyfile(jsDir + 'multi-style-layer.js',
                    jsStore + 'multi-style-layer.js')
    shutil.copyfile(jsDir + 'Autolinker.min.js',
                    jsStore + 'Autolinker.min.js')
    shutil.copyfile(jsDir + 'OSMBuildings-Leaflet.js',
                    jsStore + 'OSMBuildings-Leaflet.js')
    shutil.copyfile(jsDir + 'leaflet-heat.js',
                    jsStore + 'leaflet-heat.js')
    shutil.copyfile(jsDir + 'Leaflet.VectorGrid.js',
                    jsStore + 'Leaflet.VectorGrid.js')
    shutil.copyfile(jsDir + 'leaflet-hash.js', jsStore + 'leaflet-hash.js')
    shutil.copyfile(jsDir + 'leaflet.rotatedMarker.js',
                    jsStore + 'leaflet.rotatedMarker.js')

    # copy icons
    shutil.copyfile(cssDir + 'fontawesome-all.min.css',
                    cssStore + 'fontawesome-all.min.css')
    shutil.copyfile(fontDir + 'fa-solid-900.woff2',
                    fontStore + 'fa-solid-900.woff2')
    shutil.copyfile(fontDir + 'fa-solid-900.ttf',
                    fontStore + 'fa-solid-900.ttf')

    if len(cluster_set):
        shutil.copyfile(jsDir + 'leaflet.markercluster.js',
                        jsStore + 'leaflet.markercluster.js')
        shutil.copyfile(cssDir + 'MarkerCluster.css',
                        cssStore + 'MarkerCluster.css')
        shutil.copyfile(cssDir + 'MarkerCluster.Default.css',
                        cssStore + 'MarkerCluster.Default.css')
    if layerSearch != "None":
        shutil.copyfile(jsDir + 'leaflet-search.js',
                        jsStore + 'leaflet-search.js')
        shutil.copyfile(cssDir + 'leaflet-search.css',
                        cssStore + 'leaflet-search.css')
        shutil.copytree(imageDir, imageStore)
    else:
        os.makedirs(imageStore)
    if filterItems != []:
        shutil.copyfile(jsDir + 'tailDT.js',
                        jsStore + 'tailDT.js')
        shutil.copyfile(cssDir + 'filter.css',
                        cssStore + 'filter.css')
        shutil.copyfile(jsDir + 'nouislider.min.js',
                        jsStore + 'nouislider.min.js')
        shutil.copyfile(jsDir + 'wNumb.js',
                        jsStore + 'wNumb.js')
        shutil.copyfile(cssDir + 'nouislider.min.css',
                        cssStore + 'nouislider.min.css')
    if measure != "None":
        shutil.copyfile(jsDir + 'leaflet-measure.js',
                        jsStore + 'leaflet-measure.js')
        shutil.copyfile(cssDir + 'leaflet-measure.css',
                        cssStore + 'leaflet-measure.css')
    shutil.copytree(cssDir + 'images', cssStore + 'images')
    if (matchCRS and
            canvas.mapSettings().destinationCrs().authid() != 'EPSG:4326'):
        shutil.copyfile(jsDir + 'proj4.js', jsStore + 'proj4.js')
        shutil.copyfile(jsDir + 'proj4leaflet.js', jsStore + 'proj4leaflet.js')
    feedback.completeStep()
    return dataStore, cssStore


def writeHTMLstart(outputIndex, webpage_name, cluster_set, address, measure,
                   matchCRS, layerSearch, filterItems, canvas, locate,
                   qgis2webJS, template, feedback, useMultiStyle, useHeat,
                   useShapes, useOSMB, useWMS, useWMTS, useVT):
    useCluster = False
    for cluster in cluster_set:
        if cluster:
            useCluster = True
    feedback.showFeedback("Writing HTML...")
    cssAddress = '<link rel="stylesheet" href="css/leaflet.css">'
    jsAddress = '<script src="js/leaflet.js"></script>'
    cssAddress += """
        <link rel="stylesheet" href="css/L.Control.Layers.Tree.css">"""
    jsAddress += """
        <script src="js/L.Control.Layers.Tree.min.js"></script>"""
    if locate:
        cssAddress += """
        <link rel="stylesheet" href="css/L.Control.Locate.min.css">"""
        jsAddress += """
        <script src="js/L.Control.Locate.min.js"></script>"""
    if useMultiStyle:
        jsAddress += """
        <script src="js/multi-style-layer.js"></script>"""
    if useHeat:
        jsAddress += """
        <script src="js/leaflet-heat.js"></script>"""
    if useVT:
        jsAddress += """
        <script src="js/Leaflet.VectorGrid.js"></script>"""
    if useShapes:
        jsAddress += """
        <script src="js/leaflet-svg-shape-markers.min.js"></script>"""
    jsAddress += """
        <script src="js/leaflet.rotatedMarker.js"></script>
        <script src="js/leaflet.pattern.js"></script>"""
    if useOSMB:
        jsAddress += """
        <script src="js/OSMBuildings-Leaflet.js"></script>"""
    extracss = '<link rel="stylesheet" href="css/qgis2web.css">'
    extracss += """
        <link rel="stylesheet" href="css/fontawesome-all.min.css">"""
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
    if filterItems != []:
        layerFilterCSS = '<link rel="stylesheet" '
        layerFilterCSS += 'href="css/filter.css">\n'
        layerFilterCSS += '<link rel="stylesheet" '
        layerFilterCSS += 'href="css/nouislider.min.css">'
        layerFilterJS = '<script src="js/tailDT.js"></script>\n'
        layerFilterJS += '<script src="js/nouislider.min.js"></script>\n'
        layerFilterJS += '<script src="js/wNumb.js"></script>'
    else:
        layerFilterCSS = ""
        layerFilterJS = ""
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
    extraJS = """<script src="js/leaflet-hash.js"></script>
        <script src="js/Autolinker.min.js"></script>
        <script src="js/rbush.min.js"></script>
        <script src="js/labelgun.min.js"></script>
        <script src="js/labels.js"></script>"""
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
              "@LEAFLET_LAYERFILTERCSS@": layerFilterCSS,
              "@LEAFLET_LAYERFILTERJS@": layerFilterJS,
              "@LEAFLET_ADDRESSCSS@": addressCSS,
              "@LEAFLET_MEASURECSS@": measureCSS,
              "@LEAFLET_EXTRAJS@": extraJS,
              "@LEAFLET_ADDRESSJS@": addressJS,
              "@LEAFLET_MEASUREJS@": measureJS,
              "@LEAFLET_CRSJS@": crsJS,
              "@QGIS2WEBJS@": qgis2webJS,
              "@MAP_WIDTH@": str(canvasSize.width()) + "px",
              "@MAP_HEIGHT@": str(canvasSize.height()) + "px",
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
              "@OL3_MEASURESTYLE@": "",
              "@MBGLJS_MEASURE@": "",
              "@MBGLJS_LOCATE@": ""}

    with codecs.open(outputIndex, 'w', encoding='utf-8') as f:
        base = replaceInTemplate(template + ".html", values)
        base = re.sub(r'\n[\s_]+\n', '\n', base)
        f.write(base)
        f.close()
    feedback.completeStep()


def writeCSS(cssStore, backgroundColor, feedback, widgetAccent,
             widgetBackground, layersList):
    feedback.showFeedback("Writing CSS...")
    with open(cssStore + 'qgis2web.css', 'w') as f_css:
        text = """
        #map {
            background-color: """ + backgroundColor + """
        }
        html, body, #map {
			overflow: hidden;
        }
        .col9{
			height: 100%!important;
		}
		.col3{
			height: 100%;
			overflow: auto;
		}
        .info {
            padding: 6px 8px;
            font: 14px/16px Arial, Helvetica, sans-serif;
            background-color:""" + widgetBackground + """ !important;
            color: """ + widgetAccent + """ !important;
            box-shadow: 0 0 15px rgba(0,0,0,0.2);
            border-radius: 5px;
        }
        .info h2 {
            margin: 0 0 5px;
        }
        .leaflet-container {
            background: #fff;
            padding-right: 10px;
        }
        .leaflet-popup-scrolled {
            border-bottom: unset!important;
            border-top: unset!important;
        }
        .leaflet-popup-content{
            max-height: 70vh;
            max-width: 70vw;
        }
        .leaflet-popup-content.media{
            width: auto!important;
            height: auto!important;
        }
        .leaflet-popup-content th {
            text-align: left;
            vertical-align: top;
            min-width: 75px;
        }
        .leaflet-popup-content td {
            min-width: 75px;
        }
        .leaflet-popup-content td img {
            max-height: 60vh;
            max-width: 60vw;
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
        .abstract {
            font: bold 18px 'Lucida Console', Monaco, monospace;
            text-indent: 1px;
            background-color: """ + widgetBackground + """ !important;
            width: 30px !important;
            color: """ + widgetAccent + """ !important;
            height: 30px !important;
            text-align: center !important;
            line-height: 30px !important;
        }
        .abstractUncollapsed {
            padding: 6px 8px;
            font: 12px/1.5 "Helvetica Neue", Arial, Helvetica, sans-serif;
            background-color:""" + widgetBackground + """ !important;
            color: """ + widgetAccent + """ !important;
            box-shadow: 0 0 15px rgba(0,0,0,0.2);
            border-radius: 5px;
            max-width: 40%;
        }
        .leaflet-control {
            box-shadow: 0 3px 14px rgba(0, 0, 0, 0.4)!important;
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
        .leaflet-control-layers {
			padding: 2px;
			display: flex;
			flex-direction: column;
			align-items: flex-end;
            background-color: """ + widgetBackground + """ !important;
            color: """ + widgetAccent + """ !important;

		}
        .leaflet-control-layers-expanded {
			padding-left: 6px;
		}	
        .leaflet-control-layers-expanded .leaflet-control-layers-toggle {
            display: block;
            background-image: none;
			text-decoration: none;
            margin-bottom: 3px;
        }
        .leaflet-control-layers-expanded .leaflet-control-layers-toggle::after {
            content: '»';
            font-size: x-large;
            color: """ + widgetAccent + """ !important;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100%;
            height: 100%;
            text-align: center;
        }
        .leaflet-overlay-pane {
            z-index: 550;
        }
        .leaflet-popup-pane {
            z-index: 700;
        }"""
        if (layersList == "Collapsed"):
            text +="""
        .leaflet-control-layers-expanded .leaflet-control-layers-toggle {
            display: none;
        }
        """
        f_css.write(text)
        f_css.close()
    feedback.completeStep()
