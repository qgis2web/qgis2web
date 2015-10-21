import re


def buildPointWFS(pointStyleLabel, layerName, layerSource, categoryStr, cluster_set, cluster_num, visible):
    scriptTag = re.sub('SRSNAME\=EPSG\:\d+', 'SRSNAME=EPSG:4326', layerSource) + """&outputFormat=text%2Fjavascript&format_options=callback%3Aget""" + layerName + """Json"""
    new_obj = pointStyleLabel + categoryStr + """
        var json_{layerName}JSON;
        json_{layerName}JSON = L.geoJson(null, {{
            pointToLayer: doPointToLayer{layerName},
            onEachFeature: pop_{layerName}
        }});
        layerOrder[layerOrder.length] = json_{layerName}JSON;
        feature_group.addLayer(json_{layerName}JSON);
        layerControl.addOverlay(json_{layerName}JSON, '{layerName}');""".format(layerName=layerName)
    if cluster_set:
        new_obj += """
        var cluster_group{layerName}JSON= new L.MarkerClusterGroup({{showCoverageOnHover: false}});""".format(layerName=layerName)
    new_obj += """
        function get{layerName}Json(geojson) {{
            json_{layerName}JSON.addData(geojson);""".format(layerName=layerName)
    if visible:
        new_obj += """
            restackLayers();"""
    if cluster_set:
        new_obj += """
                cluster_group{layerName}JSON.addLayer(json_{layerName}JSON);""".format(layerName=layerName)
        cluster_num += 1
    new_obj += """
        };"""
    return new_obj, scriptTag, cluster_num


def buildNonPointJSON(categoryStr, safeLayerName, usedFields):
    if usedFields != 0:
        new_obj = categoryStr + """
            var json_{safeLayerName}JSON = new L.geoJson(json_{safeLayerName}, {{
                onEachFeature: pop_{safeLayerName},
                style: doStyle{safeLayerName}
            }});
            layerOrder[layerOrder.length] = json_{safeLayerName}JSON;""".format(safeLayerName=safeLayerName)
    else:
        new_obj = categoryStr + """
            var json_{safeLayerName}JSON = new L.geoJson(json_{safeLayerName}, {{
                style: doStyle{safeLayerName}
            }});
            layerOrder[layerOrder.length] = json_{safeLayerName}JSON;""".format(safeLayerName=safeLayerName)
    return new_obj


def buildNonPointWFS(layerName, layerSource, categoryStr, stylestr, popFuncs, visible):
    scriptTag = re.sub('SRSNAME\=EPSG\:\d+', 'SRSNAME=EPSG:4326', layerSource)
    scriptTag += """&outputFormat=text%2Fjavascript&format_options=callback%3Aget{layerName}Json""".format(layerName=layerName)
    new_obj = categoryStr + """
        var json_{layerName}JSON;
        json_{layerName}JSON = L.geoJson(null, {{{stylestr},
            onEachFeature: pop_{layerName}
        }});
        layerOrder[layerOrder.length] = json_{layerName}JSON;
        feature_group.addLayer(json_{layerName}JSON);
        layerControl.addOverlay(json_{layerName}JSON, '{layerName}');""".format(layerName=layerName, stylestr=stylestr)
    new_obj += """
        function get{layerName}Json(geojson) {{
            json_{layerName}JSON.addData(geojson);""".format(layerName=layerName)
    if visible:
        new_obj += """
            restackLayers();"""
    new_obj += """
        };"""
    return new_obj, scriptTag


def restackLayers(layerName, visible):
    if visible:
        return """
        layerOrder[layerOrder.length] = json_{layerName}JSON;
        for (index = 0; index < layerOrder.length; index++) {{
            feature_group.removeLayer(layerOrder[index]); feature_group.addLayer(layerOrder[index]);
        }}""".format(layerName=layerName)
    else:
        return ""
