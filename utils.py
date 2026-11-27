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

import json
import os
import time
import re
import shutil
import sys
import string
from io import StringIO
from qgis.PyQt.QtCore import QDate, QDateTime, QDir, QMetaType, QTime
from qgis.PyQt.QtGui import QPainter

# QVariant.Type was removed in Qt 6; QMetaType.Type values work with QgsField
# in both PyQt5 and PyQt6/QGIS 4.
try:
    FIELD_TYPE_INT = QMetaType.Type.Int
    FIELD_TYPE_DOUBLE = QMetaType.Type.Double
    FIELD_TYPE_STRING = QMetaType.Type.QString
except AttributeError:
    FIELD_TYPE_INT = QMetaType.Int
    FIELD_TYPE_DOUBLE = QMetaType.Double
    FIELD_TYPE_STRING = QMetaType.QString
from qgis.core import (QgsApplication,
                       QgsMapLayer,
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
                       QgsNullSymbolRenderer,
                       QgsVectorFileWriter,
                       QgsRasterFileWriter,
                       QgsRasterPipe,
                       QgsMessageLog,
                       QgsWkbTypes,
                       Qgs25DRenderer,
                       QgsGeometryGeneratorSymbolLayer)
from qgis.utils import Qgis
import processing
import tempfile
from qgis2web.layer_manifest import (LayerExportCache, PBF_CACHE_SCHEMA,
                                     layer_data_hash, raster_data_hash)

# QGIS 4 exposes these enums through Qgis; QGIS 3.22 keeps the legacy aliases.
def _enum_value(enum_type, name, legacy_name=None):
    """Resolve a QGIS 4 enum member with its QGIS 3 legacy spelling fallback."""
    value = getattr(enum_type, name, None)
    if value is None and legacy_name:
        value = getattr(enum_type, legacy_name)
    return value


_WKB = getattr(Qgis, 'WkbType', QgsWkbTypes)
_GEOMETRY_TYPE = getattr(Qgis, 'GeometryType', QgsWkbTypes)
_MAP_LAYER_TYPE = getattr(QgsMapLayer, 'LayerType', QgsMapLayer)
LAYER_TYPE_VECTOR = _enum_value(_MAP_LAYER_TYPE, 'Vector', 'VectorLayer')
LAYER_TYPE_RASTER = _enum_value(_MAP_LAYER_TYPE, 'Raster', 'RasterLayer')
LAYER_TYPE_PLUGIN = _enum_value(_MAP_LAYER_TYPE, 'Plugin', 'PluginLayer')
GEOMETRY_TYPE_POINT = _enum_value(_GEOMETRY_TYPE, 'Point', 'PointGeometry')
GEOMETRY_TYPE_POLYGON = _enum_value(_GEOMETRY_TYPE, 'Polygon', 'PolygonGeometry')
MESSAGE_LEVEL = getattr(Qgis, 'MessageLevel', Qgis)
WKB_TYPE_NO_GEOMETRY = _WKB.NoGeometry
WKB_TYPE_MULTIPOINT = _WKB.MultiPoint

# QgsFeatureRequest flags moved to Qgis.FeatureRequestFlag in QGIS 3.36+; the
# flat members are gone in QGIS 4.
_FEATURE_REQUEST_FLAG = getattr(Qgis, 'FeatureRequestFlag', QgsFeatureRequest)
FEATURE_REQUEST_EXACT_INTERSECT = _enum_value(_FEATURE_REQUEST_FLAG,
                                              'ExactIntersect')

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
    _WKB.MultiPoint: 'MultiPoint',
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

MB_TYPE_MAP = {
    'Point': 'symbol',
    'LineString': 'line',
    'Polygon': 'fill'}

BLEND_MODES = {
    QPainter.CompositionMode.CompositionMode_SourceOver: 'normal',
    QPainter.CompositionMode.CompositionMode_Multiply: 'multiply',
    QPainter.CompositionMode.CompositionMode_Screen: 'screen',
    QPainter.CompositionMode.CompositionMode_Overlay: 'overlay',
    QPainter.CompositionMode.CompositionMode_Darken: 'darken',
    QPainter.CompositionMode.CompositionMode_Lighten: 'lighten',
    QPainter.CompositionMode.CompositionMode_ColorDodge: 'color-dodge',
    QPainter.CompositionMode.CompositionMode_ColorBurn: 'color-burn',
    QPainter.CompositionMode.CompositionMode_HardLight: 'hard-light',
    QPainter.CompositionMode.CompositionMode_SoftLight: 'soft-light',
    QPainter.CompositionMode.CompositionMode_Difference: 'difference',
    QPainter.CompositionMode.CompositionMode_Exclusion: 'exclusion'}

PLACEMENT = ['bottomleft', 'topleft', 'topright', 'bottomleft', 'bottomright']


def tempFolder():
    tempDir = os.path.join(QDir.tempPath(), 'qgis2web')
    if not QDir(tempDir).exists():
        QDir().mkpath(tempDir)

    return os.path.abspath(tempDir)


def getUsedFields(layer):
    fields = []
    try:
        fields.append(layer.renderer().classAttribute())
    except Exception:
        pass
    labelsEnabled = layer.customProperty("labeling/enabled").lower() == "true"
    if labelsEnabled:
        fields.append(layer.customProperty("labeling/fieldName"))
    return fields


def writeTmpLayer(layer, restrictToExtent, iface, extent):
    if layer.wkbType() == _WKB.NoGeometry:
        return

    fields = layer.fields()
    usedFields = []
    for count, field in enumerate(fields):
        fieldIndex = fields.indexFromName(field.name())
        editorWidget = layer.editorWidgetSetup(fieldIndex).type()
        addField = False
        try:
            if layer.renderer().classAttribute() == field.name():
                addField = True
        except Exception:
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
        fieldIndex = layer.fields().indexFromName(
            layer.fields().field(field).name())
        editorWidget = layer.editorWidgetSetup(fieldIndex).type()
        fieldType = layer.fields().field(field).type()
        fieldName = layer.fields().field(field).name()
        fieldLength = layer.fields().field(field).length()
        if (editorWidget == 'Hidden'):
            fieldName = "q2wHide_" + fieldName
        if fieldType == FIELD_TYPE_DOUBLE or fieldType == FIELD_TYPE_INT:
            fieldType = "double"
            fieldLength = max(fieldLength, 20)
        else:
            fieldType = "string"
            if fieldLength > 0:
                fieldLength = max(fieldLength, 255)
        uri += '&field=' + fieldName + ":" + fieldType + "(%d)" % fieldLength
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
        except Exception:
            transform = QgsCoordinateTransform(canvasCRS, layerCRS)
        projectedExtent = transform.transformBoundingBox(extent)
        request = QgsFeatureRequest(projectedExtent)
        request.setFlags(FEATURE_REQUEST_EXACT_INTERSECT)
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
                 restrictToExtent, extent, feedback, matchCRS, pbfVectorTile,
                 manifest_options=None):
    feedback.showFeedback('Exporting layers...')
    layersFolder = os.path.join(folder, "layers")
    QDir().mkpath(layersFolder)
    cache = None
    if manifest_options is not None:
        cache = LayerExportCache(
            manifest_options.get('map_format', 'openlayers'),
            manifest_options.get('previous_manifest'),
            manifest_options.get('previous_root'),
            manifest_options.get('remote_files'))

    pbf_vectortile_layers = [
        # knowing that print pbfVectorTile looks like this
        #[(False, None, None), (True, 0, 8)]
        # I only take the layers that are True, and get their names from layers[i].name()
        layers[i].name()
        for i in range(len(layers))
        if pbfVectorTile[i] and pbfVectorTile[i][0] == True
    ]

    for count, (layer, encode2json, popup) in enumerate(zip(layers, json,
                                                            popupField)):
        sln = safeName(layer.name()) + "_" + str(count)
        pbf_config = pbfVectorTile[count] if count < len(pbfVectorTile) else (False, None, None)
        pbf_enabled, pbf_min_zoom, pbf_max_zoom = pbf_config
        vts = layer.customProperty("VectorTilesReader/vector_tile_source")
        if (layer.type() == LAYER_TYPE_VECTOR and vts is None and
                (layer.providerType() != "WFS" or encode2json)):
            extent_options = None
            if restrictToExtent:
                try:
                    extent_options = {
                        'configured': str(extent),
                        'canvas': iface.mapCanvas().extent().toString(),
                    }
                except AttributeError:
                    extent_options = str(extent)
            data_options = {
                'writer': 'openlayers',
                'format': 'pbf' if pbf_enabled else 'geojson',
                'precision': precision,
                'minify': bool(optimize) if not pbf_enabled else False,
                'restrictToExtent': bool(restrictToExtent),
                'extent': extent_options,
                'renderer': (layer.renderer().dump()
                             if not pbf_enabled and layer.renderer()
                             else ''),
            }
            data_hash = layer_data_hash(layer, data_options) if cache else None
            if pbf_enabled:
                pbf_min = 3 if pbf_min_zoom is None else int(pbf_min_zoom)
                pbf_max = 4 if pbf_max_zoom is None else int(pbf_max_zoom)
                pbf_options = {
                    'schema': PBF_CACHE_SCHEMA,
                    'zmin': pbf_min,
                    'zmax': pbf_max,
                    'precision': precision,
                    'restrictToExtent': bool(restrictToExtent),
                    'extent': extent_options,
                    'stringifyAttributes': hasMixedAttributeTypes(layer),
                    'crs': 'EPSG:3857',
                }
                plan = (cache.inspect(
                    layer, sln, data_hash, pbf_options=pbf_options,
                    pbf_root='layers/{}-pbf'.format(sln)) if cache else
                    {'pbf_ranges': [(pbf_min, pbf_max)]})
                feedback.showFeedback('<span style="color: gray">(attributes json required for layer search)</span>')
                if plan['pbf_ranges']:
                    feedback.showFeedback(
                        'Exporting %s to PBF XYZ EPSG:3857 [z%d-z%d]...' %
                        (layer.name(), pbf_min, pbf_max))
                    feedback.showFeedback(
                        '<span style="color: gray">(only missing or incompatible '
                        'zoom levels are generated)</span>')
                    for range_index, (range_min, range_max) in enumerate(
                            plan['pbf_ranges']):
                        exportVectorTilesXYZ(
                            layer, sln, layersFolder, restrictToExtent,
                            iface, extent, precision, range_min, range_max,
                            pbf_vectortile_layers,
                            clear_output=range_index == 0,
                            export_images=range_index == 0)
                else:
                    feedback.showFeedback(
                        'Reusing unchanged PBF data for %s.' % layer.name())
                    exportLayerImages(
                        layer, os.path.join(os.path.dirname(layersFolder), 'images'))
            else:
                plan = (cache.inspect(
                    layer, sln, data_hash,
                    data_path='layers/{}.js'.format(sln)) if cache else
                    {'reuse_data': False})
                if plan['reuse_data']:
                    feedback.showFeedback(
                        'Reusing unchanged data for %s.' % layer.name())
                    exportLayerImages(
                        layer, os.path.join(os.path.dirname(layersFolder), 'images'))
                else:
                    feedback.showFeedback('Exporting %s to JSON...' % layer.name())
                    crs = QgsCoordinateReferenceSystem("EPSG:4326")
                    exportVector(layer, sln, layersFolder, restrictToExtent,
                                 iface, extent, precision, crs, optimize)
        elif (layer.type() == LAYER_TYPE_RASTER and
                layer.providerType() != "wms"):
            data_path = 'layers/{}.png'.format(sln)
            raster_options = {
                'matchCRS': bool(matchCRS),
                'projectCrs': iface.mapCanvas().mapSettings().destinationCrs().authid(),
                'width': layer.width(),
                'height': layer.height(),
            }
            data_hash = raster_data_hash(layer, raster_options) if cache else None
            plan = (cache.inspect(
                layer, sln, data_hash, data_path=data_path) if cache else
                {'reuse_data': False})
            if plan['reuse_data']:
                feedback.showFeedback(
                    'Reusing unchanged raster data for %s.' % layer.name())
            else:
                feedback.showFeedback('Exporting %s as raster...' % layer.name())
                exportRaster(layer, count, layersFolder, feedback, iface, matchCRS)
        elif cache:
            cache.inspect(layer, sln, None)
        feedback.completeStep()
    feedback.completeStep()
    return cache

def exportVectorTilesXYZ(layer, sln, layersFolder, restrictToExtent, iface,
                         extent, precision="maintain", min_zoom=None, max_zoom=None,
                         pbf_vectortile_layers=None, clear_output=True,
                         export_images=True):
    cleanLayer = writeTmpLayer(layer, restrictToExtent, iface, extent)
    if cleanLayer is None:
        QgsMessageLog.logMessage(
            "writeTmpLayer returned None for {} - skipping PBF export".format(layer.name()),
            "qgis2web",
            level=MESSAGE_LEVEL.Warning)
        return

    target_crs = QgsCoordinateReferenceSystem("EPSG:3857")
    if cleanLayer.crs().authid() != target_crs.authid():
        try:
            reprojected = processing.run("native:reprojectlayer", {
                "INPUT": cleanLayer,
                "TARGET_CRS": target_crs,
                "OUTPUT": "memory:"
            })
            cleanLayer = reprojected["OUTPUT"]
        except Exception as e:
            QgsMessageLog.logMessage(
                "Could not reproject layer {} to EPSG:3857 before PBF export: {}".format(layer.name(), str(e)),
                "qgis2web",
                level=MESSAGE_LEVEL.Warning)

    pbf_dir = os.path.join(layersFolder, sln + "-pbf")
    if clear_output and os.path.exists(pbf_dir):
        shutil.rmtree(pbf_dir)
    QDir().mkpath(pbf_dir)

    # json_dir = os.path.join(layersFolder, sln + "-json")
    # if os.path.exists(json_dir):
    #     shutil.rmtree(json_dir)
    # QDir().mkpath(json_dir)

    min_z = 3 if min_zoom is None else int(min_zoom)
    max_z = 4 if max_zoom is None else int(max_zoom)

    # The MVT encoder of QGIS deduplicates attribute values with a
    # QMap<QVariant, int>. Comparing a string value with a numeric one is
    # unordered, so its binary search can hit an unrelated entry and the tile
    # stores another value's index: labels (and popups) then show the wrong
    # attribute. Writing every tile attribute as text keeps the ordering total.
    stringify_attributes = hasMixedAttributeTypes(cleanLayer)

    # Always use the layer extent converted to EPSG:3857
    layer_crs = cleanLayer.crs()
    extent_param = None
    try:
        transform = QgsCoordinateTransform(layer_crs, target_crs,
                                           QgsProject.instance())
    except Exception:
        transform = QgsCoordinateTransform(layer_crs, target_crs)
    extent_param = transform.transformBoundingBox(cleanLayer.extent())

    # # Add idO field with progressive numbering for each geometry
    # try:
    #     provider = cleanLayer.dataProvider()
    #     idO_field = QgsField("idO", QVariant.Int)
    #     provider.addAttributes([idO_field])
    #     cleanLayer.updateFields()
    #     idO_index = cleanLayer.fields().indexFromName("idO")
    #     if idO_index >= 0:
    #         feat_ids = {}
    #         for i, feature in enumerate(cleanLayer.getFeatures(), start=1):
    #             feat_ids[feature.id()] = {idO_index: i}
    #         if feat_ids:
    #             cleanLayer.startEditing()
    #             provider.changeAttributeValues(feat_ids)
    #             cleanLayer.commitChanges()
    # except Exception as e:
    #     QgsMessageLog.logMessage(
    #         "Could not add idO field to {}: {}".format(layer.name(), str(e)),
    #         "qgis2web",
    #         level=MESSAGE_LEVEL.Warning)

    # # Export individual JSON files ({sln}-{idO}.json) with WKB geometry (EPSG:3857) + properties
    # # Geometry is base64-encoded WKB, ready for ol.format.WKB().readGeometry() in JS
    # try:
    #     import json
    #     import base64

    #     fields = cleanLayer.fields()
    #     for feature in cleanLayer.getFeatures():
    #         geom = feature.geometry()
    #         if geom is None or geom.isNull():
    #             continue
    #         idO_val = feature.attribute("idO")
    #         if idO_val is None:
    #             continue
    #         # WKB in EPSG:3857 (cleanLayer is already in 3857)
    #         wkb = geom.asWkb()
    #         if wkb is None or len(wkb) == 0:
    #             continue
    #         wkb_b64 = base64.b64encode(bytes(wkb)).decode('ascii')
    #         # SAFE ATTRIBUTES (QVariant FIX)
    #         props = {}
    #         for field in fields:
    #             val = safe_json_value(feature.attribute(field.name()))
    #             if hasattr(val, "value"):
    #                 try:
    #                     val = val.value()
    #                 except:
    #                     val = str(val)
    #             # "NULL" string → JSON null (field kept, value becomes null)
    #             if isinstance(val, str) and val.strip().upper() == "NULL":
    #                 val = None
    #             props[field.name()] = val
    #         feature_item = {
    #             "geometry": wkb_b64,
    #             "properties": props
    #         }
    #         filename = f"{sln}-{idO_val}.json"
    #         filepath = os.path.join(json_dir, filename)
    #         with open(filepath, "w", encoding="utf-8") as f:
    #             json.dump(feature_item, f)
    # except Exception as e:
    #     QgsMessageLog.logMessage(
    #         "Could not write individual geometry JSON for {}: {}".format(layer.name(), str(e)),
    #         "qgis2web",
    #         level=MESSAGE_LEVEL.Warning
    #     )

    # Export images BEFORE PBF (so it runs even if PBF succeeds and returns)
    if export_images:
        exportLayerImages(
            layer, os.path.join(os.path.dirname(layersFolder), 'images'))

    # # save attributes-only JSON for layer search
    # try:
    #     search_json_path = os.path.join(json_dir, f"{sln}-all.json")
    #     exportJSONWithoutGeometry(cleanLayer, search_json_path)
    # except Exception as e:
    #     QgsMessageLog.logMessage(
    #         "Could not export searchable JSON for {}: {}".format(layer.name(), str(e)),
    #         "qgis2web",
    #         level=MESSAGE_LEVEL.Warning
    #     )
    last_error = None

    try:
        layers_config = []

        # ricevo layer sfoltito e semplificato in base alla geometria e alla zoom level
        for z in range(min_z, max_z + 1):
            zoomLayer = buildZoomLayer(cleanLayer, z, stringify_attributes)
            zoomLayer.setName(sln)
            layers_config.append({
                "layer": zoomLayer,
                "minZoom": z,
                "maxZoom": z
            })
        params = {
            "LAYERS": layers_config,
            "MIN_ZOOM": min_z,
            "MAX_ZOOM": max_z,
            #"EXTENT": extent_param,
            "XYZ_TEMPLATE": "{z}/{x}/{y}.pbf",
            "OUTPUT_DIRECTORY": pbf_dir,
        }
        processing.run("native:writevectortiles_xyz", params)
        QgsMessageLog.logMessage(
            "PBF export OK for {} (native:writevectortiles_xyz)".format(layer.name()),
            "qgis2web")
        return
    except Exception as e:
        last_error = e
        QgsMessageLog.logMessage(
            "native:writevectortiles_xyz failed: {}".format(str(e)),
            "qgis2web")

    # --- All strategies failed ---
    raise RuntimeError(
        "PBF vector tile export failed for layer '{}'. All algorithms tried. "
        "Last error: {}".format(layer.name(), str(last_error)))


def exportLayerImages(layer, images_folder):
    """Export image attributes even when the layer's data files are reused."""
    QDir().mkpath(images_folder)
    try:
        for field in layer.fields():
            exportImages(layer, field.name(), images_folder)
    except Exception as error:
        QgsMessageLog.logMessage(
            "Could not export images for {}: {}".format(layer.name(), str(error)),
            "qgis2web",
            level=MESSAGE_LEVEL.Warning)


WORLD_SIZE = 40075016.68557849

def numericFieldTypeIds():
    """QVariant type ids QgsField.type() uses for numeric values."""
    ids = set()
    containers = [getattr(QMetaType, "Type", None), QMetaType]
    names = ("Int", "UInt", "LongLong", "ULongLong", "Double", "Float", "Bool")
    for container in containers:
        if container is None:
            continue
        for name in names:
            value = getattr(container, name, None)
            if isinstance(value, int):
                ids.add(value)
    return ids


def hasMixedAttributeTypes(layer):
    """True when the layer mixes text and numeric attribute values."""
    numeric_ids = numericFieldTypeIds()
    has_numeric = False
    has_text = False
    for field in layer.fields():
        if field.type() in numeric_ids:
            has_numeric = True
        else:
            has_text = True
    return has_numeric and has_text


def createMemoryLayerLike(layer, name_suffix="", stringifyAttributes=False):
    geom_type = QgsWkbTypes.displayString(layer.wkbType())
    uri = geom_type
    if layer.crs().isValid():
        uri += "?crs=" + layer.crs().authid()
    out = QgsVectorLayer(
        uri,
        layer.name() + name_suffix,
        "memory"
    )
    provider = out.dataProvider()
    if stringifyAttributes:
        provider.addAttributes(
            [QgsField(field.name(), FIELD_TYPE_STRING)
             for field in layer.fields()])
    else:
        provider.addAttributes(layer.fields())
    out.updateFields()
    return out

def simplifyTolerance(z):
    """
    Tolleranza molto conservativa.
    Molto meno aggressiva di Tippecanoe.
    """
    tile_size = WORLD_SIZE / (2 ** z)
    return tile_size / 4096.0

def representativePoint(geom):
    if geom.isMultipart():
        if QgsWkbTypes.geometryType(geom.wkbType()) == GEOMETRY_TYPE_POINT:
            pts = geom.asMultiPoint()
            if pts:
                return pts[0]
    else:
        if QgsWkbTypes.geometryType(geom.wkbType()) == GEOMETRY_TYPE_POINT:
            return geom.asPoint()
    return None

def thinPointLayer(layer, zoom, stringifyAttributes=False):
    tile_size = WORLD_SIZE / (2 ** zoom)
    # extent = 4096
    # GRID_SIZE = 32
    #
    # => 4096/32 = 128 celle
    cell_size = tile_size / 128.0
    occupied = set()
    out = createMemoryLayerLike(
        layer,
        "_z{}".format(zoom),
        stringifyAttributes
    )
    provider = out.dataProvider()

    feats_out = []
    for feat in layer.getFeatures():
        geom = feat.geometry()
        if not geom or geom.isEmpty():
            continue
        p = representativePoint(geom)
        if p is None:
            continue
        gx = int(p.x() / cell_size)
        gy = int(p.y() / cell_size)
        key = (gx, gy)
        if key in occupied:
            continue
        occupied.add(key)
        feats_out.append(QgsFeature(feat))
    if feats_out:
        provider.addFeatures(feats_out)
    out.updateExtents()
    QgsMessageLog.logMessage(
        "Zoom {} -> {} point features".format(
            zoom,
            len(feats_out)
        ),
        "qgis2web"
    )
    return out

def simplifyLayer(layer, zoom, stringifyAttributes=False):
    tol = simplifyTolerance(zoom)
    out = createMemoryLayerLike(
        layer,
        "_z{}".format(zoom),
        stringifyAttributes
    )
    provider = out.dataProvider()

    feats_out = []
    for feat in layer.getFeatures():
        geom = feat.geometry()
        if not geom or geom.isEmpty():
            continue
        try:
            # Simplify geometry preserving topology, WITHOUT clipping to extent
            simplified = QgsTopologyPreservingSimplifier(tol).simplify(geom)
            if simplified and not simplified.isEmpty():
                geom = simplified
        except Exception:
            pass
        new_feat = QgsFeature(out.fields())
        new_feat.setAttributes(feat.attributes())
        new_feat.setGeometry(geom)
        feats_out.append(new_feat)
    if feats_out:
        provider.addFeatures(feats_out)
    out.updateExtents()
    QgsMessageLog.logMessage(
        "Zoom {} -> {} simplified features (tol={})".format(
            zoom,
            len(feats_out),
            round(tol, 2)
        ),
        "qgis2web"
    )
    return out

def buildZoomLayer(layer, zoom, stringifyAttributes=False):
    geom_type = QgsWkbTypes.geometryType(layer.wkbType())
    if geom_type == GEOMETRY_TYPE_POINT:
        return thinPointLayer(layer, zoom, stringifyAttributes)
    return simplifyLayer(layer, zoom, stringifyAttributes)


def safe_json_value(val):
    if val is None:
        return None
    # Python native
    if isinstance(val, (str, int, float, bool)):
        return val
    # QGIS/QVariant unwrap
    try:
        if hasattr(val, "value"):
            val = val.value()
    except:
        return str(val)
    # QGIS date/time
    if isinstance(val, QDate):
        return val.toString("yyyy-MM-dd")
    if isinstance(val, QDateTime):
        return val.toString("yyyy-MM-ddTHH:mm:ss")
    if isinstance(val, QTime):
        return val.toString("HH:mm:ss")
    # fallback totale
    return str(val)

def exportJSONWithoutGeometry(layer, output_path):
    features = []
    for feature in layer.getFeatures():
        props = {}
        for field in layer.fields():
            val = safe_json_value(feature.attribute(field.name()))
            if hasattr(val, "value"):
                try:
                    val = val.value()
                except:
                    val = str(val)
            # "NULL" string → JSON null (field kept, value becomes null)
            if isinstance(val, str) and val.strip().upper() == "NULL":
                val = None
            props[field.name()] = val
        features.append({
            "type": "Feature",
            "properties": props,
            "geometry": None
        })
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f)

        
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
        options.append("COORDINATE_PRECISION=" + str(precision))         
    
    # Define all features coordinates to 4326
    tr = QgsCoordinateTransform(cleanLayer.crs(), crs, QgsProject.instance())
    # Define option for vector file
    save_options = QgsVectorFileWriter.SaveVectorOptions()
    save_options.fileEncoding = 'utf-8' 
    save_options.ct = tr  
    save_options.driverName = 'GeoJson'
    save_options.onlySelectedFeatures = 0
    save_options.layerOptions = options     
    
    # Make sure that we are using the latest (non-deprecated) write method
    if hasattr(QgsVectorFileWriter, 'writeAsVectorFormatV3'):
        # Use writeAsVectorFormatV3 for QGIS versions >= 3.20 to avoid DeprecationWarnings
        result = QgsVectorFileWriter.writeAsVectorFormatV3(cleanLayer, tmpPath, QgsProject.instance().transformContext(), save_options)
    else:
        # Use writeAsVectorFormat for QGIS versions < 3.10.3 for backwards compatibility
        result = QgsVectorFileWriter.writeAsVectorFormat(cleanLayer, tmpPath, "utf-8", crs, 'GeoJson', 0, layerOptions=options)   
    if result:
        with open(path, mode="w", encoding="utf8") as f:
            f.write("var %s = " % ("json_" + sln))
            with open(tmpPath, encoding="utf8") as tmpFile:
                for line in tmpFile:
                    if minify:
                        line = line.strip("\n\t ")
                        line = removeSpaces(line)
                    f.write(line)
        os.remove(tmpPath)
    else:
        QgsMessageLog.logMessage(
            "Could not write json file {}: {}".format(tmpPath, result),
            "qgis2web",
            level=MESSAGE_LEVEL.Critical)
        return

    fields = layer.fields()
    images_folder = os.path.join(os.path.dirname(layersFolder), 'images')
    for field in fields:
        exportImages(layer, field.name(), images_folder)



def add25dAttributes(cleanLayer, layer, canvas):
    provider = cleanLayer.dataProvider()
    provider.addAttributes([QgsField("height", FIELD_TYPE_DOUBLE),
                            QgsField("wallColor", FIELD_TYPE_STRING),
                            QgsField("roofColor", FIELD_TYPE_STRING)])
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
    name_ts = safeName(layer.name()) + str(count) + str(int(time.time()))

    # We need to create a new file to export style
    piped_file = os.path.join(tempfile.gettempdir(), name_ts + '_piped.tif')

    piped_extent = layer.extent()
    # piped_width = layer.height()
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
    out_raster = os.path.join(layersFolder,
                              safeName(layer.name()) + "_" +
                              str(count) + ".png")

    projectCRS = iface.mapCanvas().mapSettings().destinationCrs()
    if not (matchCRS and layer.crs() == projectCRS):
        # Extent of the layer in EPSG:3857
        crsSrc = layer.crs()
        crsDest = QgsCoordinateReferenceSystem(3857)
        try:
            xform = QgsCoordinateTransform(crsSrc, crsDest,
                                           QgsProject.instance())
        except Exception:
            xform = QgsCoordinateTransform(crsSrc, crsDest)
        extentRep = xform.transformBoundingBox(layer.extent())

        extentRepNew = ','.join([str(extentRep.xMinimum()),
                                 str(extentRep.xMaximum()),
                                 str(extentRep.yMinimum()),
                                 str(extentRep.yMaximum())])

        # Reproject in 3857
        piped_3857 = os.path.join(tempfile.gettempdir(),
                                  name_ts + '_piped_3857.tif')
        # qgis_version = Qgis.QGIS_VERSION

        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        try:
            processing.algorithmHelp("gdal:warpreproject")
        except Exception:
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
                except Exception:
                    pass

        try:
            processing.run("gdal:warpreproject", warpArgs)
        except Exception:
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
        except Exception:
            shutil.copyfile(piped_3857, out_raster)
    else:
        srcExtent = ','.join([str(piped_extent.xMinimum()),
                              str(piped_extent.xMaximum()),
                              str(piped_extent.yMinimum()),
                              str(piped_extent.yMaximum())])
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
    if layer.type() != LAYER_TYPE_VECTOR:
        return False
    if layer.geometryType() != GEOMETRY_TYPE_POLYGON:
        return False
    vts = layer.customProperty("VectorTilesReader/vector_tile_source")
    if vts is not None:
        return False
    renderer = layer.renderer()
    if isinstance(renderer, QgsNullSymbolRenderer):
        return False
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
            request.setFlags(FEATURE_REQUEST_EXACT_INTERSECT)
            features = layer.getFeatures(request)
        else:
            features = layer.getFeatures()
        renderer.startRender(renderContext, fields)
        for feature in features:
            symbol = renderer.symbolForFeature(feature, renderContext)
            symbols.append(symbol)
        renderer.stopRender(renderContext)
    for sym in symbols:
        try:
            sl1 = sym.symbolLayer(1)
            sl2 = sym.symbolLayer(2)
        except IndexError:
            return False
        if (isinstance(sl1, QgsGeometryGeneratorSymbolLayer) and
                isinstance(sl2, QgsGeometryGeneratorSymbolLayer)):
            return True
    return False


def safeName(name):
    # TODO: we are assuming that at least one character is valid...
    validChr = '_' + string.digits + string.ascii_letters
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


def exportImages(layer, field, imagesFolder):
    field_index = layer.fields().indexFromName(field)

    widget = layer.editorWidgetSetup(field_index).type()
    if widget != 'ExternalResource':
        return

    fr = QgsFeatureRequest()
    fr.setSubsetOfAttributes([field_index])

    for feature in layer.getFeatures(fr):
        photo_file_name = feature.attribute(field)
        if type(photo_file_name) is not str:
            continue

        source_file_name = photo_file_name
        if not os.path.isabs(source_file_name):
            prj_fname = QgsProject.instance().fileName()
            source_file_name = os.path.join(os.path.dirname(prj_fname),
                                            source_file_name)

        photo_file_name = re.sub(r'[\\/:]', '_', photo_file_name).strip()
        photo_file_name = os.path.join(imagesFolder, photo_file_name)

        try:
            shutil.copyfile(source_file_name, photo_file_name)
        except IOError:
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
    r, g, b, a = color.split(",")[:4]
    a = (float(a) / 255) * alpha
    return "'rgba(%s)'" % ",".join([r, g, b, str(a)])

def boilType(fieldType):
    fType = None
    if fieldType.lower() in ["boolean", "bool"]:
        fType = "bool"
    if fieldType.lower() in ["double", "real", "decimal", "numeric"]:
        fType = "real"
    if fieldType.lower() in ["integer", "integer64", "uint",
                             "int", "longlong", "int4", "ulonglong"]:
        fType = "int"
    if fieldType.lower() in ["char", "string", "text", "varchar", "nchar",
                             "nvarchar"]:
        fType = "str"
    if fieldType.lower() in ["date"]:
        fType = "date"
    if fieldType.lower() in ["datetime", "timestamp",
                             "timestamp without time zone"]:
        fType = "datetime"
    if fieldType.lower() in ["time"]:
        fType = "time"
    return fType


def returnFilterValues(layer_list, fieldName, fieldType):
    if fieldType.lower() == "bool":
        return {"name": fieldName, "type": fieldType,
                "values": ["true", "false"]}
    filterValues = []
    for layer in layer_list:
        if layer.type() == LAYER_TYPE_VECTOR:
            fields = layer.fields()
            for f in fields:
                if boilType(f.typeName()) == fieldType:
                    if f.name() == fieldName:
                        iterator = layer.getFeatures()
                        for feature in iterator:
                            if feature[fieldName] is not None:
                                filterValues.append(feature[fieldName])
    if filterValues == []:
        return
    if fieldType == "str":
        cleanFilterValues = list(dict.fromkeys(filterValues))
        cleanFilterValues.sort()
    if fieldType == "int":
        cleanFilterValues = [min(filterValues) if min(filterValues) >= 0
                             else 0,
                             max(filterValues) if max(filterValues) >= 0
                             else 0]
        if cleanFilterValues[0] == cleanFilterValues[1]:
            cleanFilterValues[1] = cleanFilterValues[0] + 1
    if fieldType in ["date", "time", "real", "datetime"]:
        cleanFilterValues = [min(filter(None, filterValues)),
                             max(filterValues)]
        if cleanFilterValues[0] == cleanFilterValues[1]:
            if fieldType == "real":
                add = 1 / 10 * (cleanFilterValues[1] - cleanFilterValues[0])
                cleanFilterValues[1] = cleanFilterValues[0] + add
    return {"name": fieldName, "type": fieldType, "values": cleanFilterValues}
