var size = 0;

var styleCache_airports0={}
var style_airports0 = function(feature, resolution){
    var context = {
        feature: feature,
        variables: {}
    };
    var value = ""
    var labelText = "";
    var key = "";
    size = 0;
    var textAlign = "left";
    var offsetX = 8;
    var offsetY = 3;
    if ("" !== null) {
        labelText = String("");
    } else {
        labelText = ""
    }
    var style = [ new ol.style.Style({
        image: new ol.style.Icon({
                  imgSize: [100, 100],
                  scale: 0.07,
                  anchor: [3, 3],
                  anchorXUnits: "pixels",
                  anchorYUnits: "pixels",
                  rotation: 0.0,
                  src: "styles/qgis2web.svg"
            })
    })];
      var key = value + "_" + labelText
      if (!styleCache_airports0[key]){
          var text = new ol.style.Text({
                  font: '10.725px \'MS Shell Dlg 2\', sans-serif',
                  text: labelText,
                  textBaseline: "middle",
                  textAlign: textAlign,
                  offsetX: offsetX,
                  offsetY: offsetY,
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