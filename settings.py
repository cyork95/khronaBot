from dotenv import load_dotenv
import os

load_dotenv()

DISCORD_API_SECRET = os.getenv("DISCORD_API_TOKEN")