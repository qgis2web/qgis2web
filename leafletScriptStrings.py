def jsonScript(layer):
	jsonScript = """
		<script src=\"""" + 'data' + """/json_""" + layer + """.js\"></script>"""
	return jsonScript
		
def openScript():
	openScript = """
		<script>"""
	return openScript

def crsScript(crsAuthId, crsProj4):
	crsScript = """
		var crs = new L.Proj.CRS('""" + crsAuthId + """', '""" + crsProj4 + """', {
			resolutions: [2800, 1400, 700, 350, 175, 84, 42, 21, 11.2, 5.6, 2.8, 1.4, 0.7, 0.35, 0.14, 0.07],
		});"""
	return crsScript

def mapScript(extent, matchCRS, crsAuthId, maxZoom, minZoom, bounds):
	mapScript = """
		var map = L.map('map', {"""
	if extent == "Canvas extent" and matchCRS == True and crsAuthId != 'EPSG:4326':
		mapScript += """
			crs: crs,
			continuousWorld: false,
			worldCopyJump: false, """
	mapScript += """
			zoomControl:true, maxZoom:""" + unicode(maxZoom) + """, minZoom:""" + unicode(minZoom) + """
		})"""
	if extent == "Canvas extent":
		mapScript += """.fitBounds(""" + bounds + """);"""
	mapScript += """
		var hash = new L.Hash(map);
		var additional_attrib = '<a href="https://github.com/tomchadwin/qgis2web" target ="_blank">qgis2web</a>';"""
	return mapScript

def featureGroupsScript():
	featureGroupsScript = """
		var feature_group = new L.featureGroup([]);
		var raster_group = new L.LayerGroup([]);"""
	return featureGroupsScript

def basemapsScript(basemap, attribution):
	basemapsScript = """
		var basemap = L.tileLayer('""" + basemap + """', { 
			attribution: additional_attrib + ' """ + attribution + """'
		});
		basemap.addTo(map);"""
	return basemapsScript

def layerOrderScript():
	layerOrderScript = """	
		var layerOrder=new Array();
		function restackLayers() {
			for (index = 0; index < layerOrder.length; index++) {
				feature_group.removeLayer(layerOrder[index]);
				feature_group.addLayer(layerOrder[index]);
			}
		}

		layerControl = L.control.layers({},{},{collapsed:false});"""
	return layerOrderScript

def popupScript(safeLayerName, table):
	popupScript = """
	function pop_""" + safeLayerName + """(feature, layer) {
		var popupContent = """ + table + """;
		layer.bindPopup(popupContent);
	}"""
	return popupScript

def pointToLayerScript(radius_str, colorName, borderColor_str, opacity_str, labeltext):
	pointToLayerScript = """
		pointToLayer: function (feature, latlng) {  
			return L.circleMarker(latlng, {
				radius: """ + radius_str + """,
				fillColor: '""" + colorName + """',
				color: '""" + borderColor_str + """',
				weight: 1,
				opacity: """ + opacity_str + """,
				fillOpacity: """ + opacity_str + """
			})""" + labeltext
	return pointToLayerScript

def pointStyleScript(pointToLayer_str, popFuncs):
	pointStyleScript = pointToLayer_str + """
		},
		onEachFeature: function (feature, layer) {""" + popFuncs + """
		}"""
	return pointStyleScript

def wfsScript(scriptTag):
	wfsScript = """
		<script src='""" + scriptTag + """'></script>"""
	return wfsScript

def jsonPointScript(safeLayerName, pointToLayer_str):
	jsonPointScript = """
	var json_""" + safeLayerName + """JSON = new L.geoJson(json_""" + safeLayerName + """,{
		onEachFeature: pop_""" + safeLayerName + "," + pointToLayer_str + """
		}
	});
	layerOrder[layerOrder.length] = json_"""+safeLayerName+"""JSON;"""
	return jsonPointScript

def clusterScript(safeLayerName):
	clusterScript = """
		var cluster_group"""+ safeLayerName + """JSON= new L.MarkerClusterGroup({showCoverageOnHover: false});
		cluster_group"""+ safeLayerName + """JSON.addLayer(json_""" + safeLayerName + """JSON);"""
	return clusterScript