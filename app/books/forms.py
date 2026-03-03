from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Optional, NumberRange, ValidationError
from app.models import Book


class BookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(1, 300)])
    author = StringField('Author', validators=[DataRequired(), Length(1, 200)])
    isbn = StringField('ISBN', validators=[Optional(), Length(0, 20)])
    published_year = IntegerField('Published Year',
                                   validators=[Optional(), NumberRange(min=1, max=2100)])
    description = TextAreaField('Description', validators=[Optional(), Length(0, 2000)])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    genres = SelectMultipleField('Genres', coerce=int)
    submit = SubmitField('Save')

    def __init__(self, *args, book_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._book_id = book_id
        from app.models import Genre
        self.genres.choices = [(g.id, g.name) for g in Genre.query.order_by('name').all()]

    def validate_isbn(self, field):
        if field.data:
            query = Book.query.filter_by(isbn=field.data)
            if self._book_id:
                query = query.filter(Book.id != self._book_id)
            if query.first():
                raise ValidationError('A book with this ISBN already exists.')


class SearchForm(FlaskForm):
    query = StringField('Search', validators=[Optional()])
    submit = SubmitField('Search')
