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

        procReq = urllib2.urlopen(address+"/list")
        print procReq.geturl()

        self.remoteInfo["processes"] = json.loads(urllib2.urlopen(address+"/list").read()) # gets the list of all process names from the server and stores as vaulue of "processes"
        self.remoteInfo["procInfo"] = []

        #print self.remoteInfo

        for procName in self.remoteInfo["processes"]: # builds a 
            statUrl = address+"/status"
            reqData = json.dumps({"processName" : procName})
            statReq = urllib2.Request(statUrl, reqData, {'Content-Type': 'application/json'})
            
            statResponse = urllib2.urlopen(statReq)
            statResponse = statResponse.read()
            print statResponse
            self.remoteInfo["procInfo"].append( json.loads(statResponse) )

        #print self.remoteInfo
    def getOutput(self,processName):
        readAddress = self.address+"/read"
        reqData = json.dumps({"processName" : processName})
        statReq = urllib2.Request(readAddress, reqData, {'Content-Type': 'application/json'})
        
        statResponse = urllib2.urlopen(statReq)
        statResponse = statResponse.read()

        return statResponse

    def sendCmd(self,processName,command):
        pass

    def createProcess(self,processName,scriptPath):
        readAddress = self.address+"/createProcess"
        reqData = json.dumps({'processName':processName,"scriptPath":scriptPath})
        procReq = urllib2.Request(readAddress, reqData, {'Content-Type': 'application/json'})

        procResponse = urllib2.urlopen(procReq)
        procResponse = procResponse.read()

        reqData = json.dumps({'processName':processName})
        readAddress = self.address+"/start"
        procReq = urllib2.Request(readAddress, reqData, {'Content-Type': 'application/json'})

        procResponse = urllib2.urlopen(procReq)
        procResponse = procResponse.read()

        return procResponse


def main():
    testUrl = "http://23.22.206.63:5000"
    testClient = veiledClient(testUrl)
    pprint(testClient.remoteInfo)

    info = testClient.remoteInfo
    for proc in info["processes"]:
        print json.loads(testClient.getOutput(proc))

    pprint(testClient.createProcess("bash","/bin/bash"))






main()