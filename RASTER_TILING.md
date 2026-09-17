# Native raster tiling (this fork)

This fork of [qgis2web](https://github.com/tomchadwin/qgis2web) adds an
export option that qgis2web itself has never had: large raster layers
(drone orthophotos, etc.) can be exported as a real XYZ tile pyramid
(`{z}/{x}/{y}.png`) instead of one giant `L.imageOverlay` image. See
upstream issue [#669](https://github.com/tomchadwin/qgis2web/issues/669).

Tiling is done with GDAL's `gdal2tiles` (bundled with QGIS, called
in-process — no subprocess, no separate install), resampling directly
from the source raster's pixels. It does **not** go through QGIS's map
canvas/renderer, so quality matches the `gdal2tiles.py` CLI, not the
"QTiles"-plugin-style rendering pipeline (which resamples per rendered
tile and loses sharpness).

## What changed vs. upstream

- `utils.py`: `exportRasterTiles()`, `shouldTileRaster()`, `rasterSourcePath()`,
  `rasterPixelCount()`, and the `RASTER_TILE_PIXEL_THRESHOLD` (16 MP) constant.
- `leafletScriptStrings.py`: `rasterTileScript()` emits `L.tileLayer(...)`
  instead of `L.imageOverlay(...)`.
- `leafletWriter.py`: routes each raster layer to the tiled or the classic
  single-image export depending on the per-layer setting below.
- `maindialog.py`: adds a per-raster-layer row in the layer tree ("Tile
  natively (GDAL, for large orthophotos)") with optional Zmin/Zmax fields,
  analogous to the existing "PBF Vector Tile" row for vector layers.
- Only the **Leaflet** writer was touched. The OpenLayers writer still
  exports rasters as a single image (not in scope here).

## Using it

1. Add your raster layer (e.g. a drone orthomosaic GeoTIFF) to the project as usual.
2. Open the qgis2web export dialog. In the layer tree, expand the raster
   layer — you'll see **"Tile natively (GDAL, for large orthophotos)"**.
   - It's checked automatically for rasters over ~16 megapixels (about
     4000×4000 px); smaller rasters default to the old single-image
     behavior. You can override this per layer.
   - Zmin/Zmax are optional. Leave them blank to let GDAL pick the zoom
     range from the raster's native resolution (recommended — this is
     exactly what `gdal2tiles.py` does at the CLI).
3. Export as usual. Tiles land in `data/<layer>_<n>_tiles/<z>/<x>/<y>.png`
   inside the export folder; everything is relative-path based like the
   rest of a qgis2web export.

### Transparency / irregular edges

If the raster layer has a defined NoData value on all bands (Properties →
Transparency, or already baked into the file), it's passed to
`gdal2tiles` as `--srcnodata`, so pixels outside the flight footprint come
out as a transparent alpha channel per tile — no black/white boxes at the
edges. A 4-band RGBA GeoTIFF with an alpha band works the same way without
any extra configuration.

## Local dev setup used for this fork

- QGIS 3.40.11 (LTR), bundled Python 3.12, bundled GDAL 3.11.3 — all
  already include `osgeo` and `osgeo_utils.gdal2tiles`, so no extra
  Python packages are needed.
- The QGIS profile's plugin folder has a **directory junction** (not a
  regular copy) pointing at this checkout, so edits here are picked up by
  a running QGIS immediately after Plugin Reloader / restarting QGIS:

  ```powershell
  # from an elevated-not-required PowerShell (junctions don't need admin rights,
  # unlike symlinks on Windows)
  cmd /c mklink /J "$env:APPDATA\QGIS\QGIS3\profiles\default\python\plugins\qgis2web" "E:\VS_Code\qgis2web_fork"
  ```

  The previous plugin-manager install was preserved at
  `...\python\plugins\qgis2web_plugin_manager_backup` in case you want to
  revert (delete the junction and rename that folder back to `qgis2web`).

- To run one-off scripts against QGIS's own Python (not your system
  Python — GDAL bindings live only in QGIS's bundled interpreter), use the
  bundled launcher and pass `-s` to skip any conflicting packages in your
  Windows user site-packages (a stray `numpy` there breaks GDAL's
  `gdal_array`/`WriteArray` on this machine, though it doesn't affect
  `gdal2tiles` itself):

  ```powershell
  & "C:\Program Files\QGIS 3.40.11\bin\python-qgis-ltr.bat" -s your_script.py
  ```

## Testing performed

- Generated a synthetic 5000×4500 px (22.5 MP), 5 cm/px GeoTIFF with an
  RGBA alpha channel and an irregular circular footprint on a transparent
  background, simulating a drone orthomosaic with an unregular flight-plan
  edge.
- Ran the export path (`exportRasterTiles`) against it through QGIS's own
  `QgsApplication`/`QgsRasterLayer` (not a mock): zoom range auto-detected
  as z17–z21 for the 5 cm/px source, matching `gdal2tiles.py`'s own
  resolution-based formula.
- Verified per-tile alpha at the top zoom level: tiles fully inside the
  footprint are fully opaque, tiles fully outside are fully transparent,
  and boundary tiles have a real partial-alpha edge — no black/white
  box artifacts.
- Assembled a minimal static site (`index.html` + `leaflet.js`/`leaflet.css`
  + the generated `data/<layer>_tiles/` folder) and served it with
  `python -m http.server`; confirmed real tile URLs return
  `200 image/png` and out-of-range tile URLs return `404` (Leaflet's
  normal, expected behavior for an XYZ layer — it silently skips missing
  tiles), and that the whole page works from purely relative paths.
- Did not (yet) visually confirm in an actual browser window inside this
  environment — do that once with your own orthophoto by opening the
  exported `index.html` (served via `python -m http.server`, not
  `file://`) and checking DevTools' Network tab while panning/zooming:
  you should see only the tiles for the current viewport/zoom being
  requested.

## Known limitations / not done

- OpenLayers writer: not updated, still single-image.
- No re-tiling cache/incremental export — every export re-tiles from
  scratch, which is fine for one-off publishing but slow if you iterate a
  lot on styling; consider disabling tiling temporarily while tweaking
  unrelated settings on a large layer.
- `rasterSourcePath()` assumes a plain local file GDAL provider
  (`layer.dataProvider().name() == "gdal"`); layers backed by WMS/WMTS/VRT
  subdatasets or other providers fall back to the old single-image path
  automatically (`shouldTileRaster()` only returns true for `"gdal"`
  providers).
