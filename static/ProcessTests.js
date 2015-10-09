define(['jquery', 'qunit', 'Process', 'mockjax'], ($, Qunit, Process, mockjax) => {
"use strict";

Qunit.test("Test Process constructor", (assert) => {
	var pid = 99999;
	var cmd = 'test_string';
	var proc = new Process(cmd, pid);
	assert.equal(proc.pid, pid);
	assert.equal(proc.commandPath, cmd);
	assert.equal(proc.lastIndex, 0);
	assert.equal(proc.output, "");
	assert.equal(proc.termview, null);
});

Qunit.test("Test Process `_read` method", (assert) => {
	var done1 = assert.async();

	var pid = 99;
	var cmd = 'test_string';
	var proc = new Process(cmd, pid);

	var response = {
		'last_index': 1,
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
		assert.equal(response.last_index, data.last_index);
		assert.equal(response.output, proc.output)
		assert.equal(response.last_index, proc.lastIndex)
		done1();
	});
});

Qunit.test("Test Process `read` method", (assert) => {
	var done1 = assert.async();

	var pid = 99;
	var cmd = 'test_string';
	var proc = new Process(cmd, pid);

	var response = {
		'last_index': 1,
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
		assert.equal(response.last_index, proc.lastIndex)
		done1();
	});
});

function testMethodRequest(cmd, matchData, mType, assert){
	var done1 = assert.async();

	var pid = 99;
	var cmd = 'test_string';
	var proc = new Process(cmd, pid);

	$.mockjax({
		url: '/api/processes/'+pid,
		type: mType,
		data: matchData,
		responseTime: 1,
		onAfterComplete: function(){
			// We're only checking that the request was made properly, so if we
			// get to here, they've been done correctly.
			assert.ok(true);
			done1();
		}
	});
	return proc;
	proc.send(cmd);
};


Qunit.test("Test Process `send` method", (assert) => {
	var cmd = 'test_string';
	var proc = testMethodRequest(cmd, 'command=test_string', 'POST', assert);
	proc.send(cmd);
});


Qunit.test("Test Process `stop` method", (assert) => {
	var cmd = 'test_string';
	var proc = testMethodRequest(cmd, 'action=stop', 'PUT', assert);
	proc.stop();
});


Qunit.test("Test Process `start` method", (assert) => {
	var cmd = 'test_string';
	var proc = testMethodRequest(cmd, 'action=start', 'PUT', assert);
	proc.start();
});


Qunit.test("Test Process `register_new_process` method", (assert) => {
	var done1 = assert.async();

	var pid = 99;
	var cmd = 'test_string';

	$.mockjax({
		url: '/api/processes',
		type: 'POST',
		data: 'command_path='+cmd,
		responseTime: 1,
		responseText: {'pid': pid, 'command_path': cmd}
	});
	Process.prototype.register_new_process(cmd).then((proc) => {
		assert.equal(proc.pid, pid);
		assert.equal(proc.commandPath, cmd);
		assert.equal(proc.lastIndex, 0);
		assert.equal(proc.output, "");
		assert.equal(proc.termview, null);
		done1();
	});


});



});
