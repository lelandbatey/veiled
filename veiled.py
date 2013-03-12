import pexpect
from Queue import Queue, Empty
from threading import Thread
from collections import deque
#from pprint import pprint
#from time import sleep
import os


class procControl(object):
    """ Wrapper for pexpect, providing useful methods for controlling terminal applications """
    def __init__(self, scriptName, procType = ""):
        super(procControl, self).__init__() # <-- I don't quite get this :/
        self.scriptName = scriptName

        # If we where passed an absoloute path to the file to run, then we set up self.cwd to be the directory which the script is inside.
        if "/" in self.scriptName:
            self.cwd = self.scriptName.split("/")[:-1]
            self.cwd = "/".join(self.cwd)
        else:
            self.cwd = os.getcwd()

        # Checking the script location, and handling appropriately:
            # This is assuming that the script name contains no other path info. If it doesn't have a path, then it's run from the current working directory, the same one that webControl.py is running from.
        if "/" not in self.scriptName:
            self.scriptName = "./"+self.scriptName


        self.isRunning = False
        
    def start(self):
        """Starts up the script as a pexpect object, then creating a thread to perpetualy read the output of the process running in pexpect and enqueueing it into our queue of output (self.outQueue). """

        self.cmdOut = ""

        # To properly set the cwd, it needs to be passed into spawn() with all the other variables

        self.process = pexpect.spawn(self.scriptName,[],10000000,2000,None,None,self.cwd) # These seemingly arbitrarty variables are the default variables for spawn(), and are included so that we can pass in the current working directory properly. Actually, the '10000000' is the timeout, which is redundantly set below as well.
        self.process.logfile = file("logOut.log",'w')

        #self.process.cwd = self.cwd
        print self.process.cwd
        self.process.timeout = 10000000 # This means that trying to read() from pexpect.spawn will block forever (technically ten million seconds, which is about 115 days or till there is more input). However, since we are using a separate thread that can afford to block forever, we don't care. In fact, we want it to block forever!

        #self.pauseQueue = Queue() # Used to tell the enqueue thread to pause for 0.5 seconds
        self.outQueue = Queue()

        self.newestOut = deque(maxlen=150) # A deque allows us to have a "tickertape" style interface that is composed only of the most recent output from the loop generator.
        
        self.procThread = Thread(target=self.enqueue_output, args=(self.process, self.outQueue))
        self.procThread.daemon = True # When the program dies, our thread dies as well.
        self.procThread.start()
        
        self.isRunning = True # Nice little flag to keep track of whether the program is running or not.

# Alright, this below little snippet of code is actually PURE GENIUS. Full disclosure, I did in no way write it.
#   Here's how it works:
#       It gives out.readline to iter() and asks for it to create an iterable.
#       Iter works by calling "out.readline" with no arguments. If what is returned is equal to the sentinal value, then it AUTOMATICALLY EXITS THE FOR LOOP AND CLOSES THE FILE, **silently!**
#       
#       What's so cool about this is that it lets us spin off a thread that can read this file at whatever speed it wants, and it just silently handles adding new stuff to the queue. If there is nothing in the file to read, it handles that gracefully as well. It's just a wonderfully designed, silent little perpetual reader!
    def enqueue_output(self, out, queue):
        #try:
        for line in iter(out.readline, b''):
            queue.put(line)
            self.newestOut.append(line)
            #print line
            #print "somethingNew "+line
        out.close()
        

    def getOut(self):
        """ Returns all new output from the process, if any. 

        Additionally, this advances the state of the self.cmdOut, updating it with the latest information."""
    # GetConsoleOut:
    #   Returns everything that the process has spit out to the command line since the last time you called getConsoleOut()
        
        toReturn = ""
        while True:
            try:
                line = self.outQueue.get_nowait()
            except Empty:
                break
            toReturn += line
        self.cmdOut += toReturn
        return toReturn

    def totalConsoleOut(self):
        """ Returns all the output of the console since the start() method was called, but does not include the latests output of the console that has not been called via getOut() """
        return self.cmdOut

    def recentOutput(self):
        """ Returns a string of the contents of the newestOut deque() object. Use this for getting the most recent stuff as output. """
        toReturn = ""

        for i in self.newestOut:
            toReturn+=i

        return toReturn

    def sendCommand(self, command):
        """ Sends the given string to the running process as if it was typed into the keyboard """
        #self.pauseQueue.put(True)
        #time.sleep(1)
        self.process.send(command)

    def killConsole(self):
        """ Kills the console (forcibly) """
        self.process.sendcontrol('c')
        self.process.close(True) # Calls close() with force set to true
        self.isRunning = False

class controlBoard(object):
    """ Meta-class for controlling multiple procControl objects"""
    def __init__(self):
        #super controlBoard, self).__init__() # <- I just don't know what that's for :/
        self.processGroup = {}

    def initController(self, proccesName, scriptName):
        """ Initializes a new procControl object with the given name and script, and stores it in the dictionary of procControl objects. """

        # Adds new dictionary entry with
        try: 
            if self.processGroup[processName]:
                return "a process with that name already exists"
        except:
            self.processGroup[proccesName] = procControl(scriptName)

    def sendProcessCommand(self, processName, command):
        """ Given the name of a process, it sends a command to it. """
         # processName and command are strings
        try:
            process = self.processGroup["processName"]
        except KeyError:
            print "Process doesn't exist!"
            return

        process.sendCommand(command)

##### ListProcess #####
# Returns a list of strings, with each string being one of the names of the processes being run.
# Returns ALL process names
    def listProcess(self):
        """Returns a list all the names of processes for the current instance of the controlBoard class"""

        j = []

        print self.processGroup.keys()

        for keys in self.processGroup.keys():
            j.append(keys)

        return j

    def getProcessInfo(self,processName):
        """ Returns a dictionary of the state of various attributes of the given procControl object. """

        infoDict = {}

        print processName
        print self.processGroup.keys()

        if processName in self.processGroup.keys():
            refProcess = self.processGroup[processName]
            infoDict["name"] = processName
            infoDict["cwd"] = refProcess.cwd
            infoDict["scriptName"] = refProcess.scriptName
            infoDict["running"] = refProcess.isRunning
        else:
            return False

        return infoDict

    def processStart(self, processName):
        """ If a given procControl class is not running, it starts it. If it's already running, then it returns a string "already running". 

        This also assumes that it's being passed a valid procControl name, since this would normally be accessed through the processOperator class which checks if the given name is valid already. """

        toReturn = ""

        refProcess = self.processGroup[processName]

        if refProcess.isRunning:
            toReturn = "process already running.\n"
            #print "process was already running; couldn't start"
        else:
            refProcess.start()
            toReturn = "process has been started.\n"
            #print "process has been started!"

        return toReturn


    def processOperator(self, processName, operation, command=""):
        """ Main method/wrapper for procControl

        Acts as a router for commands, sending the given command to the correct process.
        Please note: this very much may not be the right way to do this. However, it is a way that works."""
        toReturn = True

        print "processName: " + processName
        print "operation  : " + operation
        print "command    : " + command

        if processName in self.processGroup.keys():
            refProcess = self.processGroup[processName]
        else:
            toReturn = "no process of that name"

        if operation == "kill":
            refProcess.killConsole()

        elif operation == "start":
            toReturn = self.processStart(processName)
            #refProcess.start()

        elif operation == "sendcmd":
            refProcess.sendCommand(command+"\n")

        elif operation == "getOutput":
            toReturn = refProcess.recentOutput()

        elif operation == "updateOutput":
            refProcess.totalConsoleOut()
            
        elif operation == "status":
            toReturn = self.getProcessInfo(processName)
        else:
            toReturn = "no operation of that name"

        return toReturn
