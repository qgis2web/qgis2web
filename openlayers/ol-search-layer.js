function hasClass(el, cls) {
  return el.className && new RegExp('(\\s|^)' +
    cls + '(\\s|$)').test(el.className);
}

function addClass(elem, className) {
  if (!hasClass(elem, className)) {
    elem.className += ' ' + className;
  }
}

function removeClass(elem, className) {
  var newClass = ' ' + elem.className.replace(/[\t\r\n]/g, ' ') + ' ';
  if (hasClass(elem, className)) {
    while (newClass.indexOf(' ' + className + ' ') >= 0) {
      newClass = newClass.replace(' ' + className + ' ', ' ');
    }
    elem.className = newClass.replace(/^\s+|\s+$/g, '');
  }
}


class SearchLayer extends ol.control.Control {
  constructor(optOptions) {
    const horseyComponentRef = { current: null };
    const selectRef = { current: null };

    const options = optOptions || {};
    if (!options.layer) {
      throw new Error('Missing layer in options');
    }
	
	options.maxResults = (optOptions && typeof optOptions.maxResults === 'number') 
	  ? optOptions.maxResults 
	  : 10;

    options.map = optOptions.map;
    options.colName = optOptions.colName;

    // Detect vector source
    let source;
    if (options.layer instanceof ol.layer.Image &&
        options.layer.getSource() instanceof ol.source.ImageVector) {
      source = options.layer.getSource().getSource();
    } else if (options.layer instanceof ol.layer.Vector) {
      source = options.layer.getSource();
    }
	if (source instanceof ol.source.Cluster) {
	  source = source.getSource();
	}

    // Create button
    const button = document.createElement('button');
    const toggleHideShowInput = () => {
      const input = document.querySelector('form > .search-layer-input-search');
      if (hasClass(input, 'search-layer-collapsed')) {
        removeClass(input, 'search-layer-collapsed');
      } else {
        input.value = '';
        addClass(input, 'search-layer-collapsed');
        if (horseyComponentRef.current) {
          horseyComponentRef.current.hide();
        }
        if (selectRef.current) {
          selectRef.current.getFeatures().clear();
        }
      }
    };

    button.addEventListener('click', toggleHideShowInput, false);
    button.addEventListener('touchstart', toggleHideShowInput, false);

    // Create input
    const form = document.createElement('form');
    form.setAttribute('id', 'random');
    form.onsubmit = undefined;

    const input = document.createElement('input');
    input.setAttribute('id', 'ol-search-input');
    const defaultInputClass = ['search-layer-input-search'];
    if (optOptions.collapsed) {
      defaultInputClass.push('search-layer-collapsed');
    }
    input.setAttribute('class', defaultInputClass.join(' '));
    input.setAttribute('placeholder', 'Search ...');
    input.setAttribute('type', 'text');
    form.appendChild(input);

    // Build control element
    const element = document.createElement('div');
    element.className = 'search-layer ol-unselectable ol-control';
    element.appendChild(button);
    element.appendChild(form);

    // Initialize base class
    super({
      element: element,
      target: options.target
    });

    // Create select interaction
    const select = new ol.interaction.Select({
      id: options.selectId || 'defaultSearchLayer',
      layers: [options.layer],
      condition: ol.events.condition.never
    });

    selectRef.current = select;

    const map = options.map;
    map.addInteraction(select);

    // Setup horsey autocomplete
    const typesToZoomToExtent = [
      'MultiPoint', 'LineString', 'MultiLineString', 'MultiPolygon', 'Polygon'
    ];
    const typesToZoomToCenterAndZoom = ['Point'];

    const returnHorsey = (input, source, map, select, options) => {
      return horsey(input, {
        source: [{
          list: source.getFeatures().map((el, i) => {
            if (el.getId() === undefined) {
              el.setId(i);
            }
            return {
              text: el.get(options.colName),
              value: el.getId()
            };
          })
        }],
        getText: 'text',
        getValue: 'value',
		limit: options.maxResults,
        predictNextSearch: function(info) {
          const feat = source.getFeatureById(info.selection.value);
          const featType = feat.getGeometry().getType();

          if (typesToZoomToCenterAndZoom.includes(featType)) {
            const newCenter = ol.extent.getCenter(feat.getGeometry().getExtent());
            map.getView().setCenter(newCenter);
            map.getView().setZoom(options.zoom || 12);
          } else if (typesToZoomToExtent.includes(featType)) {
            map.getView().fit(feat.getGeometry().getExtent(), map.getSize());
          }

          select.getFeatures().clear();
          select.getFeatures().push(feat);
        }
      });
    };

    if (source.getState() === 'ready') {
      horseyComponentRef.current = returnHorsey(input, source, map, select, options);
    }

    source.once('change', () => {
      if (source.getState() === 'ready') {
        horseyComponentRef.current = returnHorsey(input, source, map, select, options);
      }
    });
  }
}
