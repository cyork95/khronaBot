import random

import discord
import httpx
from discord.ext import commands
from discord import app_commands
import settings

logger = settings.LOGGER


class Videogames(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="freegame", description="Get a random free game deal")
    async def free_game(self, interaction: discord.Interaction):
        async with httpx.AsyncClient() as client:
            # Fetching all giveaways
            response = await client.get('https://www.gamerpower.com/api/giveaways')
            if response.status_code == 200:
                giveaways = response.json()
                if giveaways:
                    # Selecting a random giveaway
                    random_giveaway = random.choice(giveaways)
                    embed = discord.Embed(title=random_giveaway['title'], url=random_giveaway['open_giveaway_url'], color=discord.Color.green())
                    embed.set_thumbnail(url=random_giveaway['thumbnail'])
                    embed.add_field(name="Type", value=random_giveaway['type'], inline=True)
                    embed.add_field(name="Platforms", value=random_giveaway['platforms'], inline=True)
                    embed.add_field(name="End Date", value=random_giveaway['end_date'] or "N/A", inline=True)
                    embed.add_field(name="Description", value=random_giveaway['description'], inline=False)
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message("No free game deals found at the moment.")
            else:
                await interaction.response.send_message("Failed to retrieve free game deals. Please try again later.")

    @app_commands.command(name="humblebundle", description="Get current Humble Bundle deals")
    async def humble_bundle(self, interaction: discord.Interaction):
        url = "https://Ziggoto-humble-bundle-v1.p.rapidapi.com/bundles"
        headers = {
            'x-rapidapi-host': settings.HUMBLE_BUNDLE_RAPIDAPI_HOST,
            'x-rapidapi-key': settings.HUMBLE_BUNDLE_RAPIDAPI_KEY
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                bundles = response.json()
                if bundles:
                    # Assuming the API returns a list of bundles, display the first one for simplicity
                    first_bundle = bundles[0]
                    embed = discord.Embed(title=first_bundle['name'], url=first_bundle['url'],
                                          description="Current Humble Bundle Deal", color=discord.Color.red())
                    embed.set_thumbnail(url=first_bundle['thumbnail'])
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message("No current Humble Bundle deals found.")
            else:
                await interaction.response.send_message(
                    "Failed to retrieve Humble Bundle deals. Please try again later.")

    def create_pokemon_embed(self, pokemon_data):
        name = pokemon_data['name'].capitalize()
        pokemon_id = pokemon_data['id']
        types = ', '.join(t['type']['name'].capitalize() for t in pokemon_data['types'])
        weight = pokemon_data['weight'] / 10  # The weight is in hectograms
        height = pokemon_data['height'] / 10  # The height is in decimeters

        embed = discord.Embed(title=f"{name} (#{pokemon_id})", color=discord.Color.red())
        embed.add_field(name="Type(s)", value=types, inline=True)
        embed.add_field(name="Weight", value=f"{weight} kg", inline=True)
        embed.add_field(name="Height", value=f"{height} m", inline=True)
        embed.set_thumbnail(url=pokemon_data['sprites']['front_default'])

        return embed

    @app_commands.command(name="pokemon", description="Get information about a Pokémon")
    async def pokemon(self, interaction: discord.Interaction, name: str):
        url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                embed = self.create_pokemon_embed(data)
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(
                    f"Could not find information for Pokémon '{name}'. Please check the spelling and try again.")

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"{self.__class__.__name__} cog has been loaded.")

async def setup(bot):
    await bot.add_cog(Videogames(bot))
    await bot.tree.sync()
