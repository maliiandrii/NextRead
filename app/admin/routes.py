from flask import render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from flask_mail import Message
from app import db, mail
from app.admin import admin
from app.admin.forms import EditUserForm, SendMailForm, GenreForm
from app.models import User, Book, Borrowing, Genre
from functools import wraps


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@admin.route('/')
@login_required
@admin_required
def dashboard():
    stats = {
        'total_users': User.query.count(),
        'total_books': Book.query.count(),
        'active_borrowings': Borrowing.query.filter_by(status='borrowed').count(),
        'total_borrowings': Borrowing.query.count(),
    }
    recent_borrowings = Borrowing.query.order_by(Borrowing.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', title='Admin Dashboard',
                           stats=stats, recent_borrowings=recent_borrowings)


# ─── Users ───────────────────────────────────────────────────────────────────

@admin.route('/users')
@login_required
@admin_required
def users_list():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    query = User.query
    if search:
        query = query.filter(
            db.or_(User.username.ilike(f'%{search}%'), User.email.ilike(f'%{search}%'))
        )
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=15, error_out=False
    )
    return render_template('admin/users.html', title='Manage Users',
                           pagination=pagination, users=pagination.items, search=search)


@admin.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    borrowings = user.borrowings.order_by(db.text('created_at DESC')).all()
    return render_template('admin/user_detail.html', title=f'User: {user.username}',
                           user=user, borrowings=borrowings)


@admin.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = EditUserForm()

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.full_name = form.full_name.data
        user.role = form.role.data
        user.is_active = form.is_active.data
        db.session.commit()
        flash(f'User "{user.username}" updated.', 'success')
        return redirect(url_for('admin.user_detail', user_id=user.id))

    form.username.data = user.username
    form.email.data = user.email
    form.full_name.data = user.full_name
    form.role.data = user.role
    form.is_active.data = user.is_active

    return render_template('admin/edit_user.html', title='Edit User', form=form, user=user)


@admin.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.users_list'))
    username = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f'User "{username}" deleted.', 'success')
    return redirect(url_for('admin.users_list'))


@admin.route('/users/<int:user_id>/toggle-active', methods=['POST'])
@login_required
@admin_required
def toggle_user_active(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'danger')
        return redirect(url_for('admin.users_list'))
    user.is_active = not user.is_active
    db.session.commit()
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User "{user.username}" {status}.', 'success')
    return redirect(url_for('admin.users_list'))


# ─── Send mail to user ────────────────────────────────────────────────────────

@admin.route('/users/<int:user_id>/send-mail', methods=['GET', 'POST'])
@login_required
@admin_required
def send_mail(user_id):
    user = User.query.get_or_404(user_id)
    form = SendMailForm()

    if form.validate_on_submit():
        try:
            msg = Message(
                subject=form.subject.data,
                recipients=[user.email],
                body=form.body.data,
            )
            mail.send(msg)
            flash(f'Email sent to {user.email}.', 'success')
        except Exception as e:
            flash(f'Failed to send email: {str(e)}', 'danger')
        return redirect(url_for('admin.user_detail', user_id=user.id))

    return render_template('admin/send_mail.html', title='Send Email',
                           form=form, user=user)


# ─── Borrowings ───────────────────────────────────────────────────────────────

@admin.route('/borrowings')
@login_required
@admin_required
def borrowings_list():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    query = Borrowing.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    pagination = query.order_by(Borrowing.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/borrowings.html', title='All Borrowings',
                           pagination=pagination, borrowings=pagination.items,
                           status_filter=status_filter)


# ─── Genres ───────────────────────────────────────────────────────────────────

@admin.route('/genres')
@login_required
@admin_required
def genres_list():
    genres = Genre.query.order_by(Genre.name).all()
    return render_template('admin/genres.html', title='Genres', genres=genres)


@admin.route('/genres/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_genre():
    form = GenreForm()
    if form.validate_on_submit():
        genre = Genre(name=form.name.data, description=form.description.data)
        db.session.add(genre)
        db.session.commit()
        flash(f'Genre "{genre.name}" created.', 'success')
        return redirect(url_for('admin.genres_list'))
    return render_template('admin/genre_form.html', title='Create Genre', form=form)


@admin.route('/genres/<int:genre_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_genre(genre_id):
    genre = Genre.query.get_or_404(genre_id)
    form = GenreForm()
    if form.validate_on_submit():
        genre.name = form.name.data
        genre.description = form.description.data
        db.session.commit()
        flash(f'Genre "{genre.name}" updated.', 'success')
        return redirect(url_for('admin.genres_list'))
    form.name.data = genre.name
    form.description.data = genre.description
    return render_template('admin/genre_form.html', title='Edit Genre', form=form, genre=genre)


@admin.route('/genres/<int:genre_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_genre(genre_id):
    genre = Genre.query.get_or_404(genre_id)
    name = genre.name
    db.session.delete(genre)
    db.session.commit()
    flash(f'Genre "{name}" deleted.', 'success')
    return redirect(url_for('admin.genres_list'))
