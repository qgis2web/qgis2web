import sys
from bridgestyle import sld
from bridgestyle import geostyler
from bridgestyle import mapboxgl

_exts = {"sld": sld, "geostyler": geostyler, "mapbox": mapboxgl}

def convert(fileA, fileB):
	extA = os.path.splitext(fileA)[1][1:]
	extB = os.path.splitext(fileB)[1][1:]
	if extA not in _exts:
		print("Unsupported style type: '%s'" % extA)
	if extB not in _exts:
		print("Unsupported style type: '%s'" % ext)

	with open(fileA) as f:
		styleA = f.read()

	geostyler = _exts[extA].toGeostyler(styleA)
	styleB = _exts[extB].fromGeostyler(geostyler)

	with open(fileB, "w") as f:
		f.write(style)

def main():
	if len(sys.argv) != 3:
		print("Wrong number of parameters\nUsage: style2style original_style_file.ext destination_style_file.ext")
	else:
		convert(sys.argv[1], sys.argv[2])