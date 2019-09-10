var wms_layers = [];

var lyr_test_0 = new ol.layer.Image({
                            opacity: 1,
                            title: "test",
                            
                            
                            source: new ol.source.ImageStatic({
                               url: "./layers/test_0.png",
    attributions: ' ',
                                projection: 'EPSG:3857',
                                alwaysInRange: true,
                                imageExtent: [-234984.529972, 7356155.401586, -233243.512382, 7357901.642229]
                            })
                        });

lyr_test_0.setVisible(true);
var layersList = [lyr_test_0];
