from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, LinkTelegramForm
from app.models import User

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        # Log in the user automatically after registration
        login_user(user)
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/link_telegram', methods=['GET', 'POST'])
@login_required
def link_telegram():
    form = LinkTelegramForm()
    if form.validate_on_submit():
        chat_id = form.chat_id.data
        # Optional: Add validation for chat_id format if necessary

        # Check if this chat_id is already linked to another user
        existing_user_with_chat_id = User.query.filter_by(telegram_chat_id=chat_id).first()
        if existing_user_with_chat_id and existing_user_with_chat_id.id != current_user.id:
            flash('This Telegram account is already linked to another user.', 'error')
            return redirect(url_for('auth.link_telegram'))

        current_user.telegram_chat_id = chat_id
        db.session.commit()
        flash('Your Telegram account has been successfully linked!', 'success')
        # Optionally, send a confirmation message to the user's Telegram
        # from app.services.telegram_service import send_telegram_message
        # if current_user.telegram_chat_id:
        #     send_telegram_message(current_user.telegram_chat_id, "Your Telegram account has been successfully linked to your Finance App account.")
        return redirect(url_for('main.dashboard')) # Or wherever you want to redirect after linking

    return render_template('auth/link_telegram.html', title='Link Telegram Account', form=form)
