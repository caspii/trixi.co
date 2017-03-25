import logging

from flask import Flask, render_template, request, flash, redirect, url_for, abort, session, make_response
from flaskext.markdown import Markdown

from forms import ProjectCreateForm, PeopleForm, WhoAreYouForm, TaskForm
from humantime import pretty_date
from model import Project, Task
from session_manager import store_user, get_user, get_previous_projects

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
Markdown(app)


# Allow pretty dates via jinja2 filter
def format_datetime(value):
    return pretty_date(value)


app.jinja_env.filters['datetime'] = format_datetime


@app.route('/')
def landing():
    previous_projects = get_previous_projects(request)
    return render_template('landing.html', previous_projects=previous_projects)


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


@app.route('/project/<project_key>', methods=['GET', 'POST'])
def view_project(project_key):
    project = Project.get_project(project_key)
    if project is None:
        logging.exception("Project could not be retrieved: " + project_key)
        abort(404)
    current_user_id = get_user(request, project_key)
    if current_user_id is None:
        return redirect(url_for('who_are_you', project_key=project_key))
    current_user_name = project.people[current_user_id].name
    if request.method == 'POST':
        person_id = request.form['user_id']
        response = make_response(redirect('/project/' + project_key))
        store_user(request, response, project_key, person_id)
        return response
    # Create list of people without current user for user selection
    other_people = [p for p in project.people if p.id is not current_user_id]
    # Fetch tasks
    tasks = project.get_tasks()
    return render_template('project.html', current_user_name=current_user_name, other_people=other_people,
                           project=project, tasks=tasks)


@app.route('/create_task/<project_key>/', methods=['GET', 'POST'])
def create_task(project_key):
    form = TaskForm(request.form)
    project = Project.get_project(project_key)
    current_user_id = get_user(request, project_key)
    if current_user_id is None:
        return redirect(url_for('who_are_you', project_key=project_key))
    if request.method == 'POST' and form.validate():
        title = form.title.data
        description = form.description.data
        priority = int(form.priority.data)
        Task.new(project.key, title, priority, current_user_id, description, 1)
        flash("Your task was created")
        project.touch()
        return redirect('/project/' + project_key)
    return render_template('edit_task.html', form=form, project=project)


@app.route('/edit_task/<project_key>/<task_key>', methods=['GET', 'POST'])
def edit_task(project_key, task_key):
    form = TaskForm(request.form)
    project = Project.get_project(project_key)
    task = Task.get_task(project, task_key)
    if request.method == 'POST' and form.validate():
        flash("Task was updated")
        task.update(form.title.data, int(form.priority.data), form.description.data)
        return redirect(url_for('view_task', project_key=project_key, task_key=task_key))
    form.title.data = task.title
    form.priority.data = str(task.priority)
    form.description.data = task.description
    return render_template('edit_task.html', task=task, project=project, form=form)


@app.route('/complete_task/<project_key>/<task_key>', methods=['POST'])
def complete_task(project_key, task_key):
    project = Project.get_project(project_key)
    task = Task.get_task(project, task_key)
    task.set_status(1)
    flash('Completed: ' + task.title)
    return redirect(url_for('view_project', project_key=project_key))


@app.route('/task/<project_key>/<task_key>', methods=['GET', 'POST'])
def view_task(project_key, task_key):
    project = Project.get_project(project_key)
    task = Task.get_task(project, task_key)
    return render_template('task.html', task=task, project=project)


@app.route('/who_are_you/<project_key>', methods=['GET', 'POST'])
def who_are_you(project_key):
    project = Project.get_project(project_key)
    form = WhoAreYouForm(request.form)
    if project is None:
        logging.exception("Project could not be retrieved: " + project_key)
        abort(404)
    # Populate radio buttons
    categories = [(p.id, p.name) for p in project.people]
    form.people.choices = categories
    if request.method == 'POST' and form.validate():
        person_id = request.form['people']
        person_name = project.people[int(person_id)].name
        flash('Welcome ' + person_name + '! We recommend you bookmark this page')
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
