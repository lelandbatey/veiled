import pexpect
from Queue import Queue, Empty
from threading import Thread


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