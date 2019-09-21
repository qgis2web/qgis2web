from . import togeostyler 
from . import fromgeostyler

def toGeostyler(style):
    return togeostyler.convert(style) #TODO

def fromGeostyler(style):
    sld, warnings = fromgeostyler.convert(style)
    return sld