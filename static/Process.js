define('Process', ['jquery'], function($){
"use strict";

function Process(commandPath, pid){
	this.pid = +pid;
	this.commandPath = commandPath;
	this.afterIdx = 0;
	this.output = "";
	this.termview = null;
}

Process.prototype.read = function(){
	return new Promise((resolve, reject) => {
		this._read().then(resolve(this.output));
	});
	this._read().then((latest_idx, output) => {
		if (latest_idx > this.afterIdx){

		}
	});
}

Process.prototype.send = function(command){
	//TODO implement
}

Process.prototype.start = function(){
	// TODO implement
}

Process.prototype.stop = function(){
	// TODO implement
}

Process.prototype.isalive = function(){
	// TODO implement
}


Process.prototype._read = function(){
	return new Promise((resolve, reject) => {
		var readUrl = '/api/processes/'+this.pid+'/'+this.afterIdx;
		$.get(readUrl).then((data) => {
			var idx = +data['after_idx'];
			if (idx > this.afterIdx){
				this.output = this.output + data['output'];
			}
			resolve(+data['after_idx'], data['output'], data['isalive']);
		});
	});
}

Process.prototype.set_active = function(termview){
	this.termview = termview;
	this.termview.pid = this.pid;
	function poll(){
		setTimeout(() => {
			// If some other Process object takes control of our terminal view,
			// halt polling.
			if (this.termview.pid !== this.pid){
				return;
			}
			this._read().then((idx) => {
				if (idx > this.afterIdx){
					this.termview.update(this.output);
				}
			});
			poll();
		}, 2000);
	}
}



return Process;
});
