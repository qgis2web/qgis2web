from utils import scaleToZoom


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
        console.log("show");
        //restackLayers();
    }} else if (map.getZoom() > {min} || map.getZoom() < {max}) {{
        feature_group.removeLayer(json_{layerName}JSON);
        console.log("hide");
        //restackLayers();
    }}""".format(min=scaleToZoom(min), max=scaleToZoom(max), layerName=layerName)
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


def crsScript(crsAuthId, crsProj4):
    crs = """
        var crs = new L.Proj.CRS('{crsAuthId}', '{crsProj4}', {{
            resolutions: [2800, 1400, 700, 350, 175, 84, 42, 21, 11.2, 5.6, 2.8, 1.4, 0.7, 0.35, 0.14, 0.07],
        }});""".format(crsAuthId=crsAuthId, crsProj4=crsProj4)
    return crs


def mapScript(extent, matchCRS, crsAuthId, measure, maxZoom, minZoom, bounds):
    map = """
        var map = L.map('map', {"""
    if extent == "Canvas extent" and matchCRS and crsAuthId != 'EPSG:4326':
        map += """
            crs: crs,
            continuousWorld: false,
            worldCopyJump: false, """
    if measure:
        map += """
            measureControl:true,"""
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
        var basemap = L.tileLayer('{basemap}', {{
            attribution: additional_attrib + ' {attribution}'
        }});
        basemap.addTo(map);""".format(basemap=basemap, attribution=attribution)
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


def popFuncsScript(table):
    popFuncs = """
            var popupContent = {table};
            layer.bindPopup(popupContent);""".format(table=table)
    return popFuncs


def popupScript(safeLayerName, popFuncs):
    popup = """
        function pop_{safeLayerName}(feature, layer) {{{popFuncs}
        }}""".format(safeLayerName=safeLayerName, popFuncs=popFuncs)
    return popup


def pointToLayerScript(radius, borderWidth, borderStyle, colorName, borderColor, borderOpacity, opacity, labeltext):
    pointToLayer = """
        pointToLayer: function (feature, latlng) {{
            return L.circleMarker(latlng, {{
                radius: {radius},
                fillColor: '{colorName}',
                color: '{borderColor}',
                weight: {borderWidth},
                opacity: {borderOpacity},
                dashArray: '{dashArray}',
                fillOpacity: {opacity}
            }}){labeltext}""".format(radius=radius,
                                     colorName=colorName,
                                     borderColor=borderColor,
                                     borderWidth=borderWidth * 4,
                                     borderOpacity=borderOpacity if borderStyle != 0 else 0,
                                     dashArray=getLineStyle(borderStyle, borderWidth),
                                     opacity=opacity,
                                     labeltext=labeltext)
    return pointToLayer


def pointStyleScript(pointToLayer, popFuncs):
    pointStyle = """{pointToLayer}
        }},
        onEachFeature: function (feature, layer) {{{popFuncs}
        }}""".format(pointToLayer=pointToLayer, popFuncs=popFuncs)
    return pointStyle


def wfsScript(scriptTag):
    wfs = """
        <script src='{scriptTag}'></script>""".format(scriptTag=scriptTag)
    return wfs


def jsonPointScript(safeLayerName, pointToLayer, usedFields):
    if usedFields != 0:
        jsonPoint = """
        var json_{safeLayerName}JSON = new L.geoJson(json_{safeLayerName}, {{
            onEachFeature: pop_{safeLayerName}, {pointToLayer}
            }}
        }});
    layerOrder[layerOrder.length] = json_{safeLayerName}JSON;""".format(safeLayerName=safeLayerName, pointToLayer=pointToLayer)
    else:
        jsonPoint = """
        var json_{safeLayerName}JSON = new L.geoJson(json_{safeLayerName}, {{
            {pointToLayer}
            }}
        }});
    layerOrder[layerOrder.length] = json_{safeLayerName}JSON;""".format(safeLayerName=safeLayerName, pointToLayer=pointToLayer)
    return jsonPoint


def clusterScript(safeLayerName):
    cluster = """
        var cluster_group{safeLayerName}JSON = new L.MarkerClusterGroup({{showCoverageOnHover: false}});
        cluster_group{safeLayerName}JSON.addLayer(json_{safeLayerName}JSON);""".format(safeLayerName=safeLayerName)
    return cluster


def categorizedPointStylesScript(symbol, opacity, borderOpacity):
    styleValues = """
                    radius: '{radius}',
                    fillColor: '{fillColor}',
                    color: '{color}',
                    weight: {borderWidth},
                    opacity: {borderOpacity},
                    dashArray: '{dashArray}',
                    fillOpacity: '{opacity}',
                }};
                break;""".format(radius=symbol.size() * 2,
                                 fillColor=symbol.color().name(),
                                 color=symbol.symbolLayer(0).borderColor().name(),
                                 borderWidth=symbol.symbolLayer(0).outlineWidth() * 4,
                                 borderOpacity=borderOpacity if symbol.symbolLayer(0).outlineStyle() != 0 else 0,
                                 dashArray=getLineStyle(symbol.symbolLayer(0).outlineStyle(), symbol.symbolLayer(0).outlineWidth()),
                                 opacity=opacity)
    return styleValues


def simpleLineStyleScript(radius, colorName, penStyle, opacity):
    lineStyle = """
            return {{
                weight: {radius},
                color: '{colorName}',
                dashArray: '{penStyle}',
                opacity: {opacity}
            }};""".format(radius=radius * 4,
                          colorName=colorName,
                          penStyle=penStyle,
                          opacity=opacity)
    return lineStyle


def singlePolyStyleScript(radius, colorName, borderOpacity, fillColor, penStyle, opacity):
    polyStyle = """
            return {{
                weight: {radius},
                color: '{colorName}',
                fillColor: '{fillColor}',
                dashArray: '{penStyle}',
                opacity: {borderOpacity},
                fillOpacity: {opacity}
            }};""".format(radius=radius,
                          colorName=colorName,
                          fillColor=fillColor,
                          penStyle=penStyle,
                          borderOpacity=borderOpacity,
                          opacity=opacity)
    return polyStyle


def nonPointStylePopupsScript(lineStyle, popFuncs):
    nonPointStylePopups = """
        style: function (feature) {{{lineStyle}
        }},
        onEachFeature: function (feature, layer) {{{popFuncs}
        }}""".format(lineStyle=lineStyle, popFuncs=popFuncs)
    return nonPointStylePopups


def nonPointStyleFunctionScript(safeLayerName, lineStyle):
    nonPointStyleFunction = """
        function doStyle{safeLayerName}(feature) {{{lineStyle}
        }}""".format(safeLayerName=safeLayerName, lineStyle=lineStyle)
    return nonPointStyleFunction


def categoryScript(layerName, valueAttr):
    category = """
        function doStyle{layerName}(feature) {{
            switch (feature.properties.{valueAttr}) {{""".format(layerName=layerName, valueAttr=valueAttr)
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


def categorizedPointWFSscript(layerName, labeltext, popFuncs):
    categorizedPointWFS = """
        pointToLayer: function (feature, latlng) {{
            return L.circleMarker(latlng, doStyle{layerName}(feature)){labeltext}
        }},
        onEachFeature: function (feature, layer) {{{popFuncs}
        }}""".format(layerName=layerName, labeltext=labeltext, popFuncs=popFuncs)
    return categorizedPointWFS


def categorizedPointJSONscript(safeLayerName, labeltext, usedFields):
    if usedFields != 0:
        categorizedPointJSON = """
        var json_{safeLayerName}JSON = new L.geoJson(json_{safeLayerName}, {{
            onEachFeature: pop_{safeLayerName},
            pointToLayer: function (feature, latlng) {{
                return L.circleMarker(latlng, doStyle{safeLayerName}(feature)){labeltext}
            }}
        }});
            layerOrder[layerOrder.length] = json_{safeLayerName}JSON;""".format(safeLayerName=safeLayerName, labeltext=labeltext)
    else:
        categorizedPointJSON = """
        var json_{safeLayerName}JSON = new L.geoJson(json_{safeLayerName}, {{
            pointToLayer: function (feature, latlng) {{
                return L.circleMarker(latlng, doStyle{safeLayerName}(feature)){labeltext}
            }}
        }});
            layerOrder[layerOrder.length] = json_{safeLayerName}JSON;""".format(safeLayerName=safeLayerName, labeltext=labeltext)
    return categorizedPointJSON


def categorizedLineStylesScript(symbol, opacity):
    categorizedLineStyles = """
                    color: '{color}',
                    weight: '{weight}',
                    dashArray: '{dashArray}',
                    opacity: '{opacity}',
                }};
                break;""".format(color=symbol.color().name(),
                                 weight=symbol.width() * 4,
                                 dashArray=getLineStyle(symbol.symbolLayer(0).penStyle(), symbol.width()),
                                 opacity=opacity)
    return categorizedLineStyles


def categorizedNonPointStyleFunctionScript(layerName, popFuncs):
    categorizedNonPointStyleFunction = """
        style: doStyle{layerName},
        onEachFeature: function (feature, layer) {{{popFuncs}
        }}""".format(layerName=layerName, popFuncs=popFuncs)
    return categorizedNonPointStyleFunction


def categorizedPolygonStylesScript(symbol, opacity, borderOpacity):
    categorizedPolygonStyles = """
                    weight: '{weight}',
                    fillColor: '{fillColor}',
                    color: '{color}',
                    dashArray: '{dashArray}',
                    opacity: '{borderOpacity}',
                    fillOpacity: '{opacity}',
                }};
                break;""".format(weight=symbol.symbolLayer(0).borderWidth() * 4,
                                 fillColor=symbol.color().name() if symbol.symbolLayer(0).brushStyle() != 0 else "none",
                                 color=symbol.symbolLayer(0).borderColor().name() if symbol.symbolLayer(0).borderStyle() != 0 else "none",
                                 dashArray=getLineStyle(symbol.symbolLayer(0).borderStyle(), symbol.symbolLayer(0).borderWidth()),
                                 borderOpacity=borderOpacity,
                                 opacity=opacity)
    return categorizedPolygonStyles


def graduatedStyleScript(layerName):
    graduatedStyle = """
        function doStyle{layerName}(feature) {{""".format(layerName=layerName)
    return graduatedStyle


def rangeStartScript(valueAttr, r):
    rangeStart = """
        if (feature.properties.{valueAttr} >= {lowerValue} && feature.properties.{valueAttr} <= {upperValue}) {{""".format(valueAttr=valueAttr, lowerValue=r.lowerValue(), upperValue=r.upperValue())
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
        }}""".format(radius=symbol.size() * 2,
                     fillColor=symbol.color().name(),
                     color=symbol.symbolLayer(0).borderColor().name(),
                     lineWeight=symbol.symbolLayer(0).outlineWidth() * 4,
                     opacity=opacity,
                     borderOpacity=borderOpacity,
                     dashArray=getLineStyle(symbol.symbolLayer(0).outlineStyle(), symbol.symbolLayer(0).outlineWidth()))
    return graduatedPointStyles


def graduatedLineStylesScript(valueAttr, r, categoryStr, symbol, opacity):
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
                     dashArray=getLineStyle(symbol.symbolLayer(0).penStyle(), symbol.width()),
                     opacity=opacity)
    return graduatedLineStyles


def graduatedPolygonStylesScript(valueAttr, r, symbol, opacity, borderOpacity):
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
        }}""".format(color=symbol.symbolLayer(0).borderColor().name(),
                     weight=symbol.symbolLayer(0).borderWidth() * 4 if symbol.symbolLayer(0).borderStyle() != 0 else "0",
                     dashArray=getLineStyle(symbol.symbolLayer(0).borderStyle(), symbol.symbolLayer(0).borderWidth() if symbol.symbolLayer(0).borderStyle() != 0 else "0"),
                     fillColor=symbol.color().name() if symbol.symbolLayer(0).brushStyle() != 0 else "none",
                     borderOpacity=borderOpacity,
                     opacity=opacity)
    return graduatedPolygonStyles


def endGraduatedStyleScript():
    endGraduatedStyle = """
        }"""
    return endGraduatedStyle


def customMarkerScript(safeLayerName, labeltext, usedFields):
    if usedFields != 0:
        customMarker = """
        var json_{safeLayerName}JSON = new L.geoJson(json_{safeLayerName}, {{
            onEachFeature: pop_{safeLayerName},
            pointToLayer: function (feature, latlng) {{
                return L.marker(latlng, {{
                    icon: L.icon({{
                        iconUrl: feature.properties.icon_exp,
                        iconSize:     [24, 24], // size of the icon change this to scale your icon (first coordinate is x, second y from the upper left corner of the icon)
                        iconAnchor:   [12, 12], // point of the icon which will correspond to marker's location (first coordinate is x, second y from the upper left corner of the icon)
                        popupAnchor:  [0, -14] // point from which the popup should open relative to the iconAnchor (first coordinate is x, second y from the upper left corner of the icon)
                    }})
                }}){labeltext}
            }}}}
        );""".format(safeLayerName=safeLayerName, labeltext=labeltext)
    else:
        customMarker = """
        var json_{safeLayerName}JSON = new L.geoJson(json_{safeLayerName}, {{
            pointToLayer: function (feature, latlng) {{
                return L.marker(latlng, {{
                    icon: L.icon({{
                        iconUrl: feature.properties.icon_exp,
                        iconSize:     [24, 24], // size of the icon change this to scale your icon (first coordinate is x, second y from the upper left corner of the icon)
                        iconAnchor:   [12, 12], // point of the icon which will correspond to marker's location (first coordinate is x, second y from the upper left corner of the icon)
                        popupAnchor:  [0, -14] // point from which the popup should open relative to the iconAnchor (first coordinate is x, second y from the upper left corner of the icon)
                    }})
                }}){labeltext}
            }}}}
        );""".format(safeLayerName=safeLayerName, labeltext=labeltext)
    return customMarker


def wmsScript(safeLayerName, wms_url, wms_layer, wms_format):
    wms = """
    var overlay_{safeLayerName} = L.tileLayer.wms('{wms_url}', {{
        layers: '{wms_layer}',
        format: '{wms_format}',
        transparent: true,
        continuousWorld : true,
    }});""".format(safeLayerName=safeLayerName,
                   wms_url=wms_url,
                   wms_layer=wms_layer,
                   wms_format=wms_format)
    return wms


def rasterScript(safeLayerName, out_raster_name, bounds):
    raster = """
    var img_{safeLayerName} = '{out_raster_name}';
    var img_bounds_{safeLayerName} = {bounds};
    var overlay_{safeLayerName} = new L.imageOverlay(img_{safeLayerName}, img_bounds_{safeLayerName});""".format(safeLayerName=safeLayerName, out_raster_name=out_raster_name, bounds=bounds)
    return raster


def titleSubScript(webmap_head, webmap_subhead):
    titleSub = """
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
            .bindPopup("You are within " + radius + " meters from this point").openPopup();
            L.circle(e.latlng, radius).addTo(map);
        }
        map.on('locationfound', onLocationFound);
        """
    return locate


def endHTMLscript(wfsLayers):
    endHTML = """
    </script>{wfsLayers}
</body>
</html>""".format(wfsLayers=wfsLayers)
    return endHTML


def getLineStyle(penType, lineWidth):
    dash = lineWidth * 10
    dot = lineWidth * 1
    gap = lineWidth * 5
    if penType > 1:
        if penType == 2:
            penStyle = [dash, gap]
        if penType == 3:
            penStyle = [dot, gap]
        if penType == 4:
            penStyle = [dash, gap, dot, gap]
        if penType == 5:
            penStyle = [dash, gap, dot, gap, dot, gap]
        penStyle = ','.join(map(str, penStyle))
    else:
        penStyle = ""
    return penStyle
