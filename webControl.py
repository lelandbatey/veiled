from flask import Flask, request, json
import pexpect
from Queue import Queue, Empty
from threading import Thread
from pprint import pprint
from time import sleep
import os

#from remoteControl import termWrap

app = Flask(__name__)


class procControl():
    """ Wrapper for pexpect, providing useful methods for controlling terminal applications """
    def __init__(self, scriptName, procType = ""):
        #super(procControl, self).__init__() # <-- I don't quite get this :/
        self.scriptName = scriptName
        self.isRunning = False
        
    def start(self):
        """Starts up the script as a pexpect object, then creating a thread to perpetualy read the output of the process running in pexpect and enqueueing it into our queue of output (self.outQueue). """

        self.cmdOut = ""

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


        self.process = pexpect.spawn("./"+self.scriptName)
        self.process.logfile = file("logOut.log",'w')

        self.process.cwd = self.cwd
        self.process.timeout = 10000000 # This means that trying to read() from pexpect.spawn will block forever (technically ten million seconds, which is about 115 days or till there is more input). However, since we are using a separate thread that can afford to block forever, we don't care. In fact, we want it to block forever!

        self.pauseQueue = Queue() # Used to tell the enqueue thread to pause for 0.5 seconds
        self.outQueue = Queue()
        
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
            #print "somethingNew "+line
        out.close()
        

    def getOut(self):
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

    def sendCommand(self, command):
        """ Sends the given string to the running process as if it was typed into the keyboard """
        self.pauseQueue.put(True)
        #time.sleep(1)
        self.process.send(command)

    def killConsole(self):
        """ Kills the console (forcibly) """
        self.process.sendcontrol('c')
        self.process.close(True) # Calls close() with force set to true
        self.isRunning = False

class controlBoard():
    """ Meta-class for controlling multiple procControl objects"""
    def __init__(self, arg):
        #super controlBoard, self).__init__() # <- I just don't know what that's for :/
        self.processGroup = {}

    def initController(self, proccesName, scriptName):

        # Adds new dictionary entry with
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
    def listProcess(self):
        return self.processGroup

    def getProcessInfo(self,processName):

        infoDict = {}

        if processName in self.processGroup.keys():
            refProcess = processGroup[processName]
            infoDict["name"] = processName
            infoDict["cwd"] = refProcess.cwd
            infoDict["scriptName"] = refProcess.scriptName
            infoDict["running"] = refProcess.isRunning
        else:
            return

        return infoDict

    def processOperator(self, processName, operation, command=""):
        """ Main method wrapper for procControl """
        if porcessName in self.processGroup.keys():
            refProcess = self.processGroup[processName]
        else:
            return False

        if operation = "kill":
            refProcess.killConsole()

        elif operation = "start":
            refProcess.start()

        elif operation = "sendcmd":
            refProcess.sendCommand(command)

        elif operation = "getOutput":
            refProcess.getOut()

        elif operation = "updateOutput":
            refProcess.totalConsoleOut()
        else:
            return False

        return True

    # def processStart(self, processName):

    #     if processName in self.processGroup.keys():
    #         refProcess = self.processGroup[processName]
    #         refProcess.start()
    #         return True
    #     else:
    #         return False

    # def processKill(self, processName):

    #     if processName in self.processGroup.keys():
    #         refProcess = self.processGroup[processName]
    #         refProcess.killConsole()
    #         return True
    #     else:
    #         return False


### Reads Configuration File ###
    # Configuration file is just a json file. The "key" must be "scriptPath" with the value being a string that is the path to the script (either absolute or relative to the instance of webControl)

configFile = open(config.json,'r')
configJson = json.loads(configFile.read())

scriptPath = configJson["scriptPath"]
print scriptPath


        
remoteBeta = procControl("run_tf2_comp_exitance.sh")
#remoteBeta.start()


bigBoard = controlBoard()
bigBoard.initController("testTf2Server", scriptPath)


@app.route('/')
def hello_world():
    return 'Hello World!\n'

@app.route('/kill/', methods = ['POST'])
def kill():
    toReturn = ""
    parsedContent = request.json

    if request.headers['Content-Type'] == 'application/json':
        if "name" in parsedContent.keys:
            
            processName = parsedContent["name"]
            if parsedContent["name"] in bigBoard.processGroup:
                
                if bigBoard.processOperator(processName,"kill") == True:
                    toReturn="process killed"
                


    remoteBeta.killConsole() # Calls close() with force set to true
    return "Killing script\n"

@app.route('/read')
def read():
    toReturn = remoteBeta.getOut()
    return toReturn    

@app.route('/start')
def start():
    toReturn = ""
    if remoteBeta.isRunning == False:
        toReturn = "Starting up the script\n"
        remoteBeta.start()
    elif remoteBeta.isRunning == True:
        toReturn = "Already running\n"

    return toReturn

@app.route('/status')
def status():
    toReturn = ''
    if remoteBeta.isRunning == False:
        toReturn = "Offline\n"
    elif remoteBeta.isRunning == True:
        toReturn = "Online\n"

    return toReturn

@app.route('/cmd/', methods = ['POST'])
def apiCmd():

    toReturn = ""
    if request.headers['Content-Type'] == 'application/json':
        print "JSON Message: " + json.dumps(request.json)
        toReturn = json.dumps(request.json)
        parsedCmd = json.loads(toReturn)['cmd']
        print parsedCmd# Prints the value cooresponding to the key "cmds"
    
    else:
        toReturn = "Error, input not JSON."
    
    
    #print request.form
    return toReturn#str(request.form)

@app.route("/console")
def console(): # Serves the console html page
    return render_template('testPollPage.html')


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
