import re
import os
import json
from qgis.PyQt.QtCore import QSize
from qgis.core import (QgsSingleSymbolRenderer,
                       QgsCategorizedSymbolRenderer,
                       QgsGraduatedSymbolRenderer,
                       QgsRuleBasedRenderer,
                       QgsNullSymbolRenderer,
                       QgsHeatmapRenderer,
                       QgsSymbolLayerUtils,
                       QgsDataSourceUri,
                       QgsRenderContext,
                       QgsWkbTypes,
                       QgsSvgMarkerSymbolLayer,
                       QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsProject)
from qgis2web.leafletStyleScripts import getLayerStyle
from qgis2web.leafletScriptStrings import (popupScript,
                                           popFuncsScript,
                                           pointToLayerFunction,
                                           wfsScript,
                                           clusterScript,
                                           iconLegend)
try:
    from vector_tiles_reader.plugin.util.tile_json import TileJSON
    vt_enabled = True
except ImportError:
    vt_enabled = False

from qgis2web.exp2js import compile_to_file
from qgis2web.utils import (is25d, safeName, handleHiddenField, BLEND_MODES,
                            TYPE_MAP)


def writeVectorLayer(layer, safeLayerName, usedFields, highlight,
                     popupsOnHover, popup, outputProjectFileName, wfsLayers,
                     cluster, visible, interactive, json, legends, new_src,
                     canvas, zIndex,
                     restrictToExtent, extent, feedback, labelCode, vtLabels,
                     vtStyles, useMultiStyle, useHeat, useVT, useShapes,
                     useOSMB, pbfVectorTile):
    vts = layer.customProperty("VectorTilesReader/vector_tile_url")
    pbf_enabled = pbfVectorTile[0] if pbfVectorTile else False
    feedback.showFeedback("Writing %s..." % layer.name())
    zIndex = zIndex + 400
    markerFolder = os.path.join(outputProjectFileName, "markers")
    if pbf_enabled:
        # Generate labels via companion L.geoJSON layer (L.vectorGrid.protobuf
        # doesn't support .eachLayer() on individual features)
        (labeltext, labelBuffer,
         labelBufferColor, labelBufferSize) = getPBFLabels(
             layer, safeLayerName, outputProjectFileName)
        # Popups via click handler on the vector grid layer
        (new_pop, popFuncs) = getPBFPopups(layer, safeLayerName, highlight,
                                           popupsOnHover, popup, feedback)
    else:
        (labeltext, vtLabels, labelBuffer,
         labelBufferColor, labelBufferSize) = getLabels(layer, safeLayerName,
                                        outputProjectFileName, vts, vtLabels,
                                        feedback)
        (new_pop, popFuncs) = getPopups(layer, safeLayerName, highlight,
                                        popupsOnHover, popup, vts, feedback)
    labelCode += labeltext
    renderer = layer.renderer()
    if renderer is None:
        return

    # layer_transp = 1 - (float(layer.opacity()) / 100)
    style = ""
    useMapUnits = False

    if is25d(layer, canvas, restrictToExtent, extent):
        useOSMB = True
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
            else:
                symbol = renderer.symbolForFeature(feat, renderContext)
            symbolLayer = symbol.symbolLayer(0)
            if not symbolLayer.paintEffect().effectList()[0].enabled():
                shadows = "'2015-07-15 10:00:00'"
        renderer.stopRender(renderContext)
        new_obj = """
        var osmb = new OSMBuildings(map).date(new Date({shadows}));
        osmb.set(json_{sln});""".format(shadows=shadows, sln=safeLayerName)
    elif isinstance(renderer, QgsHeatmapRenderer):
        useHeat = True
        new_obj = heatmapLayer(layer, safeLayerName, interactive, renderer,
                               feedback)
    elif pbf_enabled:
        useVT = True
        pbf_enabled, pbf_min_zoom, pbf_max_zoom = pbfVectorTile
        print("pbf_enabled", pbf_enabled, pbf_min_zoom, pbf_max_zoom)

        # generate the style as usual and pass it to getPBFLayer() to convert it to vector-grid format
        (style, markerType, useMapUnits,
         useShapes) = getLayerStyle(layer, safeLayerName, interactive,
                                    markerFolder, outputProjectFileName,
                                    useShapes, feedback)
        # generate icon for legend
        (legend, symbol) = getLegend(layer, renderer, outputProjectFileName,
                                     safeLayerName, feedback)
        legends[safeLayerName] = legend
        slCount = 0
        if symbol:
            slCount = symbol.symbolLayerCount()
        # Fix property access for vector grid (properties['...'] not feature.properties['...'])
        style = style.replace("feature.properties['", "properties['")
        new_obj = getPBFLayer(style, renderer, safeLayerName, interactive,
                              pbf_min_zoom, pbf_max_zoom, slCount, zIndex)  
    elif vts is not None:
        useVT = True
        if vts in vtStyles:
            new_obj = ""
            addVT = False
        else:
            new_obj = VTLayer(vts)
            vtStyles[vts] = {}
            addVT = True
        vtStyle = vtStyles[vts]
        (style, markerType, useMapUnits,
         useShapes) = getLayerStyle(layer, safeLayerName, interactive,
                                    markerFolder, outputProjectFileName,
                                    useShapes, feedback)
        style = style.replace("feature.properties['", "feature.['")
        if layer.name() not in vtStyle:
            vtStyle[layer.name()] = ["", "", ""]
        isLayer = False
        geom = TYPE_MAP[layer.wkbType()].replace("Multi", "")
        if geom == "Point":
            index = 0
            isLayer = True
        if geom == "LineString":
            index = 1
            isLayer = True
        if geom == "Polygon":
            index = 2
            isLayer = True
        if isLayer:
            vtStyles[vts][layer.name()][index] = style
        style = ""
    else:
        (style, markerType, useMapUnits,
         useShapes) = getLayerStyle(layer, safeLayerName, interactive,
                                    markerFolder, outputProjectFileName,
                                    useShapes, feedback)
        (legend, symbol) = getLegend(layer, renderer, outputProjectFileName,
                                     safeLayerName, feedback)
        legends[safeLayerName] = legend
        slCount = 0
        if symbol:
            slCount = symbol.symbolLayerCount()
        (new_obj, legends, wfsLayers,
         useMultiStyle) = getLayer(layer, renderer, safeLayerName, interactive,
                                   outputProjectFileName, usedFields, legends,
                                   cluster, json, wfsLayers, markerType,
                                   useMultiStyle, slCount, feedback)
    blend = BLEND_MODES[layer.blendMode()]
    if vts is None and not pbf_enabled:
        new_obj = u"""{style}
        map.createPane('pane_{sln}');
        map.getPane('pane_{sln}').style.zIndex = {zIndex};
        map.getPane('pane_{sln}').style['mix-blend-mode'] = '{blend}';
        {new_obj}""".format(style=style, sln=safeLayerName, zIndex=zIndex,
                            blend=blend, new_obj=new_obj)
    if usedFields != 0:
        new_src += new_pop
    new_src += """
""" + new_obj
    if is25d(layer, canvas, restrictToExtent, extent):
        pass
    elif vts is not None:
        if addVT:
            sln = safeName(vts)
            new_src += """
        map.addLayer(layer_""" + sln + """);"""
    else:
        new_src += """
        bounds_group.addLayer(layer_""" + safeLayerName + """);"""
        if visible:
            if cluster is False:
                new_src += """
        map.addLayer(layer_""" + safeLayerName + """);"""
            else:
                new_src += """
        cluster_""" + safeLayerName + """.addTo(map);"""
        # PBF click handler: must come after the layer is on the map
        if pbf_enabled and usedFields != 0 and visible:
            new_src += popFuncs
        # Sync label layer visibility with parent PBF layer
        if pbf_enabled and visible:
            new_src += """
        layer_""" + safeLayerName + """.on('add', function() {
            if (!map.hasLayer(label_layer_""" + safeLayerName + """)) {
                label_layer_""" + safeLayerName + """.addTo(map);
            }
        });
        layer_""" + safeLayerName + """.on('remove', function() {
            if (map.hasLayer(label_layer_""" + safeLayerName + """)) {
                map.removeLayer(label_layer_""" + safeLayerName + """);
            }
        });"""
    feedback.completeStep()
    return (new_src, legends, wfsLayers, labelCode, vtLabels, vtStyles,
            useMapUnits, useMultiStyle, useHeat, useVT, useShapes, useOSMB)


def getLabels(layer, safeLayerName, outputProjectFileName, vts, vtLabels,
              feedback):
    # label_exp = ''
    labeltext = ""
    labelBuffer = False
    labelBufferColor = None
    labelBufferSize = None
    f = ''
    labelling = layer.labeling()
    if labelling is not None and layer.labelsEnabled():
        palyr = labelling.settings()
        if palyr and palyr.fieldName and palyr.fieldName != "":
            # buffer
            labelFormat = palyr.format()
            labelBufferObj = labelFormat.buffer()
            if labelBufferObj.enabled():
                labelBuffer = True
                labelBufferColor = labelBufferObj.color().name()
                labelBufferSize = labelBufferObj.size() * 2
            props = palyr.dataDefinedProperties()
            text = palyr.format()
            bgColor = props.property(palyr.ShapeFillColor).staticValue()
            borderWidth = props.property(palyr.ShapeStrokeWidth).staticValue()
            borderColor = props.property(palyr.ShapeStrokeColor).staticValue()
            x = props.property(palyr.ShapeSizeX).staticValue()
            y = props.property(palyr.ShapeSizeY).staticValue()
            font = text.font()
            fontSize = font.pointSize()
            fontFamily = font.family()
            fontItalic = font.italic()
            fontBold = font.bold()
            fontColor = text.color().name()
            styleStart = "'<div style=\"color: %s; font-size: %dpt; " % (
                fontColor, fontSize)
            if props.property(palyr.ShapeDraw).staticValue():
                styleStart += "background-color: %s; " % bgColor
                styleStart += "border: %dpx solid %s; " % (borderWidth,
                                                           borderColor)
                if props.property(palyr.ShapeSizeType).staticValue() == 0:
                    styleStart += "padding: %dpx %dpx; " % (y, x)
                if props.property(palyr.ShapeSizeType).staticValue() == 1:
                    styleStart += "width: %dpx; " % x
                    styleStart += "height: %dpx; " % y
            if fontBold:
                styleStart += "font-weight: bold; "
            if fontItalic:
                styleStart += "font-style: italic; "
            styleStart += "font-family: \\'%s\\', sans-serif;\">' + " % (
                fontFamily)
            styleEnd = " + '</div>'"
            if palyr.isExpression:
                exprFilename = os.path.join(outputProjectFileName, "js",
                                            "qgis2web_expressions.js")
                name = compile_to_file(palyr.getLabelExpression(),
                                       "label_%s" % safeLayerName, "Leaflet",
                                       exprFilename)
                js = "%s(context)" % (name)
                js = js.strip()
                f = js
            else:
                fn = palyr.fieldName
                f = "layer.feature.properties['%s']" % handleHiddenField(layer,
                                                                         fn)
            labeltext = ".bindTooltip((" + str(f)
            labeltext += " !== null?String(%s%s).replace(/\\\\n/g, '<br>')%s:'')" % (styleStart, 
                                                                                     str(f), 
                                                                                     styleEnd)
            labeltext += ", {permanent: true, offset: [-0, -16], "
            labeltext += "className: 'css_%s'}" % safeLayerName
            labeltext += ");"
            if vts is None:
                labeltext = """
        var i = 0;
        layer_%s.eachLayer(function(layer) {
            var context = {
                feature: layer.feature,
                variables: {}
            };
            layer%s
            labels.push(layer);
            totalMarkers += 1;
              layer.added = true;
              addLabel(layer, i);
              i++;
        });""" % (safeLayerName, labeltext)
            else:
                if palyr.isExpression:
                    labelVal = f
                else:
                    labelVal = "feature.properties['%s']" % palyr.fieldName
                labeltext = """
            if (vtLayer.name === '%s') {
                var latlng = this.vtGeometryToLatLng(feature.geometry[0],
                                                     vtLayer, tileCoords)
                marker = new L.CircleMarker(latlng,
                                            {stroke: false, fill: false});
                marker.bindTooltip(String(%s).replace(/\\\\n/g, '<br>'),
                                   {permanent: true,
                                    direction: 'center'}).openTooltip();
                this.addUserLayer(marker, tileCoords);
            }""" % (layer.name(), labelVal)
                if vts not in vtLabels:
                    vtLabels[vts] = labeltext
                else:
                    vtLabels[vts] = vtLabels[vts] + labeltext
                labeltext = ""
        else:
            labeltext = ""
    else:
        labeltext = ""
    return labeltext, vtLabels, labelBuffer, labelBufferColor, labelBufferSize


def getPBFLabels(layer, safeLayerName, outputProjectFileName):
    """Generate label JavaScript for PBF vector tile layers.

    Since L.vectorGrid.protobuf doesn't support .eachLayer(), we create
    a companion L.geoJSON layer with feature centroids for labels.
    """
    labeltext = ""
    labelBuffer = False
    labelBufferColor = None
    labelBufferSize = None

    labelling = layer.labeling()
    if labelling is None or not layer.labelsEnabled():
        return labeltext, labelBuffer, labelBufferColor, labelBufferSize

    palyr = labelling.settings()
    if not palyr or not palyr.fieldName or palyr.fieldName == "":
        return labeltext, labelBuffer, labelBufferColor, labelBufferSize

    # --- Extract label formatting (same logic as getLabels) ---
    labelFormat = palyr.format()
    labelBufferObj = labelFormat.buffer()
    if labelBufferObj.enabled():
        labelBuffer = True
        labelBufferColor = labelBufferObj.color().name()
        labelBufferSize = labelBufferObj.size() * 2

    props = palyr.dataDefinedProperties()
    text = palyr.format()
    bgColor = props.property(palyr.ShapeFillColor).staticValue()
    borderWidth = props.property(palyr.ShapeStrokeWidth).staticValue()
    borderColor = props.property(palyr.ShapeStrokeColor).staticValue()
    x = props.property(palyr.ShapeSizeX).staticValue()
    y = props.property(palyr.ShapeSizeY).staticValue()
    font = text.font()
    fontSize = font.pointSize()
    fontFamily = font.family()
    fontItalic = font.italic()
    fontBold = font.bold()
    fontColor = text.color().name()

    styleStart = "'<div style=\"color: %s; font-size: %dpt; " % (
        fontColor, fontSize)
    if props.property(palyr.ShapeDraw).staticValue():
        styleStart += "background-color: %s; " % bgColor
        styleStart += "border: %dpx solid %s; " % (borderWidth, borderColor)
        if props.property(palyr.ShapeSizeType).staticValue() == 0:
            styleStart += "padding: %dpx %dpx; " % (y, x)
        if props.property(palyr.ShapeSizeType).staticValue() == 1:
            styleStart += "width: %dpx; " % x
            styleStart += "height: %dpx; " % y
    if fontBold:
        styleStart += "font-weight: bold; "
    if fontItalic:
        styleStart += "font-style: italic; "
    styleStart += "font-family: \\'%s\\', sans-serif;\">' + " % (
        fontFamily)
    styleEnd = " + '</div>'"

    # --- Build label value expression ---
    if palyr.isExpression:
        exprFilename = os.path.join(outputProjectFileName, "js",
                                    "qgis2web_expressions.js")
        name = compile_to_file(palyr.getLabelExpression(),
                               "label_%s" % safeLayerName, "Leaflet",
                               exprFilename)
        js = "%s(context)" % (name)
        f = js
        isExpression = True
    else:
        fn = palyr.fieldName
        f = "feature.properties['%s']" % handleHiddenField(layer, fn)
        isExpression = False

    inner_html = "(" + str(f) + " !== null?String(" + styleStart + str(f) + styleEnd + ").replace(/\\\\n/g, '<br>'):'')"

    # --- Build inline GeoJSON with feature centroids in EPSG:4326 ---
    features_geojson = []
    tr = QgsCoordinateTransform(
        layer.crs(),
        QgsCoordinateReferenceSystem("EPSG:4326"),
        QgsProject.instance()
    )

    for feature in layer.getFeatures():
        if feature.geometry() is None:
            continue
        geom = feature.geometry()
        if geom.type() != QgsWkbTypes.PointGeometry:
            centroid = geom.centroid()
            if centroid is None or centroid.isEmpty():
                continue
            point_geom = centroid
        else:
            point_geom = geom

        try:
            point_geom.transform(tr)
        except Exception:
            continue

        coords = [point_geom.asPoint().x(), point_geom.asPoint().y()]

        if isExpression:
            # For expressions, include all fields so the expression can reference them
            props_dict = {}
            for field in layer.fields():
                val = feature[field.name()]
                if hasattr(val, "toString"):
                    val = val.toString()
                props_dict[field.name()] = val
        else:
            props_dict = {palyr.fieldName: feature[palyr.fieldName]}

        features_geojson.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": coords},
            "properties": props_dict
        })

    geojson_str = json.dumps({"type": "FeatureCollection",
                              "features": features_geojson})

    # --- Generate JavaScript ---
    labeltext = """
        var labeldata_%(sln)s = %(geojson)s;
        var label_layer_%(sln)s = L.geoJson(labeldata_%(sln)s, {
            pointToLayer: function(feature, latlng) {
                return L.marker(latlng, {
                    icon: L.divIcon({
                        className: 'css_%(sln)s',
                        html: %(inner)s
                    })
                });
            }
        });
        // Add label layer to map so markers render and _icon is available
        label_layer_%(sln)s.addTo(map);
        var il = 0;
        label_layer_%(sln)s.eachLayer(function(layer) {
            var context = {
                feature: layer.feature,
                variables: {}
            };
            labels.push(layer);
            totalMarkers += 1;
            addLabel(layer, il);
            il++;
        });
        """ % {
            "sln": safeLayerName,
            "geojson": geojson_str,
            "inner": inner_html
        }

    return labeltext, labelBuffer, labelBufferColor, labelBufferSize


def getPopups(layer, safeLayerName, highlight, popupsOnHover, popup, vts,
              feedback):
    if vts is not None:
        return "", ""
    fields = layer.fields()
    field_names = popup.keys()
    field_vals = popup.values()

    table = ""
    for field in popup:
        tablestart = "'<table>\\"
        row = ""
        for field, val in zip(field_names, field_vals):
            fieldIndex = fields.indexFromName(str(field))
            editorWidget = layer.editorWidgetSetup(fieldIndex).type()
            displayName = layer.attributeDisplayName(fieldIndex).replace("'", "\\'")
            
            if editorWidget == 'Hidden' or val == 'hidden field':
                continue
            
            row += """
                    <tr>\\"""
            
            if val == 'inline label - always visible':
                row += """
                        <th scope="row">"""
                row += displayName
                row += """</th>\\
                        <td>"""
            elif val == "inline label - visible with data":
                row += """
                        <th scope="row">"""
                row += displayName
                row += """</th>\\
                        <td class="visible-with-data" id="""
                row += '"' + str(field) + '"' + '>'
            else:
                if val == "header label - visible with data":
                    row += """
                        <td class="visible-with-data" id="""
                    row += '"' + str(field) + '"' + ' colspan="2">'
                else:
                    row += """
                        <td colspan="2">"""
            
            if val == "header label - always visible" or val == 'header label - visible with data':
                row += '<strong>'
                row += displayName
                row += '</strong><br />'
            
            # Handle single quotes and double quotes in the field value
            row += "' + "
            row += "(feature.properties[\'" + str(field) + "\'] "
            row += "!== null ? "

            if editorWidget == 'ExternalResource':
                row += "'<img src=\"images/' + "
                row += "String(feature.properties['" + str(field) + "']"
                row += ").replace(/[\\\\/:]/g, '_').trim()"
                row += ".replace(/'/g, '\\\'')"
                row += ".replace(/\"/g, '&quot;')"
                row += " + '\">' : '') + '"
            else:
                row += "autolinker.link("
                row += "String(feature.properties['" + str(field) + "'])"
                row += ".replace(/'/g, '\\\'')"
                row += ".toLocaleString()) : '') + '"
            
            row += """</td>\\
                    </tr>\\"""
        tableend = """
                </table>'"""
        table = tablestart + row + tableend
    if popup != 0 and table != "":
        popFuncs = popFuncsScript(table)
    else:
        popFuncs = ""
    new_pop = popupScript(safeLayerName, popFuncs, highlight, popupsOnHover)
    return new_pop, popFuncs


def getPBFPopups(layer, safeLayerName, highlight, popupsOnHover, popup,
                 feedback):
    """Generate popup JavaScript for PBF vector tile layers.

    L.vectorGrid.protobuf doesn't support onEachFeature, so we attach
    a click handler on the vector grid layer that reads e.layer.properties
    and opens a standalone L.popup at the click location.
    """
    if popup == 0 or not popup:
        return "", ""
    fields = layer.fields()
    field_names = list(popup.keys())
    field_vals = list(popup.values())

    table = ""
    for _ in popup:
        tablestart = "'<table>\\"
        row = ""
        for field, val in zip(field_names, field_vals):
            fieldIndex = fields.indexFromName(str(field))
            editorWidget = layer.editorWidgetSetup(fieldIndex).type()
            displayName = layer.attributeDisplayName(fieldIndex).replace(
                "'", "\\'")

            if editorWidget == 'Hidden' or val == 'hidden field':
                continue

            row += """
                    <tr>\\"""

            if val == 'inline label - always visible':
                row += """
                        <th scope="row">"""
                row += displayName
                row += """</th>\\
                        <td>"""
            elif val == "inline label - visible with data":
                row += """
                        <th scope="row">"""
                row += displayName
                row += """</th>\\
                        <td class="visible-with-data" id="""
                row += '"' + str(field) + '"' + '>'
            else:
                if val == "header label - visible with data":
                    row += """
                        <td class="visible-with-data" id="""
                    row += '"' + str(field) + '"' + ' colspan="2">'
                else:
                    row += """
                        <td colspan="2">"""

            if (val == "header label - always visible" or
                    val == 'header label - visible with data'):
                row += '<strong>'
                row += displayName
                row += '</strong><br />'

            # Use 'properties' directly (not feature.properties) for PBF
            # since e.layer.properties has the raw attributes
            row += "' + "
            row += "(properties['" + str(field) + "'] "
            row += "!= null ? "  # != null catches both null and undefined

            if editorWidget == 'ExternalResource':
                row += "'<img src=\"images/' + "
                row += "String(properties['" + str(field) + "']"
                row += ").replace(/[\\\\/:]/g, '_').trim()"
                row += ".replace(/'/g, '\\\'')"
                row += ".replace(/\"/g, '&quot;')"
                row += " + '\">' : '') + '"
            else:
                row += "autolinker.link("
                row += "String(properties['" + str(field) + "'])"
                row += ".replace(/'/g, '\\\'')"
                row += ".toLocaleString()) : '') + '"

            row += """</td>\\
                    </tr>\\"""
        tableend = """
                </table>'"""
        table = tablestart + row + tableend
    if table == "" or "<table></table>" in table:
        return "", ""

    new_pop = """
        function getPopupContent_%(sln)s(properties) {
            return %(table)s;
        }""" % {"sln": safeLayerName, "table": table}

    # Click handler must be added AFTER layer_XXX.addTo(map), so it's returned
    # separately and appended in writeVectorLayer at the right position
    popFuncs = """
        layer_%(sln)s.on('click', function(e) {
            if (e.layer && e.layer.properties) {
                var feature = { properties: e.layer.properties };
                var content = removeEmptyRowsFromPopupContent(getPopupContent_%(sln)s(e.layer.properties), feature);
                var popup = L.popup({ maxHeight: 400 })
                    .setLatLng(e.latlng)
                    .setContent(content)
                    .openOn(map);
                setTimeout(function() {
                    addClassToPopupIfMedia(content, popup);
                }, 10);
            }
        });""" % {"sln": safeLayerName}

    return new_pop, popFuncs


def getLegend(layer, renderer, outputProjectFileName, safeLayerName, feedback):
    if isinstance(renderer, QgsSingleSymbolRenderer):
        symbol = renderer.symbol()
        if isinstance(symbol.symbolLayer(0), QgsSvgMarkerSymbolLayer):
            iconSize = int((symbol.size() * 4) + 5)
        else:
            iconSize = 16
        legendIcon = QgsSymbolLayerUtils.symbolPreviewPixmap(symbol,
                                                             QSize(iconSize, iconSize))
        legendIcon.save(os.path.join(outputProjectFileName, "legend",
                                     safeLayerName + ".png"))
        legend = ('<img src="legend/' + safeLayerName + '.png" /> ')
        legend += layer.name().replace("'", "\\'")
    elif isinstance(renderer, QgsNullSymbolRenderer):
        legend = layer.name().replace("'", "\\'")
        symbol = None
    else:
        if isinstance(renderer, QgsCategorizedSymbolRenderer):
            classes = renderer.categories()
        elif isinstance(renderer, QgsGraduatedSymbolRenderer):
            classes = renderer.ranges()
        elif isinstance(renderer, QgsRuleBasedRenderer):
            classes = renderer.rootRule().children()
        else:
            feedback.showFeedback(
                """Layer {}: legend for renderer {}
                 not supported""".format(layer.id(), renderer.type()))

        legend = layer.name().replace("'", "\\'") + "<br />"
        legend += "<table>"
        for cnt, c in enumerate(classes):
            symbol = c.symbol()
            legend = iconLegend(symbol, c, outputProjectFileName,
                                safeLayerName, legend, cnt)
        legend += "</table>"
        symbol = classes[0].symbol()
    return (legend, symbol)

def getPBFLayer(style_str, renderer, safeLayerName, interactive,
                pbf_min_zoom, pbf_max_zoom, slCount, zIndex):
    """Generate Leaflet layer + style for PBF MVT tiles."""
    min_z = 3 if pbf_min_zoom is None else int(pbf_min_zoom)
    max_z = 4 if pbf_max_zoom is None else int(pbf_max_zoom)

    # Convert style function(s) to vector-grid format
    if isinstance(renderer, QgsSingleSymbolRenderer):
        # Extract the return object from: function style_xxx_0() { return {...} }
        m = re.search(r'return\s*(\{.*?\})\s*\}', style_str, re.DOTALL)
        if m:
            style_val = re.sub(r',\s*}', '}', m.group(1).strip())
        else:
            style_val = "{}"
        style_obj = """
        var style_%s = {'%s': %s};""" % (safeLayerName, safeLayerName, style_val)
    else:
        # Categorized/graduated: fix function signature
        for sl in range(10):
            old = """
        function style_%s_%d(feature)""" % (safeLayerName, sl)
            style_str = style_str.replace(old, "function(properties, zoom)")
        # Add fallback return for features that don't match any category/range/rule
        # (prevents Leaflet.VectorGrid from using its default blue style)
        fallback = """
            return {
                pane: 'pane_%s',
                opacity: 0.5,
                color: 'rgba(0,0,0,1.0)',
                weight: 1.0,
            };""" % safeLayerName
        # Insert fallback before each function-closing `}` (8 spaces indent)
        style_str = style_str.replace("""
        }""", fallback + """
        }""")
        style_obj = """
        var style_%s = {'%s': %s};""" % (safeLayerName, safeLayerName, style_str)

    pane = """
        map.createPane('pane_%s');
        map.getPane('pane_%s').style.zIndex = %d;""" % (safeLayerName, safeLayerName, zIndex)

    layer = """
        var layer_%(sln)s = L.vectorGrid.protobuf("data/%(sln)s-pbf/{z}/{x}/{y}.pbf", {
            rendererFactory: L.svg.tile,
            vectorTileLayerStyles: style_%(sln)s,
            pane: 'pane_%(sln)s',
            minNativeZoom: %(minZ)d,
            maxNativeZoom: %(maxZ)d,
            interactive: %(int)s
        });""" % {"sln": safeLayerName, "minZ": min_z, "maxZ": max_z,
                "int": str(interactive).lower()}

    return pane + "\n" + style_obj + "\n" + layer

def getLayer(layer, renderer, safeLayerName, interactive,
             outputProjectFileName, usedFields, legends, cluster, json,
             wfsLayers, markerType, useMultiStyle, slCount, feedback):
    if layer.geometryType() == QgsWkbTypes.PointGeometry:
        (new_obj,
         wfsLayers,
         useMultiStyle) = pointLayer(layer, safeLayerName, interactive,
                                     cluster, usedFields, json, wfsLayers,
                                     markerType, slCount, useMultiStyle,
                                     feedback)
    else:
        (new_obj, wfsLayers,
         useMultiStyle) = nonPointLayer(layer, safeLayerName, interactive,
                                        usedFields, json, wfsLayers, slCount,
                                        useMultiStyle, feedback)
    return new_obj, legends, wfsLayers, useMultiStyle


def pointLayer(layer, safeLayerName, interactive, cluster, usedFields, json,
               wfsLayers, markerType, slCount, useMultiStyle, feedback):
    if layer.providerType() == 'WFS' and json is False:
        p2lf = ""
        if slCount < 1:
            slCount = 1
        for sl in range(slCount):
            p2lf += pointToLayerFunction(safeLayerName, sl)
        (new_obj,
         scriptTag,
         useMultiStyle) = buildPointWFS(p2lf, safeLayerName, layer,
                                        interactive, cluster, slCount,
                                        useMultiStyle)
        wfsLayers += wfsScript(scriptTag)
    else:
        layerAttr = ""
        attrText = layer.attribution()
        attrUrl = layer.attributionUrl()
        if attrText != "":
            layerAttr = '<a href="%s">%s</a>' % (attrUrl, attrText)
        (new_obj,
         useMultiStyle) = buildPointJSON(slCount, safeLayerName, usedFields,
                                         interactive, markerType, layerAttr,
                                         useMultiStyle)
        if cluster:
            new_obj += clusterScript(safeLayerName)
    return new_obj, wfsLayers, useMultiStyle


def nonPointLayer(layer, safeLayerName, interactive, usedFields, json,
                  wfsLayers, slCount, useMultiStyle, feedback):
    if layer.providerType() == 'WFS' and json is False:
        (new_obj, scriptTag,
         useMultiStyle) = buildNonPointWFS(safeLayerName, layer, slCount,
                                           interactive, useMultiStyle)
        wfsLayers += wfsScript(scriptTag)
    else:
        layerAttr = ""
        attrText = layer.attribution().replace('\n', ' ').replace('\r', ' ')
        attrUrl = layer.attributionUrl()
        if attrText != "":
            layerAttr = u'<a href="%s">%s</a>' % (attrUrl, attrText)
        new_obj, useMultiStyle = buildNonPointJSON(safeLayerName, usedFields,
                                                   layerAttr, interactive,
                                                   slCount, useMultiStyle)
    return new_obj, wfsLayers, useMultiStyle


def heatmapLayer(layer, safeLayerName, interactive, renderer, feedback):
    attrText = layer.attribution()
    if attrText != "":
        attrUrl = layer.attributionUrl()
        layerAttr = '<a href="%s">%s</a>' % (attrUrl, attrText)
    else:
        layerAttr = ""
    hmRadius = renderer.radius() * 2
    hmWeight = renderer.weightExpression()
    if hmWeight is not None and hmWeight != "":
        hmWeightId = layer.fields().indexFromName(hmWeight)
        hmWeightMax = layer.maximumValue(hmWeightId)
    else:
        hmWeight = ""
        hmWeightMax = 1
    colorRamp = renderer.colorRamp()
    hmStart = colorRamp.color1().name()
    hmEnd = colorRamp.color2().name()
    hmRamp = "{0: '" + hmStart + "', "
    hmStops = colorRamp.stops()
    for stop in hmStops:
        hmRamp += str(stop.offset) + ": '" + stop.color.name() + "', "
    hmRamp += "1: '" + hmEnd + "'}"
    new_obj = """
        var %(sln)s_hm = geoJson2heat(json_%(sln)s,
                                      '%(hmWeight)s');
        var layer_%(sln)s = new L.heatLayer(%(sln)s_hm, {
            attribution: '%(attr)s',
            interactive: %(int)s,
            radius: %(hmRadius)d,
            max: %(hmWeightMax)d,
            minOpacity: 1,
            gradient: %(hmRamp)s});
        """ % {"sln": safeLayerName, "hmWeight": hmWeight, "attr": layerAttr,
               "int": str(interactive).lower(), "hmWeightMax": hmWeightMax,
               "hmRamp": hmRamp, "hmRadius": hmRadius}
    return new_obj


def VTLayer(json_url):
    sln = safeName(json_url)
    try:
        key = json_url.split("?")[1]
    except Exception:
        key = ""
    json = TileJSON(json_url)
    json.load()
    tile_url = json.tiles()[0].split("?")[0]
    key_url = "%s?%s" % (tile_url, key)
    styleSuffix = safeName(json_url)
    vtJS = """
        var layer_%s = L.vectorGrid.protobuf("%s", {
            rendererFactory: L.svg.tile,
            //onEachFeature: label_%s,
            vectorTileLayerStyles: style_%s
        });""" % (sln, key_url, sln, styleSuffix)
    return vtJS


def buildPointJSON(slCount, sln, usedFields, interactive, markerType, layerAttr,
                   useMultiStyle):
    multiStyle = ""
    if slCount > 1:
        multiStyle = ".multiStyle"
        useMultiStyle = True
    pointJSON = """
        var layer_{sln} = new L.geoJson%s(json_{sln}, {{
            attribution: '{attr}',
            interactive: {int},
            dataVar: 'json_{sln}',
            layerName: 'layer_{sln}',
            pane: 'pane_{sln}',""" % multiStyle
    if usedFields != 0:
        pointJSON += """
            onEachFeature: pop_{sln},"""
    if slCount > 1:
        pointJSON += """
            pointToLayers: ["""
        for sl in range(slCount):
            pointJSON += """function (feature, latlng) {{
                var context = {{
                    feature: feature,
                    variables: {{}}
                }};
                return L.{markerType}(latlng, """
            pointJSON += """style_{sln}_%s(feature));
            }},""" % sl
    else:
        pointJSON += """
            pointToLayer: function (feature, latlng) {{
                var context = {{
                    feature: feature,
                    variables: {{}}
                }};
                return L.{markerType}(latlng, style_{sln}_0(feature));
            }},"""
    if slCount > 1:
        pointJSON += """
        ]}});"""
    else:
        pointJSON += """
        }});"""
    pointJSON = pointJSON.format(sln=sln, int=str(interactive).lower(),
                                 markerType=markerType, attr=layerAttr)
    return (pointJSON, useMultiStyle)


def buildPointWFS(p2lf, layerName, layer, interactive, cluster_set, slCount,
                  useMultiStyle):
    layerAttr = ""
    attrText = layer.attribution()
    attrUrl = layer.attributionUrl()
    if attrText != "":
        layerAttr = '<a href="%s">%s</a>' % (attrUrl, attrText)
    scriptTag = getWFSScriptTag(layer, layerName)
    p2ls = ""
    multiStyle = ""
    p2lStart = "pointToLayer: "
    p2lEnd = ""
    if slCount > 1:
        multiStyle = ".multiStyle"
        useMultiStyle = True
        p2lStart = "pointToLayers: ["
        p2lEnd = "],"
        for sl in range(slCount):
            p2ls += "pointToLayer_%s_%s, " % (layerName, sl)
    else:
        p2ls = "pointToLayer_%s_0, " % layerName
    new_obj = p2lf + """
        var layer_{layerName} = L.geoJson{multiStyle}(null, {{
            attribution: '{layerAttr}',
            interactive: {int},
            dataVar: 'json_{layerName}',
            layerName: 'layer_{layerName}',
            pane: 'pane_{layerName}',
            {p2lStart}{p2ls}{p2lEnd}
            onEachFeature: pop_{layerName}
        }});""".format(layerName=layerName, multiStyle=multiStyle,
                       layerAttr=layerAttr, int=str(interactive).lower(),
                       p2lStart=p2lStart, p2ls=p2ls, p2lEnd=p2lEnd)
    if cluster_set:
        new_obj += """
        var cluster_{layerName} = """.format(layerName=layerName)
        new_obj += "new L.MarkerClusterGroup({showCoverageOnHover: false});"
    new_obj += """
        function get{layerName}Json(geojson) {{
            layer_{layerName}""".format(layerName=layerName)
    new_obj += ".addData(geojson);"
    if cluster_set:
        new_obj += """
            cluster_{layerName}.add""".format(layerName=layerName)
        new_obj += "Layer(layer_{layerName});".format(layerName=layerName)
    new_obj += """
            setBounds();
        };"""
    return new_obj, scriptTag, useMultiStyle


def buildNonPointJSON(safeName, usedFields, layerAttr, interactive, slCount,
                      useMultiStyle):
    if usedFields != 0:
        onEachFeature = u"""
            onEachFeature: pop_{safeName},""".format(safeName=safeName)
    else:
        onEachFeature = u""
    styles = u""
    multiStyle = u""
    styleStart = "style: "
    styleEnd = ""
    if slCount > 1:
        multiStyle = u".multiStyle"
        useMultiStyle = True
        styleStart = u"styles: ["
        styleEnd = u"]"
        for sl in range(slCount):
            styles += u"""style_%s_%s,""" % (safeName, sl)
    else:
        styles = u"""style_%s_0,""" % safeName
    new_obj = u"""
        var layer_{safeName} = new L.geoJson{multiStyle}(json_{safeName}, {{
            attribution: '{attr}',
            interactive: {int},
            dataVar: 'json_{safeName}',
            layerName: 'layer_{safeName}',
            pane: 'pane_{safeName}',{onEachFeature}
            {styleStart}{styles}{styleEnd}
        }});"""
    new_obj = new_obj.format(safeName=safeName, multiStyle=multiStyle,
                             attr=layerAttr, int=str(interactive).lower(),
                             onEachFeature=onEachFeature,
                             styleStart=styleStart, styles=styles,
                             styleEnd=styleEnd)
    return new_obj, useMultiStyle


def buildNonPointWFS(layerName, layer, slCount, interactive, useMultiStyle):
    layerAttr = ""
    attrText = layer.attribution()
    attrUrl = layer.attributionUrl()
    if attrText != "":
        layerAttr = '<a href="%s">%s</a>' % (attrUrl, attrText)
    scriptTag = getWFSScriptTag(layer, layerName)
    styles = ""
    multiStyle = ""
    styleStart = "style: "
    styleEnd = ""
    if slCount > 1:
        multiStyle = ".multiStyle"
        useMultiStyle = True
        styleStart = "styles: ["
        styleEnd = "],"
        for sl in range(slCount):
            styles += """style_%s_%s,""" % (layerName, sl)
    else:
        styles = """style_%s_0,""" % layerName
    new_obj = """
        var layer_{layerName} = L.geoJson{multiStyle}(null, {{
            attribution: '{attr}',
            interactive: {int},
            dataVar: 'json_{layerName}',
            layerName: 'layer_{layerName}',
            {styleStart}{styles}{styleEnd}
            pane: 'pane_{layerName}',
            onEachFeature: pop_{layerName}
        }});"""
    new_obj += """
        function get{layerName}Json(geojson) {{
            layer_{layerName}"""
    new_obj = new_obj.format(layerName=layerName, multiStyle=multiStyle,
                             attr=layerAttr, int=str(interactive).lower(),
                             styleStart=styleStart, styles=styles,
                             styleEnd=styleEnd)
    new_obj += ".addData(geojson);"
    new_obj += """
        };"""
    return new_obj, scriptTag, useMultiStyle


def getWFSScriptTag(layer, layerName):
    layerSource = layer.source()
    if ("retrictToRequestBBOX" in layerSource or
            "restrictToRequestBBOX" in layerSource):
        provider = layer.dataProvider()
        uri = QgsDataSourceUri(provider.dataSourceUri())
        wfsURL = uri.param("url")
        wfsTypename = uri.param("typename")
        wfsSRS = uri.param("srsname")
        layerSource = wfsURL
        layerSource += "?SERVICE=WFS&VERSION=1.0.0&"
        layerSource += "REQUEST=GetFeature&TYPENAME="
        layerSource += wfsTypename
        layerSource += "&SRSNAME="
        layerSource += wfsSRS
    scriptTag = re.sub(r'SRSNAME\=EPSG\:\d+', 'SRSNAME=EPSG:4326', layerSource)
    scriptTag += "&outputFormat=text%2Fjavascript&format_options=callback%3A"
    scriptTag += "get" + layerName + "Json"
    return scriptTag
