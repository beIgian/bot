import os
from dotenv import load_dotenv

load_dotenv()

# Your bot's token, from the Bot tab of the Discord Developer Portal
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Your application's Client ID and Client Secret, from the OAuth2 tab
CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")

# Must EXACTLY match a Redirect URI you added in the OAuth2 tab,
# e.g. https://yourdomain.com/callback or http://localhost:5000/callback
REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI", "http://localhost:5000/callback")

# Prefix for text commands like ,memberlist and ,pull
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", ",")

# Path to the SQLite database file (shared between the bot and the OAuth server)
DATABASE_PATH = os.getenv("DATABASE_PATH", "verified_members.db")

# Embed sidebar color used on every reply (hex, no leading #)
EMBED_COLOR = 0x000600

DISCORD_API_BASE = "https://discord.com/api/v10"
OAUTH_SCOPES = "identify guilds.join"
