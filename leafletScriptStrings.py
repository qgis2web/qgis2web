import re
import os
import traceback
from urllib.parse import parse_qs
from qgis.PyQt.QtCore import QSize, QDateTime
from qgis.core import (QgsProject,
                       QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsMapLayer,
                       QgsSymbolLayerUtils,
                       QgsSvgMarkerSymbolLayer,
                       QgsMessageLog,
                       Qgis,
                       QgsWkbTypes)
from qgis2web.utils import scaleToZoom, safeName


def jsonScript(layer):
    json = """
        <script src="data/{layer}.js\"></script>""".format(layer=layer)
    return json


def scaleDependentLayerScript(layer, layerName, cluster):
    max = layer.minimumScale()
    min = layer.maximumScale()
    if cluster:
        layerType = "cluster"
    else:
        layerType = "layer"
    scaleDependentLayer = """
            if (map.getZoom() <= {min} && map.getZoom() >= {max}) {{
                map.addLayer({layerType}_{layerName});
            }} else if (map.getZoom() > {min} || map.getZoom() < {max}) {{
                map.removeLayer({layerType}_{layerName});
            }}""".format(min=scaleToZoom(min), max=scaleToZoom(max),
                         layerName=layerName, layerType=layerType)
    return scaleDependentLayer


def scaleDependentLabelScript(layer, layerName):
    if layer.labeling() is not None:
        labelling = layer.labeling().settings()
        sv = labelling.scaleVisibility
        if sv:
            min = scaleToZoom(labelling.minimumScale)
            max = scaleToZoom(labelling.maximumScale)
            scaleDependentLabel = """
                if (map.hasLayer(layer_%(layerName)s)) {
                    if (map.getZoom() <= %(min)d && map.getZoom() >= %(max)d) {
                        layer_%(layerName)s.eachLayer(function (layer) {
                            layer.openTooltip();
                        });
                    } else {
                        layer_%(layerName)s.eachLayer(function (layer) {
                            layer.closeTooltip();
                        });
                    }
                }""" % {"min": min, "max": max, "layerName": layerName}
            return scaleDependentLabel
        else:
            return ""
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

            if (e.target.feature.geometry.type === 'LineString' || e.target.feature.geometry.type === 'MultiLineString') {
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


def mapScript(extent, matchCRS, crsAuthId, maxZoom, minZoom, bounds):
    map = """
        var map = L.map('map', {"""
    if matchCRS and crsAuthId != 'EPSG:4326':
        map += """
            crs: crs,
            continuousWorld: false,
            worldCopyJump: false, """
    map += """
            zoomControl:false, maxZoom:""" + str(maxZoom)
    map += """, minZoom:""" + str(minZoom) + """
        })"""
    if extent == "Canvas extent":
        map += """.fitBounds(""" + bounds + """);"""
    map += """
        var hash = new L.Hash(map);"""
    map += """
        map.attributionControl.setPrefix('<a href="""
    map += """"https://github.com/tomchadwin/qgis2web" target="_blank">"""
    map += """qgis2web</a> &middot; """
    map += """<a href="https://leafletjs.com" title="A JS library """
    map += """for interactive maps">Leaflet</a> &middot; """
    map += """<a href="https://qgis.org">QGIS</a>');"""
    map += """
        var autolinker = new Autolinker"""
    map += "({truncate: {length: 30, location: 'smart'}});"
    map += """
        // remove popup's row if "visible-with-data"
        function removeEmptyRowsFromPopupContent(content, feature) {
         var tempDiv = document.createElement('div');
         tempDiv.innerHTML = content;
         var rows = tempDiv.querySelectorAll('tr');
         for (var i = 0; i < rows.length; i++) {
             var td = rows[i].querySelector('td.visible-with-data');
             var key = td ? td.id : '';
             if (td && td.classList.contains('visible-with-data') && feature.properties[key] == null) {
                 rows[i].parentNode.removeChild(rows[i]);
             }
         }
         return tempDiv.innerHTML;
        }"""
    map += """
        // add class to format popup if it contains media
		function addClassToPopupIfMedia(content, popup) {
			var tempDiv = document.createElement('div');
			tempDiv.innerHTML = content;
			if (tempDiv.querySelector('td img')) {
				popup._contentNode.classList.add('media');
					// Delay to force the redraw
					setTimeout(function() {
						popup.update();
					}, 10);
			} else {
				popup._contentNode.classList.remove('media');
			}
		}
    """

    return map

def addZoomControl():
    zoomControlScript = """
        var zoomControl = L.control.zoom({
            position: 'topleft'
        }).addTo(map);
        """
    return zoomControlScript

def addLocateControl(locate):
    if not locate:
        return "" 
    locateScript = """
        L.control.locate({locateOptions: {maxZoom: 19}}).addTo(map);
        """
    return locateScript

def addMeasureControl(measure):
    if measure == "None":
        return ""    
    if measure == "Imperial":
        options = """{
            position: 'topleft',
            primaryLengthUnit: 'feet',
            secondaryLengthUnit: 'miles',
            primaryAreaUnit: 'sqfeet',
            secondaryAreaUnit: 'sqmiles'
        }"""
    else:
        options = """{
            position: 'topleft',
            primaryLengthUnit: 'meters',
            secondaryLengthUnit: 'kilometers',
            primaryAreaUnit: 'sqmeters',
            secondaryAreaUnit: 'hectares'
        }"""    
    measureScript = """
        var measureControl = new L.Control.Measure(%s);
        measureControl.addTo(map);
        document.getElementsByClassName('leaflet-control-measure-toggle')[0].innerHTML = '';
        document.getElementsByClassName('leaflet-control-measure-toggle')[0].className += ' fas fa-ruler';
        """ % options   
    return measureScript

def featureGroupsScript():
    featureGroups = """
        var bounds_group = new L.featureGroup([]);"""
    return featureGroups


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
        }"""
    return layerOrder


def popFuncsScript(table):
    popFuncs = """
            var popupContent = %s;
            var content = removeEmptyRowsFromPopupContent(popupContent, feature);
			layer.on('popupopen', function(e) {
				addClassToPopupIfMedia(content, e.popup);
			});
			layer.bindPopup(content, { maxHeight: 400 });""" % table
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
                    for (var i in e.target._eventParents) {
                        if (typeof e.target._eventParents[i].resetStyle === 'function') {
                            e.target._eventParents[i].resetStyle(e.target);
                        }
                    }"""
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
        iconSize = int((symbol.size() * 4) + 5)
    except Exception:
        iconSize = 16
    legendIcon = QgsSymbolLayerUtils.symbolPreviewPixmap(symbol,
                                                         QSize(iconSize,
                                                               iconSize))
    safeLabel = re.sub(r'[\W_]+', '', catr.label()) + str(cnt)
    legendIcon.save(os.path.join(outputProjectFileName, "legend",
                                 layerName + "_" + safeLabel + ".png"))
    catLegend += """<tr><td style="text-align: center;"><img src="legend/"""
    catLegend += layerName + "_" + safeLabel + """.png" /></td><td>"""
    catLegend += catr.label().replace("'", "\\'") + "</td></tr>"
    return catLegend


def pointToLayerFunction(safeLayerName, sl):
    try:
        if isinstance(sl, QgsSvgMarkerSymbolLayer):
            markerType = "marker"
        elif sl.shape() == 8:
            markerType = "circleMarker"
        else:
            markerType = "shapeMarker"
    except Exception:
        markerType = "circleMarker"

    pointToLayerFunction = """
        function pointToLayer_{safeLayerName}_{sl}(feature, latlng) {{
            var context = {{
                feature: feature,
                variables: {{}}
            }};
            return L.{markerType}(latlng, style_{safeLayerName}_{sl}""".format(
        safeLayerName=safeLayerName, sl=sl, markerType=markerType)
    pointToLayerFunction += """(feature));
        }"""
    return pointToLayerFunction


def wfsScript(scriptTag):
    wfs = """
        <script src='{scriptTag}'></script>""".format(scriptTag=scriptTag)
    return wfs


def clusterScript(safeLayerName):
    cluster = """
        var cluster_"""
    cluster += "{safeLayerName} = ".format(safeLayerName=safeLayerName)
    cluster += """new L.MarkerClusterGroup({{showCoverageOnHover: false,
            spiderfyDistanceMultiplier: 2}});
        cluster_{safeLayerName}""".format(safeLayerName=safeLayerName)
    cluster += """.addLayer(layer_{safeLayerName});
""".format(safeLayerName=safeLayerName)
    return cluster


def wmsScript(layer, safeLayerName, useWMS, useWMTS, identify, minZoom,
              maxZoom, count):
    d = parse_qs(layer.source())
    opacity = layer.renderer().opacity()
    attr = ""
    attrText = layer.attribution().replace('\n', ' ').replace('\r', ' ')
    attrUrl = layer.attributionUrl()
    zIndex = count + 400
    if attrText != "":
        attr = u'<a href="%s">%s</a>' % (attrUrl, attrText)
    wms = """
        map.createPane('pane_{safeLayerName}');
        map.getPane('pane_{safeLayerName}').style.zIndex = {zIndex};""".format(
        safeLayerName=safeLayerName, zIndex=zIndex)
    if 'type' in d and d['type'][0] == "xyz":
        if 'zmin' in d:
            zmin = "minNativeZoom: {zmin},".format(zmin=d['zmin'][0])
        else:
            zmin = ""
        if 'zmax' in d:
            zmax = "maxNativeZoom: {zmax}".format(zmax=d['zmax'][0])
        else:
            zmax = ""
        wms += """
        var layer_{safeLayerName} = L.tileLayer('{url}', {{
            pane: 'pane_{safeLayerName}',
            opacity: {opacity},
            attribution: '{attr}',
            minZoom: {minZoom},
            maxZoom: {maxZoom},
            {zmin}
            {zmax}
        }});
        layer_{safeLayerName};""".format(
            opacity=opacity, safeLayerName=safeLayerName, url=d['url'][0],
            attr=attr, zmin=zmin, zmax=zmax,
            minZoom=minZoom, maxZoom=maxZoom)
    elif 'tileMatrixSet' in d:
        useWMTS = True
        wmts_url = d['url'][0]
        wmts_url = wmts_url[:wmts_url.find('?')]
        wmts_layer = d['layers'][0]
        wmts_format = d['format'][0]
        # wmts_crs = d['crs'][0]
        try:
            wmts_style = d['styles'][0]
        except:
            wmts_style = ""
        wmts_tileMatrixSet = d['tileMatrixSet'][0]
        wms += """
        var layer_{safeLayerName} = L.tileLayer.wmts('{wmts_url}', {{
            pane: 'pane_{safeLayerName}',
            layer: '{wmts_layer}',
            tilematrixSet: '{wmts_tileMatrixSet}',
            format: '{wmts_format}',
            style: '{wmts_style}',
            uppercase: true,
            transparent: true,
            continuousWorld : true,
            opacity: {opacity},
            attribution: '{attr}',
        }});""".format(safeLayerName=safeLayerName, wmts_url=wmts_url,
                       wmts_layer=wmts_layer, wmts_format=wmts_format,
                       wmts_tileMatrixSet=wmts_tileMatrixSet,
                       wmts_style=wmts_style, opacity=opacity, attr=attr)
    else:
        useWMS = True
        wms_url = d['url'][0]
        wms_layer = d['layers'][0]
        wms_format = d['format'][0]
        getFeatureInfo = ""
        if not identify:
            getFeatureInfo = """,
            identify: false"""
        wms += """
        var layer_%s = L.WMS.layer("%s", "%s", {
            pane: 'pane_%s',
            format: '%s',
            uppercase: true,
            transparent: true,
            continuousWorld : true,
            tiled: true,
            info_format: 'text/html',
            opacity: %d%s,
            attribution: '%s',
        });""" % (safeLayerName, wms_url, wms_layer, safeLayerName, wms_format,
                  opacity, getFeatureInfo, attr)
    return wms, useWMS, useWMTS


def rasterScript(layer, safeLayerName, zIndex):
    zIndex = zIndex + 400
    out_raster = 'data/' + safeLayerName + '.png'
    pt2 = layer.extent()
    crsSrc = layer.crs()
    crsDest = QgsCoordinateReferenceSystem(4326)
    try:
        xform = QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance())
    except Exception:
        xform = QgsCoordinateTransform(crsSrc, crsDest)
    pt3 = xform.transformBoundingBox(pt2)
    bounds = '[[' + str(pt3.yMinimum()) + ','
    bounds += str(pt3.xMinimum()) + '],['
    bounds += str(pt3.yMaximum()) + ','
    bounds += str(pt3.xMaximum()) + ']]'
    raster = """
        map.createPane('pane_{safeLayerName}');
        map.getPane('pane_{safeLayerName}').style.zIndex = {zIndex};
        var img_{safeLayerName} = '{out_raster}';
        var img_bounds_{safeLayerName} = {bounds};
        var layer_{safeLayerName} = """.format(safeLayerName=safeLayerName,
                                               zIndex=zIndex,
                                               out_raster=out_raster,
                                               bounds=bounds)
    raster += "new L.imageOverlay(img_"
    raster += """{sln},
                                              img_bounds_{sln},
                                              {{pane: 'pane_{sln}'}});
        bounds_group.addLayer(layer_{sln});""".format(
        sln=safeLayerName)
    return raster

def titleSubScript(title, pos):
    if pos == "upper right":
        positionOpt = u"{'position':'topright'}"
    if pos == "lower right":
        positionOpt = u"{'position':'bottomright'}"
    if pos == "lower left":
        positionOpt = u"{'position':'bottomleft'}"
    if pos == "upper left":
        positionOpt = u"{'position':'topleft'}"
    titleSub = ""
    if pos != "None":
        titleSub = """
        var title = new L.Control(%s);
        title.onAdd = function (map) {
            this._div = L.DomUtil.create('div', 'info');
            this.update();
            return this._div;
        };
        title.update = function () {
            this._div.innerHTML = '<h2>""" % positionOpt
        titleSub += title.replace("'", "\\'") + """</h2>';
        };
        title.addTo(map);"""
    return titleSub

def abstractSubScript(abstract, pos):
    if pos == "upper right":
        positionOpt = u"{'position':'topright'}"
    if pos == "lower right":
        positionOpt = u"{'position':'bottomright'}"
    if pos == "lower left":
        positionOpt = u"{'position':'bottomleft'}"
    if pos == "upper left":
        positionOpt = u"{'position':'topleft'}"
    abstractSub = ""
    if pos != "None":
        abstractSub += """
        var abstract = new L.Control(%s);
        abstract.onAdd = function (map) {
            this._div = L.DomUtil.create('div',
            'leaflet-control abstract');
            this._div.id = 'abstract'""" % positionOpt
        if len(abstract) > 240:
            abstractSub += """
                this._div.setAttribute("onmouseenter", "abstract.show()");
                this._div.setAttribute("onmouseleave", "abstract.hide()");
                this.hide();
                return this._div;
            };
            abstract.hide = function () {
                this._div.classList.remove("abstractUncollapsed");
                this._div.classList.add("abstract");
                this._div.innerHTML = 'i'
            }
            abstract.show = function () {
                this._div.classList.remove("abstract");
                this._div.classList.add("abstractUncollapsed");
                this._div.innerHTML = '"""
        else:
            abstractSub += """

                abstract.show();
                return this._div;
            };
            abstract.show = function () {
                this._div.classList.remove("abstract");
                this._div.classList.add("abstractUncollapsed");
                this._div.innerHTML = '"""

        abstractSub += abstract.replace("'", "\\'").replace("\n", "<br />")
        abstractSub += """';
        };
        abstract.addTo(map);"""

    return abstractSub


def addLayersList(basemapList, matchCRS, layer_list, groups, cluster, legends,
                  expanded):
    #print("Layer List:", layer_list)
    #print("Groups:", groups)
    if len(basemapList) < 2 or matchCRS:
        controlStart = """
        var baseMaps = {};"""
    else:
        comma = ""
        controlStart = """
        var baseMaps = {"""
        for count, basemap in enumerate(basemapList):
            controlStart += comma + "'" + str(basemap)
            controlStart += "': basemap" + str(count)
            comma = ", "
        controlStart += "};"
    
    controlStart += """
        var overlaysTree = ["""
    layersList = controlStart

    # Dizionario per tenere traccia dei gruppi creati
    created_groups = {}
    # Dizionario per tenere traccia dei gruppi per i quali abbiamo già aggiunto la chiusura
    closed_groups = {}

    lyrCount = len(layer_list) - 1
    for i, clustered in zip(reversed(layer_list), reversed(cluster)):
        try:
            rawLayerName = i.name()
            safeLayerName = safeName(rawLayerName) + "_" + str(lyrCount)
            lyrCount -= 1

            # Verifica se il layer fa parte di uno dei gruppi
            is_in_group = False
            for group_layers in groups.values():
                if i in group_layers:
                    is_in_group = True
                    break
            
            if is_in_group:
                for group_name, group_layers in groups.items():
                    if i in group_layers:
                        # Controlla se il gruppo è già stato creato
                        if group_name not in created_groups:
                            created_groups[group_name] = []  # Crea il gruppo vuoto
                            layersList += """
        {label: '<b>""" + group_name + "</b>', selectAllCheckbox: true, children: ["""
                        # Aggiunge il layer al gruppo
                        created_groups[group_name].append(i)
                            
            if i.type() == QgsMapLayer.VectorLayer:
                # testDump = i.renderer().dump()
                if clustered and i.geometryType() == QgsWkbTypes.PointGeometry:
                    layersList += """
            {label: '""" + legends[safeLayerName].replace("'", "\'")
                    layersList += "', layer: cluster_""" + safeLayerName + "},"
                else:
                    layersList += """
            {label: '""" + legends[safeLayerName].replace("'", "\'")
                    layersList += "', layer: layer_" + safeLayerName + "},"
            elif i.type() == QgsMapLayer.RasterLayer:
                layersList += '''
            {label: "''' + rawLayerName.replace("'", "\'") + '"'
                layersList += ", layer: layer_" + safeLayerName + """},"""

            # Controlla se tutti i layer del gruppo sono stati aggiunti
            for group_name in created_groups:
                if group_name not in closed_groups and len(created_groups[group_name]) == len(groups[group_name]):
                    layersList += "]},"  # Chiude il gruppo se tutti i layer sono stati aggiunti
                    # Aggiungi il gruppo alla lista dei gruppi chiusi
                    closed_groups[group_name] = True

        except Exception:
            QgsMessageLog.logMessage(traceback.format_exc(), "qgis2web",
                                    level=Qgis.Critical)
            
    layersList += "]"

    layersList += """
        var lay = L.control.layers.tree(null, overlaysTree,{
            //namedToggle: true,
            //selectorBack: false,
            //closedSymbol: '&#8862; &#x1f5c0;',
            //openedSymbol: '&#8863; &#x1f5c1;',
            //collapseAll: 'Collapse all',
            //expandAll: 'Expand all',
        """
    if expanded:
        layersList += """
            collapsed: false, 
        });
        """
    else:
        layersList += """
            collapsed: true,
        });
        """  
    layersList += """
        lay.addTo(map);
        """
    if expanded:
        layersList += """
		document.addEventListener("DOMContentLoaded", function() {
            // set new Layers List height which considers toggle icon
            function newLayersListHeight() {
                var layerScrollbarElement = document.querySelector('.leaflet-control-layers-scrollbar');
                if (layerScrollbarElement) {
                    var layersListElement = document.querySelector('.leaflet-control-layers-list');
                    var originalHeight = layersListElement.style.height 
                        || window.getComputedStyle(layersListElement).height;
                    var newHeight = parseFloat(originalHeight) - 50;
                    layersListElement.style.height = newHeight + 'px';
                }
            }
            var isLayersListExpanded = true;
            var controlLayersElement = document.querySelector('.leaflet-control-layers');
            var toggleLayerControl = document.querySelector('.leaflet-control-layers-toggle');
            // toggle Collapsed/Expanded and apply new Layers List height
            toggleLayerControl.addEventListener('click', function() {
                if (isLayersListExpanded) {
                    controlLayersElement.classList.remove('leaflet-control-layers-expanded');
                } else {
                    controlLayersElement.classList.add('leaflet-control-layers-expanded');
                }
                isLayersListExpanded = !isLayersListExpanded;
                newLayersListHeight()
            });	
			// apply new Layers List height if toggle layerstree
			if (controlLayersElement) {
				controlLayersElement.addEventListener('click', function(event) {
					var toggleLayerHeaderPointer = event.target.closest('.leaflet-layerstree-header-pointer span');
					if (toggleLayerHeaderPointer) {
						newLayersListHeight();
					}
				});
			}
            // Collapsed/Expanded at Start to apply new height
            setTimeout(function() {
                toggleLayerControl.click();
            }, 10);
            setTimeout(function() {
                toggleLayerControl.click();
            }, 10);
            // Collapsed touch/small screen
            var isSmallScreen = window.innerWidth < 650;
            if (isSmallScreen) {
                setTimeout(function() {
                    controlLayersElement.classList.remove('leaflet-control-layers-expanded');
                    isLayersListExpanded = !isLayersListExpanded;
                }, 500);
            }  
        });       
        """
    return layersList


def scaleBar():
    scaleBar = "L.control.scale({position: 'bottomleft', "
    scaleBar += "maxWidth: 100, metric: true, imperial: false, "
    scaleBar += "updateWhenIdle: false}).addTo(map);"
    return scaleBar


def addressSearchScript():
    addressSearch = """
        var osmGeocoder = new L.Control.Geocoder({
            collapsed: true,
            position: 'topleft',
            text: 'Search',
            title: 'Testing'
        }).addTo(map);
        document.getElementsByClassName('leaflet-control-geocoder-icon')[0]
        .className += ' fa fa-search';
        document.getElementsByClassName('leaflet-control-geocoder-icon')[0]
        .title += 'Search for a place';
        """
    return addressSearch


def getVTStyles(vtStyles):
    vtStyleString = ""
    for (vts, lyrs) in vtStyles.items():
        vtStyleString += """
        style_%s = {""" % safeName(vts)
        for (lyr, styles) in lyrs.items():
            vtStyleString += """
            %s: [""" % lyr
            for style in styles:
                if style == "":
                    style = "{}"
                vtStyleString += "%s," % style
            vtStyleString += "],"
            vtStyleString = vtStyleString.replace(",]", "]")
        vtStyleString += "}"

    return vtStyleString


def getVTLabels(vtLabels):
    labels = []
    for k, v in vtLabels.items():
        labels.append("""
    function label_%s(feature, featureLayer, vtLayer, tileCoords) {
        var context = {
            feature: feature,
            variables: {}
        };
        %s
    }""" % (safeName(k), v))
    labelString = "".join(labels)
    return labelString


def endHTMLscript(wfsLayers, layerSearch, filterItems, labelCode, labels,
                  searchLayer, useHeat, useRaster, labelsList,
                  mapUnitLayers):
    if labels == "":
        endHTML = ""
    else:
        endHTML = """
        map.on("zoomend", function(){
%s
        });""" % labels
    if wfsLayers == "":
        endHTML += """
        setBounds();
        %s""" % labelCode
        endHTML += labels
    if len(mapUnitLayers) > 0:
        lyrs = []
        for layer in mapUnitLayers:
            lyrs.append("""
            layer_%s.setStyle(style_%s_0);""" % (layer, layer))
        lyrScripts = "".join(lyrs)
        endHTML += """
        newM2px();
%s
        map.on("zoomend", function(){
            newM2px();
%s
        });""" % (lyrScripts, lyrScripts)
    if layerSearch != "None":
        searchVals = layerSearch.split(": ")
        endHTML += """
        map.addControl(new L.Control.Search({{
            layer: {searchLayer},
            initial: false,
            hideMarkerOnCollapse: true,
            propertyName: '{field}'}}));
        document.getElementsByClassName('search-button')[0].className +=
         ' fa fa-binoculars';
            """.format(searchLayer=searchLayer,
                       field=searchVals[1])
    filterItems = sorted(filterItems, key=lambda k: k['type'])
    filterNum = len(filterItems)
    if filterNum != 0:
        endHTML += """
        var mapDiv = document.getElementById('map');
        var row = document.createElement('div');
        row.className="row";
        row.id="all";
        row.style.height = "100%";
        var col1 = document.createElement('div');
        col1.className="col9";
        col1.id = "mapWindow";
        col1.style.height = "99%";
        col1.style.width = "80%";
        col1.style.display = "inline-block";
        var col2 = document.createElement('div');
        col2.className="col3";
        col2.id = "menu";
        col2.style.display = "inline-block";
        mapDiv.parentNode.insertBefore(row, mapDiv);
        document.getElementById("all").appendChild(col1);
        document.getElementById("all").appendChild(col2);
        col1.appendChild(mapDiv)
        var Filters = {"""
        filterList = []
        for item in range(0, filterNum):
            filterList.append('"' + filterItems[item]["name"] + '": "' +
                              filterItems[item]["type"] + '"')
        endHTML += ",".join(filterList) + "};"
        endHTML += r"""
        function filterFunc() {
          map.eachLayer(function(lyr){
          if ("options" in lyr && "dataVar" in lyr["options"]){
            features = this[lyr["options"]["dataVar"]].features.slice(0);
            try{
              for (key in Filters){
                keyS = key.replace(/[^a-zA-Z0-9_]/g, "")
                if (Filters[key] == "str" || Filters[key] == "bool"){
                  var selection = [];
                  var options = document.getElementById("sel_" + keyS).options
                  for (var i=0; i < options.length; i++) {
                    if (options[i].selected) selection.push(options[i].value);
                  }
                    try{
                      if (key in features[0].properties){
                        for (i = features.length - 1;
                          i >= 0; --i){
                          if (selection.indexOf(
                          features[i].properties[key])<0
                          && selection.length>0) {
                          features.splice(i,1);
                          }
                        }
                      }
                    } catch(err){
                  }
                }
                if (Filters[key] == "int"){
                  sliderVals =  document.getElementById(
                    "div_" + keyS).noUiSlider.get();
                  try{
                    if (key in features[0].properties){
                    for (i = features.length - 1; i >= 0; --i){
                      if (parseInt(features[i].properties[key])
                          < sliderVals[0]
                          || parseInt(features[i].properties[key])
                          > sliderVals[1]){
                            features.splice(i,1);
                          }
                        }
                      }
                    } catch(err){
                    }
                  }
                if (Filters[key] == "real"){
                  sliderVals =  document.getElementById(
                    "div_" + keyS).noUiSlider.get();
                  try{
                    if (key in features[0].properties){
                    for (i = features.length - 1; i >= 0; --i){
                      if (features[i].properties[key]
                          < sliderVals[0]
                          || features[i].properties[key]
                          > sliderVals[1]){
                            features.splice(i,1);
                          }
                        }
                      }
                    } catch(err){
                    }
                  }
                if (Filters[key] == "date"
                  || Filters[key] == "datetime"
                  || Filters[key] == "time"){
                  try{
                    if (key in features[0].properties){
                      HTMLkey = key.replace(/[&\/\\#,+()$~%.'":*?<>{} ]/g, '');
                      startdate = document.getElementById("dat_" +
                        HTMLkey + "_date1").value.replace(" ", "T");
                      enddate = document.getElementById("dat_" +
                        HTMLkey + "_date2").value.replace(" ", "T");
                      for (i = features.length - 1; i >= 0; --i){
                        if (features[i].properties[key] < startdate
                          || features[i].properties[key] > enddate){
                          features.splice(i,1);
                        }
                      }
                    }
                  } catch(err){
                  }
                }
              }
            } catch(err){
            }
          this[lyr["options"]["layerName"]].clearLayers();
          this[lyr["options"]["layerName"]].addData(features);
          """ + labelCode + """
          }
          })
        }"""
        for item in range(0, filterNum):
            itemName = filterItems[item]["name"]
            if filterItems[item]["type"] in ["str", "bool"]:
                selSize = 2
                if filterItems[item]["type"] == "str":
                    if len(filterItems[item]["values"]) > 10:
                        selSize = 10
                    else:
                        selSize = len(filterItems[item]["values"])
                endHTML += """
            document.getElementById("menu").appendChild(
                document.createElement("div"));
            var div_{nameS} = document.createElement('div');
            div_{nameS}.id = "div_{nameS}";
            div_{nameS}.className= "filterselect";
            document.getElementById("menu").appendChild(div_{nameS});
            sel_{nameS} = document.createElement('select');
            sel_{nameS}.multiple = true;
            sel_{nameS}.size = {s};
            sel_{nameS}.id = "sel_{nameS}";
            var {nameS}_options_str = "<option value='' unselected></option>";
            sel_{nameS}.onchange = function(){{filterFunc()}};
            """.format(name=itemName, nameS=safeName(itemName), s=selSize)
                for entry in filterItems[item]["values"]:
                    try:
                        safeEntry = entry.replace("'", "&apos;")
                    except:
                        safeEntry = entry
                    endHTML += """
            {nameS}_options_str  += '<option value="{e}">{e}</option>';
                        """.format(e=safeEntry,
                                   name=itemName, nameS=safeName(itemName))
                endHTML += """
            sel_{nameS}.innerHTML = {nameS}_options_str;
            div_{nameS}.appendChild(sel_{nameS});
            var lab_{nameS} = document.createElement('div');
            lab_{nameS}.innerHTML = '{name}';
            lab_{nameS}.className = 'filterlabel';
            div_{nameS}.appendChild(lab_{nameS});
            var reset_{nameS} = document.createElement('div');
            reset_{nameS}.innerHTML = 'clear filter';
            reset_{nameS}.className = 'filterlabel';
            reset_{nameS}.onclick = function() {{
                var options = document.getElementById("sel_{nameS}").options;
                for (var i=0; i < options.length; i++) {{
                    options[i].selected = false;
                }}
                filterFunc();
            }};
            div_{nameS}.appendChild(reset_{nameS});
                """.format(name=itemName, nameS=safeName(itemName))
            if filterItems[item]["type"] in ["int", "real"]:
                endHTML += """
            document.getElementById("menu").appendChild(
                document.createElement("div"));
            var div_{nameS} = document.createElement("div");
            div_{nameS}.id = "div_{nameS}";
            div_{nameS}.className = "slider";
            document.getElementById("menu").appendChild(div_{nameS});
            var lab_{nameS} = document.createElement('div');
            lab_{nameS}.innerHTML  = '{name}: <span id="val_{nameS}"></span>';
            lab_{nameS}.className = 'filterlabel';
            document.getElementById("menu").appendChild(lab_{nameS});
            var reset_{nameS} = document.createElement('div');
            reset_{nameS}.innerHTML = 'clear filter';
            reset_{nameS}.className = 'filterlabel';
            lab_{nameS}.className = 'filterlabel';
            reset_{nameS}.onclick = function() {{
                sel_{nameS}.noUiSlider.reset();
            }};
            document.getElementById("menu").appendChild(reset_{nameS});
            var sel_{nameS} = document.getElementById('div_{nameS}');
            """ .format(name=itemName, nameS=safeName(itemName))
                if filterItems[item]["type"] == "int":
                    endHTML += """
            noUiSlider.create(sel_{nameS}, {{
                connect: true,
                start: [{min}, {max}],
                step: 1,
                format: wNumb({{
                    decimals: 0,
                    }}),
                range: {{
                min: {min},
                max: {max}
                }}
            }});
            sel_{nameS}.noUiSlider.on('update', function (values) {{
            filterVals =[];
            for (value in values){{
            filterVals.push(parseInt(value))
            }}
            val_{nameS} = document.getElementById('val_{nameS}');
            val_{nameS}.innerHTML = values.join(' - ');
                filterFunc()
            }});""".format(name=itemName, nameS=safeName(itemName),
                           min=filterItems[item]["values"][0],
                           max=filterItems[item]["values"][1])
                else:
                    endHTML += """
            noUiSlider.create(sel_{nameS}, {{
                connect: true,
                start: [{min}, {max}],
                range: {{
                min: {min},
                max: {max}
                }}
            }});
            sel_{nameS}.noUiSlider.on('update', function (values) {{
            val_{nameS} = document.getElementById('val_{nameS}');
            val_{nameS}.innerHTML = values.join(' - ');
                filterFunc()
            }});
            """.format(name=itemName, nameS=safeName(itemName),
                       min=filterItems[item]["values"][0],
                       max=filterItems[item]["values"][1])
            if filterItems[item]["type"] in ["date", "time", "datetime"]:
                startDate = filterItems[item]["values"][0]
                endDate = filterItems[item]["values"][1]
                d = "'YYYY-mm-dd'"
                t = "'HH:ii:ss'"
                Y1 = startDate.toString("yyyy")
                M1 = startDate.toString("M")
                D1 = startDate.toString("d")
                hh1 = startDate.toString("h")
                mm1 = startDate.toString("m")
                ss1 = startDate.toString("s")
                Y2 = endDate.toString("yyyy")
                M2 = endDate.toString("M")
                D2 = endDate.toString("d")
                hh2 = endDate.toString("h")
                mm2 = endDate.toString("m")
                ss2 = endDate.toString("s")
                if filterItems[item]["type"] == "date":
                    t = "false"
                    hh1 = 0
                    mm1 = 0
                    ss1 = 0
                    hh2 = 0
                    mm2 = 0
                    ss2 = 0
                    ds = QDateTime(startDate).toMSecsSinceEpoch()
                    de = QDateTime(endDate).toMSecsSinceEpoch()
                if filterItems[item]["type"] == "datetime":
                    ds = startDate.toMSecsSinceEpoch()
                    de = endDate.toMSecsSinceEpoch()
                if filterItems[item]["type"] == "time":
                    d = "false"
                    Y1 = 0
                    M1 = 1
                    D1 = 0
                    Y2 = 0
                    M2 = 1
                    D2 = 0
                    ds = "null"
                    de = "null"
                endHTML += """
            document.getElementById("menu").appendChild(
                document.createElement("div"));
            var div_{nameS}_date1 = document.createElement("div");
            div_{nameS}_date1.id = "div_{nameS}_date1";
            div_{nameS}_date1.className= "filterselect";
            document.getElementById("menu").appendChild(div_{nameS}_date1);
            dat_{nameS}_date1 = document.createElement('input');
            dat_{nameS}_date1.type = "text";
            dat_{nameS}_date1.id = "dat_{nameS}_date1";
            div_{nameS}_date1.appendChild(dat_{nameS}_date1);
            var lab_{nameS}_date1 = document.createElement('div');
            lab_{nameS}_date1.innerHTML  = '{name} from';
            lab_{nameS}_date1.className = 'filterlabel';
            document.getElementById("div_{nameS}_date1").appendChild(
                lab_{nameS}_date1);
            var reset_{nameS}_date1 = document.createElement('div');
            reset_{nameS}_date1.innerHTML = "clear";
            reset_{nameS}_date1.className = 'filterlabel';
            reset_{nameS}_date1.onclick = function() {{
                tail.DateTime("#dat_{nameS}_date1", {{
                    dateStart: {ds},
                    dateEnd: {de},
                    dateFormat: {d},
                    timeFormat: {t},
                    today: false,
                    weekStart: 1,
                    position: "left",
                    closeButton: true,
                    timeStepMinutes:1,
                    timeStepSeconds: 1
                }}).selectDate({Y1},{M1}-1,{D1},{hh1},{mm1},{ss1});
                tail.DateTime("#dat_{nameS}_date1").reload()
            }}
            document.getElementById("div_{nameS}_date1").appendChild(
                reset_{nameS}_date1);
            document.addEventListener("DOMContentLoaded", function(){{
                tail.DateTime("#dat_{nameS}_date1", {{
                    dateStart: {ds},
                    dateEnd: {de},
                    dateFormat: {d},
                    timeFormat: {t},
                    today: false,
                    weekStart: 1,
                    position: "left",
                    closeButton: true,
                    timeStepMinutes:1,
                    timeStepSeconds: 1
                }}).selectDate({Y1},{M1}-1,{D1},{hh1},{mm1},{ss1});
                tail.DateTime("#dat_{nameS}_date1").reload()
                """.format(name=itemName, nameS=safeName(itemName), de=de,
                           ds=ds, d=d, t=t, Y1=Y1, M1=M1, D1=D1, hh1=hh1,
                           mm1=mm1, ss1=ss1)
                endHTML += """
                tail.DateTime("#dat_{nameS}_date2", {{
                    dateStart: {ds},
                    dateEnd: {de},
                    dateFormat: {d},
                    timeFormat: {t},
                    today: false,
                    weekStart: 1,
                    position: "left",
                    closeButton: true,
                    timeStepMinutes:1,
                    timeStepSeconds: 1
                }}).selectDate({Y2},{M2}-1,{D2},{hh2},{mm2},{ss2});
                tail.DateTime("#dat_{nameS}_date2").reload()
                filterFunc()
                dat_{nameS}_date1.onchange = function(){{filterFunc()}};
                dat_{nameS}_date2.onchange = function(){{filterFunc()}};
            }});
            """.format(name=itemName, nameS=safeName(itemName), de=de, ds=ds,
                       d=d, t=t, Y2=Y2, M2=M2, D2=D2, hh2=hh2, mm2=mm2,
                       ss2=ss2)
                endHTML += """
            var div_{nameS}_date2 = document.createElement("div");
            div_{nameS}_date2.id = "div_{nameS}_date2";
            div_{nameS}_date2.className= "filterselect";
            document.getElementById("menu").appendChild(div_{nameS}_date2);
            dat_{nameS}_date2 = document.createElement('input');
            dat_{nameS}_date2.type = "text";
            dat_{nameS}_date2.id = "dat_{nameS}_date2";
            div_{nameS}_date2.appendChild(dat_{nameS}_date2);
            var lab_{nameS}_date2 = document.createElement('div');
            lab_{nameS}_date2.innerHTML  = '{name} till';
            lab_{nameS}_date2.className = 'filterlabel';
            document.getElementById("div_{nameS}_date2")
              .appendChild(lab_{nameS}_date2);
            var reset_{nameS}_date2 = document.createElement('div');
            reset_{nameS}_date2.innerHTML = "clear";
            reset_{nameS}_date2.className = 'filterlabel';
            reset_{nameS}_date2.onclick = function() {{
                tail.DateTime("#dat_{nameS}_date2", {{
                    dateStart: {ds},
                    dateEnd: {de},
                    dateFormat: {d},
                    timeFormat: {t},
                    today: false,
                    weekStart: 1,
                    position: "left",
                    closeButton: true,
                    timeStepMinutes:1,
                    timeStepSeconds: 1
                }}).selectDate({Y2},{M2}-1,{D2},{hh2},{mm2},{ss2});
                tail.DateTime("#dat_{nameS}_date2").reload()
            }}
            document.getElementById("div_{nameS}_date2").appendChild(
                reset_{nameS}_date2);
            """.format(name=itemName, nameS=safeName(itemName), de=de, ds=ds,
                       d=d, t=t, Y2=Y2, M2=M2, D2=D2, hh2=hh2, mm2=mm2,
                       ss2=ss2)
    if useHeat:
        endHTML += """
        function geoJson2heat(geojson, weight) {
          return geojson.features.map(function(feature) {
            return [
              feature.geometry.coordinates[1],
              feature.geometry.coordinates[0],
              feature.properties[weight]
            ];
          });
        }"""
    if useRaster:
        endHTML += """
        L.ImageOverlay.include({
            getBounds: function () {
                return this._bounds;
            }
        });"""
    if labelsList != "":
        endHTML += """
        resetLabels([%s]);
        map.on("zoomend", function(){
            resetLabels([%s]);
        });
        map.on("layeradd", function(){
            resetLabels([%s]);
        });
        map.on("layerremove", function(){
            resetLabels([%s]);
        });""" % (labelsList, labelsList, labelsList, labelsList)
    endHTML += """
        </script>%s""" % wfsLayers
    return endHTML
