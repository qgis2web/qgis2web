def buildPointWFS(layerName, layerSource, categoryStr, stylestr, cluster_set, cluster_num, visible):
	#print "Point WFS: " + layerName
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
	if visible:
		new_obj+="""
			restackLayers();"""
	if cluster_set == True:
		new_obj += """
				cluster_group"""+ layerName + """JSON.addLayer(exp_""" + layerName + """JSON);"""			
		cluster_num += 1	
		#print "cluster_num: " + str(cluster_num)
	new_obj+="""
		};"""
	return new_obj, scriptTag, cluster_num

def buildNonPointJSON(categoryStr, safeLayerName):
	#print "Non-point JSON: " + safeLayerName
	new_obj = categoryStr + """
		var exp_""" + safeLayerName + """JSON = new L.geoJson(exp_""" + safeLayerName + """,{
			onEachFeature: pop_""" + safeLayerName + """,
			style: doStyle""" + safeLayerName + """
		});
		layerOrder[layerOrder.length] = exp_"""+safeLayerName+"""JSON;"""
	return new_obj

def buildNonPointWFS(layerName, layerSource, categoryStr, stylestr, popFuncs, visible):
	#print "Non-point WFS: " + layerName
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
	if visible:
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
	if visible:
		return """
		layerOrder[layerOrder.length] = exp_"""+layerName+"""JSON;
		for (index = 0; index < layerOrder.length; index++) {
			feature_group.removeLayer(layerOrder[index]);feature_group.addLayer(layerOrder[index]);
		}"""
	else:
		return ""
