import os
import shutil
import re
import codecs
import math
import xml.etree.ElementTree
import traceback
from PyQt4.QtCore import QDir, QPyNullVariant, QSize
from qgis.core import (QgsVectorLayer,
                       QgsSingleSymbolRendererV2,
                       QgsCategorizedSymbolRendererV2,
                       QgsGraduatedSymbolRendererV2,
                       QgsRuleBasedRendererV2,
                       QgsSimpleMarkerSymbolLayerV2,
                       QgsSvgMarkerSymbolLayerV2,
                       QgsFontMarkerSymbolLayerV2,
                       QgsSimpleLineSymbolLayerV2,
                       QgsSimpleFillSymbolLayerV2,
                       QgsLinePatternFillSymbolLayer,
                       QgsSymbolLayerV2Utils,
                       QgsPalLayerSettings,
                       QgsMessageLog)
from exp2js import compile_to_file
from utils import safeName, getRGBAColor, handleHiddenField, TYPE_MAP


def exportStyles(layers, folder, clustered):
    stylesFolder = os.path.join(folder, "styles")
    QDir().mkpath(stylesFolder)
    legendFolder = os.path.join(stylesFolder, "legend")
    QDir().mkpath(legendFolder)
    vtStyles = {}
    mapUnitLayers = []
    for count, (layer, cluster) in enumerate(zip(layers, clustered)):
        sln = safeName(layer.name()) + "_" + unicode(count)
        if layer.type() != layer.VectorLayer:
            continue
        labelsEnabled = unicode(
            layer.customProperty("labeling/enabled")).lower() == "true"
        pattern = ""
        setPattern = ""
        vts = layer.customProperty("VectorTilesReader/vector_tile_source")
        labelText = getLabels(labelsEnabled, layer, folder, sln)
        defs = "var size = 0;\nvar placement = 'point';"
        try:
            renderer = layer.rendererV2()
            layer_alpha = layer.layerTransparency()
            if isinstance(renderer, QgsSingleSymbolRendererV2):
                (style, pattern, setPattern, value,
                 useMapUnits) = singleSymbol(renderer, stylesFolder,
                                             layer_alpha, sln, legendFolder,
                                             layer)
            elif isinstance(renderer, QgsCategorizedSymbolRendererV2):
                (style, pattern, setPattern, value, defs,
                 useMapUnits) = categorized(defs, sln, layer, renderer,
                                            legendFolder, stylesFolder,
                                            layer_alpha)
            elif isinstance(renderer, QgsGraduatedSymbolRendererV2):
                (style, pattern, setPattern, value,
                 useMapUnits) = graduated(layer, renderer, legendFolder, sln,
                                          stylesFolder, layer_alpha)
            elif isinstance(renderer, QgsRuleBasedRendererV2):
                (style, pattern, setPattern, value,
                 useMapUnits) = ruleBased(renderer, folder, stylesFolder,
                                          layer_alpha, sln, layer)
            else:
                style = """
    var style = [ new ol.style.Style({
        text: createTextStyle(feature, resolution, labelText, labelFont,
                              labelFill, placement)
    })];"""
                useMapUnits = False
            if useMapUnits:
                if vts is None:
                    mapUnitLayers.append(sln)
                else:
                    mapUnitLayers.append(safeName(vts))
            (labelRes, size, face, color) = getLabelFormat(layer)
            if style != "":
                geom = TYPE_MAP[layer.wkbType()].replace("Multi", "")
                style = getStyle(style, cluster, labelRes, labelText,
                                 sln, size, face, color, value, geom)
            else:
                style = "''"
        except Exception, e:
            style = ""
            QgsMessageLog.logMessage(traceback.format_exc(), "qgis2web",
                                     level=QgsMessageLog.CRITICAL)

        if vts is None:
            path = os.path.join(stylesFolder, sln + "_style.js")

            with codecs.open(path, "w", "utf-8") as f:
                f.write('''%(defs)s
%(pattern)s
var style_%(name)s = %(style)s;
%(setPattern)s''' %
                        {"defs": defs, "pattern": pattern, "name": sln,
                         "style": style, "setPattern": setPattern})
        elif style != "" and style != "''":
            new_vtStyle = "if (feature.get('layer') == "
            new_vtStyle += """'%s' && feature.getGeometry().getType() == '%s'){
            return %s(feature, resolution);
        }""" % (
                layer.name(), TYPE_MAP[layer.wkbType()].replace("Multi", ""),
                style)
            try:
                old_vtStyles = vtStyles[vts]
                new_vtStyles = """%s
                %s""" % (old_vtStyles, new_vtStyle)
            except:
                new_vtStyles = new_vtStyle
            vtStyles[vts] = new_vtStyles
    for k, v in vtStyles.items():
        styleName = safeName(k)
        styleString = v
        path = os.path.join(stylesFolder, styleName + "_style.js")

        with codecs.open(path, "w", "utf-8") as f:
            f.write('''
var style_%(name)s = function(feature, resolution) {
    %(style)s;
}''' % {"defs": defs, "pattern": pattern, "name": styleName,
                    "style": styleString, "setPattern": setPattern})
    return mapUnitLayers


def getLabels(labelsEnabled, layer, folder, sln):
    if (labelsEnabled):
        labelField = layer.customProperty("labeling/fieldName")
        if labelField != "":
            if unicode(layer.customProperty(
                    "labeling/isExpression")).lower() == "true":
                exprFilename = os.path.join(folder, "resources",
                                            "qgis2web_expressions.js")
                fieldName = layer.customProperty("labeling/fieldName")
                name = compile_to_file(fieldName, "label_%s" % sln,
                                       "OpenLayers3", exprFilename)
                js = "%s(context)" % (name)
                js = js.strip()
                labelText = js
            else:
                fieldIndex = layer.pendingFields().indexFromName(labelField)
                editFormConfig = layer.editFormConfig()
                editorWidget = editFormConfig.widgetType(fieldIndex)
                if (editorWidget == QgsVectorLayer.Hidden or
                        editorWidget == 'Hidden'):
                    labelField = "q2wHide_" + labelField
                labelText = ('feature.get("%s")' %
                             labelField.replace('"', '\\"'))
        else:
            labelText = '""'
    else:
        labelText = '""'
    return labelText


def getLabelFormat(layer):
    if layer.customProperty("labeling/fontSize"):
        size = float(layer.customProperty("labeling/fontSize")) * 1.3
    else:
        size = 10
    italic = layer.customProperty("labeling/fontItalic")
    bold = layer.customProperty("labeling/fontWeight")
    r = layer.customProperty("labeling/textColorR")
    g = layer.customProperty("labeling/textColorG")
    b = layer.customProperty("labeling/textColorB")
    if (r or g or b) is None:
        color = "rgba(0, 0, 0, 1)"
    else:
        color = "rgba(%s, %s, %s, 1)" % (r, g, b)
    face = layer.customProperty("labeling/fontFamily")
    if face is None:
        face = ","
    else:
        face = " \\'%s\\'," % face
    palyr = QgsPalLayerSettings()
    palyr.readFromLayer(layer)
    sv = palyr.scaleVisibility
    if sv:
        min = float(palyr.scaleMin)
        max = float(palyr.scaleMax)
        if min != 0:
            min = 1 / ((1 / min) * 39.37 * 90.7)
        max = 1 / ((1 / max) * 39.37 * 90.7)
        labelRes = " && resolution > %(min)d " % {"min": min}
        labelRes += "&& resolution < %(max)d" % {"max": max}
    else:
        labelRes = ""
    buffer = palyr.bufferDraw
    if buffer:
        bufferColor = palyr.bufferColor.name()
        bufferWidth = palyr.bufferSize
        stroke = """
              stroke: new ol.style.Stroke({
                color: "%s",
                width: %d
              }),""" % (bufferColor, bufferWidth)
    else:
        stroke = ""
    return (labelRes, size, face, color)


def singleSymbol(renderer, stylesFolder, layer_alpha, sln, legendFolder,
                 layer):
    symbol = renderer.symbol()
    (style, pattern, setPattern,
     useMapUnits) = getSymbolAsStyle(symbol, stylesFolder,
                                     layer_alpha, renderer, sln, layer)
    style = "var style = " + style
    legendIcon = QgsSymbolLayerV2Utils.symbolPreviewPixmap(
        symbol, QSize(16, 16))
    legendIcon.save(os.path.join(legendFolder, sln + ".png"))
    value = 'var value = ""'
    return (style, pattern, setPattern, value, useMapUnits)


def categorized(defs, sln, layer, renderer, legendFolder, stylesFolder,
                layer_alpha):
    cluster = False
    defs += """
function categories_%s(feature, value, size, resolution, labelText,
                       labelFont, labelFill) {
                switch(value.toString()) {""" % sln
    cats = []
    useAnyMapUnits = False
    for cnt, cat in enumerate(renderer.categories()):
        legendIcon = QgsSymbolLayerV2Utils.symbolPreviewPixmap(cat.symbol(),
                                                               QSize(16, 16))
        legendIcon.save(os.path.join(legendFolder,
                                     sln + "_" + unicode(cnt) + ".png"))
        if (cat.value() is not None and cat.value() != "" and
                not isinstance(cat.value(), QPyNullVariant)):
            categoryStr = "case '%s':" % unicode(
                cat.value()).replace("'", "\\'")
        else:
            categoryStr = "default:"
        (style, pattern, setPattern,
         useMapUnits) = (getSymbolAsStyle(cat.symbol(), stylesFolder,
                                          layer_alpha, renderer, sln, layer))
        if useMapUnits:
            useAnyMapUnits = True
        categoryStr += '''
                    return %s;
                    break;''' % style
        cats.append(categoryStr)
    defs += "\n".join(cats) + "}};"
    style = """
var style = categories_%s(feature, value, size, resolution, labelText,
                          labelFont, labelFill)""" % sln
    value = getValue(layer, renderer)
    return (style, pattern, setPattern, value, defs, useAnyMapUnits)


def graduated(layer, renderer, legendFolder, sln, stylesFolder, layer_alpha):
    cluster = False
    ranges = []
    elseif = ""
    useAnyMapUnits = False
    for cnt, ran in enumerate(renderer.ranges()):
        legendIcon = QgsSymbolLayerV2Utils.symbolPreviewPixmap(
            ran.symbol(), QSize(16, 16))
        legendIcon.save(os.path.join(
            legendFolder, sln + "_" + unicode(cnt) + ".png"))
        (symbolstyle, pattern, setPattern,
         useMapUnits) = getSymbolAsStyle(ran.symbol(), stylesFolder,
                                         layer_alpha, renderer, sln, layer)
        ranges.append("""%sif (value > %f && value <= %f) {
            style = %s
                    }""" % (elseif, ran.lowerValue(), ran.upperValue(),
                            symbolstyle))
        elseif = " else "
        if useMapUnits:
            useAnyMapUnits = True
    style = "".join(ranges)
    value = getValue(layer, renderer)
    return (style, pattern, setPattern, value, useAnyMapUnits)


def ruleBased(renderer, folder, stylesFolder, layer_alpha, sln, layer):
    cluster = False
    template = """
        function rules_%s(feature, value) {
            var context = {
                feature: feature,
                variables: {}
            };
            // Start of if blocks and style check logic
            %s
            else {
                return %s;
            }
        }
        var style = rules_%s(feature, value);
        """
    elsejs = "[]"
    js = ""
    root_rule = renderer.rootRule()
    rules = root_rule.children()
    expFile = os.path.join(folder, "resources",
                           "qgis2web_expressions.js")
    ifelse = "if"
    useAnyMapUnits = False
    for count, rule in enumerate(rules):
        symbol = rule.symbol()
        (styleCode, pattern, setPattern,
         useMapUnits) = getSymbolAsStyle(symbol, stylesFolder,
                                         layer_alpha, renderer, sln, layer)
        name = "".join((sln, "rule", unicode(count)))
        exp = rule.filterExpression()
        if rule.isElse():
            elsejs = styleCode
            continue
        name = compile_to_file(exp, name, "OpenLayers3", expFile)
        js += """
                    %s (%s(context)) {
                      return %s;
                    }
                    """ % (ifelse, name, styleCode)
        js = js.strip()
        ifelse = "else if"
        if useMapUnits:
            useAnyMapUnits = True
    value = ("var value = '';")
    style = template % (sln, js, elsejs, sln)
    return (style, pattern, setPattern, value, useAnyMapUnits)


def getValue(layer, renderer):
    classAttr = handleHiddenField(layer, renderer.classAttribute())
    value = ('var value = feature.get("%s");' % classAttr)
    return value


def getStyle(style, cluster, labelRes, labelText,
             sln, size, face, color, value, geom):
    placement = "point"
    if geom == "LineString":
        placement = "line"
    this_style = '''function(feature, resolution){
    var context = {
        feature: feature,
        variables: {}
    };
    %(value)s
    var labelText = "";
    ''' % {
        "value": value}
    if cluster:
        this_style += '''var clusteredFeatures = feature.get("features");
    var labelFont = "%(size)spx%(face)s sans-serif";
    var labelFill = "%(labelFill)s";
    size = clusteredFeatures.length;
    var textAlign = "center";
    var offsetX = 0;
    var offsetY = 0;
    if (size == 1) {
        textAlign = "left"
        offsetX = 8
        offsetY = 3
        var feature = clusteredFeatures[0];
        if (%(label)s !== null%(labelRes)s) {
            labelText = String(%(label)s);
        }
        key = value + "_" + labelText
    } else {
        labelText = size.toString()
        size = 2*(Math.log(size)/ Math.log(2))
    }
    %(style)s;\n''' % {"style": style, "labelRes": labelRes,
                       "label": labelText, "size": size, "face": face,
                       "labelFill": color}
    else:
        this_style += '''size = 0;
    var labelFont = "%(size)spx%(face)s sans-serif";
    var labelFill = "%(labelFill)s";
    var textAlign = "left";
    var offsetX = 8;
    var offsetY = 3;
    var placement = '%(placement)s';
    if (%(label)s !== null%(labelRes)s) {
        labelText = String(%(label)s);
    }
    %(style)s;\n''' % {"style": style, "placement": placement,
                       "labelRes": labelRes, "label": labelText, "size": size,
                       "face": face, "labelFill": color}

    this_style += '''
    return style;
}''' % {"cache": "styleCache_" + sln, "size": size, "face": face,
        "color": color}
    return this_style


def getSymbolAsStyle(symbol, stylesFolder, layer_transparency, renderer, sln,
                     layer):
    styles = {}
    useMapUnits = False
    if layer_transparency == 0:
        alpha = symbol.alpha()
    else:
        alpha = 1 - (layer_transparency / float(100))
    for i in xrange(symbol.symbolLayerCount()):
        sl = symbol.symbolLayer(i)
        props = sl.properties()
        pattern = ""
        setPattern = ""
        if isinstance(sl, QgsSimpleMarkerSymbolLayerV2):
            color = getRGBAColor(props["color"], alpha)
            borderColor = getRGBAColor(props["outline_color"], alpha)
            borderWidth = props["outline_width"]
            sizeUnits = props["size_unit"]
            if sizeUnits != "MapUnit":
                size = sl.size() * 2
            try:
                shape = sl.shape()
            except:
                shape = sl.name()
            try:
                if shape == 0 or shape == "square":
                    style, useMapUnits = getSquare(color, borderColor,
                                                   borderWidth, size, props)
                    style = "image: %s" % style
                elif shape == 1 or shape == "diamond":
                    style, useMapUnits = getDiamond(color, borderColor,
                                                    borderWidth, size, props)
                    style = "image: %s" % style
                elif shape == 2 or shape == "pentagon":
                    style, useMapUnits = getPentagon(color, borderColor,
                                                     borderWidth, size, props)
                    style = "image: %s" % style
                elif shape == 3 or shape == "hexagon":
                    style, useMapUnits = getHexagon(color, borderColor,
                                                    borderWidth, size, props)
                    style = "image: %s" % style
                elif shape == 4 or shape == 5 or shape == "triangle":
                    style, useMapUnits = getTriangle(color, borderColor,
                                                     borderWidth, size, props)
                    style = "image: %s" % style
                elif shape == 6 or shape == "star":
                    style, useMapUnits = getStar(color, borderColor,
                                                 borderWidth, size, props)
                    style = "image: %s" % style
                elif shape == 9 or shape == "cross":
                    style, useMapUnits = getCross(color, borderColor,
                                                  borderWidth, size, props)
                    style = "image: %s" % style
                elif shape == 11 or shape == "cross2":
                    style, useMapUnits = getCross2(color, borderColor,
                                                   borderWidth, size, props)
                    style = "image: %s" % style
                elif shape == 12 or shape == "line":
                    style, useMapUnits = getLine(color, borderColor,
                                                 borderWidth, size, props)
                    style = "text: %s" % style
                else:
                    style, useMapUnits = getCircle(color, borderColor,
                                                   borderWidth, size, props)
                    style = "image: %s" % style
            except:
                style, useMapUnits = getCircle(color, borderColor, borderWidth,
                                               size, props)
                style = "image: %s" % style
        elif isinstance(sl, QgsSvgMarkerSymbolLayerV2):
            path = os.path.join(stylesFolder, os.path.basename(sl.path()))
            svg = xml.etree.ElementTree.parse(sl.path()).getroot()
            svgWidth = svg.attrib["width"]
            svgWidth = re.sub("px", "", svgWidth)
            svgWidth = re.sub("mm", "", svgWidth)
            svgHeight = svg.attrib["height"]
            svgHeight = re.sub("px", "", svgHeight)
            svgHeight = re.sub("mm", "", svgHeight)
            if symbol.dataDefinedAngle().isActive():
                if symbol.dataDefinedAngle().useExpression():
                    rot = "0"
                else:
                    rot = "feature.get("
                    rot += symbol.dataDefinedAngle().expressionOrField()
                    rot += ") * 0.0174533"
            else:
                rot = unicode(sl.angle() * 0.0174533)
            shutil.copy(sl.path(), path)
            style = ("image: %s" %
                     getIcon("styles/" + os.path.basename(sl.path()),
                             sl.size(), svgWidth, svgHeight, rot))
        elif isinstance(sl, QgsFontMarkerSymbolLayerV2):
            char = sl.character()
            color = getRGBAColor(props["color"], alpha)
            style = """text: new ol.style.Text({
            text: '%s',
            %s})""" % (char, getFillStyle(color, props))
        elif isinstance(sl, QgsSimpleLineSymbolLayerV2):

            color = getRGBAColor(props["line_color"], alpha)
            line_width = props["line_width"]
            line_style = props["line_style"]
            line_units = props["line_width_unit"]
            lineCap = sl.penCapStyle()
            lineJoin = sl.penJoinStyle()

            style, useMapUnits = getStrokeStyle(color, line_style, line_width,
                                                line_units, lineCap, lineJoin)
        elif isinstance(sl, QgsSimpleFillSymbolLayerV2):
            fillColor = getRGBAColor(props["color"], alpha)

            borderColor = getRGBAColor(props["outline_color"], alpha)
            borderStyle = props["outline_style"]
            borderWidth = props["outline_width"]
            line_units = props["outline_width_unit"]

            try:
                lineCap = sl.penCapStyle()
                lineJoin = sl.penJoinStyle()
            except:
                lineCap = 0
                lineJoin = 0

            style = ""
            (stroke, useMapUnits) = getStrokeStyle(borderColor, borderStyle,
                                                   borderWidth, line_units,
                                                   lineCap, lineJoin)
            if stroke != "":
                style = "%s, " % stroke
            style += getFillStyle(fillColor, props)
        elif isinstance(sl, QgsLinePatternFillSymbolLayer):
            weight = sl.subSymbol().width()
            spaceWeight = sl.distance()
            color = sl.color().name()
            angle = 360 - sl.lineAngle()

            pattern = """
    var fill_%s = new ol.style.Fill();""" % sln
            style = """
        fill: fill_%s""" % sln
            setPattern = """
    fill_%s.setColor(stripe(%s, %s, %s, '%s'));""" % (sln, weight, spaceWeight,
                                                      angle, color)
        else:
            style = ""
        if renderer.usingSymbolLevels():
            k = sl.renderingPass()
        else:
            k = i
        if style != "":
            style += ","
        ts = ""
        vts = layer.customProperty("VectorTilesReader/vector_tile_source")
        if vts is None:
            ts = """
        text: createTextStyle(feature, resolution, labelText, labelFont,
                              labelFill, placement)"""
        styles[k] = '''new ol.style.Style({
        %s%s
    })''' % (style, ts)
    return ("[ %s]" % ",".join(styles[s] for s in sorted(styles.iterkeys())),
            pattern, setPattern, useMapUnits)


def getSquare(color, borderColor, borderWidth, size, props):
    if props['outline_style'] == "no":
        stroke = ""
    else:
        stroke, useMapUnits = getStrokeStyle(borderColor, "", borderWidth,
                                             line_units, 0, 0)
        stroke += ","
    return ("""new ol.style.RegularShape({radius: %s + size, points: 4,
            angle: Math.PI/4, %s %s})""" % (size, stroke,
                                            getFillStyle(color, props)),
            useMapUnits)


def getDiamond(color, borderColor, borderWidth, size, props):
    if props['outline_style'] == "no":
        stroke = ""
    else:
        stroke, useMapUnits = getStrokeStyle(borderColor, "", borderWidth,
                                             line_units, 0, 0)
        stroke += ","
    return ("""new ol.style.RegularShape({radius: %s + size, points: 4,
            %s %s})""" % (size, stroke, getFillStyle(color, props)),
            useMapUnits)


def getPentagon(color, borderColor, borderWidth, size, props):
    if props['outline_style'] == "no":
        stroke = ""
    else:
        stroke, useMapUnits = getStrokeStyle(borderColor, "", borderWidth,
                                             line_units, 0, 0)
        stroke += ","
    return ("""new ol.style.RegularShape({radius: %s + size, points: 5,
            %s %s})""" % (size, stroke, getFillStyle(color, props)),
            useMapUnits)


def getHexagon(color, borderColor, borderWidth, size, props):
    if props['outline_style'] == "no":
        stroke = ""
    else:
        stroke, useMapUnits = getStrokeStyle(borderColor, "", borderWidth,
                                             line_units, 0, 0)
        stroke += ","
    return ("""new ol.style.RegularShape({radius: %s + size, points: 6,
            %s %s})""" % (size, stroke, getFillStyle(color, props)),
            useMapUnits)


def getTriangle(color, borderColor, borderWidth, size, props):
    if props['outline_style'] == "no":
        stroke = ""
    else:
        stroke, useMapUnits = getStrokeStyle(borderColor, "", borderWidth,
                                             line_units, 0, 0)
        stroke += ","
    return ("""new ol.style.RegularShape({radius: %s + size, points: 3,
            %s %s})""" % (size, stroke, getFillStyle(color, props)),
            useMapUnits)


def getStar(color, borderColor, borderWidth, size, props):
    if props['outline_style'] == "no":
        stroke = ""
    else:
        stroke, useMapUnits = getStrokeStyle(borderColor, "", borderWidth,
                                             line_units, 0, 0)
        stroke += ","
    return ("""new ol.style.RegularShape({radius: %s + size, points: 5,
            radius2: %s, %s %s})""" % (size, size / 2, stroke,
                                       getFillStyle(color, props)),
            useMapUnits)


def getCircle(color, borderColor, borderWidth, size, props):
    if props['outline_style'] == "no":
        stroke = ""
    else:
        line_units = props["outline_width_unit"]
        stroke, useMapUnits = getStrokeStyle(borderColor, "", borderWidth,
                                             line_units, 0, 0)
        stroke += ","
    return ("""new ol.style.Circle({radius: %s + size,
            %s %s})""" % (size, stroke, getFillStyle(color, props)),
            useMapUnits)


def getCross(color, borderColor, borderWidth, size, props):
    if props['outline_style'] == "no":
        stroke = ""
    else:
        stroke, useMapUnits = getStrokeStyle(borderColor, "", borderWidth,
                                             line_units, 0, 0)
        stroke += ","
    return ("""new ol.style.RegularShape({radius: %s + size, points: 4,
            radius2: 0, %s %s})""" % (size, stroke,
                                      getFillStyle(color, props)), useMapUnits)


def getCross2(color, borderColor, borderWidth, size, props):
    if props['outline_style'] == "no":
        stroke = ""
    else:
        stroke, useMapUnits = getStrokeStyle(borderColor, "", borderWidth,
                                             line_units, 0, 0)
        stroke += ","
    return ("""new ol.style.RegularShape({radius: %s + size,
                                          points: 4,
                                          radius2: 0,
                                          angle: Math.PI / 4,
                                          %s
                                          %s})""" % (size, stroke,
                                                     getFillStyle(color,
                                                                  props)),
            useMapUnits)


def getLine(color, borderColor, borderWidth, size, props):
    if props['outline_style'] == "no":
        stroke = ""
    else:
        stroke, useMapUnits = getStrokeStyle(borderColor, "", borderWidth,
                                             line_units, 0, 0)
    rot = props["angle"]
    return ("""new ol.style.Text({
        rotation: %s * Math.PI/180,
        text: '\u2502',  %s})""" % (rot, stroke), useMapUnits)


def getIcon(path, size, svgWidth, svgHeight, rot):
    size = math.floor(float(size) * 3.8)
    anchor = size / 2
    scale = unicode(float(size) / float(svgWidth))
    return '''new ol.style.Icon({
                  imgSize: [%(w)s, %(h)s],
                  scale: %(scale)s,
                  anchor: [%(a)d, %(a)d],
                  anchorXUnits: "pixels",
                  anchorYUnits: "pixels",
                  rotation: %(rot)s,
                  src: "%(path)s"
            })''' % {"w": svgWidth, "h": svgHeight,
                     "scale": scale, "rot": rot,
                     "s": size, "a": anchor,
                     "path": path.replace("\\", "\\\\")}


def getStrokeStyle(color, dashed, width, line_units, linecap, linejoin):
    if dashed == "no":
        return ("", False)
    if line_units != "MapUnit":
        width = unicode(int(float(width) * 3.8))
        useMapUnits = False
    else:
        width = "m2px(%s)" % width
        useMapUnits = True
    dash = dashed.replace("dash", "10,5")
    dash = dash.replace("dot", "1,5")
    dash = dash.replace("solid", "")
    dash = dash.replace(" ", ",")
    dash = "[%s]" % dash
    if dash == "[]" or dash == "[no]":
        dash = "null"
    capString = "round"
    if linecap == 0:
        capString = "butt"
    if linecap == 16:
        capString = "square"
    joinString = "round"
    if linejoin == 0:
        joinString = "miter"
    if linejoin == 64:
        joinString = "bevel"
    strokeString = ("stroke: new ol.style.Stroke({color: %s, lineDash: %s, " %
                    (color, dash))
    strokeString += ("lineCap: '%s', lineJoin: '%s', width: %s})" %
                     (capString, joinString, width))
    return (strokeString, useMapUnits)


def getFillStyle(color, props):
    try:
        if props["style"] == "no":
            return ""
    except:
        pass
    return "fill: new ol.style.Fill({color: %s})" % color
