var wms_layers = [];
var lyr_wms_0 = new ol.layer.Tile({
                            source: new ol.source.TileWMS(({
                              url: "http://ogc.bgs.ac.uk/cgi-bin/BGS_Bedrock_and_Superficial_Geology/wms?",
    attributions: ' ',
                              params: {
                                "LAYERS": "GBR_BGS_625k_BLT",
                                "TILED": "true",
                                "VERSION": "1.3.0"},
                            })),
                            title: "wms",
                            opacity: 1.000000,
                            
                            
                          });
              wms_layers.push([lyr_wms_0, 0]);


var layersList = [lyr_wms_0];
