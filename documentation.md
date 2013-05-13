
Veiled Docs
===========

Basic docs for the Veiled python package.

#### What is the point of Veiled? ####

Veiled exists so that you can have easy access to a terminal application (or group of terminal applications) from the web, as if you where using a terminal. However, the control and interaction API makes it easy to expand how you control your applications. The API is simple, so doing what you want is also simple.

## Docs ##

### Requirements: ###
Veiled requires these python modules

    - Pexpect
    - Flask 

Each of these can be installed via "pip install <package name here>".

### Requests: ###

Default Methods:
    
    {
        "start"         : "/start"
        "list"          : "/list"
        "status"        : "/status"
        "cmd"           : "/cmd/"
        "read"          : "/read"
        "kill"          : "/kill"
        "createProcess" : "/createProcess"
    }

Each of these requires a request made to that URI to be in POST form, and to include the processName. The only exceptions to this are "list" and "cmd". "list" does not require any data, and will simply return a json formated list of all the names of all the processes. "cmd", on the other hand, also requires the string that should be sent to the given command.
Examples:
    
    "createProcess"
    {
        "processName" : "name (can be thought of as an alias) of the process being started",
        "scriptPath"  : "the ABSOLUTE PATH to the script."
    }

> Note for `createProcess`:
> With createProcess, you cannot pass in a relative path. You also can't use shell syntax that's intended to self expand. That means you can't use '~' to refer to the home directory of the current user. You'd have to use the full path e.g. "/home/yourUser/maybe/some/dirs/script.sh".

    "cmd"
    {
        "processName" : "name of the process you're accessing",
        "cmd" : "the full text of the string you want to send"
    }

    "read"
    {
        "processName" : "the full name of the process you're accessing"
    }

    "start"
    {
        "processName" : "the full name of the process you're accessing",
    }




# Notes #

###Flask Server###

To interact with Veiled, you use a very simple and basic REST-style interface. For example, to get the status of a processControl method, you'd use an http GET request directed at http://<your veiled server address>/status . This would return the status of the app, such as whether it's running, it's location, and any important configuration details.

Similarly, to send a command, you'd make an http POST request to http://<your veiled server address>/cmd/ with the json data:
    
    {"cmd" : "command to send"}

The dictionary key "cmd" is required to have the value interpreted as a command. Additionally, the value of the "cmd" key should be EXACTLY as you would type into the terminal. Note, do not use a newline character at the end of the passed value, as they'll be added automatically.

Templates for webpages need to go in the "templates" directory. Check out the docs on Flask templates: http://flask.pocoo.org/docs/templating/


###procControl Class###

procControl is the heart of Veiled. procControl is for the most part just a wrapper around the pexpect package, allowing for simple input into the controlled program, as well as keeping track of the output in a convenient and reliable way.

##### Initialization #####


When a new procControl class is created, it is passed a script name. We expect one of two things to happen with that script name:

1. It will be a lone script name, in the form of "scriptName.sh".

In this case, it is expected that this script is running from the same current working directory as the webControl program. Because of this, it is run in a terminal as "./scriptName.sh"

2. It is the full path to a script location, such as "/home/someuser/scripts/scriptName.sh"

In this case, it will be executed as "/home/someuser/scrips/scriptName.sh", with the current working directory being the directory that webControl.py is run from.

##### Starting/Stopping the Guest Process #####

<strike>Currently, there is no way to start an arbitrary command/script using the externally available API. The behavior described in this section is very likely to change.</strike>

Huzzah, for arbitrary process creation has been implemented. That means that you can use the API to create arbitrary processes that are then controlled through the API!

To launch a process, send a POST request to the "/createProcess" URI with the data as follows:

"createProcess"
    {
        "processName" : "name (can be thought of as an alias) of the process being started",
        "scriptPath"  : "the ABSOLUTE PATH to the script."
    }

> Note for `createProcess`:
> With createProcess, you cannot pass in a relative path. You also can't use shell syntax that's intended to self expand. That means you can't use '~' to refer to the home directory of the current user. You'd have to use the full path e.g. "/home/yourUser/maybe/some/dirs/script.sh".