from flask import Flask, request, json, render_template
import pexpect
from Queue import Queue, Empty
from threading import Thread
#from pprint import pprint
#from time import sleep
import os
from veiled import *


app = Flask(__name__)


### Reads Configuration File ###
    # Configuration file is just a json file. The "key" must be "scriptPath" with the value being a string that is the path to the script (either absolute or relative to the instance of webControl)

configFile = open('config.json','r')
configJson = json.loads(configFile.read())

scriptPath = configJson["scriptPath"]
print scriptPath


        
remoteBeta = procControl("run_tf2_comp_exitance.sh")
#remoteBeta.start()


bigBoard = controlBoard()
bigBoard.initController("testTf2Server", scriptPath)
bigBoard.processOperator("testTf2Server","start")

def genericRequestHandler(request,operation):
    """ Performs more generic handling of requests received at access points.

    Performs various error checks such as "did you specify a valid process name?" or "was the request of the correct type and format?"
    These checks are pretty heavy handed and not elegant, but they are necessary.
    These are designed so that if a developer where manually testing these requests (with say, curl), they'd actually receive useful error messaged. """
    toReturn=""
    parsedContent = request.json
    print request.data

    if request.headers['Content-Type'] == 'application/json':
        if "processName" in parsedContent.keys():
            
            processName = parsedContent["processName"]
            if processName in bigBoard.processGroup.keys():
                
                if operation == "sendcmd": # if we are sending a command we need to figure out what that command is now and include it
                    toReturn = bigBoard.processOperator(processName,operation,parsedContent["cmd"])
                else: # For everything else, we don't include the cmd parameter.
                    toReturn = bigBoard.processOperator(processName,operation)

                #print toReturn
                if not toReturn:
                    toReturn = "error in communicating command"

            else: # if no process exists with the given name
                toReturn = "no process exists with the given name"
        else: # if there wasn't a "name" key
            toReturn = "did not specify a value for 'name' in arguments"
    else: # If the content is not json
        toReturn = "request must be a POST request formatted as JSON"
        print request.headers['Content-Type']

    return toReturn


@app.route('/')
def hello_world():
    toReturn = []
    
    for rules in app.url_map.iter_rules():
        toReturn.append(rules)
    return str(toReturn)


@app.route('/kill/', methods = ['POST'])
def kill():
    # Handles killing the appropriate process.
    toReturn = ""
    parsedContent = request.json

    return genericRequestHandler(request,"kill")


    remoteBeta.killConsole() # Calls close() with force set to true
    return "Killing script\n"

@app.route('/read', methods = ['POST'])
def read():
    #toReturn = remoteBeta.getOut()
    toReturn = json.dumps(genericRequestHandler(request,"getOutput"))
    return toReturn    

# Checks to see if the given 
@app.route('/start')
def start():
    toReturn = genericRequestHandler(request,"start")
    return toReturn

    # if remoteBeta.isRunning == False:
    #     toReturn = "Starting up the script\n"
    #     remoteBeta.start()
    # elif remoteBeta.isRunning == True:
    #     toReturn = "Already running\n"

@app.route('/list')
def listProcs():
    return json.dumps(bigBoard.listProcess())


@app.route('/status', methods = ['POST'])
def status():
    
    toReturn = json.dumps(genericRequestHandler(request,"status"))
    print toReturn
    return toReturn


@app.route('/cmd/', methods = ['POST'])
def apiCmd():
    # Requires:
    # { "processName" : "theNameOfTheProcess",
    #   "cmd" : "theCommandToBeSentToTheProcess" }

    toReturn = ""


    if request.headers['Content-Type'] == 'application/json':
        
        parsedCmd = request.json['cmd']
        print "\n!! WE GOT A REQEUST:\n"+str(request.json)+"\n"
        returned = genericRequestHandler(request,"sendcmd")
        print returned
        if returned:
            toReturn="command communicated successfully"
    else:
        toReturn = "Error, input not JSON."
    
    
    #print request.form
    return toReturn#str(request.form)

@app.route("/testConsole")
def console(): # Serves the console html page
    return render_template('testPollPage.html')


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
