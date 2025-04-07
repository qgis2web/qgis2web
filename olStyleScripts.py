import os
import shutil
import re
import codecs
import math
import xml.etree.ElementTree
import traceback
from qgis.PyQt.QtCore import QDir, QSize
from qgis.core import (QgsSingleSymbolRenderer,
                       QgsCategorizedSymbolRenderer,
                       QgsGraduatedSymbolRenderer,
                       QgsRuleBasedRenderer,
                       QgsSimpleMarkerSymbolLayer,
                       QgsSvgMarkerSymbolLayer,
                       QgsFontMarkerSymbolLayer,
                       QgsSimpleLineSymbolLayer,
                       QgsSimpleFillSymbolLayer,
                       QgsLinePatternFillSymbolLayer,
                       QgsSymbolLayerUtils,
                       QgsMapLayer)
from qgis.PyQt.QtGui import QPixmap, QImage
from qgis2web.exp2js import compile_to_file
from qgis2web.utils import safeName, getRGBAColor, handleHiddenField, TYPE_MAP


def exportStyles(layers, folder, clustered, feedback):
    stylesFolder = os.path.join(folder, "styles")
    QDir().mkpath(stylesFolder)
    legendFolder = os.path.join(stylesFolder, "legend")
    QDir().mkpath(legendFolder)
    vtStyles = {}
    mapUnitLayers = []
    for count, (layer, cluster) in enumerate(zip(layers, clustered)):
        sln = safeName(layer.name()) + "_" + str(count)

        # if raster layer
        if layer.type() == QgsMapLayer.RasterLayer and layer.dataProvider().name() == "gdal":
            legendSymbologyItems = layer.legendSymbologyItems() # simbology items list
            for count, (name, color) in enumerate(legendSymbologyItems):
                pixmap = QPixmap(16, 16)
                pixmap.fill(color)  # fill with the legend color
                icon_name = sln + "_" + str(count) + ".png"
                print(icon_name)
                pixmap.save(os.path.join(legendFolder, icon_name))
        
        # if not vector layer      
        if layer.type() != layer.VectorLayer:
            continue
        pattern = ""
        setPattern = ""
        vts = layer.customProperty("VectorTilesReader/vector_tile_url")
        labelText = getLabels(layer, folder, sln)
        defs = "var size = 0;\nvar placement = 'point';"

        renderer = layer.renderer()
        layer_alpha = layer.opacity()

        try:
            if isinstance(renderer, QgsSingleSymbolRenderer):
                (style, pattern, setPattern, value,
                 useMapUnits) = singleSymbol(renderer, stylesFolder,
                                             layer_alpha, sln, legendFolder,
                                             layer, feedback)
            elif isinstance(renderer, QgsCategorizedSymbolRenderer):
                (style, pattern, setPattern, value, defs,
                 useMapUnits) = categorized(defs, sln, layer, renderer,
                                            legendFolder, stylesFolder,
                                            layer_alpha, feedback)
            elif isinstance(renderer, QgsGraduatedSymbolRenderer):
                (style, pattern, setPattern, value,
                 useMapUnits) = graduated(layer, renderer, legendFolder, sln,
                                          stylesFolder, layer_alpha, feedback)
            elif isinstance(renderer, QgsRuleBasedRenderer):
                (style, pattern, setPattern, value,
                 useMapUnits) = ruleBased(renderer, folder, stylesFolder, legendFolder,
                                          layer_alpha, sln, layer, feedback)
            else:
                value = "''"
                style = """
    var style = [ new ol.style.Style({
        text: createTextStyle(feature, resolution, labelText, labelFont,
                              labelFill, placement, bufferColor, bufferWidth)
    })];"""
                useMapUnits = False

            if useMapUnits:
                if vts is None:
                    mapUnitLayers.append(sln)
                else:
                    mapUnitLayers.append(safeName(vts))
            (labelRes, size, face, color,
             bufferColor, bufferWidth) = getLabelFormat(layer)
            if style != "":
                geom = TYPE_MAP[layer.wkbType()].replace("Multi", "")
                style = getStyle(style, cluster, labelRes, labelText,
                                 sln, size, face, color, bufferColor,
                                 bufferWidth, value, geom)
            else:
                style = "''"
        except Exception:
            style = "''"
            feedback.showFeedback("""Exception in layer {} with renderer {}:
                <span style=\"color: red\">{}</span>""".format(layer.id(),
                                                               renderer.dump(),
                                  traceback.format_exc()))

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
            new_vtStyle = defs
            new_vtStyle += "if (feature.get('layer') == "
            new_vtStyle += """'%s' && feature.getGeometry().getType() == '%s'){
            return %s(feature, resolution);
        }""" % (
                layer.name(), TYPE_MAP[layer.wkbType()].replace("Multi", ""),
                style)
            try:
                old_vtStyles = vtStyles[vts]
                new_vtStyles = """%s
                %s""" % (old_vtStyles, new_vtStyle)
            except Exception:
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


def getLabels(layer, folder, sln):
    labelling = layer.labeling()
    if labelling is not None and layer.labelsEnabled():
        palyr = labelling.settings()
        if palyr and palyr.fieldName and palyr.fieldName != "":
            labelField = palyr.fieldName
            if labelField != "":
                if str(layer.customProperty(
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
                    fieldIndex = layer.fields().indexFromName(
                        labelField)
                    # editFormConfig = layer.editFormConfig()
                    editorWidget = layer.editorWidgetSetup(fieldIndex).type()
                    if (editorWidget == 'Hidden'):
                        labelField = "q2wHide_" + labelField
                    labelText = ('feature.get("%s")' %
                                 labelField.replace('"', '\\"'))
            else:
                labelText = '""'
        else:
            labelText = '""'
    else:
        labelText = '""'
    return labelText


def getLabelFormat(layer):
    size = 10
    # italic = layer.customProperty("labeling/fontItalic")
    # bold = layer.customProperty("labeling/fontWeight")
    bufferColor = ""
    bufferWidth = 0
    try:
        color = layer.labeling().settings().format().color().name()
    except:
        color = "#000000"
    labelling = layer.labeling()
    face = ","
    if labelling is not None:
        palyr = labelling.settings()
        labelFormat = palyr.format()
        labelFont = labelFormat.font()
        face = labelFont.family()
        size = labelFont.pointSize() * 1.3
        if face is not None:
            face = " \\'%s\\'," % face
        sv = palyr.scaleVisibility
        if sv:
            min = float(palyr.minimumScale)
            max = float(palyr.maximumScale)
            if min != 0:
                min = 1 / ((1 / min) * 39.37 * 90.7)
            if max != 0:
                max = 1 / ((1 / max) * 39.37 * 90.7)
            labelRes = " && resolution > %(min)d " % {"min": max}
            labelRes += "&& resolution < %(max)d" % {"max": min}
        else:
            labelRes = ""
        labelBuffer = labelFormat.buffer()
        buffer = labelBuffer.enabled()
        if buffer:
            bufferColor = labelBuffer.color().name()
            bufferWidth = labelBuffer.size()
    else:
        labelRes = ""
    return (labelRes, size, face, color, bufferColor, bufferWidth)


def getLegendIconAndAnchors(symbol, sln, legendFolder):
    left_icon_space = []
    right_icon_space = []
    top_icon_space = []
    bottom_icon_space = []

    for i in range(symbol.symbolLayerCount()):
        symbolLayer = symbol.symbolLayer(i)
        props = symbolLayer.properties()
        
        if isinstance(symbolLayer, (QgsSimpleMarkerSymbolLayer, QgsSvgMarkerSymbolLayer)):
            symbolSize = symbolLayer.size()
            symbolUnit = symbolLayer.sizeUnit()
            if symbolUnit == 0:  # millimeters
                scale_factor = 4.5
            elif symbolUnit == 4:  # points
                scale_factor = 1.45
            elif symbolUnit == 2:  # pixels
                scale_factor = 1.30
            else:  # other
                scale_factor = 4.5

            if isinstance(symbolLayer, QgsSimpleMarkerSymbolLayer):
                width = symbolSize * scale_factor
                height = symbolSize * scale_factor
            elif isinstance(symbolLayer, QgsSvgMarkerSymbolLayer):
                aspect_ratio = symbolLayer.defaultAspectRatio()
                if aspect_ratio > 0:
                    width = symbolSize * scale_factor
                    height = width * aspect_ratio
                else:
                    height = symbolSize * scale_factor
                    width = height * aspect_ratio
        else:
            width = 16
            height = 16
        
        ax = int(props["horizontal_anchor_point"]) if "horizontal_anchor_point" in props else 0
        ay = int(props["vertical_anchor_point"]) if "vertical_anchor_point" in props else 0
        left = 0 if ax == 0 else width/2 if ax == 1 else width
        right = width if ax == 0 else width/2 if ax == 1 else 0
        top = 0 if ay == 0 else height/2 if ay == 1 else height
        bottom = height if ay == 0 else height/2 if ay == 1 else 0
        left_icon_space.append(left)
        right_icon_space.append(right)
        top_icon_space.append(top)
        bottom_icon_space.append(bottom)

    max_left_icon = max(left_icon_space)
    max_right_icon = max(right_icon_space)
    max_top_icon = max(top_icon_space)
    max_bottom_icon = max(bottom_icon_space)

    if isinstance(symbolLayer, (QgsSimpleMarkerSymbolLayer, QgsSvgMarkerSymbolLayer)):
        icon_width = int(max(max_left_icon, max_right_icon)*2)
        icon_height = int(max(max_top_icon, max_bottom_icon)*2)
    else:
        icon_width = 16
        icon_height = 16

    symbol_size = QSize(icon_width, icon_height)

    legendIcon = QgsSymbolLayerUtils.symbolPreviewPixmap(symbol, symbol_size)
    icon_name = sln + ".png"
    icon_path = os.path.join(legendFolder, icon_name)
    legendIcon.save(icon_path)

    if isinstance(symbolLayer, (QgsSimpleMarkerSymbolLayer, QgsSvgMarkerSymbolLayer)):
        if legendIcon:
            left_trim = int(icon_width / 2 - max_left_icon)
            right_trim = int(icon_width / 2 - max_right_icon)
            top_trim = int(icon_height / 2 - max_top_icon)
            bottom_trim = int(icon_height / 2 - max_bottom_icon)

            image = QImage(icon_path)

            cropped_width = image.width() - left_trim - right_trim
            cropped_height = image.height() - top_trim - bottom_trim

            cropped_image = image.copy(left_trim, top_trim, cropped_width, cropped_height)
            cropped_image.save(icon_path)


def singleSymbol(renderer, stylesFolder, layer_alpha, sln, legendFolder,
                 layer, feedback):
    symbol = renderer.symbol()
    (style, pattern, setPattern,
     useMapUnits) = getSymbolAsStyle(symbol, stylesFolder,
                                     layer_alpha, renderer, sln, layer,
                                     feedback)
    style = "var style = " + style

    getLegendIconAndAnchors(symbol, sln, legendFolder)
    
    value = ''
    return (style, pattern, setPattern, value, useMapUnits)


def categorized(defs, sln, layer, renderer, legendFolder, stylesFolder,
                layer_alpha, feedback):
    defs += """
function categories_%s(feature, value, size, resolution, labelText,
                       labelFont, labelFill, bufferColor, bufferWidth,
                       placement) {
                var valueStr = (value !== null && value !== undefined) ? value.toString() : 'default';
                switch(valueStr) {""" % sln
    cats = []
    useAnyMapUnits = False
    for cnt, cat in enumerate(renderer.categories()):
        symbol = cat.symbol()
        
        getLegendIconAndAnchors(symbol, sln + "_" + str(cnt), legendFolder)
        
        if cat.value() is not None and cat.value() != "":
            value = cat.value()
            if isinstance(value, float) and value.is_integer():
                # Format decimal numbers without trailing zeroes
                value_str = str(int(value))
            else:
                value_str = str(value)
            categoryStr = "case '%s':" % value_str.replace("'", "\\'")
        else:
            categoryStr = "default:"
        (style, pattern, setPattern,
         useMapUnits) = (getSymbolAsStyle(symbol, stylesFolder,
                                          layer_alpha, renderer, sln, layer,
                                          feedback))
        if useMapUnits:
            useAnyMapUnits = True
        categoryStr += '''
                    return %s;
                    break;''' % style
        cats.append(categoryStr)
    defs += "\n".join(cats) + "}};"
    style = """
    var style = categories_%s(feature, value, size, resolution, labelText,
                            labelFont, labelFill, bufferColor,
                            bufferWidth, placement)""" % sln
    value = getValue(layer, renderer)
    return (style, pattern, setPattern, value, defs, useAnyMapUnits)


def graduated(layer, renderer, legendFolder, sln, stylesFolder, layer_alpha,
              feedback):
    # cluster = False
    ranges = []
    elseif = ""
    useAnyMapUnits = False
    for cnt, ran in enumerate(renderer.ranges()):
        symbol = ran.symbol()
        
        getLegendIconAndAnchors(symbol, sln + "_" + str(cnt), legendFolder)

        (symbolstyle, pattern, setPattern,
         useMapUnits) = getSymbolAsStyle(symbol, stylesFolder,
                                         layer_alpha, renderer, sln, layer,
                                         feedback)
        ranges.append("""%sif (value >= %f && value <= %f) {
            style = %s
                    }""" % (elseif, ran.lowerValue(), ran.upperValue(),
                            symbolstyle))
        elseif = " else "
        if useMapUnits:
            useAnyMapUnits = True
    style = "".join(ranges)
    value = getValue(layer, renderer)
    return (style, pattern, setPattern, value, useAnyMapUnits)


def ruleBased(renderer, folder, stylesFolder, legendFolder, layer_alpha, sln, layer,
              feedback):
    # cluster = False
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
    expFile = os.path.join(folder, "resources", "qgis2web_expressions.js")
    ifelse = "if"
    useAnyMapUnits = False
    for cnt, rule in enumerate(rules):
        symbol = rule.symbol()

        getLegendIconAndAnchors(symbol, sln + "_" + str(cnt), legendFolder)

        (styleCode, pattern, setPattern,
         useMapUnits) = getSymbolAsStyle(symbol, stylesFolder, layer_alpha,
                                         renderer, sln, layer, feedback)
        name = "".join((sln, "rule", str(cnt)))
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
    value = handleHiddenField(layer, renderer.classAttribute())
    #value = ('var value = feature.get("%s");' % classAttr)
    return value


def getStyle(style, cluster, labelRes, labelText, sln, size,
             face, color, bufferColor, bufferWidth, value, geom):
    placement = "point"
    if geom == "LineString":
        placement = "line"
    this_style = '''function(feature, resolution){
    var context = {
        feature: feature,
        variables: {}
    };
    
    var labelText = ""; '''
    if cluster:
        this_style += '''
    var labelFont = "%(size)spx%(face)s sans-serif";
    var labelFill = "%(labelFill)s";
    var bufferColor = "%(bufferColor)s";
    var bufferWidth = %(bufferWidth)s;
    var textAlign = "center";
    var offsetX = 15;
    var offsetY = 10;
    var feature
	var value
    var clusteredFeatures = feature.get("features");
    size = clusteredFeatures.length;
    if (size == 1) { // If cluster has one feature
        var feature = clusteredFeatures[0];
        value = clusteredFeatures[0].get("%(value)s");
        if (%(label)s !== null%(labelRes)s) {
            labelText = String(%(label)s);
        }
    } else { // If cluster has more than one feature
		labelText = size.toString();
		var radius = 6 + Math.log(size) * 3;
		var maxClusterSize = 80;
		var relativeSize = Math.min(size / maxClusterSize, 1);
		var redComponent, greenComponent, blueComponent = 0;
		if (relativeSize < 0.5) {
			redComponent = Math.floor(210 * (relativeSize / 0.5));
			greenComponent = 210;
		} else {
			redComponent = 210;
			greenComponent = Math.floor(210 * (1 - (relativeSize - 0.5) / 0.5));
		}
		var color = `rgba(${redComponent}, ${greenComponent}, ${blueComponent}, 0.75)`;
		return [
			new ol.style.Style({
				image: new ol.style.Circle({
					radius: radius + 4,
					fill: new ol.style.Fill({
						color: `rgba(${redComponent}, ${greenComponent}, ${blueComponent}, 0.3)`
					})
				})
			}),
			new ol.style.Style({
				image: new ol.style.Circle({
					radius: radius,
					fill: new ol.style.Fill({
						color: color
					})
				}),
				text: new ol.style.Text({
					font: labelFont,
					text: labelText,
					fill: new ol.style.Fill({
						color: labelFill
					}),
					placement: placement
				})
			})
		];
	}
    %(style)s;\n''' % {"style": style, "labelRes": labelRes, "label": labelText, "size": size, "face": face,
            "labelFill": color, "bufferColor": bufferColor,
            "bufferWidth": bufferWidth * 3, "value": value.replace('"', '\\"')}
    else:
        this_style += '''
    var value = feature.get("%(value)s");
    var labelFont = "%(size)spx%(face)s sans-serif";
    var labelFill = "%(labelFill)s";
    var bufferColor = "%(bufferColor)s";
    var bufferWidth = %(bufferWidth)s;
    var textAlign = "left";
    var offsetX = 0;
    var offsetY = 0;
    var placement = '%(placement)s';
    if (%(label)s !== null%(labelRes)s) {
        labelText = String(%(label)s);
    }
    %(style)s;\n''' % {"style": style, "placement": placement,
                    "labelRes": labelRes, "label": labelText, "size": size,
                    "face": face, "labelFill": color, "value": value.replace('"', '\\"'),
                    "bufferColor": bufferColor, "bufferWidth": bufferWidth * 3}

    this_style += '''
    return style;
}''' % {"cache": "styleCache_" + sln, "size": size, "face": face,
        "color": color}
    return this_style


def getSymbolAsStyle(symbol, stylesFolder, layer_transparency, renderer, sln,
                     layer, feedback):
    styles = {}
    useMapUnits = False
    if layer_transparency == 0:
        alpha = symbol.alpha()
    else:
        alpha = layer_transparency
    for i in range(symbol.symbolLayerCount()):
        sl = symbol.symbolLayer(i)
        props = sl.properties()
        pattern = ""
        setPattern = "" 
        ax = int(props["horizontal_anchor_point"]) if "horizontal_anchor_point" in props else 0
        ay = int(props["vertical_anchor_point"]) if "vertical_anchor_point" in props else 0
        if isinstance(sl, QgsSimpleMarkerSymbolLayer):
            color = getRGBAColor(props["color"], alpha)
            borderColor = getRGBAColor(props["outline_color"], alpha)
            borderWidth = props["outline_width"]
            sizeUnits = props["size_unit"]
            symbolSize = None
            if sizeUnits == "MM":
                symbolSize = sl.size() * 2
            elif sizeUnits == "Point":
                symbolSize = sl.size() * 0.55
            elif sizeUnits == "Pixel":
                symbolSize = sl.size() * 0.40
            else:
                symbolSize = sl.size()
            anchorX = 0 if ax == 1 else symbolSize if ax == 0 else -symbolSize
            anchorY = 0 if ay == 1 else -symbolSize if ay == 0 else symbolSize
            try:
                shape = sl.shape()
            except Exception:
                shape = sl.name()
            try:
                if shape == 0 or shape == "square":
                    style, useMapUnits = getSquare(color, borderColor,
                                                   borderWidth, symbolSize,
                                                   props, anchorX, anchorY)
                    style = "image: %s" % style
                elif shape == 1 or shape == "diamond":
                    style, useMapUnits = getDiamond(color, borderColor,
                                                    borderWidth, symbolSize,
                                                    props, anchorX, anchorY)
                    style = "image: %s" % style
                elif shape == 2 or shape == "pentagon":
                    style, useMapUnits = getPentagon(color, borderColor,
                                                     borderWidth, symbolSize,
                                                     props, anchorX, anchorY)
                    style = "image: %s" % style
                elif shape == 3 or shape == "hexagon":
                    style, useMapUnits = getHexagon(color, borderColor,
                                                    borderWidth, symbolSize,
                                                    props, anchorX, anchorY)
                    style = "image: %s" % style
                elif shape == 4 or shape == 5 or shape == "triangle":
                    style, useMapUnits = getTriangle(color, borderColor,
                                                     borderWidth, symbolSize,
                                                     props, anchorX, anchorY)
                    style = "image: %s" % style
                elif shape == 6 or shape == "star":
                    style, useMapUnits = getStar(color, borderColor,
                                                 borderWidth, symbolSize, 
                                                 props, anchorX, anchorY)
                    style = "image: %s" % style
                elif shape == 9 or shape == "cross":
                    style, useMapUnits = getCross(color, borderColor,
                                                  borderWidth, symbolSize, 
                                                  props, anchorX, anchorY)
                    style = "image: %s" % style
                elif shape == 11 or shape == "cross2":
                    style, useMapUnits = getCross2(color, borderColor,
                                                   borderWidth, symbolSize, 
                                                   props, anchorX, anchorY)
                    style = "image: %s" % style
                elif shape == 12 or shape == "line":
                    style, useMapUnits = getLine(color, borderColor,
                                                 borderWidth, symbolSize, 
                                                 props, anchorX, anchorY)
                    style = "text: %s" % style
                else:
                    style, useMapUnits = getCircle(color, borderColor,
                                                   borderWidth, symbolSize, 
                                                   props, anchorX, anchorY)
                    style = "image: %s" % style
            except Exception:
                style, useMapUnits = getCircle(color, borderColor, borderWidth,
                                               symbolSize, props, anchorX, anchorY)
                style = "image: %s" % style
        elif isinstance(sl, QgsSvgMarkerSymbolLayer):
            svg_path = sl.path()
            base_filename = os.path.basename(svg_path)
            filename, file_extension = os.path.splitext(base_filename)
            # Check if the file already exists, if yes, append a progressive number
            count = 0
            while os.path.exists(os.path.join(stylesFolder, base_filename)):
                count += 1
                base_filename = f"{filename}_{count}{file_extension}"
            path = os.path.join(stylesFolder, base_filename)
            svg = xml.etree.ElementTree.parse(svg_path).getroot()
            try:
                svgWidth = svg.attrib["width"]
                svgWidth = re.sub("px", "", svgWidth)
                svgWidth = re.sub("mm", "", svgWidth)
            except Exception:
                svgWidth = "5"

            try:
                svgHeight = svg.attrib["height"]
                svgHeight = re.sub("px", "", svgHeight)
                svgHeight = re.sub("mm", "", svgHeight)
            except Exception:
                svgHeight = "5"

            if symbol.dataDefinedAngle().isActive():
                if symbol.dataDefinedAngle().useExpression():
                    rot = "0"
                else:
                    rot = "feature.get("
                    rot += symbol.dataDefinedAngle().expressionOrField()
                    rot += ") * 0.0174533"
            else:
                rot = str(sl.angle() * 0.0174533)
                
            # save a colorized svg in the markers folder
            # replacing "param(...)" with actual values from QGIS
            pColor = getRGBAColor(props["color"], alpha).strip("'")
            pOutline = getRGBAColor(props["outline_color"], alpha).strip("'")
            with open(svg_path) as f:
                s = f.read()
                s = s.replace('param(fill)', pColor)
                s = s.replace('param(fill-opacity)', '1')
                s = s.replace('param(outline)', pOutline)
                s = s.replace('param(outline-width)', str(float(props["outline_width"]) * 80))
                s = s.replace('param(outline-opacity)', '1')
            with open(path, 'w') as f:
                f.write(s)
        
            style = ("image: %s" %
                     getIcon("styles/" + base_filename,
                             sl.size(), svgWidth, svgHeight,
                             rot, ax, ay))
        elif isinstance(sl, QgsFontMarkerSymbolLayer):
            char = sl.character()
            color = getRGBAColor(props["color"], alpha)
            style = """text: new ol.style.Text({
            text: '%s',
            %s})""" % (char, getFillStyle(color, props))
        elif isinstance(sl, QgsSimpleLineSymbolLayer):
            color = getRGBAColor(props["line_color"], alpha)
            line_width = props["line_width"]
            line_style = props["line_style"]
            line_units = props["line_width_unit"]
            lineCap = sl.penCapStyle()
            lineJoin = sl.penJoinStyle()

            style, useMapUnits = getStrokeStyle(color, line_style, line_width,
                                                line_units, lineCap, lineJoin, props)
        elif isinstance(sl, QgsSimpleFillSymbolLayer):
            fillColor = getRGBAColor(props["color"], alpha)

            borderColor = getRGBAColor(props["outline_color"], alpha)
            borderStyle = props["outline_style"]
            borderWidth = props["outline_width"]
            line_units = props["outline_width_unit"]

            try:
                lineCap = sl.penCapStyle()
                lineJoin = sl.penJoinStyle()
            except Exception:
                lineCap = 0
                lineJoin = 0

            symbolStyles = []
            style = ""
            (stroke, useMapUnits) = getStrokeStyle(borderColor, borderStyle,
                                                   borderWidth, line_units,
                                                   lineCap, lineJoin, props)
            if stroke != "":
                symbolStyles.append(stroke)
            fill = getFillStyle(fillColor, props)
            if fill != "":
                symbolStyles.append(fill)
            style = ",".join(symbolStyles)
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
            color = getRGBAColor(props["color"], alpha)
            sizeUnits = props["size_unit"]
            props['outline_style'] = "no"
            size = None
            if sizeUnits != "MapUnit":
                size = sl.size() * 2
            style, useMapUnits = getCircle(color, None, None, size, props)

            style = "image: %s" % style

            feedback.showFeedback(
                """Layer {}: replacing symbol layer
                <span style=\"color: red\">{}</span> with
                circle.""".format(layer.id(), sl.layerType()))
            style = ""

        if renderer.usingSymbolLevels():
            k = sl.renderingPass()
        else:
            k = i
        if style != "":
            style += ","
        ts = ""
        vts = layer.customProperty("VectorTilesReader/vector_tile_url")
        if vts is None:
            ts = """
        text: createTextStyle(feature, resolution, labelText, labelFont,
                              labelFill, placement, bufferColor,
                              bufferWidth)"""
        styles[k] = '''new ol.style.Style({
        %s%s
    })''' % (style, ts)
    return ("[ %s]" % ",".join(styles[s] for s in sorted(styles.keys())),
            pattern, setPattern, useMapUnits)


def getSquare(color, borderColor, borderWidth, symbolSize, props, anchorX, anchorY):
    if props['outline_style'] == "no":
        stroke = ""
    else:
        line_units = props["outline_width_unit"]
        stroke, useMapUnits = getStrokeStyle(borderColor, "", borderWidth,
                                             line_units, 0, 0, props)
        stroke += ","

    return ("""new ol.style.RegularShape({radius: %s + size, points: 4,
            angle: Math.PI/4, displacement: [%s, %s], %s %s})""" % (symbolSize, anchorX, anchorY, stroke,
                                            getFillStyle(color, props)),
            useMapUnits)


def getDiamond(color, borderColor, borderWidth, symbolSize, props, anchorX, anchorY):
    if props['outline_style'] == "no":
        stroke = ""
    else:
        line_units = props["outline_width_unit"]
        stroke, useMapUnits = getStrokeStyle(borderColor, "", borderWidth,
                                             line_units, 0, 0, props)
        stroke += ","
    
    return ("""new ol.style.RegularShape({radius: %s + size, points: 4,
            displacement: [%s, %s], %s %s})""" % (symbolSize, anchorX, anchorY, stroke, getFillStyle(color, props)),
            useMapUnits)


def getPentagon(color, borderColor, borderWidth, symbolSize, props, anchorX, anchorY):
    if props['outline_style'] == "no":
        stroke = ""
    else:
        line_units = props["outline_width_unit"]
        stroke, useMapUnits = getStrokeStyle(borderColor, "", borderWidth,
                                             line_units, 0, 0, props)
        stroke += ","
    
    return ("""new ol.style.RegularShape({radius: %s + size, points: 5,
            displacement: [%s, %s], %s %s})""" % (symbolSize, anchorX, anchorY, stroke, getFillStyle(color, props)),
            useMapUnits)


def getHexagon(color, borderColor, borderWidth, symbolSize, props, anchorX, anchorY):
    if props['outline_style'] == "no":
        stroke = ""
    else:
        line_units = props["outline_width_unit"]
        stroke, useMapUnits = getStrokeStyle(borderColor, "", borderWidth,
                                             line_units, 0, 0, props)
        stroke += ","

    return ("""new ol.style.RegularShape({radius: %s + size, points: 6,
            displacement: [%s, %s], %s %s})""" % (symbolSize, anchorX, anchorY, stroke, getFillStyle(color, props)),
            useMapUnits)


def getTriangle(color, borderColor, borderWidth, symbolSize, props, anchorX, anchorY):
    if props['outline_style'] == "no":
        stroke = ""
    else:
        line_units = props["outline_width_unit"]
        stroke, useMapUnits = getStrokeStyle(borderColor, "", borderWidth,
                                             line_units, 0, 0, props)
        stroke += ","

    return ("""new ol.style.RegularShape({radius: %s + size, points: 3,
            displacement: [%s, %s], %s %s})""" % (symbolSize, anchorX, anchorY, stroke, getFillStyle(color, props)),
            useMapUnits)


def getStar(color, borderColor, borderWidth, symbolSize, props, anchorX, anchorY):
    if props['outline_style'] == "no":
        stroke = ""
    else:
        line_units = props["outline_width_unit"]
        stroke, useMapUnits = getStrokeStyle(borderColor, "", borderWidth,
                                             line_units, 0, 0, props)
        stroke += ","
    
    return ("""new ol.style.RegularShape({radius: %s + size, points: 5,
            radius2: %s, displacement: [%s, %s], %s %s})""" % (symbolSize, symbolSize / 2, anchorX, anchorY, stroke,
                                       getFillStyle(color, props)),
            useMapUnits)


def getCircle(color, borderColor, borderWidth, symbolSize, props, anchorX, anchorY):
    if props['outline_style'] == "no":
        stroke = ""
        useMapUnits = None
    else:
        line_units = props["outline_width_unit"]
        stroke, useMapUnits = getStrokeStyle(borderColor, "", borderWidth,
                                             line_units, 0, 0, props)
        stroke += ","
    
    return ("""new ol.style.Circle({radius: %s + size,
            displacement: [%s, %s], %s %s})""" % (symbolSize, anchorX, anchorY, stroke, getFillStyle(color, props)),
            useMapUnits)


def getCross(color, borderColor, borderWidth, symbolSize, props, anchorX, anchorY):
    if props['outline_style'] == "no":
        stroke = ""
        useMapUnits = None
    else:
        line_units = props["outline_width_unit"]
        stroke, useMapUnits = getStrokeStyle(borderColor, "", borderWidth,
                                             line_units, 0, 0, props)
        stroke += ","
    
    return ("""new ol.style.RegularShape({radius: %s + size, points: 4,
            radius2: 0, displacement: [%s, %s], %s %s})""" % (symbolSize, anchorX, anchorY, stroke,
                                      getFillStyle(color, props)), useMapUnits)


def getCross2(color, borderColor, borderWidth, symbolSize, props, anchorX, anchorY):
    if props['outline_style'] == "no":
        stroke = ""
        useMapUnits = None
    else:
        line_units = props["outline_width_unit"]
        stroke, useMapUnits = getStrokeStyle(borderColor, "", borderWidth,
                                             line_units, 0, 0, props)
        stroke += ","
 
    return ("""new ol.style.RegularShape({radius: %s + size,
                                          points: 4,
                                          radius2: 0,
                                          angle: Math.PI / 4,
                                          displacement: [%s, %s],
                                          %s
                                          %s})""" % (symbolSize, anchorX, anchorY, stroke,
                                                     getFillStyle(color,
                                                                  props)),
            useMapUnits)


def getLine(color, borderColor, borderWidth, symbolSize, props, anchorX, anchorY):
    if props['outline_style'] == "no":
        stroke = ""
        useMapUnits = None
    else:
        line_units = props["outline_width_unit"]
        stroke, useMapUnits = getStrokeStyle(borderColor, "", borderWidth,
                                             line_units, 0, 0, props)
    rot = props["angle"]
    
    return ("""new ol.style.Text({
        rotation: %s * Math.PI/180,
        displacement: [%s, %s],
        text: '\u2502',  %s})""" % (rot, anchorX, anchorY, stroke), useMapUnits)


def getIcon(path, size, svgWidth, svgHeight, rot, ax, ay):
    size = math.floor(float(size) * 3.8)
    anchorX = float(svgWidth) / 2 if ax == 1 else float(svgWidth) if ax == 2 else 0
    anchorY = float(svgHeight) / 2 if ay == 1 else float(svgHeight) if ay == 2 else 0
    scale = str(float(size) / float(svgWidth))
    return '''new ol.style.Icon({
                  imgSize: [%(w)s, %(h)s],
                  scale: %(scale)s,
                  anchor: [%(anchorX)s, %(anchorY)s],
                  anchorXUnits: "pixels",
                  anchorYUnits: "pixels",
                  rotation: %(rot)s,
                  src: "%(path)s"
            })''' % {"w": svgWidth, "h": svgHeight,
                     "scale": scale, "rot": rot,
                     "s": size, "anchorX": anchorX, "anchorY": anchorY,
                     "path": path.replace("\\", "\\\\")}


def getStrokeStyle(color, dashed, width, line_units, linecap, linejoin, props):
    if dashed == "no":
        return ("", False)
    if line_units != "MapUnit":
        #width = str(int(float(width) * 3.8))
        width = str(float(width) * 3.8)
        useMapUnits = False
    else:
        width = "m2px(%s)" % width
        useMapUnits = True
    outline_style = props.get('outline_style', 'no')
    if outline_style == "no":
        dash_length = 4 * float(width)
        dash_space = 2 * float(width)
        dot_length = 1 * float(width)
        dot_space = 2 * float(width)
    else:
        dash_length = 5 * float(width)
        dash_space = 1 * float(width)
        dot_length = 2 * float(width)
        dot_space = 1 * float(width)

    dash = dashed.replace("dash", f"{dash_length},{dash_space}")
    #dash = dashed.replace("dash", "10,5")
    dash = dash.replace("dot", f"{dot_length},{dot_space}")
    #dash = dash.replace("dot", "1,5")
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
    except Exception:
        pass

    return "fill: new ol.style.Fill({color: %s})" % color
