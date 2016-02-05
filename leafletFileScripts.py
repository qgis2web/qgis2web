# -*- coding: utf-8 -*-

import re
import os
import shutil
import codecs
from utils import replaceInTemplate


def writeFoldersAndFiles(pluginDir, outputProjectFileName, cluster_set,
                         measure, matchCRS, canvas, mapLibLocation, locate):
    jsStore = os.path.join(outputProjectFileName, 'js')
    os.makedirs(jsStore)
    jsStore += os.sep
    jsDir = pluginDir + os.sep + 'js' + os.sep
    dataStore = os.path.join(outputProjectFileName, 'data')
    os.makedirs(dataStore)
    legendStore = os.path.join(outputProjectFileName, 'legend')
    os.makedirs(legendStore)
    cssStore = os.path.join(outputProjectFileName, 'css')
    os.makedirs(cssStore)
    cssStore += os.sep
    cssDir = pluginDir + os.sep + 'css' + os.sep
    markerStore = os.path.join(outputProjectFileName, 'markers')
    os.makedirs(markerStore)
    if mapLibLocation == "Local":
        shutil.copyfile(jsDir + 'leaflet.js', jsStore + 'leaflet.js')
        shutil.copyfile(cssDir + 'leaflet.css', cssStore + 'leaflet.css')
        if locate:
            os.makedirs(os.path.join(jsStore, "images"))
            shutil.copyfile(jsDir + 'images/marker-icon.png',
                            jsStore + 'images/marker-icon.png')
            shutil.copyfile(jsDir + 'images/marker-shadow.png',
                            jsStore + 'images/marker-shadow.png')
    shutil.copyfile(jsDir + 'Autolinker.min.js',
                    jsStore + 'Autolinker.min.js')
    shutil.copyfile(jsDir + 'leaflet-hash.js', jsStore + 'leaflet-hash.js')
    if len(cluster_set):
        shutil.copyfile(jsDir + 'leaflet.markercluster.js',
                        jsStore + 'leaflet.markercluster.js')
        shutil.copyfile(cssDir + 'MarkerCluster.css',
                        cssStore + 'MarkerCluster.css')
        shutil.copyfile(cssDir + 'MarkerCluster.Default.css',
                        cssStore + 'MarkerCluster.Default.css')
    shutil.copyfile(jsDir + 'label.js', jsStore + 'label.js')
    shutil.copyfile(cssDir + 'label.css', cssStore + 'label.css')
    if measure:
        shutil.copyfile(jsDir + 'leaflet.draw.js', jsStore + 'leaflet.draw.js')
        shutil.copyfile(cssDir + 'leaflet.draw.css',
                        cssStore + 'leaflet.draw.css')
        shutil.copyfile(jsDir + 'leaflet.measurecontrol.js',
                        jsStore + 'leaflet.measurecontrol.js')
        shutil.copyfile(cssDir + 'leaflet.measurecontrol.css',
                        cssStore + 'leaflet.measurecontrol.css')
        shutil.copytree(cssDir + 'images', cssStore + 'images')
    if (matchCRS and
            canvas.mapRenderer().destinationCrs().authid() != 'EPSG:4326'):
        shutil.copyfile(jsDir + 'proj4.js', jsStore + 'proj4.js')
        shutil.copyfile(jsDir + 'proj4leaflet.js', jsStore + 'proj4leaflet.js')
    return dataStore, cssStore


def writeHTMLstart(outputIndex, webpage_name, cluster_set, address, measure,
                   matchCRS, canvas, mapLibLocation, qgis2webJS, template):
    if webpage_name == "":
        pass
    else:
        webpage_name = unicode(webpage_name)
    if mapLibLocation == "Local":
        cssAddress = '<link rel="stylesheet" href="css/leaflet.css" />'
        jsAddress = '<script src="js/leaflet.js"></script>'
    else:
        cssAddress = '<link rel="stylesheet" href='
        cssAddress += '"http://http://cdn.leafletjs.com/leaflet/v0.7.7/'
        cssAddress += 'leaflet.css" />'
        jsAddress = '<script src="http://'
        jsAddress += 'cdn.leafletjs.com/leaflet/v0.7.7/leaflet.js"></script>'
    extracss = '<link rel="stylesheet" type="text/css" '
    extracss += """href="css/qgis2web.css">
        <link rel="stylesheet" href="css/label.css" />"""
    if len(cluster_set):
        clusterCSS = '<link rel="stylesheet" '
        clusterCSS += """href="css/MarkerCluster.css" />
        <link rel="stylesheet" href="css/MarkerCluster.Default.css" />"""
        clusterJS = '<script src="js/leaflet.markercluster.js">'
        clusterJS += "</script>"
    else:
        clusterCSS = ""
        clusterJS = ""
    if address:
        addressCSS = """
        <link rel="stylesheet" href="""
        addressCSS += '"http://k4r573n.github.io/leaflet-control-osm-geocoder/'
        addressCSS += 'Control.OSMGeocoder.css" />'
        addressJS = """
        <script src="http://k4r573n.github.io/leaflet-control-osm-geocoder/"""
        addressJS += 'Control.OSMGeocoder.js"></script>'
    else:
        addressCSS = ""
        addressJS = ""
    if measure:
        measureCSS = """
        <link rel="stylesheet" href="css/leaflet.draw.css" />
        <link rel="stylesheet" href="css/leaflet.measurecontrol.css" />"""
        measureJS = """
        <script src="js/leaflet.draw.js"></script>
        <script src="js/leaflet.measurecontrol.js"></script>"""
    else:
        measureCSS = ""
        measureJS = ""
    extraJS = """<script src="js/leaflet-hash.js"></script>
        <script src="js/label.js"></script>
        <script src="js/Autolinker.min.js"></script>"""
    if (matchCRS and
            canvas.mapRenderer().destinationCrs().authid() != 'EPSG:4326'):
        crsJS = """
        <script src="js/proj4.js"></script>
        <script src="js/proj4leaflet.js"></script>"""
    else:
        crsJS = ""

    canvasSize = canvas.size()
    values = {"@PAGETITLE@": webpage_name,
              "@CSSADDRESS@": cssAddress,
              "@EXTRACSS@": extracss,
              "@JSADDRESS@": jsAddress,
              "@LEAFLET_CLUSTERCSS@": clusterCSS,
              "@LEAFLET_CLUSTERJS@": clusterJS,
              "@LEAFLET_ADDRESSCSS@": addressCSS,
              "@LEAFLET_MEASURECSS@": measureCSS,
              "@LEAFLET_EXTRAJS@": extraJS,
              "@LEAFLET_ADDRESSJS@": addressJS,
              "@LEAFLET_MEASUREJS@": measureJS,
              "@LEAFLET_CRSJS@": crsJS,
              "@QGIS2WEBJS@": qgis2webJS,
              "@MAP_WIDTH@": unicode(canvasSize.width()) + "px",
              "@MAP_HEIGHT@": unicode(canvasSize.height()) + "px",
              "@OL3_BACKGROUNDCOLOR@": "",
              "@OL3_STYLEVARS@": "",
              "@OL3_POPUP@": "",
              "@OL3_GEOJSONVARS@": "",
              "@OL3_WFSVARS@": "",
              "@OL3_PROJ4@": "",
              "@OL3_PROJDEF@": "",
              "@OL3_GEOCODINGLINKS@": "",
              "@OL3_LAYERSWITCHER@": "",
              "@OL3_LAYERS@": "",
              "@OL3_MEASURESTYLE@": ""}

    with codecs.open(outputIndex, 'w', encoding='utf-8') as f:
        base = replaceInTemplate(template + ".html", values)
        base = re.sub('\n[\s_]+\n', '\n', base)
        f.write(unicode(base))
        f.close()


def writeCSS(cssStore, backgroundColor):
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
}"""
        f_css.write(text)
        f_css.close()
