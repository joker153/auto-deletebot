from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import os
import time

# Your API ID and API hash
API_ID = int(os.environ.get("API_ID", ""))
API_HASH = os.environ.get("API_HASH", "")

# Your Bot Token
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# ID of the authorized channel
AUTH_CHANNEL = int(os.environ.get("AUTH_CHANNEL", ""))

# Create a Pyrogram client instance
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Function to check if user is authorized to use the bot
def is_authorized(chat_id):
    try:
        member = app.get_chat_member(chat_id=AUTH_CHANNEL, user_id=chat_id)
        if member.status == 'member' or member.status == 'creator' or member.status == 'administrator':
            return True
        else:
            return False
    except Exception as e:
        return False

# Function to delete messages
def delete_message(client, message):
    if message.chat.type != 'private' and is_authorized(message.chat.id):
        message.delete()

# Command to start the bot
@app.on_message(filters.command("start"))
def start(client, message):
    # Check if user is authorized
    if not is_authorized(message.chat.id):
        message.reply_text("You are not authorized to use this bot. Please join the authorized channel first.")
        return
    # Send a message with instructions
    message.reply_text("Add me to a group and give me permission to delete messages. I will automatically delete all messages in the group after 5 minutes.")

# Handler to delete messages
@app.on_message(filters.group & ~filters.edited)
def delete_messages(client, message):
    if message.chat.type != 'private' and is_authorized(message.chat.id):
        # Schedule message deletion after 5 minutes
        client.scheduler.schedule(300, delete_message, message=message)

# Custom delete button in PM settings
@app.on_callback_query()
def custom_delete_button(client, callback_query):
    if callback_query.data == "delete":
        callback_query.message.delete()

# Start the bot
app.run()
