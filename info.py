import re
from os import environ

# Regular expression to validate ID patterns
id_pattern = re.compile(r'^-?[0-9]+$')

# Primary and secondary force subscription channels
AUTH_CHANNEL = int(environ.get('AUTH_CHANNEL', '-1002147557168')) if id_pattern.search(environ.get('AUTH_CHANNEL', '-1001764441595')) else environ.get('AUTH_CHANNEL', '-1001764441595')
SECOND_AUTH_CHANNEL = int(environ.get('SECOND_AUTH_CHANNEL', '-1002135593873')) if id_pattern.search(environ.get('SECOND_AUTH_CHANNEL', '-1002135593873')) else environ.get('SECOND_AUTH_CHANNEL', '-1002135593873')

# Debugging logs to verify channel IDs
print(f"AUTH_CHANNEL IDs: {AUTH_CHANNEL}")  # Primary channel(s)
print(f"SECOND_AUTH_CHANNEL IDs: {SECOND_AUTH_CHANNEL}")  # Secondary channel(s)

# Bot session and authentication details
SESSION = environ.get('SESSION', 'TechVJBot')
API_ID = int(environ.get('API_ID', '21125'))
API_HASH = environ.get('API_HASH', '6d4121b5')
BOT_TOKEN = environ.get('BOT_TOKEN', "7774fRp4")

# Bot hosting settings
PORT = environ.get("PORT", "8080")
URL = environ.get("URL", "https:/kuapp.com/")
ON_HEROKU = 'DYNO' in environ

# Logging and admin details
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '-1002415621521'))
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '6605647659').split()]

# MongoDB database details
DATABASE_URI = environ.get('DATABASE_URI', "ms=true&w=majority")
DATABASE_NAME = environ.get('DATABASE_NAME', "techvjautobot")

# Bot features and additional configurations
MULTI_CLIENT = False
SLEEP_THRESHOLD = int(environ.get('SLEEP_THRESHOLD', '60'))
PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))  # 20 minutes

# Shortlink configurations
SHORTLINK = bool(environ.get('SHORTLINK', False))  # Set True Or False
SHORTLINK_URL = environ.get('SHORTLINK_URL', 'api.shareus.io')
SHORTLINK_API = environ.get('SHORTLINK_API', 'hRPS5vvZc0OGOEUQJMJzPiojoVK2')
