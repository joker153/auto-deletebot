import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import (CallbackContext, CommandHandler, Filters, JobQueue,
                          MessageHandler, Updater)

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
ADMINS = list(map(int, os.environ.get('ADMINS', '').split()))

# Define message deletion time
DEFAULT_DELETION_TIME = 300  # 5 minutes

# Define callback functions
def start(update: Update, context: CallbackContext) -> None:
    """Send a welcome message to the user."""
    user = update.message.from_user
    update.message.reply_text(f'Hi {user.first_name}, welcome to the bot!')

def set_deletion_time(update: Update, context: CallbackContext) -> None:
    """Allow user to set the message deletion time."""
    keyboard = [[InlineKeyboardButton("1 minute", callback_data='60'),
                 InlineKeyboardButton("5 minutes", callback_data='300')],
                [InlineKeyboardButton("10 minutes", callback_data='600'),
                 InlineKeyboardButton("30 minutes", callback_data='1800')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Select the time after which messages should be deleted:', reply_markup=reply_markup)

def delete_message(update: Update, context: CallbackContext) -> None:
    """Delete the message after the specified time."""
    message = update.message
    chat_id = message.chat_id
    message_id = message.message_id
    deletion_time = context.user_data.get('deletion_time', DEFAULT_DELETION_TIME)
    context.job_queue.run_once(delete_callback, deletion_time, context=[chat_id, message_id])

def delete_callback(context: CallbackContext) -> None:
    """Callback function to delete the message."""
    chat_id, message_id = context.job.context
    context.bot.delete_message(chat_id=chat_id, message_id=message_id)

def get_users(update: Update, context: CallbackContext) -> None:
    """Get the list of users in the chat."""
    chat_id = update.message.chat_id
    if update.message.from_user.id not in ADMINS:
        update.message.reply_text('This command is only available to admins.')
        return
    members = [member.user for member in context.bot.get_chat(chat_id).get_members()]
    user_details = [f'{user.first_name} ({user.id})' for user in members]
    message = '\n'.join(user_details)
    update.message.reply_text(f'Users in the group:\n\n{message}')

def broadcast(update: Update, context: CallbackContext) -> None:
    """Broadcast a message to the chat."""
    if update.message.from_user.id not in ADMINS:
        update.message.reply_text('This command is only available to admins.')
        return
    message = update.message.text[10:]
    members = [member.user.id for member in context.bot.get_chat(chat_id).get_members()]
    context.bot.send_message(chat_id=chat_id, text=message)
    for member_id in members:
        try:
            context.bot.send_message(chat_id=member_id, text=message)
        except Exception as e:
            logger.error(f'Error sending message to user {member_id}: {e}')

def join_channel(update: Update, context: CallbackContext) -> None:
    """Send a message with a button that allows the user to join the Telegram channel."""
    user = update.message.from_user
    keyboard = [[InlineKeyboardButton("Join our Telegram channel", url=JOIN_BUTTON_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(f'Hi {user.first_name}, please join our Telegram channel.', reply_markup=reply_markup)

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it the bot's token.
    updater = Updater(BOT_TOKEN)
    ...

# Get the dispatcher to register handlers.
dispatcher = updater.dispatcher

# Add command handlers.
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('setdeletiontime', set_deletion_time))
dispatcher.add_handler(CommandHandler('getusers', get_users))
dispatcher.add_handler(CommandHandler('broadcast', broadcast))

# Add message handler to delete messages.
dispatcher.add_handler(MessageHandler(Filters.all, delete_message))

# Add join channel handler.
dispatcher.add_handler(CommandHandler('joinchannel', join_channel))

# Start the bot.
updater.start_polling()

# Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT.
updater.idle()

main()
