QGIS to OpenLayers 3
=====================

Converts your QGIS project into an OpenLayers 3 map.

Current version includes the following features:

- Built-in preview.

- Support for both raster and vector layers.

- Support for WMS (if the service support EPSG:3857).

- Symbology exporting, including:

	- Basic styles for points, lines and polygons (single symbol, categorized, graduated).

	- SVG icons for point markers.

	- Labeling.

	- Transparency.

- Add layers list.

- Basic support for groups.

- Add scale bar.

- Add feature info popup for selected layers, based on a given field, on hover or on click.

- Template-based, so new templates can be easily be created

- Automatically minifies GeoJSON output files and removes unused attributes.

- Template-based, so new templates can be easily be created

- Add highlight function to highlight features when passing the mouse pointer over them.

Usage is documented `here <./doc/usage.rst>`_.

JavaScript libraries used by exported page
==========================================

- The generated code uses:

    - `OL3 <http://openlayers.org/>`_
    - `OL3 LayerSwitcher <https://github.com/walkermatt/ol3-layerswitcher/>`_
    - `jQuery <http://jquery.com/>`_
