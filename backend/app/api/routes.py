from flask import jsonify, request, current_app
from flask_login import login_required, current_user
from app.api import bp
from app.services.yfinance_service import get_bitcoin_price, get_gold_price
from app.services.telegram_service import send_telegram_message, handle_telegram_updates
import asyncio # For running async telegram functions

# --- Data Fetching API Endpoints ---
@bp.route('/data/bitcoin', methods=['GET'])
@login_required
def bitcoin_data():
    price = get_bitcoin_price()
    if price is not None:
        return jsonify({'success': True, 'asset': 'Bitcoin', 'price_usd': price})
    else:
        return jsonify({'success': False, 'message': 'Could not fetch Bitcoin price.'}), 500

@bp.route('/data/gold', methods=['GET'])
@login_required
def gold_data():
    price = get_gold_price()
    if price is not None:
        return jsonify({'success': True, 'asset': 'Gold', 'price_usd': price})
    else:
        return jsonify({'success': False, 'message': 'Could not fetch Gold price.'}), 500

# --- Notification API Endpoints ---
@bp.route('/notify/bitcoin', methods=['POST'])
@login_required
async def notify_bitcoin():
    if not current_user.telegram_chat_id:
        return jsonify({'success': False, 'message': 'Telegram account not linked.'}), 400

    price = get_bitcoin_price()
    if price is None:
        return jsonify({'success': False, 'message': 'Could not fetch Bitcoin price to send notification.'}), 500

    message = f"Bitcoin Price Alert:\nBTC-USD: ${price}"

    success = await send_telegram_message(current_user.telegram_chat_id, message)
    if success:
        return jsonify({'success': True, 'message': f'Bitcoin price notification sent to Telegram Chat ID {current_user.telegram_chat_id}.'})
    else:
        return jsonify({'success': False, 'message': 'Failed to send Telegram notification.'}), 500

@bp.route('/notify/gold', methods=['POST'])
@login_required
async def notify_gold():
    if not current_user.telegram_chat_id:
        return jsonify({'success': False, 'message': 'Telegram account not linked.'}), 400

    price = get_gold_price()
    if price is None:
        return jsonify({'success': False, 'message': 'Could not fetch Gold price to send notification.'}), 500

    message = f"Gold Price Alert:\nGC=F: ${price}"

    success = await send_telegram_message(current_user.telegram_chat_id, message)
    if success:
        return jsonify({'success': True, 'message': f'Gold price notification sent to Telegram Chat ID {current_user.telegram_chat_id}.'})
    else:
        return jsonify({'success': False, 'message': 'Failed to send Telegram notification.'}), 500

# --- User Info API Endpoint ---
@bp.route('/user', methods=['GET'])
@login_required
def get_user_info():
    return jsonify({
        'success': True,
        'email': current_user.email,
        'telegram_linked': bool(current_user.telegram_chat_id),
        'telegram_chat_id': current_user.telegram_chat_id
    })

# --- Telegram Bot Webhook (Optional - for bot to receive messages like /start) ---
# This endpoint would be set as the webhook for your Telegram bot.
# Telegram sends updates (messages, commands) from users to this URL.
@bp.route('/telegram_webhook/<token>', methods=['POST'])
async def telegram_webhook(token):
    # Basic security: check if the token in the URL matches your bot token
    # This is a simple way to protect your webhook. More robust methods exist.
    if token != current_app.config.get('TELEGRAM_BOT_TOKEN'):
        current_app.logger.warning(f"Invalid token received on Telegram webhook: {token}")
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    if request.is_json:
        update_data = request.get_json()
        current_app.logger.info(f"Received Telegram update via webhook: {update_data}")
        # It's good practice to run the handler in a separate task
        # so the webhook can return a response to Telegram quickly.
        asyncio.create_task(handle_telegram_updates(update_data))
        return jsonify({'success': True, 'message': 'Update received'}), 200
    else:
        current_app.logger.error("Telegram webhook received non-JSON data.")
        return jsonify({'success': False, 'message': 'Invalid request format, JSON expected.'}), 400

# Note on running async with Flask:
# Flask's default development server is synchronous. For production or robust async handling,
# you'd typically use an ASGI server like Uvicorn or Hypercorn with an ASGI adapter for Flask (e.g., asgiref.wsgi.WsgiToAsgi).
# However, for `python-telegram-bot` v20+, its network calls are async.
# `asyncio.run(send_telegram_message(...))` can work in simple sync Flask routes for one-off calls,
# but for webhook handling and general async operations, a proper ASGI setup is better.
# For simplicity in this example, we're using `async def` routes and assuming the execution environment
# can handle them (e.g. Flask 2.0+ with an ASGI server or by careful management of asyncio event loop).
# If running with Werkzeug (default dev server), you might need to wrap `asyncio.run()` around await calls
# or use `flask_apscheduler` which handles its own threading for scheduled jobs.
# The `async def` routes will work if you run Flask with an ASGI server.
# For `python-telegram-bot` calls from synchronous Flask routes, you might need:
# `asyncio.run(send_telegram_message(current_user.telegram_chat_id, message))`
# However, since `python-telegram-bot` v20 is async-first, it's better to structure for async.
# For the webhook, `asyncio.create_task` is used to prevent blocking.
# The plan doesn't explicitly state ASGI server setup, so this is a best-effort with standard Flask.
# If issues arise, using `asyncio.run()` for the `send_telegram_message` calls in the `notify_*` routes
# might be a simpler immediate fix for Werkzeug, but ASGI is the "correct" way for async Flask.
# Example of using asyncio.run() if not using an ASGI server for the notify routes:
# @bp.route('/notify/bitcoin', methods=['POST'])
# @login_required
# def notify_bitcoin_sync(): # Renamed to avoid conflict if you switch to async later
#     if not current_user.telegram_chat_id:
#         return jsonify({'success': False, 'message': 'Telegram account not linked.'}), 400
#     price = get_bitcoin_price()
#     if price is None:
#         return jsonify({'success': False, 'message': 'Could not fetch Bitcoin price.'}), 500
#     message = f"Bitcoin Price Alert: BTC-USD: ${price}"
#     try:
#         loop = asyncio.get_event_loop()
#         if loop.is_running():
#             # If an event loop is already running (e.g. in a test environment or specific setup)
#             # schedule the coroutine and wait for its result.
#             # This is a more complex scenario. For typical Flask sync routes, a new loop is often needed.
#             # Or use a thread to run the async code.
#             # For simplicity, we'll assume we can run it directly or this needs an ASGI server.
#             # Alternatively, use nest_asyncio if in a Jupyter notebook or similar environment.
#             # Simplest for now is to assume an ASGI server or that direct `await` works with Flask 2.x.
#             # If not, the `asyncio.run()` approach is a fallback for simple cases.
#             success = asyncio.run(send_telegram_message(current_user.telegram_chat_id, message))
#         else:
#             success = asyncio.run(send_telegram_message(current_user.telegram_chat_id, message))
#     except RuntimeError as e: # Handles "cannot be called from a running event loop"
#         # This can happen if Flask is run with some async capabilities already (e.g. Quart)
#         # or if called from an already async context.
#         # A more robust solution involves checking `asyncio.get_running_loop()`
#         # or using `nest_asyncio` if appropriate for the environment.
#         current_app.logger.error(f"Asyncio runtime error: {e}. Consider using nest_asyncio or checking event loop status.")
#         # Fallback or specific handling here. For now, assume failure.
#         return jsonify({'success': False, 'message': 'Async execution error.'}), 500
#
#     if success:
#         return jsonify({'success': True, 'message': 'Bitcoin price notification sent.'})
#     else:
#         return jsonify({'success': False, 'message': 'Failed to send Telegram notification.'}), 500
