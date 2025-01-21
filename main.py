import logging
from pyrogram import Client, errors, enums
from flask import Flask, request, jsonify
import threading
import re
from collections import OrderedDict
import asyncio
from typing import Union, Dict

# Initialize Flask app
vj = Flask(__name__)

# Set up the logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
    ]
)

# Pyrogram client configuration
API_ID = "26183755"  # Replace with your actual API ID
API_HASH = "7b7cfa427476172beb5ef3815209b747"  # Replace with your actual API Hash
BOT_TOKEN = "7879344121:AAF2_RTxClSdGX32jfo8OalF2zY-4x89Nvo"  # Replace with your bot token

app = Client(
    name="my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

async def get_chat_details(client: Client, username: str) -> Dict[str, Union[str, int]]:
    """Get chat details by username and provide a detailed response."""
    # Validate the username format using a regex
    username_regex = r"(?:@|t\.me\/|https:\/\/t\.me\/)([a-zA-Z][a-zA-Z0-9_]{2,})"
    match = re.match(username_regex, username)

    if not match:
        return OrderedDict([
            ("status", "false"),
            ("error", "Invalid username format."),
        ])

    username = match.group(1)

    try:
        # Fetch the chat info
        chat = await client.get_chat(username)
        print(chat)
        # Organize chat details
        response = OrderedDict([
            ("status", "true"),
            ("chat_id", chat.id),
            ("chat_type", chat.type.value if chat.type else "unknown"),
            ("name", chat.title or chat.first_name or chat.username or "N/A"),
            ("username", chat.username or "N/A"),
            ("bio", getattr(chat, "bio", "N/A")),
            ("is_verified", chat.is_verified),
            ("is_restricted", chat.is_restricted),
            ("is_scam", chat.is_scam),
            ("is_fake", chat.is_fake),
            ("is_support", chat.is_support),
            # ("is_premium", getattr(chat, "is_premium", False)),
            ("profile_photo", {
                "small_file_id": getattr(chat.photo, "small_file_id", None),
                "big_file_id": getattr(chat.photo, "big_file_id", None),
            } if chat.photo else "N/A"),
            ("dc_id", chat.dc_id),
            ("phone_number", getattr(chat, "phone_number", "N/A")),
            ("language_code", getattr(chat, "language_code", "N/A")),
        ])

        # Add additional information for groups, channels, etc.
        if chat.type in [enums.ChatType.CHANNEL, enums.ChatType.SUPERGROUP, enums.ChatType.GROUP]:
            response.update({
                "is_creator": getattr(chat, "is_creator", False),
                "is_forum": getattr(chat, "is_forum", False),
                "has_protected_content": getattr(chat, "has_protected_content", False),
                "member_count": getattr(chat, "members_count", "N/A"),
                "slowmode_enabled": getattr(chat, "is_slowmode_enabled", False),
            })

        return response

    except errors.UsernameNotOccupied:
        return OrderedDict([
            ("status", "false"),
            ("error", "Username not in use."),
        ])
    except errors.UsernameInvalid:
        return OrderedDict([
            ("status", "false"),
            ("error", "Invalid username."),
        ])
    except errors.BadRequest as e:
        return OrderedDict([
            ("status", "false"),
            ("error", f"Bad request: {str(e)}"),
        ])
    except Exception as e:
        logging.error(f"Error fetching chat: {e}")
        return OrderedDict([
            ("status", "false"),
            ("error", "An error occurred."),
        ])

@vj.route('/', methods=['GET'])
def get_user_id():
    """Flask route to handle username to ID conversion."""
    username = request.args.get('username')

    if not username:
        return jsonify(OrderedDict([
            ("status", "false"),
            ("error", "Username is required"),
        ])), 400

    try:
        loop = app.loop
        future = asyncio.run_coroutine_threadsafe(
            get_chat_details(app, username), loop
        )
        chat_info = future.result()

        return jsonify(chat_info)

    except RuntimeError:
        logging.error("No running event loop found.")
        return jsonify(OrderedDict([
            ("status", "false"),
            ("error", "Internal server error"),
        ])), 500
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return jsonify(OrderedDict([
            ("status", "false"),
            ("error", "Internal server error"),
        ])), 500

def run_flask():
    """Function to start the Flask server."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 8000, vj, use_reloader=False, use_debugger=False)

def main():
    """Main function to start both Flask and Pyrogram client."""
    loop = asyncio.get_event_loop()

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    try:
        logging.info("Starting the Pyrogram client...")
        app.start()
        logging.info("Pyrogram client started successfully.")
        loop.run_forever()
    except Exception as e:
        logging.error(f"Error during Pyrogram client startup: {e}")
    finally:
        app.stop()
        logging.info("Pyrogram client stopped.")

if __name__ == "__main__":
    main()
