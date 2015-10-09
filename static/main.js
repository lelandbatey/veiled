requirejs.config({
	baseUrl: 'static',
	paths: {
		jquery: '//ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery',
		underscore: '//cdnjs.cloudflare.com/ajax/libs/underscore.js/1.8.3/underscore',
		term: 'lib/term'
	}
});


require(['jquery', 'Process', 'Termview'], function($, Process, Termview){
"use strict";

function instantiateProcesses(){
	var processes = new Promise((resolve, reject) => {
		$.get('/api/processes').done((data) => {
			var processList = [];
			console.log(data);
			for (var key in data){
				var process = new Process(data[key], key);
				processList.push(process);
			}
			resolve(processList);
		})
	});
	return processes;
};

var term = new Termview($('#container'));

instantiateProcesses().then((processList)=>{
	console.log(processList);
	function displayProcess(proc){
		proc.read().then((output) => {
			if (!proc.isalive()){
				proc.start();
			}
			processList.push(proc);
			proc.set_active(term);
		});
	}
	if (processList.length < 1){
		Process.prototype.register_new_process('/bin/bash').then(displayProcess);
	} else {
		displayProcess(processList[0]);
	}
});



});
