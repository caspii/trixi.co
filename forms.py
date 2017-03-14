from wtforms import Form, StringField, IntegerField, validators, \
    FieldList, ValidationError, RadioField
from wtforms.validators import *

def validate_people(form, field):
    """Validator to ensure that all names are unique"""
    for person in form.people:
        if person.id is not field.id and person.data == field.data:
            raise ValidationError('Names must be unique')


class ProjectCreateForm(Form):
    project_name = StringField('Give your project a name', [validators.Length(min=1, max=40), validators.DataRequired()])
    person_count = IntegerField('Number of people on this project (not more than 10)', [validators.NumberRange(min=2, max=10)], default=2)


class PeopleForm(Form):
    people = FieldList(StringField('Name', [validators.InputRequired(), validators.Length(min=1, max=25), validate_people]))


class WhoAreYouForm(Form):
    people = RadioField('Label', coerce=int, choices=[])
