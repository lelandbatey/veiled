#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for the process_control module."""

from __future__ import print_function
import process_control
import unittest
import os.path
import os

class MockProcess(object):
    """A mocked up version of a pexpect.spawn"""
    def __init__(self, mlist=[]):
        self.count = 0
        self.mlist = mlist
    def append(self, obj):
        """Fakes the append method"""
        self.mlist.append(obj)
    def close(self):
        """Fakes the close method"""
        return None
    def __call__(self):
        """Makes callable"""
        if self.count < len(self.mlist):
            rv = self.mlist[self.count]
            self.count += 1
            return rv
        else:
            return b''


class ProcControlTests(unittest.TestCase):
    """Tests for the process_control module."""

    def setUp(self):
        """Setup to be run for every test."""
        self.fname = 'test_script.sh'
        with open(self.fname, 'w') as tmp_file: 
            tmp_file.write('#!/bin/bash\necho "this is a test command"')
    
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

    def test_enqueue_output(self):
        """Ensure enqueue functions properly."""
        pro_co = process_control.ProcessControl(self.fname)
        mock_process = MockProcess(['zero', 'one', 'two'])
        mock_queue = []
        pro_co.process = mock_process
        pro_co.read_queue = mock_queue
        pro_co.enqueue_output()
        print(mock_queue)

if __name__ == '__main__':
	unittest.main()
