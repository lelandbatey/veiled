#!/usr/bin/env python
from __future__ import print_function
from process_collection import ProcessCollection
from flask_restful import reqparse
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


def make_json_response(obj):
    """Transforms object into proper json response."""
    response = jsonpickle.encode(obj, unpicklable=False)
    response = flask.make_response(response)
    response.headers["Content-type"] = "application/json"
    return response


@APP.route('/')
def root():
    """A placeholder root for now."""
    return "Mainpage"

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
    PROC_COL.new_process(args.command_path)
    return "Process started with command_path: '{}'".format(args.command_path)

@APP.route('/api/processes', methods=['DELETE'])
def halt_all_processes():
    """Runs the 'stop' method on all processes."""
    for pid in PROC_COL:
        PROC_COL[pid].stop()
    return 'success'

@APP.route('/api/processes/<int:pid>', methods=['GET'])
def show_process_status(pid):
    """Returns the status of a process."""
    process = PROC_COL[pid]
    return make_json_response(process)

@APP.route('/api/processes/<int:pid>', methods=['PUT'])
def toggle_process(pid):
    """Starts or stops a process by it's pid."""
    process = PROC_COL[pid]
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
        ret_val = "Action was neither 'start' nor 'stop'"
    ret_val = "Successfulle {}ed the process".format(args.action)

    return make_json_response(ret_val)


if __name__ == '__main__':
    APP.debug = True
    APP.run(host='0.0.0.0')

