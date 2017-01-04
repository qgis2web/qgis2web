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
        <script src="data/{layer}.js\"></script>""".format(layer=layer)
    return json


def scaleDependentLayerScript(layer, layerName):
    min = layer.minimumScale()
    max = layer.maximumScale()
    scaleDependentLayer = """
            if (map.getZoom() <= {min} && map.getZoom() >= {max}) {{
                feature_group.addLayer(layer_{layerName});
            }} else if (map.getZoom() > {min} || map.getZoom() < {max}) {{
                feature_group.removeLayer(layer_{layerName});
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
            if (map.hasLayer(layer_%(layerName)s)) {
                if (map.getZoom() <= %(min)d && map.getZoom() >= %(max)d) {
                    layer_%(layerName)s.eachLayer(function (layer) {
                        layer.showLabel();
                    });
                } else {
                    layer_%(layerName)s.eachLayer(function (layer) {
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


def extentScript(extent, restrictToExtent):
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
                    layer.setStyle(style_"""
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


def iconLegend(symbol, catr, outputProjectFileName, layerName, catLegend, cnt):
    try:
        iconSize = (symbol.size() * 4) + 5
    except:
        iconSize = 16
    legendIcon = QgsSymbolLayerV2Utils.symbolPreviewPixmap(symbol,
                                                           QSize(iconSize,
                                                                 iconSize))
    safeLabel = re.sub('[\W_]+', '', catr.label()) + unicode(cnt)
    legendIcon.save(os.path.join(outputProjectFileName, "legend",
                                 layerName + "_" + safeLabel + ".png"))
    catLegend += """<tr><td style="text-align: center;"><img src="legend/"""
    catLegend += layerName + "_" + safeLabel + """.png" /></td><td>"""
    catLegend += catr.label() + "</td></tr>"
    return catLegend


def pointToLayerFunction(safeLayerName, labeltext, symbol):
    if isinstance(symbol.symbolLayer(0), QgsSvgMarkerSymbolLayerV2):
        markerType = "marker"
    else:
        markerType = "circleMarker"
    pointToLayerFunction = """
        function pointToLayer_{safeLayerName}(feature, latlng) {{
            return L.{markerType}(latlng, style_{safeLayerName}""".format(
                safeLayerName=safeLayerName,
                markerType=markerType)
    pointToLayerFunction += """(feature)){labeltext}
        }}""".format(labeltext=labeltext)
    return pointToLayerFunction


def wfsScript(scriptTag):
    wfs = """
        <script src='{scriptTag}'></script>""".format(scriptTag=scriptTag)
    return wfs


def clusterScript(safeLayerName):
    cluster = """
        var cluster_"""
    cluster += "{safeLayerName} = ".format(safeLayerName=safeLayerName)
    cluster += """new L.MarkerClusterGroup({{showCoverageOnHover: false}});
        cluster_{safeLayerName}""".format(safeLayerName=safeLayerName)
    cluster += """.addLayer(layer_{safeLayerName});
""".format(safeLayerName=safeLayerName)
    return cluster


def pointJSONLayer(sln, label, usedFields, markerType):
    categorizedPointJSON = """
        var layer_{sln} = new L.geoJson(json_{sln}, {{
            pane: 'pane_{sln}',"""
    if usedFields != 0:
        categorizedPointJSON += """
            onEachFeature: pop_{sln},"""
    categorizedPointJSON += """
            pointToLayer: function (feature, latlng) {{
                return L.{markerType}(latlng, """
    categorizedPointJSON += """style_{sln}(feature)){label}
            }}
        }});"""
    categorizedPointJSON = categorizedPointJSON.format(sln=sln, label=label,
                                                       markerType=markerType)
    return categorizedPointJSON


def wmsScript(layer, safeLayerName):
    d = parse_qs(layer.source())
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


def rasterScript(layer, safeLayerName):
    out_raster = 'data/' + safeLayerName + '.png'
    pt2 = layer.extent()
    crsSrc = layer.crs()
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
                    new_layer += ": cluster_""" + safeLayerName + ","
                else:
                    new_layer = "'" + legends[safeLayerName] + "':"
                    new_layer += " layer_" + safeLayerName + ","
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


def scaleBar(placement):
        scaleBar = """
        L.control.scale({position: '%s', """ % placement
        scaleBar += "maxWidth: 100, metric: true, imperial: false, "
        scaleBar += "updateWhenIdle: false}).addTo(map);"
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
