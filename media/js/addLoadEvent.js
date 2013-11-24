// addLoadEvent function
// Originally written by Simon Willison (http://simon.incutio.com)
// Allows the attachment of multiple events to the window.onload event

function addLoadEvent(func) {
	var oldonload = window.onload;
	if (typeof window.onload != 'function') {
		window.onload = func;
	}	else {
		window.onload = function() {
			oldonload();
			func();
		}
	}
}
