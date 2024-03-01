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
    <li>Set your project title, and background and highlight colours in <code>Project > Properties...</code></li>
    <li>Give your layers human-friendly names in the <code>Layers Panel</code></li>
    <li>Give your layer columns human friendly names via <code>Layer > Properties > Attributes Form > Fields > Alias</code></li>
    <li>Hide the columns you don't want to appear in your popups by changing their Widget Type to "Hidden"</li>
    <li>If any of your fields contain image's path, change their Widget Type to "Attachment" to have the images appear in popups</li>
    <li>Style your layers, and set their scale-dependent visibility, if required</li>
</ul>
<p>Run qgis2web from the Web menu, or via its icon in Web toolbar.</p>
<p>The panes lets you set options to export your map. All options are written to your QGIS project, so save your project if you want to keep these settings.

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
    <li>ol3-layerswitcher, by @walkermatt</li>
    <li>Autolinker.js, by @gregjacobs</li>
    <li>requestAnimationFrame polyfill, by @paulirish</li>
    <li>Function.prototype.bind polyfill, by @mozilla</li>
    <li>Leaflet.label, by @jacobtoye</li>
    <li>Leaflet.Locate, by @domoritz</li>
    <li>Leaflet.markercluster, by @danzel</li>
    <li>leaflet-measure, by @ljagis</li>
    <li>leaflet-hash, by @mlevans</li>
    <li>Proj4js, by @madair, @calvinmetcalf, and other</li>
    <li>Proj4Leaflet, by @kartena</li>
    <li>Leaflet.search, by @stefanocudini</li>
    <li>ol3-search-layer, by @ThomasG77</li>
    <li>Leaflet.heat, by @mourner</li>
    <li>OSMBuildings, by @kekscom</li>
    <li>multi-style-layer, by @perliedman</li>
    <li>Leaflet.SvgShapeMarkers, by @rowanwins</li>
    <li>rbush, by @mourner</li>
    <li>Labelgun, by @JamesMilnerUK</li>
    <li>Leaflet.pattern, by @teastman</li>
    <li>Leaflet.VectorGrid, by @IvanSanchez</li>
</ul>
