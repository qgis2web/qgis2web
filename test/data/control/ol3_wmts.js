
    var projection_taiwanemapen0 = ol.proj.get('EPSG:3857');
    var projectionExtent_taiwanemapen0 = projection_taiwanemapen0.getExtent();
    var size_taiwanemapen0 = ol.extent.getWidth(projectionExtent_taiwanemapen0) / 256;
    var resolutions_taiwanemapen0 = new Array(14);
    var matrixIds_taiwanemapen0 = new Array(14);
    for (var z = 0; z < 14; ++z) {
        // generate resolutions and matrixIds arrays for this WMTS
        resolutions_taiwanemapen0[z] = size_taiwanemapen0 / Math.pow(2, z);
        matrixIds_taiwanemapen0[z] = z;
    }
    var lyr_taiwanemapen0 = new ol.layer.Tile({
                            source: new ol.source.WMTS(({
                              url: "http://wmts.nlsc.gov.tw/wmts",
    attributions: [new ol.Attribution({html: '<a href=""></a>'})],
                                "layer": "EMAP8",
                                "TILED": "true",
             matrixSet: 'EPSG:3857',
             format: 'image/jpeg',
              projection: projection_taiwanemapen0,
              tileGrid: new ol.tilegrid.WMTS({
                origin: ol.extent.getTopLeft(projectionExtent_taiwanemapen0),
                resolutions: resolutions_taiwanemapen0,
                matrixIds: matrixIds_taiwanemapen0
              }),
              style: 'default',
              wrapX: true,
                                "VERSION": "1.0.0",
                            })),
                            title: "taiwane-map(en)",
                            opacity: 1.0,
                            
                            
                          });

lyr_taiwanemapen0.setVisible(true);
var layersList = [lyr_taiwanemapen0];
