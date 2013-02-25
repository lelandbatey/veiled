import urllib
import urllib2
import json

# Really simple testing script of webControl.py

url = 'http://localhost:5000/list'
values = json.dumps({"name" : "testTf2Server"})

#data = urllib.urlencode(values)
data = values
print data
req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
print req
response = urllib2.urlopen(req)
the_page = response.read()
print the_page

class veiledClient():
    """docstring for veiledClient"""
    def __init__(self, address):
        #super(veiledClient, self).__init__() # Like I said, i do not get this at all :/
        self.address = address
        

def main():
    pass