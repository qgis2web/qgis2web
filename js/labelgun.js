(function webpackUniversalModuleDefinition(root, factory) {
	if(typeof exports === 'object' && typeof module === 'object')
		module.exports = factory(require("rbush"));
	else if(typeof define === 'function' && define.amd)
		define(["rbush"], factory);
	else if(typeof exports === 'object')
		exports["labelgun"] = factory(require("rbush"));
	else
		root["labelgun"] = factory(root["rbush"]);
})(this, function(__WEBPACK_EXTERNAL_MODULE_1__) {
return /******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, {
/******/ 				configurable: false,
/******/ 				enumerable: true,
/******/ 				get: getter
/******/ 			});
/******/ 		}
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = 0);
/******/ })
/************************************************************************/
/******/ ([
/* 0 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
  value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _rbush = __webpack_require__(1);

var _rbush2 = _interopRequireDefault(_rbush);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

/**
* @summary create a label gun instance with a hide and show label callback
* @param {function} hideLabel the function responsible for hiding the label on hide event
* @param {function} showLabel the function responsible for showing the label on show event
* @param {number} entries Higher value relates to faster insertion and slower search, and vice versa
*/
var labelgun = function () {
  function labelgun(hideLabel, showLabel, entries) {
    _classCallCheck(this, labelgun);

    var usedEntries = entries || 10;
    this.tree = (0, _rbush2.default)(usedEntries);
    this.allLabels = {};
    this.hasChanged = [];
    this.allChanged = false;
    this.hideLabel = hideLabel;
    this.showLabel = showLabel;
  }

  /**
   * @name _total
   * @summary get the total hidden or shown labels in the tree
   * @memberof labelgun.prototype
   * @param {string} state whether to return 'hide' or 'show' state label totals
   * @returns {number} total number of labels of that state
   * @private
   */


  _createClass(labelgun, [{
    key: "_total",
    value: function _total(state) {
      var total = 0;
      for (var i = 0, keys = Object.keys(this.allLabels); i < keys.length; i++) {
        if (this.allLabels[keys[i]].state == state) {
          total += 1;
        }
      }
      return total;
    }

    /**
     * @name totalShown
     * @memberof labelgun
     * @method
     * @summary Return the total number of shown labels
     * @returns {number} Return total number of labels shown
     * @public
     */

  }, {
    key: "totalShown",
    value: function totalShown() {
      return this._total("show");
    }

    /**
     * @name totalHidden
     * @memberof labelgun
     * @method
     * @summary Return the total number of hidden labels
     * @returns {number} Return total number of labels hidden
     * @public
     */

  }, {
    key: "totalHidden",
    value: function totalHidden() {
      return this._total("hide");
    }

    /**
     * @name getLabelsByState
     * @summary Provided a state get all labels of that state
     * @param {string} state - the state of the labels to get (show or hide)
     * @returns {array} Labels that match the given state (show or hide)
     * @private
     */

  }, {
    key: "_getLabelsByState",
    value: function _getLabelsByState(state) {
      var labels = [];
      for (var i = 0, keys = Object.keys(this.allLabels); i < keys.length; i++) {
        if (this.allLabels[keys[i]].state == state) {
          labels.push(this.allLabels[keys[i]]);
        }
      }
      return labels;
    }

    /**
     * @name getHidden
     * @memberof labelgun
     * @method
     * @summary Return an array of all the hidden labels
     * @returns {array} An array of hidden labels
     */

  }, {
    key: "getHidden",
    value: function getHidden() {
      return this._getLabelsByState("hide");
    }

    /**
     * @name getShown
     * @memberof labelgun
     * @method
     * @summary Return an array of all shown labels
     * @returns {array} An array of shown label
     */

  }, {
    key: "getShown",
    value: function getShown() {
      return this._getLabelsByState("show");
    }

    /**
     * @name getCollisions
     * @memberof labelgun
     * @method
     * @summary Return a set of collisions (hidden and shown) for a given label
     * @param {string} id - the ID of the label to get
     * @returns {array} The list of collisions
     */

  }, {
    key: "getCollisions",
    value: function getCollisions(id) {

      var label = this.allLabels[id];
      if (label === undefined) {
        throw Error("Label doesn't exist :" + JSON.stringify(id));
      }

      var collisions = this.tree.search(label);
      var self = collisions.indexOf(label);

      // Remove the label if it's colliding with itself
      if (self !== undefined) collisions.splice(self, 1);
      return collisions;
    }

    /**
     * @name getLabel
     * @memberof labelgun
     * @method
     * @summary Convenience function to return a label by ID
     * @param {string} id the ID of the label to get
     * @returns {object} The label object for the id
     */

  }, {
    key: "getLabel",
    value: function getLabel(id) {
      return this.allLabels[id];
    }

    /**
     * @name destroy
     * @memberof labelgun
     * @method
     * @summary Destroy the collision tree and labels
     * @returns {undefined}
     */

  }, {
    key: "destroy",
    value: function destroy() {
      this.tree.clear();
      this.allLabels = {};
    }

    /**
     * @name callLabelCallbacks
     * @memberof labelgun
     * @method
     * @summary Perform the related callback for a label depending on where its state is 'show' or 'hide'
     * @param {string} [forceState] - the class of which to change the label to
     * @returns {undefined}
     * @public
     */

  }, {
    key: "callLabelCallbacks",
    value: function callLabelCallbacks(forceState) {
      var _this = this;

      Object.keys(this.allLabels).forEach(function (id) {
        _this._callLabelStateCallback(_this.allLabels[id], forceState);
      });
    }

    /**
     * @name _callLabelStateCallback
     * @summary Calls the correct callback for a particular label depending on its state (hidden or shown)
     * @param {string} label the label to update
     * @param {string} forceState the state of which to change the label to ('show' or 'hide')
     * @returns {undefined}
     * @private
     */

  }, {
    key: "_callLabelStateCallback",
    value: function _callLabelStateCallback(label, forceState) {
      var state = forceState || label.state;
      if (state === "show") this.showLabel(label);
      if (state === "hide") this.hideLabel(label);
    }

    /**
    * @name compareLabels
    * @memberof labelgun
    * @method
    * @summary Calculates which labels should show and which should hide
    * @returns {undefined}
    */

  }, {
    key: "compareLabels",
    value: function compareLabels() {
      var _this2 = this;

      this.orderedLabels = Object.values(this.allLabels).sort(this._compare);

      this.orderedLabels.forEach(function (label) {

        var collisions = _this2.tree.search(label);

        if (collisions.length === 0 || _this2._allLower(collisions, label) || label.isDragged) {
          _this2.allLabels[label.id].state = "show";
        }
      });
    }

    /**
    * @name _allLower
    * @memberof labelgun
    * @method
    * @param {array} collisions - An array of collisions (label objects)
    * @param {object} label - The label to check 
    * @summary Checks if labels are of a lower weight, currently showing, or dragged
    * @returns {boolean} - Whether collision are lower or contain already shown or dragged labels
    * @private
    */

  }, {
    key: "_allLower",
    value: function _allLower(collisions, label) {
      var collision = void 0;
      for (var i = 0; i < collisions.length; i++) {
        collision = collisions[i];
        if (collision.state === "show" || collision.weight > label.weight || collision.isDragged) {
          return false;
        }
      }

      return true;
    }

    /**
     * @name _compare
     * @memberof labelgun
     * @method
     * @param {object} a - First object to compare
     * @param {object} b - Second object to compare
     * @summary Sets up the labels depending on whether all have changed or some have changed
     * @returns {number} - The sort value
     * @private
     */

  }, {
    key: "_compare",
    value: function _compare(a, b) {
      // High to Low
      if (a.weight > b.weight) return -1;
      if (a.weight < b.weight) return 1;
      return 0;
    }

    /**
     * @name setupLabelStates
     * @memberof labelgun
     * @method
     * @summary Sets up the labels depending on whether all have changed or some have changed
     * @returns {undefined}
     */

  }, {
    key: "setupLabelStates",
    value: function setupLabelStates() {
      var _this3 = this;

      if (this.allChanged) {

        this.allChanged = false;
        this.hasChanged = [];
        this.tree.clear();

        Object.keys(this.allLabels).forEach(function (id) {
          _this3._handleLabelIngestion(id);
        });
      } else if (this.hasChanged.length > 0) {

        this.hasChanged.forEach(function (id) {
          _this3._handleLabelIngestion(id);
        });

        this.hasChanged = [];
      }
    }

    /**
     * @name _handleLabelIngestion
     * @memberof labelgun
     * @method
     * @summary DRY function for ingesting labels
     * @returns {undefined}
     * @param {string} id - ID of the label to ingest
     * @private
     */

  }, {
    key: "_handleLabelIngestion",
    value: function _handleLabelIngestion(id) {
      var label = this.allLabels[id];

      this.ingestLabel({
        bottomLeft: [label.minX, label.minY],
        topRight: [label.maxX, label.maxY]
      }, label.id, label.weight, label.labelObject, label.name, label.isDragged);
    }

    /**
     * @name update
     * @memberof labelgun
     * @method
     * @summary Sets all labels to change and reruns the whole show/hide procedure
     * @returns {undefined}
     */

  }, {
    key: "update",
    value: function update() {

      this.allChanged = true;
      this.setupLabelStates();
      this.compareLabels();
      this.callLabelCallbacks();
    }

    /**
     * @name _removeFromTree
     * @memberof labelgun
     * @method
     * @param {object} label - The label to remove from the tree
     * @param {boolean} forceUpdate if true, triggers all labels to be updated
     * @summary Removes label from tree
     * @returns {undefined}
     * @private
     */

  }, {
    key: "_removeFromTree",
    value: function _removeFromTree(label, forceUpdate) {
      var id = label.id;
      var removelLabel = this.allLabels[id];
      this.tree.remove(removelLabel);
      delete this.allLabels[id];

      if (forceUpdate) this.callLabelCallbacks(true);
    }

    /**
     * @name _addToTree
     * @memberof labelgun
     * @method
     * @param {object} label - The label to add to the tree
     * @summary inserts label into tree
     * @returns {undefined}
     * @private
     */

  }, {
    key: "_addToTree",
    value: function _addToTree(label) {
      this.allLabels[label.id] = label;
      this.tree.insert(label);
    }

    /**
     * @name ingestLabel
     * @memberof labelgun
     * @method
     * @param {object} boundingBox - The bounding box object with bottomLeft and topRight properties
     * @param {string} id - The idea of the label
     * @param {number} weight - The weight to compareLabels in the collision resolution
     * @param {object} labelObject - The object representing the actual label object from your mapping library
     * @param {string} labelName - A string depicting the name of the label
     * @param {boolean} isDragged - A flag to say whether the lable is being dragged
     * @summary Creates a label if it does not already exist, then adds it to the tree, and renders it based on whether it can be shown
     * @returns {undefined} 
     * @public
     */

  }, {
    key: "ingestLabel",
    value: function ingestLabel(boundingBox, id, weight, labelObject, labelName, isDragged) {

      // Add the new label to the tree
      if (weight === undefined || weight === null) {
        weight = 0;
      }

      if (!boundingBox || !boundingBox.bottomLeft || !boundingBox.topRight) {
        throw Error("Bounding box must be defined with bottomLeft and topRight properties");
      }

      if (typeof id !== "string" && typeof id !== "number") {
        throw Error("Label IDs must be a string or a number");
      }

      // If there is already a label in the tree, remove it
      var oldLabel = this.allLabels[id];
      if (oldLabel) this._removeFromTree(oldLabel);

      var label = {
        minX: boundingBox.bottomLeft[0],
        minY: boundingBox.bottomLeft[1],
        maxX: boundingBox.topRight[0],
        maxY: boundingBox.topRight[1],
        state: "hide",
        id: id,
        weight: weight,
        labelObject: labelObject,
        name: labelName,
        isDragged: isDragged
      };

      this._addToTree(label);
    }

    /**
     * @name labelHasChanged
     * @memberof labelgun
     * @param {string} id - The id of the label that has changed in some way
     * @method
     * @summary Let labelgun know the label has changed in some way (i.e. it's state for example, or that it is dragged)
     * @returns {undefined}
     */

  }, {
    key: "labelHasChanged",
    value: function labelHasChanged(id) {
      if (this.hasChanged.indexOf(id) === -1) {
        this.hasChanged.push(id);
      }
    }
  }]);

  return labelgun;
}();

exports.default = labelgun;

/***/ }),
/* 1 */
/***/ (function(module, exports) {

module.exports = __WEBPACK_EXTERNAL_MODULE_1__;

/***/ })
/******/ ]);
});