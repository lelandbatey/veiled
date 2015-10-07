requirejs.config({
	baseUrl: 'static',
	paths: {
		jquery: '//ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery'
	}
});


require(['jquery', 'Process'], function($, Process){
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

instantiateProcesses().then((processList)=>{
	console.log(processList);
});

});
