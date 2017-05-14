var size = 0;

var styleCache_airports0={}
var style_airports0 = function(feature, resolution){
    var context = {
        feature: feature,
        variables: {}
    };
    var value = '';
    
        function rules_airports0(feature, value) {
            var context = {
                feature: feature,
                variables: {}
            };
            // Start of if blocks and style check logic
            if (airports0rule0_eval_expression(context)) {
                      return [ new ol.style.Style({
        image: new ol.style.Circle({radius: 4.0 + size,
            stroke: new ol.style.Stroke({color: 'rgba(0,0,0,1.0)', lineDash: null, lineCap: 'butt', lineJoin: 'miter', width: 0}), fill: new ol.style.Fill({color: 'rgba(220,157,175,1.0)'})})
    })];
                    }
            else {
                return [ new ol.style.Style({
        image: new ol.style.Circle({radius: 4.0 + size,
            stroke: new ol.style.Stroke({color: 'rgba(0,0,0,1.0)', lineDash: null, lineCap: 'butt', lineJoin: 'miter', width: 0}), fill: new ol.style.Fill({color: 'rgba(39,147,25,1.0)'})})
    })];
            }
        }
        var style = rules_airports0(feature, value);
        ;
    var labelText = ""
    if (size >= 2) {
        labelText = size.toString()
    } else {
        labelText = ""
    }
    var key = value + "_" + labelText

    if (!styleCache_FieldSites0[key]){
        var text = new ol.style.Text({
              font: '13.0px \'MS Shell Dlg 2\', sans-serif',
              text: labelText,
              textAlign: "center",
              offsetX: 0,
              offsetY: 0,
              fill: new ol.style.Fill({
                color: 'rgba(0, 0, 0, 1)'
              }),
            });
        styleCache_airports0[key] = new ol.style.Style({"text": text})
    }
    var allStyles = [styleCache_airports0[key]];
    allStyles.push.apply(allStyles, style);
    return allStyles;
};