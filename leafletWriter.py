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

import processing
from qgis.core import *
import qgis.utils
import os
from urlparse import parse_qs
import time
import tempfile
import re
from basemaps import basemapLeaflet, basemapAttributions
from leafletFileScripts import *
from leafletLayerScripts import *
from leafletScriptStrings import *

basemapAddresses = basemapLeaflet()
basemapAttributions = basemapAttributions()

def writeLeaflet(outputProjectFileName, width, height, full, layer_list, visible, opacity_raster, cluster_set, webpage_name, webmap_head, webmap_subhead, legend, locate, address, labels, labelhover, selected, json, params):

	canvas = qgis.utils.iface.mapCanvas()
	pluginDir = os.path.dirname(os.path.realpath(__file__))
	outputProjectFileName = os.path.join(outputProjectFileName, 'qgis2web_' + str(time.strftime("%Y_%m_%d-%H_%M_%S")))
	outputIndex = outputProjectFileName + os.sep + 'index.html'
	cluster_num = 1

	QgsApplication.initQgis()

	minify = params["Data export"]["Minify GeoJSON files"]
	extent = params["Scale/Zoom"]["Extent"]
	minZoom = params["Scale/Zoom"]["Min zoom level"]
	maxZoom = params["Scale/Zoom"]["Max zoom level"]
	basemapName = params["Appearance"]["Base layer"]
	matchCRS = params["Appearance"]["Match project CRS"]
	
	removeSpaces = lambda txt:'"'.join( it if i%2 else ''.join(it.split())
						for i,it in enumerate(txt.split('"')))
	
	dataStore, cssStore = writeFoldersAndFiles(pluginDir, outputProjectFileName, cluster_set, labels, matchCRS, canvas)
	writeHTMLstart(outputIndex, webpage_name, cluster_set, labels, address, matchCRS, canvas, full)
	writeCSS(cssStore, full, height, width)

	wfsLayers = ""
	exp_crs = QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId)
	for count, i in enumerate(layer_list):
		rawLayerName = i.name()
		safeLayerName = re.sub('[\W_]+', '', rawLayerName)
		layerFileName = dataStore + os.sep + 'json_' + safeLayerName + '.js'
		if i.providerType() != 'WFS' or json[count] == True and i:
			#print "JSON (" + i.providerType() + "): " + rawLayerName
			precision = params["Data export"]["Precision"]
			if i.type() ==0:
				qgis.core.QgsVectorFileWriter.writeAsVectorFormat(i,layerFileName, 'utf-8', exp_crs, 'GeoJson', selected, layerOptions=["COORDINATE_PRECISION="+str(precision)])

				#now change the data structure to work with leaflet:
				with open(layerFileName) as f:
					lines = f.readlines()
				with open(layerFileName, "w") as f2:
					f2.write("var json_" + str(safeLayerName) + "=") # write the new line before
					for line in lines:
						if minify:
							line = line.strip("\n\t ")
							line = removeSpaces(line)
						f2.write(line)
					f2.close
					
				#now add the js files as data input for our map
				with open(outputIndex, 'a') as f3:
					new_src = jsonScript(safeLayerName)
					# store everything in the file
					f3.write(new_src)
					f3.close()

			#here comes the raster layers. you need an installed version of gdal
			elif i.type() == 1:
				if i.dataProvider().name() != "wms":
					in_raster = str(i.dataProvider().dataSourceUri())
					prov_raster = tempfile.gettempdir() + os.sep + 'json_' + safeLayerName + '_prov.tif'
					out_raster = dataStore + os.sep + 'json_' + safeLayerName + '.png'
					crsSrc = i.crs()
					crsDest = QgsCoordinateReferenceSystem(4326)
					xform = QgsCoordinateTransform(crsSrc, crsDest)
					extentRep = xform.transform(i.extent())
					extentRepNew = ','.join([str(extentRep.xMinimum()), str(extentRep.xMaximum()),str(extentRep.yMinimum()), str(extentRep.yMaximum())])
					processing.runalg("gdalogr:warpreproject",in_raster,i.crs().authid(),"EPSG:4326","",0,1,0,-1,75,6,1,False,0,False,"",prov_raster)
					#print extentRepNew
					processing.runalg("gdalogr:translate",prov_raster,100,True,"",0,"",extentRepNew,False,0,0,75,6,1,False,0,False,"",out_raster)
		#else:
			#print "Not JSON (" + i.providerType() + "): " + rawLayerName
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
		middle = openScript()
		if matchCRS == True and crsAuthId != 'EPSG:4326':
			middle += crsScript(crsAuthId, crsProj4)
		middle += mapScript(extent, matchCRS, crsAuthId, maxZoom, minZoom, bounds)
	if extent == 'Fit to layers extent':
		middle = openScript()
		if matchCRS == True and crsAuthId != 'EPSG:4326':
			middle += crsScript(crsAuthId, crsProj4)
		middle += mapScript(extent, matchCRS, crsAuthId, maxZoom, minZoom, bounds)
	middle += featureGroupsScript()
	if basemapName == 0 or basemapName == "" or basemapName == "None" or matchCRS == True:
		basemapText = ""
	else:
		basemapText = basemapsScript(basemapAddresses[basemapName], basemapAttributions[basemapName])
	layerOrder = layerOrderScript()
	with open(outputIndex, 'a') as f4:
			f4.write(middle)
			f4.write(basemapText)
			f4.write(layerOrder)
			f4.close()
	for count, i in enumerate(layer_list):
		rawLayerName = i.name()
		safeLayerName = re.sub('[\W_]+', '', rawLayerName)
		if i.type()==0:
			with open(outputIndex, 'a') as f5:
				fields = i.pendingFields() 
				field_names = [field.name() for field in fields]
				html_prov = False
				icon_prov = False
				label_exp = ''
				labeltext = ""
				f = ''
				if labels[count]:
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
					if str(f) != "" and str(f) == str(field) and f:
						label_exp = True
					if str(field) == 'icon_exp':
						icon_prov = True 
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
				popFuncs = popFuncsScript(table)
				new_pop = popupScript(safeLayerName, popFuncs)
				 
				layerName = safeLayerName
				renderer = i.rendererV2()
				rendererDump = renderer.dump()
				layer_transp_float = 1 - (float(i.layerTransparency()) / 100)
				new_obj = ""

				#single marker points:
				if rendererDump[0:6] == 'SINGLE':
					symbol = renderer.symbol()
					colorName = symbol.color().name()
					symbol_transp_float = symbol.alpha()
					color_transp_float = float(symbol.color().alpha())/255
					opacity_str = str(layer_transp_float*symbol_transp_float * color_transp_float)
					if i.geometryType() == 0 and icon_prov != True:
						radius_str = str(symbol.size() * 2)
						borderColor_str = str(symbol.symbolLayer(0).borderColor().name())
						pointToLayer_str = pointToLayerScript(radius_str, colorName, borderColor_str, opacity_str, labeltext)
						if i.providerType() == 'WFS' and json[count] == False:
							stylestr = pointStyleScript(pointToLayer_str, popFuncs)
							new_obj, scriptTag, cluster_num = buildPointWFS(layerName, i.source(), "", stylestr, cluster_set[count], cluster_num, visible[count])
							wfsLayers += wfsScript(scriptTag)
						else:
							new_obj = jsonPointScript(safeLayerName, pointToLayer_str)
							if cluster_set[count]:
								new_obj += clusterScript(safeLayerName)
								cluster_num += 1	
					elif i.geometryType() == 1:
						radius_str = str(symbol.width() * 5)
						penStyle_str = getLineStyle(symbol.symbolLayer(0).penStyle())
						lineStyle_str = nonPointStyleScript(radius_str, colorName, "", penStyle_str, opacity_str)
						if i.providerType() == 'WFS' and json[count] == False:
							stylestr = nonPointStylePopupsScript(lineStyle_str, popFuncs)
							new_obj, scriptTag = buildNonPointWFS(layerName, i.source(), "", stylestr, popFuncs, visible[count])
							wfsLayers += wfsScript(scriptTag)
						else:
							new_obj = nonPointStyleFunctionScript(safeLayerName, lineStyle_str)
							new_obj += buildNonPointJSON("", safeLayerName)
							new_obj += restackLayers(layerName, visible[count])		
					elif i.geometryType() == 2:
						borderStyle_str = ""
						if symbol.symbolLayer(0).layerType() == 'SimpleLine' or isinstance(symbol.symbolLayer(0), QgsSimpleLineSymbolLayerV2):
							colorName = 'none'
							borderColor_str = str(symbol.color().name())
							radius_str = str(symbol.symbolLayer(0).width() * 5)
						else:
							borderColor_str = str(symbol.symbolLayer(0).borderColor().name())
							borderStyle_str = getLineStyle(symbol.symbolLayer(0).borderStyle())
							radius_str = str(symbol.symbolLayer(0).borderWidth() * 5)
							if symbol.symbolLayer(0).brushStyle() == 0:
								borderStyle_str = "0"
						polyStyle_str = nonPointStyleScript(radius_str, borderColor_str, colorName, borderStyle_str, opacity_str)
						if i.providerType() == 'WFS' and json[count] == False:
							stylestr = nonPointStylePopupsScript(polyStyle_str, popFuncs)
							new_obj, scriptTag = buildNonPointWFS(layerName, i.source(), "", stylestr, popFuncs, visible[count])
							wfsLayers += wfsScript(scriptTag)
						else:
							new_obj = nonPointStyleFunctionScript(safeLayerName, polyStyle_str)
							new_obj += buildNonPointJSON("", safeLayerName)
							new_obj += restackLayers(layerName, visible[count])	
				elif rendererDump[0:11] == 'CATEGORIZED':
					if i.geometryType() == 0 and icon_prov != True:
						categories = renderer.categories()
						valueAttr = renderer.classAttribute()
						categoryStr = categoryScript(layerName, valueAttr)
						for cat in categories:
							if not cat.value():
								categoryStr += defaultCategoryScript()
							else:
								categoryStr += eachCategoryScript(cat.value())
							symbol = cat.symbol()
							symbol_transp_float = symbol.alpha()
							color_transp_float = float(symbol.color().alpha())/255
							opacity_str = str(layer_transp_float*symbol_transp_float*color_transp_float)
							categoryStr += styleValuesScript(symbol, opacity_str)
						categoryStr += endCategoryScript()
						if i.providerType() == 'WFS' and json[count] == False:
							stylestr = categorizedPointWFSscript(layerName, labeltext, popFuncs)
							new_obj, scriptTag, cluster_num = buildPointWFS(layerName, i.source(), categoryStr, stylestr, cluster_set[count], cluster_num, visible[count])
							wfsLayers += wfsScript(scriptTag)
						else:
							new_obj = categoryStr + categorizedPointJSONscript(safeLayerName, labeltext)
							if cluster_set[count] == True:
								new_obj += clusterScript(safeLayerName)			
							cluster_num += 1	
					elif i.geometryType() == 1:
						categories = renderer.categories()
						valueAttr = renderer.classAttribute()
						categoryStr = categoryScript(layerName, valueAttr)
						for cat in categories:
							if not cat.value():
								categoryStr += defaultCategoryScript()
							else:
								categoryStr += eachCategoryScript(cat.value())
							#categoryStr += "radius: '" + unicode(cat.symbol().size() * 2) + "',"
							symbol = cat.symbol()
							symbol_transp_float = symbol.alpha()
							color_transp_float = float(symbol.color().alpha())/255
							opacity_str = str(layer_transp_float*symbol_transp_float*color_transp_float)
							categoryStr += categorizedLineStylesScript(symbol, opacity_str)
						categoryStr += endCategoryScript()
						stylestr = categorizedNonPointStyleFunctionScript(layerName, popFuncs)
						if i.providerType() == 'WFS' and json[count] == False:
							new_obj, scriptTag = buildNonPointWFS(layerName, i.source(), categoryStr, stylestr, popFuncs, visible[count])
							wfsLayers += wfsScript(scriptTag)
						else:
							new_obj = buildNonPointJSON(categoryStr, safeLayerName)
					elif i.geometryType() == 2:
						categories = renderer.categories()
						valueAttr = renderer.classAttribute()
						categoryStr = categoryScript(layerName, valueAttr)
						for cat in categories:
							if not cat.value():
								categoryStr += defaultCategoryScript()
							else:
								categoryStr += eachCategoryScript(cat.value())
							symbol = cat.symbol()
							symbol_transp_float = symbol.alpha()
							color_transp_float = float(symbol.color().alpha())/255
							opacity_str = str(layer_transp_float*symbol_transp_float*color_transp_float)
							categoryStr += categorizedPolygonStylesScript(symbol, opacity_str)
						categoryStr += endCategoryScript()
						if i.providerType() == 'WFS' and json[count] == False:
							stylestr = categorizedNonPointStyleFunctionScript(layerName, popFuncs)
							new_obj, scriptTag = buildNonPointWFS(layerName, i.source(), categoryStr, stylestr, popFuncs, visible[count])
							wfsLayers += wfsScript(scriptTag)
						else:
							new_obj = buildNonPointJSON(categoryStr, safeLayerName)
				elif rendererDump[0:9] == 'GRADUATED':
					categoryStr = graduatedStyleScript(layerName)
					if i.geometryType() == 0 and icon_prov != True:
						valueAttr = renderer.classAttribute()
						for r in renderer.ranges():
							symbol = r.symbol()
							symbol_transp_float = symbol.alpha()
							color_transp_float = float(symbol.color().alpha())/255
							opacity_str = str(layer_transp_float*symbol_transp_float*color_transp_float)
							categoryStr += graduatedPointStylesScript(valueAttr, r, symbol, opacity_str)
						categoryStr += endGraduatedStyleScript()
						if i.providerType() == 'WFS' and json[count] == False:
							stylestr = categorizedPointWFSscript(layerName, labeltext, popFuncs)
							new_obj, scriptTag, cluster_num = buildPointWFS(layerName, i.source(), categoryStr, stylestr, cluster_set[count], cluster_num, visible[count])
							wfsLayers += wfsScript(scriptTag)
						else:
							new_obj = categoryStr + categorizedPointJSONscript(safeLayerName, labeltext)
							#add points to the cluster group
							if cluster_set[count] == True:
								new_obj += clusterScript(safeLayerName)			
								cluster_num += 1	
					elif i.geometryType() == 1:
						valueAttr = renderer.classAttribute()
						for r in renderer.ranges():
							symbol = r.symbol()
							symbol_transp_float = symbol.alpha()
							color_transp_float = float(symbol.color().alpha())/255
							opacity_str = str(layer_transp_float*symbol_transp_float*color_transp_float)
							categoryStr += graduatedLineStylesScript(valueAttr, r, categoryStr, symbol, opacity_str)
						categoryStr += endGraduatedStyleScript()
						if i.providerType() == 'WFS' and json[count] == False:
							stylestr = categorizedNonPointStyleFunctionScript(layerName, popFuncs)
							new_obj, scriptTag = buildNonPointWFS(layerName, i.source(), categoryStr, stylestr, popFuncs, visible[count])
							wfsLayers += wfsScript(scriptTag)
						else:
							new_obj = buildNonPointJSON(categoryStr, safeLayerName)
					elif i.geometryType() == 2:
						valueAttr = renderer.classAttribute()
						for r in renderer.ranges():
							symbol = r.symbol()
							symbol_transp_float = symbol.alpha()
							color_transp_float = float(symbol.color().alpha())/255
							opacity_str = str(layer_transp_float*symbol_transp_float*color_transp_float)
							categoryStr += graduatedPolygonStylesScript(valueAttr, r, symbol, opacity_str)
						categoryStr += endGraduatedStyleScript()
						if i.providerType() == 'WFS' and json[count] == False:
							stylestr = categorizedNonPointStyleFunctionScript(layerName, popFuncs)
							new_obj, scriptTag = buildNonPointWFS(layerName, i.source(), categoryStr, stylestr, popFuncs, visible[count])
							wfsLayers += wfsScript(scriptTag)
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
#								new_obj, scriptTag, cluster_num = buildPointWFS(layerName, i.source(), categoryStr, stylestr, cluster_set[count], cluster_num, visible[count])
#								wfsLayers += """
#	<script src='""" + scriptTag + """'></script>"""
#							else:
#								new_obj = categoryStr + """
#		var json_""" + safeLayerName + """JSON = new L.geoJson(json_""" + safeLayerName + """,{
#			onEachFeature: pop_""" + safeLayerName + """,
#			pointToLayer: function (feature, latlng) {  
#				return L.circleMarker(latlng, doStyle""" + safeLayerName + """(feature))"""+labeltext+"""
#			}
#		});"""
#								#add points to the cluster group
#								if cluster_set[count] == True:
#									new_obj += """
#			var cluster_group"""+ safeLayerName + """JSON= new L.MarkerClusterGroup({showCoverageOnHover: false});				
#			cluster_group"""+ safeLayerName + """JSON.addLayer(json_""" + safeLayerName + """JSON);"""			
#									cluster_num += 1	

				if icon_prov and i.geometryType() == 0:
					new_obj = customMarkerScript(safeLayerName, labeltext)
					if cluster_set[count] == True:
						new_obj += clusterScript(safeLayerName)
						cluster_num += 1
#				else:
#					new_obj = """
#var json_""" + safeLayerName + """JSON = new L.geoJson(json_""" + safeLayerName + """,{
#	onEachFeature: pop_""" + safeLayerName + """,
#});"""		

				if i.providerType() != 'WFS' or json[count] == True:
					f5.write(new_pop)
				f5.write("""
""" + new_obj)
				if visible[count]:
					if cluster_set[count] == False:
						if i.geometryType() == 0:
							f5.write("""
//add comment sign to hide this layer on the map in the initial view.
feature_group.addLayer(json_"""+ safeLayerName + """JSON);""")
						else:
							f5.write("""
//add comment sign to hide this layer on the map in the initial view.
feature_group.addLayer(json_""" + safeLayerName + """JSON);""")
					else:
						f5.write("""
//add comment sign to hide this layer on the map in the initial view.
cluster_group""" + safeLayerName + """JSON.addTo(map);""")
				else:
					if cluster_set[count] == False:
						if i.geometryType() == 0:
							f5.write("""
	//delete comment sign to show this layer on the map in the initial view.
	//feature_group.addLayer(json_"""+ safeLayerName + """JSON);""")
						if i.geometryType() != 0:
							f5.write("""
	//delete comment sign to show this layer on the map in the initial view.
	//feature_group.addLayer(json_""" + safeLayerName + """JSON);""")
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
				new_obj = wmsScript(safeLayerName, wms_url, wms_layer, wms_format)
			else:
				out_raster_name = 'data/' + 'json_' + safeLayerName + '.png'
				pt2	= i.extent()
				crsSrc = i.crs()    # WGS 84
				crsDest = QgsCoordinateReferenceSystem(4326)  # WGS 84 / UTM zone 33N
				xform = QgsCoordinateTransform(crsSrc, crsDest)
				pt3 = xform.transform(pt2)
				bbox_canvas2 = [pt3.yMinimum(), pt3.yMaximum(),pt3.xMinimum(), pt3.xMaximum()]
				bounds2 = '[[' + str(pt3.yMinimum()) + ',' + str(pt3.xMinimum()) + '],[' + str(pt3.yMaximum()) + ',' + str(pt3.xMaximum()) +']]'
				new_obj = rasterScript(safeLayerName, out_raster_name, bounds2)
			if visible[count]:
				new_obj += """
raster_group.addLayer(overlay_""" + safeLayerName + """);"""
			with open(outputIndex, 'a') as f5_raster:
				f5_raster.write(new_obj)
				f5_raster.close()
	with open(outputIndex, 'a') as f5fgroup:
		f5fgroup.write("""
		raster_group.addTo(map);
		feature_group.addTo(map);""")
		f5fgroup.close()

	if webmap_head != "": 
		titleStart = titleSubScript(webmap_head, webmap_subhead)
		with open(outputIndex, 'a') as f5contr:
			f5contr.write(titleStart)
			f5contr.close()
	if address == True:
		address_text = addressSearchScript()
		with open(outputIndex, 'a') as f5addr:
			f5addr.write(address_text)
			f5addr.close()
	if legend == True:
		legendStart = legendStartScript()
		for i in reversed(layer_list):
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
						#print legend_expression
						#print legend_icon 
						break
					legendStart += """<tr><td><img src='""" + unicode(legend_icon) + """'></img></td><td>""" + unicode(legend_expression) + """</td></tr>"""
		legendStart += legendEndScript()
		with open(outputIndex, 'a') as f5leg:
			f5leg.write(legendStart)
			f5leg.close()

	# let's add layer control
	#print len(basemapName)
	if params["Appearance"]["Add layers list"]:
		if len(basemapName) == 0 or basemapName == "None" or matchCRS == True:
			controlStart = ""
		else:
			controlStart = """
		var baseMaps = {
			'""" + str(basemapName) + """': basemap
		};"""
	#	if len(basemapName) > 1:
	#		controlStart = """
	#	var baseMaps = {"""
	#		for l in range(0,len(basemapName)):
	#			if l < len(basemapName)-1:
	#				controlStart+= """
	#		'""" + str(basemapName[l]) + """': basemap_""" + str(l) + ""","""
	#			if l == len(basemapName)-1:
	#				controlStart+= """
	#		'""" + str(basemapName[l]) + """': basemap_""" + str(l) + """};"""
		#if len
		#control_basemap = """
		#var baseMaps = {"""
		#for l in range(0,len(basemapName)):
		if len(basemapName) == 0 or basemapName == "None":
			controlStart += """
			L.control.layers({},{"""
		else:
			controlStart += """
			L.control.layers(baseMaps,{"""
		with open(outputIndex, 'a') as f6:
			f6.write(controlStart)
			f6.close()

		for count, i in enumerate(layer_list):
			rawLayerName = i.name()
			safeLayerName = re.sub('[\W_]+', '', rawLayerName)
			if i.type() == 0:
				with open(outputIndex, 'a') as f7:
					if cluster_set[count] == True and i.geometryType() == 0:
						new_layer = '"' + rawLayerName + '"' + ": cluster_group"""+ safeLayerName + """JSON,"""
					else:
						new_layer = '"' + rawLayerName + '"' + ": json_" + safeLayerName + """JSON,"""
					f7.write(new_layer)
					f7.close()
			elif i.type() == 1:
				with open(outputIndex, 'a') as f7:
					new_layer = '"' + rawLayerName + '"' + ": overlay_" + safeLayerName + ""","""
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

		for i in layer_list: 
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
	#elif opacity_raster == False:
		#print "no opacity control added"

	if locate == True:
		end = locateScript()
	else:
		end = ''
	# let's close the file but ask for the extent of all layers if the user wants to show only this extent:
	if extent == 'Fit to layers extent':
		end += """
		map.fitBounds(feature_group.getBounds());"""
	if params["Appearance"]["Add scale bar"]:
		end += """
		L.control.scale({options: {position: 'bottomleft',maxWidth: 100,metric: true,imperial: false,updateWhenIdle: false}}).addTo(map);"""
	end += endHTMLscript(wfsLayers)
	with open(outputIndex, 'a') as f12:
		f12.write(end)
		f12.close()
	return outputIndex
