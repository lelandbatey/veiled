import urllib
import urllib2
import json
from pprint import pprint

# # Really simple testing script of webControl.py

# url = 'http://localhost:5000/list'
# values = json.dumps({"name" : "testTf2Server"})

# #data = urllib.urlencode(values)
# data = values
# print data
# req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
# print req
# response = urllib2.urlopen(req)
# the_page = response.read()
# print the_page

class veiledClient(object):
    """docstring for veiledClient"""
    def __init__(self, address):
        super(veiledClient, self).__init__() # Like I said, i do not get this at all :/
        self.address = address
        self.remoteInfo = {}

        # Here we're defining some nice constants that refer to the various URL's
        # that get referenced frequently. I put these here so that I can quickly
        # and easily change them later if need be.
        self.createUrl = "/createProcess"
        self.listUrl = "/list"
        self.readUrl = "/read"
        self.startUrl = "/start"
        self.statusUrl = "/status"
        self.cmdUrl = "/cmd/"


        procReq = urllib2.urlopen(address+"/list")
        print procReq.geturl()

        self.remoteInfo["processes"] = json.loads(urllib2.urlopen(address+"/list").read()) # gets the list of all process names from the server and stores as vaulue of "processes"
        self.remoteInfo["procInfo"] = []

        #print self.remoteInfo

        for procName in self.remoteInfo["processes"]: # builds a nice dictionary of process information.

            statusResponse = self.postMesg(self.statusUrl,{"processName" : procName})

            print statusResponse
            self.remoteInfo["procInfo"].append( json.loads(statusResponse) )

    def postMesg(self,url,data):
        """ A generic method for posting data to the given url. \
        Meant to make other methods shorter and easier to read. """
        readAddress = self.address+url
        reqData = json.dumps(data)
        procReq = urllib2.Request(readAddress, reqData, {'Content-Type': 'application/json'})

        procResponse = urllib2.urlopen(procReq)
        procResponse = procResponse.read()

        return procResponse

    def getOutput(self,processName):
        # readAddress = self.address+"/read"
        # reqData = json.dumps({"processName" : processName})
        # statReq = urllib2.Request(readAddress, reqData, {'Content-Type': 'application/json'})
        
        # statResponse = urllib2.urlopen(statReq)
        # statResponse = statResponse.read()

        #data = 
        #print type(data)

        toReturn = self.postMesg('/read', {"processName" : processName})

        return toReturn

    def sendCmd(self,processName,command):
        
        toReturn = self.postMesg(self.cmdUrl, {"processName": processName, "cmd":command })

        return toReturn

    def createProcess(self,processName,scriptPath):
        # readAddress = self.address+"/createProcess"
        # reqData = json.dumps({'processName':processName,"scriptPath":scriptPath})
        # procReq = urllib2.Request(readAddress, reqData, {'Content-Type': 'application/json'})

        # procResponse = urllib2.urlopen(procReq)
        # procResponse = procResponse.read()

        toReturn = self.postMesg(self.createProcess,{'processName':processName,"scriptPath":scriptPath})
        
        # reqData = json.dumps({'processName':processName})
        # readAddress = self.address+"/start"
        # procReq = urllib2.Request(readAddress, reqData, {'Content-Type': 'application/json'})

        # procResponse = urllib2.urlopen(procReq)
        # procResponse = procResponse.read()

        toReturn = self.postMesg(self.startUrl,{'processName':processName})

        return toReturn
    def startProcess(self, processName):
        toReturn = self.postMesg(self.startUrl, {"processName": processName})
        return toReturn

def main():
    testUrl = "http://192.168.1.175:5000"
    testClient = veiledClient(testUrl)
    pprint(testClient.remoteInfo)

    info = testClient.remoteInfo
    for proc in info["processes"]:
        print json.loads(testClient.getOutput(proc))

    pprint(testClient.startProcess("exampleBash"))
    #pprint(testClient.createProcess("bash","/bin/bash"))
    #testClient.sendCmd


def readTest():
    testUrl = "http://192.168.1.175:5000"
    testClient = veiledClient(testUrl)

    print testClient.getOutput('exampleBash')
main()
readTest()