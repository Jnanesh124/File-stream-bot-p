import re
from os import environ

id_pattern = re.compile(r'^.\d+$')

# Ensure AUTH_CHANNEL and SECOND_AUTH_CHANNEL are set correctly
AUTH_CHANNEL = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('AUTH_CHANNEL', '-1001764441595').split()]
SECOND_AUTH_CHANNEL = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('SECOND_AUTH_CHANNEL', '-1002135593873').split()]  # Replace with your second channel ID
print(f"AUTH_CHANNEL IDs: {AUTH_CHANNEL}")  # Debugging line
print(f"SECOND_AUTH_CHANNEL IDs: {SECOND_AUTH_CHANNEL}")  # Debugging line

# Bot information
SESSION = environ.get('SESSION', 'TechVJBot')
API_ID = int(environ.get('API_ID', '21942125'))
API_HASH = environ.get('API_HASH', '6d412af77ce89f5bb1ed8971589d61b5')
BOT_TOKEN = environ.get('BOT_TOKEN', "7774713343:AAHJYTcuEa-20YCJDoMpiwkL2EViZdifRp4")

# Bot settings
PORT = environ.get("PORT", "8080")

# Online Stream and Download
MULTI_CLIENT = False
SLEEP_THRESHOLD = int(environ.get('SLEEP_THRESHOLD', '60'))
PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))  # 20 minutes
ON_HEROKU = 'DYNO' in environ

URL = environ.get("URL", "https://streembot-009a426ab9b2.herokuapp.com/")

# Admins, Channels & Users
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '-1002225559950'))
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '6643562770').split()]

# MongoDB information
DATABASE_URI = environ.get('DATABASE_URI', "mongodb+srv://strong:strong@cluster0.ix7usa3.mongodb.net/?retryWrites=true&w=majority")
DATABASE_NAME = environ.get('DATABASE_NAME', "techvjautobot")

# Shortlink Info
SHORTLINK = bool(environ.get('SHORTLINK', False))  # Set True Or False
SHORTLINK_URL = environ.get('SHORTLINK_URL', 'api.shareus.io')
SHORTLINK_API = environ.get('SHORTLINK_API', 'hRPS5vvZc0OGOEUQJMJzPiojoVK2')
