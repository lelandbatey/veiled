define('Termview', ['jquery', 'underscore', 'term'], ($, _, tty) => {
"use strict";

function Termview(div){
	console.log(Terminal);

	this._inputBuffer = "";

	this.term = new Terminal({
		cols: 100,
		rows: 30,
		screenKeys: false,
		geometry: [100, 30]
	});
	this.term.on('data', (data) => {
		this._inputBuffer += data;
	});
	this.term.open(document.body);

	this.pid = null;
	this.process = null;
}

Termview.prototype.update = function(contents){
	// TODO: implement update
	this.term.write(contents);
	console.log(contents);
	return;

	var esc_regex = /\[.*m/g;
	contents = contents.replace(esc_regex, '').toString();
	this.consoleDiv.text(contents);
};

Termview.prototype.inputBuffer = function(){
	var buf = this._inputBuffer;
	this._inputBuffer = "";
	return buf;
};

return Termview;
});
