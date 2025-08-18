import re
import os
import codecs
from urllib.parse import parse_qs

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProject,
                       QgsRenderContext,
                       QgsSingleSymbolRenderer,
                       QgsCategorizedSymbolRenderer,
                       QgsGraduatedSymbolRenderer,
                       QgsRuleBasedRenderer,
                       QgsHeatmapRenderer,
                       QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsWkbTypes)
from qgis2web.utils import safeName, is25d, BLEND_MODES

try:
    from vector_tiles_reader.plugin.util.tile_json import TileJSON
    vt_enabled = True
except ImportError:
    vt_enabled = False

try:
    from quick_map_services.py_tiled_layer.tilelayer import TileLayer
    qms = True
except ImportError:
    qms = False

class LegendItem:
    def __init__(self, label, color):
        self._label = label
        self._color = color
    def label(self):
        return self._label
    def color(self):
        return self._color
    
def writeLayersAndGroups(layers, groups, collapsedGroup, visible, interactive, folder, popup,
                         settings, json, matchCRS, clustered, getFeatureInfo, baseMap,
                         iface, restrictToExtent, extent, bounds, authid):

    canvas = iface.mapCanvas()
    layerVars = ""
    layer_names_id = {}
    vtLayers = []
    for count, (layer, encode2json,
                cluster, info, baseMap) in enumerate(zip(layers, json, clustered,
                                                getFeatureInfo, baseMap)):
        layer_names_id[layer.id()] = str(count)
        if is25d(layer, canvas, restrictToExtent, extent):
            pass
        else:
            (layerVar,
             vtLayers) = layerToJavascript(iface, layer, encode2json, matchCRS,
                                           interactive[count], cluster, info,
                                           restrictToExtent, extent, count,
                                           vtLayers)
            layerVars += "\n" + "\n".join([layerVar])
    (groupVars, groupedLayers) = buildGroups(groups, collapsedGroup, qms, layer_names_id)
    (mapLayers, layerObjs, osmb) = layersAnd25d(layers, canvas,
                                                restrictToExtent, extent, qms)
    visibility = getVisibility(mapLayers, layerObjs, visible)

    usedGroups = []
    (group_and_no_group_list,
     usedGroups) = getGroups(canvas, layers, restrictToExtent,
                             extent, groupedLayers)
    layersList = []
    # currentVT = ""
    for layer in (group_and_no_group_list):
        layersList.append(layer.replace("'", "\\'"))
    layersListString = "var layersList = [" + ",".join(layersList) + "];"

    fieldAliases = ""
    fieldImages = ""
    fieldLabels = ""
    blend_mode = ""
    for count, (layer, labels) in enumerate(zip(layers, popup)):
        vts = layer.customProperty("VectorTilesReader/vector_tile_url")
        sln = safeName(layer.name()) + "_" + str(count)
        if (layer.type() == layer.VectorLayer and
                layer.wkbType() != QgsWkbTypes.NoGeometry and
                vts is None and
                not isinstance(layer.renderer(), QgsHeatmapRenderer) and
                not is25d(layer, canvas, restrictToExtent, extent)):
            (fieldLabels, fieldAliases, fieldImages,
             blend_mode) = getPopups(layer, labels, sln, fieldLabels,
                                     fieldAliases, fieldImages)
    path = os.path.join(folder, "layers", "layers.js")
    with codecs.open(path, "w", "utf-8") as f:
        if matchCRS:
            f.write("""ol.proj.proj4.register(proj4);
//ol.proj.get("%s").setExtent(%s);
""" % (authid, bounds))
        f.write("""var wms_layers = [];\n""")
        f.write(layerVars + "\n")
        f.write(groupVars + "\n")
        f.write(visibility + "\n")
        f.write(layersListString + "\n")
        f.write(fieldAliases)
        f.write(fieldImages)
        f.write(fieldLabels)
        f.write(blend_mode)
    return osmb


def layerToJavascript(iface, layer, encode2json, matchCRS, interactive,
                      cluster, info, restrictToExtent, extent, count,
                      vtLayers):
    (minResolution, maxResolution) = getScaleRes(layer)
    layerName = safeName(layer.name()) + "_" + str(count)
    rawName = layer.name()
    layerAttr = getAttribution(layer)
    if layer.type() == layer.VectorLayer and not is25d(layer,
                                                       iface.mapCanvas(),
                                                       restrictToExtent,
                                                       extent):
        renderer = layer.renderer()
        cluster = isCluster(cluster, renderer)
        hmRadius = 0
        hmRamp = ""
        hmWeight = 0
        hmWeightMax = 0
        vts = layer.customProperty("VectorTilesReader/vector_tile_url")
        if vts is not None:
            if vts not in vtLayers:
                vtLayers.append(vts)
                return getVT(vts), vtLayers
            else:
                return "", vtLayers
        if isinstance(renderer, QgsHeatmapRenderer):
            (pointLayerType, hmRadius,
             hmRamp, hmWeight, hmWeightMax) = getHeatmap(layer, renderer)
        else:
            pointLayerType = "Vector"
        crsConvert = getCRS(iface, matchCRS)
        if layer.providerType() == "WFS" and not encode2json:
            return getWFS(layer, layerName, layerAttr, interactive, cluster,
                          minResolution, maxResolution), vtLayers
        else:
            return getJSON(layerName, crsConvert, layerAttr, interactive,
                           cluster, pointLayerType, minResolution,
                           maxResolution, hmRadius, hmRamp, hmWeight,
                           hmWeightMax, renderer, layer), vtLayers
    elif layer.type() == layer.RasterLayer:
        if layer.providerType().lower() == "wms":
            source = layer.source()
            opacity = layer.renderer().opacity()
            d = parse_qs(source)
            if "type" in d and d["type"][0] == "xyz":
                baseMap = layer.customProperty("qgis2web/BaseMap", 0) == 2
                return getXYZ(layerName, rawName, opacity, minResolution,
                              maxResolution, layerAttr, d["url"][0], baseMap), vtLayers
            elif "tileMatrixSet" in d:
                return getWMTS(layer, d, layerAttr, layerName, opacity,
                               minResolution, maxResolution), vtLayers
            else:
                return getWMS(source, layer, layerAttr, layerName, opacity,
                              minResolution, maxResolution, info), vtLayers
        elif layer.providerType().lower() == "gdal":
            return getRaster(iface, layer, layerName, layerAttr, minResolution,
                             maxResolution, matchCRS), vtLayers


def getScaleRes(layer):
    minResolution = ""
    maxResolution = ""
    if layer.hasScaleBasedVisibility():
        if layer.minimumScale() != 0:
            minRes = 1 / ((1 / layer.minimumScale()) * 39.37 * 90.7)
            minResolution = "\nmaxResolution:%s,\n" % str(minRes)
        if layer.maximumScale() != 0:
            maxRes = 1 / ((1 / layer.maximumScale()) * 39.37 * 90.7)
            maxResolution = "minResolution:%s,\n" % str(maxRes)
    return (minResolution, maxResolution)


def getAttribution(layer):
    attrText = layer.attribution()
    attrUrl = layer.attributionUrl()
    if attrText != "":
        layerAttr = ' &nbsp &middot; <a href="%s">%s</a>' % (attrUrl, attrText)
    else:
        layerAttr = " "
    return layerAttr


def build25d(canvas, layer, count):
    shadows = ""
    renderer = layer.renderer()
    renderContext = QgsRenderContext.fromMapSettings(canvas.mapSettings())
    fields = layer.fields()
    renderer.startRender(renderContext, fields)
    for feat in layer.getFeatures():
        if isinstance(renderer, QgsCategorizedSymbolRenderer):
            classAttribute = renderer.classAttribute()
            attrValue = feat.attribute(classAttribute)
            catIndex = renderer.categoryIndexForValue(attrValue)
            categories = renderer.categories()
            symbol = categories[catIndex].symbol()
        elif isinstance(renderer, QgsGraduatedSymbolRenderer):
            classAttribute = renderer.classAttribute()
            attrValue = feat.attribute(classAttribute)
            ranges = renderer.ranges()
            for range in ranges:
                if (attrValue >= range.lowerValue() and
                        attrValue <= range.upperValue()):
                    symbol = range.symbol().clone()
        elif isinstance(renderer, QgsRuleBasedRenderer):
            rule = renderer.rootRule().match(feat, renderContext)
            if rule is not None:
                symbol = rule.symbol().clone()
        else:
            symbol = renderer.symbolForFeature(feat, renderContext)
        symbolLayer = symbol.symbolLayer(0)
        if not symbolLayer.paintEffect().effectList()[0].enabled():
            shadows = "'2015-07-15 10:00:00'"
    renderer.stopRender(renderContext)
    osmb = """
var osmb = new OSMBuildings(map).date(new Date({shadows}));
osmb.set(json_{sln}_{count});""".format(shadows=shadows,
                                        sln=safeName(layer.name()),
                                        count=str(count))
    return osmb


def getVisibility(mapLayers, layers, visible):
    visibility = ""
    currentVT = ""
    for layer, layerObj, v in zip(mapLayers, layers, visible):
        vts = layerObj.customProperty("VectorTilesReader/vector_tile_url")
        if vts is None or vts != currentVT:
            if vts is not None:
                lname = "lyr_%s" % safeName(vts)
            else:
                lname = layer
            visibility += "\n".join(["%s.setVisible(%s);" % (
                lname, str(v).lower())])
            if vts is not None:
                currentVT = vts
    return visibility


def buildGroups(groups, collapsedGroup, qms, layer_names_id):
    groupVars = ""
    groupedLayers = {}
    collapsedIndex = 0
    for group, groupLayers in groups.items():
        groupLayerObjs = ""
        for layer in groupLayers:
            vts = layer.customProperty("VectorTilesReader/vector_tile_url")
            if qms:
                if isinstance(layer, TileLayer):
                    continue
            if vts is not None:
                continue
            groupLayerObjs += ("lyr_" + safeName(layer.name()) + "_" +
                               layer_names_id[layer.id()] + ",")
            
        groupCollapsed = "close" if collapsedGroup[collapsedIndex] else "open"
        collapsedIndex += 1
        
        groupVars += ('''var %s = new ol.layer.Group({
                                layers: [%s],
                                fold: '%s',
                                title: '%s'});\n''' %
                      ("group_" + safeName(group), groupLayerObjs, groupCollapsed, group.replace("'", "\\'")))
        for layer in groupLayers:
            groupedLayers[layer.id()] = safeName(group)
    return (groupVars, groupedLayers)


def layersAnd25d(layers, canvas, restrictToExtent, extent, qms):
    mapLayers = []
    layerObjs = []
    osmb = ""
    for count, layer in enumerate(layers):
        if is25d(layer, canvas, restrictToExtent, extent):
            osmb = build25d(canvas, layer, count)
        else:
            if (qms and not isinstance(layer, TileLayer)) or not qms:
                mapLayers.append("lyr_" + safeName(layer.name()) +
                                 "_" + str(count))
                layerObjs.append(layer)
    return (mapLayers, layerObjs, osmb)


def getGroups(canvas, layers, restrictToExtent, extent, groupedLayers):
    group_and_no_group_list = []
    usedGroups = []
    currentVT = ""
    for count, layer in enumerate(layers):
        vts = layer.customProperty("VectorTilesReader/vector_tile_url")
        if (vts is not None):
            if (vts != currentVT):
                group_and_no_group_list.append("lyr_" + safeName(vts))
                currentVT = vts
        else:
            if is25d(layer, canvas, restrictToExtent, extent):
                pass
            elif layer.id() in groupedLayers:
                groupName = groupedLayers[layer.id()]
                if groupName not in usedGroups:
                    group_and_no_group_list.append("group_" + safeName(groupName))
                    usedGroups.append(groupName)
            else:
                group_and_no_group_list.append("lyr_" + safeName(layer.name()) +
                                     "_" + str(count))

    return (group_and_no_group_list, usedGroups)


def getPopups(layer, labels, sln, fieldLabels, fieldAliases, fieldImages):
    fieldList = layer.fields()
    aliasFields = ""
    imageFields = ""
    labelFields = ""
    for field, label in zip(labels.keys(), labels.values()):
        labelFields += "'%(field)s': '%(label)s', " % (
            {"field": field.replace("'", "\\'"), "label": label})
    labelFields = "{%(labelFields)s});\n" % (
        {"labelFields": labelFields})
    labelFields = "lyr_%(name)s.set('fieldLabels', " % (
        {"name": sln}) + labelFields
    fieldLabels += labelFields
    for f in fieldList:
        fieldIndex = fieldList.indexFromName(f.name())
        aliasFields += "'%(field)s': '%(alias)s', " % (
            {"field": f.name().replace("'", "\\'"),
             "alias": layer.attributeDisplayName(fieldIndex).replace("'",
                                                                     "\\'")})
        widget = layer.editorWidgetSetup(fieldIndex).type()
        imageFields += "'%(field)s': '%(image)s', " % (
            {"field": f.name().replace("'", "\\'"),
             "image": widget})
    aliasFields = "{%(aliasFields)s});\n" % (
        {"aliasFields": aliasFields})
    aliasFields = "lyr_%(name)s.set('fieldAliases', " % (
        {"name": sln}) + aliasFields
    fieldAliases += aliasFields
    imageFields = "{%(imageFields)s});\n" % (
        {"imageFields": imageFields})
    imageFields = "lyr_%(name)s.set('fieldImages', " % (
        {"name": sln}) + imageFields
    fieldImages += imageFields
    blend_mode = """lyr_%(name)s.on('precompose', function(evt) {
    evt.context.globalCompositeOperation = '%(blend)s';
});""" % ({"name": sln, "blend": BLEND_MODES[layer.blendMode()]})
    return (fieldLabels, fieldAliases, fieldImages, blend_mode)


def getWFS(layer, layerName, layerAttr, interactive, cluster, minResolution,
           maxResolution):
    layerCode = '''var format_%(n)s = new ol.format.GeoJSON();
var jsonSource_%(n)s = new ol.source.Vector({
    attributions: '%(layerAttr)s',
    format: format_%(n)s
});''' % {"n": layerName, "layerAttr": layerAttr}
    if cluster:
        layerCode += '''cluster_%(n)s = new ol.source.Cluster({
  distance: 10,
  source: jsonSource_%(n)s
});''' % {"n": layerName}
    layerCode += '''var lyr_%(n)s = new ol.layer.Vector({
    declutter: false,
    source: ''' % {"n": layerName}
    if cluster:
        layerCode += 'cluster_%(n)s,' % {"n": layerName}
    else:
        layerCode += 'jsonSource_%(n)s,' % {"n": layerName}
    layerCode += '''%(min)s %(max)s
    style: style_%(n)s,
    interactive: %(int)s,
    title: '%(name)s'
});

function get%(n)sJson(geojson) {
    var features_%(n)s = format_%(n)s.readFeatures(geojson);
    jsonSource_%(n)s.addFeatures(features_%(n)s);
}''' % {"name": layer.name().replace("'", "\\'"), "n": layerName, "int": str(interactive).lower(),
        "min": minResolution, "max": maxResolution}
    return layerCode


def getJSON(layerName, crsConvert, layerAttr, interactive, cluster,
            pointLayerType, minResolution, maxResolution, hmRadius, hmRamp,
            hmWeight, hmWeightMax, renderer, layer):
    layerCode = '''var format_%(n)s = new ol.format.GeoJSON();
var features_%(n)s = format_%(n)s.readFeatures(json_%(n)s, %(crs)s);
var jsonSource_%(n)s = new ol.source.Vector({
    attributions: '%(layerAttr)s',
});
jsonSource_%(n)s.addFeatures(features_%(n)s);''' % {"n": layerName,
                                                    "crs": crsConvert,
                                                    "layerAttr": layerAttr}
    if cluster:
        layerCode += '''\ncluster_%(n)s = new ol.source.Cluster({
  distance: 30,
  source: jsonSource_%(n)s
});''' % {"n": layerName}
    layerCode += '''\nvar lyr_%(n)s = new ol.layer.%(t)s({
                declutter: false,
                source:''' % {"n": layerName, "t": pointLayerType}
    if cluster:
        layerCode += 'cluster_%(n)s,' % {"n": layerName}
    else:
        layerCode += 'jsonSource_%(n)s,' % {"n": layerName}
    layerCode += '''%(min)s %(max)s''' % {"min": minResolution,
                                          "max": maxResolution}
    if pointLayerType == "Vector":
        layerCode += '''
                style: style_%(n)s,
                popuplayertitle: '%(name)s',
                interactive: %(int)s,''' % {"n": layerName,
                                            "int": str(interactive).lower(),
                                            "name": layer.name().replace("'", "\\'")}
    else:
        layerCode += writeHeatmap(hmRadius, hmRamp, hmWeight, hmWeightMax)
    if isinstance(renderer, QgsSingleSymbolRenderer):
        layerCode += '''
                title: '<img src="styles/legend/%(icon)s.png" /> %(name)s'
            });''' % {"icon": layerName,
                      "name": layer.name().replace("'", "\\'")}              
    elif isinstance(renderer, QgsCategorizedSymbolRenderer):
        layerCode += getLegend(renderer.categories(), layer, layerName)
        layerCode += '''});'''
    elif isinstance(renderer, QgsGraduatedSymbolRenderer):
        layerCode += getLegend(renderer.ranges(), layer, layerName)
        layerCode += '''});'''
    elif isinstance(renderer, QgsRuleBasedRenderer):
        rules = renderer.rootRule().children()
        subitems = []
        for rule in rules:
            if rule.symbol() is not None:
                subitems.append(LegendItem(rule.label(), rule.symbol().color()))
        layerCode += getLegend(subitems, layer, layerName)
        layerCode += '''});'''
    else:
        layerCode += '''
                title: '%(name)s'
            });''' % {"name": layer.name().replace("'", "\\'")}
    return layerCode


def getLegend(subitems, layer, layerName):
    icons = ""
    for count, subitem in enumerate(subitems):
        text = subitem.label().replace("'", "\\'")
        icons += ("""\\
    <img src="styles/legend/%(icon)s_%(count)s.png" /> %(text)s<br />""" %
                  {"icon": layerName, "count": count, "text": text})
    legend = '''
    title: '%(name)s<br />%(icons)s' ''' % {"icons": icons, 
                                            "name": layer.name().replace("'", "\\'")}
    return legend


def isCluster(cluster, renderer):
    if (cluster):
        cluster = True
    else:
        cluster = False
    return cluster


def getVT(json_url):
    sln = safeName(json_url)
    try:
        key = json_url.split("?")[1]
    except Exception:
        key = ""
    json = TileJSON(json_url)
    json.load()
    tile_url = json.tiles()[0].split("?")[0]
    key_url = "%s?%s" % (tile_url, key)
    layerCode = """
        var lyr_%s = new ol.layer.VectorTile({
            source: new ol.source.VectorTile({
                format: new ol.format.MVT(),
                url: '%s',
                tileGrid: new ol.tilegrid.createXYZ({
                    tileSize: 512, maxZoom: 14
                }),
                tilePixelRatio: 8
            }),
            style: style_%s,
            interactive: %s
        });
        """ % (sln, key_url, sln, "false")
    return layerCode


def getHeatmap(layer, renderer):
    pointLayerType = "Heatmap"
    hmRadius = renderer.radius()
    colorRamp = renderer.colorRamp()
    hmStart = colorRamp.color1().name()
    hmEnd = colorRamp.color2().name()
    hmRamp = "['" + hmStart + "', "
    hmStops = colorRamp.stops()
    for stop in hmStops:
        hmRamp += "'" + stop.color.name() + "', "
    hmRamp += "'" + hmEnd + "']"
    hmWeight = renderer.weightExpression()
    fields = layer.fields()
    hmWeightId = fields.indexFromName(hmWeight)
    hmWeightMax = layer.maximumValue(hmWeightId)
    return (pointLayerType, hmRadius, hmRamp, hmWeight, hmWeightMax)


def getCRS(iface, matchCRS):
    if matchCRS:
        mapCRS = iface.mapCanvas().mapSettings().destinationCrs().authid()
        crsConvert = """
            {dataProjection: 'EPSG:4326', featureProjection: '%(d)s'}""" % {
            "d": mapCRS}
    else:
        crsConvert = """
            {dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857'}"""
    return crsConvert


def writeHeatmap(hmRadius, hmRamp, hmWeight, hmWeightMax):
    layerCode = '''
                radius: %(hmRadius)d * 2,
                gradient: %(hmRamp)s,
                blur: 15,
                shadow: 250,''' % {"hmRadius": hmRadius, "hmRamp": hmRamp}
    if hmWeight != "":
        layerCode += '''
    weight: function(feature){
        var weightField = '%(hmWeight)s';
        var featureWeight = feature.get(weightField);
        var maxWeight = %(hmWeightMax)d;
        var calibratedWeight = featureWeight/maxWeight;
        return calibratedWeight;
    },''' % {"hmWeight": hmWeight, "hmWeightMax": hmWeightMax}
    return layerCode


def getXYZ(layerName, rawName, opacity, minResolution, maxResolution,
           layerAttr, url, baseMap):
    layerCode = """
        var lyr_%s = new ol.layer.Tile({
            'title': '%s',""" % (layerName, rawName.replace("'", "\\'"))
    if baseMap:
        layerCode += """
            'type':'base',"""
    else: 
        layerCode += ""
    layerCode += """
            'opacity': %f,
            %s
            %s
            source: new ol.source.XYZ({
            attributions: '%s',
                url: '%s'
            })
        });""" % (opacity, minResolution, maxResolution,
                  layerAttr, url)
    
    return layerCode


def getWMTS(layer, d, layerAttr, layerName, opacity, minResolution,
            maxResolution):
    layerId = d["layers"][0]
    url = d["url"][0]
    format = d["format"][0]
    style = d["styles"][0]
    return '''
    var projection_%(n)s = ol.proj.get('EPSG:3857');
    var projectionExtent_%(n)s = projection_%(n)s.getExtent();
    var size_%(n)s = ol.extent.getWidth(projectionExtent_%(n)s) / 256;
    var resolutions_%(n)s = new Array(14);
    var matrixIds_%(n)s = new Array(14);
    for (var z = 0; z < 14; ++z) {
        // generate resolutions and matrixIds arrays for this WMTS
        resolutions_%(n)s[z] = size_%(n)s / Math.pow(2, z);
        matrixIds_%(n)s[z] = z;
    }
    var lyr_%(n)s = new ol.layer.Tile({
                            source: new ol.source.WMTS(({
                                url: "%(url)s",
                                attributions: '%(layerAttr)s',
                                "layer": "%(layerId)s",
                                "TILED": "true",
             matrixSet: 'EPSG:3857',
             format: '%(format)s',
              projection: projection_%(n)s,
              tileGrid: new ol.tilegrid.WMTS({
                origin: ol.extent.getTopLeft(projectionExtent_%(n)s),
                resolutions: resolutions_%(n)s,
                matrixIds: matrixIds_%(n)s
              }),
              style: '%(style)s',
              wrapX: true,
                                "VERSION": "1.0.0",
                            })),
                            title: '%(name)s',
                            opacity: %(opacity)s,
                            %(minRes)s
                            %(maxRes)s
                          });''' % {"layerId": layerId, "url": url,
                                    "layerAttr": layerAttr, "format": format,
                                    "n": layerName, "name": layer.name().replace("'", "\\'"),
                                    "opacity": opacity, "style": style,
                                    "minRes": minResolution,
                                    "maxRes": maxResolution}


def getWMS(source, layer, layerAttr, layerName, opacity, minResolution,
           maxResolution, info):
    layers = re.search(r"layers=(.*?)(?:&|$)", source).groups(0)[0]
    url = re.search(r"url=(.*?)(?:&|$)", source).groups(0)[0]
    metadata = layer.htmlMetadata()
    needle = "<tr><td>%s</td><td>(.+?)</td>" % (
        QCoreApplication.translate("QgsWmsProvider",
                                   "WMS Version"))
    result = re.search(needle, metadata)
    if result:
        version = result.group(1)
    else:
        version = ""
    return '''var lyr_%(n)s = new ol.layer.Tile({
                            source: new ol.source.TileWMS(({
                              url: "%(url)s",
                              attributions: '%(layerAttr)s',
                              params: {
                                "LAYERS": "%(layers)s",
                                "TILED": "true",
                                "VERSION": "%(version)s"},
                            })),
                            title: '%(name)s',
                            popuplayertitle: '%(name)s',
                            opacity: %(opacity)f,
                            %(minRes)s
                            %(maxRes)s
                          });
              wms_layers.push([lyr_%(n)s, %(info)d]);''' % {
        "layers": layers, "url": url, "layerAttr": layerAttr, "n": layerName,
        "name": layer.name().replace("'", "\\'"), "version": version, "opacity": opacity,
        "minRes": minResolution, "maxRes": maxResolution, "info": info}


def getRaster(iface, layer, layerName, layerAttr, minResolution, maxResolution,
              matchCRS):
    crsSrc = layer.crs()
    projectCRS = iface.mapCanvas().mapSettings().destinationCrs()
    if not (matchCRS and crsSrc == projectCRS):
        mapCRS = "EPSG:3857"
        crsDest = QgsCoordinateReferenceSystem(3857)

        try:
            xform = QgsCoordinateTransform(crsSrc, crsDest,
                                           QgsProject.instance())
        except Exception:
            xform = QgsCoordinateTransform(crsSrc, crsDest)
        extentRep = xform.transformBoundingBox(layer.extent())
    else:
        mapCRS = projectCRS.authid()
        extentRep = layer.extent()

    sExtent = "[%f, %f, %f, %f]" % (extentRep.xMinimum(), extentRep.yMinimum(),
                                    extentRep.xMaximum(), extentRep.yMaximum())
    
    # Get legend symbology items
    legendSymbologyItems = layer.legendSymbologyItems()

    # Convert legendSymbologyItems to a format compatible with getAttributionLegend and getTitleLegend
    subitems = [LegendItem(item[0], item[1]) for item in legendSymbologyItems]

    # Use getAttributionLegend and getTitleLegend to compose attribution and title
    title = getLegend(subitems, layer, layerName)

    return '''var lyr_%(n)s = new ol.layer.Image({
        opacity: 1,
        %(title)s,
        %(minRes)s
        %(maxRes)s
        source: new ol.source.ImageStatic({
            url: "./layers/%(n)s.png",
            attributions: '%(layerAttr)s',
            projection: '%(mapCRS)s',
            alwaysInRange: true,
            imageExtent: %(extent)s
        })
    });''' % {"n": layerName,
                "extent": sExtent,
                "name": layer.name().replace("'", "\\'"),
                "minRes": minResolution,
                "maxRes": maxResolution,
                "mapCRS": mapCRS,
                "layerAttr": layerAttr,
                "title": title}
