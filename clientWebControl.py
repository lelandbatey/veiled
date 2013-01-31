import urllib
import urllib2
import json

url = 'http://adrenl.in:5000/cmd/'
values = json.dumps({"cmd" : "changelevel ctf_2fort"})

#data = urllib.urlencode(values)
data = values
print data
req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
print req
response = urllib2.urlopen(req)
the_page = response.read()
print the_page