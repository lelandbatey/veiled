
RemoteControl Docs
==================

Basic docs for the RemoteControl python package.

#### What is the point of RemoteControl? ####

RemoteControl exists so that you can have easy access to a terminal application (or group of terminal applications) from the web, as if you where using a terminal. However, the control and interaction API makes it easy to expand how you control your applications. The API is simple, so doing what you want is also simple.

## Docs ##

### Requirements: ###
Veiled requires these python modules

    - Pexpect
    - Flask 

Each of these can be installed via "pip install <package name here>".

###Flask Server###

To interact with RemoteControl, you use a very simple and basic REST-style interface. For example, to get the status of a processControl method, you'd use an http GET request directed at http://<your RemoteControl server address>/status . This would return the status of the app, such as whether it's running, it's location, and any important configuration details.

Similarly, to send a command, you'd make an http POST request to http://<your RemoteControl server address>/cmd/ with the json data:
    
    {"cmd" : "command to send"}

The dictionary key "cmd" is required to have the value interpreted as a command. Additionally, the value of the "cmd" key should be EXACTLY as you would type into the terminal. Note, do not use a newline character at the end of the passed value, as they'll be added automatically.

Templates for webpages need to go in the "templates" directory. Check out the docs on Flask templates: http://flask.pocoo.org/docs/templating/


###procControl Class###

procControl is the heart of RemoteControl. procControl is for the most part just a wrapper around the pexpect package, allowing for simple input into the controlled program, as well as keeping track of the output in a convenient and reliable way.

##### Initialization #####



When a new procControl class is created, it is passed a script name. We expect one of two things to happen with that script name:

1. It will be a lone script name, in the form of "scriptName.sh".

In this case, it is expected that this script is running from the same current working directory as the webControl program. Because of this, it is run in a terminal as "./scriptName.sh"

2. It is the full path to a script location, such as "/home/someuser/scripts/scriptName.sh"

In this case, it will be executed as "/home/someuser/scrips/scriptName.sh", with the current working directory being the directory that webControl.py is run from.

##### Starting/Stopping the Guest Process #####

Currently, there is no way to start an arbitrary command/script using the externally available API. The behavior described in this section is very likely to change.    