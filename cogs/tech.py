import discord
import httpx
from discord.ext import commands
from discord import app_commands
from httpx import ReadTimeout

import settings

logger = settings.LOGGER


class Tech(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="techjoke", description="Gets a random tech joke")
    async def tech_joke(self, interaction: discord.Interaction):
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get('https://techy-api.vercel.app/api/json')
                if response.status_code == 200:
                    data = response.json()
                    joke = data['joke']
                    await interaction.response.send_message(joke)
                else:
                    await interaction.response.send_message("Oops! Couldn't fetch a tech joke. Please try again later.")
            except httpx.RequestError as e:
                await interaction.response.send_message(
                    "Sorry, I'm having trouble fetching jokes at the moment. Please try again later.")
                logger.warn(f"An error occurred in the Tech Joke API: {e}")  # Logging the error can help with debugging

    @app_commands.command(name="geekjoke", description="Get a random geek joke")
    async def geek_joke(self, interaction: discord.Interaction):
        async with httpx.AsyncClient() as client:
            response = await client.get('https://geek-jokes.sameerkumar.website/api?format=json')
            if response.status_code == 200:
                data = response.json()
                joke = data['joke']
                await interaction.response.send_message(joke)
            else:
                await interaction.response.send_message("Failed to fetch a geek joke. Please try again later.")

    @app_commands.command(name="progquote", description="Get a random programming quote.")
    async def prog_quote(self,interaction: discord.Interaction):
        timeout = httpx.Timeout(10.0, read=30.0)  # Sets a custom timeout (10 seconds connect, 30 seconds read)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get('https://programming-quotes-api.herokuapp.com/quotes/random')
                response.raise_for_status()  # This will directly raise an exception for HTTP error codes
                data = response.json()
                quote = data['en']
                author = data['author']
                message = f"\"{quote}\" - **{author}**"
                await interaction.response.send_message(message)
        except ReadTimeout:
            await interaction.response.send_message(
                "Request timed out. The server might be busy or down. Please try again later.")
        except httpx.HTTPStatusError as e:
            await interaction.response.send_message(
                f"Failed to retrieve a programming quote due to a network error: {e}. Please try again later.")

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"{self.__class__.__name__} cog has been loaded.")

async def setup(bot):
    await bot.add_cog(Tech(bot))
    await bot.tree.sync()
