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
        self.processes = {}
        # Done to allow tests to swap in mock classes for processes
        self.process_class = ProcessControl

    def new_process(self, command_path):
        """Create a new ProcessControl object with the given command_path."""
        process = self.process_class(command_path)
        pid = None
        while (pid == None) or (pid in self.processes.keys()):
            pid = random.randint(0, 50000)
        self.processes[pid] = process

    def shutdown_all(self):
        """Close all processes."""
        for pid in self.processes:
            self.processes[pid].stop()


