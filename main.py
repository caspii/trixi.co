import logging

from flask import Flask, render_template, request, flash, redirect, url_for, abort, session, make_response

from forms import ProjectCreateForm, PeopleForm, WhoAreYouForm
from model import Project
from session_manager import store_user, get_user

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
            project_name = session['project_name']
            people_names = [p.data for p in form.people]
            project_key = Project.new(project_name, people_names)
            response = make_response(redirect('/project/' + project_key))
            store_user(request, response, project_key, 0)
            return response
        else:
            return render_template('people.html', form=form)


@app.route('/project/<project_key>')
def show_project(project_key):
    project = Project.get_project(project_key)
    if project is None:
        logging.exception("Project could not be retrieved: " + project_key)
        abort(404)
    user_id = get_user(request, project_key)
    print "User id = " + str(user_id)
    if user_id is None:
        return redirect(url_for('who_are_you', project_key=project_key))
    return render_template('project.html')


@app.route('/who_are_you/<project_key>', methods=['GET', 'POST'])
def who_are_you(project_key):
    project = Project.get_project(project_key)
    form = WhoAreYouForm(request.form)
    if project is None:
        logging.exception("Project could not be retrieved: " + project_key)
        abort(404)
    if request.method == 'GET':
        # Populate radio buttons
        categories = [(p.id, p.name) for p in project.people]
        form.people.choices = categories
        return render_template('who_are_you.html', project=project, form=form, project_key=project_key)
    elif request.method == 'POST':
        print "Posting: " + str(request.form)
        flash('Welcome to the club, Dude')
        return render_template('who_are_you.html', project=project, form=form, project_key=project_key)


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
