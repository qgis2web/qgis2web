import re
import os
import shutil
from urlparse import parse_qs
from PyQt4.QtCore import QSize
from qgis.core import *
from utils import scaleToZoom
from basemaps import basemapLeaflet, basemapAttributions

basemapAddresses = basemapLeaflet()


def jsonScript(layer):
    json = """
        <script src="data/json_{layer}.js\"></script>""".format(layer=layer)
    return json


def scaleDependentLayerScript(layer, layerName):
    min = layer.minimumScale()
    max = layer.maximumScale()
    scaleDependentLayer = """
            if (map.getZoom() <= {min} && map.getZoom() >= {max}) {{
                feature_group.addLayer(json_{layerName}JSON);
            }} else if (map.getZoom() > {min} || map.getZoom() < {max}) {{
                feature_group.removeLayer(json_{layerName}JSON);
            }}""".format(min=scaleToZoom(min), max=scaleToZoom(max),
                         layerName=layerName)
    return scaleDependentLayer


def scaleDependentLabelScript(layer, layerName):
    pal = QgsPalLayerSettings()
    pal.readFromLayer(layer)
    sv = pal.scaleVisibility
    if sv:
        min = scaleToZoom(pal.scaleMin)
        max = scaleToZoom(pal.scaleMax)
        scaleDependentLabel = """
            if (map.hasLayer(json_%(layerName)sJSON)) {
                if (map.getZoom() <= %(min)d && map.getZoom() >= %(max)d) {
                    json_%(layerName)sJSON.eachLayer(function (layer) {
                        layer.showLabel();
                    });
                } else {
                    json_%(layerName)sJSON.eachLayer(function (layer) {
                        layer.hideLabel();
                    });
                }
            }""" % {"min": min, "max": max, "layerName": layerName}
        return scaleDependentLabel
    else:
        return ""


def scaleDependentScript(layers):
    scaleDependent = """
        map.on("zoomend", function(e) {"""
    scaleDependent += layers
    scaleDependent += """
        });"""
    scaleDependent += layers
    return scaleDependent


def openScript():
    openScript = """
        <script>"""
    return openScript


def highlightScript(highlight, popupsOnHover, highlightFill):
    highlightScript = """
        var highlightLayer;
        function highlightFeature(e) {
            highlightLayer = e.target;"""
    if highlight:
        highlightScript += """

            if (e.target.feature.geometry.type === 'LineString') {
              highlightLayer.setStyle({
                color: '""" + highlightFill + """',
              });
            } else {
              highlightLayer.setStyle({
                fillColor: '""" + highlightFill + """',
                fillOpacity: 1
              });
            }"""
    if popupsOnHover:
        highlightScript += """
            highlightLayer.openPopup();"""
    highlightScript += """
        }"""
    return highlightScript


def crsScript(crsAuthId, crsProj4):
    crs = """
        var crs = new L.Proj.CRS('{crsAuthId}', '{crsProj4}', {{
            resolutions: [2800, 1400, 700, 350, """.format(crsAuthId=crsAuthId,
                                                           crsProj4=crsProj4)
    crs += """175, 84, 42, 21, 11.2, 5.6, 2.8, 1.4, 0.7, 0.35, 0.14, 0.07],
        });"""
    return crs


def mapScript(extent, matchCRS, crsAuthId, measure, maxZoom, minZoom, bounds,
              locate):
    map = """
        L.ImageOverlay.include({
            getBounds: function () {
                return this._bounds;
            }
        });
        var map = L.map('map', {"""
    if matchCRS and crsAuthId != 'EPSG:4326':
        map += """
            crs: crs,
            continuousWorld: false,
            worldCopyJump: false, """
    if measure != "None":
        map += """
            measureControl:true,"""
    map += """
            zoomControl:true, maxZoom:""" + unicode(maxZoom)
    map += """, minZoom:""" + unicode(minZoom) + """
        })"""
    if extent == "Canvas extent":
        map += """.fitBounds(""" + bounds + """);"""
    map += """
        var hash = new L.Hash(map);"""
    map += """
        map.attributionControl.addAttribution('<a href="""
    map += """"https://github.com/tomchadwin/qgis2web" target="_blank">"""
    map += "qgis2web</a>');"
    if locate:
        map += """
        L.control.locate().addTo(map);"""
    return map


def featureGroupsScript():
    featureGroups = """
        var feature_group = new L.featureGroup([]);
        var bounds_group = new L.featureGroup([]);
        var raster_group = new L.LayerGroup([]);"""
    return featureGroups


def basemapsScript(basemapList, maxZoom):
    basemaps = ""
    for count, basemap in enumerate(basemapList):
        bmText = basemapAddresses[basemap.text()]
        bmAttr = basemapAttributions[basemap.text()]
        basemaps += """
        var basemap{count} = L.tileLayer('{basemap}', {{
            attribution: '{attribution}',
            maxZoom: {maxZoom}
        }});
        basemap{count}.addTo(map);""".format(count=count, basemap=bmText,
                                             attribution=bmAttr,
                                             maxZoom=maxZoom)
    return basemaps


def layerOrderScript(extent, restrictToExtent):
    layerOrder = """
        function setBounds() {"""
    if extent == 'Fit to layers extent':
        layerOrder += """
            if (bounds_group.getLayers().length) {
                map.fitBounds(bounds_group.getBounds());
            }"""
    if restrictToExtent:
        layerOrder += """
            map.setMaxBounds(map.getBounds());"""
    layerOrder += """
        }
        function geoJson2heat(geojson, weight) {
          return geojson.features.map(function(feature) {
            return [
              feature.geometry.coordinates[1],
              feature.geometry.coordinates[0],
              feature.properties[weight]
            ];
          });
        }"""
    return layerOrder


def popFuncsScript(table):
    table = table.encode("utf-8")
    popFuncs = """
            var popupContent = {table};
            layer.bindPopup(popupContent);""".format(table=table)
    return popFuncs


def popupScript(safeLayerName, popFuncs, highlight, popupsOnHover):
    popup = """
        function pop_{safeLayerName}""".format(safeLayerName=safeLayerName)
    popup += "(feature, layer) {"
    if highlight or popupsOnHover:
        popup += """
            layer.on({
                mouseout: function(e) {"""
        if highlight:
            popup += """
                    layer.setStyle(doStyle"""
            popup += """{safeLayerName}(feature));
""".format(safeLayerName=safeLayerName)
        if popupsOnHover:
            popup += """
                    if (typeof layer.closePopup == 'function') {
                        layer.closePopup();
                    } else {
                        layer.eachLayer(function(feature){
                            feature.closePopup()
                        });
                    }"""
        popup += """
                },
                mouseover: highlightFeature,
            });"""
    if "<table></table>" not in popFuncs:
        popup += """{popFuncs}
        """.format(popFuncs=popFuncs)
    popup += "}"
    return popup


def svgScript(safeLayerName, symbolLayer, outputFolder,
              rot, labeltext, zIndex):
    slPath = symbolLayer.path()
    zIndex = zIndex + 600
    shutil.copyfile(slPath, os.path.join(outputFolder, "markers",
                                         os.path.basename(slPath)))
    svg = """
        var svg{safeLayerName} = L.icon({{
            iconUrl: 'markers/{svgPath}',
            iconSize: [{size}, {size}], // size of the icon
        }});

        map.createPane('pane_{safeLayerName}');
        map.getPane('pane_{safeLayerName}').style.zIndex = {zIndex};
        function doStyle{safeLayerName}(feature) {{
            return {{
                pane: 'pane_{safeLayerName}',
                icon: svg{safeLayerName},
                rotationAngle: {rot},
                rotationOrigin: 'center center'
            }}
        }}
        function doPointToLayer{safeLayerName}(feature, latlng) {{
            return L.marker(latlng, doStyle{safeLayerName}(feature)){labeltext}
        }}""".format(safeLayerName=safeLayerName,
                     svgPath=os.path.basename(symbolLayer.path()),
                     size=symbolLayer.size() * 3.8, zIndex=zIndex, rot=rot,
                     labeltext=labeltext)
    return svg


def iconLegend(symbol, catr, outputProjectFileName, layerName, catLegend):
    legendIcon = QgsSymbolLayerV2Utils.symbolPreviewPixmap(symbol,
                                                           QSize(16, 16))
    safeLabel = re.sub('[\W_]+', '', catr.label())
    legendIcon.save(os.path.join(outputProjectFileName, "legend",
                                 layerName + "_" + safeLabel + ".png"))
    catLegend += """&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<img src="legend/"""
    catLegend += layerName + "_" + safeLabel + """.png" /> """
    catLegend += catr.label() + "<br />"
    return catLegend


def pointStyleLabelScript(safeLayerName, radius, borderWidth, borderStyle,
                          colorName, borderColor, borderOpacity, opacity,
                          labeltext, zIndex):
    radius = float(radius) * 2
    zIndex = zIndex + 600
    (dashArray, capString, joinString) = getLineStyle(borderStyle, borderWidth,
                                                      0, 0)
    pointStyleLabel = """
        map.createPane('pane_{safeLayerName}');
        map.getPane('pane_{safeLayerName}').style.zIndex = {zIndex};
        function doStyle{safeLayerName}() {{
            return {{
                pane: 'pane_{safeLayerName}',
                radius: {radius},
                fillColor: '{colorName}',
                color: '{borderColor}',
                weight: {borderWidth},
                opacity: {borderOpacity},
                dashArray: '{dashArray}',
                lineCap: '{capString}',
                lineJoin: '{joinString}',
                fillOpacity: {opacity}
            }}
        }}
        function doPointToLayer{safeLayerName}(feature, latlng) {{
            return L.circleMarker(latlng, doStyle{safeLayerName}()){labeltext}
        }}""".format(safeLayerName=safeLayerName, zIndex=zIndex, radius=radius,
                     colorName=colorName, borderColor=borderColor,
                     borderWidth=borderWidth * 4,
                     borderOpacity=borderOpacity if borderStyle != 0 else 0,
                     dashArray=dashArray, capString=capString,
                     joinString=joinString, opacity=opacity,
                     labeltext=labeltext)
    return pointStyleLabel


def pointToLayerScript(safeLayerName):
    pointToLayer = """
            pointToLayer: doPointToLayer""" + safeLayerName
    return pointToLayer


def wfsScript(scriptTag):
    wfs = """
        <script src='{scriptTag}'></script>""".format(scriptTag=scriptTag)
    return wfs


def jsonPointScript(pointStyleLabel, safeLayerName, pointToLayer, usedFields):
    jsonPoint = pointStyleLabel
    if usedFields != 0:
        jsonPoint += """
        var json_{safeLayerName}JSON = new L.geoJson(json_{safeLayerName}, {{
            pane: 'pane_{safeLayerName}',
            onEachFeature: pop_{safeLayerName},{pointToLayer}
            }});""".format(safeLayerName=safeLayerName,
                           pointToLayer=pointToLayer)
    else:
        jsonPoint += """
        var json_{safeLayerName}JSON = new L.geoJson(json_{safeLayerName}, {{
            pane: 'pane_{safeLayerName}',
            {pointToLayer}
            }});""".format(safeLayerName=safeLayerName,
                           pointToLayer=pointToLayer)
    return jsonPoint


def clusterScript(safeLayerName):
    cluster = """
        var cluster_group"""
    cluster += "{safeLayerName}JSON = ".format(safeLayerName=safeLayerName)
    cluster += """new L.MarkerClusterGroup({{showCoverageOnHover: false}});
        cluster_group{safeLayerName}JSON""".format(safeLayerName=safeLayerName)
    cluster += """.addLayer(json_{safeLayerName}JSON);
""".format(safeLayerName=safeLayerName)
    return cluster


def categorizedPointStylesScript(symbol, opacity, borderOpacity):
    symbolLayer = symbol.symbolLayer(0)
    try:
        (dashArray, capString,
         joinString) = getLineStyle(symbolLayer.outlineStyle(),
                                    symbolLayer.outlineWidth(), 0, 0)
        if symbolLayer.outlineStyle() == 0:
            borderOpacity = 0
        borderColor = symbolLayer.borderColor().name()
        borderWidth = symbolLayer.outlineWidth() * 4
    except:
        dashArray = ""
        capString = ""
        joinString = ""
        borderOpacity = 1
        borderColor = ""
        borderWidth = 0
    styleValues = """
                    radius: {radius},
                    fillColor: '{fillColor}',
                    color: '{color}',
                    weight: {borderWidth},
                    opacity: {borderOpacity},
                    dashArray: '{dashArray}',
                    fillOpacity: '{opacity}',
                }};
                break;""".format(radius=symbol.size() * 2,
                                 fillColor=symbol.color().name(),
                                 color=borderColor,
                                 borderWidth=borderWidth,
                                 borderOpacity=borderOpacity,
                                 dashArray=dashArray, opacity=opacity)
    return styleValues


def simpleLineStyleScript(radius, colorName, penStyle, capString, joinString,
                          opacity):
    lineStyle = """
            return {{
                weight: {radius},
                color: '{colorName}',
                dashArray: '{penStyle}',
                lineCap: '{capString}',
                lineJoin: '{joinString}',
                opacity: {opacity}
            }};""".format(radius=radius * 4, colorName=colorName,
                          penStyle=penStyle, capString=capString,
                          joinString=joinString, opacity=opacity)
    return lineStyle


def singlePolyStyleScript(radius, colorName, borderOpacity, fillColor,
                          penStyle, capString, joinString, opacity):
    polyStyle = """
            return {{
                weight: {radius},
                color: '{colorName}',
                fillColor: '{fillColor}',
                dashArray: '{penStyle}',
                lineCap: '{capString}',
                lineJoin: '{joinString}',
                opacity: {borderOpacity},
                fillOpacity: {opacity}
            }};""".format(radius=radius * 4, colorName=colorName,
                          fillColor=fillColor, penStyle=penStyle,
                          capString=capString, joinString=joinString,
                          borderOpacity=borderOpacity, opacity=opacity)
    return polyStyle


def nonPointStylePopupsScript(safeLayerName):
    nonPointStylePopups = """
\t\t\tstyle: doStyle{safeLayerName}""".format(safeLayerName=safeLayerName)
    return nonPointStylePopups


def nonPointStyleFunctionScript(safeLayerName, lineStyle):
    nonPointStyleFunction = """
        function doStyle{safeLayerName}(feature) {{{lineStyle}
        }}""".format(safeLayerName=safeLayerName, lineStyle=lineStyle)
    return nonPointStyleFunction


def categoryScript(layerName, valueAttr):
    category = """
        function doStyle{layerName}(feature) {{
\t\t\tswitch (feature.properties['{valueAttr}']) {{""".format(
                layerName=layerName,
                valueAttr=valueAttr)
    return category


def defaultCategoryScript():
    defaultCategory = """
                default:
                    return {"""
    return defaultCategory


def eachCategoryScript(catValue):
    if isinstance(catValue, basestring):
        valQuote = "'"
    else:
        valQuote = ""
    eachCategory = """
                case """ + valQuote + unicode(catValue).replace("'", "\\'")
    eachCategory += valQuote + """:
                    return {"""
    return eachCategory


def endCategoryScript():
    endCategory = """
            }
        }"""
    return endCategory


def categorizedPointWFSscript(layerName, labeltext):
    categorizedPointWFS = """
        function doPointToLayer{layerName}(feature, latlng) {{
            return L.circleMarker(latlng, doStyle{layerName}""".format(
        layerName=layerName)
    categorizedPointWFS += """(feature)){labeltext}
        }}""".format(labeltext=labeltext)
    return categorizedPointWFS


def categorizedPointJSONscript(safeLayerName, labeltext, usedFields, zIndex):
    zIndex = zIndex + 600
    if usedFields != 0:
        categorizedPointJSON = """
        map.createPane('pane_{sln}');
        map.getPane('pane_{sln}').style.zIndex = {zIndex};
        var json_{sln}JSON = new L.geoJson(json_{sln}, {{
            pane: 'pane_{sln}',
            onEachFeature: pop_{sln},
            pointToLayer: function (feature, latlng) {{
                return L.circleMarker(latlng, """.format(sln=safeLayerName,
                                                         zIndex=zIndex)
        categorizedPointJSON += """doStyle{sln}(feature)){label}
            }}
        }});""".format(sln=safeLayerName, label=labeltext)
    else:
        categorizedPointJSON = """
        map.createPane('pane_{sln}');
        map.getPane('pane_{sln}').style.zIndex = {zIndex}
        var json_{sln}JSON = new L.geoJson(json_{sln}, {{
            pane: 'pane_{sln}',
            pointToLayer: function (feature, latlng) {{
                return L.circleMarker(latlng, """.format(sln=safeLayerName,
                                                         zIndex=zIndex)
        categorizedPointJSON += """doStyle{safeLayerName}(feature)){labeltext}
            }}
        }});""".format(safeLayerName=safeLayerName, labeltext=labeltext)
    return categorizedPointJSON


def categorizedLineStylesScript(symbol, opacity):
    sl = symbol.symbolLayer(0)
    (dashArray, capString,
     joinString) = getLineStyle(sl.penStyle(), symbol.width(),
                                sl.penCapStyle(), sl.penJoinStyle())
    categorizedLineStyles = """
                    color: '{color}',
                    weight: '{weight}',
                    dashArray: '{dashArray}',
                    lineCap: '{capString}',
                    lineJoin: '{joinString}',
                    opacity: '{opacity}',
                }};
                break;
""".format(color=symbol.color().name(), weight=symbol.width() * 4,
           dashArray=dashArray, capString=capString, joinString=joinString,
           opacity=opacity)
    return categorizedLineStyles


def categorizedNonPointStyleFunctionScript(layerName, popFuncs):
    categorizedNonPointStyleFunction = """
        style: doStyle{layerName}""".format(layerName=layerName)
    return categorizedNonPointStyleFunction


def categorizedPolygonStylesScript(symbol, opacity, borderOpacity):
    sl = symbol.symbolLayer(0)
    try:
        capStyle = sl.penCapStyle()
        joinStyle = sl.penJoinStyle()
    except:
        capStyle = 0
        joinStyle = 0
    (dashArray, capString,
     joinString) = getLineStyle(sl.borderStyle(), sl.borderWidth(), capStyle,
                                joinStyle)
    if sl.brushStyle() == 0:
        fillColor = "none"
    else:
        fillColor = symbol.color().name()
    if sl.borderStyle() == 0:
        color = "none"
    else:
        color = sl.borderColor().name()
    categorizedPolygonStyles = """
                    weight: '{weight}',
                    fillColor: '{fillColor}',
                    color: '{color}',
                    dashArray: '{dashArray}',
                    lineCap: '{capString}',
                    lineJoin: '{joinString}',
                    opacity: '{borderOpacity}',
                    fillOpacity: '{opacity}',
                }};
                break;
""".format(weight=sl.borderWidth() * 4, fillColor=fillColor, color=color,
           dashArray=dashArray, capString=capString, joinString=joinString,
           borderOpacity=borderOpacity, opacity=opacity)
    return categorizedPolygonStyles


def graduatedStyleScript(layerName):
    graduatedStyle = """
        function doStyle{layerName}(feature) {{""".format(layerName=layerName)
    return graduatedStyle


def rangeStartScript(valueAttr, r):
    rangeStart = """
        if (feature.properties['{valueAttr}'] >= {lowerValue} &&
                feature.properties['{valueAttr}'] <= {upperValue}) {{
""".format(valueAttr=valueAttr, lowerValue=r.lowerValue(),
           upperValue=r.upperValue())
    return rangeStart


def graduatedPointStylesScript(valueAttr, r, symbol, opacity, borderOpacity):
    sl = symbol.symbolLayer(0)
    (dashArray, capString,
     joinString) = getLineStyle(sl.outlineStyle(), sl.outlineWidth(), 0, 0)
    graduatedPointStyles = rangeStartScript(valueAttr, r)
    graduatedPointStyles += """
            return {{
                radius: {radius},
                fillColor: '{fillColor}',
                color: '{color}',
                weight: {lineWeight},
                fillOpacity: '{opacity}',
                opacity: '{borderOpacity}',
                dashArray: '{dashArray}'
            }}
        }}
""".format(radius=symbol.size() * 2, fillColor=symbol.color().name(),
           color=sl.borderColor().name(), lineWeight=sl.outlineWidth() * 4,
           opacity=opacity, borderOpacity=borderOpacity, dashArray=dashArray)
    return graduatedPointStyles


def graduatedLineStylesScript(valueAttr, r, symbol, opacity):
    sl = symbol.symbolLayer(0)
    (dashArray, capString,
     joinString) = getLineStyle(sl.penStyle(), symbol.width(),
                                sl.penCapStyle(), sl.penJoinStyle())
    graduatedLineStyles = rangeStartScript(valueAttr, r)
    graduatedLineStyles += """
            return {{
                color: '{color}',
                weight: '{weight}',
                dashArray: '{dashArray}',
                lineCap: '{capString}',
                lineJoin: '{joinString}',
                opacity: '{opacity}',
            }}
        }}""".format(color=sl.color().name(),
                     weight=symbol.width() * 4, dashArray=dashArray,
                     capString=capString, joinString=joinString,
                     opacity=opacity)
    return graduatedLineStyles


def graduatedPolygonStylesScript(valueAttr, r, symbol, opacity, borderOpacity):
    sl = symbol.symbolLayer(0)
    if sl.borderStyle() == 0:
        weight = "0"
        dashArray = "0"
        capString = ""
        joinString = ""
    else:
        try:
            capStyle = sl.penCapStyle()
            joinStyle = sl.penJoinStyle()
        except:
            capStyle = 0
            joinStyle = 0
        weight = sl.borderWidth() * 4
        (dashArray, capString,
         joinString) = getLineStyle(sl.borderStyle(), sl.borderWidth(),
                                    capStyle, joinStyle)
    if sl.brushStyle() == 0:
        fillColor = "0"
    else:
        fillColor = symbol.color().name()
    graduatedPolygonStyles = rangeStartScript(valueAttr, r)
    graduatedPolygonStyles += """
            return {{
                color: '{color}',
                weight: '{weight}',
                dashArray: '{dashArray}',
                lineCap: '{capString}',
                lineJoin: '{joinString}',
                fillColor: '{fillColor}',
                opacity: '{borderOpacity}',
                fillOpacity: '{opacity}',
            }}
        }}""".format(color=sl.borderColor().name(), weight=weight,
                     dashArray=dashArray, capString=capString,
                     joinString=joinString, fillColor=fillColor,
                     borderOpacity=borderOpacity, opacity=opacity)
    return graduatedPolygonStyles


def endGraduatedStyleScript():
    endGraduatedStyle = """
        }"""
    return endGraduatedStyle


def wmsScript(i, safeLayerName):
    d = parse_qs(i.source())
    wms_url = d['url'][0]
    wms_layer = d['layers'][0]
    wms_format = d['format'][0]
    wms_crs = d['crs'][0]
    wms = """
        var overlay_{safeLayerName} = L.tileLayer.wms('{wms_url}', {{
            layers: '{wms_layer}',
            format: '{wms_format}',
            transparent: true,
            continuousWorld : true,
        }});""".format(safeLayerName=safeLayerName, wms_url=wms_url,
                       wms_layer=wms_layer, wms_format=wms_format)
    return wms


def rasterScript(i, safeLayerName):
    out_raster = 'data/' + 'json_' + safeLayerName + '.png'
    pt2 = i.extent()
    crsSrc = i.crs()
    crsDest = QgsCoordinateReferenceSystem(4326)
    xform = QgsCoordinateTransform(crsSrc, crsDest)
    pt3 = xform.transform(pt2)
    bbox_canvas2 = [pt3.yMinimum(), pt3.yMaximum(),
                    pt3.xMinimum(), pt3.xMaximum()]
    bounds = '[[' + unicode(pt3.yMinimum()) + ','
    bounds += unicode(pt3.xMinimum()) + '],['
    bounds += unicode(pt3.yMaximum()) + ','
    bounds += unicode(pt3.xMaximum()) + ']]'
    raster = """
        var img_{safeLayerName} = '{out_raster}';
        var img_bounds_{safeLayerName} = {bounds};
        var overlay_{safeLayerName} = """.format(safeLayerName=safeLayerName,
                                                 out_raster=out_raster,
                                                 bounds=bounds)
    raster += "new L.imageOverlay(img_"
    raster += """{safeLayerName}, img_bounds_{safeLayerName});
        bounds_group.addLayer(overlay_{safeLayerName});""".format(
                safeLayerName=safeLayerName)
    return raster


def titleSubScript(webmap_head):
    titleSub = """
        var title = new L.Control();
        title.onAdd = function (map) {
            this._div = L.DomUtil.create('div', 'info');
            this.update();
            return this._div;
        };
        title.update = function () {
            this._div.innerHTML = '<h2>"""
    titleSub += webmap_head.encode('utf-8').replace("'", "\\'") + """</h2>';
        };
        title.addTo(map);"""
    return titleSub


def addLayersList(basemapList, matchCRS, layer_list, cluster, legends):
    if len(basemapList) == 0 or matchCRS:
        controlStart = """
        var baseMaps = {};"""
    else:
        comma = ""
        controlStart = """
        var baseMaps = {"""
        for count, basemap in enumerate(basemapList):
            controlStart += comma + "'" + unicode(basemap.text())
            controlStart += "': basemap" + unicode(count)
            comma = ", "
        controlStart += "};"
    controlStart += """
        L.control.layers(baseMaps,{"""
    layersList = controlStart

    lyrCount = len(layer_list) - 1
    for i, clustered in zip(reversed(layer_list), reversed(cluster)):
        try:
            rawLayerName = i.name()
            safeLayerName = (re.sub('[\W_]+', '', rawLayerName) +
                             unicode(lyrCount))
            lyrCount -= 1
            if i.type() == QgsMapLayer.VectorLayer:
                testDump = i.rendererV2().dump()
                if (clustered and
                        i.geometryType() == QGis.Point):
                    new_layer = "'" + legends[safeLayerName] + "'"
                    new_layer += ": cluster_group""" + safeLayerName + "JSON,"
                else:
                    new_layer = "'" + legends[safeLayerName] + "':"
                    new_layer += " json_" + safeLayerName + "JSON,"
                layersList += new_layer
            elif i.type() == QgsMapLayer.RasterLayer:
                new_layer = '"' + rawLayerName + '"' + ": overlay_"
                new_layer += safeLayerName + ""","""
                layersList += new_layer
        except:
            pass
    controlEnd = "},{collapsed:false}).addTo(map);"
    layersList += controlEnd
    return layersList


def scaleBar():
        scaleBar = """
        L.control.scale({options: {position: 'bottomleft', """
        scaleBar += "maxWidth: 100, metric: true, imperial: false, "
        scaleBar += "updateWhenIdle: false}}).addTo(map);"
        return scaleBar


def addressSearchScript():
    addressSearch = """
        var osmGeocoder = new L.Control.OSMGeocoder({
            collapsed: false,
            position: 'topright',
            text: 'Search',
        });
        osmGeocoder.addTo(map);"""
    return addressSearch


def endHTMLscript(wfsLayers, layerSearch, labels):
    endHTML = ""
    if wfsLayers == "":
        endHTML += """
        setBounds();"""
        endHTML += labels
    if layerSearch != "None":
        searchVals = layerSearch.split(": ")
        endHTML += """
        map.addControl(new L.Control.Search({{
            layer: feature_group,
            initial: false,
            hideMarkerOnCollapse: true,
            propertyName: '{field}'}}));""".format(field=searchVals[1])
    endHTML += """
        </script>{wfsLayers}""".format(wfsLayers=wfsLayers)
    return endHTML


def getLineStyle(penType, lineWidth, penCap, penJoin):
    if lineWidth > 1:
        dash = lineWidth * 10
        dot = lineWidth * 1
        gap = lineWidth * 5
    else:
        dash = 10
        dot = 1
        gap = 5
    if penType > 1:
        if penType == 2:
            penStyle = [dash, gap]
        elif penType == 3:
            penStyle = [dot, gap]
        elif penType == 4:
            penStyle = [dash, gap, dot, gap]
        elif penType == 5:
            penStyle = [dash, gap, dot, gap, dot, gap]
        else:
            penStyle = ""
        penStyle = ','.join(map(str, penStyle))
    else:
        penStyle = ""
    capString = "square"
    if penCap == 0:
        capString = "butt"
    if penCap == 32:
        capString = "round"
    joinString = "bevel"
    if penJoin == 0:
        joinString = "miter"
    if penJoin == 128:
        joinString = "round"
    return penStyle, capString, joinString
