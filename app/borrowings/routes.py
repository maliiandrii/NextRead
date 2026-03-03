from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.borrowings import borrowings
from app.borrowings.forms import BorrowForm, ReturnForm
from app.models import Book, Borrowing
from functools import wraps
from datetime import date


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@borrowings.route('/my')
@login_required
def my_borrowings():
    active = current_user.borrowings.filter_by(status='borrowed').all()
    history = current_user.borrowings.filter_by(status='returned').order_by(
        db.text('created_at DESC')
    ).all()
    return render_template('borrowings/my.html', title='My Borrowings',
                           active=active, history=history, today=date.today())


@borrowings.route('/borrow/<int:book_id>', methods=['GET', 'POST'])
@login_required
def borrow(book_id):
    book = Book.query.get_or_404(book_id)

    if book.available <= 0:
        flash('No copies available for this book.', 'warning')
        return redirect(url_for('books.detail', book_id=book_id))

    already = current_user.borrowings.filter_by(
        book_id=book_id, status='borrowed'
    ).first()
    if already:
        flash('You already have this book borrowed.', 'warning')
        return redirect(url_for('books.detail', book_id=book_id))

    form = BorrowForm()
    if form.validate_on_submit():
        borrowing = Borrowing(
            user_id=current_user.id,
            book_id=book_id,
            borrow_date=form.borrow_date.data,
            due_date=form.due_date.data,
            status='borrowed',
        )
        book.available -= 1
        db.session.add(borrowing)
        db.session.commit()
        flash(f'You have borrowed "{book.title}". Due: {form.due_date.data}', 'success')
        return redirect(url_for('borrowings.my_borrowings'))

    return render_template('borrowings/borrow.html', title='Borrow Book',
                           form=form, book=book)


@borrowings.route('/return/<int:borrowing_id>', methods=['POST'])
@login_required
def return_book(borrowing_id):
    borrowing = Borrowing.query.get_or_404(borrowing_id)

    # Only owner or admin can return
    if borrowing.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    if borrowing.status == 'returned':
        flash('This book has already been returned.', 'info')
        return redirect(url_for('borrowings.my_borrowings'))

    from datetime import date
    borrowing.status = 'returned'
    borrowing.return_date = date.today()
    borrowing.book.available += 1
    db.session.commit()
    flash(f'"{borrowing.book.title}" returned successfully.', 'success')

    if current_user.is_admin:
        return redirect(url_for('admin.borrowings_list'))
    return redirect(url_for('borrowings.my_borrowings'))
