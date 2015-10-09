#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Eases control (start, stop, read, write) of a process."""

from __future__ import print_function
from collections import deque
from threading import Thread
from itertools import islice
from os.path import abspath
import pexpect
import json
import time
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
        self.read_queue = deque(maxlen=15000)
        self.read_thread = None
        self.process = None

    def start(self):
        """Launch the command specified as command_path, launch thread to read
        output of process."""
        if self.process != None:
            raise RuntimeError("Process already exists, cannot start.")
        self.process = pexpect.spawn(self.command_path, args=[], cwd=self.cwd,\
                                     timeout=10000000, maxread=2000)
        self.read_thread = Thread(target=self.enqueue_output)
        self.read_thread.daemon = True
        self.read_thread.start()

    def stop(self):
        """Stops the running process and read_thread, and deletes the
        underlying objects."""
        if not self.process:
            return
        self.process.close(True)
        del self.process
        self.process = None
        time.sleep(0.01)

        del self.read_thread
        self.read_thread = None
        self.read_queue.clear()

    def enqueue_output(self):
        """Perpetually reads output of process and places into the read_queue.
        Intended to be run in a separate thread."""
        read_id = long(0)
        def reader():
            return self.process.read(1)
        try:
            for line in iter(reader, b''):
                self.read_queue.append((read_id, line))
                read_id += 1
        except Exception:
            pass

    def read(self, after_idx=None):
        """Read from the process output buffer.

        If `after_idx` is not given, returns entire output buffer and the
        latest chunk_index. If after_idx is provided, returns all chunks
        that've come after `after_idx` as well as the latest chunk_index."""

        if not self.isalive() or not len(self.read_queue):
            return "", 0

        def join_chunks(chunks):
            """Joins 'chunks', the body of tuples written to the read_queue"""
            str_chunks = [c[1] for c in chunks]
            return "".join(str_chunks)
        first_id = self.read_queue[0][0]
        last_id = self.read_queue[-1][0]
        decklen = len(self.read_queue)
        print(after_idx)
        print(last_id)
        print(decklen)
        print()

        if after_idx == None:
            return join_chunks(islice(self.read_queue, decklen)), last_id

        if after_idx < first_id:
            return join_chunks(islice(self.read_queue, decklen)), last_id
        elif after_idx >= last_id:
            return '', last_id
        else:
            # Add one since `islice` is inclusive, not exclusive
            mid_id = after_idx - first_id + 1
            if mid_id == decklen:
                return '', last_id
            contents = join_chunks(islice(self.read_queue, mid_id, decklen))
            return contents, last_id

    def send(self, command):
        """Writes the given command to stdin of the process as if it where
        typed."""
        self.process.send(command)

    def isalive(self):
        """Check if the underlying process is alive."""
        isalive = False
        if self.process != None and self.process.isalive():
            isalive = True
        return isalive

    def __getstate__(self):
        """Simpler representation of ProcessControl"""
        ret_val = {'isalive': self.isalive(),
                   'command_path': self.command_path}
        ret_val['output'], ret_val['last_index'] = self.read()
        return ret_val
    def __setstate__(self, _):
        """Filler method."""
        return

    def __str__(self):
        """String representation of ProcessControl"""
        ret_val = self.__getstate__()
        ret_val = json.dumps(ret_val, sort_keys=True, indent=4,
                             separators=(',', ': '))
        return ret_val





