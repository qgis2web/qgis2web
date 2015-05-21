def jsonScript(layer):
	json = """
		<script src=\"""" + 'data' + """/json_""" + layer + """.js\"></script>"""
	return json
		
def openScript():
	openScript = """
		<script>"""
	return openScript

def crsScript(crsAuthId, crsProj4):
	crs = """
		var crs = new L.Proj.CRS('""" + crsAuthId + """', '""" + crsProj4 + """', {
			resolutions: [2800, 1400, 700, 350, 175, 84, 42, 21, 11.2, 5.6, 2.8, 1.4, 0.7, 0.35, 0.14, 0.07],
		});"""
	return crs

def mapScript(extent, matchCRS, crsAuthId, maxZoom, minZoom, bounds):
	map = """
		var map = L.map('map', {"""
	if extent == "Canvas extent" and matchCRS == True and crsAuthId != 'EPSG:4326':
		map += """
			crs: crs,
			continuousWorld: false,
			worldCopyJump: false, """
	map += """
			zoomControl:true, maxZoom:""" + unicode(maxZoom) + """, minZoom:""" + unicode(minZoom) + """
		})"""
	if extent == "Canvas extent":
		map += """.fitBounds(""" + bounds + """);"""
	map += """
		var hash = new L.Hash(map);
		var additional_attrib = '<a href="https://github.com/tomchadwin/qgis2web" target ="_blank">qgis2web</a>';"""
	return map

def featureGroupsScript():
	featureGroups = """
		var feature_group = new L.featureGroup([]);
		var raster_group = new L.LayerGroup([]);"""
	return featureGroups

def basemapsScript(basemap, attribution):
	basemaps = """
		var basemap = L.tileLayer('""" + basemap + """', { 
			attribution: additional_attrib + ' """ + attribution + """'
		});
		basemap.addTo(map);"""
	return basemaps

def layerOrderScript():
	layerOrder = """	
		var layerOrder=new Array();
		function restackLayers() {
			for (index = 0; index < layerOrder.length; index++) {
				feature_group.removeLayer(layerOrder[index]);
				feature_group.addLayer(layerOrder[index]);
			}
		}

		layerControl = L.control.layers({},{},{collapsed:false});"""
	return layerOrder

def popupScript(safeLayerName, table):
	popup = """
	function pop_""" + safeLayerName + """(feature, layer) {
		var popupContent = """ + table + """;
		layer.bindPopup(popupContent);
	}"""
	return popup

def pointToLayerScript(radius_str, colorName, borderColor_str, opacity_str, labeltext):
	pointToLayer = """
		pointToLayer: function (feature, latlng) {  
			return L.circleMarker(latlng, {
				radius: """ + radius_str + """,
				fillColor: '""" + colorName + """',
				color: '""" + borderColor_str + """',
				weight: 1,
				opacity: """ + opacity_str + """,
				fillOpacity: """ + opacity_str + """
			})""" + labeltext
	return pointToLayer

def pointStyleScript(pointToLayer_str, popFuncs):
	pointStyle = pointToLayer_str + """
		},
		onEachFeature: function (feature, layer) {""" + popFuncs + """
		}"""
	return pointStyle

def wfsScript(scriptTag):
	wfs = """
		<script src='""" + scriptTag + """'></script>"""
	return wfs

def jsonPointScript(safeLayerName, pointToLayer_str):
	jsonPoint = """
	var json_""" + safeLayerName + """JSON = new L.geoJson(json_""" + safeLayerName + """,{
		onEachFeature: pop_""" + safeLayerName + "," + pointToLayer_str + """
		}
	});
	layerOrder[layerOrder.length] = json_"""+safeLayerName+"""JSON;"""
	return jsonPoint

def clusterScript(safeLayerName):
	cluster = """
		var cluster_group"""+ safeLayerName + """JSON= new L.MarkerClusterGroup({showCoverageOnHover: false});
		cluster_group"""+ safeLayerName + """JSON.addLayer(json_""" + safeLayerName + """JSON);"""
	return cluster

def nonPointStyleScript(radius_str, colorName, fillColor, penStyle_str, opacity_str):
	nonPointStyle = """
			return {
				weight: """ + radius_str + """,
				color: '""" + colorName + """',
				fillColor: '""" + fillColor + """',
				dashArray: '""" + penStyle_str + """',
				opacity: """ + opacity_str + """,
				fillOpacity: """ + opacity_str + """
			};"""
	return nonPointStyle

def nonPointStylePopupsScript(lineStyle_str, popFuncs):
	nonPointStylePopups = """
		style: function (feature) {""" + lineStyle_str + """
		},
		onEachFeature: function (feature, layer) {""" + popFuncs + """
		}"""
	return nonPointStylePopups

def nonPointStyleFunctionScript(safeLayerName, lineStyle_str):
	nonPointStyleFunction = """
	function doStyle""" + safeLayerName + """(feature) {""" + lineStyle_str + """
	}"""
	return nonPointStyleFunction