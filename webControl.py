from flask import Flask, request, json, render_template
from flask.ext.basicauth import BasicAuth
import pexpect
from Queue import Queue, Empty
from threading import Thread
#from pprint import pprint
#from time import sleep
import os
from veiled import *

# In this feild, have the 
configuration_file = "config.json"


app = Flask(__name__)
### Reads Configuration File ###
    # Configuration file is just a json file. The "key" must be "scriptPath" with the value being a string that is the path to the script (either absolute or relative to the instance of webControl)

# configFile = open('config.json','r')
# configJson = json.loads(configFile.read())


bigBoard = controlBoard()

def loadConfig(configFile = "config.json"):
    configFile = open(configFile,"r")
    configJson = json.loads(configFile.read())

    for stuff in configJson[0]:
        bigBoard.initController(stuff["name"],stuff["scriptPath"])
        #print stuff
        if stuff["autoStart"]:
            bigBoard.processOperator(stuff["name"],"start")

    app.config['BASIC_AUTH_USERNAME'] = configJson[1]["username"]
    app.config['BASIC_AUTH_PASSWORD'] = configJson[1]["password"]

basic_auth = BasicAuth(app)
    

loadConfig(configuration_file)


#remoteBeta = procControl("run_tf2_comp_exitance.sh")
#remoteBeta.start()


# bigBoard = controlBoard()
# bigBoard.initController("testTf2Server", scriptPath)
# bigBoard.processOperator("testTf2Server","start")

def genericRequestHandler(request,operation):
    """ Performs more generic handling of requests received at access points.

    Performs various error checks such as "did you specify a valid process name?" or "was the request of the correct type and format?"
    These checks are pretty heavy handed and not elegant, but they are necessary.
    These are designed so that if a developer where manually testing these requests (with say, curl), they'd actually receive useful error messaged. """
    toReturn=""
    parsedContent = request.json
    print " @@ genericRequestHandler() @@\n\t"+str(request.data)

    if 'application/json' in request.headers['Content-Type']: # Firefox automatically appends some extra stuff onto the "Content-Type" header, even when TOLD NOT TO so you can't check for equality, only existance. Not a huge deal but a PAIN to track down.
        if "processName" in parsedContent.keys():
            
            processName = parsedContent["processName"]
            if processName in bigBoard.processGroup.keys() or operation == "createProcess":
                
                if operation == "sendcmd": # if we are sending a command we need to figure out what that command is now and include it
                    toReturn = bigBoard.processOperator(processName,operation,parsedContent["cmd"])
                elif operation == "createProcess":
                    toReturn = bigBoard.processOperator(processName,operation,parsedContent["scriptPath"])
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
        print " @@ genericRequestHandler() @@\n\tRequest not json, printing \
        the sent in request 'Content-Type': "+str(request.headers['Content-Type'])

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
@app.route('/start', methods = ['POST'])
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
    
    toReturn = json.dumps(genericRequestHandler(request,"status"), sort_keys=True,indent=4, separators=(',', ': '))
    #print toReturn
    return toReturn


@app.route('/cmd/', methods = ['POST'])
def apiCmd():
    # Requires:
    # { "processName" : "theNameOfTheProcess",
    #   "cmd" : "theCommandToBeSentToTheProcess" }

    toReturn = ""


    if  'application/json' in request.headers['Content-Type']: # DANGIT THIS AGAIN FUUUUUUUUUUUUU
        
        parsedCmd = request.json['cmd']
        #print "\n!! WE GOT A REQEUST:\n"+str(request.json)+"\n"
        returned = genericRequestHandler(request,"sendcmd")
        #print returned
        if returned:
            toReturn="command communicated successfully"
    else:
        toReturn = "Error, input not JSON."
    
    
    #print request.form
    return toReturn#str(request.form)


# ### CreateProcess ###
# Basic Method:

#     {
#         "processName" : "full name of the new process",
#         "scriptPath" : "path to script"
#     }

@app.route("/createProcess", methods = ['POST'])
def createProcess():
    pass
    toReturn = genericRequestHandler(request,"createProcess")
    return toReturn




@app.route("/testConsole")
@basic_auth.required
def console(): # Serves the console html page
    return render_template('testPollPage.html')


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
