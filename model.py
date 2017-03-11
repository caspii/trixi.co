from google.appengine.ext import ndb
import datetime
import base64
import os

class Project(ndb.Model):
    date_created =          ndb.DateTimeProperty(auto_now_add=True)
    date_altered =          ndb.DateTimeProperty(auto_now=True)
    name =          ndb.StringProperty()
    people =                ndb.StringProperty()

    @classmethod
    def new(cls, name):
        """Add a new project to the Datastore. Returns the project_key of the
            new project."""
        id = base64.urlsafe_b64encode(os.urandom(6))
        new_project = Project(name=name, id=id)
        new_project.put()
        return id

    @classmethod
    def get_project(cls, project_key):
        """Fetch a project from the Datastore"""
        project_key = ndb.Key(Project, project_key)
        return project_key.get()
