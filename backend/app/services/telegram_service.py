import telegram
from flask import current_app

async def send_telegram_message(chat_id, message_text):
    """
    Sends a message to a specified Telegram chat ID.
    Uses python-telegram-bot's async API.
    """
    token = current_app.config.get('TELEGRAM_BOT_TOKEN')
    if not token or token == "YOUR_TELEGRAM_BOT_TOKEN":
        current_app.logger.error("Telegram bot token is not configured or is set to default.")
        return False

    bot = telegram.Bot(token=token)
    try:
        await bot.send_message(chat_id=str(chat_id), text=message_text)
        current_app.logger.info(f"Sent Telegram message to {chat_id}: {message_text}")
        return True
    except telegram.error.TelegramError as e:
        current_app.logger.error(f"Error sending Telegram message to {chat_id}: {e}")
        # Specific error handling based on error type if needed
        if isinstance(e, telegram.error.BadRequest): # e.g. Chat not found
            current_app.logger.error(f"Telegram BadRequest: {e.message}. Chat ID: {chat_id} might be invalid or bot not started by user.")
        elif isinstance(e, telegram.error.Unauthorized): # e.g. Bot token invalid
            current_app.logger.error(f"Telegram Unauthorized: {e.message}. Check bot token.")
        return False
    except Exception as e:
        current_app.logger.error(f"An unexpected error occurred while sending Telegram message to {chat_id}: {e}")
        return False

async def handle_telegram_updates(request_json):
    """
    Basic handler for incoming Telegram updates (e.g., /start command).
    This is a very basic example. A real bot would have more sophisticated command handling.
    """
    token = current_app.config.get('TELEGRAM_BOT_TOKEN')
    if not token:
        current_app.logger.error("Telegram bot token is not configured.")
        return

    bot = telegram.Bot(token=token)
    update = telegram.Update.de_json(request_json, bot)

    if update.message and update.message.text:
        chat_id = update.message.chat_id
        text = update.message.text

        current_app.logger.info(f"Received Telegram message from {chat_id}: {text}")

        if text == '/start':
            reply_message = (
                f"Hello! Your Chat ID is: {chat_id}\n"
                "You can use this ID to link your account on our website."
            )
            await send_telegram_message(chat_id, reply_message)
        # Add more command handlers here if needed
        # elif text == '/help':
        #     await send_telegram_message(chat_id, "Help message...")
        else:
            # Echoing back for now, or provide a default message
            # await send_telegram_message(chat_id, f"You said: {text}")
            await send_telegram_message(chat_id, "I'm a simple notification bot. Use /start to get your chat ID.")

    # In a real application, you might want to process other types of updates too.
