import discord
import httpx
from discord.ext import commands
from discord import app_commands
import settings
import random
import requests

logger = settings.LOGGER


class Animals(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._synced = False  # Prevents multiple syncs in case of reconnections

    async def cog_load(self):
        # Placeholder for any specific cog initialization if needed
        pass

    @app_commands.command(name='axolotl', description='Sends axolotl pictures.')
    async def axolotl(self, interaction: discord.Interaction):
        # Fetching the axolotl image
        response = requests.get('https://theaxolotlapi.netlify.app/api/random')
        if response.status_code == 200:
            data = response.json()
            await interaction.response.send_message(content=data['url'])
        else:
            await interaction.response.send_message(content="Could not fetch an axolotl image. Please try again later.")

    @app_commands.command(name='catfact', description='Sends a random cat fact.')
    async def catfact(self, interaction: discord.Interaction):
        # Fetching a random cat fact
        response = requests.get('https://catfact.ninja/fact')
        if response.status_code == 200:
            data = response.json()
            await interaction.response.send_message(content=data['fact'])
        else:
            await interaction.response.send_message(content="Could not fetch a cat fact. Please try again later.")

    @app_commands.command(name='catimage', description='Sends a random cat image.')
    async def catimage(self, interaction: discord.Interaction):
        async with httpx.AsyncClient() as client:
            # Asynchronously fetching the cat image
            cat_image_url = 'https://cataas.com/cat?json=true'
            response = await client.get(cat_image_url)

            if response.status_code == 200:
                data = response.json()
                embed = discord.Embed(title="Random Cat Image")
                embed.set_image(url=f"https://cataas.com{data['url']}")
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(content="Could not fetch a cat image. Please try again later.")

    @app_commands.command(name='cat', description='Sends a random cat picture.')
    async def cat(self, interaction: discord.Interaction):
        headers = {'x-api-key': settings.THE_CAT_API_KEY}
        response = requests.get('https://api.thecatapi.com/v1/images/search', headers=headers)
        if response.status_code == 200:
            data = response.json()[0]  # Assuming we always get at least one image
            embed = discord.Embed(title="Random Cat")
            embed.set_image(url=data['url'])
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                content="Could not fetch a cat picture. Please try again later.")

    @app_commands.command(name='dogfact', description='Sends a random dog fact.')
    async def dogfact(self, interaction: discord.Interaction):
        # Fetching a random dog fact
        response = requests.get('https://dukengn.github.io/Dog-facts-API/api/v1/facts/?number=1')
        if response.status_code == 200:
            data = response.json()
            # Assuming the API always returns a list with at least one fact
            await interaction.response.send_message(content=data['facts'][0])
        else:
            await interaction.response.send_message(content="Could not fetch a dog fact. Please try again later.")

    @app_commands.command(name='dogimage', description='Sends a random dog image.')
    async def dogimage(self, interaction: discord.Interaction):
        # Fetching a random dog image
        response = requests.get('https://dog.ceo/api/breeds/image/random')
        if response.status_code == 200:
            data = response.json()
            embed = discord.Embed(title="Random Dog Image")
            embed.set_image(url=data['message'])  # The API returns the image URL in the 'message' field
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(content="Could not fetch a dog image. Please try again later.")

    @app_commands.command(name='duck', description='Sends a random duck image.')
    async def duck(self, interaction: discord.Interaction):
        # Fetching a random duck image
        response = requests.get('https://random-d.uk/api/v2/random')
        if response.status_code == 200:
            data = response.json()
            embed = discord.Embed(title="Quack! Here's a duck 🦆")
            embed.set_image(url=data['url'])  # 'url' field contains the image URL
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                content="Oops, couldn't fetch a duck image. Please try again later.")

    @app_commands.command(name='bear', description='Sends a bear image.')
    async def bear(self, interaction: discord.Interaction):
        # Here we define a fixed size for the bear images to simplify the command
        # You can modify this to accept user inputs for customizable sizes
        bear_image_url = 'https://placebear.com/640/480'
        embed = discord.Embed(title="Here's a bear for you 🐻")
        embed.set_image(url=bear_image_url)
        await interaction.response.send_message(embed=embed)


    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"{self.__class__.__name__} cog has been loaded.")


async def setup(bot):
    await bot.add_cog(Animals(bot))
    await bot.tree.sync()
