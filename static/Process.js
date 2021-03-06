define('Process', ['jquery'], function($){
"use strict";

function Process(commandPath, pid){
	this.pid = +pid;
	this.commandPath = commandPath;
	this.lastIndex = 0;
	this.updateIndex = 0;
	this._isalive = false;
	this.output = "";
	this.termview = null;
}

Process.prototype.read = function(){
	// Refresh this processes output, resolve with the entire newly reflected output.
	return new Promise((resolve, reject) => {
		this._read().then(() => resolve(this.output));
	});
};

Process.prototype.send = function(command){
	// Sends a given command to the server, return nothing
	var sendUrl = '/api/processes/'+this.pid;
	$.ajax({
		method: "POST",
		url: sendUrl,
		data: "command="+command
	});
};

Process.prototype.start = function(){
	var startUrl = '/api/processes/'+this.pid;
	$.ajax({
		method: "PUT",
		url: startUrl,
		data: "action=start"
	});
};

Process.prototype.stop = function(){
	var stopUrl = '/api/processes/'+this.pid;
	$.ajax({
		method: "PUT",
		url: stopUrl,
		data: "action=stop"
	});
};

Process.prototype.isalive = function(){
	return this._isalive;
};

/**
 * Reads the latest output of the process from the server, updating the
 * client-side cached 'output'.
 * @returns A resolving promise returns `after_idx`, `output`, and `isalive`. `output` is as returned from the server, which will probably only be the latest additions to the total output.
 */
Process.prototype._read = function(){
	var _this = this;
	return new Promise((resolve, reject) => {
		var readUrl = '/api/processes/'+_this.pid+'/'+_this.lastIndex;
		$.get(readUrl).then((data) => {
			var idx = +data['last_index'];
			_this._isalive = data['isalive']
			if (idx > _this.lastIndex){
				_this.output = _this.output + data['output'];
				_this.lastIndex = idx;
			}
			resolve(data);
		});
	});
};

Process.prototype.set_active = function(termview){
	this.termview = termview;
	this.termview.pid = this.pid;
	this.termview.process = this;
	var _this1 = this;
	function poll(){
		setTimeout(() => {
			// If some other Process object takes control of our terminal view,
			// halt polling.
			if (_this1.termview.pid !== _this1.pid){
				return;
			}
			_this1._read().then((data) => {
				if (data['last_index'] > _this1.updateIndex){
					_this1.termview.update(data['output']);
					_this1.updateIndex = data['last_index'];
				}
			});
			_this1.send(_this1.termview.inputBuffer());
			poll();
		}, 100);
	}
	poll();
};

Process.prototype.register_new_process = function(commandPath){
	// Create a new process on the server
	return new Promise((resolve, reject) => {
		var newUrl = '/api/processes';
		$.ajax({
			url: newUrl,
			method: 'POST',
			data: 'command_path='+commandPath
		}).then((data) => {
			resolve(new Process(data['command_path'], +data['pid']));
		});
	});
}


return Process;
});
