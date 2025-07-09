from flask import render_template, flash, redirect, url_for, current_app
from flask_login import current_user, login_required
from app.main import bp
# Import services that will be created later
# from app.services.yfinance_service import get_bitcoin_price, get_gold_price
# from app.services.telegram_service import send_telegram_message

@bp.route('/')
@bp.route('/index')
def index():
    # Simple landing page
    return render_template('main/index.html', title='Home')

@bp.route('/dashboard')
@login_required
def dashboard():
    # bitcoin_price = get_bitcoin_price()
    # gold_price = get_gold_price()
    # Placeholder data for now
    bitcoin_price = "N/A"
    gold_price = "N/A"

    # For now, we won't fetch live data here to keep it simple.
    # This will be done via API calls from the frontend or specific actions.
    return render_template('main/dashboard.html', title='Dashboard',
                           bitcoin_price=bitcoin_price, gold_price=gold_price,
                           user_email=current_user.email,
                           telegram_linked=bool(current_user.telegram_chat_id))

# Example of how a notification might be triggered from a route (for testing)
# This will later be primarily triggered via API calls
@bp.route('/notify_test/bitcoin')
@login_required
def notify_test_bitcoin():
    # if not current_user.telegram_chat_id:
    #     flash('Please link your Telegram account first.', 'warning')
    #     return redirect(url_for('main.dashboard'))
    #
    # price = get_bitcoin_price()
    # if price:
    #     message = f"Bitcoin Price Update: ${price}"
    #     send_telegram_message(current_user.telegram_chat_id, message)
    #     flash(f'Sent Bitcoin price notification to your Telegram: {message}', 'success')
    # else:
    #     flash('Could not fetch Bitcoin price.', 'danger')
    flash("Test notification - functionality to be fully implemented with API and services.", "info")
    return redirect(url_for('main.dashboard'))
