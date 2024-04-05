import asyncio
import random

import discord
import httpx
from discord.ext import commands
from discord import app_commands
import settings

logger = settings.LOGGER


class Fun(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Greeting Command
    @app_commands.command(name="chuckfact", description="Get a random Chuck Norris fact")
    async def chuck_fact(self, interaction: discord.Interaction):
        async with httpx.AsyncClient() as client:
            response = await client.get('https://api.chucknorris.io/jokes/random')
            if response.status_code == 200:
                data = response.json()
                await interaction.response.send_message(data['value'])
            else:
                await interaction.response.send_message(
                    "Oops! Could not retrieve a Chuck Norris fact. Please try again.")

    @app_commands.command(name="corporatebs", description="Get a random corporate buzzword phrase")
    async def corporate_bs(self, interaction: discord.Interaction):
        # Acknowledge the interaction immediately
        await interaction.response.defer()

        async with httpx.AsyncClient() as client:
            response = await client.get('https://corporatebs-generator.sameerkumar.website/')
            if response.status_code == 200:
                data = response.json()
                # Use followup.send instead of response.send_message
                await interaction.followup.send(data['phrase'])
            else:
                # Use followup.send in case of an error too
                await interaction.followup.send("Oops! Could not retrieve corporate wisdom. Please try again.")

    @app_commands.command(name="yomomma", description="Get a random 'Yo Momma' joke")
    async def yo_momma(self, interaction: discord.Interaction):
        async with httpx.AsyncClient() as client:
            response = await client.get('https://yomomma-api.herokuapp.com/jokes')
            if response.status_code == 200:
                data = response.json()
                joke = data['joke']
                await interaction.response.send_message(joke)
            else:
                await interaction.response.send_message(
                    "Oops! Couldn't fetch a 'Yo Momma' joke. Please try again later.")

    async def fetch_comic_data(self, comic_id=""):
        url = f"https://xkcd.com/{comic_id}/info.0.json" if comic_id else "https://xkcd.com/info.0.json"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                return None

    @app_commands.command(name="xkcd", description="Get an XKCD comic")
    async def xkcd(self, interaction: discord.Interaction, comic_id: str = "random"):
        if comic_id == "random":
            latest_comic_data = await self.fetch_comic_data()
            latest_comic_id = latest_comic_data['num'] if latest_comic_data else 1
            comic_id = random.randint(1, latest_comic_id)

        comic_data = await self.fetch_comic_data(str(comic_id))
        if comic_data:
            embed = discord.Embed(title=comic_data['title'], url=f"https://xkcd.com/{comic_data['num']}/",
                                  color=discord.Color.blue())
            embed.set_image(url=comic_data['img'])
            embed.set_footer(text=comic_data['alt'])
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Failed to retrieve the XKCD comic. Please try again later.")

    @app_commands.command(name="trumpquote", description="Fetch a random Trump quote")
    async def trump_quote(self, interaction: discord.Interaction):
        async with httpx.AsyncClient() as client:
            response = await client.get('https://api.tronalddump.io/random/quote')
            if response.status_code == 200:
                data = response.json()
                quote = data['value']
                embed = discord.Embed(title="Random Trump Quote", description=quote, color=discord.Color.orange())
                embed.set_footer(text="Source: Tronald Dump API")
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("Failed to fetch a quote. Please try again later.")

    def create_wanted_embed(self, person):
        embed = discord.Embed(title=person['title'], description=person.get('description', 'No description available.'),
                              color=discord.Color.red())
        if 'images' in person and person['images']:
            embed.set_image(url=person['images'][0]['original'])
        if 'reward_text' in person:
            embed.add_field(name="Reward", value=person['reward_text'], inline=False)
        if 'details' in person:
            embed.add_field(name="Details", value=person['details'], inline=False)
        if 'url' in person:
            embed.add_field(name="More Information", value=person['url'], inline=False)
        return embed

    @app_commands.command(name="fbimostwanted", description="Get information about a random FBI's Most Wanted person")
    async def fbi_most_wanted(self, interaction: discord.Interaction):
        # Defer the response to get more time for processing
        await interaction.response.defer()

        api_url = "https://api.fbi.gov/wanted/v1/list"
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url)
            if response.status_code == 200:
                data = response.json()
                items = data['items']
                if items:
                    # Select a random wanted person
                    person = random.choice(items)
                    embed = self.create_wanted_embed(person)
                    # Use 'followup.send' instead of 'send_message' after deferring
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send("No wanted persons could be found at the moment.")
            else:
                await interaction.followup.send("Failed to retrieve information. Please try again later.")

    @app_commands.command(name="insult", description="Generate a random evil insult.")
    async def insult(self, interaction: discord.Interaction):
        async with httpx.AsyncClient() as client:
            response = await client.get('https://evilinsult.com/generate_insult.php?lang=en&type=json')
            if response.status_code == 200:
                data = response.json()
                await interaction.response.send_message(data['insult'])
            else:
                await interaction.response.send_message("Failed to retrieve an insult. Please try again later.")

    @app_commands.command(name="kanyequote", description="Get a random Kanye West quote.")
    async def kanye_quote(interaction: discord.Interaction):
        retries = 3
        for attempt in range(retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get('https://api.kanye.rest', timeout=10.0)  # Added timeout
                    if response.status_code == 200:
                        data = response.json()
                        await interaction.response.send_message(data['quote'])
                        break  # Break out of the loop if successful
                    else:
                        await interaction.response.send_message(
                            "Failed to retrieve a Kanye quote. Please try again later.")
                        break  # Exit if the API returns a non-200 status code
            except httpx.RequestError as e:
                if attempt < retries - 1:  # With retries, don't wait on the last attempt
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    await interaction.response.send_message(
                        f"Failed to retrieve a Kanye quote due to a connection error: {e}. Please try again later.")

    @app_commands.command(name="quote", description="Get a random inspirational quote.")
    async def quote(self, interaction: discord.Interaction):
        async with httpx.AsyncClient() as client:
            response = await client.get('https://quote-garden.herokuapp.com/api/v3/quotes/random')
            if response.status_code == 200:
                data = response.json()
                quote_data = data['data'][0]  # Access the quote data
                quote = quote_data['quoteText']
                author = quote_data['quoteAuthor']
                message = f"\"{quote}\" \n- **{author}**"
                await interaction.response.send_message(message)
            else:
                await interaction.response.send_message("Failed to retrieve a quote. Please try again later.")

    @app_commands.command(name="apod", description="Get NASA's Astronomy Picture of the Day.")
    async def apod(self, interaction: discord.Interaction):
        url = f"https://api.nasa.gov/planetary/apod?api_key={settings.NASA_API_KEY}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                embed = discord.Embed(title=data['title'], description=data['explanation'], color=discord.Color.blue())
                embed.set_image(url=data['url'])
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("Failed to retrieve the Astronomy Picture of the Day.")

    @app_commands.command(name="marsrover", description="Get the latest Mars Rover photo.")
    @app_commands.choices(rover=[
        app_commands.Choice(name="Curiosity", value="curiosity"),
        app_commands.Choice(name="Opportunity", value="opportunity"),
        app_commands.Choice(name="Spirit", value="spirit"),
    ])
    async def mars_rover(self, interaction: discord.Interaction, rover: app_commands.Choice[str]):
        url = f"https://api.nasa.gov/mars-photos/api/v1/rovers/{rover.value}/latest_photos?api_key={settings.NASA_API_KEY}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                latest_photos = data['latest_photos']
                if latest_photos:
                    photo = latest_photos[0]
                    embed = discord.Embed(title=f"Latest photo from {rover.name}", color=discord.Color.red())
                    embed.set_image(url=photo['img_src'])
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message(f"No photos found for {rover.name}.")
            else:
                await interaction.response.send_message(f"Failed to retrieve photos for {rover.name}.")

    @app_commands.command(name="nextlaunch", description="Get information about the next SpaceX launch.")
    async def next_launch(self, interaction: discord.Interaction):
        async with httpx.AsyncClient() as client:
            response = await client.get('https://api.spacexdata.com/v4/launches/next')
            if response.status_code == 200:
                data = response.json()
                embed = discord.Embed(title="Next SpaceX Launch", description=data['name'], color=discord.Color.blue())
                embed.add_field(name="Details", value=data['details'] if data['details'] else "Details not available.",
                                inline=False)
                embed.add_field(name="Date", value=data['date_utc'], inline=True)
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("Failed to retrieve the next launch information.")

    @app_commands.command(name="latestlaunch", description="Get information about the latest SpaceX launch.")
    async def latest_launch(self, interaction: discord.Interaction):
        async with httpx.AsyncClient() as client:
            response = await client.get('https://api.spacexdata.com/v4/launches/latest')
            if response.status_code == 200:
                data = response.json()
                embed = discord.Embed(title="Latest SpaceX Launch", description=data['name'],
                                      color=discord.Color.green())
                embed.add_field(name="Details", value=data['details'] if data['details'] else "Details not available.",
                                inline=False)
                embed.add_field(name="Date", value=data['date_utc'], inline=True)
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("Failed to retrieve the latest launch information.")

    @app_commands.command(name="rocketinfo", description="Get information about a SpaceX rocket.")
    @app_commands.choices(rocket=[
        app_commands.Choice(name="Falcon 1", value="5e9d0d95eda69955f709d1eb"),
        app_commands.Choice(name="Falcon 9", value="5e9d0d95eda69973a809d1ec"),
        app_commands.Choice(name="Falcon Heavy", value="5e9d0d95eda69974db09d1ed"),
        app_commands.Choice(name="Starship", value="5e9d0d96eda699382d09d1ee"),
    ])
    async def rocket_info(self, interaction: discord.Interaction, rocket: app_commands.Choice[str]):
        async with httpx.AsyncClient() as client:
            response = await client.get(f'https://api.spacexdata.com/v4/rockets/{rocket.value}')
            if response.status_code == 200:
                data = response.json()
                embed = discord.Embed(title=data['name'], description=data['description'], color=discord.Color.orange())
                embed.set_image(url=data['flickr_images'][0] if data['flickr_images'] else discord.Embed.Empty)
                embed.add_field(name="First Flight", value=data['first_flight'], inline=True)
                embed.add_field(name="Country", value=data['country'], inline=True)
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(f"Failed to retrieve information for {rocket.name}.")

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"{self.__class__.__name__} cog has been loaded.")

async def setup(bot):
    await bot.add_cog(Fun(bot))
    await bot.tree.sync()
