var createTextStyle = function(feature, resolution, labelText, labelFont,
                               labelFill, placement, bufferColor,
                               bufferWidth, textAlign, offsetX, offsetY, overflow, repeat) {

    if (feature.hide || !labelText) {
        return; 
    } 

    // Convert a literal "\n" (backslash + n) found in the attribute data
    // into a real line break, so labels are rendered on multiple lines.
    labelText = String(labelText).replace(/\\n/g, "\n");

    if (bufferWidth == 0) {
        var bufferStyle = null;
    } else {
        var bufferStyle = new ol.style.Stroke({
            color: bufferColor,
            width: bufferWidth
        })
    }
    
    var textStyle = new ol.style.Text({
        font: labelFont,
        text: labelText,
        textBaseline: "middle",
        textAlign: textAlign,
        offsetX: offsetX,
        offsetY: offsetY,
        placement: placement,
        overflow: overflow,
        repeat: repeat,
        maxAngle: 0,
        fill: new ol.style.Fill({
          color: labelFill
        }),
        stroke: bufferStyle
    });

    return textStyle;
};

function stripe(stripeWidth, gapWidth, angle, color) {
    var step = Math.max(1, stripeWidth + gapWidth);
    var rad = ((angle % 360) * Math.PI) / 180;
    var sin = Math.sin(rad);
    var cos = Math.cos(rad);

    var tileW, tileH;
    if (Math.abs(sin) < 1e-6) {
        tileW = 64;
        tileH = step;
    } else if (Math.abs(cos) < 1e-6) {
        tileW = step;
        tileH = 64;
    } else {
        var rawW = Math.abs(step / sin);
        var rawH = Math.abs(step / cos);
        var mult = Math.max(1, Math.round(64 / Math.min(rawW, rawH)));
        tileW = Math.max(1, Math.round(rawW * mult));
        tileH = Math.max(1, Math.round(rawH * mult));
    }

    var canvas = document.createElement('canvas');
    canvas.width = tileW;
    canvas.height = tileH;
    var ctx = canvas.getContext('2d');

    ctx.save();
    ctx.translate(tileW / 2, tileH / 2);
    ctx.rotate(rad);

    var diag = Math.ceil(Math.sqrt(tileW * tileW + tileH * tileH));
    var actualStep = Math.abs(sin) >= Math.abs(cos)
        ? (tileW * Math.abs(sin)) / Math.max(1, Math.round((tileW * Math.abs(sin)) / step))
        : (tileH * Math.abs(cos)) / Math.max(1, Math.round((tileH * Math.abs(cos)) / step));

    ctx.fillStyle = color;
    for (var y = -diag; y <= diag; y += actualStep) {
        ctx.fillRect(-diag, y - stripeWidth / 2, diag * 2, stripeWidth);
    }
    ctx.restore();

    return ctx.createPattern(canvas, 'repeat');
};
