def jsonScript(layer):
    json = """
        <script src="data/json_{layer}.js\"></script>""".format(layer=layer)
    return json


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


def pointToLayerScript(radius_str, borderWidth_str, borderStyle, colorName, borderColor_str, borderOpacity_str, opacity_str, labeltext):
    pointToLayer = """
        pointToLayer: function (feature, latlng) {{
            return L.circleMarker(latlng, {{
                radius: {radius_str},
                fillColor: '{colorName}',
                color: '{borderColor_str}',
                weight: {borderWidth_str},
                opacity: {borderOpacity_str},
                dashArray: '{dashArray}',
                fillOpacity: {opacity_str}
            }}){labeltext}""".format(radius_str=radius_str,
                                     colorName=colorName,
                                     borderColor_str=borderColor_str,
                                     borderWidth_str=borderWidth_str * 4,
                                     borderOpacity_str=borderOpacity_str if borderStyle != 0 else 0,
                                     dashArray=getLineStyle(borderStyle, borderWidth_str),
                                     opacity_str=opacity_str,
                                     labeltext=labeltext)
    return pointToLayer


def pointStyleScript(pointToLayer_str, popFuncs):
    pointStyle = """{pointToLayer_str}
        }},
        onEachFeature: function (feature, layer) {{{popFuncs}
        }}""".format(pointToLayer_str=pointToLayer_str, popFuncs=popFuncs)
    return pointStyle


def wfsScript(scriptTag):
    wfs = """
        <script src='{scriptTag}'></script>""".format(scriptTag=scriptTag)
    return wfs


def jsonPointScript(safeLayerName, pointToLayer_str, usedFields):
    if usedFields != 0:
        jsonPoint = """
        var json_{safeLayerName}JSON = new L.geoJson(json_{safeLayerName}, {{
            onEachFeature: pop_{safeLayerName}, {pointToLayer_str}
            }}
        }});
    layerOrder[layerOrder.length] = json_{safeLayerName}JSON;""".format(safeLayerName=safeLayerName, pointToLayer_str=pointToLayer_str)
    else:
        jsonPoint = """
        var json_{safeLayerName}JSON = new L.geoJson(json_{safeLayerName}, {{
            {pointToLayer_str}
            }}
        }});
    layerOrder[layerOrder.length] = json_{safeLayerName}JSON;""".format(safeLayerName=safeLayerName, pointToLayer_str=pointToLayer_str)
    return jsonPoint


def clusterScript(safeLayerName):
    cluster = """
        var cluster_group{safeLayerName}JSON = new L.MarkerClusterGroup({{showCoverageOnHover: false}});
        cluster_group{safeLayerName}JSON.addLayer(json_{safeLayerName}JSON);""".format(safeLayerName=safeLayerName)
    return cluster


def categorizedPointStylesScript(symbol, opacity_str, borderOpacity_str):
    styleValues = """
                    radius: '{radius}',
                    fillColor: '{fillColor}',
                    color: '{color}',
                    weight: {borderWidth},
                    opacity: {borderOpacity_str},
                    dashArray: '{dashArray}',
                    fillOpacity: '{opacity_str}',
                }};
                break;""".format(
                    radius=symbol.size() * 2,
                    fillColor=symbol.color().name(),
                    color=symbol.symbolLayer(0).borderColor().name(),
                    borderWidth=symbol.symbolLayer(0).outlineWidth() * 4,
                    borderOpacity_str=borderOpacity_str if symbol.symbolLayer(0).outlineStyle() != 0 else 0,
                    dashArray=getLineStyle(symbol.symbolLayer(0).outlineStyle(), symbol.symbolLayer(0).outlineWidth()),
                    opacity_str=opacity_str)
    return styleValues


def simpleLineStyleScript(radius_str, colorName, penStyle_str, opacity_str):
    lineStyle = """
            return {{
                weight: {radius_str},
                color: '{colorName}',
                dashArray: '{penStyle_str}',
                opacity: {opacity_str}
            }};""".format(radius_str=radius_str * 4,
                         colorName=colorName,
                         penStyle_str=penStyle_str,
                         opacity_str=opacity_str)
    return lineStyle


def singlePolyStyleScript(radius_str, colorName, borderOpacity_str, fillColor, penStyle_str, opacity_str):
    polyStyle = """
            return {{
                weight: {radius_str},
                color: '{colorName}',
                fillColor: '{fillColor}',
                dashArray: '{penStyle_str}',
                opacity: {borderOpacity_str},
                fillOpacity: {opacity_str}
            }};""".format(radius_str=radius_str,
                         colorName=colorName,
                         fillColor=fillColor,
                         penStyle_str=penStyle_str,
                         borderOpacity_str=borderOpacity_str,
                         opacity_str=opacity_str)
    return polyStyle


def nonPointStylePopupsScript(lineStyle_str, popFuncs):
    nonPointStylePopups = """
        style: function (feature) {{{lineStyle_str}
        }},
        onEachFeature: function (feature, layer) {{{popFuncs}
        }}""".format(lineStyle_str=lineStyle_str, popFuncs=popFuncs)
    return nonPointStylePopups


def nonPointStyleFunctionScript(safeLayerName, lineStyle_str):
    nonPointStyleFunction = """
    function doStyle{safeLayerName}(feature) {{{lineStyle_str}
    }}""".format(safeLayerName=safeLayerName, lineStyle_str=lineStyle_str)
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


def categorizedLineStylesScript(symbol, opacity_str):
    categorizedLineStyles = """
                    color: '{color}',
                    weight: '{weight}',
                    dashArray: '{dashArray}',
                    opacity: '{opacity_str}',
                }};
                break;""".format(
                    color=symbol.color().name(),
                    weight=symbol.width() * 4,
                    dashArray=getLineStyle(symbol.symbolLayer(0).penStyle(), symbol.width()),
                    opacity_str=opacity_str)
    return categorizedLineStyles


def categorizedNonPointStyleFunctionScript(layerName, popFuncs):
    categorizedNonPointStyleFunction = """
        style: doStyle{layerName},
        onEachFeature: function (feature, layer) {{{popFuncs}
        }}""".format(layerName=layerName, popFuncs=popFuncs)
    return categorizedNonPointStyleFunction


def categorizedPolygonStylesScript(symbol, radius_str, opacity_str, borderOpacity_str):
    categorizedPolygonStyles = """
                    weight: '{weight}',
                    fillColor: '{fillColor}',
                    color: '{color}',
                    dashArray: '{dashArray}',
                    opacity: '{borderOpacity_str}',
                    fillOpacity: '{opacity_str}',
                }};
                break;""".format(
                    weight=symbol.symbolLayer(0).borderWidth() * 4,
                    fillColor=symbol.color().name() if symbol.symbolLayer(0).brushStyle() != 0 else "none",
                    color=symbol.symbolLayer(0).borderColor().name() if symbol.symbolLayer(0).borderStyle() != 0 else "none",
                    radius_str=radius_str,
                    dashArray=getLineStyle(symbol.symbolLayer(0).borderStyle(), symbol.symbolLayer(0).borderWidth()),
                    borderOpacity_str=borderOpacity_str,
                    opacity_str=opacity_str)
    return categorizedPolygonStyles


def graduatedStyleScript(layerName):
    graduatedStyle = """
    function doStyle{layerName}(feature) {{""".format(layerName=layerName)
    return graduatedStyle


def rangeStartScript(valueAttr, r):
    rangeStart = """
        if (feature.properties.{valueAttr} >= {lowerValue} && feature.properties.{valueAttr} <= {upperValue}) {{""".format(valueAttr=valueAttr, lowerValue=r.lowerValue(), upperValue=r.upperValue())
    return rangeStart


def graduatedPointStylesScript(valueAttr, r, symbol, opacity_str, borderOpacity_str):
    graduatedPointStyles = rangeStartScript(valueAttr, r)
    graduatedPointStyles += """
            return {{
                radius: '{radius}',
                fillColor: '{fillColor}',
                color: '{color}',
                weight: {lineWeight},
                fillOpacity: '{opacity_str}',
                opacity: '{borderOpacity_str}',
                dashArray: '{dashArray}'
            }}
        }}""".format(
            radius=symbol.size() * 2,
            fillColor=symbol.color().name(),
            color=symbol.symbolLayer(0).borderColor().name(),
            lineWeight=symbol.symbolLayer(0).outlineWidth() * 4,
            opacity_str=opacity_str,
            borderOpacity_str=borderOpacity_str,
            dashArray=getLineStyle(symbol.symbolLayer(0).outlineStyle(), symbol.symbolLayer(0).outlineWidth()))
    return graduatedPointStyles


def graduatedLineStylesScript(valueAttr, r, categoryStr, symbol, opacity_str):
    graduatedLineStyles = rangeStartScript(valueAttr, r)
    graduatedLineStyles += """
            return {{
                color: '{color}',
                weight: '{weight}',
                dashArray: '{dashArray}',
                opacity: '{opacity_str}',
            }}
        }}""".format(
            color=symbol.symbolLayer(0).color().name(),
            weight=symbol.width() * 4,
            dashArray=getLineStyle(symbol.symbolLayer(0).penStyle(), symbol.width()),
            opacity_str=opacity_str)
    return graduatedLineStyles


def graduatedPolygonStylesScript(valueAttr, r, symbol, opacity_str, borderOpacity_str):
    graduatedPolygonStyles = rangeStartScript(valueAttr, r)
    graduatedPolygonStyles += """
            return {{
                color: '{color}',
                weight: '{weight}',
                dashArray: '{dashArray}',
                fillColor: '{fillColor}',
                opacity: '{borderOpacity_str}',
                fillOpacity: '{opacity_str}',
            }}
        }}""".format(
            color=symbol.symbolLayer(0).borderColor().name(),
            weight=symbol.symbolLayer(0).borderWidth() * 4 if symbol.symbolLayer(0).borderStyle() != 0 else "0",
            dashArray=getLineStyle(symbol.symbolLayer(0).borderStyle(), symbol.symbolLayer(0).borderWidth() if symbol.symbolLayer(0).borderStyle() != 0 else "0"),
            fillColor=symbol.color().name() if symbol.symbolLayer(0).brushStyle() != 0 else "none",
            borderOpacity_str=borderOpacity_str,
            opacity_str=opacity_str)
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
    var overlay_{safeLayerName} = new L.imageOverlay(img_{safeLayerName}, img_bounds_{safeLayerName};""".format(safeLayerName=safeLayerName, out_raster_name=out_raster_name, bounds=bounds)
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


def legendStartScript():
    legendStart = """
        var legend = L.control({position: 'bottomright'});
        legend.onAdd = function (map) {
            var div = L.DomUtil.create('div', 'info legend');
            div.innerHTML = "<h3>Legend</h3><table>"""
    return legendStart


def legendEndScript():
    legendEnd = """</table>";
            return div;
        };
        legend.addTo(map);"""
    return legendEnd


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
        penStyle_str = ','.join(map(str, penStyle))
    else:
        penStyle_str = ""
    return penStyle_str
