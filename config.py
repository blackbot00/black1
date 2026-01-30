import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Private group (LOG GROUP)
LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID"))
