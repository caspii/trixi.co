import base64
import os

from google.appengine.ext import ndb


class Person(ndb.Model):
    name = ndb.StringProperty()
    active = ndb.BooleanProperty(default=True)
    id = ndb.IntegerProperty()


class Project(ndb.Model):
    read_only_key = ndb.StringProperty(required=True)
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    date_altered = ndb.DateTimeProperty(auto_now=True)
    name = ndb.StringProperty(required=True)
    people = ndb.StructuredProperty(Person, repeated=True)

    @classmethod
    def new(cls, name, people_names):
        """Add a new project to the Datastore and return the project_key of the
            new project."""
        id = base64.urlsafe_b64encode(os.urandom(6))
        read_only_key = base64.urlsafe_b64encode(os.urandom(6))
        people = [Person(name=p, id=i) for i, p in enumerate(people_names, 0)]  # Generate id field too
        new_project = Project(id=id, read_only_key=read_only_key, name=name, people=people)
        new_project.put()
        return id

    @classmethod
    def get_project(cls, project_key):
        """Fetch a project from the Datastore"""
        ndb_project_key = ndb.Key(Project, project_key)
        return ndb_project_key.get()

    def get_tasks(self):
        task_query = Task.query(ancestor=self.key)
        return [t for t in task_query]

    def touch(self):
        """Force date_altered to be updated"""
        ndb_project_key = ndb.Key(Project, self.key.id())
        ndb_project_key.get().put()


class Priority:
    low, normal, high = range(3)


class Task(ndb.Model):
    read_only_key = ndb.StringProperty(required=True)
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    date_altered = ndb.DateTimeProperty(auto_now=True)
    created_by = ndb.IntegerProperty()
    title = ndb.StringProperty(required=True)
    description = ndb.StringProperty()
    assigned_to = ndb.IntegerProperty()
    priority = ndb.IntegerProperty(required=True)

    @classmethod
    def new(cls, parent, title, priority, description=None, assigned_to=None):
        id = base64.urlsafe_b64encode(os.urandom(6))
        read_only_key = base64.urlsafe_b64encode(os.urandom(6))
        new_task = Task(id=id, read_only_key=read_only_key, parent=parent, title=title, priority=priority,
                        description=description, assigned_to=assigned_to)
        new_task.put()

    @classmethod
    def get_task(cls, project, task_key):
        """Fetch a task from the Datastore"""
        ndb_task_key = ndb.Key(Project, project.key.id(), Task, task_key)
        return ndb_task_key.get()
