from flask import Flask, request, json
import pexpect
from Queue import Queue, Empty
from threading import Thread
from pprint import pprint
from time import sleep

#from remoteControl import termWrap

app = Flask(__name__)

# infiniScript = pexpect.spawn('./perpetualScript.sh')


# def enqueue_output(out, queue):
#     for line in iter(out.readline, b''):
#         queue.put(line)
#         #print line+"newLine"
#     out.close()



# q = Queue()
# t = Thread(target=enqueue_output, args=(infiniScript, q))
# t.daemon = True ## the thread dies with the program
# t.start()


class procControl():
    """docstring for procControl"""
    def __init__(self, scriptName):
        #super(procControl, self).__init__() # <-- I don't quite get this :/
        self.scriptName = scriptName
        self.isRunning = False
        
    def start(self):
        """Starts up the script as a pexpect object, then creating a thread to perpetualy read the output of the process running in pexpect and enqueueing it into our queue of output (self.outQueue). """

        self.process = pexpect.spawn("./"+self.scriptName)
        self.process.logfile = file("logOut.log",'w')
        self.process.timeout = 10000000 # This means that trying to read() from pexpect.spawn will block forever (technically ten million seconds, which is about 115 days or till there is more input). However, since we are using a separate thread that can afford to block forever, we don't care. In fact, we want it to block forever!

        self.pauseQueue = Queue() # Used to tell the enqueue thread to pause for 0.5 seconds
        self.outQueue = Queue()
        
        self.procThread = Thread(target=self.enqueue_output, args=(self.process, self.outQueue))
        self.procThread.daemon = True # When the program dies, our thread dies as well.
        self.procThread.start()
        
        self.isRunning = True # Nice little flag to keep track of whether the program is running or not.


# Alright, this below little snippet of code is actually PURE GENIUS. Full disclosure, I did in no way write it.
#   Here's how it works:
#       It gives out.readline to iter and asks for it to create an iterable.
#       Iter works by calling "out.readline" with no arguments. If what is returned is equal to the sentinal value, then it AUTOMATICALLY EXITS THE FOR LOOP AND CLOSES THE FILE, **silently!**
#       
#       What's so cool about this is that it lets us spin off a thread that can read this file at whatever speed it wants, and it just silently handles adding new stuff to the queue. If there is nothing in the file to read, it handles that gracefully as well. It's just a wonderfully designed, silent little perpetual reader!
    def enqueue_output(self, out, queue):
        #try:
        for line in iter(out.readline, b''):
            queue.put(line)
            #print "somethingNew "+line
        out.close()
        #except:
        #    print "!!!broken !!!"

        # pauseFlag = False
        
        # # Check the pauseQueue for any message that says to pause. This avoids trying to read at the same time we're trying to send a command (which breaks HORRIBLY) 
        # try:
        #     if self.pauseQueue.get_nowait():
        #         pauseFlag = True
        #     else:
        #         pauseFlag = False
        # except Empty:
        #     pass
        # try:
        #     if not pauseFlag:
        #         for line in iter(out.readline, b''):
        #             queue.put(line)
        #             #print line+"newLine"
        #         out.close()
        #     elif pauseFlag:
        #         time.sleep(1)
        # except:
        #     pass

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
        return toReturn

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


remoteBeta = procControl("run_tf2_comp_exitance.sh")
#remoteBeta.start()

@app.route('/')
def hello_world():
    return 'Hello World!\n'

@app.route('/kill')
def kill():
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


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
