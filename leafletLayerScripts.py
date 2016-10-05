import re
import os
import shutil
import tempfile
from PyQt4.QtCore import QSize, QVariant
import time
from qgis.core import *
from qgis.utils import QGis
import processing
from leafletScriptStrings import *
from utils import (writeTmpLayer, getUsedFields, removeSpaces,
                   is25d, exportImages)


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
                     popupsOnHover, popup, count, outputProjectFileName,
                     wfsLayers, cluster, cluster_num, visible, json, legends,
                     new_src, canvas, zIndex):
    (new_pop, labeltext,
     popFuncs) = labelsAndPopups(layer, safeLayerName, highlight,
                                 popupsOnHover, popup, count)
    renderer = layer.rendererV2()
    layer_transp = 1 - (float(layer.layerTransparency()) / 100)
    new_obj = ""

    if is25d(layer, canvas):
        shadows = ""
        renderer = layer.rendererV2()
        renderContext = QgsRenderContext.fromMapSettings(
                canvas.mapSettings())
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
    elif (isinstance(renderer, QgsSingleSymbolRendererV2) or
            isinstance(renderer, QgsRuleBasedRendererV2)):
        # print safeLayerName + ": single"
        (new_obj, legends,
         wfsLayers) = singleLayer(renderer, outputProjectFileName,
                                  safeLayerName, wfsLayers, layer,
                                  layer_transp, labeltext, cluster,
                                  cluster_num, visible, json, usedFields,
                                  legends, count, popFuncs, zIndex)
    elif isinstance(renderer, QgsCategorizedSymbolRendererV2):
        # print safeLayerName + ": categorized"
        (new_obj, legends,
         wfsLayers) = categorizedLayer(layer, renderer, safeLayerName,
                                       outputProjectFileName, layer_transp,
                                       usedFields, count, legends, labeltext,
                                       cluster, cluster_num, popFuncs, visible,
                                       json, wfsLayers, zIndex)
    elif isinstance(renderer, QgsGraduatedSymbolRendererV2):
        # print safeLayerName + ": graduated"
        (new_obj, legends,
         wfsLayers) = graduatedLayer(layer, safeLayerName, renderer,
                                     outputProjectFileName, layer_transp,
                                     labeltext, popFuncs, cluster, cluster_num,
                                     visible, json, usedFields, count, legends,
                                     wfsLayers, zIndex)
    elif isinstance(renderer, Qgs25DRenderer):
        # print safeLayerName + ": 2.5d"
        pass
    elif isinstance(renderer, QgsHeatmapRenderer):
        (new_obj, legends,
         wfsLayers) = heatmapLayer(layer, safeLayerName, renderer,
                                   outputProjectFileName, layer_transp,
                                   labeltext, popFuncs, cluster, cluster_num,
                                   visible, json, usedFields, count, legends,
                                   wfsLayers)
    if usedFields[count] != 0:
        new_src += new_pop.decode("utf-8")
    new_src += """
""" + new_obj
    if is25d(layer, canvas):
        pass
    else:
        new_src += """
        bounds_group.addLayer(json_""" + safeLayerName + """JSON);"""
        if visible[count]:
            if cluster[count] is False:
                new_src += """
        feature_group.addLayer(json_""" + safeLayerName + """JSON);"""
            else:
                new_src += """
        cluster_group""" + safeLayerName + """JSON.addTo(map);"""
    return new_src, legends, wfsLayers


def labelsAndPopups(layer, safeLayerName, highlight, popupsOnHover,
                    popup, count):
    fields = layer.pendingFields()
    field_names = popup[count].keys()
    field_vals = popup[count].values()
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
    f = palyr.fieldName
    fieldIndex = layer.pendingFields().indexFromName(f)
    try:
        editorWidget = layer.editFormConfig().widgetType(fieldIndex)
    except:
        editorWidget = layer.editorWidgetV2(fieldIndex)
    if (editorWidget == QgsVectorLayer.Hidden or
            editorWidget == 'Hidden'):
        f = "q2wHide_" + f
    label_exp = False
    labeltext = ".bindTooltip((feature.properties['" + unicode(f)
    labeltext += "'] !== null?String(%sfeature.properties['%s'])%s:'')" % (
            styleStart, unicode(f), styleEnd)
    labeltext += ", {permanent: true, offset: [-0, -16], "
    labeltext += "className: 'css_%s'}" % safeLayerName
    labeltext += ").openTooltip();"
    f = palyr.fieldName
    table = ""
    for field in popup[count]:
        if unicode(field) == 'html_exp':
            html_prov = True
            table = 'feature.properties.html_exp'
        if (unicode(f) != "" and
                f and palyr.enabled):
            label_exp = True
        if not html_prov:
            tablestart = "'<table>"
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

                row += '<tr>'
                if val == 'inline label':
                    row += '<th scope="row">'
                    row += layer.attributeDisplayName(fieldIndex)
                    row += '</th><td>'
                else:
                    row += '<td colspan="2">'
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

                row += "</td></tr>"
            tableend = "</table>'"
            table = tablestart + row + tableend
    if not label_exp:
        labeltext = ""
    if popup[count] != 0 and table != "":
        popFuncs = popFuncsScript(table)
    else:
        popFuncs = ""
    new_pop = popupScript(safeLayerName, popFuncs, highlight, popupsOnHover)
    return new_pop, labeltext, popFuncs


def singleLayer(renderer, outputProjectFileName, safeLayerName, wfsLayers,
                layer, layer_transp, labeltext, cluster, cluster_num, visible,
                json, usedFields, legends, count, popFuncs, zIndex):
    if isinstance(renderer, QgsRuleBasedRendererV2):
        symbol = renderer.rootRule().children()[0].symbol()
    else:
        symbol = renderer.symbol()
    symbolLayer = symbol.symbolLayer(0)
    legendIcon = QgsSymbolLayerV2Utils.symbolPreviewPixmap(symbol,
                                                           QSize(16, 16))
    legendIcon.save(os.path.join(outputProjectFileName, "legend",
                                 safeLayerName + ".png"))
    legends[safeLayerName] = '<img src="legend/' + safeLayerName + '.png" /> '
    legends[safeLayerName] += layer.name()
    colorName = symbol.color().name()
    symbol_transp = symbol.alpha()
    fill_transp = float(symbol.color().alpha()) / 255
    fill_opacity = unicode(layer_transp * symbol_transp * fill_transp)
    if layer.geometryType() == QGis.Point:
        (new_obj, cluster_num,
         wfsLayers) = singlePoint(symbol, symbolLayer, layer_transp,
                                  symbol_transp, safeLayerName, colorName,
                                  fill_opacity, labeltext, layer, cluster,
                                  cluster_num, visible, json, usedFields,
                                  wfsLayers, count, outputProjectFileName,
                                  zIndex)
    elif layer.geometryType() == QGis.Line:
        new_obj, wfsLayers = singleLine(symbol, colorName, fill_opacity, layer,
                                        json, safeLayerName, wfsLayers,
                                        visible, usedFields, count, zIndex)
    elif layer.geometryType() == QGis.Polygon:
        new_obj, wfsLayers = singlePolygon(layer, safeLayerName, symbol,
                                           symbolLayer, colorName,
                                           layer_transp, symbol_transp,
                                           fill_opacity, visible, json,
                                           usedFields, wfsLayers, count,
                                           zIndex)
    return new_obj, legends, wfsLayers


def singlePoint(symbol, symbolLayer, layer_transp, symbol_transp,
                safeLayerName, colorName, fill_opacity, labeltext, layer,
                cluster, cluster_num, visible, json, usedFields, wfsLayers,
                count, outputProjectFileName, zIndex):
    radius = unicode(symbol.size())
    if isinstance(symbolLayer, QgsSvgMarkerSymbolLayerV2):
        if symbol.dataDefinedAngle().isActive():
            if symbol.dataDefinedAngle().useExpression():
                rot = "0"
            else:
                rot = "feature.properties["
                rot += symbol.dataDefinedAngle().expressionOrField()
                rot += "]"
        else:
            rot = symbolLayer.angle()
        pointStyleLabel = svgScript(safeLayerName, symbolLayer,
                                    outputProjectFileName, rot, labeltext,
                                    zIndex)
    else:
        try:
            borderStyle = symbolLayer.outlineStyle()
            border = symbolLayer.borderColor()
            borderColor = unicode(border.name())
            border_transp = float(border.alpha()) / 255
            borderWidth = symbolLayer.outlineWidth()
        except:
            borderStyle = ""
            borderColor = ""
            border_transp = 0
            borderWidth = 1
        borderOpacity = unicode(layer_transp * symbol_transp * border_transp)
        pointStyleLabel = pointStyleLabelScript(safeLayerName, radius,
                                                borderWidth, borderStyle,
                                                colorName, borderColor,
                                                borderOpacity, fill_opacity,
                                                labeltext, zIndex)
    pointToLayer = pointToLayerScript(safeLayerName)
    if layer.providerType() == 'WFS' and json[count] is False:
        (new_obj, scriptTag,
         cluster_num) = buildPointWFS(pointStyleLabel, safeLayerName,
                                      layer, "", cluster[count],
                                      cluster_num, visible[count])
        wfsLayers += wfsScript(scriptTag)
    else:
        rot = symbol.dataDefinedAngle().expressionOrField()
        new_obj = jsonPointScript(pointStyleLabel, safeLayerName, pointToLayer,
                                  usedFields[count])
        if cluster[count]:
            new_obj += clusterScript(safeLayerName)
            cluster_num += 1
    return new_obj, cluster_num, wfsLayers


def singleLine(symbol, colorName, fill_opacity, layer, json, safeLayerName,
               wfsLayers, visible, usedFields, count, zIndex):
    radius = symbol.width()
    sl = symbol.symbolLayer(0)
    try:
        (penStyle, capString,
         joinString) = getLineStyle(sl.penStyle(), radius, sl.penCapStyle(),
                                    sl.penJoinStyle())
    except:
        penStyle = ""
    lineStyle = simpleLineStyleScript(radius, colorName, penStyle, capString,
                                      joinString, fill_opacity)
    if layer.providerType() == 'WFS' and json[count] is False:
        stylestr = nonPointStylePopupsScript(safeLayerName)
        new_obj, scriptTag = buildNonPointWFS(safeLayerName, layer, "",
                                              stylestr, visible[count], zIndex)
        new_obj += nonPointStyleFunctionScript(safeLayerName, lineStyle)
        wfsLayers += wfsScript(scriptTag)
    else:
        new_obj = nonPointStyleFunctionScript(safeLayerName, lineStyle)
        new_obj += buildNonPointJSON("", safeLayerName, usedFields[count],
                                     zIndex)
    return new_obj, wfsLayers


def singlePolygon(layer, safeLayerName, symbol, symbolLayer, colorName,
                  layer_transp, symbol_transp, fill_opacity, visible, json,
                  usedFields, wfsLayers, count, zIndex):
    borderStyle = ""
    try:
        capStyle = symbolLayer.penCapStyle()
        joinStyle = symbolLayer.penJoinStyle()
    except:
        capStyle = 16
        joinStyle = 64
    if (symbolLayer.layerType() == 'SimpleLine' or
            isinstance(symbolLayer, QgsSimpleLineSymbolLayerV2)):
        radius = symbolLayer.width()
        colorName = 'none'
        borderColor = unicode(symbol.color().name())
        border_transp = float(symbol.color().alpha()) / 255
        lineStyle = symbolLayer.penStyle()
    else:
        try:
            radius = symbolLayer.borderWidth()
            border = symbolLayer.borderColor()
            borderColor = unicode(border.name())
            border_transp = float(border.alpha()) / 255
            lineStyle = symbolLayer.borderStyle()
        except:
            radius = 1
            borderColor = "#000000"
            borderStyle = ""
            capString = ""
            joinString = ""
            border_transp = 1
            colorName = "#ffffff"
            lineStyle = ""
    (borderStyle, capString,
     joinString) = getLineStyle(lineStyle, radius,
                                capStyle, joinStyle)
    if lineStyle == 0:
        radius = "0"
    if lineStyle == 0:
        colorName = "none"
    borderOpacity = unicode(layer_transp * symbol_transp * border_transp)
    polyStyle = singlePolyStyleScript(radius, borderColor, borderOpacity,
                                      colorName, borderStyle, capString,
                                      joinString, fill_opacity)
    if layer.providerType() == 'WFS' and json[count] is False:
        stylestr = nonPointStylePopupsScript(safeLayerName)
        new_obj, scriptTag = buildNonPointWFS(safeLayerName, layer, "",
                                              stylestr, visible[count], zIndex)
        new_obj += nonPointStyleFunctionScript(safeLayerName, polyStyle)
        wfsLayers += wfsScript(scriptTag)
    else:
        new_obj = nonPointStyleFunctionScript(safeLayerName, polyStyle)
        new_obj += buildNonPointJSON("", safeLayerName, usedFields[count],
                                     zIndex)
    return new_obj, wfsLayers


def categorizedLayer(layer, renderer, safeLayerName, outputProjectFileName,
                     layer_transp, usedFields, count, legends, labeltext,
                     cluster, cluster_num, popFuncs, visible, json, wfsLayers,
                     zIndex):
    catLegend = layer.name() + "<br />"
    if layer.geometryType() == QGis.Point:
        (new_obj, wfsLayers,
         catLegend) = categorizedPoint(outputProjectFileName, layer, renderer,
                                       safeLayerName, layer_transp, labeltext,
                                       cluster, cluster_num, usedFields,
                                       visible, json, count, wfsLayers,
                                       catLegend, zIndex)
    elif layer.geometryType() == QGis.Line:
        (new_obj, wfsLayers,
         catLegend) = categorizedLine(outputProjectFileName, layer,
                                      safeLayerName, renderer, catLegend,
                                      layer_transp, popFuncs, usedFields, json,
                                      visible, count, wfsLayers, zIndex)
    elif layer.geometryType() == QGis.Polygon:
        (new_obj, catLegend,
         wfsLayers) = categorizedPolygon(outputProjectFileName, layer,
                                         renderer, safeLayerName, catLegend,
                                         layer_transp, usedFields, visible,
                                         json, count, popFuncs, wfsLayers,
                                         zIndex)
    legends[safeLayerName] = catLegend
    return new_obj, legends, wfsLayers


def categorizedPoint(outputProjectFileName, layer, renderer, safeLayerName,
                     layer_transp, labeltext, cluster, cluster_num, usedFields,
                     visible, json, count, wfsLayers, catLegend, zIndex):
    categories = renderer.categories()
    valueAttr = renderer.classAttribute()
    fieldIndex = layer.pendingFields().indexFromName(valueAttr)
    try:
        editorWidget = layer.editFormConfig().widgetType(fieldIndex)
    except:
        editorWidget = layer.editorWidgetV2(fieldIndex)
    if (editorWidget == QgsVectorLayer.Hidden or
            editorWidget == 'Hidden'):
        valueAttr = "q2wHide_" + valueAttr
    categoryStr = categoryScript(safeLayerName, valueAttr)
    for cat in categories:
        if not cat.value():
            categoryStr += defaultCategoryScript()
        else:
            categoryStr += eachCategoryScript(cat.value())
        symbol = cat.symbol()
        catLegend = iconLegend(symbol, cat, outputProjectFileName,
                               safeLayerName, catLegend)
        symbol_transp = symbol.alpha()
        fill_transp = float(symbol.color().alpha()) / 255
        fill_opacity = unicode(layer_transp * symbol_transp * fill_transp)
        symbolLayer = symbol.symbolLayer(0)
        try:
            border_transp = float(symbolLayer.borderColor().alpha()) / 255
        except:
            border_transp = 0
        borderOpacity = unicode(layer_transp * symbol_transp * border_transp)
        categoryStr += categorizedPointStylesScript(symbol, fill_opacity,
                                                    borderOpacity)
    categoryStr += endCategoryScript()
    if layer.providerType() == 'WFS' and json[count] is False:
        stylestr = categorizedPointWFSscript(safeLayerName, labeltext)
        (new_obj, scriptTag,
         cluster_num) = buildPointWFS(stylestr, safeLayerName, layer,
                                      categoryStr, cluster[count], cluster_num,
                                      visible[count])
        wfsLayers += wfsScript(scriptTag)
    else:
        new_obj = categoryStr + categorizedPointJSONscript(safeLayerName,
                                                           labeltext,
                                                           usedFields[count],
                                                           zIndex)
        if cluster[count]:
            new_obj += clusterScript(safeLayerName)
            cluster_num += 1
    return new_obj, wfsLayers, catLegend


def categorizedLine(outputProjectFileName, layer, safeLayerName, renderer,
                    catLegend, layer_transp, popFuncs, usedFields, json,
                    visible, count, wfsLayers, zIndex):
    categories = renderer.categories()
    valueAttr = renderer.classAttribute()
    fieldIndex = layer.pendingFields().indexFromName(valueAttr)
    try:
        editorWidget = layer.editFormConfig().widgetType(fieldIndex)
    except:
        editorWidget = layer.editorWidgetV2(fieldIndex)
    if (editorWidget == QgsVectorLayer.Hidden or
            editorWidget == 'Hidden'):
        valueAttr = "q2wHide_" + valueAttr
    categoryStr = categoryScript(safeLayerName, valueAttr)
    for cat in categories:
        if not cat.value():
            categoryStr += defaultCategoryScript()
        else:
            categoryStr += eachCategoryScript(cat.value())
        symbol = cat.symbol()
        catLegend = iconLegend(symbol, cat, outputProjectFileName,
                               safeLayerName, catLegend)
        symbol_transp = symbol.alpha()
        fill_transp = float(symbol.color().alpha()) / 255
        fill_opacity = unicode(layer_transp * symbol_transp * fill_transp)
        categoryStr += categorizedLineStylesScript(symbol, fill_opacity)
    categoryStr += endCategoryScript()
    stylestr = categorizedNonPointStyleFunctionScript(safeLayerName, popFuncs)
    if layer.providerType() == 'WFS' and json[count] is False:
        new_obj, scriptTag = buildNonPointWFS(safeLayerName, layer,
                                              categoryStr, stylestr,
                                              visible[count], zIndex)
        wfsLayers += wfsScript(scriptTag)
    else:
        new_obj = buildNonPointJSON(categoryStr, safeLayerName,
                                    usedFields[count], zIndex)
    return new_obj, wfsLayers, catLegend


def categorizedPolygon(outputProjectFileName, layer, renderer, safeLayerName,
                       catLegend, layer_transp, usedFields, visible, json,
                       count, popFuncs, wfsLayers, zIndex):
    categories = renderer.categories()
    valueAttr = renderer.classAttribute()
    fieldIndex = layer.pendingFields().indexFromName(valueAttr)
    try:
        editorWidget = layer.editFormConfig().widgetType(fieldIndex)
    except:
        editorWidget = layer.editorWidgetV2(fieldIndex)
    if (editorWidget == QgsVectorLayer.Hidden or
            editorWidget == 'Hidden'):
        valueAttr = "q2wHide_" + valueAttr
    categoryStr = categoryScript(safeLayerName, valueAttr)
    for cat in categories:
        if not cat.value():
            categoryStr += defaultCategoryScript()
        else:
            categoryStr += eachCategoryScript(cat.value())
        symbol = cat.symbol()
        catLegend = iconLegend(symbol, cat, outputProjectFileName,
                               safeLayerName, catLegend)
        symbol_transp = symbol.alpha()
        symbolLayer = symbol.symbolLayer(0)
        border_transp = float(symbolLayer.borderColor().alpha()) / 255
        borderOpacity = unicode(layer_transp * symbol_transp * border_transp)
        fill_transp = float(symbol.color().alpha()) / 255
        fill_opacity = unicode(layer_transp * symbol_transp * fill_transp)
        categoryStr += categorizedPolygonStylesScript(symbol, fill_opacity,
                                                      borderOpacity)
    categoryStr += endCategoryScript()
    if layer.providerType() == 'WFS' and json[count] is False:
        stylestr = categorizedNonPointStyleFunctionScript(safeLayerName,
                                                          popFuncs)
        new_obj, scriptTag = buildNonPointWFS(safeLayerName, layer,
                                              categoryStr, stylestr,
                                              visible[count], zIndex)
        wfsLayers += wfsScript(scriptTag)
    else:
        new_obj = buildNonPointJSON(categoryStr, safeLayerName,
                                    usedFields[count], zIndex)
    return new_obj, catLegend, wfsLayers


def graduatedLayer(layer, safeLayerName, renderer, outputProjectFileName,
                   layer_transp, labeltext, popFuncs, cluster, cluster_num,
                   visible, json, usedFields, count, legends, wfsLayers,
                   zIndex):
    catLegend = layer.name() + "<br />"
    categoryStr = graduatedStyleScript(safeLayerName)
    if layer.geometryType() == QGis.Point:
        (new_obj, catLegend, wfsLayers,
         cluster_num) = graduatedPoint(outputProjectFileName, layer,
                                       safeLayerName, renderer, catLegend,
                                       layer_transp, json, count, labeltext,
                                       usedFields, cluster, cluster_num,
                                       visible, wfsLayers, categoryStr, zIndex)
    elif layer.geometryType() == QGis.Line:
        (new_obj, wfsLayers,
         catLegend) = graduatedLine(outputProjectFileName, layer,
                                    safeLayerName, renderer, catLegend,
                                    layer_transp, popFuncs, usedFields, json,
                                    visible, count, wfsLayers, categoryStr,
                                    zIndex)
    elif layer.geometryType() == QGis.Polygon:
        (new_obj, catLegend,
         wfsLayers) = graduatedPolygon(outputProjectFileName, layer, renderer,
                                       safeLayerName, catLegend, layer_transp,
                                       usedFields, visible, json, count,
                                       popFuncs, wfsLayers, categoryStr,
                                       zIndex)
    legends[safeLayerName] = catLegend
    return new_obj, legends, wfsLayers


def graduatedPoint(outputProjectFileName, layer, safeLayerName, renderer,
                   catLegend, layer_transp, json, count, labeltext, usedFields,
                   cluster, cluster_num, visible, wfsLayers, categoryStr,
                   zIndex):
    valueAttr = renderer.classAttribute()
    fieldIndex = layer.pendingFields().indexFromName(valueAttr)
    try:
        editorWidget = layer.editFormConfig().widgetType(fieldIndex)
    except:
        editorWidget = layer.editorWidgetV2(fieldIndex)
    if (editorWidget == QgsVectorLayer.Hidden or
            editorWidget == 'Hidden'):
        valueAttr = "q2wHide_" + valueAttr
    for r in renderer.ranges():
        symbol = r.symbol()
        catLegend = iconLegend(symbol, r, outputProjectFileName, safeLayerName,
                               catLegend)
        symbol_transp = symbol.alpha()
        symbolLayer = symbol.symbolLayer(0)
        border_transp = float(symbolLayer.borderColor().alpha()) / 255
        borderOpacity = unicode(layer_transp * symbol_transp * border_transp)
        fill_transp = float(symbol.color().alpha()) / 255
        fill_opacity = unicode(layer_transp * symbol_transp * fill_transp)
        categoryStr += graduatedPointStylesScript(valueAttr, r, symbol,
                                                  fill_opacity, borderOpacity)
    categoryStr += endGraduatedStyleScript()
    if layer.providerType() == 'WFS' and json[count] is False:
        stylestr = categorizedPointWFSscript(safeLayerName, labeltext)
        (new_obj, scriptTag,
         cluster_num) = buildPointWFS(stylestr, safeLayerName, layer,
                                      categoryStr, cluster[count], cluster_num,
                                      visible[count])
        wfsLayers += wfsScript(scriptTag)
    else:
        new_obj = categoryStr + categorizedPointJSONscript(safeLayerName,
                                                           labeltext,
                                                           usedFields[count],
                                                           zIndex)
        if cluster[count]:
            new_obj += clusterScript(safeLayerName)
            cluster_num += 1
    return new_obj, catLegend, wfsLayers, cluster_num


def graduatedLine(outputProjectFileName, layer, safeLayerName, renderer,
                  catLegend, layer_transp, popFuncs, usedFields, json, visible,
                  count, wfsLayers, categoryStr, zIndex):
    valueAttr = renderer.classAttribute()
    fieldIndex = layer.pendingFields().indexFromName(valueAttr)
    try:
        editorWidget = layer.editFormConfig().widgetType(fieldIndex)
    except:
        editorWidget = layer.editorWidgetV2(fieldIndex)
    if (editorWidget == QgsVectorLayer.Hidden or
            editorWidget == 'Hidden'):
        valueAttr = "q2wHide_" + valueAttr
    for r in renderer.ranges():
        symbol = r.symbol()
        catLegend = iconLegend(symbol, r, outputProjectFileName, safeLayerName,
                               catLegend)
        symbol_transp = symbol.alpha()
        fill_transp = float(symbol.color().alpha()) / 255
        fill_opacity = unicode(layer_transp * symbol_transp * fill_transp)
        categoryStr += graduatedLineStylesScript(valueAttr, r, symbol,
                                                 fill_opacity)
    categoryStr += endGraduatedStyleScript()
    if layer.providerType() == 'WFS' and json[count] is False:
        stylestr = categorizedNonPointStyleFunctionScript(safeLayerName,
                                                          popFuncs)
        new_obj, scriptTag = buildNonPointWFS(safeLayerName, layer,
                                              categoryStr, stylestr,
                                              visible[count], zIndex)
        wfsLayers += wfsScript(scriptTag)
    else:
        new_obj = buildNonPointJSON(categoryStr, safeLayerName,
                                    usedFields[count], zIndex)
    return new_obj, wfsLayers, catLegend


def graduatedPolygon(outputProjectFileName, layer, renderer, safeLayerName,
                     catLegend, layer_transp, usedFields, visible, json, count,
                     popFuncs, wfsLayers, categoryStr, zIndex):
    valueAttr = renderer.classAttribute()
    fieldIndex = layer.pendingFields().indexFromName(valueAttr)
    try:
        editorWidget = layer.editFormConfig().widgetType(fieldIndex)
    except:
        editorWidget = layer.editorWidgetV2(fieldIndex)
    if (editorWidget == QgsVectorLayer.Hidden or
            editorWidget == 'Hidden'):
        valueAttr = "q2wHide_" + valueAttr
    for r in renderer.ranges():
        symbol = r.symbol()
        catLegend = iconLegend(symbol, r, outputProjectFileName, safeLayerName,
                               catLegend)
        symbol_transp = symbol.alpha()
        symbolLayer = symbol.symbolLayer(0)
        border_transp = float(symbolLayer.borderColor().alpha()) / 255
        borderOpacity = unicode(layer_transp * symbol_transp * border_transp)
        fill_transp = float(symbol.color().alpha()) / 255
        fill_opacity = unicode(layer_transp * symbol_transp * fill_transp)
        categoryStr += graduatedPolygonStylesScript(valueAttr, r, symbol,
                                                    fill_opacity,
                                                    borderOpacity)
    categoryStr += endGraduatedStyleScript()
    if layer.providerType() == 'WFS' and json[count] is False:
        stylestr = categorizedNonPointStyleFunctionScript(safeLayerName,
                                                          popFuncs)
        new_obj, scriptTag = buildNonPointWFS(safeLayerName, layer,
                                              categoryStr, stylestr,
                                              visible[count], zIndex)
        wfsLayers += wfsScript(scriptTag)
    else:
        new_obj = buildNonPointJSON(categoryStr, safeLayerName,
                                    usedFields[count], zIndex)
    return new_obj, catLegend, wfsLayers


def heatmapLayer(layer, safeLayerName, renderer, outputProjectFileName,
                 layer_transp, labeltext, popFuncs, cluster, cluster_num,
                 visible, json, usedFields, count, legends, wfsLayers):
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
        var json_%(sln)sJSON = new L.heatLayer(%(sln)s_hm, {
            radius: %(hmRadius)d,
            max: %(hmWeightMax)d,
            minOpacity: 1,
            gradient: %(hmRamp)s});
        """ % {"sln": safeLayerName, "hmWeight": hmWeight,
               "hmWeightMax": hmWeightMax, "hmRamp": hmRamp,
               "hmRadius": hmRadius}
    return new_obj, legends, wfsLayers


def buildPointWFS(pointStyleLabel, layerName, layer, categoryStr,
                  cluster_set, cluster_num, visible):
    scriptTag = getWFSScriptTag(layer, layerName)
    new_obj = pointStyleLabel + categoryStr + """
        var json_{layerName}JSON;
        json_{layerName}JSON = L.geoJson(null, {{
            pane: 'pane_{layerName}',
            pointToLayer: doPointToLayer{layerName},
            onEachFeature: pop_{layerName}
        }});""".format(layerName=layerName)
    if cluster_set:
        new_obj += """
        var cluster_group{layerName}JSON = """.format(layerName=layerName)
        new_obj += "new L.MarkerClusterGroup({showCoverageOnHover: false});"
    else:
        if visible:
            new_obj += """
        feature_group.addLayer(json_{layerName}JSON);""".format(
                    layerName=layerName)
    new_obj += """
        function get{layerName}Json(geojson) {{
            json_{layerName}""".format(layerName=layerName)
    new_obj += "JSON.addData(geojson);"
    if cluster_set:
        new_obj += """
                cluster_group{layerName}JSON.add""".format(layerName=layerName)
        new_obj += "Layer(json_{layerName}JSON);".format(layerName=layerName)
        cluster_num += 1
    new_obj += """
        };"""
    return new_obj, scriptTag, cluster_num


def buildNonPointJSON(categoryStr, safeName, usedFields, zIndex):
    zIndex = zIndex + 600
    if usedFields != 0:
        new_obj = categoryStr + """
        map.createPane('pane_{safeName}');
        map.getPane('pane_{safeName}').style.zIndex = {zIndex};
        var json_{safeName}JSON = new L.geoJson(json_{safeName}, {{
            pane: 'pane_{safeName}',
            onEachFeature: pop_{safeName},
            style: doStyle{safeName}
        }});""".format(safeName=safeName, zIndex=zIndex)
    else:
        new_obj = categoryStr + """
        map.createPane('pane_{safeName}');
        map.getPane('pane_{safeName}').style.zIndex = {zIndex}
        var json_{safeName}JSON = new L.geoJson(json_{safeName}, {{
            pane: 'pane_{safeName}',
            style: doStyle{safeName}
        }});""".format(safeName=safeName, zIndex=zIndex)
    return new_obj


def buildNonPointWFS(layerName, layer, categoryStr, stylestr, visible, zIndex):
    zIndex = zIndex + 600
    scriptTag = getWFSScriptTag(layer, layerName)
    new_obj = categoryStr + """
        map.createPane('pane_{layerName}');
        map.getPane('pane_{layerName}').style.zIndex = {zIndex};
        var json_{layerName}JSON;
        json_{layerName}JSON = L.geoJson(null, {{{stylestr},
            pane: 'pane_{layerName}',
            onEachFeature: pop_{layerName}
        }});""".format(layerName=layerName, stylestr=stylestr, zIndex=zIndex)
    if visible:
        new_obj += """
        feature_group.addLayer(json_{layerName}JSON);""".format(
            layerName=layerName)
    new_obj += """
        function get{layerName}Json(geojson) {{
            json_{layerName}""".format(layerName=layerName)
    new_obj += "JSON.addData(geojson);"
    new_obj += """
        };"""
    return new_obj, scriptTag


def getWFSScriptTag(layer, layerName):
    layerSource = layer.source()
    if "retrictToRequestBBOX" in layerSource:
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
