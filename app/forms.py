from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, BooleanField, SubmitField, SelectField, TimeField
from wtforms.validators import DataRequired, Optional, Length, ValidationError
from datetime import date, datetime, time

def validate_future_date(form, field):
    if field.data and field.data < date.today():
        raise ValidationError('Due date cannot be in the past. Please select a future date.')

class TaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    due_date = DateField('Due Date', validators=[Optional(), validate_future_date], default=date.today)
    due_time = TimeField('Due Time', validators=[Optional()], default=time(hour=23, minute=59))
    priority = SelectField('Priority', choices=[
        ('none', 'None'), 
        ('low', 'Low'), 
        ('medium', 'Medium'), 
        ('high', 'High')
    ], default='none')
    tags = StringField('Tags', validators=[Optional(), Length(max=200)], 
                      description='Separate multiple tags with commas')
    completed = BooleanField('Completed')
    submit = SubmitField('Save')
    
class TagForm(FlaskForm):
    name = StringField('Tag Name', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Add Tag')
