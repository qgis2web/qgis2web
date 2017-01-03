import re
import os
import shutil
import tempfile
from PyQt4.QtCore import QSize, QVariant
import time
from qgis.core import *
from qgis.utils import QGis
import processing
from leafletStyleScripts import getLayerStyle
from leafletScriptStrings import *
from utils import (writeTmpLayer, getUsedFields, removeSpaces,
                   is25d, exportImages, handleHiddenField, BLEND_MODES)


def exportJSONLayer(layer, eachPopup, precision, tmpFileName, exp_crs,
                    layerFileName, safeLayerName, minify, canvas):
    cleanedLayer = writeTmpLayer(layer, eachPopup)
    if is25d(layer, canvas):
        provider = cleanedLayer.dataProvider()
        provider.addAttributes([QgsField("height", QVariant.Double),
                                QgsField("wallColor", QVariant.String),
                                QgsField("roofColor", QVariant.String)])
        cleanedLayer.updateFields()
        fields = cleanedLayer.pendingFields()
        renderer = layer.rendererV2()
        renderContext = QgsRenderContext.fromMapSettings(
                canvas.mapSettings())
        feats = layer.getFeatures()
        context = QgsExpressionContext()
        context.appendScope(QgsExpressionContextUtils.layerScope(layer))
        expression = QgsExpression('eval(@qgis_25d_height)')
        heightField = fields.indexFromName("height")
        wallField = fields.indexFromName("wallColor")
        roofField = fields.indexFromName("roofColor")
        renderer.startRender(renderContext, fields)
        cleanedLayer.startEditing()
        for feat in feats:
            context.setFeature(feat)
            height = expression.evaluate(context)
            if isinstance(renderer, QgsCategorizedSymbolRendererV2):
                classAttribute = renderer.classAttribute()
                attrValue = feat.attribute(classAttribute)
                catIndex = renderer.categoryIndexForValue(attrValue)
                categories = renderer.categories()
                symbol = categories[catIndex].symbol()
            elif isinstance(renderer, QgsGraduatedSymbolRendererV2):
                classAttribute = renderer.classAttribute()
                attrValue = feat.attribute(classAttribute)
                ranges = renderer.ranges()
                for range in ranges:
                    if (attrValue >= range.lowerValue() and
                            attrValue <= range.upperValue()):
                        symbol = range.symbol().clone()
            else:
                symbol = renderer.symbolForFeature2(feat, renderContext)
            wallColor = symbol.symbolLayer(1).subSymbol().color().name()
            roofColor = symbol.symbolLayer(2).subSymbol().color().name()
            cleanedLayer.changeAttributeValue(feat.id() + 1,
                                              heightField, height)
            cleanedLayer.changeAttributeValue(feat.id() + 1,
                                              wallField, wallColor)
            cleanedLayer.changeAttributeValue(feat.id() + 1,
                                              roofField, roofColor)
        cleanedLayer.commitChanges()
        renderer.stopRender(renderContext)

    writer = QgsVectorFileWriter
    if precision != "maintain":
        options = "COORDINATE_PRECISION=" + unicode(precision)
    else:
        options = ""
    writer.writeAsVectorFormat(cleanedLayer, tmpFileName, 'utf-8', exp_crs,
                               'GeoJson', 0, layerOptions=[options])

    with open(layerFileName, "w") as f2:
        f2.write("var json_" + unicode(safeLayerName) + "=")
        with open(tmpFileName, "r") as tmpFile:
            for line in tmpFile:
                if minify:
                    line = line.strip("\n\t ")
                    line = removeSpaces(line)
                f2.write(line)
        os.remove(tmpFileName)

    fields = layer.pendingFields()
    for field in fields:
        exportImages(layer, field.name(), layerFileName)


def exportRasterLayer(layer, safeLayerName, dataPath):
    name_ts = safeLayerName + unicode(int(time.time()))

    # We need to create a new file to export style
    piped_file = os.path.join(
        tempfile.gettempdir(),
        name_ts + '_piped.tif'
    )

    piped_extent = layer.extent()
    piped_width = layer.height()
    piped_height = layer.width()
    piped_crs = layer.crs()
    piped_renderer = layer.renderer()
    piped_provider = layer.dataProvider()

    pipe = QgsRasterPipe()
    pipe.set(piped_provider.clone())
    pipe.set(piped_renderer.clone())

    file_writer = QgsRasterFileWriter(piped_file)

    file_writer.writeRaster(pipe,
                            piped_width,
                            piped_height,
                            piped_extent,
                            piped_crs)

    # Extent of the layer in EPSG:3857
    crsSrc = layer.crs()
    crsDest = QgsCoordinateReferenceSystem(3857)
    xform = QgsCoordinateTransform(crsSrc, crsDest)
    extentRep = xform.transform(layer.extent())

    extentRepNew = ','.join([unicode(extentRep.xMinimum()),
                            unicode(extentRep.xMaximum()),
                            unicode(extentRep.yMinimum()),
                            unicode(extentRep.yMaximum())])

    # Reproject in 3857
    piped_3857 = os.path.join(tempfile.gettempdir(),
                              name_ts + '_piped_3857.tif')

    # Export layer as PNG
    out_raster = dataPath + '.png'

    qgis_version = QGis.QGIS_VERSION

    if int(qgis_version.split('.')[1]) < 15:

        processing.runalg("gdalogr:warpreproject", piped_file,
                          layer.crs().authid(), "EPSG:3857", "", 0, 1,
                          0, -1, 75, 6, 1, False, 0, False, "",
                          piped_3857)
        processing.runalg("gdalogr:translate", piped_3857, 100,
                          True, "", 0, "", extentRepNew, False, 0,
                          0, 75, 6, 1, False, 0, False, "",
                          out_raster)
    else:
        try:
            warpArgs = {
                "INPUT": piped_file,
                "SOURCE_SRS": layer.crs().authid(),
                "DEST_SRS": "EPSG:3857",
                "NO_DATA": "",
                "TR": 0,
                "METHOD": 2,
                "RAST_EXT": extentRepNew,
                "EXT_CRS": "EPSG:3857",
                "RTYPE": 0,
                "COMPRESS": 4,
                "JPEGCOMPRESSION": 75,
                "ZLEVEL": 6,
                "PREDICTOR": 1,
                "TILED": False,
                "BIGTIFF": 0,
                "TFW": False,
                "EXTRA": "",
                "OUTPUT": piped_3857
            }
            procRtn = processing.runalg("gdalogr:warpreproject", warpArgs)
            # force exception on algorithm fail
            for val in procRtn:
                pass
        except:
            try:
                warpArgs = {
                    "INPUT": piped_file,
                    "SOURCE_SRS": layer.crs().authid(),
                    "DEST_SRS": "EPSG:3857",
                    "NO_DATA": "",
                    "TR": 0,
                    "METHOD": 2,
                    "RAST_EXT": extentRepNew,
                    "RTYPE": 0,
                    "COMPRESS": 4,
                    "JPEGCOMPRESSION": 75,
                    "ZLEVEL": 6,
                    "PREDICTOR": 1,
                    "TILED": False,
                    "BIGTIFF": 0,
                    "TFW": False,
                    "EXTRA": "",
                    "OUTPUT": piped_3857
                }
                procRtn = processing.runalg("gdalogr:warpreproject", warpArgs)
                # force exception on algorithm fail
                for val in procRtn:
                    pass
            except:
                try:
                    warpArgs = {
                        "INPUT": piped_file,
                        "SOURCE_SRS": layer.crs().authid(),
                        "DEST_SRS": "EPSG:3857",
                        "NO_DATA": "",
                        "TR": 0,
                        "METHOD": 2,
                        "RTYPE": 0,
                        "COMPRESS": 4,
                        "JPEGCOMPRESSION": 75,
                        "ZLEVEL": 6,
                        "PREDICTOR": 1,
                        "TILED": False,
                        "BIGTIFF": 0,
                        "TFW": False,
                        "EXTRA": "",
                        "OUTPUT": piped_3857
                    }
                    procRtn = processing.runalg("gdalogr:warpreproject",
                                                warpArgs)
                    for val in procRtn:
                        pass
                except:
                    shutil.copyfile(piped_file, piped_3857)

        try:
            processing.runalg("gdalogr:translate", piped_3857, 100,
                              True, "", 0, "", extentRepNew, False, 5,
                              4, 75, 6, 1, False, 0, False, "",
                              out_raster)
        except:
            shutil.copyfile(piped_3857, out_raster)


def writeVectorLayer(layer, safeLayerName, usedFields, highlight,
                     popupsOnHover, popup, outputProjectFileName, wfsLayers,
                     cluster, visible, json, legends, new_src, canvas, zIndex):
    zIndex = zIndex + 600
    markerFolder = os.path.join(outputProjectFileName, "markers")
    (new_pop, labeltext,
     popFuncs) = labelsAndPopups(layer, safeLayerName, highlight,
                                 popupsOnHover, popup)
    renderer = layer.rendererV2()
    layer_transp = 1 - (float(layer.layerTransparency()) / 100)
    style = ""

    if is25d(layer, canvas):
        shadows = ""
        renderer = layer.rendererV2()
        renderContext = QgsRenderContext.fromMapSettings(canvas.mapSettings())
        fields = layer.pendingFields()
        renderer.startRender(renderContext, fields)
        for feat in layer.getFeatures():
            if isinstance(renderer, QgsCategorizedSymbolRendererV2):
                classAttribute = renderer.classAttribute()
                attrValue = feat.attribute(classAttribute)
                catIndex = renderer.categoryIndexForValue(attrValue)
                categories = renderer.categories()
                symbol = categories[catIndex].symbol()
            elif isinstance(renderer, QgsGraduatedSymbolRendererV2):
                classAttribute = renderer.classAttribute()
                attrValue = feat.attribute(classAttribute)
                ranges = renderer.ranges()
                for range in ranges:
                    if (attrValue >= range.lowerValue() and
                            attrValue <= range.upperValue()):
                        symbol = range.symbol().clone()
            else:
                symbol = renderer.symbolForFeature2(feat, renderContext)
            symbolLayer = symbol.symbolLayer(0)
            if not symbolLayer.paintEffect().effectList()[0].enabled():
                shadows = "'2015-07-15 10:00:00'"
        renderer.stopRender(renderContext)
        new_obj = """
        var osmb = new OSMBuildings(map).date(new Date({shadows}));
        osmb.set(json_{sln});""".format(shadows=shadows, sln=safeLayerName)
    # else:
    #     layer_style = getLayerStyle(layer, safeLayerName)
    elif isinstance(renderer, QgsHeatmapRenderer):
        (new_obj, legends,
         wfsLayers) = heatmapLayer(layer, safeLayerName, renderer, legends,
                                   wfsLayers)
    elif (isinstance(renderer, QgsSingleSymbolRendererV2) or
            isinstance(renderer, QgsRuleBasedRendererV2)):
        (style, markerType) = getLayerStyle(layer, safeLayerName, markerFolder)
        (new_obj, legends,
         wfsLayers) = singleLayer(renderer, outputProjectFileName,
                                  safeLayerName, wfsLayers, layer, labeltext,
                                  cluster, json, usedFields, legends,
                                  markerType)
    elif isinstance(renderer, QgsCategorizedSymbolRendererV2):
        (style, markerType) = getLayerStyle(layer, safeLayerName, markerFolder)
        (new_obj, legends,
         wfsLayers) = categorizedLayer(layer, renderer, safeLayerName,
                                       outputProjectFileName, usedFields,
                                       legends, labeltext, cluster, json,
                                       wfsLayers, markerType)
    elif isinstance(renderer, QgsGraduatedSymbolRendererV2):
        (style, markerType) = getLayerStyle(layer, safeLayerName, markerFolder)
        (new_obj, legends,
         wfsLayers) = graduatedLayer(layer, safeLayerName, renderer,
                                     outputProjectFileName, labeltext, cluster,
                                     json, usedFields, legends, wfsLayers,
                                     markerType)
    blend = BLEND_MODES[layer.blendMode()]
    new_obj = """{style}
        map.createPane('pane_{sln}');
        map.getPane('pane_{sln}').style.zIndex = {zIndex};
        map.getPane('pane_{sln}').style['mix-blend-mode'] = '{blend}';
        {new_obj}""".format(
            style=style, sln=safeLayerName, zIndex=zIndex,
            blend=blend, new_obj=new_obj)
    if usedFields != 0:
        new_src += new_pop.decode("utf-8")
    new_src += """
""" + new_obj
    if is25d(layer, canvas):
        pass
    else:
        new_src += """
        bounds_group.addLayer(layer_""" + safeLayerName + """);"""
        if visible:
            if cluster is False:
                new_src += """
        feature_group.addLayer(layer_""" + safeLayerName + """);"""
            else:
                new_src += """
        cluster_""" + safeLayerName + """.addTo(map);"""
    return new_src, legends, wfsLayers


def labelsAndPopups(layer, safeLayerName, highlight, popupsOnHover, popup):
    fields = layer.pendingFields()
    field_names = popup.keys()
    field_vals = popup.values()
    html_prov = False
    label_exp = ''
    labeltext = ""
    f = ''
    palyr = QgsPalLayerSettings()
    palyr.readFromLayer(layer)
    bgColor = palyr.shapeFillColor.name()
    borderWidth = palyr.shapeBorderWidth
    borderColor = palyr.shapeBorderColor.name()
    x = palyr.shapeSize.x()
    y = palyr.shapeSize.y()
    font = palyr.textFont
    fontSize = font.pointSize()
    fontFamily = font.family()
    fontItalic = font.italic()
    fontBold = font.bold()
    fontColor = palyr.textColor.name()
    fontUnderline = font.underline()
    xOffset = palyr.xOffset
    yOffset = palyr.yOffset
    styleStart = "'<div style=\"color: %s; font-size: %dpt; " % (
            fontColor, fontSize)
    if palyr.shapeDraw:
        styleStart += "background-color: %s; " % bgColor
        styleStart += "border: %dpx solid %s; " % (borderWidth, borderColor)
        if palyr.shapeSizeType == 0:
            styleStart += "padding: %dpx %dpx; " % (y, x)
        if palyr.shapeSizeType == 1:
            styleStart += "width: %dpx; " % x
            styleStart += "height: %dpx; " % y
    if fontBold:
        styleStart += "font-weight: bold; "
    if fontItalic:
        styleStart += "font-style: italic; "
    styleStart += "font-family: \\'%s\\', sans-serif;\">' + " % fontFamily
    styleEnd = " + '</div>'"
    f = handleHiddenField(layer, palyr.fieldName)
    label_exp = False
    labeltext = ".bindTooltip((feature.properties['" + unicode(f)
    labeltext += "'] !== null?String(%sfeature.properties['%s'])%s:'')" % (
            styleStart, unicode(f), styleEnd)
    labeltext += ", {permanent: true, offset: [-0, -16], "
    labeltext += "className: 'css_%s'}" % safeLayerName
    labeltext += ").openTooltip();"
    f = palyr.fieldName
    table = ""
    for field in popup:
        if unicode(field) == 'html_exp':
            html_prov = True
            table = 'feature.properties.html_exp'
        if (unicode(f) != "" and
                f and palyr.enabled):
            label_exp = True
        if not html_prov:
            tablestart = "'<table>\\"
            row = ""
            for field, val in zip(field_names, field_vals):
                fieldIndex = fields.indexFromName(unicode(field))
                try:
                    formCfg = layer.editFormConfig()
                    editorWidget = formCfg.widgetType(fieldIndex)
                except:
                    editorWidget = layer.editorWidgetV2(fieldIndex)
                if (editorWidget == QgsVectorLayer.Hidden or
                        editorWidget == 'Hidden'):
                    continue

                row += """
                    <tr>\\"""
                if val == 'inline label':
                    row += """
                        <th scope="row">"""
                    row += layer.attributeDisplayName(fieldIndex)
                    row += """</th>\\
                        <td>"""
                else:
                    row += """
                        <td colspan="2">"""
                if val == "header label":
                    row += '<strong>'
                    row += layer.attributeDisplayName(fieldIndex)
                    row += '</strong><br />'
                row += "' + "
                row += "(feature.properties[\'" + unicode(field) + "\'] "
                row += "!== null ? "

                if (editorWidget == QgsVectorLayer.Photo or
                        editorWidget == 'Photo'):
                    row += "'<img src=\"images/' + "
                    row += "String(feature.properties['" + unicode(field)
                    row += "']).replace(/[\\\/:]/g, '_').trim()"
                    row += " + '\">' : '') + '"
                else:
                    row += "Autolinker.link("
                    row += "String(feature.properties['" + unicode(field)
                    row += "'])) : '') + '"

                row += """</td>\\
                    </tr>\\"""
            tableend = """
                </table>'"""
            table = tablestart + row + tableend
    if not label_exp:
        labeltext = ""
    if popup != 0 and table != "":
        popFuncs = popFuncsScript(table)
    else:
        popFuncs = ""
    new_pop = popupScript(safeLayerName, popFuncs, highlight, popupsOnHover)
    return new_pop, labeltext, popFuncs


def singleLayer(renderer, outputProjectFileName, safeLayerName, wfsLayers,
                layer, labeltext, cluster, json, usedFields, legends,
                markerType):
    if isinstance(renderer, QgsRuleBasedRendererV2):
        symbol = renderer.rootRule().children()[0].symbol()
    else:
        symbol = renderer.symbol()
    legendIcon = QgsSymbolLayerV2Utils.symbolPreviewPixmap(symbol,
                                                           QSize(16, 16))
    legendIcon.save(os.path.join(outputProjectFileName, "legend",
                                 safeLayerName + ".png"))
    legends[safeLayerName] = '<img src="legend/' + safeLayerName + '.png" /> '
    legends[safeLayerName] += layer.name()
    if layer.geometryType() == QGis.Point:
        (new_obj,
         wfsLayers) = pointLayer(layer, safeLayerName, labeltext, cluster,
                                 usedFields, json, wfsLayers, markerType,
                                 renderer.symbol())
    else:
        new_obj, wfsLayers = nonPointLayer(layer, safeLayerName, usedFields,
                                           json, wfsLayers)
    return new_obj, legends, wfsLayers


def categorizedLayer(layer, renderer, safeLayerName, outputProjectFileName,
                     usedFields, legends, labeltext, cluster, json, wfsLayers,
                     markerType):
    catLegend = layer.name() + "<br />"
    catLegend += "<table>"
    categories = renderer.categories()
    for cnt, cat in enumerate(categories):
        symbol = cat.symbol()
        catLegend = iconLegend(symbol, cat, outputProjectFileName,
                               safeLayerName, catLegend, cnt)
    catLegend += "</table>"
    if layer.geometryType() == QGis.Point:
        (new_obj,
         wfsLayers) = pointLayer(layer, safeLayerName, labeltext, cluster,
                                 usedFields, json, wfsLayers, markerType,
                                 symbol)
    else:
        (new_obj,
         wfsLayers) = nonPointLayer(layer, safeLayerName, usedFields, json,
                                    wfsLayers)
    legends[safeLayerName] = catLegend
    return new_obj, legends, wfsLayers


def graduatedLayer(layer, safeLayerName, renderer, outputProjectFileName,
                   labeltext, cluster, json, usedFields, legends, wfsLayers,
                   markerType):
    catLegend = layer.name() + "<br />"
    catLegend += "<table>"
    for cnt, r in enumerate(renderer.ranges()):
        symbol = r.symbol()
        catLegend = iconLegend(symbol, r, outputProjectFileName, safeLayerName,
                               catLegend, cnt)
    catLegend += "</table>"
    if layer.geometryType() == QGis.Point:
        (new_obj,
         wfsLayers) = pointLayer(layer, safeLayerName, labeltext, cluster,
                                 usedFields, json, wfsLayers, markerType,
                                 symbol)
    else:
        (new_obj,
         wfsLayers) = nonPointLayer(layer, safeLayerName, usedFields, json,
                                    wfsLayers)
    legends[safeLayerName] = catLegend
    return new_obj, legends, wfsLayers


def pointLayer(layer, safeLayerName, labeltext, cluster, usedFields, json,
               wfsLayers, markerType, symbol):
    if layer.providerType() == 'WFS' and json is False:
        p2lf = pointToLayerFunction(safeLayerName, labeltext, symbol)
        (new_obj,
         scriptTag) = buildPointWFS(p2lf, safeLayerName, layer, cluster)
        wfsLayers += wfsScript(scriptTag)
    else:
        new_obj = pointJSONLayer(safeLayerName, labeltext,
                                 usedFields, markerType)
        if cluster:
            new_obj += clusterScript(safeLayerName)
    return new_obj, wfsLayers


def nonPointLayer(layer, safeLayerName, usedFields, json, wfsLayers):
    if layer.providerType() == 'WFS' and json is False:
        new_obj, scriptTag = buildNonPointWFS(safeLayerName, layer)
        wfsLayers += wfsScript(scriptTag)
    else:
        new_obj = buildNonPointJSON(safeLayerName, usedFields)
    return new_obj, wfsLayers


def heatmapLayer(layer, safeLayerName, renderer, legends, wfsLayers):
    hmRadius = renderer.radius() * 2
    hmWeight = renderer.weightExpression()
    if hmWeight is not None and hmWeight != "":
        hmWeightId = layer.fieldNameIndex(hmWeight)
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
        hmRamp += unicode(stop.offset) + ": '" + stop.color.name() + "', "
    hmRamp += "1: '" + hmEnd + "'}"
    new_obj = """
        var %(sln)s_hm = geoJson2heat(json_%(sln)s,
                                      '%(hmWeight)s');
        var layer_%(sln)s = new L.heatLayer(%(sln)s_hm, {
            radius: %(hmRadius)d,
            max: %(hmWeightMax)d,
            minOpacity: 1,
            gradient: %(hmRamp)s});
        """ % {"sln": safeLayerName, "hmWeight": hmWeight,
               "hmWeightMax": hmWeightMax, "hmRamp": hmRamp,
               "hmRadius": hmRadius}
    return new_obj, legends, wfsLayers


def buildPointWFS(p2lf, layerName, layer, cluster_set):
    scriptTag = getWFSScriptTag(layer, layerName)
    new_obj = p2lf + """
        var layer_{layerName} = L.geoJson(null, {{
            pane: 'pane_{layerName}',
            pointToLayer: pointToLayer_{layerName},
            onEachFeature: pop_{layerName}
        }});""".format(layerName=layerName)
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
    return new_obj, scriptTag


def buildNonPointJSON(safeName, usedFields):
    if usedFields != 0:
        onEachFeature = """
        onEachFeature: pop_{safeName},""".format(safeName=safeName)
    else:
        onEachFeature = ""
    new_obj = """
    var layer_{safeName} = new L.geoJson(json_{safeName}, {{
        pane: 'pane_{safeName}',{onEachFeature}
        style: style_{safeName}
    }});"""
    new_obj = new_obj.format(safeName=safeName, onEachFeature=onEachFeature)
    new_obj = new_obj

    return new_obj


def buildNonPointWFS(layerName, layer):
    scriptTag = getWFSScriptTag(layer, layerName)
    new_obj = """
        var layer_{layerName} = L.geoJson(null, {{
            style: style_{layerName},
            pane: 'pane_{layerName}',
            onEachFeature: pop_{layerName}
        }});"""
    new_obj += """
        function get{layerName}Json(geojson) {{
            layer_{layerName}"""
    new_obj = new_obj.format(layerName=layerName)
    new_obj += ".addData(geojson);"
    new_obj += """
        };"""
    return new_obj, scriptTag


def getWFSScriptTag(layer, layerName):
    layerSource = layer.source()
    if ("retrictToRequestBBOX" in layerSource or
            "restrictToRequestBBOX" in layerSource):
        provider = layer.dataProvider()
        uri = QgsDataSourceURI(provider.dataSourceUri())
        wfsURL = uri.param("url")
        wfsTypename = uri.param("typename")
        wfsSRS = uri.param("srsname")
        layerSource = wfsURL
        layerSource += "?SERVICE=WFS&VERSION=1.0.0&"
        layerSource += "REQUEST=GetFeature&TYPENAME="
        layerSource += wfsTypename
        layerSource += "&SRSNAME="
        layerSource += wfsSRS
    scriptTag = re.sub('SRSNAME\=EPSG\:\d+', 'SRSNAME=EPSG:4326', layerSource)
    scriptTag += "&outputFormat=text%2Fjavascript&format_options=callback%3A"
    scriptTag += "get" + layerName + "Json"
    return scriptTag
