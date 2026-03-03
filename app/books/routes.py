from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.books import books
from app.books.forms import BookForm, SearchForm
from app.models import Book, Genre
from functools import wraps


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@books.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    genre_id = request.args.get('genre', type=int)

    query = Book.query

    if search:
        query = query.filter(
            db.or_(
                Book.title.ilike(f'%{search}%'),
                Book.author.ilike(f'%{search}%'),
                Book.isbn.ilike(f'%{search}%')
            )
        )

    if genre_id:
        genre = Genre.query.get_or_404(genre_id)
        query = query.filter(Book.genres.contains(genre))

    pagination = query.order_by(Book.title).paginate(
        page=page, per_page=9, error_out=False
    )

    genres = Genre.query.order_by(Genre.name).all()
    return render_template('books/index.html', title='Book Catalog',
                           pagination=pagination, books=pagination.items,
                           search=search, genres=genres, selected_genre=genre_id)


@books.route('/<int:book_id>')
def detail(book_id):
    book = Book.query.get_or_404(book_id)
    user_has_borrowed = False
    if current_user.is_authenticated:
        user_has_borrowed = current_user.borrowings.filter_by(
            book_id=book_id, status='borrowed'
        ).first() is not None
    return render_template('books/detail.html', title=book.title,
                           book=book, user_has_borrowed=user_has_borrowed)


@books.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    form = BookForm()
    if form.validate_on_submit():
        book = Book(
            title=form.title.data,
            author=form.author.data,
            isbn=form.isbn.data or None,
            published_year=form.published_year.data,
            description=form.description.data,
            quantity=form.quantity.data,
            available=form.quantity.data,
        )
        if form.genres.data:
            book.genres = Genre.query.filter(Genre.id.in_(form.genres.data)).all()
        db.session.add(book)
        db.session.commit()
        flash(f'Book "{book.title}" added successfully.', 'success')
        return redirect(url_for('books.detail', book_id=book.id))

    return render_template('books/form.html', title='Add Book', form=form, action='Create')


@books.route('/<int:book_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(book_id):
    book = Book.query.get_or_404(book_id)
    form = BookForm(book_id=book_id)

    if form.validate_on_submit():
        quantity_diff = form.quantity.data - book.quantity
        book.title = form.title.data
        book.author = form.author.data
        book.isbn = form.isbn.data or None
        book.published_year = form.published_year.data
        book.description = form.description.data
        book.quantity = form.quantity.data
        book.available = max(0, book.available + quantity_diff)
        if form.genres.data:
            book.genres = Genre.query.filter(Genre.id.in_(form.genres.data)).all()
        else:
            book.genres = []
        db.session.commit()
        flash(f'Book "{book.title}" updated successfully.', 'success')
        return redirect(url_for('books.detail', book_id=book.id))

    # Pre-fill form
    form.title.data = book.title
    form.author.data = book.author
    form.isbn.data = book.isbn
    form.published_year.data = book.published_year
    form.description.data = book.description
    form.quantity.data = book.quantity
    form.genres.data = [g.id for g in book.genres]

    return render_template('books/form.html', title='Edit Book', form=form,
                           book=book, action='Update')


@books.route('/<int:book_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(book_id):
    book = Book.query.get_or_404(book_id)
    title = book.title
    db.session.delete(book)
    db.session.commit()
    flash(f'Book "{title}" deleted.', 'success')
    return redirect(url_for('books.index'))
