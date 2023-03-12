import os
import time
from pyrogram import Client, filters

app = Client(
    "my_bot",
    api_id=os.environ.get("API_ID"),
    api_hash=os.environ.get("API_HASH"),
    bot_token=os.environ.get("BOT_TOKEN")
)

# Define the source groups and destination channel IDs
source_group_ids = [-123456789, -987654321]  # Replace with the source group IDs
destination_channel_id = "@my_channel"  # Replace with the destination channel ID

# Define the time interval (in seconds) for copying the members
copy_interval = 60 * 60  # Copy members every hour

# Define the function to join the source groups and copy all members to the destination channel
def copy_all_members():
    for group_id in source_group_ids:
        try:
            # Join the group
            app.join_chat(group_id)
            print(f"Joined {group_id}")

            # Get all members of the group
            members = app.get_chat_members(group_id)

            # Add each member to the destination channel
            for member in members:
                if member.user.is_bot:
                    continue  # Skip bots
                app.add_chat_members(chat_id=destination_channel_id, user_ids=member.user.id)
                print(f"Copied {member.user.first_name} from {group_id} to {destination_channel_id}")
        except Exception as e:
            print(f"Failed to copy members from {group_id}: {e}")

# Define the function to run the copying process at a specified time interval
def run_copy_process():
    while True:
        copy_all_members()
        time.sleep(copy_interval)

# Start the bot and run the copying process at a specified time interval
with app:
    app.send_message(
        chat_id=app.get_me().id, 
        text="Please subscribe to our channel to use this bot.",
        disable_notification=True
    )
    @app.on_message(filters.command("start") & filters.private)
    def start(bot, update):
        bot.send_message(
            chat_id=update.chat.id,
            text="Please subscribe to our channel to use this bot.",
            disable_notification=True
        )
    app.join_chat(destination_channel_id)
    run_copy_process()
    app.idle()
