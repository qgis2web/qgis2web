# qgis-ol3 Creates OpenLayers map from QGIS layers
# Copyright (C) 2014 Victor Olaya (volayaf@gmail.com)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import os
import time
import re
import shutil
import sys
from io import StringIO
from PyQt5.QtCore import QDir, QVariant
from PyQt5.QtGui import QPainter
from qgis.core import (QgsApplication,
                       QgsProject,
                       QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsVectorLayer,
                       QgsField,
                       QgsFeature,
                       QgsFeatureRequest,
                       QgsRenderContext,
                       QgsExpression,
                       QgsExpressionContext,
                       QgsExpressionContextUtils,
                       QgsCategorizedSymbolRenderer,
                       QgsGraduatedSymbolRenderer,
                       QgsRuleBasedRenderer,
                       QgsVectorFileWriter,
                       QgsRasterFileWriter,
                       QgsRasterPipe,
                       QgsWkbTypes)
from qgis.core import (Qgs25DRenderer, QgsGeometryGeneratorSymbolLayer)
from qgis.utils import Qgis
import processing
import tempfile

NO_POPUP = 0
ALL_ATTRIBUTES = 1

TYPE_MAP = {
    QgsWkbTypes.Point: 'Point',
    QgsWkbTypes.Point25D: 'Point',
    QgsWkbTypes.PointZ: 'Point',
    QgsWkbTypes.PointM: 'Point',
    QgsWkbTypes.PointZM: 'Point',
    QgsWkbTypes.LineString: 'LineString',
    QgsWkbTypes.LineStringM: 'LineString',
    QgsWkbTypes.LineStringZ: 'LineString',
    QgsWkbTypes.LineStringZM: 'LineString',
    QgsWkbTypes.LineString25D: 'LineString',
    QgsWkbTypes.CircularString: 'LineString',
    QgsWkbTypes.CircularStringZ: 'LineString',
    QgsWkbTypes.CircularStringM: 'LineString',
    QgsWkbTypes.CircularStringZM: 'LineString',
    QgsWkbTypes.CompoundCurveZ: 'LineString',
    QgsWkbTypes.CompoundCurveM: 'LineString',
    QgsWkbTypes.CompoundCurveZM: 'LineString',
    QgsWkbTypes.MultiLineStringZ: 'LineString',
    QgsWkbTypes.MultiLineStringM: 'LineString',
    QgsWkbTypes.MultiCurve: 'LineString',
    QgsWkbTypes.MultiCurveM: 'LineString',
    QgsWkbTypes.MultiCurveZ: 'LineString',
    QgsWkbTypes.MultiCurveZM: 'LineString',
    QgsWkbTypes.Polygon: 'Polygon',
    QgsWkbTypes.PolygonZ: 'Polygon',
    QgsWkbTypes.PolygonM: 'Polygon',
    QgsWkbTypes.PolygonZM: 'Polygon',
    QgsWkbTypes.Polygon25D: 'Polygon',
    QgsWkbTypes.CurvePolygon: 'Polygon',
    QgsWkbTypes.CurvePolygonZ: 'Polygon',
    QgsWkbTypes.CurvePolygonM: 'Polygon',
    QgsWkbTypes.CurvePolygonZM: 'Polygon',
    QgsWkbTypes.MultiPolygonZ: 'Polygon',
    QgsWkbTypes.Triangle: 'Polygon',
    QgsWkbTypes.TriangleZ: 'Polygon',
    QgsWkbTypes.TriangleM: 'Polygon',
    QgsWkbTypes.TriangleZM: 'Polygon',
    QgsWkbTypes.MultiPoint: 'MultiPoint',
    QgsWkbTypes.MultiPoint25D: 'MultiPoint',
    QgsWkbTypes.MultiPointZ: 'MultiPoint',
    QgsWkbTypes.MultiPointM: 'MultiPoint',
    QgsWkbTypes.MultiPointZM: 'MultiPoint',
    QgsWkbTypes.MultiLineString: 'MultiLineString',
    QgsWkbTypes.MultiLineStringM: 'MultiLineString',
    QgsWkbTypes.MultiLineStringZ: 'MultiLineString',
    QgsWkbTypes.MultiLineStringZM: 'MultiLineString',
    QgsWkbTypes.MultiLineString25D: 'MultiLineString',
    QgsWkbTypes.MultiPolygon: 'MultiPolygon',
    QgsWkbTypes.MultiPolygon25D: 'MultiPolygon',
    QgsWkbTypes.MultiPolygonZM: 'MultiPolygon',
    QgsWkbTypes.MultiPolygonM: 'MultiPolygon'}

BLEND_MODES = {
    QPainter.CompositionMode_SourceOver: 'normal',
    QPainter.CompositionMode_Multiply: 'multiply',
    QPainter.CompositionMode_Screen: 'screen',
    QPainter.CompositionMode_Overlay: 'overlay',
    QPainter.CompositionMode_Darken: 'darken',
    QPainter.CompositionMode_Lighten: 'lighten',
    QPainter.CompositionMode_ColorDodge: 'color-dodge',
    QPainter.CompositionMode_ColorBurn: 'color-burn',
    QPainter.CompositionMode_HardLight: 'hard-light',
    QPainter.CompositionMode_SoftLight: 'soft-light',
    QPainter.CompositionMode_Difference: 'difference',
    QPainter.CompositionMode_Exclusion: 'exclusion'}

PLACEMENT = ['bottomleft', 'topleft', 'topright', 'bottomleft', 'bottomright']


def tempFolder():
    tempDir = os.path.join(unicode(QDir.tempPath()), 'qgis2web')
    if not QDir(tempDir).exists():
        QDir().mkpath(tempDir)

    return unicode(os.path.abspath(tempDir))


def getUsedFields(layer):
    fields = []
    try:
        fields.append(layer.renderer().classAttribute())
    except:
        pass
    labelsEnabled = unicode(
        layer.customProperty("labeling/enabled")).lower() == "true"
    if labelsEnabled:
        fields.append(layer.customProperty("labeling/fieldName"))
    return fields


def writeTmpLayer(layer, restrictToExtent, iface, extent):
    fields = layer.fields()
    usedFields = []
    for count, field in enumerate(fields):
        fieldIndex = fields.indexFromName(unicode(field.name()))
        editorWidget = layer.editorWidgetSetup(fieldIndex).type()
        addField = False
        try:
            if layer.renderer().classAttribute() == field.name():
                addField = True
        except:
            pass
        if layer.customProperty("labeling/fieldName") == field.name():
            addField = True
        if (editorWidget != 'Hidden'):
            addField = True
        if addField:
            usedFields.append(count)
    uri = TYPE_MAP[layer.wkbType()]
    crs = layer.crs()
    if crs.isValid():
        uri += '?crs=' + crs.authid()
    for field in usedFields:
        fieldIndex = layer.fields().indexFromName(unicode(
            layer.fields().field(field).name()))
        editorWidget = layer.editorWidgetSetup(fieldIndex).type()
        fieldType = layer.fields().field(field).type()
        fieldName = layer.fields().field(field).name()
        if (editorWidget == 'Hidden'):
            fieldName = "q2wHide_" + fieldName
        fieldType = "double" if (fieldType == QVariant.Double or
                                 fieldType == QVariant.Int) else ("string")
        uri += '&field=' + unicode(fieldName) + ":" + fieldType
    newlayer = QgsVectorLayer(uri, layer.name(), 'memory')
    writer = newlayer.dataProvider()
    outFeat = QgsFeature()
    if restrictToExtent and extent == "Canvas extent":
        canvas = iface.mapCanvas()
        extent = canvas.extent()
        canvasCRS = canvas.mapSettings().destinationCrs()
        layerCRS = layer.crs()
        try:
            transform = QgsCoordinateTransform(canvasCRS, layerCRS,
                                               QgsProject.instance())
        except:
            transform = QgsCoordinateTransform(canvasCRS, layerCRS)
        projectedExtent = transform.transformBoundingBox(extent)
        request = QgsFeatureRequest(projectedExtent)
        request.setFlags(QgsFeatureRequest.ExactIntersect)
        features = layer.getFeatures(request)
    else:
        features = layer.getFeatures()
    for feature in features:
        if feature.geometry() is not None:
            outFeat.setGeometry(feature.geometry())
        attrs = [feature[f] for f in usedFields]
        if attrs:
            outFeat.setAttributes(attrs)
        writer.addFeatures([outFeat])
    return newlayer


def exportLayers(iface, layers, folder, precision, optimize, popupField, json,
                 restrictToExtent, extent, feedback, matchCRS):
    feedback.showFeedback('Exporting layers...')
    layersFolder = os.path.join(folder, "layers")
    QDir().mkpath(layersFolder)
    for count, (layer, encode2json, popup) in enumerate(zip(layers, json,
                                                            popupField)):
        sln = safeName(layer.name()) + "_" + unicode(count)
        vts = layer.customProperty("VectorTilesReader/vector_tile_source")
        if (layer.type() == layer.VectorLayer and vts is None and
                (layer.providerType() != "WFS" or encode2json)):
            feedback.showFeedback('Exporting %s to JSON...' % layer.name())
            crs = QgsCoordinateReferenceSystem("EPSG:4326")
            exportVector(layer, sln, layersFolder, restrictToExtent,
                         iface, extent, precision, crs, optimize)
            feedback.completeStep()
        elif (layer.type() == layer.RasterLayer and
                layer.providerType() != "wms"):
            feedback.showFeedback('Exporting %s as raster...' % layer.name())
            exportRaster(layer, count, layersFolder, feedback, iface, matchCRS)
            feedback.completeStep()
    feedback.completeStep()


def exportVector(layer, sln, layersFolder, restrictToExtent, iface,
                 extent, precision, crs, minify):
    canvas = iface.mapCanvas()
    cleanLayer = writeTmpLayer(layer, restrictToExtent, iface, extent)
    if is25d(layer, canvas, restrictToExtent, extent):
        add25dAttributes(cleanLayer, layer, canvas)
    tmpPath = os.path.join(layersFolder, sln + ".json")
    path = os.path.join(layersFolder, sln + ".js")
    options = []
    if precision != "maintain":
        options.append("COORDINATE_PRECISION=" + unicode(precision))
    QgsVectorFileWriter.writeAsVectorFormat(cleanLayer, tmpPath, "utf-8", crs,
                                            'GeoJson', 0,
                                            layerOptions=options)
    with open(path, mode="w", encoding="utf8") as f:
        f.write("var %s = " % ("json_" + sln))
        with open(tmpPath, encoding="utf8") as tmpFile:
            for line in tmpFile:
                if minify:
                    line = line.strip("\n\t ")
                    line = removeSpaces(line)
                f.write(line)
    os.remove(tmpPath)
    fields = layer.fields()
    for field in fields:
        exportImages(layer, field.name(), layersFolder + "/tmp.tmp")


def add25dAttributes(cleanLayer, layer, canvas):
    provider = cleanLayer.dataProvider()
    provider.addAttributes([QgsField("height", QVariant.Double),
                            QgsField("wallColor", QVariant.String),
                            QgsField("roofColor", QVariant.String)])
    cleanLayer.updateFields()
    fields = cleanLayer.fields()
    renderer = layer.renderer()
    renderContext = QgsRenderContext.fromMapSettings(canvas.mapSettings())
    feats = layer.getFeatures()
    context = QgsExpressionContext()
    context.appendScope(QgsExpressionContextUtils.layerScope(layer))
    expression = QgsExpression('eval(@qgis_25d_height)')
    heightField = fields.indexFromName("height")
    wallField = fields.indexFromName("wallColor")
    roofField = fields.indexFromName("roofColor")
    renderer.startRender(renderContext, fields)
    cleanLayer.startEditing()
    for feat in feats:
        context.setFeature(feat)
        height = expression.evaluate(context)
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
        sl1 = symbol.symbolLayer(1)
        sl2 = symbol.symbolLayer(2)
        wallColor = sl1.subSymbol().color().name()
        roofColor = sl2.subSymbol().color().name()
        provider.changeAttributeValues({feat.id() + 1: {heightField: height,
                                                        wallField: wallColor,
                                                        roofField: roofColor}})
    cleanLayer.commitChanges()
    renderer.stopRender(renderContext)


def exportRaster(layer, count, layersFolder, feedback, iface, matchCRS):
    feedback.showFeedback("Exporting %s to PNG..." % layer.name())
    name_ts = (safeName(layer.name()) + unicode(count) +
               unicode(int(time.time())))

    # We need to create a new file to export style
    piped_file = os.path.join(tempfile.gettempdir(), name_ts + '_piped.tif')

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

    file_writer.writeRaster(pipe, piped_height, -1, piped_extent, piped_crs)

    # Export layer as PNG
    out_raster = os.path.join(layersFolder, safeName(layer.name()) + "_" +
                              unicode(count) + ".png")

    projectCRS = iface.mapCanvas().mapSettings().destinationCrs()
    if not (matchCRS and layer.crs() == projectCRS):
        # Extent of the layer in EPSG:3857
        crsSrc = layer.crs()
        crsDest = QgsCoordinateReferenceSystem(3857)
        try:
            xform = QgsCoordinateTransform(crsSrc, crsDest,
                                           QgsProject.instance())
        except:
            xform = QgsCoordinateTransform(crsSrc, crsDest)
        extentRep = xform.transformBoundingBox(layer.extent())

        extentRepNew = ','.join([unicode(extentRep.xMinimum()),
                                 unicode(extentRep.xMaximum()),
                                 unicode(extentRep.yMinimum()),
                                 unicode(extentRep.yMaximum())])

        # Reproject in 3857
        piped_3857 = os.path.join(tempfile.gettempdir(),
                                  name_ts + '_piped_3857.tif')
        qgis_version = Qgis.QGIS_VERSION

        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        try:
            processing.algorithmHelp("gdal:warpreproject")
        except:
            pass
        sys.stdout = old_stdout

        params = {
            "INPUT": piped_file,
            "SOURCE_CRS": layer.crs().authid(),
            "TARGET_CRS": "EPSG:3857",
            "NODATA": 0,
            "TARGET_RESOLUTION": 0,
            "RESAMPLING": 2,
            "TARGET_EXTENT": extentRepNew,
            "EXT_CRS": "EPSG:3857",
            "TARGET_EXTENT_CRS": "EPSG:3857",
            "DATA_TYPE": 0,
            "COMPRESS": 4,
            "JPEGCOMPRESSION": 75,
            "ZLEVEL": 6,
            "PREDICTOR": 1,
            "TILED": False,
            "BIGTIFF": 0,
            "TFW": False,
            "MULTITHREADING": False,
            "COPY_SUBDATASETS": False,
            "EXTRA": "",
            "OUTPUT": piped_3857
        }

        warpArgs = {}

        lines = mystdout.getvalue()
        for count, line in enumerate(lines.split("\n")):
            if count != 0 and ":" in line:
                try:
                    k = line.split(":")[0]
                    warpArgs[k] = params[k]
                except:
                    pass

        try:
            processing.run("gdal:warpreproject", warpArgs)
        except:
            shutil.copyfile(piped_file, piped_3857)

        try:
            processing.run("gdal:translate", {"INPUT": piped_3857,
                                              "OUTSIZE": 100,
                                              "OUTSIZE_PERC": True,
                                              "NODATA": 0,
                                              "EXPAND": 0,
                                              "TARGET_CRS": "",
                                              "PROJWIN": extentRepNew,
                                              "SDS": False,
                                              "DATA_TYPE": 0,
                                              "COMPRESS": 4,
                                              "JPEGCOMPRESSION": 75,
                                              "ZLEVEL": 6,
                                              "PREDICTOR": 1,
                                              "TILED": False,
                                              "BIGTIFF": 0,
                                              "TFW": False,
                                              "COPY_SUBDATASETS": False,
                                              "OPTIONS": "",
                                              "OUTPUT": out_raster})
        except:
            shutil.copyfile(piped_3857, out_raster)
    else:
        srcExtent = ','.join([unicode(piped_extent.xMinimum()),
                              unicode(piped_extent.xMaximum()),
                              unicode(piped_extent.yMinimum()),
                              unicode(piped_extent.yMaximum())])
        processing.run("gdal:translate", {"INPUT": piped_file,
                                          "OUTSIZE": 100,
                                          "OUTSIZE_PERC": True,
                                          "NODATA": 0,
                                          "EXPAND": 0,
                                          "TARGET_CRS": "",
                                          "PROJWIN": srcExtent,
                                          "SDS": False,
                                          "DATA_TYPE": 0,
                                          "COMPRESS": 4,
                                          "JPEGCOMPRESSION": 75,
                                          "ZLEVEL": 6,
                                          "PREDICTOR": 1,
                                          "TILED": False,
                                          "BIGTIFF": 0,
                                          "TFW": False,
                                          "COPY_SUBDATASETS": False,
                                          "OPTIONS": "",
                                          "OUTPUT": out_raster})


def is25d(layer, canvas, restrictToExtent, extent):
    if layer.type() != layer.VectorLayer:
        return False
    if layer.geometryType() != QgsWkbTypes.PolygonGeometry:
        return False
    vts = layer.customProperty("VectorTilesReader/vector_tile_source")
    if vts is not None:
        return False
    renderer = layer.renderer()
    if isinstance(renderer, Qgs25DRenderer):
        return True
    symbols = []
    if isinstance(renderer, QgsCategorizedSymbolRenderer):
        categories = renderer.categories()
        for category in categories:
            symbols.append(category.symbol())
    elif isinstance(renderer, QgsGraduatedSymbolRenderer):
        ranges = renderer.ranges()
        for range in ranges:
            symbols.append(range.symbol())
    elif isinstance(renderer, QgsRuleBasedRenderer):
        rules = renderer.rootRule().children()
        for rule in rules:
            symbols.append(rule.symbol())
    else:
        renderContext = QgsRenderContext.fromMapSettings(canvas.mapSettings())
        fields = layer.fields()
        if restrictToExtent and extent == "Canvas extent":
            request = QgsFeatureRequest(canvas.extent())
            request.setFlags(QgsFeatureRequest.ExactIntersect)
            features = layer.getFeatures(request)
        else:
            features = layer.getFeatures()
        renderer.startRender(renderContext, fields)
        for feature in features:
            symbol = renderer.symbolForFeature(feature, renderContext)
            symbols.append(symbol)
        renderer.stopRender(renderContext)
    for sym in symbols:
        sl1 = sym.symbolLayer(1)
        sl2 = sym.symbolLayer(2)
        if (isinstance(sl1, QgsGeometryGeneratorSymbolLayer) and
                isinstance(sl2, QgsGeometryGeneratorSymbolLayer)):
            return True
    return False


def safeName(name):
    # TODO: we are assuming that at least one character is valid...
    validChr = '_0123456789abcdefghijklmnopqrstuvwxyz' \
               'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return ''.join(c for c in name if c in validChr)


def removeSpaces(txt):
    return '"'.join(it if i % 2 else ''.join(it.split())
                    for i, it in enumerate(txt.split('"')))


def scaleToZoom(scale):
    if scale < 1000:
        return 19
    elif scale < 2000:
        return 18
    elif scale < 4000:
        return 17
    elif scale < 8000:
        return 16
    elif scale < 15000:
        return 15
    elif scale < 35000:
        return 14
    elif scale < 70000:
        return 13
    elif scale < 150000:
        return 12
    elif scale < 250000:
        return 11
    elif scale < 500000:
        return 10
    elif scale < 1000000:
        return 9
    elif scale < 2000000:
        return 8
    elif scale < 4000000:
        return 7
    elif scale < 10000000:
        return 6
    elif scale < 15000000:
        return 5
    elif scale < 35000000:
        return 4
    elif scale < 70000000:
        return 3
    elif scale < 150000000:
        return 2
    elif scale < 250000000:
        return 1
    else:
        return 0


def replaceInTemplate(template, values):
    path = os.path.join(QgsApplication.qgisSettingsDirPath(),
                        "qgis2web",
                        "templates",
                        template)
    with open(path) as f:
        lines = f.readlines()
    s = "".join(lines)
    for name, value in values.items():
        s = s.replace(name, value)
    return s


def exportImages(layer, field, layerFileName):
    field_index = layer.fields().indexFromName(field)

    widget = layer.editorWidgetSetup(field_index).type()
    if widget != 'Photo':
        return

    fr = QgsFeatureRequest()
    fr.setSubsetOfAttributes([field_index])

    for feature in layer.getFeatures(fr):
        photo_file_name = feature.attribute(field)
        if type(photo_file_name) is not unicode:
            continue

        source_file_name = photo_file_name
        if not os.path.isabs(source_file_name):
            prj_fname = QgsProject.instance().fileName()
            source_file_name = os.path.join(os.path.dirname(prj_fname),
                                            source_file_name)

        photo_file_name = re.sub(r'[\\/:]', '_', photo_file_name).strip()
        photo_file_name = os.path.join(os.path.dirname(layerFileName),
                                       '..', 'images', photo_file_name)

        try:
            shutil.copyfile(source_file_name, photo_file_name)
        except IOError as e:
            pass


def handleHiddenField(layer, field):
    fieldIndex = layer.fields().indexFromName(field)
    editorWidget = layer.editorWidgetSetup(fieldIndex).type()
    if (editorWidget == 'Hidden'):
        fieldName = "q2wHide_" + field
    else:
        fieldName = field
    return fieldName


def getRGBAColor(color, alpha):
    r, g, b, a = color.split(",")
    a = (float(a) / 255) * alpha
    return "'rgba(%s)'" % ",".join([r, g, b, unicode(a)])
