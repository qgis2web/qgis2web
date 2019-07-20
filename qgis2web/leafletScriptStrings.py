import re
import os
import traceback
from urllib.parse import parse_qs
from qgis.PyQt.QtCore import QSize
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
        var map = L.map('map', {"""
    if matchCRS and crsAuthId != 'EPSG:4326':
        map += """
            crs: crs,
            continuousWorld: false,
            worldCopyJump: false, """
    map += """
            zoomControl:true, maxZoom:""" + str(maxZoom)
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
    if locate:
        map += """
        L.control.locate({locateOptions: {maxZoom: 19}}).addTo(map);"""
    if measure != "None":
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
        map += """
        var measureControl = new L.Control.Measure(%s);
        measureControl.addTo(map);
        document.getElementsByClassName('leaflet-control-measure-toggle')[0]
        .innerHTML = '';
        document.getElementsByClassName('leaflet-control-measure-toggle')[0]
        .className += ' fas fa-ruler';
        """ % options
    return map


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
            layer.bindPopup(popupContent, {maxHeight: 400});""" % table
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
                    for (i in e.target._eventParents) {
                        e.target._eventParents[i].resetStyle(e.target);
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
        iconSize = (symbol.size() * 4) + 5
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


def wmsScript(layer, safeLayerName, useWMS, useWMTS, identify):
    d = parse_qs(layer.source())
    opacity = layer.renderer().opacity()
    attr = ""
    attrText = layer.attribution().replace('\n', ' ').replace('\r', ' ')
    attrUrl = layer.attributionUrl()
    if attrText != "":
        attr = u'<a href="%s">%s</a>' % (attrUrl, attrText)
    if 'type' in d and d['type'][0] == "xyz":
        wms = """
        var layer_{safeLayerName} = L.tileLayer('{url}', {{
            opacity: {opacity},
            attribution: '{attr}',
        }});
        layer_{safeLayerName};""".format(
            opacity=opacity, safeLayerName=safeLayerName, url=d['url'][0],
            attr=attr)
    elif 'tileMatrixSet' in d:
        useWMTS = True
        wmts_url = d['url'][0]
        wmts_url = wmts_url.replace("request=getcapabilities", "")
        wmts_layer = d['layers'][0]
        wmts_format = d['format'][0]
        # wmts_crs = d['crs'][0]
        wmts_style = d['styles'][0]
        wmts_tileMatrixSet = d['tileMatrixSet'][0]
        wms = """
        var layer_{safeLayerName} = L.tileLayer.wmts('{wmts_url}', {{
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
        wms = """
        var layer_%s = L.WMS.layer("%s", "%s", {
            format: '%s',
            uppercase: true,
            transparent: true,
            continuousWorld : true,
            tiled: true,
            info_format: 'text/html',
            opacity: %d%s,
            attribution: '%s',
        });""" % (safeLayerName, wms_url, wms_layer, wms_format, opacity,
                  getFeatureInfo, attr)
    return wms, useWMS, useWMTS


def rasterScript(layer, safeLayerName):
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
        var img_{safeLayerName} = '{out_raster}';
        var img_bounds_{safeLayerName} = {bounds};
        var layer_{safeLayerName} = """.format(safeLayerName=safeLayerName,
                                               out_raster=out_raster,
                                               bounds=bounds)
    raster += "new L.imageOverlay(img_"
    raster += """{safeLayerName}, img_bounds_{safeLayerName});
        bounds_group.addLayer(layer_{safeLayerName});""".format(
        safeLayerName=safeLayerName)
    return raster


def titleSubScript(webmap_head, level, pos):
    if pos == "upper right":
        positionOpt = u"{'position':'topright'}"
    if pos == "lower right":
        positionOpt = u"{'position':'bottomright'}"
    if pos == "lower left":
        positionOpt = u"{'position':'bottomleft'}"
    if pos == "upper left":
        positionOpt = u"{'position':'topleft'}"
    titleSub = ""
    if level == 1:
        titleSub += """
            var title = new L.Control();
            title.onAdd = function (map) {
                this._div = L.DomUtil.create('div', 'info');
                this.update();
                return this._div;
            };
            title.update = function () {
                this._div.innerHTML = '<h2>"""
        titleSub += webmap_head.replace("'", "\\'") + """</h2>';
            };
            title.addTo(map);"""
    if level == 2 and pos != "None":
        titleSub += """
            var abstract = new L.Control(%s);
            abstract.onAdd = function (map) {
                this._div = L.DomUtil.create('div',
                'leaflet-control leaflet-bar abstract');
                this._div.id = "abstract"
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
                this._div.innerHTML = '""" % positionOpt
        titleSub += webmap_head.replace("'", "\\'").replace("\n", "<br />")
        titleSub += """';
            };
            abstract.addTo(map);"""

    return titleSub


def addLayersList(basemapList, matchCRS, layer_list, cluster, legends,
                  collapsed):
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
        L.control.layers(baseMaps,{"""
    layersList = controlStart

    lyrCount = len(layer_list) - 1
    for i, clustered in zip(reversed(layer_list), reversed(cluster)):
        try:
            rawLayerName = i.name()
            safeLayerName = safeName(rawLayerName) + "_" + str(lyrCount)
            lyrCount -= 1
            if i.type() == QgsMapLayer.VectorLayer:
                # testDump = i.renderer().dump()
                if clustered and i.geometryType() == QgsWkbTypes.PointGeometry:
                    new_layer = "'" + legends[safeLayerName].replace("'", "\'")
                    new_layer += "': cluster_""" + safeLayerName + ","
                else:
                    new_layer = "'" + legends[safeLayerName].replace("'", "\'")
                    new_layer += "': layer_" + safeLayerName + ","
                layersList += new_layer
            elif i.type() == QgsMapLayer.RasterLayer:
                new_layer = '"' + rawLayerName.replace("'", "\'") + '"'
                new_layer += ": layer_" + safeLayerName + ""","""
                layersList += new_layer
        except Exception:
            QgsMessageLog.logMessage(traceback.format_exc(), "qgis2web",
                                     level=Qgis.Critical)
    controlEnd = "}"
    if collapsed:
        controlEnd += ",{collapsed:false}"
    controlEnd += ").addTo(map);"
    layersList += controlEnd
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
    #filterItems = sorted(filterItems, key=lambda k: k['type']) 
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
        for item in range(0,filterNum):
            filterList.append('"' + filterItems[item]["name"] + '": "' + 
                         filterItems[item]["type"] + '"')
        endHTML += ",".join(filterList) + "};"
    #add filterFunc:
        endHTML += """
            //filter function checks every layer for the desired input and 
            //removes the specific feature if it is not part of the filter set.
            function filterFunc() {
              map.eachLayer(function(lyr){
                if ("options" in lyr && "dataVar" in lyr["options"]){
                features = this[lyr["options"]["dataVar"]].features.slice(0);
                try{
                    for (key in Filters){
                        if (Filters[key] == "str" || Filters[key] == "bool"){
                          var selection = [];
                          for (option in Array.from(this["sel_" + key].selectedOptions)){
                              selection.push(this["sel_"+key].selectedOptions[option].value);
                            
                          }
                          try{
                            if (key in features[0].properties){
                              for (i = features.length - 1; i >= 0; --i){
                                if (selection.indexOf(
                                  features[i].properties[key])<0 && selection.length>0) {
                                  features.splice(i,1);
                                }
                              }
                            }
                          } catch(err){
                          }
                        }
                        if (Filters[key] == "int" || Filters[key] == "real"){
                            sliderVals = this["sel_" + key].noUiSlider.get();
                            try{
                             if (key in features[0].properties){
                               for (i = features.length - 1; i >= 0; --i){
                                   if (parseInt(features[i].properties[key]) < sliderVals[0]
                                     || parseInt(features[i].properties[key]) > sliderVals[1]
                                     ) {
                                     features.splice(i,1);
                                   }      
                               }
                             }
                            } catch(err){
                            }
                        }
                        if (Filters[key] == "date" || Filters[key] == "datetime"){
                            startdate = this["dat_" + key + "_date1"].value.replace(" ", "T");
                            enddate = this["dat_" + key + "_date2"].value.replace(" ", "T");
                            try{
                            if (key in features[0].properties){
                            
                               for (i = features.length - 1; i >= 0; --i){
                                   if (features[i].properties[key] < startdate
                                     || features[i].properties[key] > enddate
                                     ) {
                                     features.splice(i,1);
                                   }      
                               }
                             }
                            } catch(err){
                            }
                        }
                    }
                }
                catch(err){
                }
                this[lyr["options"]["layerName"]].clearLayers();
                this[lyr["options"]["layerName"]].addData(features);
              }
            })
          }"""
        for item in range(0,filterNum):

            itemName = filterItems[item]["name"]
            if filterItems[item]["type"] in ["str", "bool"] :
                endHTML += """
            document.getElementById("menu").appendChild(document.createElement("div"));
            var div_{name} = document.createElement('div');
            div_{name}.id = "sel_{name}";
            div_{name}.className= "filterselect";
            document.getElementById("menu").appendChild(div_{name});
            sel_{name} = document.createElement('select');
            sel_{name}.multiple = true;
            var {name}_options_str = "<option value='' unselected></option>";
                    """.format(name = itemName)
                endHTML += """
            sel_%s.onchange = function(){filterFunc()};""" % itemName
                for entry in filterItems[item]["values"]:
                    endHTML += """
            {name}_options_str  += '<option value="{e}">{e}</option>';
                        """.format(e = entry, name = itemName)
                endHTML += """
            sel_{name}.innerHTML = {name}_options_str;
            div_{name}.appendChild(sel_{name});""".format(name = itemName)
                endHTML += """
                var lab_{name} = document.createElement('div');
                lab_{name}.innerHTML = '{name}';
                lab_{name}.className = 'filterLabel';
                div_{name}.appendChild(lab_{name});""".format(name = itemName)
                endHTML += """
                    """
            if filterItems[item]["type"] in ["int","real"]:
                endHTML += """
            document.getElementById("menu").appendChild(document.createElement("div"));
            var div_{name} = document.createElement("div");
            div_{name}.id = "div_{name}";
            div_{name}.className = "slider";
            document.getElementById("menu").appendChild(div_{name});
            var lab_{name} = document.createElement('p');
            lab_{name}.innerHTML  = '{name}: <span id="val_{name}"></span>';
            lab_{name}.className = 'slider';
            document.getElementById("menu").appendChild(lab_{name});
            var sel_{name} = document.getElementById('div_{name}');
            """ .format(name = itemName)
                if filterItems[item]["type"] == "int":
                    endHTML += """
            noUiSlider.create(sel_%s, {
                connect: true,
                start: [ %s, %s],
                step: 1,
                format: wNumb({
                    decimals: 0,
                    }),
                range: {
                min: %s,
                max: %s                
                }
            });
            sel_%s.noUiSlider.on('update', function (values) {
            filterVals =[];
            for (value in values){
            filterVals.push(parseInt(value))
            }
            val_%s = document.getElementById('val_%s');
            val_%s.innerHTML = values.join(' - ');
                filterFunc()
            });""" % (itemName, filterItems[item]["values"][0], 
                   filterItems[item]["values"][1], 
                   filterItems[item]["values"][0],
                   filterItems[item]["values"][1],
                   itemName, itemName, itemName, itemName)
                else:
                    endHTML += """
            noUiSlider.create(sel_%s, {
                connect: true,
                start: [ %s, %s],
                range: {
                min: %s,
                max: %s
                }
            });
            sel_%s.noUiSlider.on('update', function (values) {
            val_%s = document.getElementById('val_%s');
            val_%s.innerHTML = values.join(' - ');
                filterFunc()
            });
            """ % (itemName, filterItems[item]["values"][0],
                   filterItems[item]["values"][1], 
                   filterItems[item]["values"][0],
                   filterItems[item]["values"][1],
                   itemName, itemName, itemName, itemName)
            if filterItems[item]["type"] in ["date", "time", "datetime"]:
                if filterItems[item]["type"] == "datetime":
                    startDate = filterItems[item]["values"][0]
                    endDate = filterItems[item]["values"][1]
                if filterItems[item]["type"] == "date":
                    startDate = filterItems[item]["values"][0].toString("yyyy-MM-dd")
                    endDate = filterItems[item]["values"][1].toString("yyyy-MM-dd")
                endHTML += """
            document.getElementById("menu").appendChild(document.createElement("div"));
            var div_{name}_date1 = document.createElement("div");
            div_{name}_date1.id = "div_{name}_date1";
            div_{name}_date1.className= "filterselect";
            document.getElementById("menu").appendChild(div_{name}_date1);
            dat_{name}_date1 = document.createElement('input');
            dat_{name}_date1.type = "text";
            dat_{name}_date1.id = "dat_{name}_date1";
            div_{name}_date1.appendChild(dat_{name}_date1);
            var lab_{name}_date1 = document.createElement('p');
            lab_{name}_date1.innerHTML  = '{name} from';
            document.getElementById("div_{name}_date1").appendChild(lab_{name}_date1);""".format(
                name = itemName)
                endHTML += """
            document.addEventListener("DOMContentLoaded", function(){
                tail.DateTime("#dat_%s_date1", {
                today: false,
                weekStart: 1,
                closeButton: true,
                stayOpen: true,
                timeStepMinutes:1,
                timeStepSeconds: 1
                }).selectDate(%s,%s-1,%s,%s,%s,%s);
                tail.DateTime("#dat_%s_date1").reload() 
                """ % (itemName,
                       startDate.toString("yyyy"),
                       startDate.toString("M"),
                       startDate.toString("d"),
                       startDate.toString("h"),
                       startDate.toString("m"),
                       startDate.toString("s"),
                       itemName)
                endHTML += """
                tail.DateTime("#dat_%s_date2", {
                today: false,
                weekStart: 1,
                closeButton: true,
                stayOpen: true,
                timeStepMinutes:1,
                timeStepSeconds: 1
                }).selectDate(%s,%s-1,%s,%s,%s,%s);
                tail.DateTime("#dat_%s_date2").reload()
                dat_%s_date1.onchange = function(){filterFunc()};
                dat_%s_date2.onchange = function(){filterFunc()};
            });
            """ % (itemName,
                   endDate.toString("yyyy"),
                   endDate.toString("M"),
                   endDate.toString("d"),
                   endDate.toString("h"),
                   endDate.toString("m"),
                   endDate.toString("s"),
                   itemName,
                   itemName,
                   itemName)
                
                endHTML += """
                
            var div_{name}_date2 = document.createElement("div");
            div_{name}_date2.id = "div_{name}_date2";
            div_{name}_date2.className= "filterselect";
            document.getElementById("menu").appendChild(div_{name}_date2);
            dat_{name}_date2 = document.createElement('input');
            dat_{name}_date2.type = "text";
            dat_{name}_date2.id = "dat_{name}_date2";
            div_{name}_date2.appendChild(dat_{name}_date2);
            var lab_{name}_date2 = document.createElement('p');
            lab_{name}_date2.innerHTML  = '{name} till';
            document.getElementById("div_{name}_date2").appendChild(lab_{name}_date2);""".format(
                name = itemName)
                #endHTML += """
            #//dat_%s_date2.onchange = function(){filterFunc()};""" % (itemName)
            #if filterItems[item]["type"] == "bool":
            #    endHTML += """
            #var boo_{name} = document.createElement('div');
            #boo_{name}.id = "boo_{name}";
            #boo_{name}.className = "switch";
            #boo_{name}.innerHTML = '<label>False<input type="checkbox"><span class="lever"></span>True</label>';
            #document.getElementById("menu").appendChild(boo_{name});
            #var lab_{name}_boo = document.createElement('div');
            #lab_{name}_boo.innerHTML  = '{name}';
            #document.getElementById("menu").appendChild(lab_{name}_boo);
            #""".format(name = itemName)
            #    endHTML += """
            #boo_%s.onchange = function(){filterFunc()};""" % (itemName)
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
