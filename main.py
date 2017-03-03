import logging
import humantime
import sendmail

from flask import Flask, render_template, request, flash, redirect, url_for, abort, session, make_response
from wtforms import Form, StringField, HiddenField, validators, FieldList
from wtforms.fields.html5 import EmailField



app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('A 500 error occurred during a request.')
    return 'An internal error occurred.', 500

@app.errorhandler(404)
def page_not_found(e):
    logging.info('A 404 error occurred during a request.')
    return render_template('404.html'), 404
