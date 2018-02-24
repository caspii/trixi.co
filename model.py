import base64
import os
from flask import abort
from google.appengine.ext import ndb


class Person(ndb.Model):
    name = ndb.StringProperty(required=True)
    active = ndb.BooleanProperty(required=True, default=True)
    id = ndb.IntegerProperty(required=True)


class Project(ndb.Model):
    read_only_key = ndb.StringProperty(required=True)
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    date_altered = ndb.DateTimeProperty(auto_now=True)
    name = ndb.StringProperty(required=True)
    people = ndb.StructuredProperty(Person, repeated=True)
    active = ndb.BooleanProperty(default=True)

    @classmethod
    def new(cls, name, people_names):
        """Add a new project to the Datastore and return the project_key of the
            new project."""
        id = base64.urlsafe_b64encode(os.urandom(6))
        read_only_key = base64.urlsafe_b64encode(os.urandom(6))
        people = [Person(name=p, id=i) for i, p in enumerate(people_names, 0)]  # Generate id field too
        new_project = Project(id=id, read_only_key=read_only_key, name=name, people=people)
        new_project.put()
        if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
            sendmail.project_created(name, id)
        return id

    @classmethod
    def get_project(cls, project_key):
        """Fetch a project from the Datastore"""
        ndb_project_key = ndb.Key(Project, project_key)
        project = ndb_project_key.get()
        return project

    def get_tasks(self):
        task_query = Task.query(Task.active == True, ancestor=self.key).order(-Task.priority).order(-Task.date_altered)
        return [t for t in task_query]

    def touch(self):
        """Force date_altered to be updated"""
        ndb_project_key = ndb.Key(Project, self.key.id())
        ndb_project_key.get().put()


class Comment(ndb.Model):
    text = ndb.TextProperty(required=True)
    created_by = ndb.IntegerProperty(required=True)
    date_created = ndb.DateTimeProperty(auto_now_add=True)


class Task(ndb.Model):
    read_only_key = ndb.StringProperty(required=True)
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    date_altered = ndb.DateTimeProperty(auto_now=True)
    created_by = ndb.IntegerProperty(required=True)
    title = ndb.StringProperty(required=True)
    status = ndb.IntegerProperty(required=True, default=0)  # 0=Open, 1=Completed
    priority = ndb.IntegerProperty(required=True)
    description = ndb.TextProperty()
    assigned_to = ndb.IntegerProperty(required=True)
    active = ndb.BooleanProperty(default=True)
    comments = ndb.StructuredProperty(Comment, repeated=True)

    @classmethod
    def new(cls, parent, title, priority, created_by, assigned_to, description=None):
        id = base64.urlsafe_b64encode(os.urandom(6))
        read_only_key = base64.urlsafe_b64encode(os.urandom(6))
        new_task = Task(id=id, read_only_key=read_only_key, parent=parent, title=title, priority=int(priority),
                        created_by=created_by, description=description, assigned_to=int(assigned_to))
        new_task.put()

    @classmethod
    def get_task(cls, project, task_key):
        """Fetch a task from the Datastore"""
        ndb_task_key = ndb.Key(Project, project.key.id(), Task, task_key)
        task = ndb_task_key.get()
        if task is None or task.active is False:
            abort(404)
        else:
            return task

    def touch_parent(self):
        """Touch parent's update field"""
        self.key.parent().get().touch()

    def update(self, title, priority, description, assigned_to):
        self.title = title
        self.priority = priority
        self.description = description
        self.assigned_to = assigned_to
        self.touch_parent()
        self.put()

    def set_status(self, status):
        self.status = status
        self.touch_parent()
        self.put()

    def delete(self):
        self.active = False
        self.put()

    def add_comment(self, text, created_by):
        comment = Comment(text=text, created_by=created_by)
        self.comments.append(comment)
        self.touch_parent()
        self.put()

    def get_comments(self):
        return self.comments

    def delete_comment(self, id):
        self.comments.pop(id)
        self.touch_parent()
        self.put()
