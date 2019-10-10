from xml.etree.ElementTree import Element, SubElement

def _addLiteral(parent, v):
    elem = SubElement(parent, "ogc:Literal")
    elem.text = str(v)

def processTransformation(transformation):
    root = Element("Transformation")
    trans = SubElement(root, "ogc:Function", name=transformation["type"])
    
    if transformation["type"] == "vec:Heatmap":
    	data = SubElement(trans, "ogc:Function", name="parameter")
    	_addLiteral(data, "data")
    	weight = SubElement(trans, "ogc:Function", name="parameter")
    	_addLiteral(weight, "weightAttr")
    	_addLiteral(weight, transformation["weightAttr"])
    	radius = SubElement(trans, "ogc:Function", name="parameter")
    	_addLiteral(radius, "radiusPixels")
    	_addLiteral(radius, transformation["radiusPixels"])
    	def _addEnvParam(paramName, envParamName):
    		param = SubElement(trans, "ogc:Function", name="parameter")
    		_addLiteral(param, paramName)
    		env = SubElement(param, "ogc:Function", name="env")
    		_addLiteral(env, envParamName)
    	_addEnvParam("outputBBOX", "wms_bbox")
    	_addEnvParam("outputWidth", "wms_width")
    	_addEnvParam("outputHeight", "wms_height")

    return root