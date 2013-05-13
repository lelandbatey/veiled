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

sendCmd(processName, command)
    
    Requires two strings: processName and command
        'processName'
            String
            The name of the process you're sending a command to
        'command'
            String
            The text of the command you're sending to the process. Don't put a newline at the end, that get's inserted automatically.
        * Sends the command to the given command using a POST request that sends:
            {
                "processName": processName,
                "cmd":command
            }
getOutput(processName):
    'processName'
        String
        Name of the process to get the output of

    * Get's the output of the specified process

createProcess(processName, scriptPath):
    'processName'
        String
        Name of the process (doesn't affect the process, it's just used to keep track) that you're creating
    'scriptPath'
        String
        The FULL, ABSOLUTE PATH to the script/executable to be run. If you use stuff like '~' in this path, you're gonna have a bad time.

    * Creates a new process with the given name and which will start the given 