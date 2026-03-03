from flask_wtf import FlaskForm
from wtforms import DateField, SubmitField
from wtforms.validators import DataRequired
from datetime import date, timedelta


class BorrowForm(FlaskForm):
    borrow_date = DateField('Borrow Date', validators=[DataRequired()],
                             default=date.today)
    due_date = DateField('Due Date', validators=[DataRequired()],
                          default=lambda: date.today() + timedelta(days=14))
    submit = SubmitField('Borrow Book')


class ReturnForm(FlaskForm):
    submit = SubmitField('Return Book')
