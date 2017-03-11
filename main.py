import logging
import humantime
import sendmail

from flask import Flask, render_template, request, flash, redirect, url_for, abort, session, make_response
from forms import ProjectCreateForm, PeopleForm
from model import Project


app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/new', methods=['GET', 'POST'])
def new():
    form = ProjectCreateForm(request.form)
    if request.method == 'POST' and form.validate():
        session['project_name'] = form.project_name.data
        session['person_count'] = form.person_count.data
        return redirect(url_for('people'))
    else:
        return render_template('new_project.html', form=form)

@app.route('/people', methods=['GET', 'POST'])
def people():
    form = PeopleForm(request.form)
    if request.method == 'GET':
        if not session.get('project_name') or not session.get('person_count'):
            # Means user has not come via first page of wizard,
            # therefore redirect to first page
            return redirect(url_for('new'))
        else:
            for x in range(0, int(session['person_count'])):
                form.people.append_entry()
            return render_template('people.html', form=form)
    elif request.method == 'POST':
        if form.validate():
            flash("Whoop! You created a project")
            project_key = Project.new(session['project_name'])
            return redirect('/project/' + project_key )
        else:
            return render_template('people.html', form=form)

@app.route('/project/<project_key>')
def project(project_key):
    try:
        project = Project.get_project(project_key)
        print "Retrieved project: " + project.name
    except Exception as e:
        logging.exception("Project could not be retrieved")
        abort(404)
    return render_template('project.html')

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
