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
from PyQt4.QtCore import QDir, QVariant
from PyQt4.QtGui import QPainter
from qgis.core import *
from qgis.utils import QGis
import processing
import tempfile

NO_POPUP = 0
ALL_ATTRIBUTES = 1

TYPE_MAP = {
    QGis.WKBPoint: 'Point',
    QGis.WKBPoint25D: 'Point',
    QGis.WKBLineString: 'LineString',
    QGis.WKBLineString25D: 'LineString',
    QGis.WKBPolygon: 'Polygon',
    QGis.WKBPolygon25D: 'Polygon',
    QGis.WKBMultiPoint: 'MultiPoint',
    QGis.WKBMultiLineString: 'MultiLineString',
    QGis.WKBMultiLineString25D: 'MultiLineString',
    QGis.WKBMultiPolygon: 'MultiPolygon',
    QGis.WKBMultiPolygon25D: 'MultiPolygon'}

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
        fields.append(layer.rendererV2().classAttribute())
    except:
        pass
    labelsEnabled = unicode(
        layer.customProperty("labeling/enabled")).lower() == "true"
    if labelsEnabled:
        fields.append(layer.customProperty("labeling/fieldName"))
    return fields


def writeTmpLayer(layer, popup):
    fields = layer.pendingFields()
    usedFields = []
    for count, field in enumerate(fields):
        fieldIndex = fields.indexFromName(unicode(field.name()))
        try:
            editorWidget = layer.editFormConfig().widgetType(fieldIndex)
        except:
            editorWidget = layer.editorWidgetV2(fieldIndex)
        addField = False
        try:
            if layer.rendererV2().classAttribute() == field.name():
                addField = True
        except:
            pass
        if layer.customProperty("labeling/fieldName") == field.name():
            addField = True
        if (editorWidget != QgsVectorLayer.Hidden and
                editorWidget != 'Hidden'):
            addField = True
        if addField:
            usedFields.append(count)
    uri = TYPE_MAP[layer.wkbType()]
    crs = layer.crs()
    if crs.isValid():
        uri += '?crs=' + crs.authid()
    for field in usedFields:
        fieldIndex = layer.pendingFields().indexFromName(unicode(
            layer.pendingFields().field(field).name()))
        try:
            editorWidget = layer.editFormConfig().widgetType(fieldIndex)
        except:
            editorWidget = layer.editorWidgetV2(fieldIndex)
        fieldType = layer.pendingFields().field(field).type()
        fieldName = layer.pendingFields().field(field).name()
        if (editorWidget == QgsVectorLayer.Hidden or
                editorWidget == 'Hidden'):
            fieldName = "q2wHide_" + fieldName
        fieldType = "double" if (fieldType == QVariant.Double or
                                 fieldType == QVariant.Int) else (
                                    "string")
        uri += '&field=' + unicode(fieldName) + ":" + fieldType
    newlayer = QgsVectorLayer(uri, layer.name(), 'memory')
    writer = newlayer.dataProvider()
    outFeat = QgsFeature()
    for feature in layer.getFeatures():
        if feature.geometry() is not None:
            outFeat.setGeometry(feature.geometry())
        attrs = [feature[f] for f in usedFields]
        if attrs:
            outFeat.setAttributes(attrs)
        writer.addFeatures([outFeat])
    return newlayer


def exportLayers(iface, layers, folder, precision, optimize, popupField, json):
    canvas = iface.mapCanvas()
    epsg4326 = QgsCoordinateReferenceSystem("EPSG:4326")
    layersFolder = os.path.join(folder, "layers")
    QDir().mkpath(layersFolder)
    for layer, encode2json, popup in zip(layers, json, popupField):
        if (layer.type() == layer.VectorLayer and
                (layer.providerType() != "WFS" or encode2json)):
            cleanLayer = writeTmpLayer(layer, popup)
            fields = layer.pendingFields()
            for field in fields:
                exportImages(layer, field.name(), layersFolder + "/tmp.tmp")
            if is25d(layer, canvas):
                provider = cleanLayer.dataProvider()
                provider.addAttributes([QgsField("height", QVariant.Double),
                                        QgsField("wallColor", QVariant.String),
                                        QgsField("roofColor",
                                                 QVariant.String)])
                cleanLayer.updateFields()
                fields = cleanLayer.pendingFields()
                renderer = layer.rendererV2()
                renderContext = QgsRenderContext.fromMapSettings(
                        canvas.mapSettings())
                feats = layer.getFeatures()
                context = QgsExpressionContext()
                context.appendScope(
                        QgsExpressionContextUtils.layerScope(layer))
                expression = QgsExpression('eval(@qgis_25d_height)')
                heightField = fields.indexFromName("height")
                wallField = fields.indexFromName("wallColor")
                roofField = fields.indexFromName("roofColor")
                renderer.startRender(renderContext, fields)
                cleanLayer.startEditing()
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
                        symbol = renderer.symbolForFeature2(feat,
                                                            renderContext)
                    sl1 = symbol.symbolLayer(1)
                    sl2 = symbol.symbolLayer(2)
                    wallColor = sl1.subSymbol().color().name()
                    roofColor = sl2.subSymbol().color().name()
                    provider.changeAttributeValues(
                            {feat.id() + 1:
                             {heightField: height,
                             wallField: wallColor,
                             roofField: roofColor}})
                cleanLayer.commitChanges()
                renderer.stopRender(renderContext)

            tmpPath = os.path.join(layersFolder,
                                   safeName(cleanLayer.name()) + ".json")
            path = os.path.join(layersFolder,
                                safeName(cleanLayer.name()) + ".js")
            if precision != "maintain":
                options = "COORDINATE_PRECISION=" + unicode(precision)
            else:
                options = ""
            QgsVectorFileWriter.writeAsVectorFormat(cleanLayer, tmpPath,
                                                    "utf-8", epsg4326,
                                                    'GeoJson', 0,
                                                    layerOptions=[options])
            with open(path, "w") as f:
                f.write("var %s = " % ("geojson_" +
                                       safeName(cleanLayer.name())))
                with open(tmpPath, "r") as f2:
                    for line in f2:
                        if optimize:
                            line = line.strip("\n\t ")
                            line = removeSpaces(line)
                        f.write(line)
            os.remove(tmpPath)

        elif (layer.type() == layer.RasterLayer and
                layer.providerType() != "wms"):

            name_ts = safeName(layer.name()) + unicode(int(time.time()))

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
            out_raster = os.path.join(layersFolder, layer.name() + ".png")

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
                    procRtn = processing.runalg("gdalogr:warpreproject",
                                                warpArgs)
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
                        procRtn = processing.runalg("gdalogr:warpreproject",
                                                    warpArgs)
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
                            procRtn = processing.runalg(
                                            "gdalogr:warpreproject",
                                            warpArgs)
                            # force exception on algorithm fail
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


def is25d(layer, canvas):
    try:
        renderer = layer.rendererV2()
        symbols = []
        if isinstance(renderer, QgsCategorizedSymbolRendererV2):
            categories = renderer.categories()
            for category in categories:
                symbols.append(category.symbol())
        elif isinstance(renderer, QgsGraduatedSymbolRendererV2):
            ranges = renderer.ranges()
            for range in ranges:
                symbols.append(range.symbol())
        else:
            renderContext = QgsRenderContext.fromMapSettings(
                    canvas.mapSettings())
            fields = layer.pendingFields()
            features = layer.getFeatures()
            renderer.startRender(renderContext, fields)
            for feature in features:
                symbol = renderer.symbolForFeature2(feature, renderContext)
                symbols.append(symbol)
            renderer.stopRender(renderContext)

        for sym in symbols:
            sl1 = sym.symbolLayer(1)
            sl2 = sym.symbolLayer(2)
            if (isinstance(sl1, QgsGeometryGeneratorSymbolLayerV2) and
                    isinstance(sl2, QgsGeometryGeneratorSymbolLayerV2)):
                return True
        return False
    except:
        # print traceback.format_exc()
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
    for name, value in values.iteritems():
        s = s.replace(name, value)
    return s


def exportImages(layer, field, layerFileName):
    field_index = layer.fieldNameIndex(field)

    try:
        widget = layer.editFormConfig().widgetType(field_index)
    except:
        widget = layer.editorWidgetV2(field_index)
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
    fieldIndex = layer.pendingFields().indexFromName(field)
    try:
        editFormConfig = layer.editFormConfig()
        editorWidget = editFormConfig.widgetType(fieldIndex)
    except:
        editorWidget = layer.editorWidgetV2(fieldIndex)
    if (editorWidget == QgsVectorLayer.Hidden or
            editorWidget == 'Hidden'):
        fieldName = "q2wHide_" + field
    else:
        fieldName = field
    return fieldName


def getRGBAColor(color, alpha):
    r, g, b, _ = color.split(",")
    return "'rgba(%s)'" % ",".join([r, g, b, unicode(alpha)])
