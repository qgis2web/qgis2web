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

from PyQt4.QtCore import QFileInfo
import osgeo.ogr, osgeo.osr #we will need some packages
from osgeo import ogr
from osgeo import gdal
import processing
import shutil
from qgis.core import *
import qgis.utils
import os #for file writing/folder actions
import shutil #for reverse removing directories
import urllib # to get files from the web
from urlparse import parse_qs
import time
import tempfile
import re
import fileinput
import webbrowser #to open the made map directly in your browser
import sys #to use another print command without annoying newline characters 
from basemaps import basemapLeaflet, basemapAttributions

basemapAddresses = basemapLeaflet()
basemapAttributions = basemapAttributions()

def layerstyle_single(layer):
	return color_code

def writeLeaflet(outputProjectFileName, width, height, full, layer_list, visible, opacity_raster, cluster_set, webpage_name, webmap_head, webmap_subhead, legend, locate, address, labels, labelhover, matchCRS, selected, json, params):
	# supply path to where is your qgis installed
	#QgsApplication.setPrefixPath("/path/to/qgis/installation", True)
	print "Output: " + outputProjectFileName
	pluginDir = os.path.dirname(os.path.realpath(__file__))
	
	cluster_num = 1
	# load providers
	QgsApplication.initQgis()
	# let's determine the current work folder of qgis:
	print os.getcwd()		
	print layer_list
	# let's create the overall folder structure:
	outputProjectFileName = os.path.join(outputProjectFileName, 'qgis2web_' + str(time.strftime("%Y_%m_%d-%H_%M_%S")))
	#outputProjectFileName = os.path.join(os.getcwd(),outputProjectFileName)
	jsStore = os.path.join(outputProjectFileName, 'js')
	os.makedirs(jsStore)
	jsStore += os.sep
	jsDir = pluginDir + os.sep + 'js' + os.sep
	shutil.copyfile(jsDir + 'Autolinker.min.js', jsStore + 'Autolinker.min.js')
	shutil.copyfile(jsDir + 'leaflet-hash.js', jsStore + 'leaflet-hash.js')
	if len(cluster_set):
		shutil.copyfile(jsDir + 'leaflet.markercluster.js', jsStore + 'leaflet.markercluster.js')
	if labels:
		shutil.copyfile(jsDir + 'label.js', jsStore + 'label.js')
	canvas = qgis.utils.iface.mapCanvas()
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
	if labels:
		shutil.copyfile(cssDir + 'label.css', cssStore + 'label.css')
	picturesStore = os.path.join(outputProjectFileName, 'pictures')
	os.makedirs(picturesStore)
	miscStore = os.path.join(outputProjectFileName, 'misc')
	os.makedirs(miscStore)
	
	minify = params["Data export"]["Minify GeoJSON files"]
	extent = params["Scale/Zoom"]["Extent"]
	minZoom = params["Scale/Zoom"]["Min zoom level"]
	maxZoom = params["Scale/Zoom"]["Max zoom level"]
	basemapName = params["Appearance"]["Base layer"]
	
	removeSpaces = lambda txt:'"'.join( it if i%2 else ''.join(it.split())
						for i,it in enumerate(txt.split('"')))
	
	#lets create a css file for own css:
	with open(cssStore + 'own_style.css', 'w') as f_css:
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
		if opacity_raster == True and full == 1:
			text += """
html, body, #slide {
	width: 100%;
	padding: 0;
	margin: 0;
}"""
		elif opacity_raster == True:
			text += """	
html, body, #slide {
	width: """+str(width)+"""px;
	padding: 0;
	margin: 0;
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
	background: #fff;"""
		f_css.write(text)
		f_css.close()
	
	#the index file has an easy beginning. we will store it right away:
	outputIndex = outputProjectFileName + os.sep + 'index.html'
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
		<link rel="stylesheet" type="text/css" href="css/own_style.css">"""
		if labels:
			base+= """
		<link rel="stylesheet" href="css/label.css" />"""
		if address == True:
			base += """
		<link rel="stylesheet" href="http://k4r573n.github.io/leaflet-control-osm-geocoder/Control.OSMGeocoder.css" />	"""
		base +="""
		<script src="http://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.3/leaflet.js"></script>
		<script src="js/leaflet-hash.js"></script>"""
		if labels:
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
		if opacity_raster == True:
			base += """
		<input id="slide" type="range" min="0" max="1" step="0.1" value="1" onchange="updateOpacity(this.value)">"""
  		f_html.write(base)
		f_html.close()
	# let's create the js files in the data folder of input vector files:

	wfsLayers = ""
	allLayers = canvas.layers()
	exp_crs = QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId)
	for count, i in enumerate(layer_list):
		rawLayerName = i.name()
		safeLayerName = re.sub('[\W_]+', '', rawLayerName)
		layerFileName = dataStore + os.sep + 'exp_' + safeLayerName + '.js'
		if i.providerType() != 'WFS' or json[count] == True and i:
			print "JSON (" + i.providerType() + "): " + rawLayerName
			precision = params["Data export"]["Precision"]
			if i.type() ==0:
				qgis.core.QgsVectorFileWriter.writeAsVectorFormat(i,layerFileName, 'utf-8', exp_crs, 'GeoJson', selected, layerOptions=["COORDINATE_PRECISION="+str(precision)])

				#now change the data structure to work with leaflet:
				with open(layerFileName) as f:
					lines = f.readlines()
				with open(layerFileName, "w") as f2:
					f2.write("var exp_" + str(safeLayerName) + "=") # write the new line before
					for line in lines:
						if minify:
							line = line.strip("\n\t ")
							line = removeSpaces(line)
						f2.write(line)
					f2.close
					
				#now add the js files as data input for our map
				with open(outputIndex, 'a') as f3:
					new_src = """
<script src=\"""" + 'data' + """/exp_""" + safeLayerName + """.js\"></script>"""
					# store everything in the file
					f3.write(new_src)
					f3.close()

			#here comes the raster layers. you need an installed version of gdal
			elif i.type() == 1:
				if i.dataProvider().name() != "wms":
					in_raster = str(i.dataProvider().dataSourceUri())
					prov_raster = tempfile.gettempdir() + os.sep + 'exp_' + safeLayerName + '_prov.tif'
					out_raster = dataStore + os.sep + 'exp_' + safeLayerName + '.png'
					crsSrc = i.crs()
					crsDest = QgsCoordinateReferenceSystem(4326)
					xform = QgsCoordinateTransform(crsSrc, crsDest)
					extentRep = xform.transform(i.extent())
					extentRepNew = ','.join([str(extentRep.xMinimum()), str(extentRep.xMaximum()),str(extentRep.yMinimum()), str(extentRep.yMaximum())])
					processing.runalg("gdalogr:warpreproject",in_raster,i.crs().authid(),"EPSG:4326","",0,1,0,-1,75,6,1,False,0,False,"",prov_raster)
					print extentRepNew
					processing.runalg("gdalogr:translate",prov_raster,100,True,"",0,"",extentRepNew,False,0,0,75,6,1,False,0,False,"",out_raster)
		else:
			print "Not JSON (" + i.providerType() + "): " + rawLayerName
	#now determine the canvas bounding box
	#####now with viewcontrol
	if extent == "Canvas extent":
		pt0	= canvas.extent()
		try:
			crsSrc = canvas.mapSettings().destinationCrs() # WGS 84
		except:
			crsSrc = canvas.mapRenderer().destinationCrs() # WGS 84
		crsAuthId = crsSrc.authid()
		crsProj4 = crsSrc.toProj4()
		crsDest = QgsCoordinateReferenceSystem(4326)  # WGS 84 / UTM zone 33N
		xform = QgsCoordinateTransform(crsSrc, crsDest)
		pt1 = xform.transform(pt0)
		bbox_canvas = [pt1.yMinimum(), pt1.yMaximum(),pt1.xMinimum(), pt1.xMaximum()]
		bounds = '[[' + str(pt1.yMinimum()) + ',' + str(pt1.xMinimum()) + '],[' + str(pt1.yMaximum()) + ',' + str(pt1.xMaximum()) +']]'
		middle = """
		<script>"""
		#print '>> ' + crsProj4
		if matchCRS == True and crsAuthId != 'EPSG:4326':
			print '>> ' + crsProj4
			middle += """
		var crs = new L.Proj.CRS('""" + crsAuthId + """', '""" + crsProj4 + """', {
			resolutions: [2800, 1400, 700, 350, 175, 84, 42, 21, 11.2, 5.6, 2.8, 1.4, 0.7, 0.35, 0.14, 0.07],
		});"""
		middle += """
		var map = L.map('map', {"""
		if matchCRS == True and crsAuthId != 'EPSG:4326':
			middle += """
			crs: crs,
			continuousWorld: false,
			worldCopyJump: false, """
		middle += """
			zoomControl:true, maxZoom:""" + unicode(maxZoom) + """, minZoom:""" + unicode(minZoom) + """
		}).fitBounds(""" + bounds + """);
		var hash = new L.Hash(map);
		var additional_attrib = '<a href="https://github.com/tomchadwin/qgis2web" target ="_blank">qgis2web</a>';"""
	if extent == 'Fit to layers extent':
		middle = """
		<script>
"""
		if matchCRS == True and crsAuthId != 'EPSG:4326':
			print '>> ' + crsProj4
			middle += """
		var crs = new L.Proj.CRS('""" + crsAuthId + """', '""" + crsProj4 + """', {
			resolutions: [2800, 1400, 700, 350, 175, 84, 42, 21, 11.2, 5.6, 2.8, 1.4, 0.7, 0.35, 0.14, 0.07],
		});"""
		middle += """
		var map = L.map('map', { zoomControl:true, maxZoom:19 });
		var hash = new L.Hash(map); //add hashes to html address to easy share locations
		var additional_attrib = '<a href="https://github.com/tomchadwin/qgis2web" target ="_blank">qgis2web</a>';"""
	# we will start with the clustergroup
	middle += """
		var feature_group = new L.featureGroup([]);
		var raster_group = new L.LayerGroup([]);"""
#here come the basemap (variants list thankfully provided by: "https://github.com/leaflet-extras/leaflet-providers") our geojsons will  looped after that
#basemap name	
	if basemapName == 0 or basemapName == "" or matchCRS == True:
		basemapText = ""
	else:
		basemapText = """
		var basemap = L.tileLayer('""" + basemapAddresses[basemapName] + """', { 
			attribution: additional_attrib + ' """ + basemapAttributions[basemapName] + """'
		});"""
		basemapText += """	
		basemap.addTo(map);"""
	layerOrder = """	
		var layerOrder=new Array();
		function restackLayers() {
			for (index = 0; index < layerOrder.length; index++) {
				feature_group.removeLayer(layerOrder[index]);
				feature_group.addLayer(layerOrder[index]);
			}
		}

		layerControl = L.control.layers({},{},{collapsed:false});"""
	with open(outputIndex, 'a') as f4:
			f4.write(middle)
			f4.write(basemapText)
			f4.write(layerOrder)
			f4.close()
	for count, i in enumerate(reversed(allLayers)):
		rawLayerName = i.name()
		safeLayerName = re.sub('[\W_]+', '', rawLayerName)
		if i.type()==0:
			with open(outputIndex, 'a') as f5:
				#here comes the layer style
				#here comes the html popup content
				fields = i.pendingFields() 
				field_names = [field.name() for field in fields]
				html_prov = False
				icon_prov = False
				label_exp = ''
				#lets extract possible labels form the qgis map for each layer. 
				labeltext = ""
				f = ''
				if labels == True and labelhover == False:
					palyr = QgsPalLayerSettings()
					palyr.readFromLayer(i)
					f = palyr.fieldName
					label_exp = False
					if labelhover == False:
						labeltext = """.bindLabel(feature.properties."""+str(f)+""", {noHide: true})"""
					else:
						labeltext = """.bindLabel(feature.properties."""+str(f)+""")"""
				for field in field_names:
					if str(field) == 'html_exp':
						html_prov = True
						table = 'feature.properties.html_exp'
					if str(field) == 'label_exp' and labelhover == False:
						label_exp = True
						labeltext = """.bindLabel(feature.properties.label_exp, {noHide: true})"""
					if str(field) == 'label_exp' and labelhover == True:
						label_exp = True
						labeltext = """.bindLabel(feature.properties.label_exp)"""
					# we will use labels in leaflet only if a fieldname is equal to the label defining field:
					if str(f) != "" and str(f) == str(field) and f:
						label_exp = True
					if str(field) == 'icon_exp':
						icon_prov = True #we need this later on for icon creation
					if html_prov != True:
						tablestart = """'<table>"""
						row = ""
						for field in field_names:
							if str(field) == "icon_exp":
								row += ""
							else:
								if i.editorWidgetV2(fields.indexFromName(field)) != QgsVectorLayer.Hidden and i.editorWidgetV2(fields.indexFromName(field)) != 'Hidden':
									row += """<tr><th scope="row">""" + i.attributeDisplayName(fields.indexFromName(str(field))) + """</th><td>' + Autolinker.link(String(feature.properties['""" + str(field) + """'])) + '</td></tr>"""
						tableend = """</table>'"""
						table = tablestart + row + tableend
				if label_exp == False:
					labeltext = ""
				popFuncs = """					
	var popupContent = """ + table + """;
	layer.bindPopup(popupContent);"""
				new_pop = """
function pop_""" + safeLayerName + """(feature, layer) {"""+popFuncs+"""
}"""
				#single marker points:
				 
				layerName = safeLayerName
				renderer = i.rendererV2()
				rendererDump = renderer.dump()
				layer_transp_float = 1 - (float(i.layerTransparency()) / 100)
				print "Cluster: " + unicode(cluster_set[count])

				if rendererDump[0:6] == 'SINGLE':
					symbol = renderer.symbol()
					colorName = symbol.color().name()
					symbol_transp_float = symbol.alpha()
					opacity_str = str(layer_transp_float*symbol_transp_float)
					if i.geometryType() == 0 and icon_prov != True:
						radius_str = str(symbol.size() * 2)
						borderColor_str = str(symbol.symbolLayer(0).borderColor().name())
						pointToLayer_str = """
		pointToLayer: function (feature, latlng) {  
			return L.circleMarker(latlng, {
				radius: """+radius_str+""",
				fillColor: '"""+colorName+"""',
				color: '"""+borderColor_str+"""',
				weight: 1,
				opacity: """+opacity_str+""",
				fillOpacity: """+opacity_str+"""
			})"""+labeltext
						if i.providerType() == 'WFS' and json[count] == False:
							stylestr = pointToLayer_str + """
		},
		onEachFeature: function (feature, layer) {""" + popFuncs + """
		}"""
							new_obj, scriptTag, cluster_num = buildPointWFS(layerName, i.source(), "", stylestr, cluster_set[count], cluster_num, visible)
							wfsLayers += """
<script src='""" + scriptTag + """'></script>"""
						else:
							new_obj = """
	var exp_""" + safeLayerName + """JSON = new L.geoJson(exp_""" + safeLayerName + """,{
		onEachFeature: pop_""" + safeLayerName + "," + pointToLayer_str + """
		}
	});
	layerOrder[layerOrder.length] = exp_"""+safeLayerName+"""JSON;"""
#add points to the cluster group
							if cluster_set[count]:
								new_obj += """
		var cluster_group"""+ safeLayerName + """JSON= new L.MarkerClusterGroup({showCoverageOnHover: false});"""				
								new_obj += """
		cluster_group"""+ safeLayerName + """JSON.addLayer(exp_""" + safeLayerName + """JSON);"""			
								cluster_num += 1	

					elif i.geometryType() == 1:
						radius_str = str(symbol.width() * 5)
						penStyle_str = getLineStyle(symbol.symbolLayer(0).penStyle())
						lineStyle_str = """
			return {
				weight: """+radius_str+""",
				color: '"""+colorName+"""',
				dashArray: '"""+penStyle_str+"""',
				opacity: """+opacity_str+""",
				fillOpacity: """+opacity_str+"""
			};"""
						if i.providerType() == 'WFS' and json[count] == False:
							stylestr="""
		style: function (feature) {""" + lineStyle_str + """
		},
		onEachFeature: function (feature, layer) {"""+popFuncs+"""
		}"""
							new_obj, scriptTag = buildNonPointWFS(layerName, i.source(), "", stylestr, popFuncs, visible)
							wfsLayers += """
<script src='""" + scriptTag + """'></script>"""
						else:
							new_obj = """
	function doStyle""" + safeLayerName + """(feature) {""" + lineStyle_str + """
	}"""
							new_obj += buildNonPointJSON("", safeLayerName)
							new_obj += restackLayers(layerName, visible)		
					elif i.geometryType() == 2:
						if symbol.symbolLayer(0).layerType() == 'SimpleLine':
							colorName = 'none'
							borderColor_str = str(symbol.color().name())
							radius_str = str(symbol.symbolLayer(0).width() * 5)
						else:
							borderColor_str = str(symbol.symbolLayer(0).borderColor().name())
							borderStyle_str = getLineStyle(symbol.symbolLayer(0).borderStyle())
							radius_str = str(symbol.symbolLayer(0).borderWidth() * 5)
						if symbol.symbolLayer(0).brushStyle() == 0:
							borderStyle_str = "0"
						polyStyle_str = """
			return {
				color: '"""+borderColor_str+"""',
				fillColor: '"""+colorName+"""',
				weight: """+radius_str+""",
				dashArray: '"""+borderStyle_str+"""',
				opacity: """+opacity_str+""",
				fillOpacity: """+opacity_str+"""
			};
"""
						if i.providerType() == 'WFS' and json[count] == False:
							stylestr="""
		style: function (feature) {""" + polyStyle_str + """
		},
		onEachFeature: function (feature, layer){"""+popFuncs+"""
		}"""
							new_obj, scriptTag = buildNonPointWFS(layerName, i.source(), "", stylestr, popFuncs, visible)
							wfsLayers += """
<script src='""" + scriptTag + """'></script>"""
						else:
							new_obj = """
	function doStyle""" + safeLayerName + """(feature) {""" + polyStyle_str + """
	}"""
							new_obj += buildNonPointJSON("", safeLayerName)
							new_obj += restackLayers(layerName, visible)	
				elif rendererDump[0:11] == 'CATEGORIZED':
					if i.geometryType() == 0 and icon_prov != True:
						categories = renderer.categories()
						valueAttr = renderer.classAttribute()
						categoryStr = """
	function doStyle""" + layerName + """(feature) {
		switch (feature.properties.""" + valueAttr + """) {"""
						for cat in categories:
							if not cat.value():
								categoryStr += """
			default:
				return {"""
							else:
								if isinstance(cat.value(), basestring):
									categoryStr += """
			case '""" + unicode(cat.value()) + """':
				return {"""
								else:
									categoryStr += """
			case """ + unicode(cat.value()) + """:
				return {"""
							symbol = cat.symbol()
							symbol_transp_float = symbol.alpha()
							opacity_str = str(layer_transp_float*symbol_transp_float)
							print str(layer_transp_float) + " x " + str(symbol_transp_float) + " = " + opacity_str
							categoryStr += """
					radius: '""" + unicode(symbol.size() * 2) + """',
					fillColor: '""" + unicode(symbol.color().name()) + """',
					color: '""" + unicode(symbol.symbolLayer(0).borderColor().name())+ """',
					weight: 1,
					fillOpacity: '""" + opacity_str + """',
				};
				break;"""
						categoryStr += """
		}
	}"""
						if i.providerType() == 'WFS' and json[count] == False:
							stylestr="""
		pointToLayer: function (feature, latlng) {  
			return L.circleMarker(latlng, doStyle""" + layerName + """(feature))"""+labeltext+"""
		},
		onEachFeature: function (feature, layer) {"""+popFuncs+"""
		}"""
							new_obj, scriptTag, cluster_num = buildPointWFS(layerName, i.source(), categoryStr, stylestr, cluster_set[count], cluster_num, visible)
							wfsLayers += """
<script src='""" + scriptTag + """'></script>"""
						else:
							new_obj = categoryStr + """
	var exp_""" + safeLayerName + """JSON = new L.geoJson(exp_""" + safeLayerName + """,{
		onEachFeature: pop_""" + safeLayerName + """,
		pointToLayer: function (feature, latlng) {  
			return L.circleMarker(latlng, doStyle""" + layerName + """(feature))"""+labeltext+"""
		}
	});
		layerOrder[layerOrder.length] = exp_"""+safeLayerName+"""JSON;"""
			#add points to the cluster group
							if cluster_set[count] == True:
								
								new_obj += """
		var cluster_group"""+ safeLayerName + """JSON= new L.MarkerClusterGroup({showCoverageOnHover: false});
		cluster_group"""+ safeLayerName + """JSON.addLayer(exp_""" + safeLayerName + """JSON);"""			
							cluster_num += 1	
					elif i.geometryType() == 1:
						categories = renderer.categories()
						valueAttr = renderer.classAttribute()
						categoryStr = """
	function doStyle""" + layerName + """(feature) {"""
						categoryStr += """
		switch (feature.properties.""" + valueAttr + ") {"
						for cat in categories:
							if not cat.value():
								categoryStr += """
			default:
				return {"""
							else:
								if isinstance(cat.value(), basestring):
									categoryStr += """
			case '""" + unicode(cat.value()) + """':
				return {"""
								else:
									categoryStr += """
			case """ + unicode(cat.value()) + """:
				return {"""
							#categoryStr += "radius: '" + unicode(cat.symbol().size() * 2) + "',"
							symbol = cat.symbol()
							symbol_transp_float = symbol.alpha()
							opacity_str = str(layer_transp_float*symbol_transp_float)
							print str(layer_transp_float) + " x " + str(symbol_transp_float) + " = " + opacity_str
							categoryStr += """
					color: '""" + unicode(symbol.color().name()) + """',
					weight: '""" + unicode(symbol.width() * 5) + """',
					dashArray: '""" + getLineStyle(symbol.symbolLayer(0).penStyle()) + """',
					opacity: '""" + opacity_str + """',
				};
				break;"""
						categoryStr += """
		}
	}"""
						stylestr="""
		style:doStyle""" + layerName + """,
		onEachFeature: function (feature, layer) {"""+popFuncs+"""
		}"""
						if i.providerType() == 'WFS' and json[count] == False:
							new_obj, scriptTag = buildNonPointWFS(layerName, i.source(), categoryStr, stylestr, popFuncs, visible)
							wfsLayers += """
<script src='""" + scriptTag + """'></script>"""
						else:
							new_obj = buildNonPointJSON(categoryStr, safeLayerName)
					elif i.geometryType() == 2:
						categories = renderer.categories()
						valueAttr = renderer.classAttribute()
						categoryStr = """
	function doStyle""" + layerName + "(feature) {"
						categoryStr += """
		switch (feature.properties.""" + valueAttr + ") {"
						for cat in categories:
							if not cat.value():
								categoryStr += """
			default:
				return {"""
							else:
								if isinstance(cat.value(), basestring):
									categoryStr += """
			case '""" + unicode(cat.value()) + """':
				return {"""
								else:
									categoryStr += """
			case """ + unicode(cat.value()) + """:
				return {"""
							symbol = cat.symbol()
							symbol_transp_float = symbol.alpha()
							opacity_str = str(layer_transp_float*symbol_transp_float)
							print str(layer_transp_float) + " x " + str(symbol_transp_float) + " = " + opacity_str
							categoryStr += """
					weight: '""" + unicode(symbol.symbolLayer(0).borderWidth() * 5) + """',
					fillColor: '""" + unicode(symbol.color().name()) + """',
					color: '""" + unicode(symbol.symbolLayer(0).borderColor().name()) + """',
					weight: '1',
					dashArray: '""" + getLineStyle(symbol.symbolLayer(0).borderStyle()) + """',
					opacity: '""" + opacity_str + """',
					fillOpacity: '""" + opacity_str + """',
				};
				break;"""
						categoryStr += """
		}
	}"""
						if i.providerType() == 'WFS' and json[count] == False:
							stylestr="""
		style:doStyle""" + layerName + """,
		onEachFeature : function (feature, layer) {"""+popFuncs+"""
		}"""
							new_obj, scriptTag = buildNonPointWFS(layerName, i.source(), categoryStr, stylestr, popFuncs, visible)
							wfsLayers += """
<script src='""" + scriptTag + """'></script>"""
						else:
							new_obj = buildNonPointJSON(categoryStr, safeLayerName)
				elif rendererDump[0:9] == 'GRADUATED':
					if i.geometryType() == 0 and icon_prov != True:
						valueAttr = renderer.classAttribute()
						categoryStr = """
	function doStyle""" + layerName + "(feature) {"
						for r in renderer.ranges():
							symbol = r.symbol()
							symbol_transp_float = symbol.alpha()
							opacity_str = str(layer_transp_float*symbol_transp_float)
							print str(layer_transp_float) + " x " + str(symbol_transp_float) + " = " + opacity_str
							categoryStr += """
		if (feature.properties.""" + valueAttr + " >= " + unicode(r.lowerValue()) + " && feature.properties." + valueAttr + " <= " + unicode(r.upperValue()) + """) {
			return {
				radius: '""" + unicode(symbol.size() * 2) + """',
				fillColor: '""" + unicode(symbol.color().name()) + """',
				color: '""" + unicode(symbol.symbolLayer(0).borderColor().name())+ """',
				weight: 1,
				fillOpacity: '""" + opacity_str + """',
			}
		}"""
						categoryStr += """
	}"""
						if i.providerType() == 'WFS' and json[count] == False:
							stylestr="""
		pointToLayer: function (feature, latlng) {  
			return L.circleMarker(latlng, doStyle""" + layerName + """(feature))"""+labeltext+"""
		},
		onEachFeature: function (feature, layer) {"""+popFuncs+"""
		}"""
							new_obj, scriptTag, cluster_num = buildPointWFS(layerName, i.source(), categoryStr, stylestr, cluster_set[count], cluster_num, visible)
							wfsLayers += """
<script src='""" + scriptTag + """'></script>"""
						else:
							new_obj = categoryStr + """
	var exp_""" + safeLayerName + """JSON = new L.geoJson(exp_""" + safeLayerName + """,{
		onEachFeature: pop_""" + safeLayerName + """,
		pointToLayer: function (feature, latlng) {  
			return L.circleMarker(latlng, doStyle""" + safeLayerName + """(feature))"""+labeltext+"""
		}
	});
		layerOrder[layerOrder.length] = exp_"""+safeLayerName+"""JSON;"""
							#add points to the cluster group
							if cluster_set[count] == True:
								new_obj += """
		var cluster_group"""+ safeLayerName + """JSON= new L.MarkerClusterGroup({showCoverageOnHover: false});				
		cluster_group"""+ safeLayerName + """JSON.addLayer(exp_""" + safeLayerName + """JSON);"""			
								cluster_num += 1	
					elif i.geometryType() == 1:
						valueAttr = renderer.classAttribute()
						categoryStr = """
	function doStyle""" + layerName + "(feature) {"
						for r in renderer.ranges():
							symbol = r.symbol()
							symbol_transp_float = symbol.alpha()
							opacity_str = str(layer_transp_float*symbol_transp_float)
							print str(layer_transp_float) + " x " + str(symbol_transp_float) + " = " + opacity_str
							categoryStr += """
		if (feature.properties.""" + valueAttr + " >= " + unicode(r.lowerValue()) + " && feature.properties." + valueAttr + " <= " + unicode(r.upperValue()) + """) {
			return {"""
							categoryStr += """
				color: '""" + unicode(symbol.symbolLayer(0).color().name())+ """',
				weight: '""" + unicode(symbol.width() * 5) + """',
				opacity: '""" + opacity_str + """',
			}
		}"""
						categoryStr += """
	}"""
						if i.providerType() == 'WFS' and json[count] == False:
							stylestr="""
		style:doStyle""" + layerName + """,
		onEachFeature: function (feature, layer) {"""+popFuncs+"""
		}"""
							new_obj, scriptTag = buildNonPointWFS(layerName, i.source(), categoryStr, stylestr, popFuncs, visible)
							wfsLayers += """
<script src='""" + scriptTag + """'></script>"""
						else:
							new_obj = buildNonPointJSON(categoryStr, safeLayerName)
					elif i.geometryType() == 2:
						valueAttr = renderer.classAttribute()
						categoryStr = """
	function doStyle""" + layerName + "(feature) {"
						for r in renderer.ranges():
							symbol = r.symbol()
							symbol_transp_float = symbol.alpha()
							opacity_str = str(layer_transp_float*symbol_transp_float)
							print str(layer_transp_float) + " x " + str(symbol_transp_float) + " = " + opacity_str
							categoryStr += """
		if (feature.properties.""" + valueAttr + " >= " + unicode(r.lowerValue()) + " && feature.properties." + valueAttr + " <= " + unicode(r.upperValue()) + """) {
			return {
				color: '""" + unicode(symbol.symbolLayer(0).borderColor().name())+ """',
				weight: '""" + unicode(symbol.symbolLayer(0).borderWidth() * 5) + """',
				fillColor: '""" + unicode(symbol.color().name())+ """',
				opacity: '""" + opacity_str + """',
				fillOpacity: '""" + opacity_str + """',
			}
		}"""
						categoryStr += """
	}"""
						if i.providerType() == 'WFS' and json[count] == False:
							stylestr="""
		style: doStyle""" + layerName + """,
		onEachFeature: function (feature, layer) {"""+popFuncs+"""
		}"""
							new_obj, scriptTag = buildNonPointWFS(layerName, i.source(), categoryStr, stylestr, popFuncs, visible)
							wfsLayers += """
<script src='""" + scriptTag + """'></script>"""
						else:
							new_obj = buildNonPointJSON(categoryStr, safeLayerName)
#						elif rendererDump[0:10] == 'Rule-based':
#							for rule in renderer.rootRule().children():
#								try:
#									print rule.filterExpression() + ": " + rule.filter().functionCount()
#								except:
#									print 11111
#							print renderer.rootRule().filterExpression()
#							categoryStr = """
#		function doStyle""" + layerName + "(feature) {"
#							for r in renderer.rootRule().children():
#								symbol = r.symbol()
#								filterExpression = r.filterExpression()
#								filterExpression = re.sub('=', '==', filterExpression)
#								categoryStr += """
#			if (""" + filterExpression + """) {
#				return {
#					radius: '""" + unicode(symbol.size() * 2) + """',
#					fillColor: '""" + unicode(symbol.color().name()) + """',
#					color: '""" + unicode(symbol.symbolLayer(0).borderColor().name())+ """',
#					weight: 1,
#					fillOpacity: '""" + str(symbol.alpha()) + """',
#				}
#			}"""
#							categoryStr += """
#		}"""
#							if i.providerType() == 'WFS' and json[count] == False:
#								stylestr="""
#			pointToLayer: function (feature, latlng) {  
#				return L.circleMarker(latlng, doStyle""" + layerName + """(feature))"""+labeltext+"""
#			},
#			onEachFeature: function (feature, layer) {"""+popFuncs+"""
#			}"""
#								new_obj, scriptTag, cluster_num = buildPointWFS(layerName, i.source(), categoryStr, stylestr, cluster_set[count], cluster_num, visible)
#								wfsLayers += """
#	<script src='""" + scriptTag + """'></script>"""
#							else:
#								new_obj = categoryStr + """
#		var exp_""" + safeLayerName + """JSON = new L.geoJson(exp_""" + safeLayerName + """,{
#			onEachFeature: pop_""" + safeLayerName + """,
#			pointToLayer: function (feature, latlng) {  
#				return L.circleMarker(latlng, doStyle""" + safeLayerName + """(feature))"""+labeltext+"""
#			}
#		});"""
#								#add points to the cluster group
	#							if cluster_set[count] == True:
	#								new_obj += """
	#		var cluster_group"""+ safeLayerName + """JSON= new L.MarkerClusterGroup({showCoverageOnHover: false});				
	#		cluster_group"""+ safeLayerName + """JSON.addLayer(exp_""" + safeLayerName + """JSON);"""			
	#								cluster_num += 1	

				elif icon_prov == True and i.geometryType() == 0:
					new_obj = """
var exp_""" + safeLayerName + """JSON = new L.geoJson(exp_""" + safeLayerName + """,{
	onEachFeature: pop_""" + safeLayerName + """,
	pointToLayer: function (feature, latlng) {
		return L.marker(latlng, {
			icon: L.icon({
				iconUrl: feature.properties.icon_exp,
				iconSize:     [24, 24], // size of the icon change this to scale your icon (first coordinate is x, second y from the upper left corner of the icon)
				iconAnchor:   [12, 12], // point of the icon which will correspond to marker's location (first coordinate is x, second y from the upper left corner of the icon)
				popupAnchor:  [0, -14] // point from which the popup should open relative to the iconAnchor (first coordinate is x, second y from the upper left corner of the icon)
			})
		})"""+labeltext+"""
	}}
);"""
		#add points to the cluster group
					if cluster_set[count] == True:
						new_obj += """
var cluster_group"""+ safeLayerName + """JSON= new L.MarkerClusterGroup({showCoverageOnHover: false});
cluster_group"""+ safeLayerName + """JSON.addLayer(exp_""" + safeLayerName + """JSON);"""			
						cluster_num += 1
				else:
					new_obj = """
var exp_""" + safeLayerName + """JSON = new L.geoJson(exp_""" + safeLayerName + """,{
	onEachFeature: pop_""" + safeLayerName + """,
});"""		
		
				# store everything in the file
				if i.providerType() != 'WFS' or json[count] == True:
					f5.write(new_pop)
				f5.write("""
""" + new_obj)
				if visible == 'show all':
					if cluster_set[count] == False:
						if i.geometryType() == 0:
							f5.write("""
//add comment sign to hide this layer on the map in the initial view.
feature_group.addLayer(exp_"""+ safeLayerName + """JSON);""")
						else:
							f5.write("""
//add comment sign to hide this layer on the map in the initial view.
feature_group.addLayer(exp_""" + safeLayerName + """JSON);""")
					else:
						f5.write("""
//add comment sign to hide this layer on the map in the initial view.
cluster_group""" + safeLayerName + """JSON.addTo(map);""")
				if visible == 'show none':
					if cluster_set[count] == False:
						if i.geometryType() == 0:
							f5.write("""
	//delete comment sign to show this layer on the map in the initial view.
	//feature_group.addLayer(exp_"""+ safeLayerName + """JSON);""")
						if i.geometryType() != 0:
							f5.write("""
	//delete comment sign to show this layer on the map in the initial view.
	//feature_group.addLayer(exp_""" + safeLayerName + """JSON);""")
					else:
						f5.write("""
	//delete comment sign to show this layer on the map in the initial view.
	//cluster_group""" + safeLayerName + """JSON.addTo(map);""")
				f5.close()
		elif i.type() == 1:
			if i.dataProvider().name() == "wms":
				d = parse_qs(i.source())
				wms_url = d['url'][0]
				wms_layer = d['layers'][0]
				wms_format = d['format'][0]
				wms_crs = d['crs'][0]
				
				new_obj = """
var overlay_""" + safeLayerName + """ = L.tileLayer.wms('""" + wms_url + """', {
	layers: '""" + wms_layer + """',
	format: '""" + wms_format + """',
	transparent: true,
	continuousWorld : true,
}).addTo(map);"""
				
				print d
				#print i.source()
			else:
				out_raster_name = 'data/' + 'exp_' + safeLayerName + '.png'
				pt2	= i.extent()
				crsSrc = i.crs()    # WGS 84
				crsDest = QgsCoordinateReferenceSystem(4326)  # WGS 84 / UTM zone 33N
				xform = QgsCoordinateTransform(crsSrc, crsDest)
				pt3 = xform.transform(pt2)
				bbox_canvas2 = [pt3.yMinimum(), pt3.yMaximum(),pt3.xMinimum(), pt3.xMaximum()]
				bounds2 = '[[' + str(pt3.yMinimum()) + ',' + str(pt3.xMinimum()) + '],[' + str(pt3.yMaximum()) + ',' + str(pt3.xMaximum()) +']]'
				new_obj = """
var img_""" + safeLayerName + """= '""" + out_raster_name + """';
var img_bounds_""" + safeLayerName + """ = """+ bounds2 + """;
var overlay_""" + safeLayerName + """ = new L.imageOverlay(img_""" + safeLayerName + """, img_bounds_""" + safeLayerName + """).addTo(map);
raster_group.addLayer(overlay_""" + safeLayerName + """);"""
				
			with open(outputIndex, 'a') as f5_raster:
					

				f5_raster.write(new_obj)
				f5_raster.close()
	
	with open(outputIndex, 'a') as f5fgroup:
		f5fgroup.write("""

		feature_group.addTo(map);""")
		f5fgroup.close()

	#let's add a Title and a subtitle
	if webmap_head != "": 
		titleStart ="""
		var title = new L.Control();
		title.onAdd = function (map) {
			this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
			this.update();
			return this._div;
		};
		title.update = function () {
			this._div.innerHTML = '<h2>""" + webmap_head.encode('utf-8') + """</h2>""" + webmap_subhead.encode('utf-8') + """'
		};
		title.addTo(map);"""
		with open(outputIndex, 'a') as f5contr:
			f5contr.write(titleStart)
			f5contr.close()
			#here comes the address search:
	if address == True:
		address_text = """
		var osmGeocoder = new L.Control.OSMGeocoder({
            collapsed: false,
            position: 'topright',
            text: 'Find!',
		});
		osmGeocoder.addTo(map);"""
		with open(outputIndex, 'a') as f5addr:
			f5addr.write(address_text)
			f5addr.close()


	#let's add a legend
	if legend == True:
		legendStart = """
		var legend = L.control({position: 'bottomright'});
		legend.onAdd = function (map) {
			var div = L.DomUtil.create('div', 'info legend');
			div.innerHTML = "<h3>Legend</h3><table>"""
		for i in reversed(allLayers):
			rawLayerName = i.name()
			safeLayerName = re.sub('[\W_]+', '', rawLayerName)
			if i.type() == 0:
				fields = i.pendingFields() 
				field_names = [field.name() for field in fields]
				legend_ico_prov = False
				legend_exp_prov = False
				for field in field_names:
					if str(field) == 'legend_ico':
						legend_ico_prov = True
					if str(field) == 'legend_exp':
						legend_exp_prov = True
				if legend_ico_prov == True and legend_exp_prov == True:
					iter = i.getFeatures()
					for feat in iter:
						fid = feat.id()
						provider = i.dataProvider()
						legend_ico_index = provider.fieldNameIndex('legend_ico')
						legend_exp_index = provider.fieldNameIndex('legend_exp')
						attribute_map = feat.attributes()
						legend_icon = attribute_map[legend_ico_index]
						legend_expression = attribute_map[legend_exp_index]
						print legend_expression
						print legend_icon 
						break
					legendStart += """<tr><td><img src='""" + unicode(legend_icon) + """'></img></td><td>"""+unicode(legend_expression) + """</td></tr>"""

		legendStart += """</table>";
    		return div;
		};
		legend.addTo(map);"""
		with open(outputIndex, 'a') as f5leg:
			f5leg.write(legendStart)
			f5leg.close()

	# let's add layer control
	print len(basemapName)
	if len(basemapName) == 0 or matchCRS == True:
		controlStart = """"""
	if len(basemapName) == 1:
		controlStart = """
	var baseMaps = {
		'""" + str(basemapName[0]) + """': basemap_0
	};"""
	if len(basemapName) > 1:
		controlStart = """
	var baseMaps = {"""
		for l in range(0,len(basemapName)):
			if l < len(basemapName)-1:
				controlStart+= """
		'""" + str(basemapName[l]) + """': basemap_""" + str(l) + ""","""
			if l == len(basemapName)-1:
				controlStart+= """
		'""" + str(basemapName[l]) + """': basemap_""" + str(l) + """};"""
    #if len
	#control_basemap = """
	#var baseMaps = {"""
	#for l in range(0,len(basemapName)):
	if len(basemapName) == 0:
		controlStart += """
		L.control.layers({},{"""
	else:
		controlStart += """
		L.control.layers(baseMaps,{"""
	with open(outputIndex, 'a') as f6:
		f6.write(controlStart)
		f6.close()

	for count, i in enumerate(allLayers):
		rawLayerName = i.name()
		safeLayerName = re.sub('[\W_]+', '', rawLayerName)
		if i.type() == 0:
			with open(outputIndex, 'a') as f7:
				if cluster_set[count] == True and i.geometryType() == 0:
					new_layer = '"' + safeLayerName + '"' + ": cluster_group"""+ safeLayerName + """JSON,"""
				else:
					new_layer = '"' + safeLayerName + '"' + ": exp_" + safeLayerName + """JSON,"""
				f7.write(new_layer)
				f7.close()
		elif i.type() == 1:
			with open(outputIndex, 'a') as f7:
				new_layer = '"' + safeLayerName + '"' + ": overlay_" + safeLayerName + ""","""
				f7.write(new_layer)
				f7.close()	
	controlEnd = "},{collapsed:false}).addTo(map);"	
	


	with open(outputIndex, 'rb+') as f8:
		f8.seek(-1, os.SEEK_END)
		f8.truncate()
		f8.write(controlEnd)
		f8.close()
	if opacity_raster == True:
		opacityStart = """
		function updateOpacity(value) {
		"""
		with open(outputIndex, 'a') as f9:
			f9.write(opacityStart)
			f9.close()

		for i in allLayers: 
			rawLayerName = i.name()
			safeLayerName = re.sub('[\W_]+', '', rawLayerName)
			if i.type() == 1:
				with open(outputIndex, 'a') as f10:
					new_opc = """
					overlay_""" + safeLayerName + """.setOpacity(value);"""
					f10.write(new_opc)
					f10.close()	
		opacityEnd = """}"""	
		with open(outputIndex, 'rb+') as f11:
			f11.seek(-1, os.SEEK_END)
			f11.truncate()
			f11.write(opacityEnd)
			f11.close()
	elif opacity_raster == False:
		print "no opacity control added"

	#here comes the user locate:
	if locate == True:
		end = """
		map.locate({setView: true, maxZoom: 16});
		function onLocationFound(e) {
    		var radius = e.accuracy / 2;
			L.marker(e.latlng).addTo(map)
        	.bindPopup("You are within " + radius + " meters from this point").openPopup();
			L.circle(e.latlng, radius).addTo(map);
		}
		map.on('locationfound', onLocationFound);
		"""
	else:
		end = ''
	# let's close the file but ask for the extent of all layers if the user wants to show only this extent:
	if extent == 'Fit to layers extent':
		end += """
		map.fitBounds(feature_group.getBounds());"""
	else:
		end += """
		L.control.scale({options: {position: 'bottomleft',maxWidth: 100,metric: true,imperial: false,updateWhenIdle: false}}).addTo(map);"""
	end += """
	</script>""" + wfsLayers + """
</body>
</html>"""
	with open(outputIndex, 'a') as f12:
		f12.write(end)
		f12.close()
	return outputIndex
	#webbrowser.open(outputIndex)

def buildPointWFS(layerName, layerSource, categoryStr, stylestr, cluster_set, cluster_num, visible):
	print "Point WFS: " + layerName
	scriptTag = re.sub('SRSNAME\=EPSG\:\d+', 'SRSNAME=EPSG:4326', layerSource)+"""&outputFormat=text%2Fjavascript&format_options=callback%3Aget"""+layerName+"""Json"""
	new_obj = categoryStr + """
		var exp_"""+layerName+"""JSON;
		exp_"""+layerName+"""JSON = L.geoJson(null, {"""+stylestr+"""
		});
		layerOrder[layerOrder.length] = exp_"""+layerName+"""JSON;
		feature_group.addLayer(exp_"""+layerName+"""JSON);
		layerControl.addOverlay(exp_"""+layerName+"""JSON, '"""+layerName+"""');"""
	if cluster_set == True:
		new_obj += """
		var cluster_group"""+ layerName + """JSON= new L.MarkerClusterGroup({showCoverageOnHover: false});"""				
	new_obj+="""
		function get"""+layerName+"""Json(geojson) {
			exp_"""+layerName+"""JSON.addData(geojson);"""
	if visible == 'show all':
		new_obj+="""
			restackLayers();"""
	if cluster_set == True:
		new_obj += """
				cluster_group"""+ layerName + """JSON.addLayer(exp_""" + layerName + """JSON);"""			
		cluster_num += 1	
		print "cluster_num: " + str(cluster_num)
	new_obj+="""
		};"""
	return new_obj, scriptTag, cluster_num

def buildNonPointJSON(categoryStr, safeLayerName):
	print "Non-point JSON: " + safeLayerName
	new_obj = categoryStr + """
		var exp_""" + safeLayerName + """JSON = new L.geoJson(exp_""" + safeLayerName + """,{
			onEachFeature: pop_""" + safeLayerName + """,
			style: doStyle""" + safeLayerName + """
		});
		layerOrder[layerOrder.length] = exp_"""+safeLayerName+"""JSON;"""
	return new_obj

def buildNonPointWFS(layerName, layerSource, categoryStr, stylestr, popFuncs, visible):
	print "Non-point WFS: " + layerName
	scriptTag = re.sub('SRSNAME\=EPSG\:\d+', 'SRSNAME=EPSG:4326', layerSource)+"""&outputFormat=text%2Fjavascript&format_options=callback%3Aget"""+layerName+"""Json"""
	new_obj = categoryStr + """
		var exp_"""+layerName+"""JSON;
		exp_"""+layerName+"""JSON = L.geoJson(null, {"""+stylestr+"""
		});
		layerOrder[layerOrder.length] = exp_"""+layerName+"""JSON;
		feature_group.addLayer(exp_"""+layerName+"""JSON);
		layerControl.addOverlay(exp_"""+layerName+"""JSON, '"""+layerName+"""');"""
	new_obj+="""
		function get"""+layerName+"""Json(geojson) {
			exp_"""+layerName+"""JSON.addData(geojson);"""
	if visible == 'show all':
		new_obj+="""
			restackLayers();"""
	new_obj+="""
		};"""
	return new_obj, scriptTag

def getLineStyle(penType):
	if penType > 1:
		if penType == 2:
			penStyle_str = "10,5"
		if penType == 3:
			penStyle_str = "1,5"
		if penType == 4:
			penStyle_str = "15,5,1,5"
		if penType == 5:
			penStyle_str = "15,5,1,5,1,5"
	else:
		penStyle_str = ""
	return penStyle_str

def restackLayers(layerName, visible):
	if visible == 'show all':
		return """
		layerOrder[layerOrder.length] = exp_"""+layerName+"""JSON;
		for (index = 0; index < layerOrder.length; index++) {
			feature_group.removeLayer(layerOrder[index]);feature_group.addLayer(layerOrder[index]);
		}"""
	else:
		return ""