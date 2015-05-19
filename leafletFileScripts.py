# -*- coding: utf-8 -*-

import os
import shutil

def writeFoldersAndFiles(pluginDir, outputProjectFileName, cluster_set, labels, matchCRS, canvas):
	#outputProjectFileName = os.path.join(os.getcwd(),outputProjectFileName)
	jsStore = os.path.join(outputProjectFileName, 'js')
	os.makedirs(jsStore)
	jsStore += os.sep
	jsDir = pluginDir + os.sep + 'js' + os.sep
	shutil.copyfile(jsDir + 'Autolinker.min.js', jsStore + 'Autolinker.min.js')
	shutil.copyfile(jsDir + 'leaflet-hash.js', jsStore + 'leaflet-hash.js')
	if len(cluster_set):
		shutil.copyfile(jsDir + 'leaflet.markercluster.js', jsStore + 'leaflet.markercluster.js')
	if len(labels):
		shutil.copyfile(jsDir + 'label.js', jsStore + 'label.js')
	if matchCRS == True and canvas.mapRenderer().destinationCrs().authid() != 'EPSG:4326':
		shutil.copyfile(jsDir + 'proj4.js', jsStore + 'proj4.js')
		shutil.copyfile(jsDir + 'proj4leaflet.js', jsStore + 'proj4leaflet.js')
	dataStore = os.path.join(outputProjectFileName, 'data')
	os.makedirs(dataStore)
	cssStore = os.path.join(outputProjectFileName, 'css')
	os.makedirs(cssStore)
	cssStore += os.sep
	cssDir = pluginDir + os.sep + 'css' + os.sep
	if len(cluster_set):
		shutil.copyfile(cssDir + 'MarkerCluster.css', cssStore + 'MarkerCluster.css')
		shutil.copyfile(cssDir + 'MarkerCluster.Default.css', cssStore + 'MarkerCluster.Default.css')
	if len(labels):
		shutil.copyfile(cssDir + 'label.css', cssStore + 'label.css')
	picturesStore = os.path.join(outputProjectFileName, 'pictures')
	os.makedirs(picturesStore)
	miscStore = os.path.join(outputProjectFileName, 'misc')
	os.makedirs(miscStore)
	return dataStore, cssStore

def writeHTMLstart(outputIndex, webpage_name, cluster_set, labels, address, matchCRS, canvas, full):
	with open(outputIndex, 'w') as f_html:
		base = """<!DOCTYPE html>
<html>
	<head>"""
		if webpage_name == "":
			base +="""
		<title>QGIS2leaf webmap</title>
	"""
		else:
			base +="""
		<title>""" + (webpage_name).encode('utf-8') + """</title>"""
		base += """
		<meta charset="utf-8" />
		<link rel="stylesheet" href="http://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.3/leaflet.css" />"""
		if len(cluster_set):
			base+= """
		<link rel="stylesheet" href="css/MarkerCluster.css" />
		<link rel="stylesheet" href="css/MarkerCluster.Default.css" />"""
		base+= """
		<link rel="stylesheet" type="text/css" href="css/qgis2web.css">"""
		if len(labels):
			base+= """
		<link rel="stylesheet" href="css/label.css" />"""
		if address == True:
			base += """
		<link rel="stylesheet" href="http://k4r573n.github.io/leaflet-control-osm-geocoder/Control.OSMGeocoder.css" />	"""
		base +="""
		<script src="http://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.3/leaflet.js"></script>
		<script src="js/leaflet-hash.js"></script>"""
		if len(labels):
			base += """
		<script src="js/label.js"></script>"""
		base += """
		<script src="js/Autolinker.min.js"></script>"""
		if address == True:
			base +="""
		<script src="http://k4r573n.github.io/leaflet-control-osm-geocoder/Control.OSMGeocoder.js"></script>"""
		if len(cluster_set):
			base +="""
		<script src="js/leaflet.markercluster.js"></script>"""
		if matchCRS == True and canvas.mapRenderer().destinationCrs().authid() != 'EPSG:4326':
			base += """
		<script src="js/proj4.js"></script>
		<script src="js/proj4leaflet.js"></script>"""
		if full == 1:
			base += """
		<meta name="viewport" content="initial-scale=1.0, user-scalable=no" />"""
		base += """
	</head>
	<body>
		<div id="map"></div>"""
#		if opacity_raster == True:
#			base += """
#		<input id="slide" type="range" min="0" max="1" step="0.1" value="1" onchange="updateOpacity(this.value)">"""
  		f_html.write(base)
		f_html.close()

def writeCSS(cssStore, full, height, width):
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
}"""
		else:
			text += """
html, body, #map {
	height: """+str(height)+"""px;
	width: """+str(width)+"""px;
}"""
#		if opacity_raster == True and full == 1:
#			text += """
#html, body, #slide {
#	width: 100%;
#	padding: 0;
#	margin: 0;
#}"""
#		elif opacity_raster == True:
#			text += """	
#html, body, #slide {
#	width: """+str(width)+"""px;
#	padding: 0;
#	margin: 0;
#}"""
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
	background: #fff;"""
		f_css.write(text)
		f_css.close()
