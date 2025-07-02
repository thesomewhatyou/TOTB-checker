import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Discord Bot Token (Required)
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not DISCORD_BOT_TOKEN:
    raise ValueError("Missing DISCORD_BOT_TOKEN in .env file")

# Discord Channel ID for announcements (Required)
DISCORD_CHANNEL_ID_STR = os.getenv("DISCORD_CHANNEL_ID")
if not DISCORD_CHANNEL_ID_STR:
    raise ValueError("Missing DISCORD_CHANNEL_ID in .env file")
try:
    DISCORD_CHANNEL_ID = int(DISCORD_CHANNEL_ID_STR)
except ValueError:
    raise ValueError("DISCORD_CHANNEL_ID must be an integer")

# Role ID to ping (Optional)
PING_ROLE_ID_STR = os.getenv("PING_ROLE_ID")
PING_ROLE_ID = None
if PING_ROLE_ID_STR:
    try:
        PING_ROLE_ID = int(PING_ROLE_ID_STR)
    except ValueError:
        print("Warning: PING_ROLE_ID is not a valid integer. It will be ignored.")
        # No need to raise error, it's optional

# User IDs to ping (Optional)
PING_USER_IDS_STR = os.getenv("PING_USER_IDS")
PING_USER_IDS = []
if PING_USER_IDS_STR:
    user_id_list = PING_USER_IDS_STR.split(',')
    for user_id in user_id_list:
        try:
            PING_USER_IDS.append(int(user_id.strip()))
        except ValueError:
            print(f"Warning: User ID '{user_id.strip()}' is not a valid integer. It will be ignored.")

# Log Level (Optional, defaults to INFO)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
VALID_LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
if LOG_LEVEL not in VALID_LOG_LEVELS:
    print(f"Warning: Invalid LOG_LEVEL '{LOG_LEVEL}'. Defaulting to INFO.")
    LOG_LEVEL = "INFO"

if __name__ == '__main__':
    # This part is for quick testing of the config loading
    print(f"Bot Token: {'*' * (len(DISCORD_BOT_TOKEN) - 4) + DISCORD_BOT_TOKEN[-4:] if DISCORD_BOT_TOKEN else 'Not Set'}")
    print(f"Channel ID: {DISCORD_CHANNEL_ID}")
    print(f"Ping Role ID: {PING_ROLE_ID if PING_ROLE_ID else 'Not Set'}")
    print(f"Ping User IDs: {PING_USER_IDS if PING_USER_IDS else 'Not Set'}")
    print(f"Log Level: {LOG_LEVEL}")

    # Example of how other modules would import these:
    # from config import DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID
    # print(DISCORD_BOT_TOKEN)
