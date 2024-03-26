[![GitHub version](https://badge.fury.io/gh/tomchadwin%2Fqgis2web.svg)](https://badge.fury.io/gh/tomchadwin%2Fqgis2web)
[![Donate](https://img.shields.io/badge/donate%20to-qgis2web-green)](https://www.opengis.it/buy-me-a-coffee/)
<h1>qgis2web</h1>

&nbsp;&nbsp;&nbsp;&nbsp;![qgis2web](https://github.com/qgis2web/qgis2web/blob/master/icons/qgis2web.png)

QGIS plugin to export your project to an OpenLayers or Leaflet webmap.</br>
It replicates as many aspects of the project as it can, including layers, extent and styles (including categorized and graduated).</br>
No server-side software required.

<h2>Installation</h2>
<ul>
    <li>In QGIS, select <code>Plugins > Manage and Install Plugins...</code></li>
</ul>
<p>or:</p>
<ul>
    <li>Download and unzip this repo to your QGIS plugins directory</li>
</ul>

<h2>Usage</h2>
<p>Prepare your map as far as possible in QGIS, as you want it to appear in
your webmap. Specific tasks you can carry out to improve your webmap include:
</p>
<ul>
    <li>Set your project title, and background and highlight colours in 
        <code>Project > Project Properties...</code></li>
    <li>Give your layers human-friendly names in the <code>Layers Panel</code>
    </li>
    <li>Give your layer columns human friendly names via <code>Layer > Properties > Fields > Alias</code></li>
    <li>Hide the columns you don't want to appear in your popups by changing
        their Edit widget to "Hidden"</li>
    <li>If any of your fields contain image filenames, change their Edit
        widget to "Photo" to have the images appear in popups</li>
    <li>Style your layers, and set their scale-dependent visibility, if
        required</li>
</ul>
<p>Run qgis2web from the Web menu, or via its icon. If required, choose a
basemap from the list below the preview pane, and click "Update preview".
CTRL/CMD-click for multiple basemaps or to deselect a basemap.</p>
<p>The top-left pane lets you set options for each layer in your map. The
bottom-left pane sets overall options for your project. All options are written
to your QGIS project, so save your project if you want to keep these settings.

<b>More info on the [WIKI](https://qgis2web.github.io/qgis2web/)</b>
</p>

<h2>Awards</h2>

qgis2web is among the winners of the [OSGeo:UK](https://uk.osgeo.org/agm/agm2023minutes.html) 2023 competition via GoFundGeo
</br>
![os geo uk](https://github.com/tomchadwin/qgis2web/assets/89784373/275553ce-39bd-42b2-81d3-12e551ce1261)


<h2>Donations</h2>
We are thrilled to see how widely our project is being used and appreciated around the world. The development and maintenance require significant time and effort, and we want to continue improving and adding new features.

Please consider a small donation; even a modest "virtual coffee" can help support our commitment to providing quality software. 

[<img src="https://github.com/tomchadwin/qgis2web/assets/89784373/3bf8e193-e65e-4dc6-a189-a9e669f98b1e">](https://www.opengis.it/buy-me-a-coffee/)
</br><b>🎁 As a token of our gratitude, donors will receive as a gift [qgis2opengis](https://github.com/andreaordonselli/qgis2opengis) (a plugin enhancing OpenLayers export of qgis2web).🎁</b>

Thank you for your support!
</br>Happy mapping!🗺️

<h2>Credits</h2>
<p>qgis2web is fundamentally a merge of Victor Olaya's qgis-ol3 and Riccardo
Klinger's qgis2leaf. It would not exist without their work. Thank you,
gentlemen. Thanks are also very much due to Paolo Cavallini, who suggested
and supported the merge.</p>
<ul>
    <li>@volaya</li>
    <li>@riccardoklinger</li>
    <li>@pcav</li>
</ul>

<p>Obviously, qgis2web could not exist without the following monumental
software:</p>
<ul>
    <li>QGIS</li>
    <li>OpenLayers</li>
    <li>Leaflet</li>
</ul>

<p>Thanks are also due for major code contributions to:</p>
<ul>
    <li>@akbargumbira</li>
    <li>@lucacasagrande</li>
    <li>@walkermatt</li>
    <li>@boesiii</li>
    <li>@ThomasG77</li>
    <li>@NathanW2</li>
    <li>@nyalldawson (FTP export for Faunalia/ENEL)</li>
    <li>@perliedman</li>
    <li>@olakov</li>
</ul>

<p>In addition, the following libraries have been used:</p>
<ul>
    <li>[ol-layerswitcher](https://github.com/walkermatt/ol-layerswitcher), by @walkermatt</li>
    <li>[Autolinker.js](https://github.com/gregjacobs/Autolinker.js), by @gregjacobs</li>
    <li>[requestAnimationFrame polyfill](https://gist.github.com/paulirish/1579671), by @paulirish</li>
    <li>Function.prototype.bind polyfill, by @mozilla</li>
    <li>[Leaflet.label](https://github.com/Leaflet/Leaflet.label), by @jacobtoye</li>
    <li>[Leaflet.Locate](https://github.com/domoritz/leaflet-locatecontrol), by @domoritz</li>
    <li>[Leaflet.markercluster](https://github.com/Leaflet/Leaflet.markercluster), by @danzel</li>
    <li>[leaflet-measure](https://github.com/ljagis/leaflet-measure), by @ljagis</li>
    <li>[leaflet-hash](https://github.com/mlevans/leaflet-hash), by @mlevans</li>
    <li>[proj4js](https://github.com/proj4js/proj4js), by @madair, @calvinmetcalf, @ahocevar and other</li>
    <li>[Proj4Leaflet](https://github.com/kartena/Proj4Leaflet), by @kartena</li>
    <li>[leaflet-search](https://github.com/stefanocudini/leaflet-search), by @stefanocudini</li>
    <li>[ol3-search-layer](https://github.com/webgeodatavore/ol3-search-layer), by @ThomasG77</li>
    <li>[simpleheat](https://github.com/mourner/simpleheat), by @mourner</li>
    <li>[OSMBuildings](https://github.com/kekscom/osmbuildings), by @kekscom</li>
    <li>[leaflet-multi-style](https://github.com/perliedman/leaflet-multi-style), by @perliedman</li>
    <li>[Leaflet.SvgShapeMarkers](https://github.com/rowanwins/Leaflet.SvgShapeMarkers), by @rowanwins</li>
    <li>[rbush](https://github.com/mourner/rbush), by @mourner</li>
    <li>[Labelgun](https://github.com/Geovation/labelgun), by @JamesMilnerUK</li>
    <li>[Leaflet.pattern](https://github.com/teastman/Leaflet.pattern), by @teastman</li>
    <li>[Leaflet.VectorGrid](https://github.com/Leaflet/Leaflet.VectorGrid), by @IvanSanchez</li>
    <li>[Leaflet.Control.Layers.Tree](https://github.com/jjimenezshaw/Leaflet.Control.Layers.Tree), by @jjimenezshaw</li>
</ul>
