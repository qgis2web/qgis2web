# -*- coding: utf-8 -*-

import os
import shutil


def writeFoldersAndFiles(pluginDir, outputProjectFileName, cluster_set,
                         labels, measure, matchCRS, canvas,
                         mapLibLocation, locate):
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
    if len(labels):
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


def writeHTMLstart(outputIndex, webpage_name, cluster_set, labels, address,
                   measure, matchCRS, canvas, full, mapLibLocation):
    with open(outputIndex, 'w') as f_html:
        base = """<!DOCTYPE html>
<html>
    <head>"""
        if webpage_name == "":
            base += """
        <title>qgis2web Leaflet webmap</title>
    """
        else:
            base += """
        <title>""" + (webpage_name).encode('utf-8') + """</title>"""
        base += """
        <meta charset="utf-8" />"""
        if mapLibLocation == "Local":
            base += """
        <link rel="stylesheet" href="css/leaflet.css" />"""
        else:
            base += """
        <link rel="stylesheet" href="""
            base += '"http://cdn.leafletjs.com/leaflet-0.7.5/leaflet.css" />'
        if len(cluster_set):
            base += """
        <link rel="stylesheet" href="css/MarkerCluster.css" />
        <link rel="stylesheet" href="css/MarkerCluster.Default.css" />"""
        base += """
        <link rel="stylesheet" type="text/css" href="css/qgis2web.css">"""
        if len(labels):
            base += """
        <link rel="stylesheet" href="css/label.css" />"""
        if address:
            base += """
        <link rel="stylesheet" href="""
            base += 'http://k4r573n.github.io/leaflet-control-osm-geocoder/'
            base += 'Control.OSMGeocoder.css" />'
        if measure:
            base += """
        <link rel="stylesheet" href="css/leaflet.draw.css" />
        <link rel="stylesheet" href="css/leaflet.measurecontrol.css" />"""
        if mapLibLocation == "Local":
            base += """
        <script src="js/leaflet.js"></script>"""
        else:
            base += """
        <script src="http://cdn.leafletjs.com/leaflet-0.7.5/leaflet.js">"""
            base += '</script>'
        base += """
        <script src="js/leaflet-hash.js"></script>"""
        if len(labels):
            base += """
        <script src="js/label.js"></script>"""
        base += """
        <script src="js/Autolinker.min.js"></script>"""
        if address:
            base += """
        <script src="http://k4r573n.github.io/leaflet-control-osm-geocoder/"""
            base += 'Control.OSMGeocoder.js"></script>'
        if len(cluster_set):
            base += """
        <script src="js/leaflet.markercluster.js"></script>"""
        if measure:
            base += """
        <script src="js/leaflet.draw.js"></script>
        <script src="js/leaflet.measurecontrol.js"></script>"""
        if (matchCRS and
                canvas.mapRenderer().destinationCrs().authid() != 'EPSG:4326'):
            base += """
        <script src="js/proj4.js"></script>
        <script src="js/proj4leaflet.js"></script>"""
        if full == 1:
            base += """
        <meta name="viewport" content="initial-scale=1.0, """
            base += 'user-scalable=no" />'
        base += """
    </head>
    <body>
        <div id="map"></div>"""
        f_html.write(base)
        f_html.close()


def writeCSS(cssStore, full, height, width, backgroundColor):
    with open(cssStore + 'qgis2web.css', 'w') as f_css:
        text = """
body {
    padding: 0;
    margin: 0;
}"""
        if full == 1:
            text += """
html, body, #map {
    height: 100%;
    width: 100%;
    padding: 0;
    margin: 0;
    background-color: """ + backgroundColor + """
}"""
        else:
            text += """
html, body, #map {
    height: """ + str(height) + """px;
    width: """ + str(width) + """px;
    background-color: """ + backgroundColor + """;
}"""
        text += """
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
