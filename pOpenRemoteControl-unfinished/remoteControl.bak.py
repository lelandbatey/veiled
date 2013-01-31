# My goal with this is to be able to read the input and output of a process in a non-blocking way.
# This will allow me to controll existing programs/scripts with Python.
# This is a big resource for me: http://stackoverflow.com/questions/375427/non-blocking-read-on-a-subprocess-pipe-in-python

# Notes about remoteControl.py

# Since I'm primarily taking this from a given source and I don't totally get all this, I'll write down notes and explanations as I need them, to help me better understand.

# Queue:
#     In computer science, a 'queue' is a specific kind of data structure. Things can be added to the "front" of the queue (an action know as an *enqueue*) and things can be removed from the "back" of the queue (an action called *dequeue*).

# !NOTICE!
# Things commented out with a double pound (##) are comments taken verbatim from the example

import sys
from subprocess import PIPE, Popen
from threading import Thread
from Queue import Queue, Empty
from time import sleep


# def enqueue_output(out, queue):
#     for line in iter(out.readline, b''):
#         queue.put(line)
#     out.close()

class consoleWrapper:
    """docstring for consoleWrapper"""
    
    def __init__(self, runscript):
        #super(consoleWrapper, self).__init__() # I don't know how this works :/
        self.runscript = "./"+runscript
        #print self.runscript
        
    def startScriptThread(self):
        self.process = Popen(self.runscript, stdin=PIPE, stdout=PIPE, bufsize=1)
        self.queue = Queue()
        
        self.thread = Thread(target=self.enqueue_output, args=(self.process.stdout, self.queue))
        self.thread.daemon = True # When the program dies, the thread also dies.
        self.thread.start()

    def enqueue_output(self, out, queue):
        #print out, "out"
        #print queue, "queue"
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()

    def getConsoleOut(self):
    # GetConsoleOut:
    #   Returns everything that the process has spit out to the command line since the last time you called getConsoleOut()
        
        toReturn = ""
        while True:
            try:
                line = self.queue.get_nowait()
            except Empty:
                break
            toReturn += line
        
        return toReturn

    def sendInput(self, text):
        #print text
        self.process.stdin.write(text)

    def killConsole(self):
        self.process.terminate() # Kills the sub-process running our stuff

def main():
    cWraper = consoleWrapper("perpetualScript.sh")

    cWraper.startScriptThread()



    try:
        while True:
            i = cWraper.getConsoleOut()
            #i = cWraper.procCommunicate()

            if i: print i#, "cWraper consoleOut"
            sleep(2.5)
            cWraper.sendInput("testing this thing!\n")
            sleep(2.5)
    except (KeyboardInterrupt, SystemExit):
        cWraper.killConsole()



    # p = Popen("./perpetualScript.sh",stdin=PIPE, stdout=PIPE, bufsize=1)
    # q = Queue()
    # t = Thread(target=enqueue_output, args=(p.stdout, q))
    # t.daemon = True ## the thread dies with the program
    # t.start()

    # i = 0

    # try:
    #     while True:
    #         ## Reads the line without blocking
    #         try: 
    #             line = q.get_nowait() ## or q.get(timeout=.1)
            
    #         except Empty:
    #             #print('no output yet')
    #             i += 1
    #         else: ## we DID get a line
    #             ## ... do something with line
    #             print line, "- We got output after:", i
    #             i = 0
    # except (KeyboardInterrupt, SystemExit):
    #     p.terminate() # THIS RIGHT HERE IS THE WINNING COMMAND!!!

main()