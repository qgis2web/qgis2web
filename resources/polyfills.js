if (!Function.prototype.bind) {
    Function.prototype.bind = function(oThis) {
        if (typeof this !== 'function') {
            // closest thing possible to the ECMAScript 5
            // internal IsCallable function
            throw new TypeError('Function#bind - not callable');
        }

        var aArgs   = Array.prototype.slice.call(arguments, 1),
            fToBind = this,
            fNOP    = function() {},
            fBound  = function() {
              return fToBind.apply(this instanceof fNOP
                     ? this
                     : oThis,
                     aArgs.concat(Array.prototype.slice.call(arguments)));
            };

        if (this.prototype) {
            // native functions don't have a prototype
            fNOP.prototype = this.prototype;
        }
        fBound.prototype = new fNOP();

        return fBound;
    };
}

/**
 * requestAnimationFrame polyfill v1.0.0
 * requires Date.now
 *
 * © Polyfiller 2015
 * Released under the MIT license
 * github.com/Polyfiller/requestAnimationFrame
 */
window.requestAnimationFrame || function (window) {

    'use strict';

    window.requestAnimationFrame = window.msRequestAnimationFrame
    || window.mozRequestAnimationFrame
    || window.webkitRequestAnimationFrame
    || function () {

        var fps = 60;
        var delay = 1000 / fps;
        var animationStartTime = Date.now();
        var previousCallTime = animationStartTime;

        return function requestAnimationFrame(callback) {

            var requestTime = Date.now();
            var timeout = Math.max(0, delay - (requestTime - previousCallTime));
            var timeToCall = requestTime + timeout;

            previousCallTime = timeToCall;

            return window.setTimeout(function onAnimationFrame() {

                callback(timeToCall - animationStartTime);

            }, timeout);
        };
    }();

    window.cancelAnimationFrame = window.mozCancelAnimationFrame
    || window.webkitCancelAnimationFrame
    || window.cancelRequestAnimationFrame
    || window.msCancelRequestAnimationFrame
    || window.mozCancelRequestAnimationFrame
    || window.webkitCancelRequestAnimationFrame
    || function cancelAnimationFrame(id) {
           window.clearTimeout(id);
       };

}(this);

