from flask import render_template, request
from app.main import main
from app.models import Book, Borrowing, User


@main.route('/')
def index():
    recent_books = Book.query.order_by(Book.created_at.desc()).limit(6).all()
    return render_template('main/index.html', title='Library', recent_books=recent_books)


@main.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403


@main.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404


@main.errorhandler(500)
def internal_error(e):
    return render_template('errors/500.html'), 500
