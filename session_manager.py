"""Contains functions to retrieve and store user information in cookie"""
import json
import logging

from model import Project


def get_previous_projects(request):
    """Return a list of previous project keys from cookies in the request"""
    projects = []
    project_list = {}
    json_str = request.cookies.get('projects')
    if json_str is not None:
        try:
            project_list = json.loads(json_str)
        except (ValueError, KeyError, TypeError):
            print "JSON format error"
            logging.exception("Cookie json could not be decoded")
            return
    project_keys = [k for k in project_list.keys()]
    for key in project_keys:
        project = Project.get_project(key)
        projects.append(project)
    return projects

def store_user(request, response, project_key, user_id):
    """Store user for given project in a cookie"""
    projects = {}
    json_str = request.cookies.get('projects')
    if json_str is not None:
        try:
            projects = json.loads(json_str)
        except (ValueError, KeyError, TypeError):
            print "JSON format error"
            logging.exception("Cookie json could not be decoded")
    projects[project_key] = user_id
    cookie_json = json.dumps(projects)
    response.set_cookie('projects', cookie_json, max_age=10 * 365 * 24 * 60 * 60)


def get_user(request, project_key):
    """Return the ID of the current user for the given project"""
    projects = request.cookies.get('projects')
    if projects is None:
        return None
    try:
        projects = json.loads(projects)
    except (ValueError, KeyError, TypeError):
        print "JSON format error"
        logging.exception("Cookie json could not be decoded")
        return None
    user_id = projects.get(project_key)
    if user_id is not None:
        return int(user_id)
    else:
        return None
