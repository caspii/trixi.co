from google.appengine.ext import ndb
import datetime
import base64
import os

class Person(ndb.Model):
    name = ndb.StringProperty()
    active = ndb.BooleanProperty(default=True)

class Project(ndb.Model):
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    date_altered = ndb.DateTimeProperty(auto_now=True)
    name = ndb.StringProperty(required=True)
    people = ndb.StructuredProperty(Person, repeated=True)

    @classmethod
    def new(cls, name, people_names):
        """Add a new project to the Datastore. Returns the project_key of the
            new project."""
        id = base64.urlsafe_b64encode(os.urandom(6))
        people = [ Person(name=p) for p in people_names ]
        new_project = Project(name=name, id=id, people=people)
        new_project.put()
        return id

    @classmethod
    def get_project(cls, project_key):
        """Fetch a project from the Datastore"""
        project_key = ndb.Key(Project, project_key)
        return project_key.get()
