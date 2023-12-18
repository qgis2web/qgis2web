from qgis.core import QgsExpressionNode, QgsExpression, QgsExpressionNodeBinaryOperator


class UnsupportedExpressionException(Exception):
    pass


binaryOps = [
    "Or",
    "And",
    "PropertyIsEqualTo",
    "PropertyIsNotEqualTo",
    "PropertyIsLessThanOrEqualTo",
    "PropertyIsGreaterThanOrEqualTo",
    "PropertyIsLessThan",
    "PropertyIsGreaterThan",
    None,
    "PropertyIsLike",
    None,
    None,
    None,
    None,
    None,
    "Add",
    "Sub",
    "Mul",
    "Div",
    None,
    None,
    None,
    None,
]

unaryOps = ["Not", "Sub"]

functions = {
    "radians": "toRadians",
    "degrees": "toDegrees",
    "floor": "floor",
    "ceil": "ceil",
    "area": "area",
    "buffer": "buffer",
    "centroid": "centroid",
    "if": "if_then_else",
    "bounds": "envelope",
    "distance": "distance",
    "convex_hull": "convexHull",
    "end_point": "endPoint",
    "start_point": "startPoint",
    "x": "getX",
    "y": "getY",
    "concat": "Concatenate",
    "substr": "strSubstr",
    "lower": "strToLower",
    "upper": "strToUpper",
    "replace": "strReplace",
    "exterior_ring": "exteriorRing",
    "intersects": "intersects",
    "overlaps": "overlaps",
    "touches": "touches",
    "within": "within",
    "relates": "relates",
    "crosses": "crosses",
    "disjoint": "disjoint",
    "geom_from_wkt": "geomFromWKT",
    "perimeter": "geomLength",
    "union": "union",
    "acos": "acos",
    "asin": "asin",
    "atan": "atan",
    "atan2": "atan2",
    "sin": "sin",
    "cos": "cos",
    "tan": "tan",
    "ln": "log",
    "title": "strCapitalize",
    "translate": "offset",
    "min": "min",
    "max": "max",
}  # TODO


def walkExpression(node, layer):
    if node.nodeType() == QgsExpressionNode.ntBinaryOperator:
        exp = handleBinary(node, layer)
    elif node.nodeType() == QgsExpressionNode.ntUnaryOperator:
        exp = handleUnary(node, layer)
    elif node.nodeType() == QgsExpressionNode.ntInOperator:
        exp = handle_in(node, layer)
    elif node.nodeType() == QgsExpressionNode.ntFunction:
        exp = handleFunction(node, layer)
    elif node.nodeType() == QgsExpressionNode.ntLiteral:
        exp = handleLiteral(node)
    elif node.nodeType() == QgsExpressionNode.ntColumnRef:
        exp = handleColumnRef(node, layer)
    else:
        exp = None
    # elif node.nodeType() == QgsExpression.ntCondition:
    #    filt = handle_condition(nod)
    if exp is None:
        raise UnsupportedExpressionException(
            "Unsupported operator in expression: '%s'" % str(node)
        )
    return exp


# handle IN expression
# convert to a series of (A='a') OR (B='b')
def handle_in(node, layer):
    if node.isNotIn():
        raise UnsupportedExpressionException("expression NOT IN is unsupported")
    # convert this expression to another (equivelent Expression)
    if node.node().nodeType() != QgsExpressionNode.ntColumnRef:
        raise UnsupportedExpressionException("expression  IN doesn't ref column!")
    if node.list().count() == 0:
        raise UnsupportedExpressionException(
            "expression  IN doesn't have anything inside the IN"
        )

    colRef = handleColumnRef(node.node(), layer)
    propEqualsExprs = []  # one for each of the literals in the expression
    for item in node.list().list():
        if item.nodeType() != QgsExpressionNode.ntLiteral:
            raise UnsupportedExpressionException("expression  IN isn't literal")
        # equals_expr = QgsExpressionNodeBinaryOperator(2,colRef,item) #2 is "="
        equals_expr = [binaryOps[2], colRef, handleLiteral(item)]  # 2 is "="
        propEqualsExprs.append(equals_expr)

    # bulid into single expression
    if len(propEqualsExprs) == 1:
        return propEqualsExprs[0]  # handle 1 item in the list
    accum = [binaryOps[0], propEqualsExprs[0], propEqualsExprs[1]]  # 0="OR"
    for idx in range(2, len(propEqualsExprs)):
        accum = [binaryOps[0], accum, propEqualsExprs[idx]]  # 0="OR"
    return accum


def handleBinary(node, layer):
    op = node.op()
    retOp = binaryOps[op]
    left = node.opLeft()
    right = node.opRight()
    retLeft = walkExpression(left, layer)
    retRight = walkExpression(right, layer)
    return [retOp, retLeft, retRight]


def handleUnary(node, layer):
    op = node.op()
    operand = node.operand()
    retOp = unaryOps[op]
    retOperand = walkExpression(operand, layer)
    if retOp == "Sub":  # handle the particular case of a minus in a negative number
        return [retOp, 0, retOperand]
    else:
        return [retOp, retOperand]


def handleLiteral(node):
    val = node.value()
    quote = ""
    if isinstance(val, basestring):
        quote = "'"
        val = val.replace("\n", "\\n")
    elif val is None:
        val = "null"
    return val


def handleColumnRef(node, layer):
    if layer is not None:
        attrName = node.name().casefold()
        for field in layer.fields():
            if field.name().casefold() == attrName:
                return ["PropertyName", field.name()]
    return ["PropertyName", node.name()]


def handleFunction(node, layer):
    fnIndex = node.fnIndex()
    func = QgsExpression.Functions()[fnIndex].name()
    if func == "$geometry":
        return ["PropertyName", "geom"]
    elif func in functions:
        elems = [functions[func]]
        args = node.args()
        if args is not None:
            args = args.list()
            for arg in args:
                elems.append(walkExpression(arg, layer))
        return elems
    else:
        raise UnsupportedExpressionException(
            "Unsupported function in expression: '%s'" % func
        )
