#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Eases control (start, stop, read, write) of a process."""

from __future__ import print_function
from collections import deque
from threading import Thread
from os.path import abspath
import pexpect
import os


class ProcessControl(object):
    """Eases controll of a process."""
    def __init__(self, command_path):
        self.command_path = abspath(command_path)

        # If we where passed an absoloute path to the file to run, then we set
        # up self.cwd to be the directory which the script is inside.
        if "/" in self.command_path:
            #self.cwd = self.command_path.split("/")[:-1]
            self.cwd = "/".join(self.command_path.split("/")[:-1])
        else:
            self.cwd = os.getcwd()
        self.read_queue = deque(maxlen=150)
        self.process = None

    def start(self):
        """Launch the command specified as command_path, launch thread to read
        output of process."""
        self.process = pexpect.spawn(self.command_path, args=[], cwd=self.cwd,
                                     timeout=10000000, maxread=2000)
        self.read_thread = Thread(self.enqueue_output)
        self.read_thread.daemon = True
        self.read_thread.start()

    def enqueue_output(self):
        """Perpetually reads output of process and places into the read_queue.
        Intended to be run in a separate thread."""
        read_id = long(0)
        for line in iter(self.process, b''):
            self.read_queue.append((read_id, line))
            read_id += 1
        self.process.close()




