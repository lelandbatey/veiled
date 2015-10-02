#!/usr/bin/env python
from __future__ import print_function
import veiled
import flask
import json

APP = flask.Flask(__name__)

@APP.route('/')
def root():
    return "Mainpage"


