function mToPx(metres) {
    var C = 40075016.686;
    var c = map.getCenter();
    var l = c.lat;
    var r = 180/Math.PI;
    var z = map.getZoom();
    var m = C * Math.abs(Math.cos(l * r)) / Math.pow(2, z + 8);
    var px = Math.ceil(1 / m);
    return px;
}
