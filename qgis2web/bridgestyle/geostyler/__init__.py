import json

def toGeostyler(style):
	return json.loads(style)

def fromGeostyler(style):
	return json.dumps(style)