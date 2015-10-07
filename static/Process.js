define('Process', ['jquery'], function($){

function Process(command_path, pid){
	"use strict";
	this.pid = +pid;
	this.command_path = command_path;
	this.after_idx = 0;
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

return Process;
});
