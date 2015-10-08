define(['jquery', 'qunit', 'Process', 'mockjax'], ($, Qunit, Process, mockjax) => {
"use strict";

Qunit.test("Test Process constructor", (assert) => {
	var pid = 99999;
	var cmd = 'test_string';
	var proc = new Process(cmd, pid);
	assert.equal(proc.pid, pid);
	assert.equal(proc.commandPath, cmd);
	assert.equal(proc.afterIdx, 0);
	assert.equal(proc.output, "");
	assert.equal(proc.termview, null);
});

Qunit.test("Test Process `_read` method", (assert) => {
	var done1 = assert.async();

	var pid = 99;
	var cmd = 'test_string';
	var proc = new Process(cmd, pid);

	var response = {
		'after_idx': 1,
		'output': 'zeroth\n',
		'isalive': true
	};
	$.mockjax({
		url: '/api/processes/'+pid+'/0',
		responseText: response,
		responseTime: 1
	});
	proc._read().then(function(data){
		console.log(response, data);
		assert.equal(response.isalive, data.isalive);
		assert.equal(response.output, data.output);
		assert.equal(response.after_idx, data.after_idx);
		assert.equal(response.output, proc.output)
		assert.equal(response.after_idx, proc.afterIdx)
		done1();
	});
});

Qunit.test("Test Process `read` method", (assert) => {
	var done1 = assert.async();

	var pid = 99;
	var cmd = 'test_string';
	var proc = new Process(cmd, pid);

	var response = {
		'after_idx': 1,
		'output': 'zeroth\n',
		'isalive': true
	};
	$.mockjax({
		url: '/api/processes/'+pid+'/0',
		responseText: response,
		responseTime: 1
	});
	proc.read().then(function(output){
		assert.equal(response.isalive, proc._isalive);
		assert.equal(response.output, proc.output);
		assert.equal(response.after_idx, proc.afterIdx)
		done1();
	});
});



});
