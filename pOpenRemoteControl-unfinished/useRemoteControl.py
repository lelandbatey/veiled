import sys
from subprocess import PIPE, Popen
from threading import Thread
from Queue import Queue, Empty
from time import sleep

from remoteControl import termWrap

def main():
    cWraper = termWrap("perpetualScript.sh")

    cWraper.startThread()

    try:
        while True:
            i = cWraper.getOut()
            #i = cWraper.procCommunicate()

            if i: print i#, "cWraper consoleOut"
            sleep(2.5)
            #cWraper.sendInput("testing this thing!\n")
            sleep(2.5)
    except (KeyboardInterrupt, SystemExit):
        cWraper.killThread()

main()