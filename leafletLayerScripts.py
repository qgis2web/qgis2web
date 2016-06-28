import re
import os
import tempfile
from PyQt4.QtCore import QSize, QVariant
import time
from qgis.core import *
from qgis.utils import QGis
import processing
from leafletScriptStrings import *
from utils import (writeTmpLayer, getUsedFields, removeSpaces,
                   is25d, exportImages)


def exportJSONLayer(i, eachPopup, precision, tmpFileName, exp_crs,
                    layerFileName, safeLayerName, minify, canvas):
    cleanedLayer = writeTmpLayer(i, eachPopup)
    if is25d(i, canvas):
        provider = cleanedLayer.dataProvider()
        provider.addAttributes([QgsField("height", QVariant.Double),
                                QgsField("wallColor", QVariant.String),
                                QgsField("roofColor", QVariant.String)])
        cleanedLayer.updateFields()
        fields = cleanedLayer.pendingFields()
        renderer = i.rendererV2()
        renderContext = QgsRenderContext.fromMapSettings(
                canvas.mapSettings())
        feats = i.getFeatures()
        context = QgsExpressionContext()
        context.appendScope(QgsExpressionContextUtils.layerScope(i))
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

    if eachPopup == 0:
        pass
    elif eachPopup == 1:
        fields = i.pendingFields()
        for field in fields:
            exportImages(i, field.name(), layerFileName)
    else:
        exportImages(i, eachPopup, layerFileName)


def exportRasterLayer(i, safeLayerName, dataPath):
    layer = i
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
"""        try:
            print "1"
            warpArgs = {
                "INPUT": piped_file,
                "SOURCE_SRS": layer.crs().authid(),
                "DEST_SRS": "EPSG:3857",
                "NO_DATA": "",
                "TR": 0,
                "METHOD": 0,
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
            print 11
            # force exception on algorithm fail
            for val in procRtn:
                pass
        except:
            try:"""
                # print "2"
        warpArgs = {
            "INPUT": piped_file,
            "SOURCE_SRS": layer.crs().authid(),
            "DEST_SRS": "EPSG:3857",
            "NO_DATA": "",
            "TR": 0,
            "METHOD": 0,
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
                # print 22
                # force exception on algorithm fail
                # for val in procRtn:
                #     pass
"""            except:
                print "3"
                warpArgs = {
                    "INPUT": piped_file,
                    "SOURCE_SRS": layer.crs().authid(),
                    "DEST_SRS": "EPSG:3857",
                    "NO_DATA": "",
                    "TR": 0,
                    "METHOD": 0,
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
                print 33"""

        processing.runalg("gdalogr:translate", piped_3857, 100,
                          True, "", 0, "", extentRepNew, False, 5,
                          4, 75, 6, 1, False, 0, False, "",
                          out_raster)


def writeVectorLayer(i, safeLayerName, usedFields, highlight, popupsOnHover,
                     popup, count, outputProjectFileName, wfsLayers, cluster,
                     cluster_num, visible, json, legends, new_src, canvas):
    (new_pop, labeltext,
     popFuncs) = labelsAndPopups(i, safeLayerName, usedFields, highlight,
                                 popupsOnHover, popup, count)
    renderer = i.rendererV2()
    layer_transp = 1 - (float(i.layerTransparency()) / 100)
    new_obj = ""

    if is25d(i, canvas):
        shadows = ""
        renderer = i.rendererV2()
        renderContext = QgsRenderContext.fromMapSettings(
                canvas.mapSettings())
        fields = i.pendingFields()
        renderer.startRender(renderContext, fields)
        for feat in i.getFeatures():
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
                                  safeLayerName, wfsLayers, i, layer_transp,
                                  labeltext, cluster, cluster_num, visible,
                                  json, usedFields, legends, count, popFuncs)
    elif isinstance(renderer, QgsCategorizedSymbolRendererV2):
        # print safeLayerName + ": categorized"
        (new_obj, legends,
         wfsLayers) = categorizedLayer(i, renderer, safeLayerName,
                                       outputProjectFileName, layer_transp,
                                       usedFields, count, legends, labeltext,
                                       cluster, cluster_num, popFuncs, visible,
                                       json, wfsLayers)
    elif isinstance(renderer, QgsGraduatedSymbolRendererV2):
        # print safeLayerName + ": graduated"
        (new_obj, legends,
         wfsLayers) = graduatedLayer(i, safeLayerName, renderer,
                                     outputProjectFileName, layer_transp,
                                     labeltext, popFuncs, cluster, cluster_num,
                                     visible, json, usedFields, count, legends,
                                     wfsLayers)
    elif isinstance(renderer, Qgs25DRenderer):
        # print safeLayerName + ": 2.5d"
        pass

    if usedFields[count] != 0:
        new_src += new_pop.decode("utf-8")
    new_src += """
""" + new_obj
    if is25d(i, canvas):
        pass
    else:
        new_src += """
        bounds_group.addLayer(json_""" + safeLayerName + """JSON);"""
        if visible[count]:
            if cluster[count] is False:
                new_src += """
        initialOrder[initialOrder.length] = json_""" + safeLayerName + """JSON;
        feature_group.addLayer(json_""" + safeLayerName + """JSON);"""
            else:
                new_src += """
        initialOrder[initialOrder.length] = cluster_group""" + safeLayerName
                new_src += """JSON;
        cluster_group""" + safeLayerName + """JSON.addTo(map);"""
    return new_src, legends, wfsLayers


def labelsAndPopups(i, safeLayerName, usedFields, highlight, popupsOnHover,
                    popup, count):
    fields = i.pendingFields()
    field_names = [field.name() for field in fields]
    usedFields = getUsedFields(i)
    if popup[count] != 0 and popup[count] != 1:
        usedFields.append(popup[count])
        new_field_names = []
        for field in usedFields:
            new_field_names.append(field)
        field_names = new_field_names
    html_prov = False
    label_exp = ''
    labeltext = ""
    f = ''
    palyr = QgsPalLayerSettings()
    palyr.readFromLayer(i)
    f = palyr.fieldName
    label_exp = False
    labeltext = ".bindLabel((feature.properties." + unicode(f)
    labeltext += " !== null?String(feature.properties." + unicode(f) + "):'')"
    labeltext += ", {noHide: true, offset: [-0, -16]}"
    labeltext += ")"
    for field in field_names:
        if unicode(field) == 'html_exp':
            html_prov = True
            table = 'feature.properties.html_exp'
        if (unicode(f) != "" and unicode(f) == unicode(field) and
                f and palyr.enabled):
            label_exp = True
        if not html_prov:
            tablestart = "'<table>"
            row = ""
            for field in field_names:
                fieldIndex = fields.indexFromName(unicode(field))
                try:
                    editorWidget = i.editFormConfig().widgetType(fieldIndex)
                except:
                    editorWidget = i.editorWidgetV2(fieldIndex)
                if (editorWidget == QgsVectorLayer.Hidden or
                        editorWidget == 'Hidden'):
                    continue

                row += '<tr><th scope="row">'
                row += i.attributeDisplayName(fieldIndex)
                row += "</th><td>' + "
                row += "(feature.properties['" + unicode(field) + "'] "
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
    if popup[count] != 0:
        popFuncs = popFuncsScript(table)
    else:
        popFuncs = ""
    new_pop = popupScript(safeLayerName, popFuncs, highlight, popupsOnHover)
    return new_pop, labeltext, popFuncs


def singleLayer(renderer, outputProjectFileName, safeLayerName, wfsLayers, i,
                layer_transp, labeltext, cluster, cluster_num, visible, json,
                usedFields, legends, count, popFuncs):
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
    legends[safeLayerName] += i.name()
    colorName = symbol.color().name()
    symbol_transp = symbol.alpha()
    fill_transp = float(symbol.color().alpha()) / 255
    fill_opacity = unicode(layer_transp * symbol_transp * fill_transp)
    if i.geometryType() == QGis.Point:
        (new_obj, cluster_num,
         wfsLayers) = singlePoint(symbol, symbolLayer, layer_transp,
                                  symbol_transp, safeLayerName, colorName,
                                  fill_opacity, labeltext, i, cluster,
                                  cluster_num, visible, json, usedFields,
                                  wfsLayers, count, outputProjectFileName)
    elif i.geometryType() == QGis.Line:
        new_obj, wfsLayers = singleLine(symbol, colorName, fill_opacity, i,
                                        json, safeLayerName, wfsLayers,
                                        visible, usedFields, count)
    elif i.geometryType() == QGis.Polygon:
        new_obj, wfsLayers = singlePolygon(i, safeLayerName, symbol,
                                           symbolLayer, colorName,
                                           layer_transp, symbol_transp,
                                           fill_opacity, visible, json,
                                           usedFields, wfsLayers, count)
    return new_obj, legends, wfsLayers


def singlePoint(symbol, symbolLayer, layer_transp, symbol_transp,
                safeLayerName, colorName, fill_opacity, labeltext, i, cluster,
                cluster_num, visible, json, usedFields, wfsLayers, count,
                outputProjectFileName):
    radius = unicode(symbol.size())
    if isinstance(symbolLayer, QgsSvgMarkerSymbolLayerV2):
        pointStyleLabel = svgScript(safeLayerName, symbolLayer,
                                    outputProjectFileName, labeltext)
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
                                                labeltext)
    pointToLayer = pointToLayerScript(safeLayerName)
    if i.providerType() == 'WFS' and json[count] is False:
        (new_obj, scriptTag,
         cluster_num) = buildPointWFS(pointStyleLabel, safeLayerName,
                                      i.source(), "", cluster[count],
                                      cluster_num, visible[count])
        wfsLayers += wfsScript(scriptTag)
    else:
        new_obj = jsonPointScript(pointStyleLabel, safeLayerName, pointToLayer,
                                  usedFields[count])
        if cluster[count]:
            new_obj += clusterScript(safeLayerName)
            cluster_num += 1
        else:
            new_obj += """
        layerOrder[layerOrder.length] = json_{layer}JSON;
""".format(layer=safeLayerName)
    return new_obj, cluster_num, wfsLayers


def singleLine(symbol, colorName, fill_opacity, i, json, safeLayerName,
               wfsLayers, visible, usedFields, count):
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
    if i.providerType() == 'WFS' and json[count] is False:
        stylestr = nonPointStylePopupsScript(safeLayerName)
        new_obj, scriptTag = buildNonPointWFS(safeLayerName, i.source(), "",
                                              stylestr, visible[count])
        new_obj += nonPointStyleFunctionScript(safeLayerName, lineStyle)
        wfsLayers += wfsScript(scriptTag)
    else:
        new_obj = nonPointStyleFunctionScript(safeLayerName, lineStyle)
        new_obj += buildNonPointJSON("", safeLayerName, usedFields[count])
    return new_obj, wfsLayers


def singlePolygon(i, safeLayerName, symbol, symbolLayer, colorName,
                  layer_transp, symbol_transp, fill_opacity, visible, json,
                  usedFields, wfsLayers, count):
    borderStyle = ""
    if (symbolLayer.layerType() == 'SimpleLine' or
            isinstance(symbolLayer, QgsSimpleLineSymbolLayerV2)):
        radius = symbolLayer.width()
        colorName = 'none'
        borderColor = unicode(symbol.color().name())
        border_transp = float(symbol.color().alpha()) / 255
    else:
        try:
            capStyle = symbolLayer.penCapStyle()
            joinStyle = symbolLayer.penJoinStyle()
        except:
            capStyle = 16
            joinStyle = 64
        try:
            radius = symbolLayer.borderWidth()
            border = symbolLayer.borderColor()
            borderColor = unicode(border.name())
            (borderStyle, capString,
             joinString) = getLineStyle(symbolLayer.borderStyle(), radius,
                                        capStyle, joinStyle)
            border_transp = float(border.alpha()) / 255
            if symbolLayer.borderStyle() == 0:
                radius = "0"
            if symbolLayer.brushStyle() == 0:
                colorName = "none"
        except:
            radius = 1
            borderColor = "#000000"
            borderStyle = ""
            capString = ""
            joinString = ""
            border_transp = 1
            colorName = "#ffffff"
    borderOpacity = unicode(layer_transp * symbol_transp * border_transp)
    polyStyle = singlePolyStyleScript(radius, borderColor, borderOpacity,
                                      colorName, borderStyle, capString,
                                      joinString, fill_opacity)
    if i.providerType() == 'WFS' and json[count] is False:
        stylestr = nonPointStylePopupsScript(safeLayerName)
        new_obj, scriptTag = buildNonPointWFS(safeLayerName, i.source(), "",
                                              stylestr, visible[count])
        new_obj += nonPointStyleFunctionScript(safeLayerName, polyStyle)
        wfsLayers += wfsScript(scriptTag)
    else:
        new_obj = nonPointStyleFunctionScript(safeLayerName, polyStyle)
        new_obj += buildNonPointJSON("", safeLayerName, usedFields[count])
    return new_obj, wfsLayers


def categorizedLayer(i, renderer, safeLayerName, outputProjectFileName,
                     layer_transp, usedFields, count, legends, labeltext,
                     cluster, cluster_num, popFuncs, visible, json, wfsLayers):
    catLegend = i.name() + "<br />"
    if i.geometryType() == QGis.Point:
        (new_obj, wfsLayers,
         catLegend) = categorizedPoint(outputProjectFileName, i, renderer,
                                       safeLayerName, layer_transp, labeltext,
                                       cluster, cluster_num, usedFields,
                                       visible, json, count, wfsLayers,
                                       catLegend)
    elif i.geometryType() == QGis.Line:
        (new_obj, wfsLayers,
         catLegend) = categorizedLine(outputProjectFileName, i, safeLayerName,
                                      renderer, catLegend, layer_transp,
                                      popFuncs, usedFields, json, visible,
                                      count, wfsLayers)
    elif i.geometryType() == QGis.Polygon:
        (new_obj, catLegend,
         wfsLayers) = categorizedPolygon(outputProjectFileName, i, renderer,
                                         safeLayerName, catLegend,
                                         layer_transp, usedFields, visible,
                                         json, count, popFuncs, wfsLayers)
    legends[safeLayerName] = catLegend
    return new_obj, legends, wfsLayers


def categorizedPoint(outputProjectFileName, i, renderer, safeLayerName,
                     layer_transp, labeltext, cluster, cluster_num, usedFields,
                     visible, json, count, wfsLayers, catLegend):
    categories = renderer.categories()
    valueAttr = renderer.classAttribute()
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
        border_transp = float(symbolLayer.borderColor().alpha()) / 255
        borderOpacity = unicode(layer_transp * symbol_transp * border_transp)
        categoryStr += categorizedPointStylesScript(symbol, fill_opacity,
                                                    borderOpacity)
    categoryStr += endCategoryScript()
    if i.providerType() == 'WFS' and json[count] is False:
        stylestr = categorizedPointWFSscript(safeLayerName, labeltext)
        (new_obj, scriptTag,
         cluster_num) = buildPointWFS(stylestr, safeLayerName, i.source(),
                                      categoryStr, cluster[count], cluster_num,
                                      visible[count])
        wfsLayers += wfsScript(scriptTag)
    else:
        new_obj = categoryStr + categorizedPointJSONscript(safeLayerName,
                                                           labeltext,
                                                           usedFields[count])
        if cluster[count]:
            new_obj += clusterScript(safeLayerName)
            cluster_num += 1
        else:
            new_obj += """
        layerOrder[layerOrder.length] = json_{layer}JSON;
""".format(layer=safeLayerName)
    return new_obj, wfsLayers, catLegend


def categorizedLine(outputProjectFileName, i, safeLayerName, renderer,
                    catLegend, layer_transp, popFuncs, usedFields, json,
                    visible, count, wfsLayers):
    categories = renderer.categories()
    valueAttr = renderer.classAttribute()
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
    if i.providerType() == 'WFS' and json[count] is False:
        new_obj, scriptTag = buildNonPointWFS(safeLayerName, i.source(),
                                              categoryStr, stylestr,
                                              visible[count])
        wfsLayers += wfsScript(scriptTag)
    else:
        new_obj = buildNonPointJSON(categoryStr, safeLayerName,
                                    usedFields[count])
    return new_obj, wfsLayers, catLegend


def categorizedPolygon(outputProjectFileName, i, renderer, safeLayerName,
                       catLegend, layer_transp, usedFields, visible, json,
                       count, popFuncs, wfsLayers):
    categories = renderer.categories()
    valueAttr = renderer.classAttribute()
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
    if i.providerType() == 'WFS' and json[count] is False:
        stylestr = categorizedNonPointStyleFunctionScript(safeLayerName,
                                                          popFuncs)
        new_obj, scriptTag = buildNonPointWFS(safeLayerName, i.source(),
                                              categoryStr, stylestr,
                                              visible[count])
        wfsLayers += wfsScript(scriptTag)
    else:
        new_obj = buildNonPointJSON(categoryStr, safeLayerName,
                                    usedFields[count])
    return new_obj, catLegend, wfsLayers


def graduatedLayer(i, safeLayerName, renderer, outputProjectFileName,
                   layer_transp, labeltext, popFuncs, cluster, cluster_num,
                   visible, json, usedFields, count, legends, wfsLayers):
    catLegend = i.name() + "<br />"
    categoryStr = graduatedStyleScript(safeLayerName)
    if i.geometryType() == QGis.Point:
        (new_obj, catLegend, wfsLayers,
         cluster_num) = graduatedPoint(outputProjectFileName, i, safeLayerName,
                                       renderer, catLegend, layer_transp, json,
                                       count, labeltext, usedFields, cluster,
                                       cluster_num, visible, wfsLayers,
                                       categoryStr)
    elif i.geometryType() == QGis.Line:
        (new_obj, wfsLayers,
         catLegend) = graduatedLine(outputProjectFileName, i, safeLayerName,
                                    renderer, catLegend, layer_transp,
                                    popFuncs, usedFields, json, visible, count,
                                    wfsLayers, categoryStr)
    elif i.geometryType() == QGis.Polygon:
        (new_obj, catLegend,
         wfsLayers) = graduatedPolygon(outputProjectFileName, i, renderer,
                                       safeLayerName, catLegend, layer_transp,
                                       usedFields, visible, json, count,
                                       popFuncs, wfsLayers, categoryStr)
    legends[safeLayerName] = catLegend
    return new_obj, legends, wfsLayers


def graduatedPoint(outputProjectFileName, i, safeLayerName, renderer,
                   catLegend, layer_transp, json, count, labeltext, usedFields,
                   cluster, cluster_num, visible, wfsLayers, categoryStr):
    valueAttr = renderer.classAttribute()
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
    if i.providerType() == 'WFS' and json[count] is False:
        stylestr = categorizedPointWFSscript(safeLayerName, labeltext)
        (new_obj, scriptTag,
         cluster_num) = buildPointWFS(stylestr, safeLayerName, i.source(),
                                      categoryStr, cluster[count], cluster_num,
                                      visible[count])
        wfsLayers += wfsScript(scriptTag)
    else:
        new_obj = categoryStr + categorizedPointJSONscript(safeLayerName,
                                                           labeltext,
                                                           usedFields[count])
        if cluster[count]:
            new_obj += clusterScript(safeLayerName)
            cluster_num += 1
        else:
            new_obj += """
        layerOrder[layerOrder.length] = json_{layer}JSON;
""".format(layer=safeLayerName)
    return new_obj, catLegend, wfsLayers, cluster_num


def graduatedLine(outputProjectFileName, i, safeLayerName, renderer, catLegend,
                  layer_transp, popFuncs, usedFields, json, visible, count,
                  wfsLayers, categoryStr):
    valueAttr = renderer.classAttribute()
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
    if i.providerType() == 'WFS' and json[count] is False:
        stylestr = categorizedNonPointStyleFunctionScript(safeLayerName,
                                                          popFuncs)
        new_obj, scriptTag = buildNonPointWFS(safeLayerName, i.source(),
                                              categoryStr, stylestr,
                                              visible[count])
        wfsLayers += wfsScript(scriptTag)
    else:
        new_obj = buildNonPointJSON(categoryStr, safeLayerName,
                                    usedFields[count])
    return new_obj, wfsLayers, catLegend


def graduatedPolygon(outputProjectFileName, i, renderer, safeLayerName,
                     catLegend, layer_transp, usedFields, visible, json, count,
                     popFuncs, wfsLayers, categoryStr):
    valueAttr = renderer.classAttribute()
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
    if i.providerType() == 'WFS' and json[count] is False:
        stylestr = categorizedNonPointStyleFunctionScript(safeLayerName,
                                                          popFuncs)
        new_obj, scriptTag = buildNonPointWFS(safeLayerName, i.source(),
                                              categoryStr, stylestr,
                                              visible[count])
        wfsLayers += wfsScript(scriptTag)
    else:
        new_obj = buildNonPointJSON(categoryStr, safeLayerName,
                                    usedFields[count])
    return new_obj, catLegend, wfsLayers


def buildPointWFS(pointStyleLabel, layerName, layerSource, categoryStr,
                  cluster_set, cluster_num, visible):
    scriptTag = getWFSScriptTag(layerSource, layerName)
    new_obj = pointStyleLabel + categoryStr + """
        var json_{layerName}JSON;
        json_{layerName}JSON = L.geoJson(null, {{
            pointToLayer: doPointToLayer{layerName},
            onEachFeature: pop_{layerName}
        }});
        layerControl.addOverlay(json_""".format(layerName=layerName)
    new_obj += "{layerName}JSON, '{layerName}');".format(layerName=layerName)
    if cluster_set:
        new_obj += """
        var cluster_group{layerName}JSON = """.format(layerName=layerName)
        new_obj += "new L.MarkerClusterGroup({showCoverageOnHover: false});"
        new_obj += """
        layerOrder[layerOrder.length] = cluster_group"""
        new_obj += "{layerName}JSON;".format(layerName=layerName)
    else:
        new_obj += """
        feature_group.addLayer(json_{layerName}JSON);
        layerOrder[layerOrder.length] = json_{layerName}JSON;""".format(
                layerName=layerName)
    new_obj += """
        function get{layerName}Json(geojson) {{
            json_{layerName}""".format(layerName=layerName)
    new_obj += "JSON.addData(geojson);"
    if visible:
        new_obj += """
            stackLayers();"""
    if cluster_set:
        new_obj += """
                cluster_group{layerName}JSON.add""".format(layerName=layerName)
        new_obj += "Layer(json_{layerName}JSON);".format(layerName=layerName)
        cluster_num += 1
    new_obj += """
        };"""
    return new_obj, scriptTag, cluster_num


def buildNonPointJSON(categoryStr, safeName, usedFields):
    if usedFields != 0:
        new_obj = categoryStr + """
        var json_{safeName}JSON = new L.geoJson(json_{safeName}, {{
            onEachFeature: pop_{safeName},
            style: doStyle{safeName}
        }});
        layerOrder[layerOrder.length]""".format(safeName=safeName)
        new_obj += " = json_{safeName}JSON;".format(safeName=safeName)
    else:
        new_obj = categoryStr + """
        var json_{safeName}JSON = new L.geoJson(json_{safeName}, {{
            style: doStyle{safeName}
        }});
        layerOrder[layerOrder.length] = """.format(safeName=safeName)
        new_obj += "json_{safeName}JSON;".format(safeName=safeName)
    return new_obj


def buildNonPointWFS(layerName, layerSource, categoryStr, stylestr, visible):
    scriptTag = getWFSScriptTag(layerSource, layerName)
    new_obj = categoryStr + """
        var json_{layerName}JSON;
        json_{layerName}JSON = L.geoJson(null, {{{stylestr},
            onEachFeature: pop_{layerName}
        }});""".format(layerName=layerName, stylestr=stylestr)
    new_obj += """
        layerOrder[layerOrder.length] = json_{layerName}JSON;
        feature_group.addLayer(json_{layerName}JSON);
        layerControl.addOverlay(json_""".format(layerName=layerName)
    new_obj += "{layerName}JSON, '{layerName}');".format(layerName=layerName)
    new_obj += """
        function get{layerName}Json(geojson) {{
            json_{layerName}""".format(layerName=layerName)
    new_obj += "JSON.addData(geojson);"
    if visible:
        new_obj += """
            stackLayers();"""
    new_obj += """
        };"""
    return new_obj, scriptTag


def getWFSScriptTag(layerSource, layerName):
    scriptTag = re.sub('SRSNAME\=EPSG\:\d+', 'SRSNAME=EPSG:4326', layerSource)
    scriptTag += "&outputFormat=text%2Fjavascript&format_options=callback%3A"
    scriptTag += "get" + layerName + "Json"
    return scriptTag
