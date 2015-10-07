#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A collection of ProcessControl objects."""

from __future__ import print_function
from process_control import ProcessControl
import jsonpickle
import random


class ProcessCollection(object):
    """Contains several ProcessControl objects, with methods for their
    maniplulation."""
    def __init__(self):
        self.processes = dict()
        # Done to allow tests to swap in mock classes for processes
        self.process_class = ProcessControl
        # Allows for swaping in more deterministic pid generators in tests
        self.pid_selector = lambda: random.randint(0, 50000)

    def new_process(self, command_path):
        """Create a new ProcessControl object with the given command_path."""
        process = self.process_class(command_path)
        pid = None
        while (pid == None) or (pid in self.processes.keys()):
            pid = self.pid_selector()
        self.processes[pid] = process

    def shutdown_all(self):
        """Close all processes."""
        for pid in self.processes:
            self.processes[pid].stop()

    def __getitem__(self, key):
        """Passthrough for dict-like access to self.processes"""
        return self.processes[key]

    def __setitem__(self, key, value):
        """Passthrough for dict-like assignment to self.processes"""
        self.processes[key] = value

    def __delitem__(self, key):
        """Special handling for deletion of self.process"""
        self.processes[key].stop()
        del self.processes[key]
    def __iter__(self):
        """Passthrough for dict-like iteration to self.processes"""
        for key in self.processes.keys():
            yield key
    def __getstate__(self):
        """Simpler representation of ProcessCollection"""
        ret_val = {key: self.processes[key].command_path for key in self.processes}
        return ret_val


