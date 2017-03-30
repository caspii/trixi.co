import logging
import random
from string import ascii_letters, digits
from flask import Flask, render_template, request, flash, redirect, url_for, session, make_response, abort
from flaskext.markdown import Markdown
from forms import ProjectCreateForm, PeopleForm, WhoAreYouForm, TaskForm, CommentForm

from humantime import pretty_date
from model import Project, Task
from session_manager import store_user, get_user, get_previous_projects

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
Markdown(app)


def format_datetime(value):
    """Allow pretty dates via jinja2 filter"""
    return pretty_date(value)


app.jinja_env.filters['datetime'] = format_datetime


def generate_form_token():
    """Sets a token to prevent double posts."""
    if '_form_token' not in session:
        form_token = \
            ''.join([random.choice(ascii_letters + digits) for i in range(32)])
        session['_form_token'] = form_token
    return session['_form_token']


app.jinja_env.globals['form_token'] = generate_form_token


@app.before_request
def check_form_token():
    """Checks for a valid form token in POST requests."""
    print "CHECK TOKEN CALLED"
    if request.method == 'POST':
        token = session.pop('_form_token', None)
        if not token or token != request.form.get('_form_token'):
            redirect(request.url)


@app.route('/')
def landing():
    previous_projects = get_previous_projects(request)
    flash('Note that Trixi is currently in Beta! Not everything is working just yet.')
    return render_template('landing.html', previous_projects=previous_projects)


@app.route('/new', methods=['GET', 'POST'])
def new():
    form = ProjectCreateForm(request.form)
    if request.method == 'POST' and form.validate():
        session['project_name'] = form.project_name.data
        session['person_count'] = form.person_count.data
        return redirect(url_for('people'))
    else:
        flash('Note that Trixi is currently in Beta!')
        return render_template('new_project.html', form=form)


@app.route('/people', methods=['GET', 'POST'])
def people():
    form = PeopleForm(request.form)
    if request.method == 'GET':
        flash('Note that Trixi is currently in Beta!')
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


@app.route('/project/<project_key>', methods=['GET', 'POST'])
def view_project(project_key):
    project = Project.get_project(project_key)
    if project is None:
        abort(404)
    current_user_id = get_user(request, project_key)
    if current_user_id is None:
        return redirect(url_for('who_are_you', project_key=project_key))
    if request.method == 'POST':
        person_id = request.form['user_id']
        response = make_response(redirect('/project/' + project_key))
        store_user(request, response, project_key, person_id)
        return response
    # Create list of people without current user for user selection
    other_people = [p for p in project.people if p.id is not current_user_id]
    # Fetch tasks
    tasks = project.get_tasks()
    return render_template('project.html', current_user_id=current_user_id, other_people=other_people,
                           project=project, tasks=tasks)


@app.route('/create_task/<project_key>/', methods=['GET', 'POST'])
def create_task(project_key):
    form = TaskForm(request.form)
    project = Project.get_project(project_key)
    if project is None:
        abort(404)
    current_user_id = get_user(request, project_key)
    if current_user_id is None:
        return redirect(url_for('who_are_you', project_key=project_key))
    choices = [(p.id, p.name) for p in project.people]
    form.assigned_to.choices = choices
    if request.method == 'POST' and form.validate():
        title = form.title.data
        description = form.description.data
        priority = form.priority.data
        assigned_to = form.assigned_to.data
        Task.new(project.key, title, priority, current_user_id, assigned_to, description)
        flash("Your task was created")
        project.touch()
        return redirect('/project/' + project_key)
    else:
        assigned_to = current_user_id
        form.assigned_to.default = current_user_id
        form.process()
    print request.form
    return render_template('edit_task.html', form=form, project=project,
                           assigned_to=assigned_to)


@app.route('/edit_task/<project_key>/<task_key>', methods=['GET', 'POST'])
def edit_task(project_key, task_key):
    form = TaskForm(request.form)
    project = Project.get_project(project_key)
    if project is None:
        abort(404)
    task = Task.get_task(project, task_key)
    choices = [(p.id, p.name) for p in project.people]
    form.assigned_to.choices = choices
    if request.method == 'POST' and form.validate():
        flash("Task was updated")
        task.update(form.title.data, int(form.priority.data), form.description.data, form.assigned_to.data)
        return redirect(url_for('view_task', project_key=project_key, task_key=task_key))
    form.title.data = task.title
    form.priority.data = str(task.priority)
    form.description.data = task.description
    form.assigned_to.data = task.assigned_to
    return render_template('edit_task.html', task=task, project=project, form=form)


@app.route('/toggle_task_status/<project_key>/<task_key>', methods=['POST'])
def toggle_task_status(project_key, task_key):
    project = Project.get_project(project_key)
    if project is None:
        abort(404)
    task = Task.get_task(project, task_key)
    if task.status == 0:
        flash('Completed: ' + task.title)
        task.set_status(1)
    else:
        flash('Task not complete: ' + task.title)
        task.set_status(0)
    return redirect(url_for('view_project', project_key=project_key))


@app.route('/delete_tasks/<project_key>/<task_key>', methods=['POST'])
def delete_task(project_key, task_key):
    project = Project.get_project(project_key)
    if project is None:
        abort(404)
    task = Task.get_task(project, task_key)
    flash('Task deleted: ' + task.title)
    task.delete()
    return redirect(url_for('view_project', project_key=project_key))


@app.route('/delete_comment/<project_key>/<task_key>', methods=['POST'])
def delete_comment(project_key, task_key):
    project = Project.get_project(project_key)
    if project is None:
        abort(404)
    task = Task.get_task(project, task_key)
    deletion_id = int(request.form['delete_comment'])
    task.delete_comment(deletion_id)
    flash('Comment was deleted')
    return redirect(url_for('view_task', project_key=project_key, task_key=task_key))


@app.route('/task/<project_key>/<task_key>', methods=['GET', 'POST'])
def view_task(project_key, task_key):
    project = Project.get_project(project_key)
    if project is None:
        abort(404)
    task = Task.get_task(project, task_key)
    current_user_id = get_user(request, project_key)
    form = CommentForm(request.form)
    if request.method == 'POST' and form.validate():
        flash("Your comment was added")
        task.add_comment(form.comment.data, current_user_id)
        return redirect(url_for('view_task', project_key=project_key, task_key=task_key))
    return render_template('task.html', task=task, project=project, form=form)


@app.route('/who_are_you/<project_key>', methods=['GET', 'POST'])
def who_are_you(project_key):
    project = Project.get_project(project_key)
    if project is None:
        abort(404)
    form = WhoAreYouForm(request.form)
    # Populate radio buttons
    categories = [(p.id, p.name) for p in project.people]
    form.people.choices = categories
    if request.method == 'POST' and form.validate():
        person_id = request.form['people']
        person_name = project.people[int(person_id)].name
        flash('Welcome ' + person_name + '! Please bookmark this page')
        response = make_response(redirect('/project/' + project_key))
        store_user(request, response, project_key, person_id)
        return response
    else:
        return render_template('who_are_you.html', project=project, form=form)


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
