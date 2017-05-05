
    var projection_wms0 = ol.proj.get('EPSG:3857');
    var projectionExtent_wms0 = projection_wms0.getExtent();
    var size_wms0 = ol.extent.getWidth(projectionExtent_wms0) / 256;
    var resolutions_wms0 = new Array(14);
    var matrixIds_wms0 = new Array(14);
    for (var z = 0; z < 14; ++z) {
        // generate resolutions and matrixIds arrays for this WMTS
        resolutions_wms0[z] = size_wms0 / Math.pow(2, z);
        matrixIds_wms0[z] = z;
    }
    var lyr_wms0 = new ol.layer.Tile({
                            source: new ol.source.WMTS(({
                              url: "http://wmts.nlsc.gov.tw/wmts",
    attributions: [new ol.Attribution({html: '<a href=""></a>'})],
                                "layer": "EMAP8",
                                "TILED": "true",
             matrixSet: 'EPSG:3857',
             format: 'image/jpeg',
              projection: projection_wms0,
              tileGrid: new ol.tilegrid.WMTS({
                origin: ol.extent.getTopLeft(projectionExtent_wms0),
                resolutions: resolutions_wms0,
                matrixIds: matrixIds_wms0
              }),
              style: 'default',
              wrapX: true,
                                "VERSION": "1.0.0",
                            })),
                            title: "wms",
                            opacity: 1.0,
                            
                            
                          });

lyr_wms0.setVisible(true);
var layersList = [lyr_wms0];
