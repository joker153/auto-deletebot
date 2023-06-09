import os
import time
import pyrogram
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# Telegram API configuration
api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
bot_token = os.environ.get("BOT_TOKEN")

# Bot configuration
auth_channel = int(os.environ.get("AUTH_CHANNEL"))
delete_time = 300  # seconds (5 minutes)

# Create a new Pyrogram Client instance
app = Client(
    "my_bot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)

# Initialize the message infos list
app._message_infos = []

# Handle the "/start" command
@app.on_message(filters.private & filters.command("start"))
def start_command(client: Client, message: Message):
    # Send a welcome message
    message.reply_text(f"Hello {message.from_user.mention}! Please add me to a group so I can delete messages there.")

# Handle the "/settings" command
@app.on_message(filters.private & filters.command("settings"))
def settings_command(client: Client, message: Message):
    # Send a message with custom deletion time buttons
    button_1 = InlineKeyboardButton(text="1 minute", callback_data="delete_60")
    button_2 = InlineKeyboardButton(text="5 minutes", callback_data="delete_300")
    button_3 = InlineKeyboardButton(text="10 minutes", callback_data="delete_600")
    markup = InlineKeyboardMarkup([[button_1], [button_2], [button_3]])
    message.reply_text("Select the custom deletion time:", reply_markup=markup)

# Handle messages in a group chat
@app.on_message(filters.group & ~filters.edited)
def group_message(client: Client, message: Message):
    if message.chat.id == auth_channel:
        # Save the message ID and timestamp for future use
        message_info = {
            "chat_id": message.chat.id,
            "message_id": message.message_id,
            "timestamp": time.time()
        }

        # Store the message info in a list
        client._message_infos = client._message_infos[:10] + [message_info]

        # Add a custom "Delete" button to the message
        button = InlineKeyboardButton(
            text="Delete",
            callback_data=f"delete_{message.chat.id}_{message.message_id}"
        )
        markup = InlineKeyboardMarkup([[button]])

        # Send the message with the custom button
        client.send_message(
            chat_id=message.chat.id,
            text=message.text,
            reply_markup=markup
        )

# Handle button clicks
@app.on_callback_query()
def handle_callback(client: Client, callback_query: Message):
    if "delete" in callback_query.data:
        # Get the chat ID and message ID from the callback data
        chat_id, message_id = map(int, callback_query.data.split("_")[1:3])

        # Get the custom deletion time from the callback data
        delete_time = int(callback_query.data.split("_")[3])

        # Check if the user is authorized to delete messages
        if callback_query.from_user.id != auth_channel:
            callback_query.answer("You are not authorized to perform this action!")
            return

        # Delete the message
        client.delete_messages(chat_id=chat_id, message_ids=message_id)

        # Answer the callback query
        callback_query.answer("Message deleted successfully!")

# Start the bot
app.start()

# Periodically delete old messages
while True:
    now = time.time()
    for message_info in app._message_infos:
        if now - message_info["timestamp"] > delete_time:
            # Delete the message
            app.delete_messages(chat_id=message_info["chat_id"], message_ids=message_info["message_id"])

            # Remove the message info from the list
            app._message_infos.remove(message_info)

    # Wait for a minute before checking again
    time.sleep(60)
