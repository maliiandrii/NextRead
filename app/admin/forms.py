from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional


class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(3, 80)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 120)])
    full_name = StringField('Full Name', validators=[Length(0, 150)])
    role = SelectField('Role', choices=[('user', 'User'), ('admin', 'Admin')])
    is_active = BooleanField('Active')
    submit = SubmitField('Save Changes')


class SendMailForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired(), Length(1, 200)])
    body = TextAreaField('Message', validators=[DataRequired(), Length(1, 5000)])
    submit = SubmitField('Send Email')


class GenreForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 100)])
    description = TextAreaField('Description', validators=[Optional(), Length(0, 500)])
    submit = SubmitField('Save')
