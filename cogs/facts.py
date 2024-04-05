import csv
import datetime
import random

import discord
import httpx
from discord.ext import commands
from discord import app_commands
import settings

logger = settings.LOGGER


class Facts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._synced = False  # Prevents multiple syncs in case of reconnections

    async def cog_load(self):
        # Placeholder for any specific cog initialization if needed
        pass

    @app_commands.command(name="fact", description="Get a Random Fact")
    async def fact(self, interaction: discord.Interaction):
        facts_file_path = settings.RESOURCES_DIR / "facts.csv"
        with open(facts_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            chosen_row = random.choice(list(reader))
        await interaction.response.send_message(f"**{chosen_row['category']}**: {chosen_row['fact']}")

    @app_commands.command(name="onthisday", description="Get an 'On this Day' Fact")
    async def onthisday(self, interaction: discord.Interaction):
        today = (datetime.date.today().strftime("%m/%d"))
        fact_found = False
        facts_file_path = settings.RESOURCES_DIR / "facts_by_date.csv"
        with open(facts_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['date'] == today:
                    await interaction.response.send_message(f"**{row['theme']}**: {row['fact']}")
                    fact_found = True
                    break
        if not fact_found:
            await interaction.response.send_message("No fact found for today.")

    @app_commands.command(name="uselessfact", description="Generates a random useless fact")
    async def useless_fact(self, interaction: discord.Interaction):
        async with httpx.AsyncClient() as client:
            response = await client.get('https://uselessfacts.jsph.pl/random.json?language=en')
            if response.status_code == 200:
                data = response.json()
                fact = data['text']
                await interaction.response.send_message(f"Did you know? {fact}")
            else:
                await interaction.response.send_message("Oops! Could not retrieve a fact. Please try again later.")

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"{self.__class__.__name__} cog has been loaded.")
async def setup(bot):
    await bot.add_cog(Facts(bot))
    await bot.tree.sync()
