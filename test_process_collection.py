#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for the process_collection module."""

from __future__ import print_function
import process_collection
import unittest

class MockProcControl(object):
    """Mock class of ProcessControl."""
    def __init__(self, command_path):
        self.command_path = command_path
        self._isalive = None
    def stop(self):
        """Fakes the stop method"""
        self._isalive = False
    def isalive(self):
        """Returns underlying self.isalive"""
        return self._isalive

def auto_increment_factory(_x_=None):
    """Closure which returns a function which returns a number that increments
    up each time it is called."""
    if _x_ == None:
        _x_ = [0]
    def f():
        rv = _x_[0]
        _x_[0] += 1
        return rv
    return f

class ProcCollectionTests(unittest.TestCase):
    """Tests for the process_collection module."""
    def setUp(self):
        """Setup to be run for each test."""
        return

    def test_init(self):
        """Test proper initialization"""
        pro_col = process_collection.ProcessCollection()
        self.assertEqual(pro_col.processes, dict())
        self.assertEqual(pro_col.process_class, process_collection.ProcessControl)

    def test_new_process(self):
        """Test that new processes are correctly created."""
        pro_col = process_collection.ProcessCollection()
        pro_col.process_class = MockProcControl
        test_path = 'test_path'
        pro_col.pid_selector = lambda: 1
        pro_col.new_process(test_path)

        self.assertTrue([1] == pro_col.processes.keys())
        self.assertEqual(pro_col[1].command_path, test_path)

    def test_shutdown_all(self):
        """Test of shutdown of all processes."""
        pro_col = process_collection.ProcessCollection()
        test_path = 'test_path'
        pro_col.pid_selector = auto_increment_factory()

        for _ in range(10):
            pro_col.new_process(test_path)
        self.assertEqual(sorted(pro_col.processes.keys()), [x for x in range(10)])
        for pid in pro_col.processes:
            self.assertEqual(pro_col[pid].isalive(), False)

    def test_delete(self):
        """Test that deletion of process causes stoppage."""
        pro_col = process_collection.ProcessCollection()
        pro_col.process_class = MockProcControl
        pro_col.pid_selector = auto_increment_factory()

        test_path = 'test_path'
        pro_col.new_process(test_path)
        proc = pro_col[0]
        del pro_col[0]

        self.assertEqual(proc.isalive(), False)

    def test_iter(self):
        """Test that iteration is properly implemented."""
        pro_col = process_collection.ProcessCollection()
        pro_col.process_class = MockProcControl
        pro_col.pid_selector = auto_increment_factory()

        test_path = 'test_path'
        for _ in range(10):
            pro_col.new_process(test_path)

        self.assertEqual(sorted([x for x in pro_col]), sorted([y for y in pro_col.processes]))


if __name__ == '__main__':
    unittest.main()
