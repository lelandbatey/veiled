import pexpect
from Queue import Queue, Empty
from threading import Thread
from collections import deque
import os


class ProcessControl(object):
    """Wrapper for pexpect, providing useful methods for controlling terminal
    applications"""
    def __init__(self, script_name):
        self.script_name = script_name

        # If we where passed an absoloute path to the file to run, then we set
        # up self.cwd to be the directory which the script is inside.
        if "/" in self.script_name:
            self.cwd = self.script_name.split("/")[:-1]
            self.cwd = "/".join(self.cwd)
        else:
            self.cwd = os.getcwd()
            # In this case, it's a bare program name
            self.script_name = "./"+self.script_name

        self.is_running = False

    def start(self):
        """Starts up the script as a pexpect object, then creating a thread to
        perpetualy read the output of the process running in pexpect and
        enqueueing it into our queue of output (self.outQueue). """

        self.cmd_output = ""

        self.process = pexpect.spawn(self.script_name, args=[], cwd=self.cwd,
                                     timeout=10000000, maxread=2000)
        self.process.logfile = file("logOut.log", 'w')

        print "!! start() !!\n\t"+self.process.cwd

        self.outQueue = Queue()

        # A deque allows us to have a "tickertape" style interface that is
        # composed only of the most recent output from the loop generator.
        self.newestOut = deque(maxlen=150)

        self.process_thread = Thread(target=self.enqueue_output,
                                 args=(self.process, self.outQueue))
        # When the program dies, our thread dies as well.
        self.process_thread.daemon = True
        self.process_thread.start()

        # Nice little flag to keep track of whether the program is running or
        # not.
        self.is_running = True

# Alright, this below little snippet of code is actually PURE GENIUS. Full
# disclosure, I did in no way write it. This is where it originates :
#    http://stackoverflow.com/a/4896288
#
#     Here's how it works:
#         It gives out.readline to iter() and asks for it to create an
#         iterable.
#
#         Iter works by calling "out.readline" with no arguments. If what is
#         returned is equal to the sentinal value, then it AUTOMATICALLY EXITS
#         THE FOR LOOP AND CLOSES THE FILE, **silently!**
#
#         What's so cool about this is that it lets us spin off a thread that
#         can read this file at whatever speed it wants, and it just silently
#         handles adding new stuff to the queue. If there is nothing in the
#         file to read, it handles that gracefully as well. It's just a
#         wonderfully designed, silent little perpetual reader!
    def enqueue_output(self, out, queue):
        #try:
        for line in iter(out.readline, b''):
            # queue.put(line)
            self.newestOut.append(line)

        out.close()

    def getOut(self):
        """ Returns all new output from the process, if any.

        Additionally, this advances the state of the self.cmd_output, updating it
        with the latest information."""

        # Returns everything that the process has spit out to the command line
        # since the last time you called getConsoleOut()

        ret_val = ""
        while True:
            try:
                line = self.outQueue.get_nowait()
            except Empty:
                break
            ret_val += line
        self.cmd_output += ret_val
        return ret_val

    def totalConsoleOut(self):
        """ Returns all the output of the console since the start() method was
        called, but does not include the latests output of the console that has
        not been called via getOut() """
        return self.cmd_output

    def recentOutput(self):
        """ Returns a string of the contents of the newestOut deque() object.
        Use this for getting the most recent stuff as output. """
        ret_val = ""
        for i in self.newestOut:
            ret_val += i
        return ret_val

    def sendCommand(self, command):
        """ Sends the given string to the running process as if it was typed
        into the keyboard """

        self.process.send(command)

    def killConsole(self):
        """ Kills the console (forcibly) """
        self.process.sendcontrol('c')
        self.process.close(True) # Calls close() with 'force' set to true
        self.is_running = False

    def isAlive(self):
        """ Passthrough for pexpect isalive() method. """
        try:
            ret_val = self.process.isalive()
        except AttributeError:
            ret_val = False
        # Why the try/except?
        # Well, until the start() method is run on a given ProcessControl object,
        # there isn't actually a process object associated with a given
        # ProcessControl object. It used to be that the "is_running" variable would
        # just be set to False and wouldn't ever touch the process object (at
        # least till it was started, in which case it'd be switched to True).
        # However, the is_running variable only kept track of what the mode that
        # had been set on the process, not the processes actuall status. Thus,
        # the program running inside the process might have crashed while
        # running, but the is_running variable would still be marked as "True".
        # By accessing the more 'native' method, we're able to know a lot more!

        return ret_val

class controlBoard(object):
    """ Meta-class for controlling multiple ProcessControl objects.

    Named after the large audio mixers seen at concerts, allowing you to
    control and adjust all sorts of different devices from one huge, cool
    looking place."""

    def __init__(self):
        self.processGroup = {}

    def initController(self, proccesName, script_name):
        """ Initializes a new ProcessControl object with the given name and script,
         and stores it in the dictionary of ProcessControl objects. """

        # Adds new dictionary entry with the processName as the key
        try:
            if self.processGroup[processName]:
                return "a process with that name already exists"
        except: # if no process with the given name exists, then:
            self.processGroup[proccesName] = ProcessControl(script_name)
            # Creates a new entry in the dictionary which keeps track of our
            # processes
            # with the 'key' being the given name of the process and the value
            # being the ProcessControl object.

        return "process controler successfully created"

    def sendProcessCommand(self, processName, command):
        """ Given the name of a process, it sends a command to it. """
         # processName and command are strings
        try:
            process = self.processGroup["processName"]
        except KeyError:
            print " == sendProcessCommand ==\n\tProcess doesn't exist!"
            return

        process.sendCommand(command)

    def listProcess(self):
        """Returns a list all the names of processes for the current instance
        of the controlBoard class"""

        j = []

        print " == listProcess() ==\n\t"+str(self.processGroup.keys())

        for keys in self.processGroup.keys():
            j.append(keys)

        return j

    def getProcessInfo(self, processName):
        """ Returns a dictionary of the state of various attributes of the
        given ProcessControl object. """

        infoDict = {}

        print " == getProcessInfo() ==\n\t"+processName
        print "\t processGroup.keys():"+str(self.processGroup.keys())

        if processName in self.processGroup.keys():
            refProcess = self.processGroup[processName]
            infoDict["name"] = processName
            infoDict["cwd"] = refProcess.cwd
            infoDict["script_name"] = refProcess.script_name
            infoDict["running"] = refProcess.isAlive()
        else:
            return False

        return infoDict

    def processStart(self, processName):
        """ If a given ProcessControl class is not running, it starts it. If it's
        already running, then it returns a string "already running".

        This also assumes that it's being passed a valid ProcessControl name,
        since this would normally be accessed through the processOperator
         class which checks if the given name is valid already. """

        ret_val = 'an error of some type occured while starting the proccess'

        refProcess = self.processGroup[processName]

        if refProcess.is_running:
            ret_val = "process already running.\n"
        else:
            refProcess.start()
            ret_val = "process has been started.\n"

        return ret_val


    def processOperator(self, processName, operation, command=""):
        """ Main method/wrapper for ProcessControl

        Acts as a router for commands, sending the given command to the correct
        process.

        Please note: this very much may not be the right way to do this.
        However, it is a way that works."""
        ret_val = True

        print " == processOperator =="
        print "  processName: " + processName
        print "  operation  : " + operation
        print "  command    : " + command

        if processName in self.processGroup.keys():
            refProcess = self.processGroup[processName]
        else:
            ret_val = "no process of that name"

        if operation == "kill":
            refProcess.killConsole()

        elif operation == "start":
            ret_val = self.processStart(processName)
            #refProcess.start()

        elif operation == "sendcmd":
            refProcess.sendCommand(command+"\n")

        elif operation == "getOutput":
            if refProcess.is_running:
                ret_val = refProcess.recentOutput()
            else:
                ret_val = "process not running"
            if not ret_val:
                ret_val = "Process has not output anything yet.\n"
                ret_val += "Try sending a command of some kind."

        elif operation == "updateOutput":
            refProcess.totalConsoleOut()

        elif operation == "status":
            ret_val = self.getProcessInfo(processName)

        elif operation == "createProcess":
            ret_val = self.initController(processName, command)

        else:
            ret_val = "no operation of that name"

        return ret_val
