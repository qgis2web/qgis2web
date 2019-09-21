import os
from xml.etree.ElementTree import Element, SubElement
from xml.etree import ElementTree
from xml.dom import minidom
from .transformations import processTransformation

import zipfile

_warnings = []

def convert(geostyler):
    global _warnings
    _warnings = []
    attribs = {
        "version": "1.0.0",
        "xsi:schemaLocation": "http://www.opengis.net/sld StyledLayerDescriptor.xsd",
        "xmlns": "http://www.opengis.net/sld",
        "xmlns:ogc": "http://www.opengis.net/ogc",
        "xmlns:xlink": "http://www.w3.org/1999/xlink",
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance"
        }
    root = Element("StyledLayerDescriptor", attrib=attribs) 
    namedLayer = SubElement(root, "NamedLayer")
    layerName = SubElement(namedLayer, "Name")
    layerName.text = geostyler["name"]
    userStyle = SubElement(namedLayer, "UserStyle")
    userStyleTitle = SubElement(userStyle, "Title")
    userStyleTitle.text = geostyler["name"]

    featureTypeStyle = SubElement(userStyle, "FeatureTypeStyle")
    if "transformation" in geostyler:
        featureTypeStyle.append(processTransformation(geostyler["transformation"]))
    for rule in geostyler["rules"]:
        featureTypeStyle.append(processRule(rule))
    
    sldstring = ElementTree.tostring(root, encoding='utf8', method='xml').decode()
    dom = minidom.parseString(sldstring)    
    return dom.toprettyxml(indent="  "), _warnings



def processRule(rule):    
    ruleElement = Element("Rule")
    ruleName = SubElement(ruleElement, "Name")
    ruleName.text = rule.get("name", "")
    if "scaleDenominator" in rule:
        scale = rule["scaleDenominator"]
        if "max" in scale:
            maxScale = SubElement(ruleElement, "MaxScaleDenominator")
            maxScale.text = scale["max"]
        if "min" in scale:
            minScale = SubElement(ruleElement, "MinScaleDenominator")
            maxScale.text = scale["min"]
    filt = convertExpression(rule.get("filter", None))
    if filt is not None:
        filterElement = Element("ogc:Filter")
        filterElement.append(filt)
        ruleElement.append(filterElement)
    symbolizers = _createSymbolizers(rule["symbolizers"])
    ruleElement.extend(symbolizers)
    
    return ruleElement
        
def _createSymbolizers(symbolizers):    
    sldSymbolizers = []    
    for sl in symbolizers:
        symbolizer = _createSymbolizer(sl)        
        if symbolizer is not None:
            if isinstance(symbolizer, list):
                sldSymbolizers.extend(symbolizer)
            else:
                sldSymbolizers.append(symbolizer)

    return sldSymbolizers

def _createSymbolizer(sl):
    symbolizerType = sl["kind"]
    if symbolizerType == "Icon":
        symbolizer = _iconSymbolizer(sl)
    if symbolizerType == "Line":
        symbolizer = _lineSymbolizer(sl)            
    if symbolizerType == "Fill":
        symbolizer = _fillSymbolizer(sl)
    if symbolizerType == "Mark":
        symbolizer = _markSymbolizer(sl)
    if symbolizerType == "Text":
        symbolizer = _textSymbolizer(sl)
    if symbolizerType == "Raster":
        symbolizer = _rasterSymbolizer(sl)        
    
    geom = _geometryFromSymbolizer(sl)
    if geom is not None:
        symbolizer.insert(0, geom)

    return symbolizer

def _symbolProperty(sl, name):
    if name in sl:        
        return _processProperty(sl[name])      
    else:
        return None

def _processProperty(value):
    v = convertExpression(value)
    if isinstance(v, Element) and v.tag == "ogc:Literal":
        v = v.text
    return v
    
def _addValueToElement(element, value):
    if value is not None:  
        if isinstance(value, Element):
            element.append(value)
        else:
            element.text = str(value)

def _addCssParameter(parent, name, value):
    if value is not None:        
        sub = SubElement(parent, "CssParameter", name=name)
        _addValueToElement(sub, value)
        return sub

def _addSubElement(parent, tag, value=None, attrib={}):
    strAttrib = {k: str(v) for k,v in attrib.items()}
    sub = SubElement(parent, tag, strAttrib)
    _addValueToElement(sub, value)
    return sub

def _addVendorOption(parent, name, value):
    sub = SubElement(parent, "VendorOption", name=name)
    _addValueToElement(sub, value)
    return sub    

def _rasterSymbolizer(sl):
    opacity = sl["opacity"]
    root = Element("RasterSymbolizer")
    _addSubElement(root, "Opacity", opacity)
    
    channelSelectionElement = _addSubElement(root, "ChannelSelection")
    for chanName in ["grayChannel", "redChannel", "greenChannel", "blueChannel"]:
        if chanName in sl["channelSelection"]:
            sldChanName = chanName[0].upper() + chanName[1:]
            channel = _addSubElement(channelSelectionElement, sldChanName)
            _addSubElement(channel, "SourceChannelName", sl["channelSelection"][chanName]["sourceChannelName"])
        
    if "colorMap" in sl:
        colMap = sl["colorMap"]
        colMapElement = _addSubElement(root, "ColorMap", None, {"type": sl["colorMap"]["type"]})
        for entry in colMap["colorMapEntries"]:
            attribs = {"color": entry["color"], "quantity": entry["quantity"],
                        "label": entry["label"], "opacity": entry["opacity"]}                        
            _addSubElement(colMapElement, "ColorMapEntry", None, attribs)

    return root

def _textSymbolizer(sl):
    color = _symbolProperty(sl, "color")
    fontFamily = _symbolProperty(sl, "font")
    label = _symbolProperty(sl, "label")
    size = _symbolProperty(sl, "size")

    root = Element("TextSymbolizer")
    _addSubElement(root, "Label", label)
    fontElem = _addSubElement(root, "Font")    
    _addCssParameter(fontElem, "font-family", fontFamily)
    _addCssParameter(fontElem, "font-size", size)
    fillElem = _addSubElement(root, "Fill")
    _addCssParameter(fontElem, "fill", color)

    if "offset" in sl:
        placement = _addSubElement(root, "LabelPlacement")
        pointPlacement = _addSubElement(placement, "PointPlacement")      
        if "anchor" in sl:
            anchor = sl["anchor"]
            #######
        displacement = _addSubElement(pointPlacement, "Displacement")
        offset = sl["offset"]
        offsetx = _processProperty(offset[0])
        offsety = _processProperty(offset[1])            
        _addSubElement(displacement, "DisplacementX", offsetx)
        _addSubElement(displacement, "DisplacementY", offsety)
    if "dist" in sl:
        placement = _addSubElement(root, "LabelPlacement")
        linePlacement = _addSubElement(placement, "LinePlacement")
        dist = _processProperty(offset)
        _addSubElement(linePlacement, "PerpendicularOffset", dist)



    if "haloColor" in sl and "haloSize" in sl:
        haloElem = _addSubElement(root, "Halo")
        _addSubElement(haloElem, "Radius", sl["haloSize"])
        haloFillElem = _addSubElement(haloElem, "Fill")
        _addCssParameter(haloFillElem, "fill", sl["haloColor"])

    return root

def _lineSymbolizer(sl, graphicStrokeLayer = 0):
    opacity = _symbolProperty(sl, "opacity")
    color =  sl.get("color", None)
    graphicStroke =  sl.get("graphicStroke", None)
    width = _symbolProperty(sl, "width")
    dasharray = _symbolProperty(sl, "dasharray")
    cap = _symbolProperty(sl, "cap")
    join = _symbolProperty(sl, "join")
    offset = _symbolProperty(sl, "perpendicularOffset")

    root = Element("LineSymbolizer")
    symbolizers = [root]
    stroke = _addSubElement(root, "Stroke")
    if graphicStroke is not None:
        graphicStrokeElement = _addSubElement(stroke, "GraphicStroke")
        graphic = _graphicFromSymbolizer(graphicStroke[graphicStrokeLayer])
        graphicStrokeElement.append(graphic[0])
        interval = sl.get("graphicStrokeInterval")
        dashOffset = sl.get("graphicStrokeOffset")
        size = graphicStroke[graphicStrokeLayer].get("size")
        _addCssParameter(stroke, "stroke-dasharray", "%s %s" % (str(size), str(interval)))
        _addCssParameter(stroke, "stroke-dashoffset", dashOffset)
        if graphicStrokeLayer == 0 and len(graphicStroke) > 1:
            for i in range(1, len(graphicStroke)):
                symbolizers.extend(_lineSymbolizer(sl, i))
    if color is not None:                
        _addCssParameter(stroke, "stroke", color)
        _addCssParameter(stroke, "stroke-width", width)
        _addCssParameter(stroke, "stroke-opacity", opacity)
        _addCssParameter(stroke, "stroke-linejoin", join)
        _addCssParameter(stroke, "stroke-linecap", cap)    
        if dasharray is not None:
            _addCssParameter(stroke, "stroke-dasharray", dasharray)
    if offset is not None:
        _addSubElement(root, "PerpendicularOffset", offset)
    return root
    
def _geometryFromSymbolizer(sl):
    geomExpr = convertExpression(sl.get("geometry", None))
    if geomExpr is not None:
        geomElement = Element("Geometry")
        geomElement.append(geomExpr)
        return geomElement        

def _iconSymbolizer(sl):
    path = sl["image"]
    if path.lower().endswith("svg"):
        return _svgMarkerSymbolizer(sl)
    else:
        return _rasterImageMarkerSymbolizer(sl)

def _svgMarkerSymbolizer(sl):
    root, graphic = _basePointSimbolizer(sl)
    svg = _svgGraphic(sl)
    graphic.insert(0, svg)
    return root

def _rasterImageMarkerSymbolizer(sl):
    root, graphic = _basePointSimbolizer(sl)
    img = _rasterImageGraphic(sl)
    graphic.insert(0, img)
    return root    

def _markSymbolizer(sl):
    root, graphic = _basePointSimbolizer(sl)
    mark = _markGraphic(sl)
    graphic.insert(0, mark)
    return root

def _basePointSimbolizer(sl):
    size = _symbolProperty(sl, "size")
    rotation = _symbolProperty(sl, "rotate")
    opacity = _symbolProperty(sl, "opacity")
    
    root = Element("PointSymbolizer")
    graphic = _addSubElement(root, "Graphic")
    _addSubElement(graphic, "Opacity", opacity)
    _addSubElement(graphic, "Size", size)
    _addSubElement(graphic, "Rotation", rotation)
  
    return root, graphic

def _markGraphic(sl):
    color = _symbolProperty(sl, "color")
    outlineColor = _symbolProperty(sl, "strokeColor")
    outlineWidth = _symbolProperty(sl, "strokeWidth")
    outlineDasharray = _symbolProperty(sl, "strokeDasharray")
    shape = _symbolProperty(sl, "wellKnownName")
    mark = Element("Mark")
    _addSubElement(mark, "WellKnownName", shape)
    fill = SubElement(mark, "Fill")
    _addCssParameter(fill, "fill", color)
    stroke = _addSubElement(mark, "Stroke")    
    _addCssParameter(stroke, "stroke", outlineColor)
    _addCssParameter(stroke, "stroke-width", outlineWidth)
    if outlineDasharray is not None:
        _addCssParameter(stroke, "stroke-dasharray", outlineDasharray)

    return mark

def _svgGraphic(sl):
    path = os.path.basename(sl["image"])
    color = _symbolProperty(sl, "color")
    outlineColor = _symbolProperty(sl, "strokeColor")
    outlineWidth = _symbolProperty(sl, "strokeWidth")
    mark = Element("Mark")
    _addSubElement(mark, "WellKnownName", "file://%s" % path)
    fill = _addSubElement(mark, "Fill")
    _addCssParameter(fill, "fill", color)
    stroke = _addSubElement(mark, "Stroke")    
    _addCssParameter(stroke, "stroke", outlineColor)
    _addCssParameter(stroke, "stroke-width", outlineWidth)    
    return mark   

def _rasterImageGraphic(sl):
    path = os.path.basename(sl["image"])
    externalGraphic = Element("ExternalGraphic")  
    attrib = {
        "xlink:type": "simple",
        "xlink:href": path
    } 
    SubElement(externalGraphic, "OnlineResource", attrib=attrib)
    _addSubElement(externalGraphic, "Format", "image/%s" % os.path.splitext(path)[1][1:]) 
    return externalGraphic 

def _baseFillSymbolizer(sl):
    root = Element("PolygonSymbolizer")
    return root

def _graphicFromSymbolizer(sl):
    symbolizer = _createSymbolizer(sl)
    return [graph for graph in symbolizer.iter("Graphic")]
        
def _fillSymbolizer(sl, graphicFillLayer = 0):
    root = _baseFillSymbolizer(sl)
    symbolizers = [root]
    opacity = _symbolProperty(sl, "opacity")
    color =  sl.get("color", None)
    graphicFill =  sl.get("graphicFill", None)
    if graphicFill is not None:
        margin = _symbolProperty(sl, "graphicFillMarginX")
        fill = _addSubElement(root, "Fill")
        graphicFillElement = _addSubElement(fill, "GraphicFill")        
        graphic = _graphicFromSymbolizer(graphicFill[graphicFillLayer])
        graphicFillElement.append(graphic[0])
        _addVendorOption(root, "graphic-margin", margin)
        if graphicFillLayer == 0 and len(graphicFill) > 1:
            for i in range(1, len(graphicFill)):
                symbolizers.extend(_fillSymbolizer(sl, i))
    if color is not None:                
        fill = _addSubElement(root, "Fill")
        _addCssParameter(fill, "fill", color)
        _addCssParameter(fill, "fill-opacity", opacity)

    outlineColor = _symbolProperty(sl, "outlineColor")
    if outlineColor is not None:
        outlineDasharray = _symbolProperty(sl, "outlineDasharray")
        outlineWidth = _symbolProperty(sl, "outlineWidth")                
        #borderWidthUnits = props["outline_width_unit"]
        stroke = _addSubElement(root, "Stroke")
        _addCssParameter(stroke, "stroke", outlineColor)
        _addCssParameter(stroke, "stroke-width", outlineWidth)
        _addCssParameter(stroke, "stroke-opacity", opacity)
        #_addCssParameter(stroke, "stroke-linejoin", join)
        #_addCssParameter(stroke, "stroke-linecap", cap)
        if outlineDasharray is not None:
            _addCssParameter(stroke, "stroke-dasharray", " ".join(str(v) for v in outlineDasharray))

    return symbolizers

#######################

operators = ["PropertyName", 
     "Or", 
    "And", 
     "PropertyIsEqualTo", 
     "PropertyIsNotEqualTo", 
     "PropertyIsLessThanOrEqualTo", 
     "PropertyIsGreaterThanOrEqualTo", 
     "PropertyIsLessThan", 
     "PropertyIsGreaterThan", 
     "Add", 
      "Sub", 
      "Mul", 
      "Div", 
      "Not"]

def convertExpression(exp):
    if exp is None:
        return None
    elif isinstance(exp, list):
        if exp[0] in operators:
            return handleOperator(exp)
        else:
            return handleFunction(exp)        
    else:
        return handleLiteral(exp)

def handleOperator(exp):
    name = exp[0]
    elem = Element("ogc:" + name) 
    if name == "PropertyName":
        elem.text = exp[1]  
    else:
        for operand in exp[1:]:
            elem.append(convertExpression(operand))    
    return elem

def handleFunction(exp):
    name = exp[0]
    elem = Element("ogc:Function", name=name)
    if len(exp) > 1:        
        for arg in exp[1:]:
            elem.append(convertExpression(arg))
    return elem

def handleLiteral(v):
    elem = Element("ogc:Literal")
    elem.text = str(v)
    return elem
