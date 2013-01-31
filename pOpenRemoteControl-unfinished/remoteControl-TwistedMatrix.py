# I've had very limited success with threading and python. As a result, I am going to be experimenting with Twisted, a library that is supposed to allow me to do what I am trying to do.

# Found through this: http://stackoverflow.com/questions/4585692/python-nonblocking-subprocess-check-stdout


# For further experimentation, refer to the guid I was linked to:
#   http://twistedmatrix.com/documents/current/core/howto/process.html

from twisted.internet import reactor
from twisted.internet import protocol
from Queue import Queue, Empty # I'm going to use a queue to store the lines of text.


class WCProcessProtocol(protocol.ProcessProtocol):

    def __init__(self, text):
        self.text = text

    def connectionMade(self):
        self.transport.write(self.text)
        self.transport.closeStdin()
        # "Transport" is the connection to the process, and can be written to, closed, opened, etc.

    def outReceived(self, data):
        fieldLength = len(data) / 3
        lines = int(data[:fieldLength])
        words = int(data[fieldLength:fieldLength*2])
        chars = int(data[fieldLength*2:])
        self.transport.loseConnection()
        self.receiveCounts(lines, words, chars)

    def receiveCounts(self, lines, words, chars):
        print 'Received counts from wc.'
        print 'Lines:', lines
        print 'Words:', words
        print 'Characters:', chars

#wcProcess = WCProcessProtocol("accessing protocols through Twisted is fun!\n")
#reactor.spawnProcess(wcProcess, 'wc', ['wc'])
#reactor.run()

class PSProcessProtocol(protocol.ProcessProtocol):
    """PSProcessProtocol: takes no arguments. Simply runs till there's a keyboard interupt. """
    def __init__(self):
        self.queue = Queue() # Setting up a queue to store the output of the program in.
    
    def connectionMade(self):
        self.transport.closeStdin()

    def outReceived(self, data):
        print data , "data!"
        self.queue.put(data)

    def timeToEnd(self):
        self.transport.signalProcess("KILL")

# This is going to read from the process output, checking if there is no new output and counting till there is new output. Once there is new output it resets the counter, prints the output, and prints how many numbers it counted while there was no new output.
def main():

    perpetualScript = PSProcessProtocol()
    reactor.spawnProcess(perpetualScript, "perpetualScript.sh", ['perpetualScript.sh'])
    reactor.run()
    print "reactor finished running"
    i = 0

    try:
        while True:
            try: line = perpetualScript.queue.get_nowait()
            except Empty:
                i += 1 
            else: # There IS a new line!
                print line
                print "We waited", i
    except (KeyboardInterrupt, SystemExit):
        perpetualScript.timeToEnd()
        sys.exit()

main()

##############
# CONCLUSION #
##############
# I pretty much thought Twisted would solve all my problems and just auto-thread things for me.
# Despite my hopes, Twisted does NOT actually provide a drop dead way of doing things asynchronously. It turns out that Twisted provides a lot of methods of doing things in non-blocking ways, but that's pretty much not what I want. I am going to have to get used to threading. *shudder*
# This conclusion is gathered from my experience and from this :http://stackoverflow.com/questions/6117587/twisted-making-code-non-blocking