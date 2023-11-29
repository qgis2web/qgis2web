var wms_layers = [];

    var projection_wms_0 = ol.proj.get('EPSG:3857');
    var projectionExtent_wms_0 = projection_wms_0.getExtent();
    var size_wms_0 = ol.extent.getWidth(projectionExtent_wms_0) / 256;
    var resolutions_wms_0 = new Array(14);
    var matrixIds_wms_0 = new Array(14);
    for (var z = 0; z < 14; ++z) {
        // generate resolutions and matrixIds arrays for this WMTS
        resolutions_wms_0[z] = size_wms_0 / Math.pow(2, z);
        matrixIds_wms_0[z] = z;
    }
    var lyr_wms_0 = new ol.layer.Tile({
                            source: new ol.source.WMTS(({
                              url: "http://wmts.nlsc.gov.tw/wmts",
    attributions: ' ',
                                "layer": "EMAP8",
                                "TILED": "true",
             matrixSet: 'EPSG:3857',
             format: 'image/jpeg',
              projection: projection_wms_0,
              tileGrid: new ol.tilegrid.WMTS({
                origin: ol.extent.getTopLeft(projectionExtent_wms_0),
                resolutions: resolutions_wms_0,
                matrixIds: matrixIds_wms_0
              }),
              style: 'default',
              wrapX: true,
                                "VERSION": "1.0.0",
                            })),
                            title: "wms",
                            opacity: 1.0,
                            
                            
                          });


var layersList = [lyr_wms_0];
