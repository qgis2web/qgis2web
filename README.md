[![GitHub version](https://badge.fury.io/gh/tomchadwin%2Fqgis2web.svg)](https://badge.fury.io/gh/tomchadwin%2Fqgis2web)
[![Coverage Status](https://coveralls.io/repos/github/tomchadwin/qgis2web/badge.svg?branch=master)](https://coveralls.io/github/tomchadwin/qgis2web?branch=master)
[![Join the chat at https://gitter.im/tomchadwin/qgis2web](https://badges.gitter.im/tomchadwin/qgis2web.svg)](https://gitter.im/tomchadwin/qgis2web?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Donate to QGIS](https://img.shields.io/badge/donate%20to-QGIS-green.svg)](http://qgis.org/en/site/getinvolved/donations.html)
<h1>qgis2web</h1>

&nbsp;&nbsp;&nbsp;&nbsp;![qgis2web](https://github.com/tomchadwin/qgis2web/blob/master/qgis2web.png)



<p>QGIS plugin to export your project to an OpenLayers or Leaflet webmap.
It replicates as many aspects of the project as it can, including layers, extent and styles (including categorized and graduated).
No server-side software required.</p>

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

<b>More info on the [WIKI](https://github.com/tomchadwin/qgis2web/wiki)</b>
</p>

<h2>Awards</h2>

qgis2web is among the winners of the [OSGeo:UK](https://uk.osgeo.org/agm/agm2023minutes.html) 2023 competition via GoFundGeo
![os geo uk](https://github.com/tomchadwin/qgis2web/assets/89784373/275553ce-39bd-42b2-81d3-12e551ce1261)


<h2>Donations</h2>
We are thrilled to see how widely our project is being used and appreciated around the world. The development and maintenance require significant time and effort, and we want to continue improving and adding new features.

Please consider a small donation; even a modest "virtual coffee" can help support our commitment to providing quality software. 

[<img src="https://github.com/tomchadwin/qgis2web/assets/89784373/3bf8e193-e65e-4dc6-a189-a9e669f98b1e">](https://www.opengis.it/buy-me-a-coffee/)
</br><b>🎁 As a token of our gratitude, donors will receive as a gift [qgis2opengis](https://github.com/andreaordonselli/qgis2opengis) (a plugin enhancing OpenLayers export of qgis2web).🎁</b>

Thank you for your support!
</br>Happy mapping!🗺️

<h2>Current limitations</h2>
<p>QGIS, OpenLayers, and Leaflet are all different mapping technologies.
This means that their respective functionality differs in many ways. qgis2web
does its best to interpret a QGIS project and to export HTML, Javascript, and
CSS to create a web map as close to the QGIS project as possible.</p>
<p>However, many elements of a QGIS project cannot be reproduced, and many are
only possible in <em>either</em> OpenLayers <em>or</em> Leaflet. qgis2web
tries its best to produce a publish-ready map, but you can always manually edit
the output code to achieve what qgis2web cannot.</p>
<ul>
    <li>in OL3 maps, only single rendered points cluster, not categorized
        or graduated</li>
    <li>line style (dashed/dotted) does not appear in OL3 preview, but works in
        export</li>
    <li>only a single 2.5d layer will render per map</li>
    <li>2.5d layers only appear when zoomed in to building scales</li>
    <li>attribute filters and abstract export only works in leaflet based webmaps</li>
</ul>

<h2>Reporting bugs</h2>
<p>Please report any problems you have with qgis2web. Without this feedback, I
am often completely unaware that a problem exists. To ensure no time or effort
is wasted in bug reporting, please follow these steps:</p>
<ol>
    <li>Make sure you are using the latest release of qgis2web</li>
    <li>Check the issues on Github to see whether the bug has already been
        reported, and if so, read through all the comments on the issue, and
        add any additional information from your experience of the bug</li>
    <li>Make sure you can reproduce the bug reliably</li>
    <li>Reduce the complexity of your bug conditions as far as you can,
        especially by reducing the number of layers, ideally to one</li>
    <li>Raise a Github issue, including:
    <ul>
        <li>only one bug per Github issue</li>
        <li>the qgis2web version (or make it clear you are using Github master
            branch)</li>
        <li>any Python error text/stack trace which occurs</li>
        <li>browser JS console errors - press F12 in qgis2web to open the 
            developer toolbar and find the console</li>
        <li>screenshot of your settings</li>
        <li>screenshot of the output</li>
        <li>a link to the data you used, if possible</li>
    </ul></li>
</ol>
<p>The stability of qgis2web relies on your bug reports, so please keep them
coming.</p>

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


[![Greenkeeper badge](https://badges.greenkeeper.io/tomchadwin/qgis2web.svg)](https://greenkeeper.io/)
