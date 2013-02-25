webcontrolClient Classes
========================

Initially required variables
    "address" : "some address" # This could be something like "localhost" or "192.168.2.150:5000". It must be a string with the ipaddress/host and port (assumes 80 by default)

On initialization, the client-class will set up the following:

    {
        "processes" : ["nameOfFirstProcess","theSecondProcessesName","couldBeAThirdProcessesName"]
        "methods" : {
            "start" : "/start"
            "list"  : "/list"
            "status": "/status"
            "cmd"   : "/cmd/"
            "read"  : "/read"
            "kill"  : "/kill"
        }
    }

Methods of veiledClient
-----------------------

sendCommand(process, command)
    
    Requires two strings: process and command
        Sends the command to the given command using a POST request that sends:
            {""}