"""Contains functions to retrieve and store user information in cookie"""
import json
import logging


def store_user(request, response, project_key, user_id):
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
    projects = {}
    try:
        projects = json.loads(request.cookies.get('projects'))
    except (ValueError, KeyError, TypeError):
        print "JSON format error"
        logging.exception("Cookie json could not be decoded")
    return projects.get(project_key)
