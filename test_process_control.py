#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for the process_control module."""

from __future__ import print_function
import process_control
import unittest
import os.path
import time
import os

class MockProcess(object):
    """A mocked up version of a pexpect.spawn"""
    def __init__(self, mlist):
        self.count = 0
        self.mlist = mlist
        self.commands = []
    def append(self, obj):
        """Fakes the append method"""
        self.mlist.append(obj)
    def close(self):
        """Fakes the close method"""
        self = self
        return None
    def readline(self):
        """Fake readline method"""
        if self.count < len(self.mlist):
            ret_val = self.mlist[self.count]
            self.count += 1
            return ret_val
        else:
            return b''
    def send(self, command):
        """Fakes the `send` method"""
        self.commands.append(command)


class ProcControlTests(unittest.TestCase):
    """Tests for the process_control module."""

    def setUp(self):
        """Setup to be run for every test."""
        self.fname = 'test_script.sh'
        with open(self.fname, 'w') as tmp_file:
            tmp_file.write('''#!/bin/bash
for x in $(seq 0 200); do echo "$x"; done;''')
        os.chmod(self.fname, 0755)

    def tearDown(self):
        """Cleanup after each test."""
        os.remove(self.fname)

    def test_init(self):
        """Ensure initial variables are set properly."""
        pro_co = process_control.ProcessControl(self.fname)
        self.assertEqual(pro_co.command_path, os.path.abspath(self.fname))
        self.assertEqual(pro_co.cwd, os.getcwd())
        self.assertEqual(pro_co.read_queue, process_control.deque(maxlen=150))
        self.assertEqual(pro_co.process, None)

    def test_start(self):
        """Test for correct process start."""
        pro_co = process_control.ProcessControl(self.fname)
        pro_co.start()
        self.assertTrue(isinstance(pro_co.process,
                                   process_control.pexpect.spawn))
        self.assertTrue(isinstance(pro_co.read_thread, process_control.Thread))

    def test_stop(self):
        """Test for correct process stop."""
        pro_co = process_control.ProcessControl(self.fname)
        pro_co.start()
        pro_co.stop()
        self.assertTrue(pro_co.process == None)
        self.assertTrue(pro_co.read_thread == None)
        self.assertTrue(len(pro_co.read_queue) == 0)

    def test_enqueue_output(self):
        """Ensure enqueue writes proper tuple for read in results."""
        pro_co = process_control.ProcessControl(self.fname)
        s_list = ['zero', 'one', 'two']
        mock_process = MockProcess(s_list)
        mock_queue = []

        pro_co.process = mock_process
        pro_co.read_queue = mock_queue
        pro_co.enqueue_output()

        for idx, val, in enumerate(s_list):
            result_idx, result_val = mock_queue[idx]
            self.assertEqual(result_idx, idx)
            self.assertEqual(result_val, val)

    def test_read(self):
        """Test reading from process at different positions"""
        pro_co = process_control.ProcessControl(self.fname)
        pro_co.start()
        time.sleep(0.01)
        call_vals = ((None, 701, 200),
                     (200,  0,   200),
                     (195,  30,  200))

        for call in call_vals:
            in_val, good_len, good_idx = call
            ret_len, ret_idx = pro_co.read(after_idx=in_val)
            ret_len = len(ret_len)
            self.assertEqual(good_len, ret_len)
            self.assertEqual(good_idx, ret_idx)

    def test_send(self):
        """Test sending a command to a process."""
        pro_co = process_control.ProcessControl(self.fname)
        s_list = ['zero', 'one', 'two']
        mock_process = MockProcess(s_list)
        pro_co.process = mock_process

        pro_co.send('test command')

        self.assertEqual(['test command'], mock_process.commands)


if __name__ == '__main__':
    unittest.main()
