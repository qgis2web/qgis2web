import os
import shutil
from utils import scaleToZoom
from basemaps import basemapLeaflet, basemapAttributions

basemapAddresses = basemapLeaflet()
basemapAttributions = basemapAttributions()


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
            highlightLayer.setStyle({
                fillColor: '""" + highlightFill + """',
                fillOpacity: 1
            });

            if (!L.Browser.ie && !L.Browser.opera) {
                highlightLayer.bringToFront();
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


def mapScript(extent, matchCRS, crsAuthId, measure, maxZoom, minZoom, bounds):
    map = """
        var map = L.map('map', {"""
    if matchCRS and crsAuthId != 'EPSG:4326':
        map += """
            crs: crs,
            continuousWorld: false,
            worldCopyJump: false, """
    if measure:
        map += """
            measureControl:true,"""
    map += """
            zoomControl:true, maxZoom:""" + unicode(maxZoom)
    map += """, minZoom:""" + unicode(minZoom) + """
        })"""
    if extent == "Canvas extent":
        map += """.fitBounds(""" + bounds + """);"""
    map += """
        var hash = new L.Hash(map);
        var additional_attrib = '<a href="https://github.com/tomchadwin/"""
    map += """qgis2web" target ="_blank">qgis2web</a>';"""
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
        bmName = basemap.text()
        bmAddr = basemapAddresses[bmName]
        bmAttr = basemapAttributions[bmName]
        basemaps += """
        var basemap{count} = L.tileLayer('{basemap}', {{
            attribution: additional_attrib + ' {attribution}',
            maxZoom: {maxZoom}
        }});
        basemap{count}.addTo(map);""".format(count=count, basemap=bmAddr,
                                             attribution=bmAttr,
                                             maxZoom=maxZoom)
    return basemaps


def layerOrderScript(extent):
    layerOrder = """
        var layerOrder = new Array();
        function stackLayers() {
            for (index = 0; index < layerOrder.length; index++) {
                map.removeLayer(layerOrder[index]);
                map.addLayer(layerOrder[index]);
            }"""
    if extent == 'Fit to layers extent':
        layerOrder += """
            map.fitBounds(bounds_group.getBounds());"""
    layerOrder += """
        }
        function restackLayers() {
            for (index = 0; index < layerOrder.length; index++) {
                layerOrder[index].bringToFront();
            }
        }
        map.on('overlayadd', restackLayers);
        layerControl = L.control.layers({},{},{collapsed:false});"""
    return layerOrder


def popFuncsScript(table):
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
    popup += """{popFuncs}
        }}""".format(popFuncs=popFuncs)
    return popup


def svgScript(safeLayerName, symbolLayer, outputFolder, labeltext):
    shutil.copyfile(symbolLayer.path(), os.path.join(outputFolder, "markers",
                                                     os.path.basename(
                                                        symbolLayer.path())))
    svg = """
        var svg{safeLayerName} = L.icon({{
            iconUrl: 'markers/{svgPath}',
            iconSize: [{size}, {size}], // size of the icon
        }});

        function doStyle{safeLayerName}() {{
            return {{
                icon: svg{safeLayerName}
            }}
        }}
        function doPointToLayer{safeLayerName}(feature, latlng) {{
            return L.marker(latlng, doStyle{safeLayerName}()){labeltext}
        }}""".format(safeLayerName=safeLayerName,
                     svgPath=os.path.basename(symbolLayer.path()),
                     size=symbolLayer.size() * 3.8,
                     labeltext=labeltext)
    return svg


def pointStyleLabelScript(safeLayerName, radius, borderWidth, borderStyle,
                          colorName, borderColor, borderOpacity,
                          opacity, labeltext):
    pointStyleLabel = """
        function doStyle{safeLayerName}() {{
            return {{
                radius: {radius},
                fillColor: '{colorName}',
                color: '{borderColor}',
                weight: {borderWidth},
                opacity: {borderOpacity},
                dashArray: '{dashArray}',
                fillOpacity: {opacity}
            }}
        }}
        function doPointToLayer{safeLayerName}(feature, latlng) {{
            return L.circleMarker(latlng, doStyle{safeLayerName}()){labeltext}
        }}""".format(safeLayerName=safeLayerName, radius=radius,
                     colorName=colorName, borderColor=borderColor,
                     borderWidth=borderWidth * 4,
                     borderOpacity=borderOpacity if borderStyle != 0 else 0,
                     dashArray=getLineStyle(borderStyle, borderWidth),
                     opacity=opacity, labeltext=labeltext)
    return pointStyleLabel


def pointToLayerScript(safeLayerName):
    pointToLayer = """
            pointToLayer: doPointToLayer""" + safeLayerName
    return pointToLayer


def doPointToLayerScript(safeLayerName, labeltext):
    return """
        function doPointToLayer{safeLayerName}(feature, latlng) {{
            return L.circleMarker(latlng, doStyle{safeLayerName}()){labeltext}
        }}""".format(safeLayerName=safeLayerName, labeltext=labeltext)


def wfsScript(scriptTag):
    wfs = """
        <script src='{scriptTag}'></script>""".format(scriptTag=scriptTag)
    return wfs


def jsonPointScript(pointStyleLabel, safeLayerName, pointToLayer, usedFields):
    jsonPoint = pointStyleLabel
    if usedFields != 0:
        jsonPoint += """
        var json_{safeLayerName}JSON = new L.geoJson(json_{safeLayerName}, {{
            onEachFeature: pop_{safeLayerName}, {pointToLayer}
            }});
        layerOrder[layerOrder.length]""".format(safeLayerName=safeLayerName,
                                                pointToLayer=pointToLayer)
        jsonPoint += """ = json_{safeLayerName}JSON;
""".format(safeLayerName=safeLayerName)
    else:
        jsonPoint += """
        var json_{safeLayerName}JSON = new L.geoJson(json_{safeLayerName}, {{
            {pointToLayer}
            }});
        layerOrder[layerOrder.length]""".format(safeLayerName=safeLayerName,
                                                pointToLayer=pointToLayer)
        jsonPoint += """ = json_{safeLayerName}JSON;
""".format(safeLayerName=safeLayerName)
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
    if symbolLayer.outlineStyle() == 0:
        borderOpacity = 0
    styleValues = """
                    radius: '{radius}',
                    fillColor: '{fillColor}',
                    color: '{color}',
                    weight: {borderWidth},
                    opacity: {borderOpacity},
                    dashArray: '{dashArray}',
                    fillOpacity: '{opacity}',
                }};
                break;""".format(radius=symbol.size(),
                                 fillColor=symbol.color().name(),
                                 color=symbolLayer.borderColor().name(),
                                 borderWidth=symbolLayer.outlineWidth() * 4,
                                 borderOpacity=borderOpacity,
                                 dashArray=getLineStyle(
                                     symbolLayer.outlineStyle(),
                                     symbolLayer.outlineWidth()),
                                 opacity=opacity)
    return styleValues


def simpleLineStyleScript(radius, colorName, penStyle, opacity):
    lineStyle = """
            return {{
                weight: {radius},
                color: '{colorName}',
                dashArray: '{penStyle}',
                opacity: {opacity}
            }};""".format(radius=radius * 4, colorName=colorName,
                          penStyle=penStyle, opacity=opacity)
    return lineStyle


def singlePolyStyleScript(radius, colorName, borderOpacity,
                          fillColor, penStyle, opacity):
    polyStyle = """
            return {{
                weight: {radius},
                color: '{colorName}',
                fillColor: '{fillColor}',
                dashArray: '{penStyle}',
                opacity: {borderOpacity},
                fillOpacity: {opacity}
            }};""".format(radius=radius, colorName=colorName,
                          fillColor=fillColor, penStyle=penStyle,
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
\t\t\tswitch (feature.properties.{valueAttr}) {{""".format(layerName=layerName,
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
                case """ + valQuote + unicode(catValue) + valQuote + """:
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


def categorizedPointJSONscript(safeLayerName, labeltext, usedFields):
    if usedFields != 0:
        categorizedPointJSON = """
        var json_{sln}JSON = new L.geoJson(json_{sln}, {{
            onEachFeature: pop_{sln},
            pointToLayer: function (feature, latlng) {{
                return L.circleMarker(latlng, """.format(sln=safeLayerName)
        categorizedPointJSON += """doStyle{sln}(feature)){label}
            }}
        }});
            layerOrder[layerOrder.length] = json_""".format(sln=safeLayerName,
                                                            label=labeltext)
        categorizedPointJSON += """{safeLayerName}JSON;
""".format(safeLayerName=safeLayerName)
    else:
        categorizedPointJSON = """
        var json_{sln}JSON = new L.geoJson(json_{sln}, {{
            pointToLayer: function (feature, latlng) {{
                return L.circleMarker(latlng, """.format(sln=safeLayerName)
        categorizedPointJSON += """doStyle{safeLayerName}(feature)){labeltext}
            }}
        }});
            layerOrder[layerOrder.length] = json_{safeLayerName}JSON;
""".format(safeLayerName=safeLayerName, labeltext=labeltext)
    return categorizedPointJSON


def categorizedLineStylesScript(symbol, opacity):
    categorizedLineStyles = """
                    color: '{color}',
                    weight: '{weight}',
                    dashArray: '{dashArray}',
                    opacity: '{opacity}',
                }};
                break;
""".format(color=symbol.color().name(),
           weight=symbol.width() * 4,
           dashArray=getLineStyle(symbol.symbolLayer(0).penStyle(),
                                  symbol.width()),
           opacity=opacity)
    return categorizedLineStyles


def categorizedNonPointStyleFunctionScript(layerName, popFuncs):
    categorizedNonPointStyleFunction = """
        style: doStyle{layerName},
        onEachFeature: function (feature, layer) {{{popFuncs}
        }}""".format(layerName=layerName, popFuncs=popFuncs)
    return categorizedNonPointStyleFunction


def categorizedPolygonStylesScript(symbol, opacity, borderOpacity):
    symbolLayer = symbol.symbolLayer(0)
    if symbolLayer.brushStyle() == 0:
        fillColor = "none"
    else:
        fillColor = symbol.color().name()
    if symbolLayer.borderStyle() == 0:
        color = "none"
    else:
        color = symbolLayer.borderColor().name()
    categorizedPolygonStyles = """
                    weight: '{weight}',
                    fillColor: '{fillColor}',
                    color: '{color}',
                    dashArray: '{dashArray}',
                    opacity: '{borderOpacity}',
                    fillOpacity: '{opacity}',
                }};
                break;
""".format(weight=symbolLayer.borderWidth() * 4,
           fillColor=fillColor,
           color=color,
           dashArray=getLineStyle(symbolLayer.borderStyle(),
                                  symbolLayer.borderWidth()),
           borderOpacity=borderOpacity,
           opacity=opacity)
    return categorizedPolygonStyles


def graduatedStyleScript(layerName):
    graduatedStyle = """
        function doStyle{layerName}(feature) {{""".format(layerName=layerName)
    return graduatedStyle


def rangeStartScript(valueAttr, r):
    rangeStart = """
        if (feature.properties.{valueAttr} >= {lowerValue} &&
                feature.properties.{valueAttr} <= {upperValue}) {{
""".format(valueAttr=valueAttr, lowerValue=r.lowerValue(),
           upperValue=r.upperValue())
    return rangeStart


def graduatedPointStylesScript(valueAttr, r, symbol, opacity, borderOpacity):
    graduatedPointStyles = rangeStartScript(valueAttr, r)
    graduatedPointStyles += """
            return {{
                radius: '{radius}',
                fillColor: '{fillColor}',
                color: '{color}',
                weight: {lineWeight},
                fillOpacity: '{opacity}',
                opacity: '{borderOpacity}',
                dashArray: '{dashArray}'
            }}
        }}
""".format(radius=symbol.size(),
           fillColor=symbol.color().name(),
           color=symbol.symbolLayer(0).borderColor().name(),
           lineWeight=symbol.symbolLayer(0).outlineWidth() * 4,
           opacity=opacity, borderOpacity=borderOpacity,
           dashArray=getLineStyle(symbol.symbolLayer(0).outlineStyle(),
                                  symbol.symbolLayer(0).outlineWidth()))
    return graduatedPointStyles


def graduatedLineStylesScript(valueAttr, r, symbol, opacity):
    graduatedLineStyles = rangeStartScript(valueAttr, r)
    graduatedLineStyles += """
            return {{
                color: '{color}',
                weight: '{weight}',
                dashArray: '{dashArray}',
                opacity: '{opacity}',
            }}
        }}""".format(color=symbol.symbolLayer(0).color().name(),
                     weight=symbol.width() * 4,
                     dashArray=getLineStyle(symbol.symbolLayer(0).penStyle(),
                                            symbol.width()),
                     opacity=opacity)
    return graduatedLineStyles


def graduatedPolygonStylesScript(valueAttr, r, symbol, opacity, borderOpacity):
    symbolLayer = symbol.symbolLayer(0)
    if symbolLayer.borderStyle() == 0:
        weight = "0"
    else:
        weight = symbolLayer.borderWidth() * 4
    if symbolLayer.borderStyle() == 0:
        dashArray = "0"
    else:
        dashArray = getLineStyle(symbolLayer.borderStyle(),
                                 symbolLayer.borderWidth())
    if symbolLayer.brushStyle() == 0:
        fillColor = "0"
    else:
        fillColor = symbol.color().name()
    graduatedPolygonStyles = rangeStartScript(valueAttr, r)
    graduatedPolygonStyles += """
            return {{
                color: '{color}',
                weight: '{weight}',
                dashArray: '{dashArray}',
                fillColor: '{fillColor}',
                opacity: '{borderOpacity}',
                fillOpacity: '{opacity}',
            }}
        }}""".format(color=symbolLayer.borderColor().name(), weight=weight,
                     dashArray=dashArray, fillColor=fillColor,
                     borderOpacity=borderOpacity, opacity=opacity)
    return graduatedPolygonStyles


def endGraduatedStyleScript():
    endGraduatedStyle = """
        }"""
    return endGraduatedStyle


def wmsScript(safeLayerName, wms_url, wms_layer, wms_format):
    wms = """
    var overlay_{safeLayerName} = L.tileLayer.wms('{wms_url}', {{
        layers: '{wms_layer}',
        format: '{wms_format}',
        transparent: true,
        continuousWorld : true,
    }});""".format(safeLayerName=safeLayerName, wms_url=wms_url,
                   wms_layer=wms_layer, wms_format=wms_format)
    return wms


def rasterScript(safeLayerName, out_raster_name, bounds):
    raster = """
    var img_{safeLayerName} = '{out_raster_name}';
    var img_bounds_{safeLayerName} = {bounds};
    var overlay_{safeLayerName} = """.format(safeLayerName=safeLayerName,
                                             out_raster_name=out_raster_name,
                                             bounds=bounds)
    raster += "new L.imageOverlay(img_"
    raster += """{safeLayerName}, img_bounds_{safeLayerName});
""".format(safeLayerName=safeLayerName, out_raster_name=out_raster_name,
           bounds=bounds)
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


def addressSearchScript():
    addressSearch = """
        var osmGeocoder = new L.Control.OSMGeocoder({
            collapsed: false,
            position: 'topright',
            text: 'Search',
        });
        osmGeocoder.addTo(map);"""
    return addressSearch


def locateScript():
    locate = """
        map.locate({setView: true, maxZoom: 16});
        function onLocationFound(e) {
            var radius = e.accuracy / 2;
            L.marker(e.latlng).addTo(map)
            .bindPopup("You are within " + radius + " meters from this point")
            .openPopup();
            L.circle(e.latlng, radius).addTo(map);
        }
        map.on('locationfound', onLocationFound);
        """
    return locate


def endHTMLscript(wfsLayers):
    endHTML = ""
    if wfsLayers == "":
        endHTML += """
        stackLayers();"""
    endHTML += """
    </script>{wfsLayers}""".format(wfsLayers=wfsLayers)
    return endHTML


def getLineStyle(penType, lineWidth):
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
    return penStyle
