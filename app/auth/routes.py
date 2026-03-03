from flask import render_template, redirect, url_for, flash, request, session, make_response
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.auth import auth
from app.auth.forms import LoginForm, RegisterForm, EditProfileForm, ChangePasswordForm
from app.models import User, UserProfile


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Contact administrator.', 'danger')
                return redirect(url_for('auth.login'))

            login_user(user, remember=form.remember_me.data)

            # Store user info in session
            session['user_role'] = user.role
            session['username'] = user.username

            # Set a cookie with the username (for demonstration)
            next_page = request.args.get('next')
            response = make_response(
                redirect(next_page if next_page else url_for('main.index'))
            )
            response.set_cookie('last_login_user', user.username, max_age=30 * 24 * 3600)

            flash(f'Welcome back, {user.full_name or user.username}!', 'success')
            return response
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('auth/login.html', form=form, title='Login')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()

        # Create profile (one-to-one)
        profile = UserProfile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form, title='Register')


@auth.route('/logout')
@login_required
def logout():
    session.pop('user_role', None)
    session.pop('username', None)
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth.route('/profile')
@login_required
def profile():
    borrowings = current_user.borrowings.order_by(
        db.text('created_at DESC')
    ).limit(5).all()
    return render_template('auth/profile.html', title='My Profile',
                           borrowings=borrowings)


@auth.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    profile = current_user.profile

    if form.validate_on_submit():
        current_user.full_name = form.full_name.data
        if not profile:
            profile = UserProfile(user_id=current_user.id)
            db.session.add(profile)
        profile.bio = form.bio.data
        profile.phone = form.phone.data
        profile.address = form.address.data
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('auth.profile'))

    # Pre-fill form
    form.full_name.data = current_user.full_name
    if profile:
        form.bio.data = profile.bio
        form.phone.data = profile.phone
        form.address.data = profile.address

    return render_template('auth/edit_profile.html', form=form, title='Edit Profile')


@auth.route('/profile/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Password changed successfully.', 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash('Current password is incorrect.', 'danger')

    return render_template('auth/change_password.html', form=form, title='Change Password')
