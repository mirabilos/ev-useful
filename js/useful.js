/*-
 * Copyright © 2020, 2023
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

/**
 * Escape plaintext, such as from textarea.value, for HTML such as in
 * span.innerHTML: entities for amp, lt, gt and (numeric) the double,
 * but not⚠ single, quote; "<br />" for newlines.
 */
var text2html = (function _closure_text2html() {
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
 * Make a string XML/HTML/XHTML/tty-safe: for the BMP, substitute any
 * codepoint XML/HTML do not permit or that is any control character,
 * other than CRLF and Tab, with U+FFFD: most C0 controls and DEL and
 * all C1 controls; loose surrogates, U+FFFE‥U+FFFF (though not other
 * noncharacters). In astral planes U-00010000‥U-0010FFFF are passed.
 */
var xhtsafe = (function _closure_xhtsafe() {
	var re = /((?:[\t\n\r -~\xA0-\uD7FF\uE000-\uFFFD]|[\uD800-\uDBFF][\uDC00-\uDFFF])+)/;

	return (function xhtsafe(s) {
		var i, j, o = "";
		var g = String(s).split(re);

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
var deferDOM = (function _closure_deferDOM() {
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
 * Easy XMLHttpRequest (“AJAX”). Callback is run upon completion,
 * whether success or failure, with the status code, data and the
 * request/response object. Doing JSON.parse(responseText) maybe.
 */
function ezXHR(cb, url, data, method, rt) {
	if (!method)
		method = data === undefined ? "GET" : "POST";
	var xhr = new XMLHttpRequest();
	var responseTextAvailable = rt === undefined ||
	    rt === '' || rt === 'text';
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
}
