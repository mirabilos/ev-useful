/*-
 * Copyright © 2014, 2020, 2023
 *	mirabilos <m@mirbsd.org>
 *
 * Provided that these terms and disclaimer and all copyright notices
 * are retained or reproduced in an accompanying document, permission
 * is granted to deal in this work without restriction, including un‐
 * limited rights to use, publicly perform, distribute, sell, modify,
 * merge, give away, or sublicence.
 *
 * This work is provided “AS IS” and WITHOUT WARRANTY of any kind, to
 * the utmost extent permitted by applicable law, neither express nor
 * implied; without malicious intent or gross negligence. In no event
 * may a licensor, author or contributor be held liable for indirect,
 * direct, other damage, loss, or other issues arising in any way out
 * of dealing in the work, even if advised of the possibility of such
 * damage or existence of a defect, except proven that it results out
 * of said person’s immediate fault when using the work as intended.
 */
"use strict";

/* make this work with nodejs and in browsers */
(function _closure_usefulJS(G) {

var _hasOwnProperty = Object.prototype.hasOwnProperty;
var _toString = Object.prototype.toString;

var _isArray = function isArray(o) {
	return (_toString.call(o) === "[object Array]");
    };
if (typeof(Array.isArray) === "function" &&
    Array.isArray([]) && !Array.isArray({}))
	_isArray = Array.isArray;

var _needsdom = function _unavailable_outside_browser() {
	throw "unavailable without document object";
    };

/**
 * Usage:
 *
 * usefulJS.hOP = Object.prototype.hasOwnProperty
 * usefulJS.toString = Object.prototype.toString
 * usefulJS.isArray = Array.isArray or polyfill
 * usefulJS.filter(array, callback): array.filter(callback) or polyfill
 * usefulJS.zpad(n, l, f=0): sprintf("%0*s", l, n.toFixed(f))
 * usefulJS.ISO8601(dateobject): dateobject.toISOString() timezone-aware
 *     (arguments can also be these of the Date constructor)
 * usefulJS.date2mjd(dateobject) → [mjd, seconds]
 * usefulJS.mjd2date(mjd, seconds): Modified Julian Date to js Date object
 */
G.hOP = _hasOwnProperty;
G.toString = Object.prototype.toString;
G.isArray = _isArray;
G.filter = Array.prototype.filter ? function filter(a, cb) {
	return (a.filter(cb));
    } : function filter(a, cb) {
	var res = [], i, v;
	for (i = 0; i < a.length; ++i)
		if (usefulJS.hOP.call(a, i)) {
			v = a[i];
			if (cb(v, i, a))
				res.push(v);
		}
	return (res);
    };

var _zpad = function zeropad(number, len, fractional) {
	var res = Number(number).toFixed(fractional ? fractional : 0);
	while (res.length < len)
		res = "0" + res;
	return (res);
    };
G.zeropad = _zpad;

// helper, not exported
var _makeDateObject = function _makeDateObject() {
	var a = arguments;
	switch (a.length) {
	case 0: return (new Date());
	case 1: return (new Date(a[0]));
	case 2: return (new Date(a[0], a[1]));
	case 3: return (new Date(a[0], a[1], a[2]));
	case 4: return (new Date(a[0], a[1], a[2], a[3]));
	case 5: return (new Date(a[0], a[1], a[2], a[3], a[4]));
	case 6: return (new Date(a[0], a[1], a[2], a[3], a[4], a[5]));
	default: return (new Date(a[0], a[1], a[2], a[3], a[4], a[5], a[6]));
	}
    };
var _getDateObject = function _getDateObject(a1) {
	if (_toString.call(a1) === "[object Date]" && !isNaN(a1))
		return (a1);
	return (_makeDateObject.apply(null, arguments));
    };

G.ISO8601 = function ISO8601(dateobject) {
	/* could be called like Date constructor */
	var d = _getDateObject.apply(null, arguments);
	var Y = d.getFullYear(),
	    M = d.getMonth() + 1,
	    D = d.getDate(),
	    h = d.getHours(),
	    m = d.getMinutes(),
	    s = d.getSeconds(),
	    S = d.getMilliseconds(),
	    o = d.getTimezoneOffset(),
	    r, oh, om;
	if (!o)
		r = "Z";
	else {
		if (o < 0) {
			r = "+";
			o = -o;
		} else
			r = "-";
		om = o % 60;
		oh = (o - om) / 60;
		r += _zpad(oh, 2) + ":" + _zpad(om, 2);
	}
	r = "-" + _zpad(M, 2) + "-" + _zpad(D, 2) + "T" +
	    _zpad(h, 2) + ":" + _zpad(m, 2) + ":" + _zpad(s, 2) +
	    "." + _zpad(S, 3) + r;
	if (Y < 0)
		r = "-" + _zpad(-Y, 4) + r;
	else if (Y > 9999)
		r = "+" + _zpad(Y, 5) + r;
	else
		r = _zpad(Y, 4) + r;
	return (r);
    };

G.date2mjd = function date2mjd(dateobject) {
	/* could be called like Date constructor */
	var d = _getDateObject.apply(null, arguments);
	var s = d.valueOf() / 1000;
	var sec = s % 86400;
	var mjd = (s - sec) / 86400 + 40587;
	sec = Number(sec.toFixed(3));
	while (sec < 0) {
		--mjd;
		sec += 86400;
	}
	return ([mjd, sec]);
    };

G.mjd2date = function mjd2date(mjd, sec) {
	var s = (mjd - 40587) * 86400 + sec;
	return (new Date(s));
    };

/**
 * Escape plaintext, such as from textarea.value, for HTML such as in
 * span.innerHTML: entities for amp, lt, gt and (numeric) the double,
 * but not⚠ single, quote; "<br />" for newlines.
 */
G.text2html = (function _closure_text2html() {
	var ra = /&/g;
	var rl = /</g;
	var rg = />/g;
	var rq = /"/g;
	var rn = /\n/g;

	return (function text2html(s) {
		return (String(s)
		    .replace(ra, "&amp;")
		    .replace(rl, "&lt;")
		    .replace(rg, "&gt;")
		    .replace(rq, "&#34;")
		    .replace(rn, "<br />")
		    );
	    });
    })();

/**
 * Make a string XML/HTML/XHTML/tty-safe: substitute codepoints not
 * permitted by XML/HTML: CRLF for NEL and FF, U+FFFD for the rest:
 * C0 control characters except Tab, CR, LF; C1 control characters;
 * DEL; surrogates; noncharacters (U+FFFE‥U+FFFF and others).
 */
G.xhtsafe = (function _closure_xhtsafe() {
	var re = /((?:[\t\n\r -~\xA0-\uD7FF\uE000-\uFDCF\uFDF0-\uFFFD]|[\uD800-\uD83E\uD840-\uD87E\uD880-\uD8BE\uD8C0-\uD8FE\uD900-\uD93E\uD940-\uD97E\uD980-\uD9BE\uD9C0-\uD9FE\uDA00-\uDA3E\uDA40-\uDA7E\uDA80-\uDABE\uDAC0-\uDAFE\uDB00-\uDB3E\uDB40-\uDB7E\uDB80-\uDBBE\uDBC0-\uDBFE][\uDC00-\uDFFF]|[\uD83F\uD87F\uD8BF\uD8FF\uD93F\uD97F\uD9BF\uD9FF\uDA3F\uDA7F\uDABF\uDAFF\uDB3F\uDB7F\uDBBF\uDBFF][\uDC00-\uDFFD])+)/;
	var rs = /[\x0C\x85]/g;

	return (function xhtsafe(s) {
		var i, j, o = "";
		var g = String(s).replace(rs, "\r\n").split(re);

		for (i = 0; i < g.length; ++i) {
			for (j = 0; j < g[i].length; ++j)
				o += "\uFFFD";
			if (++i < g.length)
				o += g[i];
		}
		return (o);
	    });
    })();

/**
 * Usage:
 *
 * • deferDOM(some_function);
 *   enqueues the function as callback (or runs it now)
 * • deferDOM()
 *   just returns the status
 *
 * Both return true if the DOM is ready, false otherwise.
 */
G.deferDOM = (function _closure_deferDOM() {
	if (typeof(document) === "undefined")
		return (_needsdom);

	var called = false;
	var tmo = false;
	var callbackfns = [];
	var handler = function deferDOM_handler() {
		/* execute once only */
		if (called)
			return;
		called = true;
		/* clear event handlers and timers */
		if (document.addEventListener) {
			document.removeEventListener("DOMContentLoaded",
			    handler, false);
			window.removeEventListener("load", handler, false);
		} else {
			if (tmo !== false)
				window.clearTimeout(tmo);
			window.detachEvent("onload", handler);
		}
		/* run user callbacks */
		var i;
		for (i = 0; i < callbackfns.length; ++i)
			callbackfns[i]();
	    };

	/* install DOM readiness listeners */

	if (document.addEventListener) {
		/* Opera 9 and other modern browsers */
		document.addEventListener("DOMContentLoaded", handler, false);
		/* last resort: always works, but later than possible */
		window.addEventListener("load", handler, false);
	} else {
		/* IE or something */
		var tryPoll = false;
		if (document.documentElement.doScroll) {
			try {
				tryPoll = !window.frameElement;
			} catch (e) {}
		}
		if (tryPoll) {
			tryPoll = document.documentElement.doScroll;
			var poll = function deferDOM_poll() {
				try {
					tryPoll("left");
				} catch (e) {
					tmo = window.setTimeout(poll, 50);
					return;
				}
				handler();
			    };
			poll();
		}
		/* generic ancient browser */
		var rdychange = function deferDOM_rdychange() {
			if (document.readyState === "complete")
				handler();
			/* detach if ever called from anywhere */
			if (!called)
				return;
			document.detachEvent("onreadystatechange", rdychange);
		    };
		document.attachEvent("onreadystatechange", rdychange);
		/* last resort: always works, but later than possible */
		window.attachEvent("onload", handler);
	}

	/* already loaded? */
	if (document.readyState === "complete")
		handler();

	/* function that is called by the user */
	return (function deferDOM(cb) {
		/* DOM not ready yet? */
		if (!called) {
			/* enqueue into list of callbacks to run */
			if (typeof(cb) === "function")
				callbackfns.push(cb);
			return (false);
		}
		/* already ready, so just run callback now */
		if (typeof(cb) === "function")
			cb();
		return (true);
	    });
    })();

/**
 * Usage:
 *
 * • hashlib(cb);
 *   initialise hashlib if not yet done and, if cb is a function,
 *   register it to be called on document hash change, cumulative
 * • hashlib.get(key) → String|null|Array[String|null]|undefined
 *   retrieve value of a document hash parameter; null = present
 *   key without equals sign afterwards; undefined = absent key
 * • hashlib.set(key, value);
 *   set value of a hash parameter, stringified (use undefined to unset)
 * • hashlib.clear();
 *   remove all hash parameters
 * • hashlib.keys() → Array[String]* sorted
 *   list keys of currently set items
 *
 * Callbacks are called with the following parameters:
 * – String newhash (unparsed, but may access .get)
 * – bool set_initiated (true if called as result of calling .set/.clear
 *   so callee may ignore this invocation wrt. internal state synching)
 */
G.hashlib = (function _closure_hashlib() {
	if (typeof(document) === "undefined")
		return (_needsdom);

	var initialised = false;
	var set_initiated = false;
	var callbacks = [];
	var prevhash = "";
	var checkhash = function checkhash() {
		var newhash = String(document.location.href.split("#")[1] || "");
		if (prevhash !== newhash) {
			var ign = set_initiated;
			prevhash = newhash;
			set_initiated = false;
			if (newhash === "%20" || newhash === " ")
				newhash = "";
			var i;
			for (i = 0; i < callbacks.length; ++i)
				callbacks[i](newhash, ign);
		}
	    };
	var keys = [];
	var values = {};
	callbacks.push(function cbparse(h, ignorechange) {
		if (ignorechange)
			return;
		keys = [];
		values = {};
		var pairs = h.split("&"), i, key, value, pair;
		for (i = 0; i < pairs.length; ++i) {
			pair = pairs[i].split("=");
			key = decodeURIComponent(pair.shift());
			value = pair.length < 1 ? null :
			    decodeURIComponent(pair.length > 1 ?
			    pair.join("=") : pair[0]);
			if (usefulJS.hOP.call(values, key)) {
				if (!_isArray(values[key]))
					values[key] = [values[key]];
				values[key].push(value);
			} else {
				keys.push(key);
				values[key] = value;
			}
		}
	    });
	var h2c = /%2C/ig;
	var genhash = function genhash() {
		var res = [], i, j, vals, key;
		for (i = 0; i < keys.length; ++i) {
			key = encodeURIComponent(keys[i]);
			vals = values[keys[i]];
			if (vals === null)
				res.push(key);
			else if (!_isArray(vals))
				res.push(key + "=" +
				    encodeURIComponent(vals));
			else for (j = 0; j < vals.length; ++j) {
				if (vals[j] === null)
					res.push(key);
				else
					res.push(key + "=" +
					    encodeURIComponent(vals[j]));
			}
		}
		return (res.join("&").replace(h2c, ","));
	    };
	var updhash = function updhash() {
		var newhash = genhash();
		if (!newhash.length)
			newhash = " ";
		if (newhash !== prevhash) {
			set_initiated = true;
			window.location.hash = newhash;
		}
	    };
	var hl_get = function hashlib_get(key) {
		key = String(key);
		return (usefulJS.hOP.call(values, key) ?
		    values[key] : undefined);
	    };
	var hl_set = function hashlib_set(key, value) {
		key = String(key);
		if (value === undefined) {
			keys = usefulJS.filter(keys, function unsetter(v) {
				return (v !== key);
			    });
			delete values[key];
			updhash();
			return;
		}
		if (!usefulJS.hOP.call(values, key))
			keys.push(key);
		if (value === null) {
			values[key] = null;
		} else if (!_isArray(value)) {
			values[key] = String(value);
		} else {
			var res = [], i;
			for (i = 0; i < value.length; ++i)
				if (usefulJS.hOP.call(value, i))
					res.push(value[i] === null ?
					    null : String(value[i]));
			values[key] = res;
		}
		updhash();
	    };
	var hl_keys = function hashlib_keys() {
		return (keys.slice(0).sort());
	    };
	var hl_clear = function hashlib_clear() {
		keys = [];
		values = {};
		updhash();
	    };
	var hl_initialise = function hl_initialise(hl) {
		initialised = true;
		if (typeof(window.onhashchange) !== "undefined" &&
		    (document.documentMode === undefined || document.documentMode > 7))
			window.onhashchange = checkhash;
		else
			window.setInterval(checkhash, 100);
		checkhash(); // will only call cbparse
		hl.get = hl_get;
		hl.set = hl_set;
		hl.keys = hl_keys;
		hl.clear = hl_clear;
	    };
	var hl = function hashlib(cb) {
		if (!initialised)
			hl_initialise(hl);
		if (typeof(cb) === "function")
			callbacks.push(cb);
	    };
	// ONLY for debugging!
	//hl.getValues = function hl_getv() { return (values); };
	return (hl);
    })();

/**
 * Easy XMLHttpRequest (“AJAX”). Callback is run upon completion,
 * whether success or failure, with the status code, data and the
 * request/response object. Doing JSON.parse(responseText) maybe.
 */
G.ezXHR = function ezXHR(cb, url, data, method, rt) {
	if (!method)
		method = data === undefined ? "GET" : "POST";
	var xhr = new XMLHttpRequest();
	var responseTextAvailable = rt === undefined ||
	    rt === "" || rt === "text";
	xhr.onreadystatechange = function ezXHR_event() {
		if (xhr.readyState === 4)
			cb(xhr.status, responseTextAvailable ?
			    xhr.responseText : undefined, xhr);
	    };
	xhr.open(method, url, true);
	if (rt !== undefined)
		xhr.responseType = rt;
	xhr.send(data);
	return (xhr);
    };

/* </_closure_usefulJS> */
})(typeof(exports) === "undefined" ? (this["usefulJS"] = {}) : exports);

/* canonical: <https://evolvis.org/plugins/scmgit/cgi-bin/gitweb.cgi?p=useful-scripts/useful-scripts.git;a=tree;f=js;hb=HEAD> */
