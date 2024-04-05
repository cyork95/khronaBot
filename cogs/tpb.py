import csv
import datetime
import random

import discord
from discord.ext import commands
from discord import app_commands
import settings

logger = settings.LOGGER


class Tpb(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._synced = False  # Prevents multiple syncs in case of reconnections

    async def cog_load(self):
        # Placeholder for any specific cog initialization if needed
        pass

    @app_commands.command(name="tpb", description="Get a Random Quote from TPB!")
    async def tpb(self, interaction: discord.Interaction):
        quotes_file_path = settings.RESOURCES_DIR / "tpb_quotes.csv"
        with open(quotes_file_path, 'r') as file:
            reader = csv.DictReader(file)
            chosen_row = random.choice(list(reader))
        await interaction.response.send_message(f"**{chosen_row['character']}**: {chosen_row['quote']} \n*----{chosen_row['episode']}*")


    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"{self.__class__.__name__} cog has been loaded.")
async def setup(bot):
    await bot.add_cog(Tpb(bot))
    await bot.tree.sync()
