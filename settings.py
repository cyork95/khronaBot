import os
import logging
import pathlib
import discord
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler

load_dotenv()

DISCORD_API_SECRET = os.getenv("DISCORD_API_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
THE_CAT_API_KEY = os.getenv("THE_CAT_API_KEY")
RECIPE_APP_ID = os.getenv("RECIPE_APP_ID")
RECIPE_API_KEY = os.getenv("RECIPE_API_KEY")
HUMBLE_BUNDLE_RAPIDAPI_KEY = os.getenv("HUMBLE_BUNDLE_RAPIDAPI_KEY")
HUMBLE_BUNDLE_RAPIDAPI_HOST = os.getenv("HUMBLE_BUNDLE_RAPIDAPI_HOST")
POKEMON_TCG_API_KEY = os.getenv("POKEMON_TCG_API_KEY")
NASA_API_KEY=os.getenv("NASA_API_KEY")
BASE_DIR = pathlib.Path(__file__).parent
COGS_DIR = BASE_DIR / "cogs"
RESOURCES_DIR = BASE_DIR / "resources"

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
