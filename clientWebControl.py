import urllib
import urllib2
import json

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



def main():
    testUrl = "http://192.168.2.150:5000"
    testClient = veiledClient(testUrl)
    print testClient.remoteInfo

main()