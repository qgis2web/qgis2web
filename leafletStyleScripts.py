import base64
import os
import shutil
from qgis.core import (QgsSingleSymbolRenderer,
                       QgsCategorizedSymbolRenderer,
                       QgsGraduatedSymbolRenderer,
                       QgsRuleBasedRenderer,
                       QgsNullSymbolRenderer,
                       QgsSimpleMarkerSymbolLayer,
                       QgsSimpleLineSymbolLayer,
                       QgsSimpleFillSymbolLayer,
                       QgsLinePatternFillSymbolLayer,
                       QgsSvgMarkerSymbolLayer)
from qgis2web.exp2js import compile_to_file
from qgis2web.utils import getRGBAColor, handleHiddenField


def getLayerStyle(layer, sln, interactivity, markerFolder,
                  outputProjectFilename, useShapes, feedback):
    markerType = None
    useMapUnits = False
    renderer = layer.renderer()
    layer_alpha = layer.opacity()
    style = ""
    if isinstance(renderer, QgsNullSymbolRenderer):
        style += """
        function style_%s_0() {
            return {
                fill: false,
                stroke: false,
                interactive: false
            }
        }""" % (sln)
        markerType = "circleMarker"
    elif isinstance(renderer, QgsSingleSymbolRenderer):
        symbol = renderer.symbol()
        slCount = symbol.symbolLayerCount()
        if slCount < 1:
            slCount = 1
        for sl in range(slCount):
            (styleCode, markerType, useMapUnits,
             pattern) = getSymbolAsStyle(symbol, markerFolder,
                                         layer_alpha, interactivity, sln, sl,
                                         useMapUnits, feedback)
            style += pattern
            style += """
        function style_%s_%s() {
            return %s
        }""" % (sln, sl, styleCode)
    elif isinstance(renderer, QgsCategorizedSymbolRenderer):
        classAttr = handleHiddenField(layer, renderer.classAttribute())
        symbol = renderer.categories()[0].symbol()
        slCount = symbol.symbolLayerCount()
        patterns = ""
        if slCount < 1:
            slCount = 1
        for sl in range(slCount):
            style += """
        function style_%s_%s(feature) {
            switch(String(feature.properties['%s'])) {""" % (sln, sl,
                                                             classAttr.replace("'", "\\'"))
            for cat in renderer.categories():
                (styleCode, markerType, useMapUnits,
                 pattern) = getSymbolAsStyle(cat.symbol(), markerFolder,
                                             layer_alpha, interactivity, sln,
                                             sl, useMapUnits, feedback)
                patterns += pattern
                if (cat.value() is not None and cat.value() != ""):
                    style += """
                case '%s':""" % str(cat.value()).replace("'", "\\'")
                else:
                    style += """
                default:"""
                style += """
                    return %s
                    break;""" % styleCode
            style = patterns + style + """
            }
        }"""
    elif isinstance(renderer, QgsGraduatedSymbolRenderer):
        classAttr = handleHiddenField(layer, renderer.classAttribute())
        symbol = renderer.ranges()[0].symbol()
        slCount = symbol.symbolLayerCount()
        patterns = ""
        if slCount < 1:
            slCount = 1
        for sl in range(slCount):
            style += """
        function style_%s_%s(feature) {""" % (sln, sl)
            for ran in renderer.ranges():
                (styleCode, markerType, useMapUnits,
                 pattern) = getSymbolAsStyle(ran.symbol(), markerFolder,
                                             layer_alpha, interactivity, sln,
                                             sl, useMapUnits, feedback)
                patterns += pattern
                style += """
            if (feature.properties['%(a)s'] >= %(l)f """
                style += """&& feature.properties['%(a)s'] <= %(u)f ) {
                return %(s)s
            }"""
                style = style % {"a": classAttr.replace("'", "\\'"), "l": ran.lowerValue(),
                                 "u": ran.upperValue(),
                                 "s": styleCode}
            style = patterns + style + """
        }"""
    elif isinstance(renderer, QgsRuleBasedRenderer):
        symbol = renderer.rootRule().children()[0].symbol()
        slCount = symbol.symbolLayerCount()
        patterns = ""
        if slCount < 1:
            slCount = 1
        for sl in range(slCount):
            template = """
        %s
        function style_%s_{sl}(feature) {{
            var context = {{
                feature: feature,
                variables: {{}}
            }};
            // Start of if blocks and style check logic
            %s
            else {{
                return %s;
            }}
        }}
        """.format(sl=sl)
            elsejs = "{fill: false, stroke: false}"
            js = ""
            root_rule = renderer.rootRule()
            rules = root_rule.children()
            expFile = os.path.join(outputProjectFilename, "js",
                                   "qgis2web_expressions.js")
            ifelse = "if"
            for count, rule in enumerate(rules):
                if rule.symbol().symbolLayer(sl) is not None:
                    (styleCode, markerType, useMapUnits,
                     pattern) = getSymbolAsStyle(rule.symbol(), markerFolder,
                                                 layer_alpha, interactivity,
                                                 sln, sl, useMapUnits,
                                                 feedback)
                    patterns += pattern
                    name = "".join((sln, "rule", str(count)))
                    exp = rule.filterExpression()
                    if rule.isElse():
                        elsejs = styleCode
                        continue
                    name = compile_to_file(exp, name, "Leaflet", expFile)
                    js += """
                %s (%s(context)) {
                  return %s;
                }
                """ % (ifelse, name, styleCode)
                    js = js.strip()
                    ifelse = "else if"
            if js == "":
                js = """
                if (false) {}"""
            style += template % (patterns, sln, js, elsejs)
    else:
        useMapUnits = False
        style = """
        function style_%s_0() {
            return {};
        }""" % (sln)
    if markerType == "shapeMarker":
        useShapes = True
    return style, markerType, useMapUnits, useShapes


def getSymbolAsStyle(symbol, markerFolder, layer_transparency, interactivity,
                     sln, sl, useMapUnits, feedback):
    interactive = str(interactivity).lower()
    markerType = None
    pattern = ""
    # styles = []
    if layer_transparency == 0:
        alpha = symbol.alpha()
    else:
        alpha = layer_transparency
    slc = sl
    sl = symbol.symbolLayer(sl)
    try:
        props = sl.properties()
    except Exception:
        props = {}
    if isinstance(sl, QgsSimpleMarkerSymbolLayer):
        color = getRGBAColor(props["color"], alpha)
        borderColor = getRGBAColor(props["outline_color"], alpha)
        borderWidth = props["outline_width"]
        borderUnits = props["outline_width_unit"]
        lineStyle = props["outline_style"]
        sizeUnits = props["size_unit"]
        size = sl.size()
        if sizeUnits != "MapUnit":
            size = size * 2
        shape = 8
        try:
            shape = sl.shape()
        except Exception:
            try:
                shape = sl.name()
            except Exception:
                pass
        style, useMapUnits = getMarker(color, borderColor, borderWidth,
                                       borderUnits, size, sizeUnits, props,
                                       lineStyle, shape, feedback)
        try:
            if shape == 8 or shape == "circle":
                markerType = "circleMarker"
            else:
                markerType = "shapeMarker"
        except Exception:
            markerType = "circleMarker"
    elif isinstance(sl, QgsSvgMarkerSymbolLayer):
        svgSize = sl.size() * 3.8
        if symbol.dataDefinedAngle().isActive():
            if symbol.dataDefinedAngle().useExpression():
                rot = "0"
            else:
                rot = "feature.get("
                rot += symbol.dataDefinedAngle().expressionOrField()
                rot += ") * 0.0174533"
        else:
            rot = str(sl.angle() * 0.0174533)
        style = """
        rotationAngle: %s,
        rotationOrigin: 'center center',
        icon: %s""" % (rot, getIcon("markers/" + sln + ".svg", svgSize))
        markerType = "marker"

        # save a colorized svg in the markers folder
        # replacing "param(...)" with actual values from QGIS
        # and renaming to safe layer name
        pColor = getRGBAColor(props["color"], alpha).strip("'")
        pOutline = getRGBAColor(props["outline_color"], alpha).strip("'")

        # check if svg is embedded in project file or not
        # as per QgsSymbolLayerUtils::svgSymbolNameToPath and
        #        QgsSymbolLayerUtils::svgSymbolPathToName
        if sl.path()[0:7] == "base64:":
            s = base64.standard_b64decode(sl.path()[7:]).decode("utf-8")

        else:
            f = open(sl.path())
            s = f.read()
            f.close()

        s = s.replace("param(fill)", pColor)
        s = s.replace("param(fill-opacity)", "1")
        s = s.replace("param(outline)", pOutline)
        s = s.replace("param(outline-width)", str(float(props["outline_width"]) * 80))
        s = s.replace("param(outline-opacity)", "1")

        with open(os.path.join(markerFolder, sln + ".svg"), "w") as f:
            f.write(s)
    elif isinstance(sl, QgsSimpleLineSymbolLayer):
        color = getRGBAColor(props["line_color"], alpha)
        line_width = props["line_width"]
        line_style = props["line_style"]
        line_units = props["line_width_unit"]

        lineCap = sl.penCapStyle()
        lineJoin = sl.penJoinStyle()

        style, useMapUnits = getStrokeStyle(color, line_style, line_width,
                                            line_units, lineCap, lineJoin,
                                            useMapUnits, feedback, props)
        style += """
                fillOpacity: 0,"""
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

        strokeStyle, useMapUnits = getStrokeStyle(borderColor, borderStyle,
                                                  borderWidth, line_units,
                                                  lineCap, lineJoin,
                                                  useMapUnits, feedback, props)

        style = ('''%s %s''' %
                 (strokeStyle, getFillStyle(fillColor, props)))
    elif isinstance(sl, QgsLinePatternFillSymbolLayer):
        weight = sl.subSymbol().width()
        spaceWeight = sl.distance()
        color = sl.color().name()
        angle = 360 - sl.lineAngle()
        pattern = """
        var pattern_%s_%d = new L.StripePattern({
            weight: %s,
            spaceWeight: %s,
            color: '%s',
            opacity: %s,
            spaceOpacity: 0,
            angle: %d
        });
        pattern_%s_%d.addTo(map);""" % (sln, slc, weight, spaceWeight,
                                        color, alpha, angle, sln, slc)
        style = """
                stroke: false,
                fillOpacity: 1,
                fillPattern: pattern_%s_%d,""" % (sln, slc)
    else:
        feedback.showFeedback("""replacing symbol layer {}
                                 with circle""".format(sl.layerType()))
        markerType = "circleMarker"
        style = ""
        useMapUnits = False
    style += """
                interactive: %s""" % interactive
    return ("""{
                pane: 'pane_%s',%s,
            }""" % (sln, style), markerType, useMapUnits,
            pattern)


def getMarker(color, borderColor, borderWidth, borderUnits, size, sizeUnits,
              props, lineStyle, shape, feedback):
    useMapUnits = False
    strokeStyle, useMapUnits = getStrokeStyle(borderColor, lineStyle,
                                              borderWidth, borderUnits, 0, 0,
                                              useMapUnits, feedback, props)
    if sizeUnits == "MapUnit":
        useMapUnits = True
        size = "geoStyle(%s)" % size
    if shape == 0 or shape == "square":
        markerShape = "shape: 'square',"
    elif shape == 1 or shape == "diamond":
        markerShape = "shape: 'diamond',"
    elif shape == 4 or shape == "triangle":
        markerShape = "shape: 'triangle',"
    elif shape == 11 or shape == "cross2":
        markerShape = "shape: 'x',"
    else:
        markerShape = ""
    return ("""
                %s
                radius: %s,%s%s""" % (markerShape, size, strokeStyle,
                                      getFillStyle(color, props)),
            useMapUnits)


def getIcon(path, svgSize):
    return '''L.icon({
            iconUrl: '%(path)s',
            iconSize: [%(s)s, %(s)s]
        }),''' % {"s": svgSize, "path": path.replace("\\", "\\\\")}


def getStrokeStyle(color, dashed, width, units, linecap, linejoin,
                   useMapUnits, feedback, props):
    if dashed != "no":
        width = round(float(width) * 3.8, 0)
        if width == 0:
            width = 1
        if units == "MapUnit":
            useMapUnits = True
            width = "geoStyle(%s)" % width
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
        #♀dash = dash.replace("dot", "1,5")
        dash = dash.replace("solid", "")
        dash = dash.replace(" ", ",")
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
        strokeString = """
                opacity: 1,
                color: %s,
                dashArray: '%s',""" % (color, dash)
        strokeString += """
                lineCap: '%s',
                lineJoin: '%s',
                weight: %s,""" % (capString, joinString, width)
    else:
        strokeString = """
                stroke: false,"""

    return strokeString, useMapUnits


def getFillStyle(color, props):
    try:
        if props["style"] == "no":
            return """
                fillOpacity: 0,"""
    except Exception:
        pass

    return """
                fill: true,
                fillOpacity: 1,
                fillColor: %s,""" % color
