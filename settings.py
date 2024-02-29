import os
import logging
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler

load_dotenv()

DISCORD_API_SECRET = os.getenv("DISCORD_API_TOKEN")

# Configure logging
LOGGER = logging.getLogger('discord')
LOGGER.setLevel(logging.INFO)  # Adjust to your logging level preference

# Create a file handler which logs even debug messages
fh = RotatingFileHandler('discord_bot.log', maxBytes=5*1024*1024, backupCount=5)
fh.setLevel(logging.INFO)  # Adjust to your logging level preference

# Create a formatter and set the formatter for the handler.
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

# Add the handler to the logger
LOGGER.addHandler(fh)
