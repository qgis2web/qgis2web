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
    <li>Find <code>qgis2web</code></li>
</ul>
<p>or:</p>
<ul>
    <li><a href="https://github.com/qgis2web/qgis2web/archive/master.zip" target="_blank">Download</a> master repository from github</li>
	<li>In QGIS, open <code>Plugins &gt; Manage and Install Plugins... &gt; Install from ZIP</code></li>	
				
</ul>

<h2>Usage</h2>
<p>Prepare your QGIS map with simple symbologies. You can improve your webmap like this:
</p>
<ul>
    <li>Set your project title, abstract, background and highlight colours in <code>Project > Properties... > General/Metadata</code></li>
    <li>Give your layers human-friendly names in <code>Layers Panel</code></li>
    <li>Give your layer columns human friendly names via <code>Layer > Properties > Attributes Form > Fields > Alias</code></li>
    <li>Hide fields you don't want to appear in your popups by changing their Widget Type to "Hidden"</li>
    <li>Show media in your popups by changing their Widget Type to "Attachment" (your fields must contain image's path)</li>
    <li>Style your layers as explained in [WIKI](https://qgis2web.github.io/qgis2web/), and set their scale-dependent visibility, if required</li>
</ul>
<p>Run qgis2web from the Web menu, or via its icon in Web toolbar</p>
<p>The panes lets you set options to export your map. All options are written to your QGIS project, so save your project if you want to keep these settings.
</p>

<h2>Documentation</h2>

Read documentation on the [WIKI](https://qgis2web.github.io/qgis2web/)

<h2>Awards</h2>

qgis2web is among the winners of the [OSGeo:UK](https://uk.osgeo.org/agm/agm2023minutes.html) 2023 competition via GoFundGeo
</br>
![os geo uk](https://github.com/tomchadwin/qgis2web/assets/89784373/275553ce-39bd-42b2-81d3-12e551ce1261)


<h2>Donations</h2>
We are thrilled to see how widely our project is being used and appreciated around the world. The development and maintenance require significant time and effort, and we want to continue improving and adding new features.

Please consider a small donation; even a modest "virtual coffee" can help support our commitment to providing quality software. 

[<img src="https://github.com/tomchadwin/qgis2web/assets/89784373/3bf8e193-e65e-4dc6-a189-a9e669f98b1e">](https://www.opengis.it/buy-me-a-coffee/)
</br><b>🎁 As a token of our gratitude, donors will receive as a gift [qgis2o.gis](https://github.com/andreaordonselli/qgis2o.gis) (a plugin enhancing OpenLayers export of qgis2web).🎁</b>

Thank you for your support!
</br>Happy mapping!🗺️

<h2>Credits</h2>
qgis2web's author is Tom Chadwin (@tomchadwin), in charge as official developer from April 2015 to November 2023, from this date Andrea Ordonselli (@andreaordonselli) took over.
<p>The list of all other contributing developers is available at this link https://github.com/qgis2web/qgis2web/graphs/contributors
<p>For qgis2web enthusiasts we recommend reading this splendid article written by Tom which describes the birth and growth of qgis2web:
https://tom.chadw.in/wrote/qgis2webTheStorySoFar

<p>In short words:
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
    <li><a href="https://github.com/walkermatt/ol-layerswitcher">ol-layerswitcher</a>, by @walkermatt</li>
    <li><a href="https://github.com/gregjacobs/Autolinker.js">Autolinker.js</a>, by @gregjacobs</li>
    <li><a href="https://gist.github.com/paulirish/1579671">requestAnimationFrame polyfill</a>, by @paulirish</li>
    <li>Function.prototype.bind polyfill, by @mozilla</li>
    <li><a href="https://github.com/Leaflet/Leaflet.label">Leaflet.label</a>, by @jacobtoye</li>
    <li><a href="https://github.com/domoritz/leaflet-locatecontrol">Leaflet.Locate</a>, by @domoritz</li>
    <li><a href="https://github.com/Leaflet/Leaflet.markercluster">Leaflet.markercluster</a>, by @danzel</li>
    <li><a href="https://github.com/ljagis/leaflet-measure">leaflet-measure</a>, by @ljagis</li>
    <li><a href="https://github.com/mlevans/leaflet-hash">leaflet-hash</a>, by @mlevans</li>
    <li><a href="https://github.com/proj4js/proj4js">proj4js</a>, by @madair, @calvinmetcalf, @ahocevar and others</li>
    <li><a href="https://github.com/kartena/Proj4Leaflet">Proj4Leaflet</a>, by @kartena</li>
    <li><a href="https://github.com/stefanocudini/leaflet-search">leaflet-search</a>, by @stefanocudini</li>
    <li><a href="https://github.com/webgeodatavore/ol3-search-layer">ol3-search-layer</a>, by @ThomasG77</li>
    <li><a href="https://github.com/mourner/simpleheat">simpleheat</a>, by @mourner</li>
    <li><a href="https://github.com/kekscom/osmbuildings">OSMBuildings</a>, by @kekscom</li>
    <li><a href="https://github.com/perliedman/leaflet-multi-style">leaflet-multi-style</a>, by @perliedman</li>
    <li><a href="https://github.com/rowanwins/Leaflet.SvgShapeMarkers">Leaflet.SvgShapeMarkers</a>, by @rowanwins</li>
    <li><a href="https://github.com/mourner/rbush">rbush</a>, by @mourner</li>
    <li><a href="https://github.com/Geovation/labelgun">Labelgun</a>, by @JamesMilnerUK</li>
    <li><a href="https://github.com/teastman/Leaflet.pattern">Leaflet.pattern</a>, by @teastman</li>
    <li><a href="https://github.com/Leaflet/Leaflet.VectorGrid">Leaflet.VectorGrid</a>, by @IvanSanchez</li>
    <li><a href="https://github.com/jjimenezshaw/Leaflet.Control.Layers.Tree">Leaflet.Control.Layers.Tree</a>, by @jjimenezshaw</li>
</ul>

