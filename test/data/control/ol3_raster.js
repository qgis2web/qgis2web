var lyr_3857 = new ol.layer.Image({
                            opacity: 1,
                            title: "3857",
                            
                            
                            source: new ol.source.ImageStatic({
                               url: "./layers/3857.png",
                                projection: 'EPSG:3857',
                                alwaysInRange: true,
                                //imageSize: [1000, 1003],
                                imageExtent: [-234984.529972, 7356155.401586, -233243.512382, 7357901.642229]
                            })
                        });

lyr_3857.setVisible(true);
var layersList = [lyr_3857];
