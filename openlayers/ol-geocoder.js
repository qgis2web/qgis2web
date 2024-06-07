/*!
 * ol-geocoder - v4.2.0
 * A geocoder extension for OpenLayers.
 * https://github.com/jonataswalker/ol-geocoder
 * Built: Thu Aug 17 2023 09:55:15 GMT-0300 (Brasilia Standard Time)
 */
!function (t, e) {
    "object" == typeof exports && "undefined" != typeof module ? module.exports = e(require("ol/control/Control"), require("ol/style/Style"), require("ol/style/Icon"), require("ol/layer/Vector"), require("ol/source/Vector"), require("ol/geom/Point"), require("ol/Feature"), require("ol/proj")) : "function" == typeof define && define.amd ? define(["ol/control/Control", "ol/style/Style", "ol/style/Icon", "ol/layer/Vector", "ol/source/Vector", "ol/geom/Point", "ol/Feature", "ol/proj"], e) : (t = "undefined" != typeof globalThis ? globalThis : t || self).Geocoder = e(t.ol.control.Control, t.ol.style.Style, t.ol.style.Icon, t.ol.layer.Vector, t.ol.source.Vector, t.ol.geom.Point, t.ol.Feature, t.ol.proj)
}
(this, (function (t, e, n, r, s, o, i, a) {
        "use strict";
        function l(t) {
            return t && "object" == typeof t && "default" in t ? t : {
            default:
                t
            }
        }
        var u = l(t),
        c = l(e),
        p = l(n),
        d = l(r),
        h = l(s),
        m = l(o),
        g = l(i),
        y = l(a),
        f = "gcd-container",
        v = "gcd-button-control",
        b = "gcd-input-query",
        w = "gcd-input-reset",
        x = {
            namespace: "ol-geocoder",
            spin: "gcd-pseudo-rotate",
            hidden: "gcd-hidden",
            address: "gcd-address",
            country: "gcd-country",
            city: "gcd-city",
            road: "gcd-road",
            olControl: "ol-control",
            glass: {
                container: "gcd-gl-container",
                control: "gcd-gl-control",
                button: "gcd-gl-btn",
                input: "gcd-gl-input",
                expanded: "gcd-gl-expanded",
                reset: "gcd-gl-reset",
                result: "gcd-gl-result"
            },
            inputText: {
                container: "gcd-txt-container",
                control: "gcd-txt-control",
                input: "gcd-txt-input",
                reset: "gcd-txt-reset",
                icon: "gcd-txt-glass",
                result: "gcd-txt-result"
            }
        },
        k = {
            containerId: f,
            buttonControlId: v,
            inputQueryId: b,
            inputResetId: w,
            cssClasses: x
        },
        q = Object.freeze({
            __proto__: null,
            containerId: f,
            buttonControlId: v,
            inputQueryId: b,
            inputResetId: w,
            cssClasses: x,
        default:
            k
        }),
        C = "addresschosen",
        S = "nominatim",
        L = "reverse",
        E = "glass-button",
        A = "text-input",
        T = "osm",
        j = "mapquest",
        F = "photon",
        N = "bing",
        R = "opencage",
        P = {
            provider: T,
            placeholder: "Search for an address",
            featureStyle: null,
            targetType: E,
            lang: "en-US",
            limit: 5,
            keepOpen: !1,
            preventDefault: !1,
            autoComplete: !1,
            autoCompleteMinLength: 2,
            autoCompleteTimeout: 200,
            debug: !1
        };
        function I(t, e) {
            if (void 0 === e && (e = "Assertion failed"), !t) {
                if ("undefined" != typeof Error)
                    throw new Error(e);
                throw e
            }
        }
        function _(t) {
            var e = function () {
                if ("performance" in window == 0 && (window.performance = {}), "now" in window.performance == 0) {
                    var t = Date.now();
                    performance.timing && performance.timing.navigationStart && (t = performance.timing.navigationStart),
                    window.performance.now = function () {
                        return Date.now() - t
                    }
                }
                return window.performance.now()
            }
            ().toString(36);
            return t ? t + e : e
        }
        function M(t) {
            return /^[0-9]+$/.test(t)
        }
        function O(t, e, n) {
            if (Array.isArray(t))
                t.forEach((function (t) {
                        return O(t, e)
                    }));
            else
                for (var r = Array.isArray(e) ? e : e.split(/[\t-\r \xA0\u1680\u2000-\u200A\u2028\u2029\u202F\u205F\u3000\uFEFF]+/), s = r.length; s--; )
                    V(t, r[s]) || G(t, r[s], n)
        }
        function D(t, e, n) {
            if (Array.isArray(t))
                t.forEach((function (t) {
                        return D(t, e, n)
                    }));
            else
                for (var r = Array.isArray(e) ? e : e.split(/[\t-\r \xA0\u1680\u2000-\u200A\u2028\u2029\u202F\u205F\u3000\uFEFF]+/), s = r.length; s--; )
                    V(t, r[s]) && z(t, r[s], n)
        }
        function V(t, e) {
            return t.classList ? t.classList.contains(e) : U(e).test(t.className)
        }
        function Q(t, e) {
            return t.replace(/\{[\t-\r \xA0\u1680\u2000-\u200A\u2028\u2029\u202F\u205F\u3000\uFEFF]*([\x2D0-9A-Z_a-z]+)[\t-\r \xA0\u1680\u2000-\u200A\u2028\u2029\u202F\u205F\u3000\uFEFF]*\}/g, (function (t, n) {
                    var r = void 0 === e[n] ? "" : e[n];
                    return String(r).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#039;")
                }))
        }
        function B(t, e) {
            var n;
            if (Array.isArray(t)) {
                if (n = document.createElement(t[0]), t[1].id && (n.id = t[1].id), t[1].classname && (n.className = t[1].classname), t[1].attr) {
                    var r = t[1].attr;
                    if (Array.isArray(r))
                        for (var s = -1; ++s < r.length; )
                            n.setAttribute(r[s].name, r[s].value);
                    else
                        n.setAttribute(r.name, r.value)
                }
            } else
                n = document.createElement(t);
            n.innerHTML = e;
            for (var o = document.createDocumentFragment(); n.childNodes[0]; )
                o.append(n.childNodes[0]);
            return n.append(o),
            n
        }
        function U(t) {
            return new RegExp("(^|\\s+) " + t + " (\\s+|$)", "u")
        }
        function G(t, e, n) {
            t.classList ? t.classList.add(e) : t.className = (t.className + " " + e).trim(),
            n && M(n) && window.setTimeout((function () {
                    return z(t, e)
                }), n)
        }
        function z(t, e, n) {
            t.classList ? t.classList.remove(e) : t.className = t.className.replace(U(e), " ").trim(),
            n && M(n) && window.setTimeout((function () {
                    return G(t, e)
                }), n)
        }
        var $ = q.cssClasses,
        H = function (t) {
            this.options = t.options,
            this.els = this.createControl()
        };
        H.prototype.createControl = function () {
            var t,
            e,
            n;
            return this.options.targetType === A ? (e = $.namespace + " " + $.inputText.container, n = {
                    container: t = B(["div", {
                                    id: q.containerId,
                                    classname: e
                                }
                            ], H.input),
                    control: t.querySelector("." + $.inputText.control),
                    input: t.querySelector("." + $.inputText.input),
                    reset: t.querySelector("." + $.inputText.reset),
                    result: t.querySelector("." + $.inputText.result)
                }) : (e = $.namespace + " " + $.glass.container, n = {
                    container: t = B(["div", {
                                    id: q.containerId,
                                    classname: e
                                }
                            ], H.glass),
                    control: t.querySelector("." + $.glass.control),
                    button: t.querySelector("." + $.glass.button),
                    input: t.querySelector("." + $.glass.input),
                    reset: t.querySelector("." + $.glass.reset),
                    result: t.querySelector("." + $.glass.result)
                }),
            n.input.placeholder = this.options.placeholder,
            n
        },
        H.glass = '\n  <div class="' + $.glass.control + " " + $.olControl + '">\n    <button type="button" id="' + q.buttonControlId + '" class="' + $.glass.button + '"></button>\n    <input type="text" id="' + q.inputQueryId + '" class="' + $.glass.input + '" autocomplete="off" placeholder="Search ...">\n    <a id="' + q.inputResetId + '" class="' + $.glass.reset + " " + $.hidden + '"></a>\n  </div>\n  <ul class="' + $.glass.result + '"></ul>\n',
        H.input = '\n  <div class="' + $.inputText.control + '">\n    <input type="text" id="' + q.inputQueryId + '" class="' + $.inputText.input + '" autocomplete="off" placeholder="Search ...">\n    <span class="' + $.inputText.icon + '"></span>\n    <button type="button" id="' + q.inputResetId + '" class="' + $.inputText.reset + " " + $.hidden + '"></button>\n  </div>\n  <ul class="' + $.inputText.result + '"></ul>\n';
        var K = function () {
            this.settings = {
                url: "https://photon.komoot.io/api/",
                params: {
                    q: "",
                    limit: 10,
                    lang: "en"
                },
                langs: ["de", "it", "fr", "en"]
            }
        };
        K.prototype.getParameters = function (t) {
            return t.lang = t.lang.toLowerCase(), {
                url: this.settings.url,
                params: {
                    q: t.query,
                    limit: t.limit || this.settings.params.limit,
                    lang: this.settings.langs.includes(t.lang) ? t.lang : this.settings.params.lang
                }
            }
        },
        K.prototype.handleResponse = function (t) {
            return 0 === t.features.length ? [] : t.features.map((function (t) {
                    return {
                        lon: t.geometry.coordinates[0],
                        lat: t.geometry.coordinates[1],
                        address: {
                            name: t.properties.name,
                            postcode: t.properties.postcode,
                            city: t.properties.city,
                            state: t.properties.state,
                            country: t.properties.country
                        },
                        original: {
                            formatted: t.properties.name,
                            details: t.properties
                        }
                    }
                }))
        };
        var Z = function () {
            this.settings = {
                url: "https://nominatim.openstreetmap.org/search",
                params: {
                    q: "",
                    format: "json",
                    addressdetails: 1,
                    limit: 10,
                    countrycodes: "",
                    "accept-language": "en-US"
                }
            }
        };
        Z.prototype.getParameters = function (t) {
            return {
                url: this.settings.url,
                params: {
                    q: t.query,
                    format: this.settings.params.format,
                    addressdetails: this.settings.params.addressdetails,
                    limit: t.limit || this.settings.params.limit,
                    countrycodes: t.countrycodes || this.settings.params.countrycodes,
                    "accept-language": t.lang || this.settings.params["accept-language"]
                }
            }
        },
        Z.prototype.handleResponse = function (t) {
            return 0 === t.length ? [] : t.map((function (t) {
                    return {
                        lon: t.lon,
                        lat: t.lat,
                        bbox: t.boundingbox,
                        address: {
                            name: t.display_name,
                            road: t.address.road || "",
                            houseNumber: t.address.house_number || "",
                            postcode: t.address.postcode,
                            city: t.address.city || t.address.town,
                            state: t.address.state,
                            country: t.address.country
                        },
                        original: {
                            formatted: t.display_name,
                            details: t.address
                        }
                    }
                }))
        };
        var J = function () {
            this.settings = {
                url: "https://open.mapquestapi.com/nominatim/v1/search.php",
                params: {
                    q: "",
                    key: "",
                    format: "json",
                    addressdetails: 1,
                    limit: 10,
                    countrycodes: "",
                    "accept-language": "en-US"
                }
            }
        };
        J.prototype.getParameters = function (t) {
            return {
                url: this.settings.url,
                params: {
                    q: t.query,
                    key: t.key,
                    format: "json",
                    addressdetails: 1,
                    limit: t.limit || this.settings.params.limit,
                    countrycodes: t.countrycodes || this.settings.params.countrycodes,
                    "accept-language": t.lang || this.settings.params["accept-language"]
                }
            }
        },
        J.prototype.handleResponse = function (t) {
            return 0 === t.length ? [] : t.map((function (t) {
                    return {
                        lon: t.lon,
                        lat: t.lat,
                        address: {
                            name: t.address.neighbourhood || "",
                            road: t.address.road || "",
                            postcode: t.address.postcode,
                            city: t.address.city || t.address.town,
                            state: t.address.state,
                            country: t.address.country
                        },
                        original: {
                            formatted: t.display_name,
                            details: t.address
                        }
                    }
                }))
        };
        var W = function () {
            this.settings = {
                url: "https://dev.virtualearth.net/REST/v1/Locations",
                callbackName: "jsonp",
                params: {
                    query: "",
                    key: "",
                    includeNeighborhood: 0,
                    maxResults: 10
                }
            }
        };
        W.prototype.getParameters = function (t) {
            return {
                url: this.settings.url,
                callbackName: this.settings.callbackName,
                params: {
                    query: t.query,
                    key: t.key,
                    includeNeighborhood: t.includeNeighborhood || this.settings.params.includeNeighborhood,
                    maxResults: t.maxResults || this.settings.params.maxResults
                }
            }
        },
        W.prototype.handleResponse = function (t) {
            var e = t.resourceSets[0].resources;
            return 0 === e.length ? [] : e.map((function (t) {
                    return {
                        lon: t.point.coordinates[1],
                        lat: t.point.coordinates[0],
                        address: {
                            name: t.name
                        },
                        original: {
                            formatted: t.address.formattedAddress,
                            details: t.address
                        }
                    }
                }))
        };
        var X = function () {
            this.settings = {
                url: "https://api.opencagedata.com/geocode/v1/json?",
                params: {
                    q: "",
                    key: "",
                    limit: 10,
                    countrycode: "",
                    pretty: 1,
                    no_annotations: 1
                }
            }
        };
        function Y(t) {
            return new Promise((function (e, n) {
                    var r = function (t, e) {
                        e && "object" == typeof e && (t += (/\?/.test(t) ? "&" : "?") + tt(e));
                        return t
                    }
                    (t.url, t.data);
                    t.jsonp ? function (t, e, n) {
                        var r = document.head,
                        s = document.createElement("script"),
                        o = "f" + Math.round(Math.random() * Date.now());
                        s.setAttribute("src", t + (t.indexOf("?") > 0 ? "&" : "?") + e + "=" + o),
                        window[o] = function (t) {
                            window[o] = void 0,
                            setTimeout((function () {
                                    return r.removeChild(s)
                                }), 0),
                            n(t)
                        },
                        r.append(s)
                    }
                    (r, t.callbackName, e) : fetch(r, {
                        method: "GET",
                        mode: "cors",
                        credentials: "same-origin"
                    }).then((function (t) {
                            return t.json()
                        })).then(e).catch(n)
                }))
        }
        function tt(t) {
            return Object.keys(t).reduce((function (e, n) {
                    return e.push("object" == typeof t[n] ? tt(t[n]) : encodeURIComponent(n) + "=" + encodeURIComponent(t[n])),
                    e
                }), []).join("&")
        }
        X.prototype.getParameters = function (t) {
            return {
                url: this.settings.url,
                params: {
                    q: t.query,
                    key: t.key,
                    limit: t.limit || this.settings.params.limit,
                    countrycode: t.countrycodes || this.settings.params.countrycodes
                }
            }
        },
        X.prototype.handleResponse = function (t) {
            return 0 === t.results.length ? [] : t.results.map((function (t) {
                    return {
                        lon: t.geometry.lng,
                        lat: t.geometry.lat,
                        address: {
                            name: t.components.house_number || "",
                            road: t.components.road || "",
                            postcode: t.components.postcode,
                            city: t.components.city || t.components.town,
                            state: t.components.state,
                            country: t.components.country
                        },
                        original: {
                            formatted: t.formatted,
                            details: t.components
                        }
                    }
                }))
        };
        var et = q.cssClasses,
        nt = function (t, e) {
            this.Base = t,
            this.layerName = _("geocoder-layer-"),
            this.layer = new d.default({
                name: this.layerName,
                source: new h.default
            }),
            this.options = t.options,
            this.options.provider = "string" == typeof this.options.provider ? this.options.provider.toLowerCase() : this.options.provider,
            this.provider = this.newProvider(),
            this.els = e,
            this.lastQuery = "",
            this.container = this.els.container,
            this.registeredListeners = {
                mapClick: !1
            },
            this.setListeners()
        };
        nt.prototype.setListeners = function () {
            var t,
            e,
            n = this;
            this.els.input.addEventListener("keypress", (function (t) {
                    var e = t.target.value.trim();
                    (t.key ? "Enter" === t.key : t.which ? 13 === t.which : !!t.keyCode && 13 === t.keyCode) && (t.preventDefault(), n.query(e))
                }), !1),
            this.els.input.addEventListener("click", (function (t) {
                    return t.stopPropagation()
                }), !1),
            this.els.input.addEventListener("input", (function (r) {
                    var s = r.target.value.trim();
                    0 !== s.length ? D(n.els.reset, et.hidden) : O(n.els.reset, et.hidden),
                    n.options.autoComplete && s !== e && (e = s, t && clearTimeout(t), t = setTimeout((function () {
                                    s.length >= n.options.autoCompleteMinLength && n.query(s)
                                }), n.options.autoCompleteTimeout))
                }), !1),
            this.els.reset.addEventListener("click", (function (t) {
                    n.els.input.focus(),
                    n.els.input.value = "",
                    n.lastQuery = "",
                    O(n.els.reset, et.hidden),
                    n.clearResults()
                }), !1),
            this.options.targetType === E && this.els.button.addEventListener("click", (function (t) {
                    t.stopPropagation(),
                    V(n.els.control, et.glass.expanded) ? n.collapse() : n.expand()
                }), !1)
        },
        nt.prototype.query = function (t) {
            var e = this;
            this.provider || (this.provider = this.newProvider());
            var n = this.provider.getParameters({
                query: t,
                key: this.options.key,
                lang: this.options.lang,
                countrycodes: this.options.countrycodes,
                limit: this.options.limit
            });
            if (this.lastQuery !== t || !this.els.result.firstChild) {
                this.lastQuery = t,
                this.clearResults(),
                O(this.els.reset, et.spin);
                var r = {
                    url: n.url,
                    data: n.params
                };
                n.callbackName && (r.jsonp = !0, r.callbackName = n.callbackName),
                Y(r).then((function (t) {
                        e.options.debug && console.info(t),
                        D(e.els.reset, et.spin);
                        var n = e.provider.handleResponse(t);
                        n && (e.createList(n), e.listenMapClick())
                    })).catch((function (t) {
                        D(e.els.reset, et.spin);
                        var n = B("li", "<h5>Error! No internet connection?</h5>");
                        e.els.result.append(n)
                    }))
            }
        },
        nt.prototype.createList = function (t) {
            var e = this,
            n = this.els.result;
            t.forEach((function (t) {
                    var r;
                    if (e.options.provider === T)
                        r = '<span class="' + et.road + '">' + t.address.name + "</span>";
                    else
                        r = e.addressTemplate(t.address);
                    var s = B("li", '<a href="#">' + r + "</a>");
                    s.addEventListener("click", (function (n) {
                            n.preventDefault(),
                            e.chosen(t, r, t.address, t.original)
                        }), !1),
                    n.append(s)
                }))
        },
        nt.prototype.chosen = function (t, e, n, r) {
            var s = this.Base.getMap(),
            o = [Number.parseFloat(t.lon), Number.parseFloat(t.lat)],
            i = s.getView().getProjection(),
            a = y.default.transform(o, "EPSG:4326", i),
            l = t.bbox;
            l && (l = y.default.transformExtent([l[2], l[1], l[3], l[0]], "EPSG:4326", i));
            var u = {
                formatted: e,
                details: n,
                original: r
            };
            if (!1 === this.options.keepOpen && this.clearResults(!0), !0 === this.options.preventDefault)
                this.Base.dispatchEvent({
                    type: C,
                    address: u,
                    coordinate: a,
                    bbox: l,
                    place: t
                });
            else {
                l ? s.getView().fit(l, {
                    duration: 500
                }) : function (t, e, n, r) {
                    void 0 === n && (n = 500),
                    void 0 === r && (r = 2.388657133911758),
                    t.getView().animate({
                        duration: n,
                        resolution: r
                    }, {
                        duration: n,
                        center: e
                    })
                }
                (s, a);
                var c = this.createFeature(a, u);
                this.Base.dispatchEvent({
                    type: C,
                    address: u,
                    feature: c,
                    coordinate: a,
                    bbox: l,
                    place: t
                })
            }
        },
        nt.prototype.createFeature = function (t) {
            var e = new g.default(new m.default(t));
            return this.addLayer(),
            e.setStyle(this.options.featureStyle),
            e.setId(_("geocoder-ft-")),
            this.getSource().addFeature(e),
            e
        },
        nt.prototype.addressTemplate = function (t) {
            var e = [];
            return t.name && e.push(['<span class="', et.road, '">{name}</span>'].join("")),
            (t.road || t.building || t.house_number) && e.push(['<span class="', et.road, '">{building} {road} {house_number}</span>'].join("")),
            (t.city || t.town || t.village) && e.push(['<span class="', et.city, '">{postcode} {city} {town} {village}</span>'].join("")),
            (t.state || t.country) && e.push(['<span class="', et.country, '">{state} {country}</span>'].join("")),
            Q(e.join("<br>"), t)
        },
        nt.prototype.newProvider = function () {
            switch (this.options.provider) {
            case T:
                return new Z;
            case j:
                return new J;
            case F:
                return new K;
            case N:
                return new W;
            case R:
                return new X;
            default:
                return this.options.provider
            }
        },
        nt.prototype.expand = function () {
            var t = this;
            D(this.els.input, et.spin),
            O(this.els.control, et.glass.expanded),
            window.setTimeout((function () {
                    return t.els.input.focus()
                }), 100),
            this.listenMapClick()
        },
        nt.prototype.collapse = function () {
            this.els.input.value = "",
            this.els.input.blur(),
            O(this.els.reset, et.hidden),
            D(this.els.control, et.glass.expanded),
            this.clearResults()
        },
        nt.prototype.listenMapClick = function () {
            if (!this.registeredListeners.mapClick) {
                var t = this,
                e = this.Base.getMap().getTargetElement();
                this.registeredListeners.mapClick = !0,
                e.addEventListener("click", {
                    handleEvent: function (n) {
                        t.clearResults(!0),
                        e.removeEventListener(n.type, this, !1),
                        t.registeredListeners.mapClick = !1
                    }
                }, !1)
            }
        },
        nt.prototype.clearResults = function (t) {
            t && this.options.targetType === E ? this.collapse() : function (t) {
                for (; t.firstChild; )
                    t.firstChild.remove()
            }
            (this.els.result)
        },
        nt.prototype.getSource = function () {
            return this.layer.getSource()
        },
        nt.prototype.addLayer = function () {
            var t = this,
            e = !1,
            n = this.Base.getMap();
            n.getLayers().forEach((function (n) {
                    n === t.layer && (e = !0)
                })),
            e || n.addLayer(this.layer)
        };
        var rt = function (t) {
            function e(n, r) {
                if (void 0 === n && (n = S), void 0 === r && (r = {}), !(this instanceof e))
                    return new e;
                var s;
                I("string" == typeof n, "@param `type` should be string!"),
                I(n === S || n === L, "@param 'type' should be '" + S + "'\n      or '" + L + "'!"),
                I("object" == typeof r, "@param `options` should be object!"),
                P.featureStyle = [new c.default({
                        image: new p.default({
                            scale: .7,
                            src: "./resources/marker.png"
                        })
                    })],
                this.options = function (t, e) {
                    var n = {};
                    for (var r in t)
                        Object.prototype.hasOwnProperty.call(t, r) && (n[r] = t[r]);
                    for (var s in e)
                        Object.prototype.hasOwnProperty.call(e, s) && (n[s] = e[s]);
                    return n
                }
                (P, r),
                this.container = void 0;
                var o = new H(this);
                n === S && (this.container = o.els.container, s = new nt(this, o.els), this.layer = s.layer),
                t.call(this, {
                    element: this.container
                })
            }
            return t && (e.__proto__ = t),
            e.prototype = Object.create(t && t.prototype),
            e.prototype.constructor = e,
            e.prototype.getLayer = function () {
                return this.layer
            },
            e.prototype.getSource = function () {
                return this.getLayer().getSource()
            },
            e.prototype.setProvider = function (t) {
                this.options.provider = t
            },
            e.prototype.setProviderKey = function (t) {
                this.options.key = t
            },
            e
        }
        (u.default);
        return rt
    }));
//# sourceMappingURL=ol-geocoder.js.map
