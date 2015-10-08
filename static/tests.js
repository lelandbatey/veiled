requirejs.config({
	baseUrl: '/static',
	paths: {
		jquery: '//ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery',
		underscore: '//cdnjs.cloudflare.com/ajax/libs/underscore.js/1.8.3/underscore',
		mockjax: 'lib/jquery.mockjax',
		qunit: '//code.jquery.com/qunit/qunit-1.19.0'
	}
});


require(['qunit', 'ProcessTests'], function(Qunit, ProcessTests){
"use strict";

function initialize(){
	Qunit.start();
}

$(initialize);

});
