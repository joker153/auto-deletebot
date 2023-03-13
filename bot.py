import os
import time
import pyrogram
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# TELEGRAM API CONFIGURATION
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# BOT CONFIGURATION
AUTH_CHANNEL = int(os.environ.get("AUTH_CHANNEL"))
DELETE_TIME = 300  # seconds (5 minutes)

# CREATE A NEW PYROGRAM CLIENT INSTANCE
app = Client(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# HANDLE THE "/start" COMMAND
@app.on_message(filters.command("start"))
def start_command(client: Client, message: Message):
    # SEND A WELCOME MESSAGE
    message.reply_text("Hello! Please add me to a group so I can delete messages there.")

# HANDLE MESSAGES IN A GROUP CHAT
@app.on_message(filters.group & ~filters.edited)
def group_message(client: Client, message: Message):
    if message.chat.id == AUTH_CHANNEL:
        # SAVE THE MESSAGE ID AND TIMESTAMP FOR FUTURE USE
        message_info = {
            "chat_id": message.chat.id,
            "message_id": message.message_id,
            "timestamp": time.time()
        }

        # STORE THE MESSAGE INFO IN A LIST
        client._message_infos = client._message_infos[:10] + [message_info]

        # ADD A CUSTOM "DELETE" BUTTON TO THE MESSAGE
        button = InlineKeyboardButton(
            text="Delete",
            callback_data=f"delete_{message.chat.id}_{message.message_id}"
        )
        markup = InlineKeyboardMarkup([[button]])

        # SEND THE MESSAGE WITH THE CUSTOM BUTTON
        client.send_message(
            chat_id=message.chat.id,
            text=message.text,
            reply_markup=markup
        )

# HANDLE BUTTON CLICKS
@app.on_callback_query()
def handle_callback(client: Client, callback_query: Message):
    if "delete" in callback_query.data:
        # GET THE CHAT ID AND MESSAGE ID FROM THE CALLBACK DATA
        chat_id, message_id = map(int, callback_query.data.split("_")[1:3])

        # CHECK IF THE USER IS AUTHORIZED TO DELETE MESSAGES
        if callback_query.from_user.id != AUTH_CHANNEL:
            callback_query.answer("You are not authorized to perform this action!")
            return

        # DELETE THE MESSAGE
        client.delete_messages(chat_id=chat_id, message_ids=message_id)

        # ANSWER THE CALLBACK QUERY
        callback_query.answer("Message deleted successfully!")

# START THE BOT
app.start()

# PERIODICALLY DELETE OLD MESSAGES
while True:
    now = time.time()
    for message_info in app._message_infos:
        if now - message_info["timestamp"] > DELETE_TIME:
            # DELETE THE MESSAGE
            app.delete_messages(chat_id=message_info["chat_id"], message_ids=message_info["message_id"])

            # REMOVE THE MESSAGE INFO FROM THE LIST
            app._message_infos.remove(message_info)

    # WAIT FOR A MINUTE BEFORE CHECKING AGAIN
    time.sleep(60)
