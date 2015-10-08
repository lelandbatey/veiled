#!/usr/bin/env python
from __future__ import print_function
from process_collection import ProcessCollection
from flask_restful import reqparse
from functools import wraps
import jsonpickle
import flask
import json

# Set encoding options so jsonpickle will pretty-print it's output
jsonpickle.set_preferred_backend('json')
jsonpickle.set_encoder_options('json', sort_keys=True,
                               indent=4, separators=(',', ': '))


# Declaration of the important constants for this
APP = flask.Flask(__name__)
PROC_COL = ProcessCollection()

def validate_pid(func):
    """Decorator that validates the given pid, then passes a valid process to
    the actual handler.

    Makes use of the convenience function `functools.wraps` which changes the
    __name__ and __doc__ attributes of the wrapping function. Info here:
        https://docs.python.org/2/library/functools.html#functools.wraps"""
    @wraps(func)
    def validator(*args, **kwargs):
        """Validates the pid"""
        print(jsonpickle.encode(kwargs, unpicklable=False))
        pid = kwargs['pid']
        if not pid in PROC_COL:
            return "No process with given pid", 400
        process = PROC_COL[pid]
        kwargs['process'] = process
        return func(*args)
    return validator


def make_json_response(obj):
    """Transforms object into proper json response."""
    response = jsonpickle.encode(obj, unpicklable=False)
    response = flask.make_response(response)
    response.headers["Content-type"] = "application/json"
    return response


@APP.route('/')
def root():
    """A placeholder root for now."""
    return flask.render_template('console.html')


@APP.route('/api/processes', methods=['GET'])
def show_processes():
    """Shows all processes"""
    return make_json_response(PROC_COL)


@APP.route('/api/processes', methods=['POST'])
def create_process():
    """Creates a process. Specify the executable in the 'command_path' arg."""
    parser = reqparse.RequestParser()
    parser.add_argument('command_path', required=True,
                        help='path to an executable on the system to be run.')
    args = parser.parse_args()
    pid = PROC_COL.new_process(args.command_path)
    return make_json_response({'pid': pid, 'command_path': args.command_path})


@APP.route('/api/processes', methods=['DELETE'])
def halt_all_processes():
    """Runs the 'stop' method on all processes."""
    for pid in PROC_COL:
        PROC_COL[pid].stop()
    return 'success'


@APP.route('/api/processes/<int:pid>', methods=['GET'])
@validate_pid
def show_process_status(pid, process):
    """Returns the status of a process."""
    return make_json_response(process)


@APP.route('/api/processes/<int:pid>/<int:after_idx>', methods=['GET'])
@validate_pid
def show_process_status_after_idx(pid, after_idx, process):
    """Returns the status of a process after a given index."""
    ret_val = {'isalive': process.isalive(),
               'command_path': process.command_path}
    ret_val['output'], ret_val['last_index'] = process.read(after_idx)
    return make_json_response(ret_val)

@APP.route('/api/processes/<int:pid>', methods=['POST'])
@validate_pid
def send_to_process(pid, process):
    """Sends a given command to a process."""
    parser = reqparse.RequestParser()
    parser.add_argument('command', required=True,
                        help='Command to be sent to the process')
    args = parser.parse_args()

    if not process.isalive():
        return "process is not running", 500
    else:
        process.send(args.command)
        return "success"


@APP.route('/api/processes/<int:pid>', methods=['PUT'])
@validate_pid
def toggle_process(pid, process):
    """Starts or stops a process by it's pid."""
    parser = reqparse.RequestParser()
    parser.add_argument('action', required=True,
                        help='Either "start" or "stop" the process')
    args = parser.parse_args()
    ret_val = ""

    if args.action == 'start':
        process.start()
    elif args.action == 'stop':
        process.stop()
    else:
        return "Action was neither 'start' nor 'stop'", 400
    ret_val = "Successfulle {}ed the process".format(args.action)

    return make_json_response(ret_val)



APP.debug = True
if __name__ == '__main__':
    APP.debug = True
    APP.run(host='0.0.0.0')

