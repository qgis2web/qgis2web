!function (e, t) {
    "object" == typeof exports && "undefined" != typeof module ? t(exports, require("ol/Map.js"), require("ol/View.js"), require("ol/extent.js"), require("ol/format/GeoJSON.js"), require("ol/format/MVT.js"), require("ol/has.js"), require("ol/layer/Group.js"), require("ol/layer/Layer.js"), require("ol/layer/Tile.js"), require("ol/layer/Vector.js"), require("ol/layer/VectorTile.js"), require("ol/loadingstrategy.js"), require("ol/proj.js"), require("ol/proj/Units.js"), require("ol/source/Source.js"), require("ol/source/TileJSON.js"), require("ol/source/Vector.js"), require("ol/source/VectorTile.js"), require("ol/tilegrid.js"), require("ol/tilegrid/TileGrid.js"), require("ol/color.js"), require("ol/layer/Image.js"), require("ol/source/Raster.js"), require("ol/coordinate.js"), require("ol/functions.js"), require("ol/render/Feature.js"), require("ol/style/Circle.js"), require("ol/style/Fill.js"), require("ol/style/Icon.js"), require("ol/style/Stroke.js"), require("ol/style/Style.js"), require("ol/style/Text.js"), require("ol/render/canvas.js"), require("ol"), require("ol/TileState.js"), require("ol/util.js"), require("ol/events/Event.js"), require("ol/events/EventType.js")) : "function" == typeof define && define.amd ? define(["exports", "ol/Map.js", "ol/View.js", "ol/extent.js", "ol/format/GeoJSON.js", "ol/format/MVT.js", "ol/has.js", "ol/layer/Group.js", "ol/layer/Layer.js", "ol/layer/Tile.js", "ol/layer/Vector.js", "ol/layer/VectorTile.js", "ol/loadingstrategy.js", "ol/proj.js", "ol/proj/Units.js", "ol/source/Source.js", "ol/source/TileJSON.js", "ol/source/Vector.js", "ol/source/VectorTile.js", "ol/tilegrid.js", "ol/tilegrid/TileGrid.js", "ol/color.js", "ol/layer/Image.js", "ol/source/Raster.js", "ol/coordinate.js", "ol/functions.js", "ol/render/Feature.js", "ol/style/Circle.js", "ol/style/Fill.js", "ol/style/Icon.js", "ol/style/Stroke.js", "ol/style/Style.js", "ol/style/Text.js", "ol/render/canvas.js", "ol", "ol/TileState.js", "ol/util.js", "ol/events/Event.js", "ol/events/EventType.js"], t) : t((e = "undefined" != typeof globalThis ? globalThis : e || self).olms = {}, e.ol.Map, e.ol.View, e.ol.extent, e.ol.format.GeoJSON, e.ol.format.MVT, e.ol.has, e.ol.layer.Group, e.ol.layer.Layer, e.ol.layer.Tile, e.ol.layer.Vector, e.ol.layer.VectorTile, e.ol.loadingstrategy, e.ol.proj, e.ol.proj.Units, e.ol.source.Source, e.ol.source.TileJSON, e.ol.source.Vector, e.ol.source.VectorTile, e.ol.tilegrid, e.ol.tilegrid.TileGrid, e.ol.color, e.ol.layer.Image, e.ol.source.Raster, e.ol.coordinate, e.ol.functions, e.ol.render.Feature, e.ol.style.Circle, e.ol.style.Fill, e.ol.style.Icon, e.ol.style.Stroke, e.ol.style.Style, e.ol.style.Text, e.ol.render.canvas, e.ol, e.ol.TileState, e.ol.util, e.ol.events.Event, e.ol.events.EventType)
}
(this, function (e, t, r, n, o, a, i, s, l, u, c, p, f, d, m, y, h, g, b, v, x, w, k, M, z, S, j, A, E, q, $, C, _, T, O, N, P, I, F) {
    "use strict";
    var R = {
        $version: 8,
        $root: {
            version: {
                required: !0,
                type: "enum",
                values: [8]
            },
            name: {
                type: "string"
            },
            metadata: {
                type: "*"
            },
            center: {
                type: "array",
                value: "number",
                length: 2
            },
            centerAltitude: {
                type: "number"
            },
            zoom: {
                type: "number"
            },
            bearing: {
                type: "number",
            default:
                0,
                period: 360,
                units: "degrees"
            },
            pitch: {
                type: "number",
            default:
                0,
                units: "degrees"
            },
            roll: {
                type: "number",
            default:
                0,
                units: "degrees"
            },
            state: {
                type: "state",
            default: {}
            },
            light: {
                type: "light"
            },
            sky: {
                type: "sky"
            },
            projection: {
                type: "projection"
            },
            terrain: {
                type: "terrain"
            },
            sources: {
                required: !0,
                type: "sources"
            },
            sprite: {
                type: "sprite"
            },
            glyphs: {
                type: "string"
            },
            "font-faces": {
                type: "fontFaces"
            },
            transition: {
                type: "transition"
            },
            layers: {
                required: !0,
                type: "array",
                value: "layer"
            }
        },
        sources: {
            "*": {
                type: "source"
            }
        },
        source: ["source_vector", "source_raster", "source_raster_dem", "source_geojson", "source_video", "source_image"],
        source_vector: {
            type: {
                required: !0,
                type: "enum",
                values: {
                    vector: {}
                }
            },
            url: {
                type: "string"
            },
            tiles: {
                type: "array",
                value: "string"
            },
            bounds: {
                type: "array",
                value: "number",
                length: 4,
            default:
                [-180, -85.051129, 180, 85.051129]
            },
            scheme: {
                type: "enum",
                values: {
                    xyz: {},
                    tms: {}
                },
            default:
                "xyz"
            },
            minzoom: {
                type: "number",
            default:
                0
            },
            maxzoom: {
                type: "number",
            default:
                22
            },
            attribution: {
                type: "string"
            },
            promoteId: {
                type: "promoteId"
            },
            volatile: {
                type: "boolean",
            default:
                !1
            },
            encoding: {
                type: "enum",
                values: {
                    mvt: {},
                    mlt: {}
                },
            default:
                "mvt"
            },
            "*": {
                type: "*"
            }
        },
        source_raster: {
            type: {
                required: !0,
                type: "enum",
                values: {
                    raster: {}
                }
            },
            url: {
                type: "string"
            },
            tiles: {
                type: "array",
                value: "string"
            },
            bounds: {
                type: "array",
                value: "number",
                length: 4,
            default:
                [-180, -85.051129, 180, 85.051129]
            },
            minzoom: {
                type: "number",
            default:
                0
            },
            maxzoom: {
                type: "number",
            default:
                22
            },
            tileSize: {
                type: "number",
            default:
                512,
                units: "pixels"
            },
            scheme: {
                type: "enum",
                values: {
                    xyz: {},
                    tms: {}
                },
            default:
                "xyz"
            },
            attribution: {
                type: "string"
            },
            volatile: {
                type: "boolean",
            default:
                !1
            },
            "*": {
                type: "*"
            }
        },
        source_raster_dem: {
            type: {
                required: !0,
                type: "enum",
                values: {
                    "raster-dem": {}
                }
            },
            url: {
                type: "string"
            },
            tiles: {
                type: "array",
                value: "string"
            },
            bounds: {
                type: "array",
                value: "number",
                length: 4,
            default:
                [-180, -85.051129, 180, 85.051129]
            },
            minzoom: {
                type: "number",
            default:
                0
            },
            maxzoom: {
                type: "number",
            default:
                22
            },
            tileSize: {
                type: "number",
            default:
                512,
                units: "pixels"
            },
            attribution: {
                type: "string"
            },
            encoding: {
                type: "enum",
                values: {
                    terrarium: {},
                    mapbox: {},
                    custom: {}
                },
            default:
                "mapbox"
            },
            redFactor: {
                type: "number",
            default:
                1
            },
            blueFactor: {
                type: "number",
            default:
                1
            },
            greenFactor: {
                type: "number",
            default:
                1
            },
            baseShift: {
                type: "number",
            default:
                0
            },
            volatile: {
                type: "boolean",
            default:
                !1
            },
            "*": {
                type: "*"
            }
        },
        source_geojson: {
            type: {
                required: !0,
                type: "enum",
                values: {
                    geojson: {}
                }
            },
            data: {
                required: !0,
                type: "*"
            },
            maxzoom: {
                type: "number",
            default:
                18
            },
            attribution: {
                type: "string"
            },
            buffer: {
                type: "number",
            default:
                128,
                maximum: 512,
                minimum: 0
            },
            filter: {
                type: "filter"
            },
            tolerance: {
                type: "number",
            default:
                .375
            },
            cluster: {
                type: "boolean",
            default:
                !1
            },
            clusterRadius: {
                type: "number",
            default:
                50,
                minimum: 0
            },
            clusterMaxZoom: {
                type: "number"
            },
            clusterMinPoints: {
                type: "number"
            },
            clusterProperties: {
                type: "*"
            },
            lineMetrics: {
                type: "boolean",
            default:
                !1
            },
            generateId: {
                type: "boolean",
            default:
                !1
            },
            promoteId: {
                type: "promoteId"
            }
        },
        source_video: {
            type: {
                required: !0,
                type: "enum",
                values: {
                    video: {}
                }
            },
            urls: {
                required: !0,
                type: "array",
                value: "string"
            },
            coordinates: {
                required: !0,
                type: "array",
                length: 4,
                value: {
                    type: "array",
                    length: 2,
                    value: "number"
                }
            }
        },
        source_image: {
            type: {
                required: !0,
                type: "enum",
                values: {
                    image: {}
                }
            },
            url: {
                required: !0,
                type: "string"
            },
            coordinates: {
                required: !0,
                type: "array",
                length: 4,
                value: {
                    type: "array",
                    length: 2,
                    value: "number"
                }
            }
        },
        layer: {
            id: {
                type: "string",
                required: !0
            },
            type: {
                type: "enum",
                values: {
                    fill: {},
                    line: {},
                    symbol: {},
                    circle: {},
                    heatmap: {},
                    "fill-extrusion": {},
                    raster: {},
                    hillshade: {},
                    "color-relief": {},
                    background: {}
                },
                required: !0
            },
            metadata: {
                type: "*"
            },
            source: {
                type: "string"
            },
            "source-layer": {
                type: "string"
            },
            minzoom: {
                type: "number",
                minimum: 0,
                maximum: 24
            },
            maxzoom: {
                type: "number",
                minimum: 0,
                maximum: 24
            },
            filter: {
                type: "filter"
            },
            layout: {
                type: "layout"
            },
            paint: {
                type: "paint"
            }
        },
        layout: ["layout_fill", "layout_line", "layout_circle", "layout_heatmap", "layout_fill-extrusion", "layout_symbol", "layout_raster", "layout_hillshade", "layout_color-relief", "layout_background"],
        layout_background: {
            visibility: {
                type: "enum",
                values: {
                    visible: {},
                    none: {}
                },
            default:
                "visible",
                expression: {
                    interpolated: !1,
                    parameters: ["global-state"]
                },
                "property-type": "data-constant"
            }
        },
        layout_fill: {
            "fill-sort-key": {
                type: "number",
                expression: {
                    interpolated: !1,
                    parameters: ["zoom", "feature"]
                },
                "property-type": "data-driven"
            },
            visibility: {
                type: "enum",
                values: {
                    visible: {},
                    none: {}
                },
            default:
                "visible",
                expression: {
                    interpolated: !1,
                    parameters: ["global-state"]
                },
                "property-type": "data-constant"
            }
        },
        layout_circle: {
            "circle-sort-key": {
                type: "number",
                expression: {
                    interpolated: !1,
                    parameters: ["zoom", "feature"]
                },
                "property-type": "data-driven"
            },
            visibility: {
                type: "enum",
                values: {
                    visible: {},
                    none: {}
                },
            default:
                "visible",
                expression: {
                    interpolated: !1,
                    parameters: ["global-state"]
                },
                "property-type": "data-constant"
            }
        },
        layout_heatmap: {
            visibility: {
                type: "enum",
                values: {
                    visible: {},
                    none: {}
                },
            default:
                "visible",
                expression: {
                    interpolated: !1,
                    parameters: ["global-state"]
                },
                "property-type": "data-constant"
            }
        },
        "layout_fill-extrusion": {
            visibility: {
                type: "enum",
                values: {
                    visible: {},
                    none: {}
                },
            default:
                "visible",
                expression: {
                    interpolated: !1,
                    parameters: ["global-state"]
                },
                "property-type": "data-constant"
            }
        },
        layout_line: {
            "line-cap": {
                type: "enum",
                values: {
                    butt: {},
                    round: {},
                    square: {}
                },
            default:
                "butt",
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "line-join": {
                type: "enum",
                values: {
                    bevel: {},
                    round: {},
                    miter: {}
                },
            default:
                "miter",
                expression: {
                    interpolated: !1,
                    parameters: ["zoom", "feature"]
                },
                "property-type": "data-driven"
            },
            "line-miter-limit": {
                type: "number",
            default:
                2,
                requires: [{
                        "line-join": "miter"
                    }
                ],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "line-round-limit": {
                type: "number",
            default:
                1.05,
                requires: [{
                        "line-join": "round"
                    }
                ],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "line-sort-key": {
                type: "number",
                expression: {
                    interpolated: !1,
                    parameters: ["zoom", "feature"]
                },
                "property-type": "data-driven"
            },
            visibility: {
                type: "enum",
                values: {
                    visible: {},
                    none: {}
                },
            default:
                "visible",
                expression: {
                    interpolated: !1,
                    parameters: ["global-state"]
                },
                "property-type": "data-constant"
            }
        },
        layout_symbol: {
            "symbol-placement": {
                type: "enum",
                values: {
                    point: {},
                    line: {},
                    "line-center": {}
                },
            default:
                "point",
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "symbol-spacing": {
                type: "number",
            default:
                250,
                minimum: 1,
                units: "pixels",
                requires: [{
                        "symbol-placement": "line"
                    }
                ],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "symbol-avoid-edges": {
                type: "boolean",
            default:
                !1,
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "symbol-sort-key": {
                type: "number",
                expression: {
                    interpolated: !1,
                    parameters: ["zoom", "feature"]
                },
                "property-type": "data-driven"
            },
            "symbol-z-order": {
                type: "enum",
                values: {
                    auto: {},
                    "viewport-y": {},
                    source: {}
                },
            default:
                "auto",
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "icon-allow-overlap": {
                type: "boolean",
            default:
                !1,
                requires: ["icon-image", {
                        "!": "icon-overlap"
                    }
                ],
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "icon-overlap": {
                type: "enum",
                values: {
                    never: {},
                    always: {},
                    cooperative: {}
                },
                requires: ["icon-image"],
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "icon-ignore-placement": {
                type: "boolean",
            default:
                !1,
                requires: ["icon-image"],
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "icon-optional": {
                type: "boolean",
            default:
                !1,
                requires: ["icon-image", "text-field"],
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "icon-rotation-alignment": {
                type: "enum",
                values: {
                    map: {},
                    viewport: {},
                    auto: {}
                },
            default:
                "auto",
                requires: ["icon-image"],
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "icon-size": {
                type: "number",
            default:
                1,
                minimum: 0,
                units: "factor of the original icon size",
                requires: ["icon-image"],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature"]
                },
                "property-type": "data-driven"
            },
            "icon-text-fit": {
                type: "enum",
                values: {
                    none: {},
                    width: {},
                    height: {},
                    both: {}
                },
            default:
                "none",
                requires: ["icon-image", "text-field"],
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "icon-text-fit-padding": {
                type: "array",
                value: "number",
                length: 4,
            default:
                [0, 0, 0, 0],
                units: "pixels",
                requires: ["icon-image", "text-field", {
                        "icon-text-fit": ["both", "width", "height"]
                    }
                ],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "icon-image": {
                type: "resolvedImage",
                tokens: !0,
                expression: {
                    interpolated: !1,
                    parameters: ["zoom", "feature"]
                },
                "property-type": "data-driven"
            },
            "icon-rotate": {
                type: "number",
            default:
                0,
                period: 360,
                units: "degrees",
                requires: ["icon-image"],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature"]
                },
                "property-type": "data-driven"
            },
            "icon-padding": {
                type: "padding",
            default:
                [2],
                units: "pixels",
                requires: ["icon-image"],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature"]
                },
                "property-type": "data-driven"
            },
            "icon-keep-upright": {
                type: "boolean",
            default:
                !1,
                requires: ["icon-image", {
                        "icon-rotation-alignment": "map"
                    }, {
                        "symbol-placement": ["line", "line-center"]
                    }
                ],
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "icon-offset": {
                type: "array",
                value: "number",
                length: 2,
            default:
                [0, 0],
                requires: ["icon-image"],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature"]
                },
                "property-type": "data-driven"
            },
            "icon-anchor": {
                type: "enum",
                values: {
                    center: {},
                    left: {},
                    right: {},
                    top: {},
                    bottom: {},
                    "top-left": {},
                    "top-right": {},
                    "bottom-left": {},
                    "bottom-right": {}
                },
            default:
                "center",
                requires: ["icon-image"],
                expression: {
                    interpolated: !1,
                    parameters: ["zoom", "feature"]
                },
                "property-type": "data-driven"
            },
            "icon-pitch-alignment": {
                type: "enum",
                values: {
                    map: {},
                    viewport: {},
                    auto: {}
                },
            default:
                "auto",
                requires: ["icon-image"],
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "text-pitch-alignment": {
                type: "enum",
                values: {
                    map: {},
                    viewport: {},
                    auto: {}
                },
            default:
                "auto",
                requires: ["text-field"],
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "text-rotation-alignment": {
                type: "enum",
                values: {
                    map: {},
                    viewport: {},
                    "viewport-glyph": {},
                    auto: {}
                },
            default:
                "auto",
                requires: ["text-field"],
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "text-field": {
                type: "formatted",
            default:
                "",
                tokens: !0,
                expression: {
                    interpolated: !1,
                    parameters: ["zoom", "feature"]
                },
                "property-type": "data-driven"
            },
            "text-font": {
                type: "array",
                value: "string",
            default:
                ["Open Sans Regular", "Arial Unicode MS Regular"],
                requires: ["text-field"],
                expression: {
                    interpolated: !1,
                    parameters: ["zoom", "feature"]
                },
                "property-type": "data-driven"
            },
            "text-size": {
                type: "number",
            default:
                16,
                minimum: 0,
                units: "pixels",
                requires: ["text-field"],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature"]
                },
                "property-type": "data-driven"
            },
            "text-max-width": {
                type: "number",
            default:
                10,
                minimum: 0,
                units: "ems",
                requires: ["text-field"],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature"]
                },
                "property-type": "data-driven"
            },
            "text-line-height": {
                type: "number",
            default:
                1.2,
                units: "ems",
                requires: ["text-field"],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "text-letter-spacing": {
                type: "number",
            default:
                0,
                units: "ems",
                requires: ["text-field"],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature"]
                },
                "property-type": "data-driven"
            },
            "text-justify": {
                type: "enum",
                values: {
                    auto: {},
                    left: {},
                    center: {},
                    right: {}
                },
            default:
                "center",
                requires: ["text-field"],
                expression: {
                    interpolated: !1,
                    parameters: ["zoom", "feature"]
                },
                "property-type": "data-driven"
            },
            "text-radial-offset": {
                type: "number",
                units: "ems",
            default:
                0,
                requires: ["text-field"],
                "property-type": "data-driven",
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature"]
                }
            },
            "text-variable-anchor": {
                type: "array",
                value: "enum",
                values: {
                    center: {},
                    left: {},
                    right: {},
                    top: {},
                    bottom: {},
                    "top-left": {},
                    "top-right": {},
                    "bottom-left": {},
                    "bottom-right": {}
                },
                requires: ["text-field", {
                        "symbol-placement": ["point"]
                    }
                ],
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "text-variable-anchor-offset": {
                type: "variableAnchorOffsetCollection",
                requires: ["text-field", {
                        "symbol-placement": ["point"]
                    }
                ],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature"]
                },
                "property-type": "data-driven"
            },
            "text-anchor": {
                type: "enum",
                values: {
                    center: {},
                    left: {},
                    right: {},
                    top: {},
                    bottom: {},
                    "top-left": {},
                    "top-right": {},
                    "bottom-left": {},
                    "bottom-right": {}
                },
            default:
                "center",
                requires: ["text-field", {
                        "!": "text-variable-anchor"
                    }
                ],
                expression: {
                    interpolated: !1,
                    parameters: ["zoom", "feature"]
                },
                "property-type": "data-driven"
            },
            "text-max-angle": {
                type: "number",
            default:
                45,
                units: "degrees",
                requires: ["text-field", {
                        "symbol-placement": ["line", "line-center"]
                    }
                ],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "text-writing-mode": {
                type: "array",
                value: "enum",
                values: {
                    horizontal: {},
                    vertical: {}
                },
                requires: ["text-field", {
                        "symbol-placement": ["point"]
                    }
                ],
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "text-rotate": {
                type: "number",
            default:
                0,
                period: 360,
                units: "degrees",
                requires: ["text-field"],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature"]
                },
                "property-type": "data-driven"
            },
            "text-padding": {
                type: "number",
            default:
                2,
                minimum: 0,
                units: "pixels",
                requires: ["text-field"],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "text-keep-upright": {
                type: "boolean",
            default:
                !0,
                requires: ["text-field", {
                        "text-rotation-alignment": "map"
                    }, {
                        "symbol-placement": ["line", "line-center"]
                    }
                ],
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "text-transform": {
                type: "enum",
                values: {
                    none: {},
                    uppercase: {},
                    lowercase: {}
                },
            default:
                "none",
                requires: ["text-field"],
                expression: {
                    interpolated: !1,
                    parameters: ["zoom", "feature"]
                },
                "property-type": "data-driven"
            },
            "text-offset": {
                type: "array",
                value: "number",
                units: "ems",
                length: 2,
            default:
                [0, 0],
                requires: ["text-field", {
                        "!": "text-radial-offset"
                    }
                ],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature"]
                },
                "property-type": "data-driven"
            },
            "text-allow-overlap": {
                type: "boolean",
            default:
                !1,
                requires: ["text-field", {
                        "!": "text-overlap"
                    }
                ],
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "text-overlap": {
                type: "enum",
                values: {
                    never: {},
                    always: {},
                    cooperative: {}
                },
                requires: ["text-field"],
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "text-ignore-placement": {
                type: "boolean",
            default:
                !1,
                requires: ["text-field"],
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "text-optional": {
                type: "boolean",
            default:
                !1,
                requires: ["text-field", "icon-image"],
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            visibility: {
                type: "enum",
                values: {
                    visible: {},
                    none: {}
                },
            default:
                "visible",
                expression: {
                    interpolated: !1,
                    parameters: ["global-state"]
                },
                "property-type": "data-constant"
            }
        },
        layout_raster: {
            visibility: {
                type: "enum",
                values: {
                    visible: {},
                    none: {}
                },
            default:
                "visible",
                expression: {
                    interpolated: !1,
                    parameters: ["global-state"]
                },
                "property-type": "data-constant"
            }
        },
        layout_hillshade: {
            visibility: {
                type: "enum",
                values: {
                    visible: {},
                    none: {}
                },
            default:
                "visible",
                expression: {
                    interpolated: !1,
                    parameters: ["global-state"]
                },
                "property-type": "data-constant"
            }
        },
        "layout_color-relief": {
            visibility: {
                type: "enum",
                values: {
                    visible: {},
                    none: {}
                },
            default:
                "visible",
                expression: {
                    interpolated: !1,
                    parameters: ["global-state"]
                },
                "property-type": "data-constant"
            }
        },
        filter: {
            type: "boolean",
            expression: {
                interpolated: !1,
                parameters: ["zoom", "feature"]
            },
            "property-type": "data-driven"
        },
        filter_operator: {
            type: "enum",
            values: {
                "==": {},
                "!=": {},
                ">": {},
                ">=": {},
                "<": {},
                "<=": {},
                in: {},
                "!in": {},
                all: {},
                any: {},
                none: {},
                has: {},
                "!has": {}
            }
        },
        geometry_type: {
            type: "enum",
            values: {
                Point: {},
                LineString: {},
                Polygon: {}
            }
        },
        function : {
            expression: {
                type: "expression"
            },
            stops: {
                type: "array",
                value: "function_stop"
            },
            base: {
                type: "number",
            default:
                1,
                minimum: 0
            },
            property: {
                type: "string",
            default:
                "$zoom"
            },
            type: {
                type: "enum",
                values: {
                    identity: {},
                    exponential: {},
                    interval: {},
                    categorical: {}
                },
            default:
                "exponential"
            },
            colorSpace: {
                type: "enum",
                values: {
                    rgb: {},
                    lab: {},
                    hcl: {}
                },
            default:
                "rgb"
            },
        default: {
                type: "*",
                required: !1
            }
        },
        function_stop: {
            type: "array",
            minimum: 0,
            maximum: 24,
            value: ["number", "color"],
            length: 2
        },
        expression: {
            type: "array",
            value: "expression_name",
            minimum: 1
        },
        light: {
            anchor: {
                type: "enum",
            default:
                "viewport",
                values: {
                    map: {},
                    viewport: {}
                },
                "property-type": "data-constant",
                transition: !1,
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                }
            },
            position: {
                type: "array",
            default:
                [1.15, 210, 30],
                length: 3,
                value: "number",
                "property-type": "data-constant",
                transition: !0,
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                }
            },
            color: {
                type: "color",
                "property-type": "data-constant",
            default:
                "#ffffff",
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                transition: !0
            },
            intensity: {
                type: "number",
                "property-type": "data-constant",
            default:
                .5,
                minimum: 0,
                maximum: 1,
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                transition: !0
            }
        },
        sky: {
            "sky-color": {
                type: "color",
                "property-type": "data-constant",
            default:
                "#88C6FC",
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                transition: !0
            },
            "horizon-color": {
                type: "color",
                "property-type": "data-constant",
            default:
                "#ffffff",
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                transition: !0
            },
            "fog-color": {
                type: "color",
                "property-type": "data-constant",
            default:
                "#ffffff",
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                transition: !0
            },
            "fog-ground-blend": {
                type: "number",
                "property-type": "data-constant",
            default:
                .5,
                minimum: 0,
                maximum: 1,
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                transition: !0
            },
            "horizon-fog-blend": {
                type: "number",
                "property-type": "data-constant",
            default:
                .8,
                minimum: 0,
                maximum: 1,
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                transition: !0
            },
            "sky-horizon-blend": {
                type: "number",
                "property-type": "data-constant",
            default:
                .8,
                minimum: 0,
                maximum: 1,
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                transition: !0
            },
            "atmosphere-blend": {
                type: "number",
                "property-type": "data-constant",
            default:
                .8,
                minimum: 0,
                maximum: 1,
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                transition: !0
            }
        },
        terrain: {
            source: {
                type: "string",
                required: !0
            },
            exaggeration: {
                type: "number",
                minimum: 0,
            default:
                1
            }
        },
        projection: {
            type: {
                type: "projectionDefinition",
            default:
                "mercator",
                "property-type": "data-constant",
                transition: !1,
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                }
            }
        },
        paint: ["paint_fill", "paint_line", "paint_circle", "paint_heatmap", "paint_fill-extrusion", "paint_symbol", "paint_raster", "paint_hillshade", "paint_color-relief", "paint_background"],
        paint_fill: {
            "fill-antialias": {
                type: "boolean",
            default:
                !0,
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "fill-opacity": {
                type: "number",
            default:
                1,
                minimum: 0,
                maximum: 1,
                transition: !0,
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature", "feature-state"]
                },
                "property-type": "data-driven"
            },
            "fill-color": {
                type: "color",
            default:
                "#000000",
                transition: !0,
                requires: [{
                        "!": "fill-pattern"
                    }
                ],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature", "feature-state"]
                },
                "property-type": "data-driven"
            },
            "fill-outline-color": {
                type: "color",
                transition: !0,
                requires: [{
                        "!": "fill-pattern"
                    }, {
                        "fill-antialias": !0
                    }
                ],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature", "feature-state"]
                },
                "property-type": "data-driven"
            },
            "fill-translate": {
                type: "array",
                value: "number",
                length: 2,
            default:
                [0, 0],
                transition: !0,
                units: "pixels",
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "fill-translate-anchor": {
                type: "enum",
                values: {
                    map: {},
                    viewport: {}
                },
            default:
                "map",
                requires: ["fill-translate"],
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "fill-pattern": {
                type: "resolvedImage",
                transition: !0,
                expression: {
                    interpolated: !1,
                    parameters: ["zoom", "feature"]
                },
                "property-type": "cross-faded-data-driven"
            }
        },
        "paint_fill-extrusion": {
            "fill-extrusion-opacity": {
                type: "number",
            default:
                1,
                minimum: 0,
                maximum: 1,
                transition: !0,
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "fill-extrusion-color": {
                type: "color",
            default:
                "#000000",
                transition: !0,
                requires: [{
                        "!": "fill-extrusion-pattern"
                    }
                ],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature", "feature-state"]
                },
                "property-type": "data-driven"
            },
            "fill-extrusion-translate": {
                type: "array",
                value: "number",
                length: 2,
            default:
                [0, 0],
                transition: !0,
                units: "pixels",
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "fill-extrusion-translate-anchor": {
                type: "enum",
                values: {
                    map: {},
                    viewport: {}
                },
            default:
                "map",
                requires: ["fill-extrusion-translate"],
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "fill-extrusion-pattern": {
                type: "resolvedImage",
                transition: !0,
                expression: {
                    interpolated: !1,
                    parameters: ["zoom", "feature"]
                },
                "property-type": "cross-faded-data-driven"
            },
            "fill-extrusion-height": {
                type: "number",
            default:
                0,
                minimum: 0,
                units: "meters",
                transition: !0,
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature", "feature-state"]
                },
                "property-type": "data-driven"
            },
            "fill-extrusion-base": {
                type: "number",
            default:
                0,
                minimum: 0,
                units: "meters",
                transition: !0,
                requires: ["fill-extrusion-height"],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature", "feature-state"]
                },
                "property-type": "data-driven"
            },
            "fill-extrusion-vertical-gradient": {
                type: "boolean",
            default:
                !0,
                transition: !1,
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            }
        },
        paint_line: {
            "line-opacity": {
                type: "number",
            default:
                1,
                minimum: 0,
                maximum: 1,
                transition: !0,
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature", "feature-state"]
                },
                "property-type": "data-driven"
            },
            "line-color": {
                type: "color",
            default:
                "#000000",
                transition: !0,
                requires: [{
                        "!": "line-pattern"
                    }
                ],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature", "feature-state"]
                },
                "property-type": "data-driven"
            },
            "line-translate": {
                type: "array",
                value: "number",
                length: 2,
            default:
                [0, 0],
                transition: !0,
                units: "pixels",
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "line-translate-anchor": {
                type: "enum",
                values: {
                    map: {},
                    viewport: {}
                },
            default:
                "map",
                requires: ["line-translate"],
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "line-width": {
                type: "number",
            default:
                1,
                minimum: 0,
                transition: !0,
                units: "pixels",
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature", "feature-state"]
                },
                "property-type": "data-driven"
            },
            "line-gap-width": {
                type: "number",
            default:
                0,
                minimum: 0,
                transition: !0,
                units: "pixels",
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature", "feature-state"]
                },
                "property-type": "data-driven"
            },
            "line-offset": {
                type: "number",
            default:
                0,
                transition: !0,
                units: "pixels",
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature", "feature-state"]
                },
                "property-type": "data-driven"
            },
            "line-blur": {
                type: "number",
            default:
                0,
                minimum: 0,
                transition: !0,
                units: "pixels",
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature", "feature-state"]
                },
                "property-type": "data-driven"
            },
            "line-dasharray": {
                type: "array",
                value: "number",
                minimum: 0,
                transition: !0,
                units: "line widths",
                requires: [{
                        "!": "line-pattern"
                    }
                ],
                expression: {
                    interpolated: !1,
                    parameters: ["zoom", "feature"]
                },
                "property-type": "cross-faded-data-driven"
            },
            "line-pattern": {
                type: "resolvedImage",
                transition: !0,
                expression: {
                    interpolated: !1,
                    parameters: ["zoom", "feature"]
                },
                "property-type": "cross-faded-data-driven"
            },
            "line-gradient": {
                type: "color",
                transition: !1,
                requires: [{
                        "!": "line-dasharray"
                    }, {
                        "!": "line-pattern"
                    }, {
                        source: "geojson",
                        has: {
                            lineMetrics: !0
                        }
                    }
                ],
                expression: {
                    interpolated: !0,
                    parameters: ["line-progress"]
                },
                "property-type": "color-ramp"
            }
        },
        paint_circle: {
            "circle-radius": {
                type: "number",
            default:
                5,
                minimum: 0,
                transition: !0,
                units: "pixels",
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature", "feature-state"]
                },
                "property-type": "data-driven"
            },
            "circle-color": {
                type: "color",
            default:
                "#000000",
                transition: !0,
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature", "feature-state"]
                },
                "property-type": "data-driven"
            },
            "circle-blur": {
                type: "number",
            default:
                0,
                transition: !0,
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature", "feature-state"]
                },
                "property-type": "data-driven"
            },
            "circle-opacity": {
                type: "number",
            default:
                1,
                minimum: 0,
                maximum: 1,
                transition: !0,
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature", "feature-state"]
                },
                "property-type": "data-driven"
            },
            "circle-translate": {
                type: "array",
                value: "number",
                length: 2,
            default:
                [0, 0],
                transition: !0,
                units: "pixels",
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "circle-translate-anchor": {
                type: "enum",
                values: {
                    map: {},
                    viewport: {}
                },
            default:
                "map",
                requires: ["circle-translate"],
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "circle-pitch-scale": {
                type: "enum",
                values: {
                    map: {},
                    viewport: {}
                },
            default:
                "map",
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "circle-pitch-alignment": {
                type: "enum",
                values: {
                    map: {},
                    viewport: {}
                },
            default:
                "viewport",
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "circle-stroke-width": {
                type: "number",
            default:
                0,
                minimum: 0,
                transition: !0,
                units: "pixels",
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature", "feature-state"]
                },
                "property-type": "data-driven"
            },
            "circle-stroke-color": {
                type: "color",
            default:
                "#000000",
                transition: !0,
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature", "feature-state"]
                },
                "property-type": "data-driven"
            },
            "circle-stroke-opacity": {
                type: "number",
            default:
                1,
                minimum: 0,
                maximum: 1,
                transition: !0,
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature", "feature-state"]
                },
                "property-type": "data-driven"
            }
        },
        paint_heatmap: {
            "heatmap-radius": {
                type: "number",
            default:
                30,
                minimum: 1,
                transition: !0,
                units: "pixels",
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature", "feature-state"]
                },
                "property-type": "data-driven"
            },
            "heatmap-weight": {
                type: "number",
            default:
                1,
                minimum: 0,
                transition: !1,
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature", "feature-state"]
                },
                "property-type": "data-driven"
            },
            "heatmap-intensity": {
                type: "number",
            default:
                1,
                minimum: 0,
                transition: !0,
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "heatmap-color": {
                type: "color",
            default:
                ["interpolate", ["linear"], ["heatmap-density"], 0, "rgba(0, 0, 255, 0)", .1, "royalblue", .3, "cyan", .5, "lime", .7, "yellow", 1, "red"],
                transition: !1,
                expression: {
                    interpolated: !0,
                    parameters: ["heatmap-density"]
                },
                "property-type": "color-ramp"
            },
            "heatmap-opacity": {
                type: "number",
            default:
                1,
                minimum: 0,
                maximum: 1,
                transition: !0,
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            }
        },
        paint_symbol: {
            "icon-opacity": {
                type: "number",
            default:
                1,
                minimum: 0,
                maximum: 1,
                transition: !0,
                requires: ["icon-image"],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature", "feature-state"]
                },
                "property-type": "data-driven"
            },
            "icon-color": {
                type: "color",
            default:
                "#000000",
                transition: !0,
                requires: ["icon-image"],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature", "feature-state"]
                },
                "property-type": "data-driven"
            },
            "icon-halo-color": {
                type: "color",
            default:
                "rgba(0, 0, 0, 0)",
                transition: !0,
                requires: ["icon-image"],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature", "feature-state"]
                },
                "property-type": "data-driven"
            },
            "icon-halo-width": {
                type: "number",
            default:
                0,
                minimum: 0,
                transition: !0,
                units: "pixels",
                requires: ["icon-image"],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature", "feature-state"]
                },
                "property-type": "data-driven"
            },
            "icon-halo-blur": {
                type: "number",
            default:
                0,
                minimum: 0,
                transition: !0,
                units: "pixels",
                requires: ["icon-image"],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature", "feature-state"]
                },
                "property-type": "data-driven"
            },
            "icon-translate": {
                type: "array",
                value: "number",
                length: 2,
            default:
                [0, 0],
                transition: !0,
                units: "pixels",
                requires: ["icon-image"],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "icon-translate-anchor": {
                type: "enum",
                values: {
                    map: {},
                    viewport: {}
                },
            default:
                "map",
                requires: ["icon-image", "icon-translate"],
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "text-opacity": {
                type: "number",
            default:
                1,
                minimum: 0,
                maximum: 1,
                transition: !0,
                requires: ["text-field"],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature", "feature-state"]
                },
                "property-type": "data-driven"
            },
            "text-color": {
                type: "color",
            default:
                "#000000",
                transition: !0,
                overridable: !0,
                requires: ["text-field"],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature", "feature-state"]
                },
                "property-type": "data-driven"
            },
            "text-halo-color": {
                type: "color",
            default:
                "rgba(0, 0, 0, 0)",
                transition: !0,
                requires: ["text-field"],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature", "feature-state"]
                },
                "property-type": "data-driven"
            },
            "text-halo-width": {
                type: "number",
            default:
                0,
                minimum: 0,
                transition: !0,
                units: "pixels",
                requires: ["text-field"],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature", "feature-state"]
                },
                "property-type": "data-driven"
            },
            "text-halo-blur": {
                type: "number",
            default:
                0,
                minimum: 0,
                transition: !0,
                units: "pixels",
                requires: ["text-field"],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom", "feature", "feature-state"]
                },
                "property-type": "data-driven"
            },
            "text-translate": {
                type: "array",
                value: "number",
                length: 2,
            default:
                [0, 0],
                transition: !0,
                units: "pixels",
                requires: ["text-field"],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "text-translate-anchor": {
                type: "enum",
                values: {
                    map: {},
                    viewport: {}
                },
            default:
                "map",
                requires: ["text-field", "text-translate"],
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            }
        },
        paint_raster: {
            "raster-opacity": {
                type: "number",
            default:
                1,
                minimum: 0,
                maximum: 1,
                transition: !0,
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "raster-hue-rotate": {
                type: "number",
            default:
                0,
                period: 360,
                transition: !0,
                units: "degrees",
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "raster-brightness-min": {
                type: "number",
            default:
                0,
                minimum: 0,
                maximum: 1,
                transition: !0,
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "raster-brightness-max": {
                type: "number",
            default:
                1,
                minimum: 0,
                maximum: 1,
                transition: !0,
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "raster-saturation": {
                type: "number",
            default:
                0,
                minimum: -1,
                maximum: 1,
                transition: !0,
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "raster-contrast": {
                type: "number",
            default:
                0,
                minimum: -1,
                maximum: 1,
                transition: !0,
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "raster-resampling": {
                type: "enum",
                values: {
                    linear: {},
                    nearest: {}
                },
            default:
                "linear",
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "raster-fade-duration": {
                type: "number",
            default:
                300,
                minimum: 0,
                transition: !1,
                units: "milliseconds",
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            }
        },
        paint_hillshade: {
            "hillshade-illumination-direction": {
                type: "numberArray",
            default:
                335,
                minimum: 0,
                maximum: 359,
                transition: !1,
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "hillshade-illumination-altitude": {
                type: "numberArray",
            default:
                45,
                minimum: 0,
                maximum: 90,
                transition: !1,
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "hillshade-illumination-anchor": {
                type: "enum",
                values: {
                    map: {},
                    viewport: {}
                },
            default:
                "viewport",
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "hillshade-exaggeration": {
                type: "number",
            default:
                .5,
                minimum: 0,
                maximum: 1,
                transition: !0,
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "hillshade-shadow-color": {
                type: "colorArray",
            default:
                "#000000",
                transition: !0,
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "hillshade-highlight-color": {
                type: "colorArray",
            default:
                "#FFFFFF",
                transition: !0,
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "hillshade-accent-color": {
                type: "color",
            default:
                "#000000",
                transition: !0,
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "hillshade-method": {
                type: "enum",
                values: {
                    standard: {},
                    basic: {},
                    combined: {},
                    igor: {},
                    multidirectional: {}
                },
            default:
                "standard",
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            }
        },
        "paint_color-relief": {
            "color-relief-opacity": {
                type: "number",
            default:
                1,
                minimum: 0,
                maximum: 1,
                transition: !0,
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "color-relief-color": {
                type: "color",
                transition: !1,
                expression: {
                    interpolated: !0,
                    parameters: ["elevation"]
                },
                "property-type": "color-ramp"
            }
        },
        paint_background: {
            "background-color": {
                type: "color",
            default:
                "#000000",
                transition: !0,
                requires: [{
                        "!": "background-pattern"
                    }
                ],
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            },
            "background-pattern": {
                type: "resolvedImage",
                transition: !0,
                expression: {
                    interpolated: !1,
                    parameters: ["zoom"]
                },
                "property-type": "cross-faded"
            },
            "background-opacity": {
                type: "number",
            default:
                1,
                minimum: 0,
                maximum: 1,
                transition: !0,
                expression: {
                    interpolated: !0,
                    parameters: ["zoom"]
                },
                "property-type": "data-constant"
            }
        },
        transition: {
            duration: {
                type: "number",
            default:
                300,
                minimum: 0,
                units: "milliseconds"
            },
            delay: {
                type: "number",
            default:
                0,
                minimum: 0,
                units: "milliseconds"
            }
        },
        "property-type": {
            "data-driven": {
                type: "property-type"
            },
            "cross-faded": {
                type: "property-type"
            },
            "cross-faded-data-driven": {
                type: "property-type"
            },
            "color-ramp": {
                type: "property-type"
            },
            "data-constant": {
                type: "property-type"
            },
            constant: {
                type: "property-type"
            }
        },
        promoteId: {
            "*": {
                type: "string"
            }
        },
        interpolation: {
            type: "array",
            value: "interpolation_name",
            minimum: 1
        },
        interpolation_name: {
            type: "enum",
            values: {
                linear: {
                    syntax: {
                        overloads: [{
                                parameters: [],
                                "output-type": "interpolation"
                            }
                        ],
                        parameters: []
                    }
                },
                exponential: {
                    syntax: {
                        overloads: [{
                                parameters: ["base"],
                                "output-type": "interpolation"
                            }
                        ],
                        parameters: [{
                                name: "base",
                                type: "number literal"
                            }
                        ]
                    }
                },
                "cubic-bezier": {
                    syntax: {
                        overloads: [{
                                parameters: ["x1", "y1", "x2", "y2"],
                                "output-type": "interpolation"
                            }
                        ],
                        parameters: [{
                                name: "x1",
                                type: "number literal"
                            }, {
                                name: "y1",
                                type: "number literal"
                            }, {
                                name: "x2",
                                type: "number literal"
                            }, {
                                name: "y2",
                                type: "number literal"
                            }
                        ]
                    }
                }
            }
        }
    };
    const L = ["type", "source", "source-layer", "minzoom", "maxzoom", "filter", "layout"];
    function D(e, t) {
        const r = {};
        for (const t in e)
            "ref" !== t && (r[t] = e[t]);
        return L.forEach(e => {
            e in t && (r[e] = t[e])
        }),
        r
    }
    function U(e) {
        e = e.slice();
        const t = Object.create(null);
        for (let r = 0; r < e.length; r++)
            t[e[r].id] = e[r];
        for (let r = 0; r < e.length; r++)
            "ref" in e[r] && (e[r] = D(e[r], t[e[r].ref]));
        return e
    }
    class G extends Error {
        constructor(e, t) {
            super(t),
            this.message = t,
            this.key = e
        }
    }
    class V {
        constructor(e, t = []) {
            this.parent = e,
            this.bindings = {};
            for (const [e, r] of t)
                this.bindings[e] = r
        }
        concat(e) {
            return new V(this, e)
        }
        get(e) {
            if (this.bindings[e])
                return this.bindings[e];
            if (this.parent)
                return this.parent.get(e);
            throw new Error(`${e} not found in scope.`)
        }
        has(e) {
            return !!this.bindings[e] || !!this.parent && this.parent.has(e)
        }
    }
    const J = {
        kind: "null"
    },
    W = {
        kind: "number"
    },
    Z = {
        kind: "string"
    },
    B = {
        kind: "boolean"
    },
    H = {
        kind: "color"
    },
    X = {
        kind: "projectionDefinition"
    },
    K = {
        kind: "object"
    },
    Y = {
        kind: "value"
    },
    Q = {
        kind: "collator"
    },
    ee = {
        kind: "formatted"
    },
    te = {
        kind: "padding"
    },
    re = {
        kind: "colorArray"
    },
    ne = {
        kind: "numberArray"
    },
    oe = {
        kind: "resolvedImage"
    },
    ae = {
        kind: "variableAnchorOffsetCollection"
    };
    function ie(e, t) {
        return {
            kind: "array",
            itemType: e,
            N: t
        }
    }
    function se(e) {
        if ("array" === e.kind) {
            const t = se(e.itemType);
            return "number" == typeof e.N ? `array<${t}, ${e.N}>` : "value" === e.itemType.kind ? "array" : `array<${t}>`
        }
        return e.kind
    }
    const le = [J, W, Z, B, H, X, ee, K, ie(Y), te, ne, re, oe, ae];
    function ue(e, t) {
        if ("error" === t.kind)
            return null;
        if ("array" === e.kind) {
            if ("array" === t.kind && (0 === t.N && "value" === t.itemType.kind || !ue(e.itemType, t.itemType)) && ("number" != typeof e.N || e.N === t.N))
                return null
        } else {
            if (e.kind === t.kind)
                return null;
            if ("value" === e.kind)
                for (const e of le)
                    if (!ue(e, t))
                        return null
        }
        return `Expected ${se(e)} but found ${se(t)} instead.`
    }
    function ce(e, t) {
        return t.some(t => t.kind === e.kind)
    }
    function pe(e, t) {
        return t.some(t => "null" === t ? null === e : "array" === t ? Array.isArray(e) : "object" === t ? e && !Array.isArray(e) && "object" == typeof e : t === typeof e)
    }
    function fe(e, t) {
        return "array" === e.kind && "array" === t.kind ? e.itemType.kind === t.itemType.kind && "number" == typeof e.N : e.kind === t.kind
    }
    const de = .96422,
    me = .82521,
    ye = 4 / 29,
    he = 6 / 29,
    ge = 3 * he * he,
    be = he * he * he,
    ve = Math.PI / 180,
    xe = 180 / Math.PI;
    function we(e) {
        return (e %= 360) < 0 && (e += 360),
        e
    }
    function ke([e, t, r, n]) {
        let o,
        a;
        const i = ze((.2225045 * (e = Me(e)) + .7168786 * (t = Me(t)) + .0606169 * (r = Me(r))) / 1);
        e === t && t === r ? o = a = i : (o = ze((.4360747 * e + .3850649 * t + .1430804 * r) / de), a = ze((.0139322 * e + .0971045 * t + .7141733 * r) / me));
        const s = 116 * i - 16;
        return [s < 0 ? 0 : s, 500 * (o - i), 200 * (i - a), n]
    }
    function Me(e) {
        return e <= .04045 ? e / 12.92 : Math.pow((e + .055) / 1.055, 2.4)
    }
    function ze(e) {
        return e > be ? Math.pow(e, 1 / 3) : e / ge + ye
    }
    function Se([e, t, r, n]) {
        let o = (e + 16) / 116,
        a = isNaN(t) ? o : o + t / 500,
        i = isNaN(r) ? o : o - r / 200;
        return o = 1 * Ae(o),
        a = de * Ae(a),
        i = me * Ae(i),
        [je(3.1338561 * a - 1.6168667 * o - .4906146 * i), je( - .9787684 * a + 1.9161415 * o + .033454 * i), je(.0719453 * a - .2289914 * o + 1.4052427 * i), n]
    }
    function je(e) {
        return (e = e <= .00304 ? 12.92 * e : 1.055 * Math.pow(e, 1 / 2.4) - .055) < 0 ? 0 : e > 1 ? 1 : e
    }
    function Ae(e) {
        return e > he ? e * e * e : ge * (e - ye)
    }
    const Ee = Object.hasOwn || function (e, t) {
        return Object.prototype.hasOwnProperty.call(e, t)
    };
    function qe(e, t) {
        return Ee(e, t) ? e[t] : void 0
    }
    function $e(e) {
        if ("transparent" === (e = e.toLowerCase().trim()))
            return [0, 0, 0, 0];
        const t = qe(Ne, e);
        if (t) {
            const [e, r, n] = t;
            return [e / 255, r / 255, n / 255, 1]
        }
        if (e.startsWith("#")) {
            if (/^#(?:[0-9a-f]{3,4}|[0-9a-f]{6}|[0-9a-f]{8})$/.test(e)) {
                const t = e.length < 6 ? 1 : 2;
                let r = 1;
                return [Ce(e.slice(r, r += t)), Ce(e.slice(r, r += t)), Ce(e.slice(r, r += t)), Ce(e.slice(r, r + t) || "ff")]
            }
        }
        if (e.startsWith("rgb")) {
            const t = /^rgba?\(\s*([\de.+-]+)(%)?(?:\s+|\s*(,)\s*)([\de.+-]+)(%)?(?:\s+|\s*(,)\s*)([\de.+-]+)(%)?(?:\s*([,\/])\s*([\de.+-]+)(%)?)?\s*\)$/,
            r = e.match(t);
            if (r) {
                const [e, t, n, o, a, i, s, l, u, c, p, f] = r,
                d = [o || " ", s || " ", c].join("");
                if ("  " === d || "  /" === d || ",," === d || ",,," === d) {
                    const e = [n, i, u].join(""),
                    r = "%%%" === e ? 100 : "" === e ? 255 : 0;
                    if (r) {
                        const e = [Te(+t / r, 0, 1), Te(+a / r, 0, 1), Te(+l / r, 0, 1), p ? _e(+p, f) : 1];
                        if (Oe(e))
                            return e
                    }
                }
                return
            }
        }
        const r = e.match(/^hsla?\(\s*([\de.+-]+)(?:deg)?(?:\s+|\s*(,)\s*)([\de.+-]+)%(?:\s+|\s*(,)\s*)([\de.+-]+)%(?:\s*([,\/])\s*([\de.+-]+)(%)?)?\s*\)$/);
        if (r) {
            const [e, t, n, o, a, i, s, l, u] = r,
            c = [n || " ", a || " ", s].join("");
            if ("  " === c || "  /" === c || ",," === c || ",,," === c) {
                const e = [+t, Te(+o, 0, 100), Te(+i, 0, 100), l ? _e(+l, u) : 1];
                if (Oe(e))
                    return function ([e, t, r, n]) {
                        function o(n) {
                            const o = (n + e / 30) % 12,
                            a = t * Math.min(r, 1 - r);
                            return r - a * Math.max(-1, Math.min(o - 3, 9 - o, 1))
                        }
                        return e = we(e),
                        t /= 100,
                        r /= 100,
                        [o(0), o(8), o(4), n]
                    }
                (e)
            }
        }
    }
    function Ce(e) {
        return parseInt(e.padEnd(2, e), 16) / 255
    }
    function _e(e, t) {
        return Te(t ? e / 100 : e, 0, 1)
    }
    function Te(e, t, r) {
        return Math.min(Math.max(t, e), r)
    }
    function Oe(e) {
        return !e.some(Number.isNaN)
    }
    const Ne = {
        aliceblue: [240, 248, 255],
        antiquewhite: [250, 235, 215],
        aqua: [0, 255, 255],
        aquamarine: [127, 255, 212],
        azure: [240, 255, 255],
        beige: [245, 245, 220],
        bisque: [255, 228, 196],
        black: [0, 0, 0],
        blanchedalmond: [255, 235, 205],
        blue: [0, 0, 255],
        blueviolet: [138, 43, 226],
        brown: [165, 42, 42],
        burlywood: [222, 184, 135],
        cadetblue: [95, 158, 160],
        chartreuse: [127, 255, 0],
        chocolate: [210, 105, 30],
        coral: [255, 127, 80],
        cornflowerblue: [100, 149, 237],
        cornsilk: [255, 248, 220],
        crimson: [220, 20, 60],
        cyan: [0, 255, 255],
        darkblue: [0, 0, 139],
        darkcyan: [0, 139, 139],
        darkgoldenrod: [184, 134, 11],
        darkgray: [169, 169, 169],
        darkgreen: [0, 100, 0],
        darkgrey: [169, 169, 169],
        darkkhaki: [189, 183, 107],
        darkmagenta: [139, 0, 139],
        darkolivegreen: [85, 107, 47],
        darkorange: [255, 140, 0],
        darkorchid: [153, 50, 204],
        darkred: [139, 0, 0],
        darksalmon: [233, 150, 122],
        darkseagreen: [143, 188, 143],
        darkslateblue: [72, 61, 139],
        darkslategray: [47, 79, 79],
        darkslategrey: [47, 79, 79],
        darkturquoise: [0, 206, 209],
        darkviolet: [148, 0, 211],
        deeppink: [255, 20, 147],
        deepskyblue: [0, 191, 255],
        dimgray: [105, 105, 105],
        dimgrey: [105, 105, 105],
        dodgerblue: [30, 144, 255],
        firebrick: [178, 34, 34],
        floralwhite: [255, 250, 240],
        forestgreen: [34, 139, 34],
        fuchsia: [255, 0, 255],
        gainsboro: [220, 220, 220],
        ghostwhite: [248, 248, 255],
        gold: [255, 215, 0],
        goldenrod: [218, 165, 32],
        gray: [128, 128, 128],
        green: [0, 128, 0],
        greenyellow: [173, 255, 47],
        grey: [128, 128, 128],
        honeydew: [240, 255, 240],
        hotpink: [255, 105, 180],
        indianred: [205, 92, 92],
        indigo: [75, 0, 130],
        ivory: [255, 255, 240],
        khaki: [240, 230, 140],
        lavender: [230, 230, 250],
        lavenderblush: [255, 240, 245],
        lawngreen: [124, 252, 0],
        lemonchiffon: [255, 250, 205],
        lightblue: [173, 216, 230],
        lightcoral: [240, 128, 128],
        lightcyan: [224, 255, 255],
        lightgoldenrodyellow: [250, 250, 210],
        lightgray: [211, 211, 211],
        lightgreen: [144, 238, 144],
        lightgrey: [211, 211, 211],
        lightpink: [255, 182, 193],
        lightsalmon: [255, 160, 122],
        lightseagreen: [32, 178, 170],
        lightskyblue: [135, 206, 250],
        lightslategray: [119, 136, 153],
        lightslategrey: [119, 136, 153],
        lightsteelblue: [176, 196, 222],
        lightyellow: [255, 255, 224],
        lime: [0, 255, 0],
        limegreen: [50, 205, 50],
        linen: [250, 240, 230],
        magenta: [255, 0, 255],
        maroon: [128, 0, 0],
        mediumaquamarine: [102, 205, 170],
        mediumblue: [0, 0, 205],
        mediumorchid: [186, 85, 211],
        mediumpurple: [147, 112, 219],
        mediumseagreen: [60, 179, 113],
        mediumslateblue: [123, 104, 238],
        mediumspringgreen: [0, 250, 154],
        mediumturquoise: [72, 209, 204],
        mediumvioletred: [199, 21, 133],
        midnightblue: [25, 25, 112],
        mintcream: [245, 255, 250],
        mistyrose: [255, 228, 225],
        moccasin: [255, 228, 181],
        navajowhite: [255, 222, 173],
        navy: [0, 0, 128],
        oldlace: [253, 245, 230],
        olive: [128, 128, 0],
        olivedrab: [107, 142, 35],
        orange: [255, 165, 0],
        orangered: [255, 69, 0],
        orchid: [218, 112, 214],
        palegoldenrod: [238, 232, 170],
        palegreen: [152, 251, 152],
        paleturquoise: [175, 238, 238],
        palevioletred: [219, 112, 147],
        papayawhip: [255, 239, 213],
        peachpuff: [255, 218, 185],
        peru: [205, 133, 63],
        pink: [255, 192, 203],
        plum: [221, 160, 221],
        powderblue: [176, 224, 230],
        purple: [128, 0, 128],
        rebeccapurple: [102, 51, 153],
        red: [255, 0, 0],
        rosybrown: [188, 143, 143],
        royalblue: [65, 105, 225],
        saddlebrown: [139, 69, 19],
        salmon: [250, 128, 114],
        sandybrown: [244, 164, 96],
        seagreen: [46, 139, 87],
        seashell: [255, 245, 238],
        sienna: [160, 82, 45],
        silver: [192, 192, 192],
        skyblue: [135, 206, 235],
        slateblue: [106, 90, 205],
        slategray: [112, 128, 144],
        slategrey: [112, 128, 144],
        snow: [255, 250, 250],
        springgreen: [0, 255, 127],
        steelblue: [70, 130, 180],
        tan: [210, 180, 140],
        teal: [0, 128, 128],
        thistle: [216, 191, 216],
        tomato: [255, 99, 71],
        turquoise: [64, 224, 208],
        violet: [238, 130, 238],
        wheat: [245, 222, 179],
        white: [255, 255, 255],
        whitesmoke: [245, 245, 245],
        yellow: [255, 255, 0],
        yellowgreen: [154, 205, 50]
    };
    function Pe(e, t, r) {
        return e + r * (t - e)
    }
    function Ie(e, t, r) {
        return e.map((e, n) => Pe(e, t[n], r))
    }
    class Fe {
        constructor(e, t, r, n = 1, o = !0) {
            this.r = e,
            this.g = t,
            this.b = r,
            this.a = n,
            o || (this.r *= n, this.g *= n, this.b *= n, n || this.overwriteGetter("rgb", [e, t, r, n]))
        }
        static parse(e) {
            if (e instanceof Fe)
                return e;
            if ("string" != typeof e)
                return;
            const t = $e(e);
            return t ? new Fe(...t, !1) : void 0
        }
        get rgb() {
            const {
                r: e,
                g: t,
                b: r,
                a: n
            } = this,
            o = n || 1 / 0;
            return this.overwriteGetter("rgb", [e / o, t / o, r / o, n])
        }
        get hcl() {
            return this.overwriteGetter("hcl", function (e) {
                const [t, r, n, o] = ke(e),
                a = Math.sqrt(r * r + n * n);
                return [Math.round(1e4 * a) ? we(Math.atan2(n, r) * xe) : NaN, a, t, o]
            }
                (this.rgb))
        }
        get lab() {
            return this.overwriteGetter("lab", ke(this.rgb))
        }
        overwriteGetter(e, t) {
            return Object.defineProperty(this, e, {
                value: t
            }),
            t
        }
        toString() {
            const [e, t, r, n] = this.rgb;
            return `rgba(${[e, t, r].map(e => Math.round(255 * e)).join(",")},${n})`
        }
        static interpolate(e, t, r, n = "rgb") {
            switch (n) {
            case "rgb": {
                    const [n, o, a, i] = Ie(e.rgb, t.rgb, r);
                    return new Fe(n, o, a, i, !1)
                }
            case "hcl": {
                    const [n, o, a, i] = e.hcl,
                    [s, l, u, c] = t.hcl;
                    let p,
                    f;
                    if (isNaN(n) || isNaN(s))
                        isNaN(n) ? isNaN(s) ? p = NaN : (p = s, 1 !== a && 0 !== a || (f = l)) : (p = n, 1 !== u && 0 !== u || (f = o));
                    else {
                        let e = s - n;
                        s > n && e > 180 ? e -= 360 : s < n && n - s > 180 && (e += 360),
                        p = n + r * e
                    }
                    const [d, m, y, h] = function ([e, t, r, n]) {
                        return e = isNaN(e) ? 0 : e * ve,
                        Se([r, Math.cos(e) * t, Math.sin(e) * t, n])
                    }
                    ([p, null != f ? f : Pe(o, l, r), Pe(a, u, r), Pe(i, c, r)]);
                    return new Fe(d, m, y, h, !1)
                }
            case "lab": {
                    const [n, o, a, i] = Se(Ie(e.lab, t.lab, r));
                    return new Fe(n, o, a, i, !1)
                }
            }
        }
    }
    Fe.black = new Fe(0, 0, 0, 1),
    Fe.white = new Fe(1, 1, 1, 1),
    Fe.transparent = new Fe(0, 0, 0, 0),
    Fe.red = new Fe(1, 0, 0, 1);
    class Re {
        constructor(e, t, r) {
            this.sensitivity = e ? t ? "variant" : "case" : t ? "accent" : "base",
            this.locale = r,
            this.collator = new Intl.Collator(this.locale ? this.locale : [], {
                sensitivity: this.sensitivity,
                usage: "search"
            })
        }
        compare(e, t) {
            return this.collator.compare(e, t)
        }
        resolvedLocale() {
            return new Intl.Collator(this.locale ? this.locale : []).resolvedOptions().locale
        }
    }
    const Le = ["bottom", "center", "top"];
    class De {
        constructor(e, t, r, n, o, a) {
            this.text = e,
            this.image = t,
            this.scale = r,
            this.fontStack = n,
            this.textColor = o,
            this.verticalAlign = a
        }
    }
    class Ue {
        constructor(e) {
            this.sections = e
        }
        static fromString(e) {
            return new Ue([new De(e, null, null, null, null, null)])
        }
        isEmpty() {
            return 0 === this.sections.length || !this.sections.some(e => 0 !== e.text.length || e.image && 0 !== e.image.name.length)
        }
        static factory(e) {
            return e instanceof Ue ? e : Ue.fromString(e)
        }
        toString() {
            return 0 === this.sections.length ? "" : this.sections.map(e => e.text).join("")
        }
    }
    class Ge {
        constructor(e) {
            this.values = e.slice()
        }
        static parse(e) {
            if (e instanceof Ge)
                return e;
            if ("number" == typeof e)
                return new Ge([e, e, e, e]);
            if (Array.isArray(e) && !(e.length < 1 || e.length > 4)) {
                for (const t of e)
                    if ("number" != typeof t)
                        return;
                switch (e.length) {
                case 1:
                    e = [e[0], e[0], e[0], e[0]];
                    break;
                case 2:
                    e = [e[0], e[1], e[0], e[1]];
                    break;
                case 3:
                    e = [e[0], e[1], e[2], e[1]]
                }
                return new Ge(e)
            }
        }
        toString() {
            return JSON.stringify(this.values)
        }
        static interpolate(e, t, r) {
            return new Ge(Ie(e.values, t.values, r))
        }
    }
    class Ve {
        constructor(e) {
            this.values = e.slice()
        }
        static parse(e) {
            if (e instanceof Ve)
                return e;
            if ("number" == typeof e)
                return new Ve([e]);
            if (Array.isArray(e)) {
                for (const t of e)
                    if ("number" != typeof t)
                        return;
                return new Ve(e)
            }
        }
        toString() {
            return JSON.stringify(this.values)
        }
        static interpolate(e, t, r) {
            return new Ve(Ie(e.values, t.values, r))
        }
    }
    class Je {
        constructor(e) {
            this.values = e.slice()
        }
        static parse(e) {
            if (e instanceof Je)
                return e;
            if ("string" == typeof e) {
                const t = Fe.parse(e);
                if (!t)
                    return;
                return new Je([t])
            }
            if (!Array.isArray(e))
                return;
            const t = [];
            for (const r of e) {
                if ("string" != typeof r)
                    return;
                const e = Fe.parse(r);
                if (!e)
                    return;
                t.push(e)
            }
            return new Je(t)
        }
        toString() {
            return JSON.stringify(this.values)
        }
        static interpolate(e, t, r, n = "rgb") {
            const o = [];
            if (e.values.length != t.values.length)
                throw new Error(`colorArray: Arrays have mismatched length (${e.values.length} vs. ${t.values.length}), cannot interpolate.`);
            for (let a = 0; a < e.values.length; a++)
                o.push(Fe.interpolate(e.values[a], t.values[a], r, n));
            return new Je(o)
        }
    }
    class We extends Error {
        constructor(e) {
            super(e),
            this.name = "RuntimeError"
        }
        toJSON() {
            return this.message
        }
    }
    const Ze = new Set(["center", "left", "right", "top", "bottom", "top-left", "top-right", "bottom-left", "bottom-right"]);
    class Be {
        constructor(e) {
            this.values = e.slice()
        }
        static parse(e) {
            if (e instanceof Be)
                return e;
            if (Array.isArray(e) && !(e.length < 1) && e.length % 2 == 0) {
                for (let t = 0; t < e.length; t += 2) {
                    const r = e[t],
                    n = e[t + 1];
                    if ("string" != typeof r || !Ze.has(r))
                        return;
                    if (!Array.isArray(n) || 2 !== n.length || "number" != typeof n[0] || "number" != typeof n[1])
                        return
                }
                return new Be(e)
            }
        }
        toString() {
            return JSON.stringify(this.values)
        }
        static interpolate(e, t, r) {
            const n = e.values,
            o = t.values;
            if (n.length !== o.length)
                throw new We(`Cannot interpolate values of different length. from: ${e.toString()}, to: ${t.toString()}`);
            const a = [];
            for (let e = 0; e < n.length; e += 2) {
                if (n[e] !== o[e])
                    throw new We(`Cannot interpolate values containing mismatched anchors. from[${e}]: ${n[e]}, to[${e}]: ${o[e]}`);
                a.push(n[e]);
                const [t, i] = n[e + 1],
                [s, l] = o[e + 1];
                a.push([Pe(t, s, r), Pe(i, l, r)])
            }
            return new Be(a)
        }
    }
    class He {
        constructor(e) {
            this.name = e.name,
            this.available = e.available
        }
        toString() {
            return this.name
        }
        static fromString(e) {
            return e ? new He({
                name: e,
                available: !1
            }) : null
        }
    }
    class Xe {
        constructor(e, t, r) {
            this.from = e,
            this.to = t,
            this.transition = r
        }
        static interpolate(e, t, r) {
            return new Xe(e, t, r)
        }
        static parse(e) {
            return e instanceof Xe ? e : Array.isArray(e) && 3 === e.length && "string" == typeof e[0] && "string" == typeof e[1] && "number" == typeof e[2] ? new Xe(e[0], e[1], e[2]) : "object" == typeof e && "string" == typeof e.from && "string" == typeof e.to && "number" == typeof e.transition ? new Xe(e.from, e.to, e.transition) : "string" == typeof e ? new Xe(e, e, 1) : void 0
        }
    }
    function Ke(e, t, r, n) {
        if (!("number" == typeof e && e >= 0 && e <= 255 && "number" == typeof t && t >= 0 && t <= 255 && "number" == typeof r && r >= 0 && r <= 255)) {
            return `Invalid rgba value [${("number" == typeof n ? [e, t, r, n] : [e, t, r]).join(", ")}]: 'r', 'g', and 'b' must be between 0 and 255.`
        }
        return void 0 === n || "number" == typeof n && n >= 0 && n <= 1 ? null : `Invalid rgba value [${[e, t, r, n].join(", ")}]: 'a' must be between 0 and 1.`
    }
    function Ye(e) {
        if (null === e || "string" == typeof e || "boolean" == typeof e || "number" == typeof e || e instanceof Xe || e instanceof Fe || e instanceof Re || e instanceof Ue || e instanceof Ge || e instanceof Ve || e instanceof Je || e instanceof Be || e instanceof He)
            return !0;
        if (Array.isArray(e)) {
            for (const t of e)
                if (!Ye(t))
                    return !1;
            return !0
        }
        if ("object" == typeof e) {
            for (const t in e)
                if (!Ye(e[t]))
                    return !1;
            return !0
        }
        return !1
    }
    function Qe(e) {
        if (null === e)
            return J;
        if ("string" == typeof e)
            return Z;
        if ("boolean" == typeof e)
            return B;
        if ("number" == typeof e)
            return W;
        if (e instanceof Fe)
            return H;
        if (e instanceof Xe)
            return X;
        if (e instanceof Re)
            return Q;
        if (e instanceof Ue)
            return ee;
        if (e instanceof Ge)
            return te;
        if (e instanceof Ve)
            return ne;
        if (e instanceof Je)
            return re;
        if (e instanceof Be)
            return ae;
        if (e instanceof He)
            return oe;
        if (Array.isArray(e)) {
            const t = e.length;
            let r;
            for (const t of e) {
                const e = Qe(t);
                if (r) {
                    if (r === e)
                        continue;
                    r = Y;
                    break
                }
                r = e
            }
            return ie(r || Y, t)
        }
        return K
    }
    function et(e) {
        const t = typeof e;
        return null === e ? "" : "string" === t || "number" === t || "boolean" === t ? String(e) : e instanceof Fe || e instanceof Xe || e instanceof Ue || e instanceof Ge || e instanceof Ve || e instanceof Je || e instanceof Be || e instanceof He ? e.toString() : JSON.stringify(e)
    }
    class tt {
        constructor(e, t) {
            this.type = e,
            this.value = t
        }
        static parse(e, t) {
            if (2 !== e.length)
                return t.error(`'literal' expression requires exactly one argument, but found ${e.length - 1} instead.`);
            if (!Ye(e[1]))
                return t.error("invalid value");
            const r = e[1];
            let n = Qe(r);
            const o = t.expectedType;
            return "array" !== n.kind || 0 !== n.N || !o || "array" !== o.kind || "number" == typeof o.N && 0 !== o.N || (n = o),
            new tt(n, r)
        }
        evaluate() {
            return this.value
        }
        eachChild() {}
        outputDefined() {
            return !0
        }
    }
    const rt = {
        string: Z,
        number: W,
        boolean: B,
        object: K
    };
    class nt {
        constructor(e, t) {
            this.type = e,
            this.args = t
        }
        static parse(e, t) {
            if (e.length < 2)
                return t.error("Expected at least one argument.");
            let r,
            n = 1;
            const o = e[0];
            if ("array" === o) {
                let o,
                a;
                if (e.length > 2) {
                    const r = e[1];
                    if ("string" != typeof r || !(r in rt) || "object" === r)
                        return t.error('The item type argument of "array" must be one of string, number, boolean', 1);
                    o = rt[r],
                    n++
                } else
                    o = Y;
                if (e.length > 3) {
                    if (null !== e[2] && ("number" != typeof e[2] || e[2] < 0 || e[2] !== Math.floor(e[2])))
                        return t.error('The length argument to "array" must be a positive integer literal', 2);
                    a = e[2],
                    n++
                }
                r = ie(o, a)
            } else {
                if (!rt[o])
                    throw new Error(`Types doesn't contain name = ${o}`);
                r = rt[o]
            }
            const a = [];
            for (; n < e.length; n++) {
                const r = t.parse(e[n], n, Y);
                if (!r)
                    return null;
                a.push(r)
            }
            return new nt(r, a)
        }
        evaluate(e) {
            for (let t = 0; t < this.args.length; t++) {
                const r = this.args[t].evaluate(e);
                if (!ue(this.type, Qe(r)))
                    return r;
                if (t === this.args.length - 1)
                    throw new We(`Expected value to be of type ${se(this.type)}, but found ${se(Qe(r))} instead.`)
            }
            throw new Error
        }
        eachChild(e) {
            this.args.forEach(e)
        }
        outputDefined() {
            return this.args.every(e => e.outputDefined())
        }
    }
    const ot = {
        "to-boolean": B,
        "to-color": H,
        "to-number": W,
        "to-string": Z
    };
    class at {
        constructor(e, t) {
            this.type = e,
            this.args = t
        }
        static parse(e, t) {
            if (e.length < 2)
                return t.error("Expected at least one argument.");
            const r = e[0];
            if (!ot[r])
                throw new Error(`Can't parse ${r} as it is not part of the known types`);
            if (("to-boolean" === r || "to-string" === r) && 2 !== e.length)
                return t.error("Expected one argument.");
            const n = ot[r],
            o = [];
            for (let r = 1; r < e.length; r++) {
                const n = t.parse(e[r], r, Y);
                if (!n)
                    return null;
                o.push(n)
            }
            return new at(n, o)
        }
        evaluate(e) {
            switch (this.type.kind) {
            case "boolean":
                return Boolean(this.args[0].evaluate(e));
            case "color": {
                    let t,
                    r;
                    for (const n of this.args) {
                        if (t = n.evaluate(e), r = null, t instanceof Fe)
                            return t;
                        if ("string" == typeof t) {
                            const r = e.parseColor(t);
                            if (r)
                                return r
                        } else if (Array.isArray(t) && (r = t.length < 3 || t.length > 4 ? `Invalid rgba value ${JSON.stringify(t)}: expected an array containing either three or four numeric values.` : Ke(t[0], t[1], t[2], t[3]), !r))
                            return new Fe(t[0] / 255, t[1] / 255, t[2] / 255, t[3])
                    }
                    throw new We(r || `Could not parse color from value '${"string" == typeof t ? t : JSON.stringify(t)}'`)
                }
            case "padding": {
                    let t;
                    for (const r of this.args) {
                        t = r.evaluate(e);
                        const n = Ge.parse(t);
                        if (n)
                            return n
                    }
                    throw new We(`Could not parse padding from value '${"string" == typeof t ? t : JSON.stringify(t)}'`)
                }
            case "numberArray": {
                    let t;
                    for (const r of this.args) {
                        t = r.evaluate(e);
                        const n = Ve.parse(t);
                        if (n)
                            return n
                    }
                    throw new We(`Could not parse numberArray from value '${"string" == typeof t ? t : JSON.stringify(t)}'`)
                }
            case "colorArray": {
                    let t;
                    for (const r of this.args) {
                        t = r.evaluate(e);
                        const n = Je.parse(t);
                        if (n)
                            return n
                    }
                    throw new We(`Could not parse colorArray from value '${"string" == typeof t ? t : JSON.stringify(t)}'`)
                }
            case "variableAnchorOffsetCollection": {
                    let t;
                    for (const r of this.args) {
                        t = r.evaluate(e);
                        const n = Be.parse(t);
                        if (n)
                            return n
                    }
                    throw new We(`Could not parse variableAnchorOffsetCollection from value '${"string" == typeof t ? t : JSON.stringify(t)}'`)
                }
            case "number": {
                    let t = null;
                    for (const r of this.args) {
                        if (t = r.evaluate(e), null === t)
                            return 0;
                        const n = Number(t);
                        if (!isNaN(n))
                            return n
                    }
                    throw new We(`Could not convert ${JSON.stringify(t)} to number.`)
                }
            case "formatted":
                return Ue.fromString(et(this.args[0].evaluate(e)));
            case "resolvedImage":
                return He.fromString(et(this.args[0].evaluate(e)));
            case "projectionDefinition":
                return this.args[0].evaluate(e);
            default:
                return et(this.args[0].evaluate(e))
            }
        }
        eachChild(e) {
            this.args.forEach(e)
        }
        outputDefined() {
            return this.args.every(e => e.outputDefined())
        }
    }
    const it = ["Unknown", "Point", "LineString", "Polygon"];
    class st {
        constructor() {
            this.globals = null,
            this.feature = null,
            this.featureState = null,
            this.formattedSection = null,
            this._parseColorCache = new Map,
            this.availableImages = null,
            this.canonical = null
        }
        id() {
            return this.feature && "id" in this.feature ? this.feature.id : null
        }
        geometryType() {
            return this.feature ? "number" == typeof this.feature.type ? it[this.feature.type] : this.feature.type : null
        }
        geometry() {
            return this.feature && "geometry" in this.feature ? this.feature.geometry : null
        }
        canonicalID() {
            return this.canonical
        }
        properties() {
            return this.feature && this.feature.properties || {}
        }
        parseColor(e) {
            let t = this._parseColorCache.get(e);
            return t || (t = Fe.parse(e), this._parseColorCache.set(e, t)),
            t
        }
    }
    class lt {
        constructor(e, t, r = [], n, o = new V, a = []) {
            this.registry = e,
            this.path = r,
            this.key = r.map(e => `[${e}]`).join(""),
            this.scope = o,
            this.errors = a,
            this.expectedType = n,
            this._isConstant = t
        }
        parse(e, t, r, n, o = {}) {
            return t ? this.concat(t, r, n)._parse(e, o) : this._parse(e, o)
        }
        _parse(e, t) {
            function r(e, t, r) {
                return "assert" === r ? new nt(t, [e]) : "coerce" === r ? new at(t, [e]) : e
            }
            if (null !== e && "string" != typeof e && "boolean" != typeof e && "number" != typeof e || (e = ["literal", e]), Array.isArray(e)) {
                if (0 === e.length)
                    return this.error('Expected an array with at least one element. If you wanted a literal array, use ["literal", []].');
                const n = e[0];
                if ("string" != typeof n)
                    return this.error(`Expression name must be a string, but found ${typeof n} instead. If you wanted a literal array, use ["literal", [...]].`, 0), null;
                const o = this.registry[n];
                if (o) {
                    let n = o.parse(e, this);
                    if (!n)
                        return null;
                    if (this.expectedType) {
                        const e = this.expectedType,
                        o = n.type;
                        if ("string" !== e.kind && "number" !== e.kind && "boolean" !== e.kind && "object" !== e.kind && "array" !== e.kind || "value" !== o.kind) {
                            if ("projectionDefinition" === e.kind && ["string", "array"].includes(o.kind) || ["color", "formatted", "resolvedImage"].includes(e.kind) && ["value", "string"].includes(o.kind) || ["padding", "numberArray"].includes(e.kind) && ["value", "number", "array"].includes(o.kind) || "colorArray" === e.kind && ["value", "string", "array"].includes(o.kind) || "variableAnchorOffsetCollection" === e.kind && ["value", "array"].includes(o.kind))
                                n = r(n, e, t.typeAnnotation || "coerce");
                            else if (this.checkSubtype(e, o))
                                return null
                        } else
                            n = r(n, e, t.typeAnnotation || "assert")
                    }
                    if (!(n instanceof tt) && "resolvedImage" !== n.type.kind && this._isConstant(n)) {
                        const e = new st;
                        try {
                            n = new tt(n.type, n.evaluate(e))
                        } catch (e) {
                            return this.error(e.message),
                            null
                        }
                    }
                    return n
                }
                return this.error(`Unknown expression "${n}". If you wanted a literal array, use ["literal", [...]].`, 0)
            }
            return void 0 === e ? this.error("'undefined' value invalid. Use null instead.") : "object" == typeof e ? this.error('Bare objects invalid. Use ["literal", {...}] instead.') : this.error(`Expected an array, but found ${typeof e} instead.`)
        }
        concat(e, t, r) {
            const n = "number" == typeof e ? this.path.concat(e) : this.path,
            o = r ? this.scope.concat(r) : this.scope;
            return new lt(this.registry, this._isConstant, n, t || null, o, this.errors)
        }
        error(e, ...t) {
            const r = `${this.key}${t.map(e => `[${e}]`).join("")}`;
            this.errors.push(new G(r, e))
        }
        checkSubtype(e, t) {
            const r = ue(e, t);
            return r && this.error(r),
            r
        }
    }
    class ut {
        constructor(e, t) {
            this.type = t.type,
            this.bindings = [].concat(e),
            this.result = t
        }
        evaluate(e) {
            return this.result.evaluate(e)
        }
        eachChild(e) {
            for (const t of this.bindings)
                e(t[1]);
            e(this.result)
        }
        static parse(e, t) {
            if (e.length < 4)
                return t.error(`Expected at least 3 arguments, but found ${e.length - 1} instead.`);
            const r = [];
            for (let n = 1; n < e.length - 1; n += 2) {
                const o = e[n];
                if ("string" != typeof o)
                    return t.error(`Expected string, but found ${typeof o} instead.`, n);
                if (/[^a-zA-Z0-9_]/.test(o))
                    return t.error("Variable names must contain only alphanumeric characters or '_'.", n);
                const a = t.parse(e[n + 1], n + 1);
                if (!a)
                    return null;
                r.push([o, a])
            }
            const n = t.parse(e[e.length - 1], e.length - 1, t.expectedType, r);
            return n ? new ut(r, n) : null
        }
        outputDefined() {
            return this.result.outputDefined()
        }
    }
    class ct {
        constructor(e, t) {
            this.type = t.type,
            this.name = e,
            this.boundExpression = t
        }
        static parse(e, t) {
            if (2 !== e.length || "string" != typeof e[1])
                return t.error("'var' expression requires exactly one string literal argument.");
            const r = e[1];
            return t.scope.has(r) ? new ct(r, t.scope.get(r)) : t.error(`Unknown variable "${r}". Make sure "${r}" has been bound in an enclosing "let" expression before using it.`, 1)
        }
        evaluate(e) {
            return this.boundExpression.evaluate(e)
        }
        eachChild() {}
        outputDefined() {
            return !1
        }
    }
    class pt {
        constructor(e, t, r) {
            this.type = e,
            this.index = t,
            this.input = r
        }
        static parse(e, t) {
            if (3 !== e.length)
                return t.error(`Expected 2 arguments, but found ${e.length - 1} instead.`);
            const r = t.parse(e[1], 1, W),
            n = t.parse(e[2], 2, ie(t.expectedType || Y));
            if (!r || !n)
                return null;
            const o = n.type;
            return new pt(o.itemType, r, n)
        }
        evaluate(e) {
            const t = this.index.evaluate(e),
            r = this.input.evaluate(e);
            if (t < 0)
                throw new We(`Array index out of bounds: ${t} < 0.`);
            if (t >= r.length)
                throw new We(`Array index out of bounds: ${t} > ${r.length - 1}.`);
            if (t !== Math.floor(t))
                throw new We(`Array index must be an integer, but found ${t} instead.`);
            return r[t]
        }
        eachChild(e) {
            e(this.index),
            e(this.input)
        }
        outputDefined() {
            return !1
        }
    }
    class ft {
        constructor(e, t) {
            this.type = B,
            this.needle = e,
            this.haystack = t
        }
        static parse(e, t) {
            if (3 !== e.length)
                return t.error(`Expected 2 arguments, but found ${e.length - 1} instead.`);
            const r = t.parse(e[1], 1, Y),
            n = t.parse(e[2], 2, Y);
            return r && n ? ce(r.type, [B, Z, W, J, Y]) ? new ft(r, n) : t.error(`Expected first argument to be of type boolean, string, number or null, but found ${se(r.type)} instead`) : null
        }
        evaluate(e) {
            const t = this.needle.evaluate(e),
            r = this.haystack.evaluate(e);
            if (!r)
                return !1;
            if (!pe(t, ["boolean", "string", "number", "null"]))
                throw new We(`Expected first argument to be of type boolean, string, number or null, but found ${se(Qe(t))} instead.`);
            if (!pe(r, ["string", "array"]))
                throw new We(`Expected second argument to be of type array or string, but found ${se(Qe(r))} instead.`);
            return r.indexOf(t) >= 0
        }
        eachChild(e) {
            e(this.needle),
            e(this.haystack)
        }
        outputDefined() {
            return !0
        }
    }
    class dt {
        constructor(e, t, r) {
            this.type = W,
            this.needle = e,
            this.haystack = t,
            this.fromIndex = r
        }
        static parse(e, t) {
            if (e.length <= 2 || e.length >= 5)
                return t.error(`Expected 2 or 3 arguments, but found ${e.length - 1} instead.`);
            const r = t.parse(e[1], 1, Y),
            n = t.parse(e[2], 2, Y);
            if (!r || !n)
                return null;
            if (!ce(r.type, [B, Z, W, J, Y]))
                return t.error(`Expected first argument to be of type boolean, string, number or null, but found ${se(r.type)} instead`);
            if (4 === e.length) {
                const o = t.parse(e[3], 3, W);
                return o ? new dt(r, n, o) : null
            }
            return new dt(r, n)
        }
        evaluate(e) {
            const t = this.needle.evaluate(e),
            r = this.haystack.evaluate(e);
            if (!pe(t, ["boolean", "string", "number", "null"]))
                throw new We(`Expected first argument to be of type boolean, string, number or null, but found ${se(Qe(t))} instead.`);
            let n;
            if (this.fromIndex && (n = this.fromIndex.evaluate(e)), pe(r, ["string"])) {
                const e = r.indexOf(t, n);
                return -1 === e ? -1 : [...r.slice(0, e)].length
            }
            if (pe(r, ["array"]))
                return r.indexOf(t, n);
            throw new We(`Expected second argument to be of type array or string, but found ${se(Qe(r))} instead.`)
        }
        eachChild(e) {
            e(this.needle),
            e(this.haystack),
            this.fromIndex && e(this.fromIndex)
        }
        outputDefined() {
            return !1
        }
    }
    class mt {
        constructor(e, t, r, n, o, a) {
            this.inputType = e,
            this.type = t,
            this.input = r,
            this.cases = n,
            this.outputs = o,
            this.otherwise = a
        }
        static parse(e, t) {
            if (e.length < 5)
                return t.error(`Expected at least 4 arguments, but found only ${e.length - 1}.`);
            if (e.length % 2 != 1)
                return t.error("Expected an even number of arguments.");
            let r,
            n;
            t.expectedType && "value" !== t.expectedType.kind && (n = t.expectedType);
            const o = {},
            a = [];
            for (let i = 2; i < e.length - 1; i += 2) {
                let s = e[i];
                const l = e[i + 1];
                Array.isArray(s) || (s = [s]);
                const u = t.concat(i);
                if (0 === s.length)
                    return u.error("Expected at least one branch label.");
                for (const e of s) {
                    if ("number" != typeof e && "string" != typeof e)
                        return u.error("Branch labels must be numbers or strings.");
                    if ("number" == typeof e && Math.abs(e) > Number.MAX_SAFE_INTEGER)
                        return u.error(`Branch labels must be integers no larger than ${Number.MAX_SAFE_INTEGER}.`);
                    if ("number" == typeof e && Math.floor(e) !== e)
                        return u.error("Numeric branch labels must be integer values.");
                    if (r) {
                        if (u.checkSubtype(r, Qe(e)))
                            return null
                    } else
                        r = Qe(e);
                    if (void 0 !== o[String(e)])
                        return u.error("Branch labels must be unique.");
                    o[String(e)] = a.length
                }
                const c = t.parse(l, i, n);
                if (!c)
                    return null;
                n = n || c.type,
                a.push(c)
            }
            const i = t.parse(e[1], 1, Y);
            if (!i)
                return null;
            const s = t.parse(e[e.length - 1], e.length - 1, n);
            return s ? "value" !== i.type.kind && t.concat(1).checkSubtype(r, i.type) ? null : new mt(r, n, i, o, a, s) : null
        }
        evaluate(e) {
            const t = this.input.evaluate(e);
            return (Qe(t) === this.inputType && this.outputs[this.cases[t]] || this.otherwise).evaluate(e)
        }
        eachChild(e) {
            e(this.input),
            this.outputs.forEach(e),
            e(this.otherwise)
        }
        outputDefined() {
            return this.outputs.every(e => e.outputDefined()) && this.otherwise.outputDefined()
        }
    }
    class yt {
        constructor(e, t, r) {
            this.type = e,
            this.branches = t,
            this.otherwise = r
        }
        static parse(e, t) {
            if (e.length < 4)
                return t.error(`Expected at least 3 arguments, but found only ${e.length - 1}.`);
            if (e.length % 2 != 0)
                return t.error("Expected an odd number of arguments.");
            let r;
            t.expectedType && "value" !== t.expectedType.kind && (r = t.expectedType);
            const n = [];
            for (let o = 1; o < e.length - 1; o += 2) {
                const a = t.parse(e[o], o, B);
                if (!a)
                    return null;
                const i = t.parse(e[o + 1], o + 1, r);
                if (!i)
                    return null;
                n.push([a, i]),
                r = r || i.type
            }
            const o = t.parse(e[e.length - 1], e.length - 1, r);
            if (!o)
                return null;
            if (!r)
                throw new Error("Can't infer output type");
            return new yt(r, n, o)
        }
        evaluate(e) {
            for (const [t, r] of this.branches)
                if (t.evaluate(e))
                    return r.evaluate(e);
            return this.otherwise.evaluate(e)
        }
        eachChild(e) {
            for (const [t, r] of this.branches)
                e(t), e(r);
            e(this.otherwise)
        }
        outputDefined() {
            return this.branches.every(([e, t]) => t.outputDefined()) && this.otherwise.outputDefined()
        }
    }
    class ht {
        constructor(e, t, r, n) {
            this.type = e,
            this.input = t,
            this.beginIndex = r,
            this.endIndex = n
        }
        static parse(e, t) {
            if (e.length <= 2 || e.length >= 5)
                return t.error(`Expected 2 or 3 arguments, but found ${e.length - 1} instead.`);
            const r = t.parse(e[1], 1, Y),
            n = t.parse(e[2], 2, W);
            if (!r || !n)
                return null;
            if (!ce(r.type, [ie(Y), Z, Y]))
                return t.error(`Expected first argument to be of type array or string, but found ${se(r.type)} instead`);
            if (4 === e.length) {
                const o = t.parse(e[3], 3, W);
                return o ? new ht(r.type, r, n, o) : null
            }
            return new ht(r.type, r, n)
        }
        evaluate(e) {
            const t = this.input.evaluate(e),
            r = this.beginIndex.evaluate(e);
            let n;
            if (this.endIndex && (n = this.endIndex.evaluate(e)), pe(t, ["string"]))
                return [...t].slice(r, n).join("");
            if (pe(t, ["array"]))
                return t.slice(r, n);
            throw new We(`Expected first argument to be of type array or string, but found ${se(Qe(t))} instead.`)
        }
        eachChild(e) {
            e(this.input),
            e(this.beginIndex),
            this.endIndex && e(this.endIndex)
        }
        outputDefined() {
            return !1
        }
    }
    function gt(e, t) {
        const r = e.length - 1;
        let n,
        o,
        a = 0,
        i = r,
        s = 0;
        for (; a <= i; )
            if (s = Math.floor((a + i) / 2), n = e[s], o = e[s + 1], n <= t) {
                if (s === r || t < o)
                    return s;
                a = s + 1
            } else {
                if (!(n > t))
                    throw new We("Input is not a number.");
                i = s - 1
            }
        return 0
    }
    class bt {
        constructor(e, t, r) {
            this.type = e,
            this.input = t,
            this.labels = [],
            this.outputs = [];
            for (const [e, t] of r)
                this.labels.push(e), this.outputs.push(t)
        }
        static parse(e, t) {
            if (e.length - 1 < 4)
                return t.error(`Expected at least 4 arguments, but found only ${e.length - 1}.`);
            if ((e.length - 1) % 2 != 0)
                return t.error("Expected an even number of arguments.");
            const r = t.parse(e[1], 1, W);
            if (!r)
                return null;
            const n = [];
            let o = null;
            t.expectedType && "value" !== t.expectedType.kind && (o = t.expectedType);
            for (let r = 1; r < e.length; r += 2) {
                const a = 1 === r ? -1 / 0 : e[r],
                i = e[r + 1],
                s = r,
                l = r + 1;
                if ("number" != typeof a)
                    return t.error('Input/output pairs for "step" expressions must be defined using literal numeric values (not computed expressions) for the input values.', s);
                if (n.length && n[n.length - 1][0] >= a)
                    return t.error('Input/output pairs for "step" expressions must be arranged with input values in strictly ascending order.', s);
                const u = t.parse(i, l, o);
                if (!u)
                    return null;
                o = o || u.type,
                n.push([a, u])
            }
            return new bt(o, r, n)
        }
        evaluate(e) {
            const t = this.labels,
            r = this.outputs;
            if (1 === t.length)
                return r[0].evaluate(e);
            const n = this.input.evaluate(e);
            if (n <= t[0])
                return r[0].evaluate(e);
            const o = t.length;
            if (n >= t[o - 1])
                return r[o - 1].evaluate(e);
            return r[gt(t, n)].evaluate(e)
        }
        eachChild(e) {
            e(this.input);
            for (const t of this.outputs)
                e(t)
        }
        outputDefined() {
            return this.outputs.every(e => e.outputDefined())
        }
    }
    function vt(e) {
        return e && e.__esModule && Object.prototype.hasOwnProperty.call(e, "default") ? e.default : e
    }
    var xt,
    wt;
    var kt = function () {
        if (wt)
            return xt;
        function e(e, t, r, n) {
            this.cx = 3 * e,
            this.bx = 3 * (r - e) - this.cx,
            this.ax = 1 - this.cx - this.bx,
            this.cy = 3 * t,
            this.by = 3 * (n - t) - this.cy,
            this.ay = 1 - this.cy - this.by,
            this.p1x = e,
            this.p1y = t,
            this.p2x = r,
            this.p2y = n
        }
        return wt = 1,
        xt = e,
        e.prototype = {
            sampleCurveX: function (e) {
                return ((this.ax * e + this.bx) * e + this.cx) * e
            },
            sampleCurveY: function (e) {
                return ((this.ay * e + this.by) * e + this.cy) * e
            },
            sampleCurveDerivativeX: function (e) {
                return (3 * this.ax * e + 2 * this.bx) * e + this.cx
            },
            solveCurveX: function (e, t) {
                if (void 0 === t && (t = 1e-6), e < 0)
                    return 0;
                if (e > 1)
                    return 1;
                for (var r = e, n = 0; n < 8; n++) {
                    var o = this.sampleCurveX(r) - e;
                    if (Math.abs(o) < t)
                        return r;
                    var a = this.sampleCurveDerivativeX(r);
                    if (Math.abs(a) < 1e-6)
                        break;
                    r -= o / a
                }
                var i = 0,
                s = 1;
                for (r = e, n = 0; n < 20 && (o = this.sampleCurveX(r), !(Math.abs(o - e) < t)); n++)
                    e > o ? i = r : s = r, r = .5 * (s - i) + i;
                return r
            },
            solve: function (e, t) {
                return this.sampleCurveY(this.solveCurveX(e, t))
            }
        },
        xt
    }
    (),
    Mt = vt(kt);
    class zt {
        constructor(e, t, r, n, o) {
            this.type = e,
            this.operator = t,
            this.interpolation = r,
            this.input = n,
            this.labels = [],
            this.outputs = [];
            for (const [e, t] of o)
                this.labels.push(e), this.outputs.push(t)
        }
        static interpolationFactor(e, t, r, n) {
            let o = 0;
            if ("exponential" === e.name)
                o = St(t, e.base, r, n);
            else if ("linear" === e.name)
                o = St(t, 1, r, n);
            else if ("cubic-bezier" === e.name) {
                const a = e.controlPoints;
                o = new Mt(a[0], a[1], a[2], a[3]).solve(St(t, 1, r, n))
            }
            return o
        }
        static parse(e, t) {
            let [r, n, o, ...a] = e;
            if (!Array.isArray(n) || 0 === n.length)
                return t.error("Expected an interpolation type expression.", 1);
            if ("linear" === n[0])
                n = {
                    name: "linear"
                };
            else if ("exponential" === n[0]) {
                const e = n[1];
                if ("number" != typeof e)
                    return t.error("Exponential interpolation requires a numeric base.", 1, 1);
                n = {
                    name: "exponential",
                    base: e
                }
            } else {
                if ("cubic-bezier" !== n[0])
                    return t.error(`Unknown interpolation type ${String(n[0])}`, 1, 0); {
                    const e = n.slice(1);
                    if (4 !== e.length || e.some(e => "number" != typeof e || e < 0 || e > 1))
                        return t.error("Cubic bezier interpolation requires four numeric arguments with values between 0 and 1.", 1);
                    n = {
                        name: "cubic-bezier",
                        controlPoints: e
                    }
                }
            }
            if (e.length - 1 < 4)
                return t.error(`Expected at least 4 arguments, but found only ${e.length - 1}.`);
            if ((e.length - 1) % 2 != 0)
                return t.error("Expected an even number of arguments.");
            if (o = t.parse(o, 2, W), !o)
                return null;
            const i = [];
            let s = null;
            "interpolate-hcl" !== r && "interpolate-lab" !== r || t.expectedType == re ? t.expectedType && "value" !== t.expectedType.kind && (s = t.expectedType) : s = H;
            for (let e = 0; e < a.length; e += 2) {
                const r = a[e],
                n = a[e + 1],
                o = e + 3,
                l = e + 4;
                if ("number" != typeof r)
                    return t.error('Input/output pairs for "interpolate" expressions must be defined using literal numeric values (not computed expressions) for the input values.', o);
                if (i.length && i[i.length - 1][0] >= r)
                    return t.error('Input/output pairs for "interpolate" expressions must be arranged with input values in strictly ascending order.', o);
                const u = t.parse(n, l, s);
                if (!u)
                    return null;
                s = s || u.type,
                i.push([r, u])
            }
            return fe(s, W) || fe(s, X) || fe(s, H) || fe(s, te) || fe(s, ne) || fe(s, re) || fe(s, ae) || fe(s, ie(W)) ? new zt(s, r, n, o, i) : t.error(`Type ${se(s)} is not interpolatable.`)
        }
        evaluate(e) {
            const t = this.labels,
            r = this.outputs;
            if (1 === t.length)
                return r[0].evaluate(e);
            const n = this.input.evaluate(e);
            if (n <= t[0])
                return r[0].evaluate(e);
            const o = t.length;
            if (n >= t[o - 1])
                return r[o - 1].evaluate(e);
            const a = gt(t, n),
            i = t[a],
            s = t[a + 1],
            l = zt.interpolationFactor(this.interpolation, n, i, s),
            u = r[a].evaluate(e),
            c = r[a + 1].evaluate(e);
            switch (this.operator) {
            case "interpolate":
                switch (this.type.kind) {
                case "number":
                    return Pe(u, c, l);
                case "color":
                    return Fe.interpolate(u, c, l);
                case "padding":
                    return Ge.interpolate(u, c, l);
                case "colorArray":
                    return Je.interpolate(u, c, l);
                case "numberArray":
                    return Ve.interpolate(u, c, l);
                case "variableAnchorOffsetCollection":
                    return Be.interpolate(u, c, l);
                case "array":
                    return Ie(u, c, l);
                case "projectionDefinition":
                    return Xe.interpolate(u, c, l)
                }
            case "interpolate-hcl":
                switch (this.type.kind) {
                case "color":
                    return Fe.interpolate(u, c, l, "hcl");
                case "colorArray":
                    return Je.interpolate(u, c, l, "hcl")
                }
            case "interpolate-lab":
                switch (this.type.kind) {
                case "color":
                    return Fe.interpolate(u, c, l, "lab");
                case "colorArray":
                    return Je.interpolate(u, c, l, "lab")
                }
            }
        }
        eachChild(e) {
            e(this.input);
            for (const t of this.outputs)
                e(t)
        }
        outputDefined() {
            return this.outputs.every(e => e.outputDefined())
        }
    }
    function St(e, t, r, n) {
        const o = n - r,
        a = e - r;
        return 0 === o ? 0 : 1 === t ? a / o : (Math.pow(t, a) - 1) / (Math.pow(t, o) - 1)
    }
    class jt {
        constructor(e, t) {
            this.type = e,
            this.args = t
        }
        static parse(e, t) {
            if (e.length < 2)
                return t.error("Expected at least one argument.");
            let r = null;
            const n = t.expectedType;
            n && "value" !== n.kind && (r = n);
            const o = [];
            for (const n of e.slice(1)) {
                const e = t.parse(n, 1 + o.length, r, void 0, {
                    typeAnnotation: "omit"
                });
                if (!e)
                    return null;
                r = r || e.type,
                o.push(e)
            }
            if (!r)
                throw new Error("No output type");
            const a = n && o.some(e => ue(n, e.type));
            return new jt(a ? Y : r, o)
        }
        evaluate(e) {
            let t,
            r = null,
            n = 0;
            for (const o of this.args)
                if (n++, r = o.evaluate(e), r && r instanceof He && !r.available && (t || (t = r.name), r = null, n === this.args.length && (r = t)), null !== r)
                    break;
            return r
        }
        eachChild(e) {
            this.args.forEach(e)
        }
        outputDefined() {
            return this.args.every(e => e.outputDefined())
        }
    }
    function At(e, t) {
        return "==" === e || "!=" === e ? "boolean" === t.kind || "string" === t.kind || "number" === t.kind || "null" === t.kind || "value" === t.kind : "string" === t.kind || "number" === t.kind || "value" === t.kind
    }
    function Et(e, t, r, n) {
        return 0 === n.compare(t, r)
    }
    function qt(e, t, r) {
        const n = "==" !== e && "!=" !== e;
        return class o {
            constructor(e, t, r) {
                this.type = B,
                this.lhs = e,
                this.rhs = t,
                this.collator = r,
                this.hasUntypedArgument = "value" === e.type.kind || "value" === t.type.kind
            }
            static parse(e, t) {
                if (3 !== e.length && 4 !== e.length)
                    return t.error("Expected two or three arguments.");
                const r = e[0];
                let a = t.parse(e[1], 1, Y);
                if (!a)
                    return null;
                if (!At(r, a.type))
                    return t.concat(1).error(`"${r}" comparisons are not supported for type '${se(a.type)}'.`);
                let i = t.parse(e[2], 2, Y);
                if (!i)
                    return null;
                if (!At(r, i.type))
                    return t.concat(2).error(`"${r}" comparisons are not supported for type '${se(i.type)}'.`);
                if (a.type.kind !== i.type.kind && "value" !== a.type.kind && "value" !== i.type.kind)
                    return t.error(`Cannot compare types '${se(a.type)}' and '${se(i.type)}'.`);
                n && ("value" === a.type.kind && "value" !== i.type.kind ? a = new nt(i.type, [a]) : "value" !== a.type.kind && "value" === i.type.kind && (i = new nt(a.type, [i])));
                let s = null;
                if (4 === e.length) {
                    if ("string" !== a.type.kind && "string" !== i.type.kind && "value" !== a.type.kind && "value" !== i.type.kind)
                        return t.error("Cannot use collator to compare non-string types.");
                    if (s = t.parse(e[3], 3, Q), !s)
                        return null
                }
                return new o(a, i, s)
            }
            evaluate(o) {
                const a = this.lhs.evaluate(o),
                i = this.rhs.evaluate(o);
                if (n && this.hasUntypedArgument) {
                    const t = Qe(a),
                    r = Qe(i);
                    if (t.kind !== r.kind || "string" !== t.kind && "number" !== t.kind)
                        throw new We(`Expected arguments for "${e}" to be (string, string) or (number, number), but found (${t.kind}, ${r.kind}) instead.`)
                }
                if (this.collator && !n && this.hasUntypedArgument) {
                    const e = Qe(a),
                    r = Qe(i);
                    if ("string" !== e.kind || "string" !== r.kind)
                        return t(o, a, i)
                }
                return this.collator ? r(o, a, i, this.collator.evaluate(o)) : t(o, a, i)
            }
            eachChild(e) {
                e(this.lhs),
                e(this.rhs),
                this.collator && e(this.collator)
            }
            outputDefined() {
                return !0
            }
        }
    }
    const $t = qt("==", function (e, t, r) {
        return t === r
    }, Et),
    Ct = qt("!=", function (e, t, r) {
        return t !== r
    }, function (e, t, r, n) {
        return !Et(0, t, r, n)
    }),
    _t = qt("<", function (e, t, r) {
        return t < r
    }, function (e, t, r, n) {
        return n.compare(t, r) < 0
    }),
    Tt = qt(">", function (e, t, r) {
        return t > r
    }, function (e, t, r, n) {
        return n.compare(t, r) > 0
    }),
    Ot = qt("<=", function (e, t, r) {
        return t <= r
    }, function (e, t, r, n) {
        return n.compare(t, r) <= 0
    }),
    Nt = qt(">=", function (e, t, r) {
        return t >= r
    }, function (e, t, r, n) {
        return n.compare(t, r) >= 0
    });
    class Pt {
        constructor(e, t, r) {
            this.type = Q,
            this.locale = r,
            this.caseSensitive = e,
            this.diacriticSensitive = t
        }
        static parse(e, t) {
            if (2 !== e.length)
                return t.error("Expected one argument.");
            const r = e[1];
            if ("object" != typeof r || Array.isArray(r))
                return t.error("Collator options argument must be an object.");
            const n = t.parse(void 0 !== r["case-sensitive"] && r["case-sensitive"], 1, B);
            if (!n)
                return null;
            const o = t.parse(void 0 !== r["diacritic-sensitive"] && r["diacritic-sensitive"], 1, B);
            if (!o)
                return null;
            let a = null;
            return r.locale && (a = t.parse(r.locale, 1, Z), !a) ? null : new Pt(n, o, a)
        }
        evaluate(e) {
            return new Re(this.caseSensitive.evaluate(e), this.diacriticSensitive.evaluate(e), this.locale ? this.locale.evaluate(e) : null)
        }
        eachChild(e) {
            e(this.caseSensitive),
            e(this.diacriticSensitive),
            this.locale && e(this.locale)
        }
        outputDefined() {
            return !1
        }
    }
    class It {
        constructor(e, t, r, n, o) {
            this.type = Z,
            this.number = e,
            this.locale = t,
            this.currency = r,
            this.minFractionDigits = n,
            this.maxFractionDigits = o
        }
        static parse(e, t) {
            if (3 !== e.length)
                return t.error("Expected two arguments.");
            const r = t.parse(e[1], 1, W);
            if (!r)
                return null;
            const n = e[2];
            if ("object" != typeof n || Array.isArray(n))
                return t.error("NumberFormat options argument must be an object.");
            let o = null;
            if (n.locale && (o = t.parse(n.locale, 1, Z), !o))
                return null;
            let a = null;
            if (n.currency && (a = t.parse(n.currency, 1, Z), !a))
                return null;
            let i = null;
            if (n["min-fraction-digits"] && (i = t.parse(n["min-fraction-digits"], 1, W), !i))
                return null;
            let s = null;
            return n["max-fraction-digits"] && (s = t.parse(n["max-fraction-digits"], 1, W), !s) ? null : new It(r, o, a, i, s)
        }
        evaluate(e) {
            return new Intl.NumberFormat(this.locale ? this.locale.evaluate(e) : [], {
                style: this.currency ? "currency" : "decimal",
                currency: this.currency ? this.currency.evaluate(e) : void 0,
                minimumFractionDigits: this.minFractionDigits ? this.minFractionDigits.evaluate(e) : void 0,
                maximumFractionDigits: this.maxFractionDigits ? this.maxFractionDigits.evaluate(e) : void 0
            }).format(this.number.evaluate(e))
        }
        eachChild(e) {
            e(this.number),
            this.locale && e(this.locale),
            this.currency && e(this.currency),
            this.minFractionDigits && e(this.minFractionDigits),
            this.maxFractionDigits && e(this.maxFractionDigits)
        }
        outputDefined() {
            return !1
        }
    }
    class Ft {
        constructor(e) {
            this.type = ee,
            this.sections = e
        }
        static parse(e, t) {
            if (e.length < 2)
                return t.error("Expected at least one argument.");
            const r = e[1];
            if (!Array.isArray(r) && "object" == typeof r)
                return t.error("First argument must be an image or text section.");
            const n = [];
            let o = !1;
            for (let r = 1; r <= e.length - 1; ++r) {
                const a = e[r];
                if (o && "object" == typeof a && !Array.isArray(a)) {
                    o = !1;
                    let e = null;
                    if (a["font-scale"] && (e = t.parse(a["font-scale"], 1, W), !e))
                        return null;
                    let r = null;
                    if (a["text-font"] && (r = t.parse(a["text-font"], 1, ie(Z)), !r))
                        return null;
                    let i = null;
                    if (a["text-color"] && (i = t.parse(a["text-color"], 1, H), !i))
                        return null;
                    let s = null;
                    if (a["vertical-align"]) {
                        if ("string" == typeof a["vertical-align"] && !Le.includes(a["vertical-align"]))
                            return t.error(`'vertical-align' must be one of: 'bottom', 'center', 'top' but found '${a["vertical-align"]}' instead.`);
                        if (s = t.parse(a["vertical-align"], 1, Z), !s)
                            return null
                    }
                    const l = n[n.length - 1];
                    l.scale = e,
                    l.font = r,
                    l.textColor = i,
                    l.verticalAlign = s
                } else {
                    const a = t.parse(e[r], 1, Y);
                    if (!a)
                        return null;
                    const i = a.type.kind;
                    if ("string" !== i && "value" !== i && "null" !== i && "resolvedImage" !== i)
                        return t.error("Formatted text type must be 'string', 'value', 'image' or 'null'.");
                    o = !0,
                    n.push({
                        content: a,
                        scale: null,
                        font: null,
                        textColor: null,
                        verticalAlign: null
                    })
                }
            }
            return new Ft(n)
        }
        evaluate(e) {
            return new Ue(this.sections.map(t => {
                    const r = t.content.evaluate(e);
                    return Qe(r) === oe ? new De("", r, null, null, null, t.verticalAlign ? t.verticalAlign.evaluate(e) : null) : new De(et(r), null, t.scale ? t.scale.evaluate(e) : null, t.font ? t.font.evaluate(e).join(",") : null, t.textColor ? t.textColor.evaluate(e) : null, t.verticalAlign ? t.verticalAlign.evaluate(e) : null)
                }))
        }
        eachChild(e) {
            for (const t of this.sections)
                e(t.content), t.scale && e(t.scale), t.font && e(t.font), t.textColor && e(t.textColor), t.verticalAlign && e(t.verticalAlign)
        }
        outputDefined() {
            return !1
        }
    }
    class Rt {
        constructor(e) {
            this.type = oe,
            this.input = e
        }
        static parse(e, t) {
            if (2 !== e.length)
                return t.error("Expected two arguments.");
            const r = t.parse(e[1], 1, Z);
            return r ? new Rt(r) : t.error("No image name provided.")
        }
        evaluate(e) {
            const t = this.input.evaluate(e),
            r = He.fromString(t);
            return r && e.availableImages && (r.available = e.availableImages.indexOf(t) > -1),
            r
        }
        eachChild(e) {
            e(this.input)
        }
        outputDefined() {
            return !1
        }
    }
    class Lt {
        constructor(e) {
            this.type = W,
            this.input = e
        }
        static parse(e, t) {
            if (2 !== e.length)
                return t.error(`Expected 1 argument, but found ${e.length - 1} instead.`);
            const r = t.parse(e[1], 1);
            return r ? "array" !== r.type.kind && "string" !== r.type.kind && "value" !== r.type.kind ? t.error(`Expected argument of type string or array, but found ${se(r.type)} instead.`) : new Lt(r) : null
        }
        evaluate(e) {
            const t = this.input.evaluate(e);
            if ("string" == typeof t)
                return [...t].length;
            if (Array.isArray(t))
                return t.length;
            throw new We(`Expected value to be of type string or array, but found ${se(Qe(t))} instead.`)
        }
        eachChild(e) {
            e(this.input)
        }
        outputDefined() {
            return !1
        }
    }
    const Dt = 8192;
    function Ut(e, t) {
        const r = (180 + e[0]) / 360;
        const n = (o = e[1], (180 - 180 / Math.PI * Math.log(Math.tan(Math.PI / 4 + o * Math.PI / 360))) / 360);
        var o;
        const a = Math.pow(2, t.z);
        return [Math.round(r * a * Dt), Math.round(n * a * Dt)]
    }
    function Gt(e, t) {
        const r = Math.pow(2, t.z),
        n = (e[0] / Dt + t.x) / r,
        o = (e[1] / Dt + t.y) / r;
        return [(i = n, 360 * i - 180), (a = o, 360 / Math.PI * Math.atan(Math.exp((180 - 360 * a) * Math.PI / 180)) - 90)];
        var a,
        i
    }
    function Vt(e, t) {
        e[0] = Math.min(e[0], t[0]),
        e[1] = Math.min(e[1], t[1]),
        e[2] = Math.max(e[2], t[0]),
        e[3] = Math.max(e[3], t[1])
    }
    function Jt(e, t) {
        return !(e[0] <= t[0]) && (!(e[2] >= t[2]) && (!(e[1] <= t[1]) && !(e[3] >= t[3])))
    }
    function Wt(e, t, r) {
        return t[1] > e[1] != r[1] > e[1] && e[0] < (r[0] - t[0]) * (e[1] - t[1]) / (r[1] - t[1]) + t[0]
    }
    function Zt(e, t, r) {
        const n = e[0] - t[0],
        o = e[1] - t[1],
        a = e[0] - r[0],
        i = e[1] - r[1];
        return n * i - a * o === 0 && n * a <= 0 && o * i <= 0
    }
    function Bt(e, t, r, n) {
        const o = [t[0] - e[0], t[1] - e[1]],
        a = [n[0] - r[0], n[1] - r[1]];
        return 0 !== (i = a)[0] * (s = o)[1] - i[1] * s[0] && !(!er(e, t, r, n) || !er(r, n, e, t));
        var i,
        s
    }
    function Ht(e, t, r) {
        for (const n of r)
            for (let r = 0; r < n.length - 1; ++r)
                if (Bt(e, t, n[r], n[r + 1]))
                    return !0;
        return !1
    }
    function Xt(e, t, r = !1) {
        let n = !1;
        for (const o of t)
            for (let t = 0; t < o.length - 1; t++) {
                if (Zt(e, o[t], o[t + 1]))
                    return r;
                Wt(e, o[t], o[t + 1]) && (n = !n)
            }
        return n
    }
    function Kt(e, t) {
        for (const r of t)
            if (Xt(e, r))
                return !0;
        return !1
    }
    function Yt(e, t) {
        for (const r of e)
            if (!Xt(r, t))
                return !1;
        for (let r = 0; r < e.length - 1; ++r)
            if (Ht(e[r], e[r + 1], t))
                return !1;
        return !0
    }
    function Qt(e, t) {
        for (const r of t)
            if (Yt(e, r))
                return !0;
        return !1
    }
    function er(e, t, r, n) {
        const o = e[0] - r[0],
        a = e[1] - r[1],
        i = t[0] - r[0],
        s = t[1] - r[1],
        l = n[0] - r[0],
        u = n[1] - r[1],
        c = o * u - l * a,
        p = i * u - l * s;
        return c > 0 && p < 0 || c < 0 && p > 0
    }
    function tr(e, t, r) {
        const n = [];
        for (let o = 0; o < e.length; o++) {
            const a = [];
            for (let n = 0; n < e[o].length; n++) {
                const i = Ut(e[o][n], r);
                Vt(t, i),
                a.push(i)
            }
            n.push(a)
        }
        return n
    }
    function rr(e, t, r) {
        const n = [];
        for (let o = 0; o < e.length; o++) {
            const a = tr(e[o], t, r);
            n.push(a)
        }
        return n
    }
    function nr(e, t, r, n) {
        if (e[0] < r[0] || e[0] > r[2]) {
            const t = .5 * n;
            let o = e[0] - r[0] > t ? -n : r[0] - e[0] > t ? n : 0;
            0 === o && (o = e[0] - r[2] > t ? -n : r[2] - e[0] > t ? n : 0),
            e[0] += o
        }
        Vt(t, e)
    }
    function or(e, t, r, n) {
        const o = Math.pow(2, n.z) * Dt,
        a = [n.x * Dt, n.y * Dt],
        i = [];
        for (const n of e)
            for (const e of n) {
                const n = [e.x + a[0], e.y + a[1]];
                nr(n, t, r, o),
                i.push(n)
            }
        return i
    }
    function ar(e, t, r, n) {
        const o = Math.pow(2, n.z) * Dt,
        a = [n.x * Dt, n.y * Dt],
        i = [];
        for (const r of e) {
            const e = [];
            for (const n of r) {
                const r = [n.x + a[0], n.y + a[1]];
                Vt(t, r),
                e.push(r)
            }
            i.push(e)
        }
        if (t[2] - t[0] <= o / 2) {
            (s = t)[0] = s[1] = 1 / 0,
            s[2] = s[3] = -1 / 0;
            for (const e of i)
                for (const n of e)
                    nr(n, t, r, o)
        }
        var s;
        return i
    }
    class ir {
        constructor(e, t) {
            this.type = B,
            this.geojson = e,
            this.geometries = t
        }
        static parse(e, t) {
            if (2 !== e.length)
                return t.error(`'within' expression requires exactly one argument, but found ${e.length - 1} instead.`);
            if (Ye(e[1])) {
                const t = e[1];
                if ("FeatureCollection" === t.type) {
                    const e = [];
                    for (const r of t.features) {
                        const {
                            type: t,
                            coordinates: n
                        } = r.geometry;
                        "Polygon" === t && e.push(n),
                        "MultiPolygon" === t && e.push(...n)
                    }
                    if (e.length) {
                        return new ir(t, {
                            type: "MultiPolygon",
                            coordinates: e
                        })
                    }
                } else if ("Feature" === t.type) {
                    const e = t.geometry.type;
                    if ("Polygon" === e || "MultiPolygon" === e)
                        return new ir(t, t.geometry)
                } else if ("Polygon" === t.type || "MultiPolygon" === t.type)
                    return new ir(t, t)
            }
            return t.error("'within' expression requires valid geojson object that contains polygon geometry type.")
        }
        evaluate(e) {
            if (null != e.geometry() && null != e.canonicalID()) {
                if ("Point" === e.geometryType())
                    return function (e, t) {
                        const r = [1 / 0, 1 / 0, -1 / 0, -1 / 0],
                        n = [1 / 0, 1 / 0, -1 / 0, -1 / 0],
                        o = e.canonicalID();
                        if ("Polygon" === t.type) {
                            const a = tr(t.coordinates, n, o),
                            i = or(e.geometry(), r, n, o);
                            if (!Jt(r, n))
                                return !1;
                            for (const e of i)
                                if (!Xt(e, a))
                                    return !1
                        }
                        if ("MultiPolygon" === t.type) {
                            const a = rr(t.coordinates, n, o),
                            i = or(e.geometry(), r, n, o);
                            if (!Jt(r, n))
                                return !1;
                            for (const e of i)
                                if (!Kt(e, a))
                                    return !1
                        }
                        return !0
                    }
                (e, this.geometries);
                if ("LineString" === e.geometryType())
                    return function (e, t) {
                        const r = [1 / 0, 1 / 0, -1 / 0, -1 / 0],
                        n = [1 / 0, 1 / 0, -1 / 0, -1 / 0],
                        o = e.canonicalID();
                        if ("Polygon" === t.type) {
                            const a = tr(t.coordinates, n, o),
                            i = ar(e.geometry(), r, n, o);
                            if (!Jt(r, n))
                                return !1;
                            for (const e of i)
                                if (!Yt(e, a))
                                    return !1
                        }
                        if ("MultiPolygon" === t.type) {
                            const a = rr(t.coordinates, n, o),
                            i = ar(e.geometry(), r, n, o);
                            if (!Jt(r, n))
                                return !1;
                            for (const e of i)
                                if (!Qt(e, a))
                                    return !1
                        }
                        return !0
                    }
                (e, this.geometries)
            }
            return !1
        }
        eachChild() {}
        outputDefined() {
            return !0
        }
    }
    class sr {
        constructor(e = [], t = (e, t) => e < t ? -1 : e > t ? 1 : 0) {
            if (this.data = e, this.length = this.data.length, this.compare = t, this.length > 0)
                for (let e = (this.length >> 1) - 1; e >= 0; e--)
                    this._down(e)
        }
        push(e) {
            this.data.push(e),
            this._up(this.length++)
        }
        pop() {
            if (0 === this.length)
                return;
            const e = this.data[0],
            t = this.data.pop();
            return --this.length > 0 && (this.data[0] = t, this._down(0)),
            e
        }
        peek() {
            return this.data[0]
        }
        _up(e) {
            const {
                data: t,
                compare: r
            } = this,
            n = t[e];
            for (; e > 0; ) {
                const o = e - 1 >> 1,
                a = t[o];
                if (r(n, a) >= 0)
                    break;
                t[e] = a,
                e = o
            }
            t[e] = n
        }
        _down(e) {
            const {
                data: t,
                compare: r
            } = this,
            n = this.length >> 1,
            o = t[e];
            for (; e < n; ) {
                let n = 1 + (e << 1);
                const a = n + 1;
                if (a < this.length && r(t[a], t[n]) < 0 && (n = a), r(t[n], o) >= 0)
                    break;
                t[e] = t[n],
                e = n
            }
            t[e] = o
        }
    }
    function lr(e) {
        let t = 0;
        for (let r, n, o = 0, a = e.length, i = a - 1; o < a; i = o++)
            r = e[o], n = e[i], t += (n.x - r.x) * (r.y + n.y);
        return t
    }
    const ur = 1 / 298.257223563,
    cr = ur * (2 - ur),
    pr = Math.PI / 180;
    class fr {
        constructor(e) {
            const t = 6378.137 * pr * 1e3,
            r = Math.cos(e * pr),
            n = 1 / (1 - cr * (1 - r * r)),
            o = Math.sqrt(n);
            this.kx = t * o * r,
            this.ky = t * o * n * (1 - cr)
        }
        distance(e, t) {
            const r = this.wrap(e[0] - t[0]) * this.kx,
            n = (e[1] - t[1]) * this.ky;
            return Math.sqrt(r * r + n * n)
        }
        pointOnLine(e, t) {
            let r,
            n,
            o,
            a,
            i = 1 / 0;
            for (let s = 0; s < e.length - 1; s++) {
                let l = e[s][0],
                u = e[s][1],
                c = this.wrap(e[s + 1][0] - l) * this.kx,
                p = (e[s + 1][1] - u) * this.ky,
                f = 0;
                0 === c && 0 === p || (f = (this.wrap(t[0] - l) * this.kx * c + (t[1] - u) * this.ky * p) / (c * c + p * p), f > 1 ? (l = e[s + 1][0], u = e[s + 1][1]) : f > 0 && (l += c / this.kx * f, u += p / this.ky * f)),
                c = this.wrap(t[0] - l) * this.kx,
                p = (t[1] - u) * this.ky;
                const d = c * c + p * p;
                d < i && (i = d, r = l, n = u, o = s, a = f)
            }
            return {
                point: [r, n],
                index: o,
                t: Math.max(0, Math.min(1, a))
            }
        }
        wrap(e) {
            for (; e < -180; )
                e += 360;
            for (; e > 180; )
                e -= 360;
            return e
        }
    }
    function dr(e, t) {
        return t[0] - e[0]
    }
    function mr(e) {
        return e[1] - e[0] + 1
    }
    function yr(e, t) {
        return e[1] >= e[0] && e[1] < t
    }
    function hr(e, t) {
        if (e[0] > e[1])
            return [null, null];
        const r = mr(e);
        if (t) {
            if (2 === r)
                return [e, null];
            const t = Math.floor(r / 2);
            return [[e[0], e[0] + t], [e[0] + t, e[1]]]
        }
        if (1 === r)
            return [e, null];
        const n = Math.floor(r / 2) - 1;
        return [[e[0], e[0] + n], [e[0] + n + 1, e[1]]]
    }
    function gr(e, t) {
        if (!yr(t, e.length))
            return [1 / 0, 1 / 0, -1 / 0, -1 / 0];
        const r = [1 / 0, 1 / 0, -1 / 0, -1 / 0];
        for (let n = t[0]; n <= t[1]; ++n)
            Vt(r, e[n]);
        return r
    }
    function br(e) {
        const t = [1 / 0, 1 / 0, -1 / 0, -1 / 0];
        for (const r of e)
            for (const e of r)
                Vt(t, e);
        return t
    }
    function vr(e) {
        return e[0] !== -1 / 0 && e[1] !== -1 / 0 && e[2] !== 1 / 0 && e[3] !== 1 / 0
    }
    function xr(e, t, r) {
        if (!vr(e) || !vr(t))
            return NaN;
        let n = 0,
        o = 0;
        return e[2] < t[0] && (n = t[0] - e[2]),
        e[0] > t[2] && (n = e[0] - t[2]),
        e[1] > t[3] && (o = e[1] - t[3]),
        e[3] < t[1] && (o = t[1] - e[3]),
        r.distance([0, 0], [n, o])
    }
    function wr(e, t, r) {
        const n = r.pointOnLine(t, e);
        return r.distance(e, n.point)
    }
    function kr(e, t, r, n, o) {
        const a = Math.min(wr(e, [r, n], o), wr(t, [r, n], o)),
        i = Math.min(wr(r, [e, t], o), wr(n, [e, t], o));
        return Math.min(a, i)
    }
    function Mr(e, t, r, n, o) {
        if (!(yr(t, e.length) && yr(n, r.length)))
            return 1 / 0;
        let a = 1 / 0;
        for (let i = t[0]; i < t[1]; ++i) {
            const t = e[i],
            s = e[i + 1];
            for (let e = n[0]; e < n[1]; ++e) {
                const n = r[e],
                i = r[e + 1];
                if (Bt(t, s, n, i))
                    return 0;
                a = Math.min(a, kr(t, s, n, i, o))
            }
        }
        return a
    }
    function zr(e, t, r, n, o) {
        if (!(yr(t, e.length) && yr(n, r.length)))
            return NaN;
        let a = 1 / 0;
        for (let i = t[0]; i <= t[1]; ++i)
            for (let t = n[0]; t <= n[1]; ++t)
                if (a = Math.min(a, o.distance(e[i], r[t])), 0 === a)
                    return a;
        return a
    }
    function Sr(e, t, r) {
        if (Xt(e, t, !0))
            return 0;
        let n = 1 / 0;
        for (const o of t) {
            const t = o[0],
            a = o[o.length - 1];
            if (t !== a && (n = Math.min(n, wr(e, [a, t], r)), 0 === n))
                return n;
            const i = r.pointOnLine(o, e);
            if (n = Math.min(n, r.distance(e, i.point)), 0 === n)
                return n
        }
        return n
    }
    function jr(e, t, r, n) {
        if (!yr(t, e.length))
            return NaN;
        for (let n = t[0]; n <= t[1]; ++n)
            if (Xt(e[n], r, !0))
                return 0;
        let o = 1 / 0;
        for (let a = t[0]; a < t[1]; ++a) {
            const t = e[a],
            i = e[a + 1];
            for (const e of r)
                for (let r = 0, a = e.length, s = a - 1; r < a; s = r++) {
                    const a = e[s],
                    l = e[r];
                    if (Bt(t, i, a, l))
                        return 0;
                    o = Math.min(o, kr(t, i, a, l, n))
                }
        }
        return o
    }
    function Ar(e, t) {
        for (const r of e)
            for (const e of r)
                if (Xt(e, t, !0))
                    return !0;
        return !1
    }
    function Er(e, t, r, n = 1 / 0) {
        const o = br(e),
        a = br(t);
        if (n !== 1 / 0 && xr(o, a, r) >= n)
            return n;
        if (Jt(o, a)) {
            if (Ar(e, t))
                return 0
        } else if (Ar(t, e))
            return 0;
        let i = 1 / 0;
        for (const n of e)
            for (let e = 0, o = n.length, a = o - 1; e < o; a = e++) {
                const o = n[a],
                s = n[e];
                for (const e of t)
                    for (let t = 0, n = e.length, a = n - 1; t < n; a = t++) {
                        const n = e[a],
                        l = e[t];
                        if (Bt(o, s, n, l))
                            return 0;
                        i = Math.min(i, kr(o, s, n, l, r))
                    }
            }
        return i
    }
    function qr(e, t, r, n, o, a) {
        if (!a)
            return;
        const i = xr(gr(n, a), o, r);
        i < t && e.push([i, a, [0, 0]])
    }
    function $r(e, t, r, n, o, a, i) {
        if (!a || !i)
            return;
        const s = xr(gr(n, a), gr(o, i), r);
        s < t && e.push([s, a, i])
    }
    function Cr(e, t, r, n, o = 1 / 0) {
        let a = Math.min(n.distance(e[0], r[0][0]), o);
        if (0 === a)
            return a;
        const i = new sr([[0, [0, e.length - 1], [0, 0]]], dr),
        s = br(r);
        for (; i.length > 0; ) {
            const o = i.pop();
            if (o[0] >= a)
                continue;
            const l = o[1],
            u = t ? 50 : 100;
            if (mr(l) <= u) {
                if (!yr(l, e.length))
                    return NaN;
                if (t) {
                    const t = jr(e, l, r, n);
                    if (isNaN(t) || 0 === t)
                        return t;
                    a = Math.min(a, t)
                } else
                    for (let t = l[0]; t <= l[1]; ++t) {
                        const o = Sr(e[t], r, n);
                        if (a = Math.min(a, o), 0 === a)
                            return 0
                    }
            } else {
                const r = hr(l, t);
                qr(i, a, n, e, s, r[0]),
                qr(i, a, n, e, s, r[1])
            }
        }
        return a
    }
    function _r(e, t, r, n, o, a = 1 / 0) {
        let i = Math.min(a, o.distance(e[0], r[0]));
        if (0 === i)
            return i;
        const s = new sr([[0, [0, e.length - 1], [0, r.length - 1]]], dr);
        for (; s.length > 0; ) {
            const a = s.pop();
            if (a[0] >= i)
                continue;
            const l = a[1],
            u = a[2],
            c = t ? 50 : 100,
            p = n ? 50 : 100;
            if (mr(l) <= c && mr(u) <= p) {
                if (!yr(l, e.length) && yr(u, r.length))
                    return NaN;
                let a;
                if (t && n)
                    a = Mr(e, l, r, u, o), i = Math.min(i, a);
                else if (t && !n) {
                    const t = e.slice(l[0], l[1] + 1);
                    for (let e = u[0]; e <= u[1]; ++e)
                        if (a = wr(r[e], t, o), i = Math.min(i, a), 0 === i)
                            return i
                } else if (!t && n) {
                    const t = r.slice(u[0], u[1] + 1);
                    for (let r = l[0]; r <= l[1]; ++r)
                        if (a = wr(e[r], t, o), i = Math.min(i, a), 0 === i)
                            return i
                } else
                    a = zr(e, l, r, u, o), i = Math.min(i, a)
            } else {
                const a = hr(l, t),
                c = hr(u, n);
                $r(s, i, o, e, r, a[0], c[0]),
                $r(s, i, o, e, r, a[0], c[1]),
                $r(s, i, o, e, r, a[1], c[0]),
                $r(s, i, o, e, r, a[1], c[1])
            }
        }
        return i
    }
    function Tr(e, t) {
        const r = e.geometry();
        if (0 === r.length || 0 === r[0].length)
            return NaN;
        const n = function (e) {
            if (e.length <= 1)
                return [e];
            const t = [];
            let r,
            n;
            for (const o of e) {
                const e = lr(o);
                0 !== e && (o.area = Math.abs(e), void 0 === n && (n = e < 0), n === e < 0 ? (r && t.push(r), r = [o]) : r.push(o))
            }
            return r && t.push(r),
            t
        }
        (r).map(t => t.map(t => t.map(t => Gt([t.x, t.y], e.canonical)))),
        o = new fr(n[0][0][0][1]);
        let a = 1 / 0;
        for (const e of t)
            for (const t of n) {
                switch (e.type) {
                case "Point":
                    a = Math.min(a, Cr([e.coordinates], !1, t, o, a));
                    break;
                case "LineString":
                    a = Math.min(a, Cr(e.coordinates, !0, t, o, a));
                    break;
                case "Polygon":
                    a = Math.min(a, Er(t, e.coordinates, o, a))
                }
                if (0 === a)
                    return a
            }
        return a
    }
    function Or(e) {
        return "MultiPolygon" === e.type ? e.coordinates.map(e => ({
                type: "Polygon",
                coordinates: e
            })) : "MultiLineString" === e.type ? e.coordinates.map(e => ({
                type: "LineString",
                coordinates: e
            })) : "MultiPoint" === e.type ? e.coordinates.map(e => ({
                type: "Point",
                coordinates: e
            })) : [e]
    }
    class Nr {
        constructor(e, t) {
            this.type = W,
            this.geojson = e,
            this.geometries = t
        }
        static parse(e, t) {
            if (2 !== e.length)
                return t.error(`'distance' expression requires exactly one argument, but found ${e.length - 1} instead.`);
            if (Ye(e[1])) {
                const t = e[1];
                if ("FeatureCollection" === t.type)
                    return new Nr(t, t.features.map(e => Or(e.geometry)).flat());
                if ("Feature" === t.type)
                    return new Nr(t, Or(t.geometry));
                if ("type" in t && "coordinates" in t)
                    return new Nr(t, Or(t))
            }
            return t.error("'distance' expression requires valid geojson object that contains polygon geometry type.")
        }
        evaluate(e) {
            if (null != e.geometry() && null != e.canonicalID()) {
                if ("Point" === e.geometryType())
                    return function (e, t) {
                        const r = e.geometry(),
                        n = r.flat().map(t => Gt([t.x, t.y], e.canonical));
                        if (0 === r.length)
                            return NaN;
                        const o = new fr(n[0][1]);
                        let a = 1 / 0;
                        for (const e of t) {
                            switch (e.type) {
                            case "Point":
                                a = Math.min(a, _r(n, !1, [e.coordinates], !1, o, a));
                                break;
                            case "LineString":
                                a = Math.min(a, _r(n, !1, e.coordinates, !0, o, a));
                                break;
                            case "Polygon":
                                a = Math.min(a, Cr(n, !1, e.coordinates, o, a))
                            }
                            if (0 === a)
                                return a
                        }
                        return a
                    }
                (e, this.geometries);
                if ("LineString" === e.geometryType())
                    return function (e, t) {
                        const r = e.geometry(),
                        n = r.flat().map(t => Gt([t.x, t.y], e.canonical));
                        if (0 === r.length)
                            return NaN;
                        const o = new fr(n[0][1]);
                        let a = 1 / 0;
                        for (const e of t) {
                            switch (e.type) {
                            case "Point":
                                a = Math.min(a, _r(n, !0, [e.coordinates], !1, o, a));
                                break;
                            case "LineString":
                                a = Math.min(a, _r(n, !0, e.coordinates, !0, o, a));
                                break;
                            case "Polygon":
                                a = Math.min(a, Cr(n, !0, e.coordinates, o, a))
                            }
                            if (0 === a)
                                return a
                        }
                        return a
                    }
                (e, this.geometries);
                if ("Polygon" === e.geometryType())
                    return Tr(e, this.geometries)
            }
            return NaN
        }
        eachChild() {}
        outputDefined() {
            return !0
        }
    }
    class Pr {
        constructor(e) {
            this.type = Y,
            this.key = e
        }
        static parse(e, t) {
            if (2 !== e.length)
                return t.error(`Expected 1 argument, but found ${e.length - 1} instead.`);
            const r = e[1];
            return null == r ? t.error("Global state property must be defined.") : "string" != typeof r ? t.error(`Global state property must be string, but found ${typeof e[1]} instead.`) : new Pr(r)
        }
        evaluate(e) {
            var t;
            const r = null === (t = e.globals) || void 0 === t ? void 0 : t.globalState;
            return r && 0 !== Object.keys(r).length ? qe(r, this.key) : null
        }
        eachChild() {}
        outputDefined() {
            return !1
        }
    }
    const Ir = {
        "==": $t,
        "!=": Ct,
        ">": Tt,
        "<": _t,
        ">=": Nt,
        "<=": Ot,
        array: nt,
        at: pt,
        boolean: nt,
    case :
        yt,
        coalesce: jt,
        collator: Pt,
        format: Ft,
        image: Rt,
        in: ft,
        "index-of": dt,
        interpolate: zt,
        "interpolate-hcl": zt,
        "interpolate-lab": zt,
        length: Lt,
        let: ut,
        literal: tt,
        match: mt,
        number: nt,
        "number-format": It,
        object: nt,
        slice: ht,
        step: bt,
        string: nt,
        "to-boolean": at,
        "to-color": at,
        "to-number": at,
        "to-string": at,
        var: ct,
        within: ir,
        distance: Nr,
        "global-state": Pr
    };
    class Fr {
        constructor(e, t, r, n) {
            this.name = e,
            this.type = t,
            this._evaluate = r,
            this.args = n
        }
        evaluate(e) {
            return this._evaluate(e, this.args)
        }
        eachChild(e) {
            this.args.forEach(e)
        }
        outputDefined() {
            return !1
        }
        static parse(e, t) {
            const r = e[0],
            n = Fr.definitions[r];
            if (!n)
                return t.error(`Unknown expression "${r}". If you wanted a literal array, use ["literal", [...]].`, 0);
            const o = Array.isArray(n) ? n[0] : n.type,
            a = Array.isArray(n) ? [[n[1], n[2]]] : n.overloads,
            i = a.filter(([t]) => !Array.isArray(t) || t.length === e.length - 1);
            let s = null;
            for (const [n, a] of i) {
                s = new lt(t.registry, Gr, t.path, null, t.scope);
                const i = [];
                let l = !1;
                for (let t = 1; t < e.length; t++) {
                    const r = e[t],
                    o = Array.isArray(n) ? n[t - 1] : n.type,
                    a = s.parse(r, 1 + i.length, o);
                    if (!a) {
                        l = !0;
                        break
                    }
                    i.push(a)
                }
                if (!l)
                    if (Array.isArray(n) && n.length !== i.length)
                        s.error(`Expected ${n.length} arguments, but found ${i.length} instead.`);
                    else {
                        for (let e = 0; e < i.length; e++) {
                            const t = Array.isArray(n) ? n[e] : n.type,
                            r = i[e];
                            s.concat(e + 1).checkSubtype(t, r.type)
                        }
                        if (0 === s.errors.length)
                            return new Fr(r, o, a, i)
                    }
            }
            if (1 === i.length)
                t.errors.push(...s.errors);
            else {
                const r = (i.length ? i : a).map(([e]) => {
                    return t = e,
                    Array.isArray(t) ? `(${t.map(se).join(", ")})` : `(${se(t.type)}...)`;
                    var t
                }).join(" | "),
                n = [];
                for (let r = 1; r < e.length; r++) {
                    const o = t.parse(e[r], 1 + n.length);
                    if (!o)
                        return null;
                    n.push(se(o.type))
                }
                t.error(`Expected arguments of type ${r}, but found (${n.join(", ")}) instead.`)
            }
            return null
        }
        static register(e, t) {
            Fr.definitions = t;
            for (const r in t)
                e[r] = Fr
        }
    }
    function Rr(e, [t, r, n, o]) {
        t = t.evaluate(e),
        r = r.evaluate(e),
        n = n.evaluate(e);
        const a = o ? o.evaluate(e) : 1,
        i = Ke(t, r, n, a);
        if (i)
            throw new We(i);
        return new Fe(t / 255, r / 255, n / 255, a, !1)
    }
    function Lr(e, t) {
        return e in t
    }
    function Dr(e, t) {
        const r = t[e];
        return void 0 === r ? null : r
    }
    function Ur(e) {
        return {
            type: e
        }
    }
    function Gr(e) {
        if (e instanceof ct)
            return Gr(e.boundExpression);
        if (e instanceof Fr && "error" === e.name)
            return !1;
        if (e instanceof Pt)
            return !1;
        if (e instanceof ir)
            return !1;
        if (e instanceof Nr)
            return !1;
        if (e instanceof Pr)
            return !1;
        const t = e instanceof at || e instanceof nt;
        let r = !0;
        return e.eachChild(e => {
            r = t ? r && Gr(e) : r && e instanceof tt
        }),
        !!r && (Vr(e) && Wr(e, ["zoom", "heatmap-density", "elevation", "line-progress", "accumulated", "is-supported-script"]))
    }
    function Vr(e) {
        if (e instanceof Fr) {
            if ("get" === e.name && 1 === e.args.length)
                return !1;
            if ("feature-state" === e.name)
                return !1;
            if ("has" === e.name && 1 === e.args.length)
                return !1;
            if ("properties" === e.name || "geometry-type" === e.name || "id" === e.name)
                return !1;
            if (/^filter-/.test(e.name))
                return !1
        }
        if (e instanceof ir)
            return !1;
        if (e instanceof Nr)
            return !1;
        let t = !0;
        return e.eachChild(e => {
            t && !Vr(e) && (t = !1)
        }),
        t
    }
    function Jr(e) {
        if (e instanceof Fr && "feature-state" === e.name)
            return !1;
        let t = !0;
        return e.eachChild(e => {
            t && !Jr(e) && (t = !1)
        }),
        t
    }
    function Wr(e, t) {
        if (e instanceof Fr && t.indexOf(e.name) >= 0)
            return !1;
        let r = !0;
        return e.eachChild(e => {
            r && !Wr(e, t) && (r = !1)
        }),
        r
    }
    function Zr(e) {
        return {
            result: "success",
            value: e
        }
    }
    function Br(e) {
        return {
            result: "error",
            value: e
        }
    }
    function Hr(e) {
        return "object" == typeof e && null !== e && !Array.isArray(e) && Qe(e) === K
    }
    Fr.register(Ir, {
        error: [{
                kind: "error"
            }, [Z], (e, [t]) => {
                throw new We(t.evaluate(e))
            }
        ],
        typeof: [Z, [Y], (e, [t]) => se(Qe(t.evaluate(e)))],
        "to-rgba": [ie(W, 4), [H], (e, [t]) => {
                const [r, n, o, a] = t.evaluate(e).rgb;
                return [255 * r, 255 * n, 255 * o, a]
            }
        ],
        rgb: [H, [W, W, W], Rr],
        rgba: [H, [W, W, W, W], Rr],
        has: {
            type: B,
            overloads: [[[Z], (e, [t]) => Lr(t.evaluate(e), e.properties())], [[Z, K], (e, [t, r]) => Lr(t.evaluate(e), r.evaluate(e))]]
        },
        get: {
            type: Y,
            overloads: [[[Z], (e, [t]) => Dr(t.evaluate(e), e.properties())], [[Z, K], (e, [t, r]) => Dr(t.evaluate(e), r.evaluate(e))]]
        },
        "feature-state": [Y, [Z], (e, [t]) => Dr(t.evaluate(e), e.featureState || {})],
        properties: [K, [], e => e.properties()],
        "geometry-type": [Z, [], e => e.geometryType()],
        id: [Y, [], e => e.id()],
        zoom: [W, [], e => e.globals.zoom],
        "heatmap-density": [W, [], e => e.globals.heatmapDensity || 0],
        elevation: [W, [], e => e.globals.elevation || 0],
        "line-progress": [W, [], e => e.globals.lineProgress || 0],
        accumulated: [Y, [], e => void 0 === e.globals.accumulated ? null : e.globals.accumulated],
        "+": [W, Ur(W), (e, t) => {
                let r = 0;
                for (const n of t)
                    r += n.evaluate(e);
                return r
            }
        ],
        "*": [W, Ur(W), (e, t) => {
                let r = 1;
                for (const n of t)
                    r *= n.evaluate(e);
                return r
            }
        ],
        "-": {
            type: W,
            overloads: [[[W, W], (e, [t, r]) => t.evaluate(e) - r.evaluate(e)], [[W], (e, [t]) => -t.evaluate(e)]]
        },
        "/": [W, [W, W], (e, [t, r]) => t.evaluate(e) / r.evaluate(e)],
        "%": [W, [W, W], (e, [t, r]) => t.evaluate(e) % r.evaluate(e)],
        ln2: [W, [], () => Math.LN2],
        pi: [W, [], () => Math.PI],
        e: [W, [], () => Math.E],
        "^": [W, [W, W], (e, [t, r]) => Math.pow(t.evaluate(e), r.evaluate(e))],
        sqrt: [W, [W], (e, [t]) => Math.sqrt(t.evaluate(e))],
        log10: [W, [W], (e, [t]) => Math.log(t.evaluate(e)) / Math.LN10],
        ln: [W, [W], (e, [t]) => Math.log(t.evaluate(e))],
        log2: [W, [W], (e, [t]) => Math.log(t.evaluate(e)) / Math.LN2],
        sin: [W, [W], (e, [t]) => Math.sin(t.evaluate(e))],
        cos: [W, [W], (e, [t]) => Math.cos(t.evaluate(e))],
        tan: [W, [W], (e, [t]) => Math.tan(t.evaluate(e))],
        asin: [W, [W], (e, [t]) => Math.asin(t.evaluate(e))],
        acos: [W, [W], (e, [t]) => Math.acos(t.evaluate(e))],
        atan: [W, [W], (e, [t]) => Math.atan(t.evaluate(e))],
        min: [W, Ur(W), (e, t) => Math.min(...t.map(t => t.evaluate(e)))],
        max: [W, Ur(W), (e, t) => Math.max(...t.map(t => t.evaluate(e)))],
        abs: [W, [W], (e, [t]) => Math.abs(t.evaluate(e))],
        round: [W, [W], (e, [t]) => {
                const r = t.evaluate(e);
                return r < 0 ? -Math.round(-r) : Math.round(r)
            }
        ],
        floor: [W, [W], (e, [t]) => Math.floor(t.evaluate(e))],
        ceil: [W, [W], (e, [t]) => Math.ceil(t.evaluate(e))],
        "filter-==": [B, [Z, Y], (e, [t, r]) => e.properties()[t.value] === r.value],
        "filter-id-==": [B, [Y], (e, [t]) => e.id() === t.value],
        "filter-type-==": [B, [Z], (e, [t]) => e.geometryType() === t.value],
        "filter-<": [B, [Z, Y], (e, [t, r]) => {
                const n = e.properties()[t.value],
                o = r.value;
                return typeof n == typeof o && n < o
            }
        ],
        "filter-id-<": [B, [Y], (e, [t]) => {
                const r = e.id(),
                n = t.value;
                return typeof r == typeof n && r < n
            }
        ],
        "filter->": [B, [Z, Y], (e, [t, r]) => {
                const n = e.properties()[t.value],
                o = r.value;
                return typeof n == typeof o && n > o
            }
        ],
        "filter-id->": [B, [Y], (e, [t]) => {
                const r = e.id(),
                n = t.value;
                return typeof r == typeof n && r > n
            }
        ],
        "filter-<=": [B, [Z, Y], (e, [t, r]) => {
                const n = e.properties()[t.value],
                o = r.value;
                return typeof n == typeof o && n <= o
            }
        ],
        "filter-id-<=": [B, [Y], (e, [t]) => {
                const r = e.id(),
                n = t.value;
                return typeof r == typeof n && r <= n
            }
        ],
        "filter->=": [B, [Z, Y], (e, [t, r]) => {
                const n = e.properties()[t.value],
                o = r.value;
                return typeof n == typeof o && n >= o
            }
        ],
        "filter-id->=": [B, [Y], (e, [t]) => {
                const r = e.id(),
                n = t.value;
                return typeof r == typeof n && r >= n
            }
        ],
        "filter-has": [B, [Y], (e, [t]) => t.value in e.properties()],
        "filter-has-id": [B, [], e => null !== e.id() && void 0 !== e.id()],
        "filter-type-in": [B, [ie(Z)], (e, [t]) => t.value.indexOf(e.geometryType()) >= 0],
        "filter-id-in": [B, [ie(Y)], (e, [t]) => t.value.indexOf(e.id()) >= 0],
        "filter-in-small": [B, [Z, ie(Y)], (e, [t, r]) => r.value.indexOf(e.properties()[t.value]) >= 0],
        "filter-in-large": [B, [Z, ie(Y)], (e, [t, r]) => function (e, t, r, n) {
                for (; r <= n; ) {
                    const o = r + n >> 1;
                    if (t[o] === e)
                        return !0;
                    t[o] > e ? n = o - 1 : r = o + 1
                }
                return !1
            }
            (e.properties()[t.value], r.value, 0, r.value.length - 1)],
        all: {
            type: B,
            overloads: [[[B, B], (e, [t, r]) => t.evaluate(e) && r.evaluate(e)], [Ur(B), (e, t) => {
                        for (const r of t)
                            if (!r.evaluate(e))
                                return !1;
                        return !0
                    }
                ]]
        },
        any: {
            type: B,
            overloads: [[[B, B], (e, [t, r]) => t.evaluate(e) || r.evaluate(e)], [Ur(B), (e, t) => {
                        for (const r of t)
                            if (r.evaluate(e))
                                return !0;
                        return !1
                    }
                ]]
        },
        "!": [B, [B], (e, [t]) => !t.evaluate(e)],
        "is-supported-script": [B, [Z], (e, [t]) => {
                const r = e.globals && e.globals.isSupportedScript;
                return !r || r(t.evaluate(e))
            }
        ],
        upcase: [Z, [Z], (e, [t]) => t.evaluate(e).toUpperCase()],
        downcase: [Z, [Z], (e, [t]) => t.evaluate(e).toLowerCase()],
        concat: [Z, Ur(Y), (e, t) => t.map(t => et(t.evaluate(e))).join("")],
        "resolved-locale": [Z, [Q], (e, [t]) => t.evaluate(e).resolvedLocale()]
    });
    class Xr {
        constructor(e, t, r) {
            this.expression = e,
            this._warningHistory = {},
            this._evaluator = new st,
            this._defaultValue = t ? function (e) {
                if ("color" === e.type && Hr(e.default))
                    return new Fe(0, 0, 0, 0);
                switch (e.type) {
                case "color":
                    return Fe.parse(e.default) || null;
                case "padding":
                    return Ge.parse(e.default) || null;
                case "numberArray":
                    return Ve.parse(e.default) || null;
                case "colorArray":
                    return Je.parse(e.default) || null;
                case "variableAnchorOffsetCollection":
                    return Be.parse(e.default) || null;
                case "projectionDefinition":
                    return Xe.parse(e.default) || null;
                default:
                    return void 0 === e.default ? null : e.default
                }
            }
            (t) : null,
            this._enumValues = t && "enum" === t.type ? t.values : null,
            this._globalState = r
        }
        evaluateWithoutErrorHandling(e, t, r, n, o, a) {
            return this._globalState && (e = on(e, this._globalState)),
            this._evaluator.globals = e,
            this._evaluator.feature = t,
            this._evaluator.featureState = r,
            this._evaluator.canonical = n,
            this._evaluator.availableImages = o || null,
            this._evaluator.formattedSection = a,
            this.expression.evaluate(this._evaluator)
        }
        evaluate(e, t, r, n, o, a) {
            this._globalState && (e = on(e, this._globalState)),
            this._evaluator.globals = e,
            this._evaluator.feature = t || null,
            this._evaluator.featureState = r || null,
            this._evaluator.canonical = n,
            this._evaluator.availableImages = o || null,
            this._evaluator.formattedSection = a || null;
            try {
                const e = this.expression.evaluate(this._evaluator);
                if (null == e || "number" == typeof e && e != e)
                    return this._defaultValue;
                if (this._enumValues && !(e in this._enumValues))
                    throw new We(`Expected value to be one of ${Object.keys(this._enumValues).map(e => JSON.stringify(e)).join(", ")}, but found ${JSON.stringify(e)} instead.`);
                return e
            } catch (e) {
                return this._warningHistory[e.message] || (this._warningHistory[e.message] = !0, "undefined" != typeof console && console.warn(e.message)),
                this._defaultValue
            }
        }
    }
    function Kr(e) {
        return Array.isArray(e) && e.length > 0 && "string" == typeof e[0] && e[0]in Ir
    }
    function Yr(e, t, r) {
        const n = new lt(Ir, Gr, [], t ? function (e) {
            const t = {
                color: H,
                string: Z,
                number: W,
                enum: Z,
                boolean: B,
                formatted: ee,
                padding: te,
                numberArray: ne,
                colorArray: re,
                projectionDefinition: X,
                resolvedImage: oe,
                variableAnchorOffsetCollection: ae
            };
            if ("array" === e.type)
                return ie(t[e.value] || Y, e.length);
            return t[e.type]
        }
                (t) : void 0),
        o = n.parse(e, void 0, void 0, void 0, t && "string" === t.type ? {
            typeAnnotation: "coerce"
        }
                 : void 0);
        return o ? Zr(new Xr(o, t, r)) : Br(n.errors)
    }
    class Qr {
        constructor(e, t, r) {
            this.kind = e,
            this._styleExpression = t,
            this.isStateDependent = "constant" !== e && !Jr(t.expression),
            this.globalStateRefs = nn(t.expression),
            this._globalState = r
        }
        evaluateWithoutErrorHandling(e, t, r, n, o, a) {
            return this._globalState && (e = on(e, this._globalState)),
            this._styleExpression.evaluateWithoutErrorHandling(e, t, r, n, o, a)
        }
        evaluate(e, t, r, n, o, a) {
            return this._globalState && (e = on(e, this._globalState)),
            this._styleExpression.evaluate(e, t, r, n, o, a)
        }
    }
    class en {
        constructor(e, t, r, n, o) {
            this.kind = e,
            this.zoomStops = r,
            this._styleExpression = t,
            this.isStateDependent = "camera" !== e && !Jr(t.expression),
            this.globalStateRefs = nn(t.expression),
            this.interpolationType = n,
            this._globalState = o
        }
        evaluateWithoutErrorHandling(e, t, r, n, o, a) {
            return this._globalState && (e = on(e, this._globalState)),
            this._styleExpression.evaluateWithoutErrorHandling(e, t, r, n, o, a)
        }
        evaluate(e, t, r, n, o, a) {
            return this._globalState && (e = on(e, this._globalState)),
            this._styleExpression.evaluate(e, t, r, n, o, a)
        }
        interpolationFactor(e, t, r) {
            return this.interpolationType ? zt.interpolationFactor(this.interpolationType, e, t, r) : 0
        }
    }
    function tn(e, t, r) {
        const n = Yr(e, t, r);
        if ("error" === n.result)
            return n;
        const o = n.value.expression,
        a = Vr(o);
        if (!a && ("data-driven" !== (i = t)["property-type"] && "cross-faded-data-driven" !== i["property-type"]))
            return Br([new G("", "data expressions not supported")]);
        var i;
        const s = Wr(o, ["zoom"]);
        if (!s && !function (e) {
            return !!e.expression && e.expression.parameters.indexOf("zoom") > -1
        }
            (t))
            return Br([new G("", "zoom expressions not supported")]);
        const l = rn(o);
        if (!l && !s)
            return Br([new G("", '"zoom" expression may only be used as input to a top-level "step" or "interpolate" expression.')]);
        if (l instanceof G)
            return Br([l]);
        if (l instanceof zt && !function (e) {
            return !!e.expression && e.expression.interpolated
        }
            (t))
            return Br([new G("", '"interpolate" expressions cannot be used with this property')]);
        if (!l)
            return Zr(new Qr(a ? "constant" : "source", n.value, r));
        const u = l instanceof zt ? l.interpolation : void 0;
        return Zr(new en(a ? "camera" : "composite", n.value, l.labels, u, r))
    }
    function rn(e) {
        let t = null;
        if (e instanceof ut)
            t = rn(e.result);
        else if (e instanceof jt) {
            for (const r of e.args)
                if (t = rn(r), t)
                    break
        } else (e instanceof bt || e instanceof zt) && e.input instanceof Fr && "zoom" === e.input.name && (t = e);
        return t instanceof G || e.eachChild(e => {
            const r = rn(e);
            r instanceof G ? t = r : !t && r ? t = new G("", '"zoom" expression may only be used as input to a top-level "step" or "interpolate" expression.') : t && r && t !== r && (t = new G("", 'Only one zoom-based "step" or "interpolate" subexpression may be used in an expression.'))
        }),
        t
    }
    function nn(e, t = new Set) {
        return e instanceof Pr && t.add(e.key),
        e.eachChild(e => {
            nn(e, t)
        }),
        t
    }
    function on(e, t) {
        const {
            zoom: r,
            heatmapDensity: n,
            elevation: o,
            lineProgress: a,
            isSupportedScript: i,
            accumulated: s
        } = null != e ? e : {};
        return {
            zoom: r,
            heatmapDensity: n,
            elevation: o,
            lineProgress: a,
            isSupportedScript: i,
            accumulated: s,
            globalState: t
        }
    }
    function an(e) {
        if (!0 === e || !1 === e)
            return !0;
        if (!Array.isArray(e) || 0 === e.length)
            return !1;
        switch (e[0]) {
        case "has":
            return e.length >= 2 && "$id" !== e[1] && "$type" !== e[1];
        case "in":
            return e.length >= 3 && ("string" != typeof e[1] || Array.isArray(e[2]));
        case "!in":
        case "!has":
        case "none":
            return !1;
        case "==":
        case "!=":
        case ">":
        case ">=":
        case "<":
        case "<=":
            return 3 !== e.length || Array.isArray(e[1]) || Array.isArray(e[2]);
        case "any":
        case "all":
            for (const t of e.slice(1))
                if (!an(t) && "boolean" != typeof t)
                    return !1;
            return !0;
        default:
            return !0
        }
    }
    const sn = {
        type: "boolean",
    default:
        !1,
        transition: !1,
        "property-type": "data-driven",
        expression: {
            interpolated: !1,
            parameters: ["zoom", "feature"]
        }
    };
    function ln(e, t) {
        if (null == e)
            return {
                filter: () => !0,
                needGeometry: !1,
                getGlobalStateRefs: () => new Set
            };
        an(e) || (e = pn(e));
        const r = Yr(e, sn, t);
        if ("error" === r.result)
            throw new Error(r.value.map(e => `${e.key}: ${e.message}`).join(", "));
        return {
            filter: (e, t, n) => r.value.evaluate(e, t, {}, n),
            needGeometry: cn(e),
            getGlobalStateRefs: () => nn(r.value.expression)
        }
    }
    function un(e, t) {
        return e < t ? -1 : e > t ? 1 : 0
    }
    function cn(e) {
        if (!Array.isArray(e))
            return !1;
        if ("within" === e[0] || "distance" === e[0])
            return !0;
        for (let t = 1; t < e.length; t++)
            if (cn(e[t]))
                return !0;
        return !1
    }
    function pn(e) {
        if (!e)
            return !0;
        const t = e[0];
        if (e.length <= 1)
            return "any" !== t;
        var r;
        return "==" === t ? fn(e[1], e[2], "==") : "!=" === t ? yn(fn(e[1], e[2], "==")) : "<" === t || ">" === t || "<=" === t || ">=" === t ? fn(e[1], e[2], t) : "any" === t ? (r = e.slice(1), ["any"].concat(r.map(pn))) : "all" === t ? ["all"].concat(e.slice(1).map(pn)) : "none" === t ? ["all"].concat(e.slice(1).map(pn).map(yn)) : "in" === t ? dn(e[1], e.slice(2)) : "!in" === t ? yn(dn(e[1], e.slice(2))) : "has" === t ? mn(e[1]) : "!has" !== t || yn(mn(e[1]))
    }
    function fn(e, t, r) {
        switch (e) {
        case "$type":
            return [`filter-type-${r}`, t];
        case "$id":
            return [`filter-id-${r}`, t];
        default:
            return [`filter-${r}`, e, t]
        }
    }
    function dn(e, t) {
        if (0 === t.length)
            return !1;
        switch (e) {
        case "$type":
            return ["filter-type-in", ["literal", t]];
        case "$id":
            return ["filter-id-in", ["literal", t]];
        default:
            return t.length > 200 && !t.some(e => typeof e != typeof t[0]) ? ["filter-in-large", e, ["literal", t.sort(un)]] : ["filter-in-small", e, ["literal", t]]
        }
    }
    function mn(e) {
        switch (e) {
        case "$type":
            return !0;
        case "$id":
            return ["filter-has-id"];
        default:
            return ["filter-has", e]
        }
    }
    function yn(e) {
        return ["!", e]
    }
    function hn(e) {
        return "object" == typeof e ? ["literal", e] : e
    }
    function gn(e, t) {
        let r = e.stops;
        if (!r)
            return function (e, t) {
                const r = ["get", e.property];
                if (void 0 === e.default)
                    return "string" === t.type ? ["string", r] : r;
                if ("enum" === t.type)
                    return ["match", r, Object.keys(t.values), r, e.default]; {
                    const n = ["color" === t.type ? "to-color" : t.type, r, hn(e.default)];
                    return "array" === t.type && n.splice(1, 0, t.value, t.length || null),
                    n
                }
            }
        (e, t);
        const n = r && "object" == typeof r[0][0],
        o = n || void 0 !== e.property,
        a = n || !o;
        return r = r.map(e => !o && t.tokens && "string" == typeof e[1] ? [e[0], zn(e[1])] : [e[0], hn(e[1])]),
        n ? function (e, t, r) {
            const n = {},
            o = {},
            a = [];
            for (let t = 0; t < r.length; t++) {
                const i = r[t],
                s = i[0].zoom;
                void 0 === n[s] && (n[s] = {
                        zoom: s,
                        type: e.type,
                        property: e.property,
                    default:
                        e.default
                    }, o[s] = [], a.push(s)),
                o[s].push([i[0].value, i[1]])
            }
            const i = Mn({}, t);
            if ("exponential" === i) {
                const r = [bn(e), ["linear"], ["zoom"]];
                for (const e of a) {
                    kn(r, e, xn(n[e], t, o[e]), !1)
                }
                return r
            } {
                const e = ["step", ["zoom"]];
                for (const r of a) {
                    kn(e, r, xn(n[r], t, o[r]), !0)
                }
                return wn(e),
                e
            }
        }
        (e, t, r) : a ? function (e, t, r, n = ["zoom"]) {
            const o = Mn(e, t);
            let a,
            i = !1;
            if ("interval" === o)
                a = ["step", n], i = !0;
            else {
                if ("exponential" !== o)
                    throw new Error(`Unknown zoom function type "${o}"`); {
                    const t = void 0 !== e.base ? e.base : 1;
                    a = [bn(e), 1 === t ? ["linear"] : ["exponential", t], n]
                }
            }
            for (const e of r)
                kn(a, e[0], e[1], i);
            return wn(a),
            a
        }
        (e, t, r) : xn(e, t, r)
    }
    function bn(e) {
        switch (e.colorSpace) {
        case "hcl":
            return "interpolate-hcl";
        case "lab":
            return "interpolate-lab";
        default:
            return "interpolate"
        }
    }
    function vn(e, t) {
        const r = hn((n = e.default, o = t.default, void 0 !== n ? n : void 0 !== o ? o : void 0));
        var n,
        o;
        return void 0 === r && "resolvedImage" === t.type ? "" : r
    }
    function xn(e, t, r) {
        const n = Mn(e, t),
        o = ["get", e.property];
        if ("categorical" === n && "boolean" == typeof r[0][0]) {
            const n = ["case"];
            for (const e of r)
                n.push(["==", o, e[0]], e[1]);
            return n.push(vn(e, t)),
            n
        }
        if ("categorical" === n) {
            const n = ["match", o];
            for (const e of r)
                kn(n, e[0], e[1], !1);
            return n.push(vn(e, t)),
            n
        }
        if ("interval" === n) {
            const t = ["step", ["number", o]];
            for (const e of r)
                kn(t, e[0], e[1], !0);
            return wn(t),
            void 0 === e.default ? t : ["case", ["==", ["typeof", o], "number"], t, hn(e.default)]
        }
        if ("exponential" === n) {
            const t = void 0 !== e.base ? e.base : 1,
            n = [bn(e), 1 === t ? ["linear"] : ["exponential", t], ["number", o]];
            for (const e of r)
                kn(n, e[0], e[1], !1);
            return void 0 === e.default ? n : ["case", ["==", ["typeof", o], "number"], n, hn(e.default)]
        }
        throw new Error(`Unknown property function type ${n}`)
    }
    function wn(e) {
        "step" === e[0] && 3 === e.length && (e.push(0), e.push(e[3]))
    }
    function kn(e, t, r, n) {
        e.length > 3 && t === e[e.length - 2] || (n && 2 === e.length || e.push(t), e.push(r))
    }
    function Mn(e, t) {
        return e.type ? e.type : t.expression.interpolated ? "exponential" : "interval"
    }
    function zn(e) {
        const t = ["concat"],
        r = /{([^{}]+)}/g;
        let n = 0;
        for (let o = r.exec(e); null !== o; o = r.exec(e)) {
            const a = e.slice(n, r.lastIndex - o[0].length);
            n = r.lastIndex,
            a.length > 0 && t.push(a),
            t.push(["get", o[1]])
        }
        if (1 === t.length)
            return e;
        if (n < e.length)
            t.push(e.slice(n));
        else if (2 === t.length)
            return ["to-string", t[1]];
        return t
    }
    const Sn = R;
    function jn(e, t) {
        const r = t[0].evaluate(e),
        n = t[1].evaluate(e),
        o = t[2].evaluate(e),
        a = t[3] ? t[3].evaluate(e) : 1;
        return Fe.parse(`hsla(${r}, ${n}%, ${o}%, ${a})`)
    }
    function An(e) {
        if (Array.isArray(e)) {
            if (0 === e.length)
                return e;
            const t = e[0];
            if ("literal" === t)
                return e;
            if ("image" === t && 3 === e.length && "object" == typeof e[2] && null !== e[2] && !Array.isArray(e[2])) {
                return ["image-config", An(e[1]), ["literal", e[2]]]
            }
            const r = e.length;
            for (let n = 1; n < r; ++n) {
                const o = e[n],
                a = An(o);
                if (a !== o) {
                    const o = [t];
                    for (let t = 1; t < n; ++t)
                        o.push(e[t]);
                    o.push(a);
                    for (let t = n + 1; t < r; ++t)
                        o.push(An(e[t]));
                    return o
                }
            }
        }
        return e
    }
    const En = {},
    qn = {
        zoom: 0,
        distanceFromCenter: 0
    };
    Fr.register(Ir, {
        ...Fr.definitions,
        pitch: [{
                kind: "number"
            }, [], e => qn.pitch || 0],
        "distance-from-center": [{
                kind: "number"
            }, [], e => qn.distanceFromCenter || 0],
        "to-hsla": [{
                kind: "array",
                itemType: {
                    kind: "number"
                },
                N: 4
            }, [{
                    kind: "string"
                }
            ], (e, [t]) => function (e) {
                const t = e[0] / 255,
                r = e[1] / 255,
                n = e[2] / 255,
                o = e[3],
                a = Math.max(t, r, n),
                i = Math.min(t, r, n),
                s = (a + i) / 2;
                let l,
                u;
                if (a === i)
                    l = 0, u = 0;
                else {
                    const e = a - i;
                    switch (u = s > .5 ? e / (2 - a - i) : e / (a + i), a) {
                    case t:
                        l = (r - n) / e + (r < n ? 6 : 0);
                        break;
                    case r:
                        l = (n - t) / e + 2;
                        break;
                    case n:
                        l = (t - r) / e + 4;
                        break;
                    default:
                        l = 0
                    }
                    l /= 6
                }
                return [360 * l, 100 * u, 100 * s, o]
            }
            (w.fromString(t.evaluate(e)))],
        hsl: [{
                kind: "color"
            }, [{
                    kind: "number"
                }, {
                    kind: "number"
                }, {
                    kind: "number"
                }
            ], jn],
        hsla: [{
                kind: "color"
            }, [{
                    kind: "number"
                }, {
                    kind: "number"
                }, {
                    kind: "number"
                }, {
                    kind: "number"
                }
            ], jn],
        "image-config": [{
                kind: "value"
            }, [{
                    kind: "string"
                }, {
                    kind: "value"
                }
            ], (e, [t, r]) => t.evaluate(e)],
        "measure-light": [{
                kind: "number"
            }, [{
                    kind: "value"
                }
            ], () => 1],
        config: [{
                kind: "value"
            }, [{
                    kind: "string"
                }
            ], (e, [t]) => {
                const r = En[t.evaluate(e)];
                return void 0 === r ? {}
                 : r
            }
        ]
    });
    const $n = "https://api.mapbox.com";
    function Cn(e) {
        const t = "mapbox://";
        return 0 !== e.indexOf(t) ? "" : e.slice(9)
    }
    function _n(e, t, r) {
        const n = Cn(e);
        if (!t || !n)
            return decodeURI(new URL(e, r).href);
        const o = "sprites/";
        if (0 !== n.indexOf(o))
            throw new Error(`unexpected sprites url: ${e}`);
        const a = n.slice(8);
        return `${$n}/styles/v1/${a}/sprite?access_token=${t}`
    }
    function Tn(e, t) {
        const r = Cn(e);
        if (!r || !t)
            return decodeURI(new URL(e, location.href).href);
        const n = "styles/";
        if (0 !== r.indexOf(n))
            throw new Error(`unexpected style url: ${e}`);
        const o = r.slice(7);
        return `${$n}/styles/v1/${o}?&access_token=${t}`
    }
    const On = ["a", "b", "c", "d"];
    function Nn(e, t, r, n) {
        const o = new URL(e, n || location.href),
        a = Cn(e);
        if (!a)
            return t ? (o.searchParams.has(r) || o.searchParams.set(r, t), [decodeURI(o.href)]) : [decodeURI(o.href)];
        if ("mapbox.satellite" === a) {
            const e = window.devicePixelRatio >= 1.5 ? "@2x" : "";
            return [`https://api.mapbox.com/v4/${a}/{z}/{x}/{y}${e}.webp?access_token=${t}`]
        }
        return On.map(e => `https://${e}.tiles.mapbox.com/v4/${a}/{z}/{x}/{y}.vector.pbf?access_token=${t}`)
    }
    function Pn(e, t) {
        const r = e[0],
        n = r.width,
        o = r.height,
        a = r.data,
        i = new Uint8ClampedArray(a.length),
        s = 2 * t.resolution,
        l = n - 1,
        u = o - 1,
        c = [0, 0, 0, 0],
        p = Math.PI,
        f = t.encoding,
        d = t.exaggeration,
        m = t.zoom,
        y = t.method || "standard",
        h = t.accentColor,
        g = t.shadowColors || [t.shadowColor],
        b = t.highlightColors || [t.highlightColor],
        v = (t.azimuths || [t.sunAz]).map(e => e * p / 180),
        x = (t.altitudes || [45]).map(e => e * p / 180),
        w = Math.min(v.length, x.length, g.length, b.length, 4),
        k = m < 2 ? .4 : m < 4.5 ? .35 : .3,
        M = m < 15 ? Math.pow(2, (15 - m) * k) : 1;
        function z(e, t = "mapbox") {
            return "mapbox" === t ? .1 * (256 * e[0] * 256 + 256 * e[1] + e[2]) - 1e4 : "terrarium" === t ? 256 * e[0] + e[1] + e[2] / 256 - 32768 : 0
        }
        function S(e, t) {
            return 0 !== e ? Math.atan2(t, -e) : p / 2 * (t > 0 ? 1 : -1)
        }
        const j = "igor" === y ? function (e, t) {
            const r = S(e *= 2 * d, t *= 2 * d),
            n = v[0] + p,
            o = Math.atan(Math.sqrt(e * e + t * t)) * (2 / p);
            let a = (r + n) / p + .5;
            a %= 2,
            a < 0 && (a += 2);
            const i = 1 - Math.abs(a - 1),
            s = o * i,
            l = o * (1 - i),
            u = g[0],
            c = b[0];
            return [u.r * s + c.r * l, u.g * s + c.g * l, u.b * s + c.b * l, u.a * s + c.a * l]
        }
         : "basic" === y ? function (e, t) {
            e *= 2 * d,
            t *= 2 * d;
            const r = v[0] + p,
            n = Math.cos(r),
            o = Math.sin(r),
            a = Math.cos(x[0]),
            i = (Math.sin(x[0]) - (t * n * a - e * o * a)) / Math.sqrt(1 + e * e + t * t),
            s = Math.max(0, Math.min(1, i));
            if (s > .5) {
                const e = 2 * s - 1,
                t = b[0];
                return [t.r * e, t.g * e, t.b * e, t.a * e]
            }
            const l = 1 - 2 * s,
            u = g[0];
            return [u.r * l, u.g * l, u.b * l, u.a * l]
        }
         : "combined" === y ? function (e, t) {
            e *= 2 * d,
            t *= 2 * d;
            const r = v[0] + p,
            n = Math.cos(r),
            o = Math.sin(r),
            a = Math.cos(x[0]),
            i = Math.sin(x[0]);
            let s = Math.acos((i - (t * n * a - e * o * a)) / Math.sqrt(1 + e * e + t * t));
            s = Math.max(0, Math.min(p / 2, s));
            const l = Math.atan(Math.sqrt(e * e + t * t)) * (4 / p / p),
            u = s * l,
            c = (p / 2 - s) * l,
            f = g[0],
            m = b[0];
            return [f.r * u + m.r * c, f.g * u + m.g * c, f.b * u + m.b * c, f.a * u + m.a * c]
        }
         : "multidirectional" === y ? function (e, t) {
            const r = (e *= 2 * d) * e + (t *= 2 * d) * t,
            n = Math.sqrt(1 + r);
            let o = 0,
            a = 0,
            i = 0,
            s = 0;
            for (let r = 0; r < w; r++) {
                const l = Math.cos(x[r]),
                u = (Math.sin(x[r]) - (t * -Math.cos(v[r]) * l - e * -Math.sin(v[r]) * l)) / n,
                c = Math.max(0, Math.min(1, u)),
                p = g[Math.min(r, g.length - 1)],
                f = b[Math.min(r, b.length - 1)];
                if (c > .5) {
                    const e = (2 * c - 1) / w;
                    o += f.r * e,
                    a += f.g * e,
                    i += f.b * e,
                    s += f.a * e
                } else {
                    const e = (1 - 2 * c) / w;
                    o += p.r * e,
                    a += p.g * e,
                    i += p.b * e,
                    s += p.a * e
                }
            }
            return [o, a, i, s]
        }
         : function (e, t) {
            const r = v[0] + p,
            n = Math.atan(.625 * Math.sqrt(e * e + t * t)),
            o = S(e, t),
            a = 1.875 - 1.75 * d,
            i = .5 * p,
            s = .5 !== d ? (Math.pow(a, n) - 1) / (Math.pow(a, i) - 1) * i : n,
            l = Math.cos(s),
            u = Math.min(Math.max(2 * d, 0), 1),
            c = (1 - l) * u,
            f = h,
            m = f.r * c,
            y = f.g * c,
            x = f.b * c,
            w = f.a * c;
            let k = (o + r) / p + .5;
            k %= 2,
            k < 0 && (k += 2);
            const M = Math.abs(k - 1),
            z = Math.sin(s) * u,
            j = g[0],
            A = b[0],
            E = (j.r * (1 - M) + A.r * M) * z,
            q = (j.g * (1 - M) + A.g * M) * z,
            $ = (j.b * (1 - M) + A.b * M) * z,
            C = (j.a * (1 - M) + A.a * M) * z;
            return [m * (1 - C) + E, y * (1 - C) + q, x * (1 - C) + $, w * (1 - C) + C]
        };
        let A,
        E,
        q,
        $,
        C,
        _,
        T,
        O,
        N,
        P,
        I;
        for (E = 0; E <= u; ++E)
            for (C = 0 === E ? 0 : E - 1, _ = E === u ? u : E + 1, A = 0; A <= l; ++A) {
                q = 0 === A ? 0 : A - 1,
                $ = A === l ? l : A + 1,
                T = 4 * (E * n + q),
                c[0] = a[T],
                c[1] = a[T + 1],
                c[2] = a[T + 2],
                c[3] = a[T + 3],
                O = z(c, f),
                T = 4 * (E * n + $),
                c[0] = a[T],
                c[1] = a[T + 1],
                c[2] = a[T + 2],
                c[3] = a[T + 3],
                N = z(c, f),
                P = (N - O) / s * M,
                T = 4 * (C * n + A),
                c[0] = a[T],
                c[1] = a[T + 1],
                c[2] = a[T + 2],
                c[3] = a[T + 3],
                O = z(c, f),
                T = 4 * (_ * n + A),
                c[0] = a[T],
                c[1] = a[T + 1],
                c[2] = a[T + 2],
                c[3] = a[T + 3],
                N = z(c, f),
                I = (N - O) / s * M;
                const e = j(P, I),
                t = e[3];
                T = 4 * (E * n + A),
                t > 0 && (i[T] = e[0] / t * 255, i[T + 1] = e[1] / t * 255, i[T + 2] = e[2] / t * 255),
                i[T + 3] = 255 * t
            }
        return new ImageData(i, n, o)
    }
    function In(e, t) {
        const r = e[0],
        n = r.width,
        o = r.height,
        a = r.data,
        i = new Uint8ClampedArray(a.length),
        s = n - 1,
        l = o - 1,
        u = [0, 0, 0, 0];
        let c,
        p,
        f;
        const d = (m = t.saturation) > 0 ? 1 - 1 / (1.001 - m) : -m;
        var m;
        const y = (h = t.contrast) > 0 ? 1 / (1 - h) : 1 + h;
        var h;
        const g = function (e) {
            e *= Math.PI / 180;
            const t = Math.sin(e),
            r = Math.cos(e);
            return [(2 * r + 1) / 3, (-Math.sqrt(3) * t - r + 1) / 3, (Math.sqrt(3) * t - r + 1) / 3]
        }
        (t.hueRotate),
        b = g,
        v = [g[2], g[0], g[1]],
        x = [g[1], g[2], g[0]],
        w = t.brightnessLow,
        k = t.brightnessHigh;
        for (p = 0; p <= l; ++p)
            for (c = 0; c <= s; ++c) {
                f = 4 * (p * n + c),
                u[0] = a[f],
                u[1] = a[f + 1],
                u[2] = a[f + 2],
                u[3] = a[f + 3];
                const e = u[0],
                t = u[1],
                r = u[2],
                o = (e, t) => {
                    let r = 0;
                    for (let n = 0; n < e.length; n++)
                        r += e[n] * t[n];
                    return r
                };
                let s = o([e, t, r], b),
                l = o([e, t, r], v),
                m = o([e, t, r], x);
                const h = (s + l + m) / 3;
                s += (h - s) * d,
                l += (h - l) * d,
                m += (h - m) * d,
                s = (s - 127.5) * y + 127.5,
                l = (l - 127.5) * y + 127.5,
                m = (m - 127.5) * y + 127.5,
                s = w * (255 - s) + k * s,
                l = w * (255 - l) + k * l,
                m = w * (255 - m) + k * m,
                i[f] = s,
                i[f + 1] = l,
                i[f + 2] = m,
                i[f + 3] = u[3]
            }
        return new ImageData(i, n, o)
    }
    var Fn = {
        thin: 100,
        hairline: 100,
        "ultra-light": 200,
        "extra-light": 200,
        light: 300,
        book: 300,
        regular: 400,
        normal: 400,
        plain: 400,
        roman: 400,
        standard: 400,
        medium: 500,
        "semi-bold": 600,
        "demi-bold": 600,
        bold: 700,
        "extra-bold": 800,
        "ultra-bold": 800,
        heavy: 900,
        black: 900,
        "heavy-black": 900,
        fat: 900,
        poster: 900,
        "ultra-black": 950,
        "extra-black": 950
    },
    Rn = " ",
    Ln = /(italic|oblique)$/i,
    Dn = {};
    function Un(e, t, r) {
        var n = Dn[e];
        if (!n) {
            Array.isArray(e) || (e = [e]);
            for (var o, a, i = 400, s = "normal", l = [], u = 0, c = e.length; u < c; ++u) {
                var p = e[u].split(" "),
                f = p[p.length - 1].toLowerCase();
                for (var d in "normal" == f || "italic" == f || "oblique" == f ? (s = a ? s : f, a = !0, p.pop(), f = p[p.length - 1].toLowerCase()) : Ln.test(f) && (f = f.replace(Ln, ""), s = a ? s : p[p.length - 1].replace(f, ""), a = !0), Fn) {
                    var m = p.length > 1 ? p[p.length - 2].toLowerCase() : "";
                    if (f == d || f == d.replace("-", "") || m + "-" + f == d) {
                        i = o ? i : Fn[d],
                        p.pop(),
                        m && d.startsWith(m) && p.pop();
                        break
                    }
                }
                o || "number" != typeof f || (i = f, o = !0);
                var y = p.join(Rn).replace("Klokantech Noto Sans", "Noto Sans").replace("DIN Pro", "Barlow").replace("Arial Unicode MS", "Arial");
                -1 !== y.indexOf(Rn) && (y = '"' + y + '"'),
                l.push(y)
            }
            n = Dn[e] = [s, i, l]
        }
        return n[0] + Rn + n[1] + Rn + t + "px" + (r ? "/" + r : "") + Rn + n[2]
    }
    const Gn = Object.freeze({}),
    Vn = {},
    Jn = {};
    let Wn = 0;
    function Zn(e) {
        return e.id || (e.id = Wn++),
        e.id
    }
    function Bn(e, t) {
        return Zn(e) + "." + P.getUid(t)
    }
    function Hn(e) {
        let t = Vn[e.id];
        return t || (t = {}, Vn[Zn(e)] = t),
        t
    }
    function Xn(e) {
        let t = Jn[e.id];
        return t || (t = {}, Jn[Zn(e)] = t),
        t
    }
    function Kn(e) {
        return e * Math.PI / 180
    }
    const Yn = function () {
        const e = [];
        for (let t = 78271.51696402048; e.length <= 24; t /= 2)
            e.push(t);
        return e
    }
    ();
    function Qn(e, t) {
        if ("undefined" != typeof WorkerGlobalScope && self instanceof WorkerGlobalScope && "undefined" != typeof OffscreenCanvas)
            return new OffscreenCanvas(e, t);
        const r = document.createElement("canvas");
        return r.width = e,
        r.height = t,
        r
    }
    function eo(e, t) {
        let r = 0;
        const n = t.length;
        for (; r < n; ++r) {
            if (t[r] < e && r + 1 < n) {
                const n = t[r] / t[r + 1];
                return r + Math.log(t[r] / e) / Math.log(n)
            }
        }
        return n - 1
    }
    function to(e, t) {
        const r = Math.floor(e),
        n = Math.pow(2, e - r);
        return t[r] / n
    }
    const ro = {};
    function no(e, t, r = {}, n) {
        if (t in ro)
            return n && (n.url = ro[t][0].url), ro[t][1];
        const o = r.transformRequest && r.transformRequest(t, e) || t,
        a = function (e) {
            return delete ro[t],
            Promise.reject(new Error("Error fetching source " + t))
        },
        i = function (e) {
            return delete ro[t],
            e.ok ? e.json() : Promise.reject(new Error("Error fetching source " + t))
        },
        s = S.toPromise(() => o).then(e => e instanceof Response ? (n && (n.url = e.url), i(e)) : (e instanceof Request || (e = new Request(e)), e.headers.get("Accept") || e.headers.set("Accept", "application/json"), n && (n.url = e.url), fetch(e).then(i).catch(a))).catch(a);
        return ro[t] = [o, s],
        s
    }
    function oo(e, t) {
        if ("string" != typeof e)
            return Promise.resolve(e);
        if (!e.trim().startsWith("{"))
            return no("Style", e = Tn(e, t.accessToken), t);
        try {
            const t = JSON.parse(e);
            return Promise.resolve(t)
        } catch (e) {
            return Promise.reject(e)
        }
    }
    const ao = {};
    function io(e, t, r = {}) {
        const n = [t, JSON.stringify(e)].toString();
        let o = ao[n];
        if (!o || r.transformRequest) {
            let a;
            r.transformRequest && (a = (e, t) => {
                const n = r.transformRequest && r.transformRequest(t, "Tiles") || t;
                if (e instanceof O.VectorTile)
                    e.setLoader((t, r, o) => {
                        const a = function (r) {
                            r.arrayBuffer().then(r => {
                                const n = e.getFormat().readFeatures(r, {
                                    extent: t,
                                    featureProjection: o
                                });
                                e.setFeatures(n)
                            })
                        };
                        S.toPromise(() => n).then(t => {
                            if (t instanceof Response)
                                return a(t);
                            fetch(t).then(a).catch(t => e.setState(N.ERROR))
                        }).catch(t => e.setState(N.ERROR))
                    });
                else {
                    const t = e.getImage();
                    S.toPromise(() => n).then(r => {
                        if ("string" == typeof r)
                            return void(t.src = r);
                        const n = e => e.blob().then(e => {
                            const r = URL.createObjectURL(e);
                            t.addEventListener("load", () => URL.revokeObjectURL(r)),
                            t.addEventListener("error", () => URL.revokeObjectURL(r)),
                            t.src = r
                        });
                        if (r instanceof Response)
                            return n(r);
                        fetch(r).then(n).catch(t => e.setState(N.ERROR))
                    }).catch(t => e.setState(N.ERROR))
                }
            });
            const i = e.url;
            if (i && !e.tiles) {
                const n = Nn(i, r.accessToken, r.accessTokenParam || "access_token", t || location.href);
                if (i.startsWith("mapbox://"))
                    o = Promise.resolve({
                        tileJson: Object.assign({}, e, {
                            url: void 0,
                            tiles: n
                        }),
                        tileLoadFunction: a
                    });
                else {
                    const e = {};
                    o = no("Source", n[0], r, e).then(function (t) {
                        return t.tiles = t.tiles.map(function (n) {
                            return "tms" === t.scheme && (n = n.replace("{y}", "{-y}")),
                            Nn(n, r.accessToken, r.accessTokenParam || "access_token", e.url)[0]
                        }),
                        Promise.resolve({
                            tileJson: t,
                            tileLoadFunction: a
                        })
                    })
                }
            } else
                e.tiles ? (e = Object.assign({}, e, {
                        tiles: e.tiles.map(function (n) {
                            return "tms" === e.scheme && (n = n.replace("{y}", "{-y}")),
                            Nn(n, r.accessToken, r.accessTokenParam || "access_token", t || location.href)[0]
                        })
                    }), o = Promise.resolve({
                        tileJson: Object.assign({}, e),
                        tileLoadFunction: a
                    })) : o = Promise.reject(new Error("source has no `tiles` nor `url`"));
            ao[n] = o
        }
        return o
    }
    function so(e, t, r, n) {
        const o = [2 * r * t.pixelRatio + t.width, 2 * r * t.pixelRatio + t.height],
        a = Qn(o[0], o[1]),
        i = a.getContext("2d");
        i.drawImage(e, t.x, t.y, t.width, t.height, r * t.pixelRatio, r * t.pixelRatio, t.width, t.height);
        const s = i.getImageData(0, 0, o[0], o[1]);
        i.globalCompositeOperation = "destination-over",
        i.fillStyle = `rgba(${255 * n.r},${255 * n.g},${255 * n.b},${n.a})`;
        const l = s.data;
        for (let e = 0, n = s.width; e < n; ++e)
            for (let o = 0, a = s.height; o < a; ++o) {
                l[4 * (o * n + e) + 3] > 0 && i.arc(e, o, r * t.pixelRatio, 0, 2 * Math.PI)
            }
        return i.fill(),
        a
    }
    function lo(e, t, r) {
        const n = Math.max(0, Math.min(1, (r - e) / (t - e)));
        return n * n * (3 - 2 * n)
    }
    function uo(e, t, r) {
        const n = Qn(t.width, t.height),
        o = n.getContext("2d");
        o.drawImage(e, t.x, t.y, t.width, t.height, 0, 0, t.width, t.height);
        const a = o.getImageData(0, 0, t.width, t.height),
        i = a.data;
        for (let e = 0, t = a.width; e < t; ++e)
            for (let n = 0, o = a.height; n < o; ++n) {
                const o = 4 * (n * t + e),
                a = .75,
                s = .1,
                l = lo(a - s, a + s, i[o + 3] / 255);
                l > 0 ? (i[o + 0] = Math.round(255 * r.r * l), i[o + 1] = Math.round(255 * r.g * l), i[o + 2] = Math.round(255 * r.b * l), i[o + 3] = Math.round(255 * l)) : i[o + 3] = 0
            }
        return o.putImageData(a, 0, 0),
        n
    }
    const co = Array(256).join(" ");
    function po(e, t) {
        if (t >= .05) {
            let r = "";
            const n = e.split("\n"),
            o = co.slice(0, Math.round(t / .1));
            for (let e = 0, t = n.length; e < t; ++e)
                e > 0 && (r += "\n"), r += n[e].split("").join(o);
            return r
        }
        return e
    }
    let fo;
    function mo() {
        return fo || (fo = Qn(1, 1).getContext("2d")),
        fo
    }
    function yo(e, t) {
        if (/\d+ \d+/.test(e)) {
            const [r, n] = e.split(" ").map(Number);
            return r <= t && t <= n
        }
        return e == t
    }
    function ho(e, t) {
        return mo().measureText(e).width + (e.length - 1) * t
    }
    const go = {};
    function bo(e, t, r, n) {
        if (-1 !== e.indexOf("\n")) {
            const o = e.split("\n"),
            a = [];
            for (let e = 0, i = o.length; e < i; ++e)
                a.push(bo(o[e], t, r, n));
            return a.join("\n")
        }
        const o = r + "," + t + "," + e + "," + n;
        let a = go[o];
        if (!a) {
            const i = e.split(" ");
            if (i.length > 1) {
                const e = mo();
                e.font = t;
                const o = e.measureText("M").width * r;
                let s = "";
                const l = [];
                for (let e = 0, t = i.length; e < t; ++e) {
                    const t = i[e],
                    r = s + (s ? " " : "") + t;
                    ho(r, n) <= o ? s = r : (s && l.push(s), s = t)
                }
                s && l.push(s);
                for (let e = 0, t = l.length; e < t && t > 1; ++e) {
                    const r = l[e];
                    if (ho(r, n) < .35 * o) {
                        const o = e > 0 ? ho(l[e - 1], n) : 1 / 0,
                        a = e < t - 1 ? ho(l[e + 1], n) : 1 / 0;
                        l.splice(e, 1),
                        t -= 1,
                        o < a ? (l[e - 1] += " " + r, e -= 1) : l[e] = r + " " + l[e]
                    }
                }
                for (let e = 0, t = l.length - 1; e < t; ++e) {
                    const r = l[e],
                    a = l[e + 1];
                    if (ho(r, n) > .7 * o && ho(a, n) < .6 * o) {
                        const i = r.split(" "),
                        s = i.pop();
                        ho(s, n) < .2 * o && (l[e] = i.join(" "), l[e + 1] = s + " " + a),
                        t -= 1
                    }
                }
                a = l.join("\n")
            } else
                a = e;
            a = po(a, n),
            go[o] = a
        }
        return a
    }
    T.checkedFonts.on("propertychange", () => {
        for (const e in go)
            delete go[e]
    });
    const vo = ["Arial", "Courier New", "Times New Roman", "Verdana", "sans-serif", "serif", "monospace", "cursive", "fantasy"],
    xo = {};
    const wo = {
        Point: 1,
        MultiPoint: 1,
        LineString: 2,
        MultiLineString: 2,
        Polygon: 3,
        MultiPolygon: 3
    },
    ko = {
        center: [.5, .5],
        left: [0, .5],
        right: [1, .5],
        top: [.5, 0],
        bottom: [.5, 1],
        "top-left": [0, 0],
        "top-right": [1, 0],
        "bottom-left": [0, 1],
        "bottom-right": [1, 1]
    },
    Mo = function (e, t) {
        let r = tn(e, t);
        if ("error" === r.result) {
            const n = An(e);
            n !== e && (r = tn(n, t))
        }
        if ("error" === r.result) {
            const n = r.value[0];
            return console.error("Error parsing expression:", e, n.key, n.message), {
                evaluate: () => t.default
            }
        }
        return r.value
    };
    let zo,
    So;
    function jo(e, t, r, n, o, a) {
        const i = e.id;
        o || (o = {}, console.warn("No functionCache provided to getValue()")),
        o[i] || (o[i] = {});
        const s = o[i];
        if (!s[r]) {
            let n = (e[t] || Gn)[r];
            const o = Sn[`${t}_${e.type}`] && Sn[`${t}_${e.type}`][r];
            void 0 === n && o && (n = o.default);
            let a = Kr(n);
            if (!a && Hr(n) && (n = gn(n, o), a = !0), a) {
                const e = Mo(n, o);
                s[r] = e.evaluate.bind(e)
            } else {
                const e = o ? o.type : typeof n;
                "color" !== e && "colorArray" !== e || (n = Fe.parse(n));
                let t = !1;
                if ("array" === e)
                    for (let e = 0; e < n.length; ++e) {
                        const r = n[e];
                        if (Kr(r) || Hr(r)) {
                            t = !0;
                            break
                        }
                    }
                if (t) {
                    const e = Object.assign({}, o, {
                        type: o.value
                    }),
                    t = [];
                    for (let r = 0; r < n.length; ++r) {
                        let o = n[r];
                        if (!Kr(o) && Hr(o) && (o = gn(o, e)), Kr(o)) {
                            const r = Mo(o, e);
                            t.push(r.evaluate.bind(r))
                        } else
                            t.push(function () {
                                return o
                            })
                    }
                    s[r] = function (e, r, n) {
                        const o = [];
                        for (let a = 0; a < t.length; ++a)
                            o[a] = t[a](e, r, n);
                        return o
                    }
                } else
                    s[r] = function () {
                        return n
                    }
            }
        }
        return s[r](qn, n, a)
    }
    function Ao(e, t, r, n) {
        if (!jo(e, "layout", `${r}-allow-overlap`, t, n))
            return "declutter";
        return jo(e, "layout", `${r}-ignore-placement`, t, n) ? "none" : "obstacle"
    }
    function Eo(e, t, r, n) {
        if (n || console.warn("No filterCache provided to evaluateFilter()"), !(e in n))
            try {
                n[e] = ln(t).filter
            } catch (t) {
                console.warn("Filter will evaluate to false: " + t.message),
                n[e] = function () {
                    return !1
                }
            }
        return n[e](qn, r)
    }
    let qo = !1;
    function $o(e, t) {
        if (e) {
            if (!qo && (0 === e.a || 0 === t))
                return;
            const r = e.a;
            return t = void 0 === t ? 1 : t,
            0 === r ? "transparent" : "rgba(" + Math.round(255 * e.r / r) + "," + Math.round(255 * e.g / r) + "," + Math.round(255 * e.b / r) + "," + r * t + ")"
        }
        return e
    }
    const Co = /\{[^{}}]*\}/g;
    function _o(e, t) {
        return e.replace(Co, function (e) {
            return t[e.slice(1, -1)] || ""
        })
    }
    function To(e, t) {
        let r = e.split(":")[0];
        return r === e && (r = "default"),
        t[r]
    }
    let Oo = !1;
    const No = {};
    function Po(e, r, o, a = Yn, i = void 0, s = void 0, l = void 0, u = void 0) {
        if ("string" == typeof r && (r = JSON.parse(r)), r.schema)
            for (const e in r.schema) {
                const t = r.schema[e];
                "default" in t && (En[e] = t.default)
            }
        if (8 != r.version)
            throw new Error("glStyle version 8 required.");
        No[Bn(r, e)] = Array.from(arguments);
        const c = {};
        ("string" == typeof s || s instanceof Request || s instanceof Response || s instanceof Promise) && (s = {
            default:
                s
            });
        for (const t in s) {
            const r = s[t];
            S.toPromise(() => r).then(async r => {
                let n;
                if ("undefined" != typeof Image) {
                    const o = new Image;
                    if ("string" == typeof r)
                        o.crossOrigin = "anonymous", o.src = r;
                    else {
                        let e;
                        r instanceof Request ? e = await fetch(r) : r instanceof Response && (e = r);
                        const t = await e.blob();
                        n = URL.createObjectURL(t),
                        o.src = n
                    }
                    o.addEventListener("load", function r() {
                        o.removeEventListener("load", r),
                        c[t] = {
                            image: o,
                            size: [o.width, o.height]
                        },
                        e.changed(),
                        n && URL.revokeObjectURL(n)
                    }),
                    o.addEventListener("error", function e() {
                        URL.revokeObjectURL(n),
                        o.removeEventListener("error", e)
                    })
                } else if ("undefined" != typeof WorkerGlobalScope && self instanceof WorkerGlobalScope) {
                    const e = self;
                    e.postMessage({
                        action: "loadImage",
                        src: r
                    }),
                    e.addEventListener("message", function (e) {
                        "imageLoaded" === e.data.action && e.data.src === r && (c[t] = {
                                image: e.data.image,
                                size: [e.data.image.width, e.data.image.height]
                            })
                    })
                }
            })
        }
        const p = U(r.layers),
        f = {},
        d = [],
        m = {},
        y = {},
        h = Hn(r),
        g = Xn(r);
        let b;
        for (let e = 0, t = p.length; e < t; ++e) {
            const t = p[e],
            n = t.id;
            if ("string" == typeof o && t.source == o || Array.isArray(o) && -1 !== o.indexOf(n)) {
                const o = t["source-layer"];
                if (b) {
                    if (t.source !== b)
                        throw new Error(`Layer "${n}" does not use source "${b}`)
                } else {
                    b = t.source;
                    const e = r.sources[b];
                    if (!e)
                        throw new Error(`Source "${b}" is not defined`);
                    const n = e.type;
                    if ("vector" !== n && "geojson" !== n)
                        throw new Error(`Source "${b}" is not of type "vector" or "geojson", but "${n}"`)
                }
                let a = f[o];
                a || (a = [], f[o] = a),
                a.push({
                    layer: t,
                    index: e
                }),
                d.push(n)
            }
        }
        const v = [],
        x = function (o, s, p) {
            const d = e.getSource?.()?.format_?.layerName_ ?? "mvt:layer",
            b = o.getProperties(),
            x = f[b[d]];
            if (!x)
                return;
            let w = a.indexOf(s);
            -1 == w && (w = eo(s, a)),
            qn.zoom = w,
            qn.distanceFromCenter = 0;
            const k = o.getGeometry(),
            M = wo[k.getType()],
            S = e.get("map");
            if (S && S instanceof t && 1 === M) {
                const e = S.getSize();
                if (e) {
                    const t = S.getView().getCenter(),
                    r = n.getCenter(k.getExtent());
                    qn.distanceFromCenter = z.distance(t, r) / s / e[1]
                }
            }
            const T = {
                id: o.getId(),
                properties: b,
                type: M
            },
            O = e.get("mapbox-featurestate")[o.getId()];
            let N,
            P = -1;
            for (let t = 0, n = x.length; t < n; ++t) {
                const n = x[t],
                a = n.layer,
                f = a.id;
                if (void 0 !== p && p !== f)
                    continue;
                const d = a.layout || Gn,
                k = a.paint || Gn;
                if ("none" === jo(a, "layout", "visibility", T, h, O) || "minzoom" in a && w < a.minzoom || "maxzoom" in a && w >= a.maxzoom)
                    continue;
                const z = a.filter;
                if (!z || Eo(f, z, T, g)) {
                    let t,
                    p,
                    f,
                    g,
                    x,
                    w;
                    N = a;
                    const z = n.index;
                    if (3 == M && ("fill" == a.type || "fill-extrusion" == a.type))
                        if (p = jo(a, "paint", a.type + "-opacity", T, h, O), a.type + "-pattern" in k) {
                            const e = jo(a, "paint", a.type + "-pattern", T, h, O);
                            if (e) {
                                const t = "string" == typeof e ? _o(e, b) : e.toString(),
                                r = To(t, c);
                                if (i && i[t] && r) {
                                    ++P,
                                    w = v[P],
                                    w && w.getFill() && !w.getStroke() && !w.getText() || (w = new C({
                                            fill: new E
                                        }), v[P] = w),
                                    f = w.getFill(),
                                    w.setZIndex(z);
                                    const e = t + "." + p;
                                    let n = y[e];
                                    if (!n) {
                                        const o = i[t],
                                        a = Qn(o.width, o.height),
                                        s = a.getContext("2d");
                                        s.globalAlpha = p,
                                        s.drawImage(r.image, o.x, o.y, o.width, o.height, 0, 0, o.width, o.height),
                                        n = s.createPattern(a, "repeat"),
                                        y[e] = n
                                    }
                                    f.setColor(n)
                                }
                            }
                        } else if (t = $o(jo(a, "paint", a.type + "-color", T, h, O), p), a.type + "-outline-color" in k && (x = $o(jo(a, "paint", a.type + "-outline-color", T, h, O), p)), x || (x = t), t || x) {
                            if (++P, w = v[P], (!w || t && !w.getFill() || !t && w.getFill() || x && !w.getStroke() || !x && w.getStroke() || w.getText()) && (w = new C({
                                        fill: t ? new E : void 0,
                                        stroke: x ? new $ : void 0
                                    }), v[P] = w), t && (f = w.getFill(), f.setColor(t)), "fill-extrusion" === a.type) {
                                const e = jo(a, "paint", "fill-extrusion-height", T, h, O);
                                if (e > 0) {
                                    const t = Math.max(.1, .9 - Math.min(e, 225) / 280);
                                    if (x && "transparent" !== x) {
                                        const e = Fe.parse(x);
                                        x = `rgba(${Math.round(255 * e.r * t)},${Math.round(255 * e.g * t)},${Math.round(255 * e.b * t)},${e.a})`
                                    }
                                }
                            }
                            x && (g = w.getStroke(), g.setColor(x), g.setWidth(.5)),
                            w.setZIndex(z)
                        }
                    if (1 != M && "line" == a.type) {
                        t = "line-pattern" in k ? void 0 : $o(jo(a, "paint", "line-color", T, h, O), jo(a, "paint", "line-opacity", T, h, O));
                        const e = jo(a, "paint", "line-width", T, h, O);
                        t && e > 0 && (++P, w = v[P], w && w.getStroke() && !w.getFill() && !w.getText() || (w = new C({
                                    stroke: new $
                                }), v[P] = w), g = w.getStroke(), g.setLineCap(jo(a, "layout", "line-cap", T, h, O)), g.setLineJoin(jo(a, "layout", "line-join", T, h, O)), g.setMiterLimit(jo(a, "layout", "line-miter-limit", T, h, O)), g.setColor(t), g.setWidth(e), g.setLineDash(k["line-dasharray"] ? jo(a, "paint", "line-dasharray", T, h, O).map(function (t) {
                                    return t * e
                                }) : null), "function" == typeof g.setOffset && g.setOffset(jo(a, "paint", "line-offset", T, h, O)), w.setZIndex(z))
                    }
                    let S,
                    I,
                    F,
                    R,
                    L,
                    D,
                    U,
                    G,
                    V,
                    J = !1,
                    W = null,
                    Z = 0;
                    if ((1 == M || 2 == M) && "icon-image" in d) {
                        const t = jo(a, "layout", "icon-image", T, h, O);
                        if (t) {
                            let r;
                            S = "string" == typeof t ? _o(t, b) : t.toString();
                            const n = u ? u(e, S) : void 0,
                            l = To(S, c);
                            if (i && i[S] && l || n) {
                                const e = jo(a, "layout", "icon-rotation-alignment", T, h, O);
                                if (2 == M) {
                                    const t = o.getGeometry();
                                    if (t.getFlatMidpoint || t.getFlatMidpoints) {
                                        const n = t.getExtent();
                                        if (Math.sqrt(Math.max(Math.pow((n[2] - n[0]) / s, 2), Math.pow((n[3] - n[1]) / s, 2))) > 150) {
                                            const n = "MultiLineString" === t.getType() ? t.getFlatMidpoints() : t.getFlatMidpoint();
                                            So || (zo = [NaN, NaN], So = new j("Point", zo, [], 2, {}, void 0)),
                                            r = So,
                                            zo[0] = n[0],
                                            zo[1] = n[1];
                                            if ("line" === jo(a, "layout", "symbol-placement", T, h, O) && "map" === e) {
                                                const e = t.getStride(),
                                                r = t.getFlatCoordinates();
                                                for (let t = 0, o = r.length - e; t < o; t += e) {
                                                    const o = r[t],
                                                    a = r[t + 1],
                                                    i = r[t + e],
                                                    s = r[t + e + 1],
                                                    l = Math.min(o, i),
                                                    u = Math.max(o, i),
                                                    c = n[0],
                                                    p = (s - a) * (c - o) - (i - o) * (n[1] - a);
                                                    if (Math.abs(p) < .001 && c <= u && c >= l) {
                                                        Z = Math.atan2(a - s, i - o);
                                                        break
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                                if (2 !== M || r) {
                                    const t = jo(a, "layout", "icon-size", T, h, O),
                                    o = void 0 !== k["icon-color"] ? jo(a, "paint", "icon-color", T, h, O) : null;
                                    if (!o || 0 !== o.a) {
                                        const r = jo(a, "paint", "icon-halo-color", T, h, O),
                                        s = jo(a, "paint", "icon-halo-width", T, h, O);
                                        let u = `${S}.${t}.${s}.${r}`;
                                        if (null !== o && (u += `.${o}`), I = m[u], !I) {
                                            const c = Ao(a, T, "icon", h);
                                            let p;
                                            "icon-offset" in d && (p = jo(a, "layout", "icon-offset", T, h, O).slice(0), p[0] *= t, p[1] *= -t);
                                            let f = o ? [255 * o.r, 255 * o.g, 255 * o.b, o.a] : void 0;
                                            if (n) {
                                                const r = {
                                                    color: f,
                                                    rotateWithView: "map" === e,
                                                    displacement: p,
                                                    declutterMode: c,
                                                    scale: t
                                                };
                                                "string" == typeof n ? r.src = n : (r.img = n, r.imgSize = [n.width, n.height]),
                                                I = new q(r)
                                            } else {
                                                const n = i[S];
                                                let a,
                                                u,
                                                d;
                                                if (s)
                                                    n.sdf ? (a = so(uo(l.image, n, o || [0, 0, 0, 1]), {
                                                            x: 0,
                                                            y: 0,
                                                            width: n.width,
                                                            height: n.height,
                                                            pixelRatio: n.pixelRatio
                                                        }, s, r), f = void 0) : a = so(l.image, n, s, r);
                                                else {
                                                    if (n.sdf && !l.unSDFed) {
                                                        const e = uo(l.image, {
                                                            x: 0,
                                                            y: 0,
                                                            width: l.size[0],
                                                            height: l.size[1]
                                                        }, {
                                                            r: 1,
                                                            g: 1,
                                                            b: 1
                                                        });
                                                        l.image = e,
                                                        l.unSDFed = !0
                                                    }
                                                    a = l.image,
                                                    u = [n.width, n.height],
                                                    d = [n.x, n.y]
                                                }
                                                I = new q({
                                                    color: f,
                                                    img: a,
                                                    imgSize: l.size,
                                                    size: u,
                                                    offset: d,
                                                    rotateWithView: "map" === e,
                                                    scale: t / n.pixelRatio,
                                                    displacement: p,
                                                    declutterMode: c
                                                })
                                            }
                                            m[u] = I
                                        }
                                    }
                                    I && (++P, w = v[P], w && w.getImage() && !w.getFill() && !w.getStroke() || (w = new C, v[P] = w), w.setGeometry(r), I.setRotation(Z + Kn(jo(a, "layout", "icon-rotate", T, h, O))), I.setOpacity(jo(a, "paint", "icon-opacity", T, h, O)), I.setAnchor(ko[jo(a, "layout", "icon-anchor", T, h, O)]), w.setImage(I), W = w.getText(), w.setText(void 0), w.setZIndex(z), J = !0, F = !1)
                                } else
                                    F = !0
                            }
                        }
                    }
                    if (1 == M && "circle" === a.type) {
                        ++P,
                        w = v[P],
                        w && w.getImage() && !w.getFill() && !w.getStroke() || (w = new C, v[P] = w);
                        const e = "circle-radius" in k ? jo(a, "paint", "circle-radius", T, h, O) : 5,
                        t = $o(jo(a, "paint", "circle-stroke-color", T, h, O), jo(a, "paint", "circle-stroke-opacity", T, h, O)),
                        r = jo(a, "paint", "circle-translate", T, h, O),
                        n = $o(jo(a, "paint", "circle-color", T, h, O), jo(a, "paint", "circle-opacity", T, h, O)),
                        o = jo(a, "paint", "circle-stroke-width", T, h, O),
                        i = e + "." + t + "." + n + "." + o + "." + r[0] + "." + r[1];
                        I = m[i],
                        I || (I = new A({
                                radius: e,
                                displacement: [r[0], -r[1]],
                                stroke: t && o > 0 ? new $({
                                    width: o,
                                    color: t
                                }) : void 0,
                                fill: n ? new E({
                                    color: n
                                }) : void 0,
                                declutterMode: "none"
                            }), m[i] = I),
                        w.setImage(I),
                        W = w.getText(),
                        w.setText(void 0),
                        w.setGeometry(void 0),
                        w.setZIndex(z),
                        J = !0
                    }
                    if ("text-field" in d) {
                        U = Math.round(jo(a, "layout", "text-size", T, h, O));
                        const e = jo(a, "layout", "text-font", T, h, O);
                        D = jo(a, "layout", "text-line-height", T, h, O),
                        L = Un(l ? l(e, r.metadata ? r.metadata["ol:webfonts"] : void 0) : e, U, D),
                        L.includes("sans-serif") || (L += ",sans-serif"),
                        G = jo(a, "layout", "text-letter-spacing", T, h, O),
                        V = jo(a, "layout", "text-max-width", T, h, O);
                        const t = jo(a, "layout", "text-field", T, h, O);
                        R = "object" == typeof t && t.sections ? 1 === t.sections.length ? t.toString() : t.sections.reduce((t, r, n) => {
                            const o = r.fontStack ? r.fontStack.split(",") : e,
                            a = Un(l ? l(o) : o, U * (r.scale || 1), D);
                            let i = r.text;
                            if ("\n" === i)
                                return t.push("\n", ""), t;
                            if (2 == M)
                                return t.push(po(i, G), a), t;
                            i = bo(i, a, V, G).split("\n");
                            for (let e = 0, r = i.length; e < r; ++e)
                                e > 0 && t.push("\n", ""), t.push(i[e], a);
                            return t
                        }, []) : _o(t, b).trim(),
                        p = jo(a, "paint", "text-opacity", T, h, O)
                    }
                    if (R && p && !F) {
                        J || (++P, w = v[P], w && w.getText() && !w.getFill() && !w.getStroke() || (w = new C, v[P] = w), w.setImage(void 0), w.setGeometry(void 0));
                        const e = Ao(a, T, "text", h);
                        w.getText() || w.setText(W),
                        W = w.getText(),
                        (!W || "getDeclutterMode" in W && W.getDeclutterMode() !== e) && (W = new _({
                                padding: [2, 2, 2, 2],
                                declutterMode: e
                            }), w.setText(W));
                        const t = jo(a, "layout", "text-transform", T, h, O);
                        "uppercase" == t ? R = Array.isArray(R) ? R.map((e, t) => t % 2 ? e : e.toUpperCase()) : R.toUpperCase() : "lowercase" == t && (R = Array.isArray(R) ? R.map((e, t) => t % 2 ? e : e.toLowerCase()) : R.toLowerCase());
                        const r = Array.isArray(R) ? R : 2 == M ? po(R, G) : bo(R, L, V, G);
                        if (W.setText(r), W.setFont(L), W.setRotation(Kn(jo(a, "layout", "text-rotate", T, h, O))), "function" == typeof W.setKeepUpright) {
                            const e = jo(a, "layout", "text-keep-upright", T, h, O);
                            W.setKeepUpright(e)
                        }
                        const n = jo(a, "layout", "text-anchor", T, h, O),
                        o = J || 1 == M ? "point" : jo(a, "layout", "symbol-placement", T, h, O);
                        let i;
                        if ("line-center" === o ? (W.setPlacement("line"), i = "center") : W.setPlacement(o), "line" === o && "function" == typeof W.setRepeat) {
                            const e = jo(a, "layout", "symbol-spacing", T, h, O);
                            W.setRepeat(2 * e)
                        }
                        W.setOverflow("point" === o);
                        let s = jo(a, "paint", "text-halo-width", T, h, O);
                        const l = jo(a, "layout", "text-offset", T, h, O),
                        u = jo(a, "paint", "text-translate", T, h, O);
                        let c = 0,
                        f = 0;
                        if ("point" == o) {
                            i = "center",
                            -1 !== n.indexOf("left") ? (i = "left", f = s) : -1 !== n.indexOf("right") && (i = "right", f = -s);
                            const e = jo(a, "layout", "text-rotation-alignment", T, h, O);
                            W.setRotateWithView("map" == e)
                        } else
                            W.setMaxAngle(Kn(jo(a, "layout", "text-max-angle", T, h, O)) * R.length / r.length), W.setRotateWithView(!1);
                        W.setTextAlign(i);
                        let d = "middle";
                        0 == n.indexOf("bottom") ? (d = "bottom", c = -s - .5 * (D - 1) * U) : 0 == n.indexOf("top") && (d = "top", c = s + .5 * (D - 1) * U),
                        W.setTextBaseline(d);
                        const m = jo(a, "layout", "text-justify", T, h, O);
                        W.setJustify("auto" === m ? void 0 : m),
                        W.setOffsetX(l[0] * U + f + u[0]),
                        W.setOffsetY(l[1] * U + c + u[1]);
                        const y = W.getFill() || new E;
                        y.setColor($o(jo(a, "paint", "text-color", T, h, O), p)),
                        W.setFill(y);
                        const g = $o(jo(a, "paint", "text-halo-color", T, h, O), p);
                        if (g && s > 0) {
                            const e = W.getStroke() || new $;
                            e.setColor(g),
                            s *= 2;
                            const t = .5 * U;
                            e.setWidth(s <= t ? s : t),
                            W.setStroke(e)
                        } else
                            W.setStroke(void 0);
                        const b = jo(a, "layout", "text-padding", T, h, O),
                        x = W.getPadding();
                        b !== x[0] && (x[0] = b, x[1] = b, x[2] = b, x[3] = b),
                        w.setZIndex(z)
                    }
                }
            }
            return P > -1 ? (v.length = P + 1, Oo && ("set" in o ? o.set("mapbox-layer", N) : o.getProperties()["mapbox-layer"] = N), v) : void 0
        };
        return e.setStyle(x),
        e.set("mapbox-layers", d),
        e.set("mapbox-source", b),
        e.set("mapbox-featurestate", e.get("mapbox-featurestate") || {}),
        x
    }
    const Io = Fe.parse("#000000"),
    Fo = Fe.parse("#FFFFFF"),
    Ro = Fe.parse("#000000");
    const Lo = ["raster-saturation", "raster-contrast", "raster-brightness-max", "raster-brightness-min", "raster-hue-rotate"];
    function Do(e, t, r) {
        let n = null;
        return function (o) {
            e.paint && "raster-opacity" in e.paint && o.frameState.viewState.zoom !== n && (n = o.frameState.viewState.zoom, delete r[e.id], function (e, t, r, n) {
                qn.zoom = r,
                qn.distanceFromCenter = 0;
                const o = jo(e, "paint", "raster-opacity", Gn, n);
                t.setOpacity(o)
            }
                (e, t, n, r))
        }
    }
    const Uo = ["background", "circle", "fill", "fill-extrusion", "line", "symbol", "raster", "hillshade"];
    function Go(e, t = 512) {
        return e.getExtent() ? v.createXYZ({
            extent: e.getExtent(),
            tileSize: t,
            maxZoom: 22
        }).getResolutions() : Yn
    }
    function Vo(e, t) {
        if (!t.accessToken) {
            t = Object.assign({}, t);
            new URL(e).searchParams.forEach((e, r) => {
                t.accessToken = e,
                t.accessTokenParam = r
            })
        }
        return t
    }
    function Jo(e, t, r = "", n = {}, o = void 0) {
        let s,
        l,
        u,
        f,
        y = !0;
        return "string" == typeof r || Array.isArray(r) ? f = r : (u = r, f = u.source || u.layers, n = u),
        "string" == typeof n ? (s = n, u = {}) : (s = n.styleUrl, u = n),
        !1 === u.updateSource && (y = !1),
        o || (o = u.resolutions),
        s || "string" != typeof t || t.trim().startsWith("{") || (s = t),
        s && (s = s.startsWith("data:") ? location.href : Tn(s, u.accessToken), u = Vo(s, u)),
        new Promise(function (r, n) {
            oo(t, u).then(function (t) {
                if (8 != t.version)
                    return n(new Error("glStyle version 8 required."));
                if (!(e instanceof c || e instanceof p))
                    return n(new Error("Can only apply to VectorLayer or VectorTileLayer"));
                const h = e instanceof p ? "vector" : "geojson";
                if (f ? l = Array.isArray(f) ? t.layers.find(function (e) {
                        return e.id === f[0]
                    }).source : f : (l = t.layers.find(function (e) {
                                return e.source && t.sources[e.source].type === h
                            }).source, f = l), !l)
                    return n(new Error(`No ${h} source found in the glStyle.`));
                function g() {
                    if (!y)
                        return Promise.resolve();
                    if (e instanceof p)
                        return Yo(t.sources[l], s, u).then(function (t) {
                            const r = e.getSource();
                            r ? t !== r && (r.setTileUrlFunction(t.getTileUrlFunction()), "function" == typeof r.setUrls && "function" == typeof t.getUrls && r.setUrls(t.getUrls()), r.format_ || (r.format_ = t.format_), r.getAttributions() || r.setAttributions(t.getAttributions()), r.getTileLoadFunction() === b.defaultLoadFunction && r.setTileLoadFunction(t.getTileLoadFunction()), d.equivalent(r.getProjection(), t.getProjection()) && (r.tileGrid = t.getTileGrid())) : e.setSource(t);
                            const n = e.getSource().getTileGrid();
                            !isFinite(e.getMaxResolution()) && !isFinite(e.getMinZoom()) && n.getMinZoom() > 0 && e.setMaxResolution(to(Math.max(0, n.getMinZoom() - 1e-12), n.getResolutions()))
                        });
                    const r = t.sources[l];
                    let n = e.getSource();
                    n && n.get("mapbox-source") === r || (n = ra(r, s, u));
                    const o = e.getSource();
                    return o ? n !== o && (o.getAttributions() || o.setAttributions(n.getAttributions()), o.format_ || (o.format_ = n.getFormat()), o.url_ = n.getUrl()) : e.setSource(n),
                    Promise.resolve()
                }
                let v,
                x;
                const w = {},
                k = {};
                function M() {
                    if (x || t.sprite && !w)
                        x ? (e.setStyle(x), g().then(r).catch(n)) : n(new Error("Something went wrong trying to apply style."));
                    else {
                        if (u.projection && !o) {
                            const e = d.get(u.projection).getUnits();
                            "m" !== e && (o = Yn.map(t => t / m.METERS_PER_UNIT[e]))
                        }
                        let s;
                        const c = e.getSource();
                        c instanceof b && c.format_ instanceof a && (s = c.format_.layerName_),
                        x = Po(e, t, f, o, w, k, (e, t = u.webfonts) => function (e, t = "https://cdn.jsdelivr.net/npm/@fontsource/{font-family}/{fontweight}{-fontstyle}.css") {
                            if (i.WORKER_OFFSCREEN_CANVAS)
                                return e;
                            let r;
                            for (let t = 0, n = e.length; t < n; ++t) {
                                const n = e[t];
                                if (n in xo)
                                    continue;
                                xo[n] = !0;
                                const o = Un(n, 16).split(" ");
                                r || (r = []),
                                r.push([o.slice(3).join(" ").replace(/"/g, ""), o[1], o[0]])
                            }
                            return r ? ((async() => {
                                    await document.fonts.ready;
                                    for (let e = 0, n = r.length; e < n; ++e) {
                                        const n = r[e],
                                        o = n[0];
                                        if (vo.includes(o))
                                            continue;
                                        const a = n[1],
                                        i = n[2];
                                        if (!(await document.fonts.load(`${i} ${a} 16px "${o}"`)).some(e => e.family.replace(/^['"]|['"]$/g, "").toLowerCase() === o.toLowerCase() && yo(e.weight, a) && e.style === i)) {
                                            const e = t.replace("{font-family}", o.replace(/ /g, "-").toLowerCase()).replace("{Font+Family}", o.replace(/ /g, "+")).replace("{fontweight}", a).replace("{-fontstyle}", i.replace("normal", "").replace(/(.+)/, "-$1")).replace("{fontstyle}", i);
                                            if (!document.querySelector('link[href="' + e + '"]')) {
                                                const t = document.createElement("link");
                                                t.href = e,
                                                t.rel = "stylesheet",
                                                document.head.appendChild(t)
                                            }
                                        }
                                    }
                                })(), e) : e
                        }
                                (e, t), u.getImage, s),
                        e.getStyle() ? g().then(r).catch(n) : n(new Error(`Nothing to show for source [${l}]`))
                    }
                }
                if (t.sprite) {
                    const e = function (e, t, r) {
                        if ("string" == typeof e)
                            return [{
                                    id: "default",
                                    url: _n(e, t, r)
                                }
                            ];
                        for (const n of e)
                            n.url = _n(n.url, t, r);
                        return e
                    }
                    (t.sprite, u.accessToken, s || location.href);
                    v = i.WORKER_OFFSCREEN_CANVAS ? 1 : window.devicePixelRatio >= 1.5 ? .5 : 1;
                    const r = .5 == v ? "@2x" : "";
                    Promise.all(e.map(function (e) {
                            const t = new URL(e.url);
                            let o = t.origin + t.pathname + r + ".json" + t.search;
                            return new Promise(function (e, r) {
                                no("Sprite", o, u).then(e).catch(function (n) {
                                    o = t.origin + t.pathname + ".json" + t.search,
                                    no("Sprite", o, u).then(e).catch(r)
                                })
                            }).then(function (o) {
                                let a;
                                if (void 0 === o && n(new Error("No sprites found.")), a = t.origin + t.pathname + r + ".png" + t.search, u.transformRequest) {
                                    const e = u.transformRequest(a, "SpriteImage") || a;
                                    (e instanceof Request || e instanceof Promise) && (a = e)
                                }
                                k[e.id] = a;
                                for (const t in o) {
                                    const r = "default" == e.id ? t : `${e.id}:${t}`;
                                    w[r] = o[t]
                                }
                            }).catch(function (e) {
                                n(new Error(`Sprites cannot be loaded: ${o}: ${e.message}`))
                            })
                        })).then(M).catch(n)
                } else
                    M()
            }).catch(n)
        })
    }
    function Wo(e, r, n = {}) {
        return oo(r, n).then(function (r) {
            !function (e, r, n) {
                r.layers.some(function (r) {
                    if ("background" === r.type) {
                        if (e instanceof l)
                            return e.setBackground(function (e) {
                                return Xo(r, e, n, {})
                            }), !0;
                        if (e instanceof t || e instanceof s)
                            return e.getLayers().insertAt(0, Ko(r, n, {})), !0
                    }
                })
            }
            (e, r, n)
        })
    }
    const Zo = ["type", "source", "source-layer", "minzoom", "maxzoom", "filter", "layout"];
    function Bo(e, t) {
        if (!t.ref)
            return t;
        const r = e.find(e => e.id === t.ref);
        if (!r)
            return t;
        const n = Object.assign({}, t);
        for (const e of Zo)
            !(e in n) && e in r && (n[e] = r[e]);
        return n
    }
    function Ho(e, t, r) {
        const o = new h({
            tileJSON: t,
            tileSize: e.tileSize || t.tileSize || 512
        }),
        a = o.getTileJSON(),
        i = o.getTileGrid(),
        s = d.get(r.projection || "EPSG:3857"),
        l = function (e, t) {
            const r = e.bounds;
            if (r) {
                const e = d.fromLonLat([r[0], r[1]], t),
                n = d.fromLonLat([r[2], r[3]], t);
                return [e[0], e[1], n[0], n[1]]
            }
            return d.get(t).getExtent()
        }
        (a, s),
        u = s.getExtent(),
        c = a.minzoom || 0,
        p = a.maxzoom || 22,
        f = {
            attributions: o.getAttributions(),
            projection: s,
            tileGrid: new x({
                origin: u ? n.getTopLeft(u) : i.getOrigin(0),
                extent: l || i.getExtent(),
                minZoom: c,
                resolutions: Go(s, t.tileSize).slice(0, p + 1),
                tileSize: i.getTileSize(0)
            })
        };
        return Array.isArray(a.tiles) ? f.urls = a.tiles : f.url = a.tiles,
        f
    }
    function Xo(e, t, r, n) {
        const o = {
            id: e.id,
            type: e.type
        },
        a = e.paint || {};
        let i;
        o.paint = a,
        qn.zoom = eo(t, r.resolutions || Yn),
        qn.distanceFromCenter = 0;
        const s = jo(o, "paint", "background-color", Gn, n);
        return void 0 !== a["background-opacity"] && (i = jo(o, "paint", "background-opacity", Gn, n)),
        "none" === jo(o, "layout", "visibility", Gn, n) ? void 0 : $o(s, i)
    }
    function Ko(e, t, r) {
        const n = i.WORKER_OFFSCREEN_CANVAS ? {
            style: {}
        }
         : document.createElement("div");
        return n.className = "ol-mapbox-style-background",
        n.style.position = "absolute",
        n.style.width = "100%",
        n.style.height = "100%",
        new l({
            source: new y({}),
            render(o) {
                const a = Xo(e, o.viewState.resolution, t, r);
                return n.style.backgroundColor = a,
                n
            }
        })
    }
    function Yo(e, t, r) {
        return new Promise(function (n, o) {
            io(e, t, r).then(function ({
                    tileJson: t,
                    tileLoadFunction: o
                }) {
                const i = Ho(e, t, r);
                i.tileLoadFunction = o,
                i.format = new a({
                    layerName: "mvt:layer"
                });
                const s = new b(i);
                s.set("mapbox-source", e),
                n(s)
            }).catch(o)
        })
    }
    function Qo(e) {
        return `{bbox-${(e ? e.getCode() : "EPSG:3857").toLowerCase().replace(/[^a-z0-9]/g, "-")}}`
    }
    function ea(e, t, r) {
        return new Promise(function (n, o) {
            io(e, t, r).then(function ({
                    tileJson: t,
                    tileLoadFunction: o
                }) {
                const a = new h({
                    interpolate: void 0 === r.interpolate || r.interpolate,
                    transition: 0,
                    crossOrigin: "anonymous",
                    tileJSON: t
                });
                a.tileGrid = Ho(e, t, r).tileGrid,
                r.projection && (a.projection = d.get(r.projection));
                const i = a.getTileUrlFunction();
                o && a.setTileLoadFunction(o),
                a.setTileUrlFunction(function (e, t, r) {
                    const n = Qo(r);
                    let o = i(e, t, r);
                    if (-1 != o.indexOf(n)) {
                        const t = a.getTileGrid().getTileCoordExtent(e);
                        o = o.replace(n, t.toString())
                    }
                    return o
                }),
                a.set("mapbox-source", e),
                n(a)
            }).catch(function (e) {
                o(e)
            })
        })
    }
    function ta(e, t, r) {
        const n = new u;
        return ea(e, t, r).then(function (e) {
            n.setSource(e)
        }).catch(function () {
            n.setSource(void 0)
        }),
        n
    }
    function ra(e, t, r) {
        const n = r.projection ? new o({
            dataProjection: r.projection
        }) : new o,
        a = e.data,
        i = {};
        if ("string" == typeof a) {
            const [o] = Nn(a, r.accessToken, r.accessTokenParam || "access_token", t || location.href);
            if (/\{bbox-[0-9a-z-]+\}/.test(o)) {
                const t = (e, t, r) => {
                    const n = Qo(r);
                    return o.replace(n, `${e.join(",")}`)
                },
                a = new g({
                    attributions: e.attribution,
                    format: n,
                    loader: (e, n, o, i, s) => {
                        no("GeoJSON", "function" == typeof t ? t(e, n, o) : t, r).then(e => {
                            const t = a.getFormat().readFeatures(e, {
                                featureProjection: o
                            });
                            a.addFeatures(t),
                            i(t)
                        }).catch(t => {
                            a.removeLoadedExtent(e),
                            s()
                        })
                    },
                    strategy: f.bbox
                });
                return a.set("mapbox-source", e),
                a
            }
            const i = new g({
                attributions: e.attribution,
                format: n,
                url: o,
                loader: (e, t, n, a, s) => {
                    no("GeoJSON", o, r).then(e => {
                        const t = i.getFormat().readFeatures(e, {
                            featureProjection: n
                        });
                        i.addFeatures(t),
                        a(t)
                    }).catch(t => {
                        i.removeLoadedExtent(e),
                        s()
                    })
                }
            });
            return i
        }
        i.features = n.readFeatures(a, {
            featureProjection: d.getUserProjection() || "EPSG:3857"
        });
        const s = new g(Object.assign({
                    attributions: e.attribution,
                    format: n
                }, i));
        return s.set("mapbox-source", e),
        s
    }
    function na(e, t, r, o) {
        r = Bo(e.layers, r);
        const a = Hn(e),
        i = r.type;
        let s = r.source;
        const l = e.sources[s];
        let u;
        if ("background" == i)
            u = Ko(r, o, a), s = void 0;
        else if ("vector" == l.type)
            u = function (e, t, r) {
                const n = new p({
                    declutter: !0,
                    visible: !1
                });
                return Yo(e, t, r).then(function (e) {
                    n.setSource(e)
                }).catch(function (e) {
                    n.setSource(void 0)
                }),
                n
            }
        (l, t, o);
        else if ("raster" == l.type) {
            if (!!Object.keys(r.paint || {}).find(e => Lo.includes(e))) {
                u = function (e) {
                    return new k({
                        source: new M({
                            operationType: "image",
                            operation: In,
                            sources: [e]
                        })
                    })
                }
                (ta(l, t, o)),
                function (e, t, r, n) {
                    e.getSource().on("beforeoperations", function (e) {
                        qn.zoom = eo(e.resolution, r.resolutions || Yn),
                        qn.distanceFromCenter = 0;
                        const o = e.data;
                        o.saturation = jo(t, "paint", "raster-saturation", Gn, n),
                        o.contrast = jo(t, "paint", "raster-contrast", Gn, n),
                        o.brightnessHigh = jo(t, "paint", "raster-brightness-max", Gn, n),
                        o.brightnessLow = jo(t, "paint", "raster-brightness-min", Gn, n),
                        o.hueRotate = jo(t, "paint", "raster-hue-rotate", Gn, n)
                    })
                }
                (u, r, o, a)
            } else
                u = ta(l, t, o);
            !1 !== u.get("syncMapboxVisibility") && u.setVisible(!r.layout || "none" !== jo(r, "layout", "visibility", Gn, a)),
            u.on("prerender", Do(r, u, a))
        } else if ("geojson" == l.type)
            u = function (e, t, r) {
                return new c({
                    declutter: !0,
                    source: ra(e, t, r),
                    visible: !1
                })
            }
        (l, t, o);
        else if ("raster-dem" == l.type && "hillshade" == r.type) {
            u = function (e) {
                return new k({
                    source: new M({
                        operationType: "image",
                        operation: Pn,
                        sources: [e]
                    })
                })
            }
            (ta(l, t, o)),
            function (e, t, r, o, a) {
                e.getSource().on("beforeoperations", function (e) {
                    const i = e.data;
                    i.resolution = d.getPointResolution(o.projection || "EPSG:3857", e.resolution, n.getCenter(e.extent), "m");
                    const s = eo(e.resolution, o.resolutions || Yn);
                    qn.zoom = s,
                    qn.distanceFromCenter = 0,
                    i.zoom = s,
                    i.encoding = t.encoding,
                    i.method = jo(r, "paint", "hillshade-method", Gn, a) || "standard",
                    i.exaggeration = jo(r, "paint", "hillshade-exaggeration", Gn, a);
                    let l = jo(r, "paint", "hillshade-illumination-direction", Gn, a);
                    null == l && (l = 335),
                    i.azimuths = Array.isArray(l) ? l : [l],
                    i.sunAz = i.azimuths[0];
                    let u = jo(r, "paint", "hillshade-illumination-altitude", Gn, a);
                    function c(e) {
                        return e && e.values ? e.values[0] : e
                    }
                    function p(e) {
                        const t = r.paint?.[e];
                        if (Array.isArray(t) && t.length > 0 && "string" == typeof t[0] && void 0 !== Fe.parse(t[0]))
                            return t.map(e => Fe.parse(e));
                        let n = jo(r, "paint", e, Gn, a);
                        return n = c(n),
                        n ? [n] : void 0
                    }
                    null == u && (u = 45),
                    i.altitudes = Array.isArray(u) ? u : [u],
                    i.highlightColors = p("hillshade-highlight-color"),
                    i.highlightColor = i.highlightColors?.[0] || Fo,
                    i.highlightColors || (i.highlightColors = [i.highlightColor]),
                    i.shadowColors = p("hillshade-shadow-color"),
                    i.shadowColor = i.shadowColors?.[0] || Io,
                    i.shadowColors || (i.shadowColors = [i.shadowColor]),
                    i.accentColor = c(jo(r, "paint", "hillshade-accent-color", Gn, a)) || Ro
                })
            }
            (u, l, r, o, a),
            !1 !== u.get("syncMapboxVisibility") && u.setVisible(!r.layout || "none" !== jo(r, "layout", "visibility", Gn, a))
        }
        return u && u.set("mapbox-source", s),
        u
    }
    function oa(e, n, o, a) {
        e.schema && Object.assign(En, Object.keys(e.schema).reduce((t, r) => (t[r] = e.schema[r]?.default , t), {}));
                        const i = [];
                        let s = null;
                        if (n instanceof t) {
                            if (s = n.getView(), !s.isDef() && !s.getRotation() && !s.getResolutions()) {
                                const e = a.projection ? d.get(a.projection) : s.getProjection();
                                s = new r(Object.assign(s.getProperties(), {
                                            maxResolution: Yn[0] / m.METERS_PER_UNIT[e.getUnits()],
                                            projection: a.projection || s.getProjection()
                                        })),
                                n.setView(s)
                            }
                            "center" in e && !s.getCenter() && s.setCenter(d.fromLonLat(e.center, s.getProjection())),
                            "zoom" in e && void 0 === s.getZoom() && s.setResolution(Yn[0] / m.METERS_PER_UNIT[s.getProjection().getUnits()] / Math.pow(2, e.zoom)),
                            s.getCenter() && void 0 !== s.getZoom() || s.fit(s.getProjection().getExtent(), {
                                nearest: !0,
                                size: n.getSize()
                            })
                        }
                        n.set("mapbox-style", e), n.set("mapbox-metadata", {
                            styleUrl: o,
                            options: a
                        });
                        const l = e.layers;
                        let u, f, y, h = [];
                        for (let t = 0, r = l.length; t < r; ++t) {
                            const r = Bo(l, l[t]),
                            s = r.type;
                            Uo.includes(s) ? (y = r.source, y && y == f || (h.length && (i.push(ia(u, h, e, o, n, a)), h = []), u = na(e, o, r, a), u instanceof c || u instanceof p || (h = []), f = u.get("mapbox-source")), h.push(r.id)) : console.warn(`layers[${t}].type "${s}" not supported`)
                        }
                        return i.push(ia(u, h, e, o, n, a)), Promise.all(i)
                }
                function aa(e, r, n = {}) {
                    let o,
                    a;
                    if (i.WORKER_OFFSCREEN_CANVAS) {
                        if (!(e instanceof t || e instanceof s))
                            throw new Error("ol-mapbox-style in a web worker requires a Map or a LayerGroup as first argument");
                        a = e
                    } else
                        a = "string" == typeof e || e instanceof HTMLElement ? new t({
                            target: e
                        }) : e;
                    if ("string" == typeof r) {
                        const e = r.startsWith("data:") ? location.href : Tn(r, n.accessToken);
                        n = Vo(e, n),
                        o = new Promise(function (t, o) {
                            oo(r, n).then(function (r) {
                                oa(r, a, e, n).then(function () {
                                    t(a)
                                }).catch(o)
                            }).catch(function (e) {
                                o(new Error(`Could not load ${r}: ${e.message}`))
                            })
                        })
                    } else
                        o = new Promise(function (e, t) {
                            oa(r, a, !n.styleUrl || n.styleUrl.startsWith("data:") ? location.href : Tn(n.styleUrl, n.accessToken), n).then(function () {
                                e(a)
                            }).catch(t)
                        });
                    return o
                }
                function ia(e, t, r, n, o, a = {}) {
                    let i = 24,
                    s = 0;
                    const l = r.layers;
                    for (let e = 0, r = l.length; e < r; ++e) {
                        const r = l[e];
                        -1 !== t.indexOf(r.id) && (i = Math.min("minzoom" in r ? r.minzoom : 0, i), s = Math.max("maxzoom" in r ? r.maxzoom : 24, s))
                    }
                    return new Promise(function (l, u) {
                        const c = function () {
                            const c = e.getSource();
                            if (c && "error" !== c.getState()) {
                                if ("getTileGrid" in c) {
                                    const t = c.getTileGrid();
                                    if (t) {
                                        const r = t.getMinZoom();
                                        (i > 0 || r > 0) && e.setMaxResolution(Math.min(to(Math.max(0, i - 1e-12), Yn), to(Math.max(0, r - 1e-12), t.getResolutions()))),
                                        s < 24 && e.setMinResolution(to(s, Yn))
                                    }
                                } else
                                    i > 0 && e.setMaxResolution(to(Math.max(0, i - 1e-12), Yn));
                                c instanceof g || c instanceof b ? Jo(e, r, t, Object.assign({
                                        styleUrl: n
                                    }, a)).then(function () {
                                    !function (e, t, r) {
                                        function n() {
                                            const n = t.get("mapbox-style");
                                            if (!n)
                                                return;
                                            const o = U(n.layers),
                                            a = e.get("mapbox-layers"),
                                            i = o.filter(function (e) {
                                                return a.includes(e.id)
                                            }).some(function (e) {
                                                return !e.layout || "visible" === jo(e, "layout", "visibility", Gn, r)
                                            });
                                            !1 !== e.get("syncMapboxVisibility") && e.get("visible") !== i && e.setVisible(i)
                                        }
                                        e.on("change", n),
                                        n()
                                    }
                                    (e, o, Hn(r)),
                                    l()
                                }).catch(u) : l()
                            } else
                                u(new Error("Error accessing data for source " + e.get("mapbox-source")))
                        };
                        e.set("mapbox-layers", t);
                        const p = o.getLayers();
                        -1 === p.getArray().indexOf(e) && p.push(e),
                        e.getSource() ? c() : e.once("change:source", c)
                    })
                }
                function sa(e, t) {
                    const r = e.get("mapbox-style").layers.find(function (e) {
                        return e.id === t
                    });
                    return r
                }
                function la(e, t) {
                    const r = e.getLayers().getArray();
                    for (let e = 0, n = r.length; e < n; ++e) {
                        const n = r[e].get("mapbox-layers");
                        if (n && -1 !== n.indexOf(t))
                            return r[e]
                    }
                }
                function ua(e, t) {
                    const r = [],
                    n = e.getLayers().getArray();
                    for (let e = 0, o = n.length; e < o; ++e)
                        n[e].get("mapbox-source") === t && r.push(n[e]);
                    return r
                }
                function ca(e, t) {
                    const r = e.getLayers().getArray();
                    for (let e = 0, n = r.length; e < n; ++e) {
                        const n = r[e].getSource();
                        if (r[e].get("mapbox-source") === t)
                            return n
                    }
                }
                class pa extends I {
                    constructor(e) {
                        super(F.ERROR),
                        this.error = e
                    }
                }
                e.MapboxVectorLayer = class extends p {
                    constructor(e) {
                        const t = !("declutter" in e) || e.declutter,
                        r = new b({
                            state: "loading",
                            format: new a({
                                layerName: "mvt:layer"
                            })
                        });
                        super({
                            source: r,
                            background: !1 === e.background ? null : e.background,
                            declutter: t,
                            extent: e.extent,
                            className: e.className,
                            opacity: e.opacity,
                            visible: e.visible,
                            zIndex: e.zIndex,
                            minResolution: e.minResolution,
                            maxResolution: e.maxResolution,
                            minZoom: e.minZoom,
                            maxZoom: e.maxZoom,
                            renderOrder: e.renderOrder,
                            renderBuffer: e.renderBuffer,
                            renderMode: e.renderMode,
                            map: e.map,
                            updateWhileAnimating: e.updateWhileAnimating,
                            updateWhileInteracting: e.updateWhileInteracting,
                            preload: e.preload,
                            useInterimTilesOnError: e.useInterimTilesOnError,
                            properties: e.properties
                        }),
                        e.accessToken && (this.accessToken = e.accessToken);
                        const n = [Jo(this, e.styleUrl, e.layers || e.source, {
                                accessToken: this.accessToken
                            })];
                        void 0 === this.getBackground() && n.push(Wo(this, e.styleUrl, {
                                accessToken: this.accessToken
                            })),
                        Promise.all(n).then(() => {
                            r.setState("ready")
                        }).catch(e => {
                            this.dispatchEvent(new pa(e));
                            this.getSource().setState("error")
                        })
                    }
                },
                e.addMapboxLayer = function (e, t, r) {
                    const n = e.get("mapbox-style"),
                    o = n.layers;
                    let a,
                    i,
                    s = -1;
                    if (void 0 !== r) {
                        const t = sa(e, r);
                        if (void 0 === t)
                            throw new Error(`Layer with id "${r}" not found.`);
                        a = o.indexOf(t)
                    } else
                        a = o.length;
                    if (a > 0 && o[a - 1].source === t.source ? (s = a - 1, i = -1) : a < o.length && o[a].source === t.source && (s = a, i = 0), -1 === s) {
                        const {
                            options: i,
                            styleUrl: s
                        } = e.get("mapbox-metadata"),
                        l = na(n, s, t, i);
                        if (r) {
                            const t = la(e, r),
                            n = e.getLayers().getArray().indexOf(t);
                            e.getLayers().insertAt(n, l)
                        }
                        return o.splice(a, 0, t),
                        ia(l, [t.id], n, s, e, i)
                    }
                    if (o.some(e => e.id === t.id))
                        throw new Error(`Layer with id "${t.id}" already exists.`);
                    const l = o[s].id,
                    u = No[Bn(e.get("mapbox-style"), la(e, l))];
                    if (o.splice(a, 0, t), u) {
                        const [e, r, n, o, a, s, c, p] = u;
                        if (Array.isArray(n)) {
                            const e = n.indexOf(l) + i;
                            n.splice(e, 0, t.id)
                        }
                        Po(e, r, n, o, a, s, c, p)
                    } else
                        la(e, o[s].id).changed();
                    return Promise.resolve()
                },
                e.apply = aa,
                e.applyBackground = Wo,
                e.applyStyle = Jo,
                e.default = aa,
                e.getFeatureState = function (e, t) {
                    const r = "getLayers" in e ? ua(e, t.source) : [e];
                    for (let e = 0, n = r.length; e < n; ++e) {
                        const n = r[e].get("mapbox-featurestate");
                        if (n && n[t.id])
                            return n[t.id]
                    }
                },
                e.getLayer = la,
                e.getLayers = ua,
                e.getMapboxLayer = sa,
                e.getSource = ca,
                e.getStyleForLayer = function (e, t, r, n) {
                    const o = r.getStyleFunction();
                    if (3 === o.length)
                        return o(e, t, n)
                },
                e.recordStyleLayer = function (e = !1) {
                    Oo = e
                },
                e.removeMapboxLayer = function (e, t) {
                    const r = "string" == typeof t ? t : t.id,
                    n = la(e, r),
                    o = n.get("mapbox-layers");
                    if (1 === o.length)
                        throw new Error("Cannot remove last Mapbox layer from an OpenLayers layer.");
                    o.splice(o.indexOf(r), 1);
                    const a = e.get("mapbox-style"),
                    i = a.layers;
                    i.splice(i.findIndex(e => e.id === r), 1);
                    const s = No[Bn(a, n)];
                    if (s) {
                        const [e, t, n, o, a, i, l, u] = s;
                        Array.isArray(n) && n.splice(n.findIndex(e => e === r), 1),
                        Po(e, t, n, o, a, i, l, u)
                    } else
                        la(e, r).changed()
                },
                e.renderTransparent = function (e) {
                    e !== qo && (!function () {
                        for (const e in Vn)
                            delete Vn[e]
                    }
                        (), qo = e)
                },
                e.setFeatureState = function (e, t, r) {
                    const n = "getLayers" in e ? ua(e, t.source) : [e];
                    for (let e = 0, o = n.length; e < o; ++e) {
                        const o = n[e].get("mapbox-featurestate");
                        if (!o)
                            throw new Error(`Map or layer for source "${t.source}" not found.`);
                        r ? o[t.id] = r : delete o[t.id],
                        n[e].changed()
                    }
                },
                e.styleConfig = En,
                e.stylefunction = Po,
                e.updateMapboxLayer = function (e, t) {
                    const r = e.get("mapbox-style"),
                    n = r.layers,
                    o = n.findIndex(function (e) {
                        return e.id === t.id
                    });
                    if (-1 === o)
                        throw new Error(`Layer with id "${t.id}" not found.`);
                    if (n[o].source !== t.source)
                        throw new Error("Updated layer and previous version must use the same source.");
                    delete Hn(r)[t.id],
                    delete Xn(r)[t.id],
                    n[o] = t;
                    const a = No[Bn(e.get("mapbox-style"), la(e, t.id))];
                    if (a)
                        return Po.apply(void 0, a), Promise.resolve();
                    const i = la(e, t.id), {
                        options: s,
                        styleUrl: l
                    } = e.get("mapbox-metadata");
                    return ia(i, [t.id], r, l, e, s)
                },
                e.updateMapboxSource = function (e, t, r) {
                    const n = ca(e, t),
                    o = e.getLayers().getArray().filter(function (e) {
                        return (e instanceof c || e instanceof u || e instanceof p) && e.getSource() === n
                    }),
                    a = e.get("mapbox-metadata");
                    let i;
                    switch (r.type) {
                    case "vector":
                        i = Yo(r, a.styleUrl, a.options);
                        break;
                    case "geojson":
                        i = Promise.resolve(ra(r, a.styleUrl, a.options));
                        break;
                    case "raster":
                    case "raster-dem":
                        i = ea(r, a.styleUrl, a.options);
                        break;
                    default:
                        return Promise.reject(new Error("Unsupported source type " + r.type))
                    }
                    return i.then(function (e) {
                        o.forEach(function (t) {
                            t.setSource(e)
                        })
                    }),
                    i
                },
                Object.defineProperty(e, "__esModule", {
                    value: !0
                })
            });
            //# sourceMappingURL=olms.js.map
