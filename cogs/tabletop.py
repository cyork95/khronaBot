import discord
import httpx
from discord.ext import commands
from discord import app_commands
import settings

logger = settings.LOGGER


class Tabletop(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def fetch_card_data(self, card_name):
        url = f"https://db.ygoprodeck.com/api/v7/cardinfo.php?name={card_name}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200 and response.json()["data"]:
                return response.json()["data"][0]  # Return the first match
            return None

    def create_card_embed(self, card_data):
        embed = discord.Embed(title=card_data['name'], color=discord.Color.dark_blue())
        if 'card_images' in card_data and card_data['card_images']:
            embed.set_image(url=card_data['card_images'][0]['image_url'])
        if 'desc' in card_data:
            embed.add_field(name="Description", value=card_data['desc'], inline=False)
        if 'type' in card_data:
            embed.add_field(name="Type", value=card_data['type'], inline=True)
        if 'atk' in card_data and 'def' in card_data:
            embed.add_field(name="ATK/DEF", value=f"{card_data['atk']}/{card_data['def']}", inline=True)
        if 'attribute' in card_data:
            embed.add_field(name="Attribute", value=card_data['attribute'], inline=True)
        return embed

    @app_commands.command(name="yugiohcard", description="Search for a Yu-Gi-Oh! card")
    async def yugioh_card(self, interaction: discord.Interaction, card_name: str):
        card_data = await self.fetch_card_data(card_name)
        if card_data:
            embed = self.create_card_embed(card_data)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Card not found. Please check the spelling and try again.")

    @app_commands.command(name="boardgame", description="Search for a board game on BoardGameGeek")
    async def board_game(self, interaction: discord.Interaction, search_query: str):
        search_url = f"https://www.boardgamegeek.com/xmlapi2/search?query={search_query}&type=boardgame"

        async with httpx.AsyncClient() as client:
            search_response = await client.get(search_url)
            if search_response.status_code == 200:
                # Parse XML search results
                root = ET.fromstring(search_response.content)
                if root.findall('item'):
                    # Assuming the first item is the most relevant
                    game_id = root.find('item').attrib['id']
                    game_details_url = f"https://www.boardgamegeek.com/xmlapi2/thing?id={game_id}"
                    details_response = await client.get(game_details_url)
                    if details_response.status_code == 200:
                        details_root = ET.fromstring(details_response.content)
                        game_info = details_root.find('item')
                        game_name = game_info.find("name").attrib['value']
                        year_published = game_info.find("yearpublished").attrib['value']

                        embed = discord.Embed(title=f"{game_name} ({year_published})", color=discord.Color.dark_blue())
                        embed.add_field(name="BGG Link", value=f"https://boardgamegeek.com/boardgame/{game_id}",
                                        inline=False)
                        await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message("No board games found. Try refining your search.")
            else:
                await interaction.response.send_message(
                    "Failed to retrieve board game information. Please try again later.")

    def create_magic_card_embed(self, card):
        embed = discord.Embed(title=card['name'], description=card.get('text', 'No description available.'),
                              color=discord.Color.dark_green())
        if 'imageUrl' in card:
            embed.set_image(url=card['imageUrl'])
        embed.add_field(name="Type", value=card.get('type', 'N/A'), inline=True)
        if 'setName' in card:
            embed.add_field(name="Set Name", value=card['setName'], inline=True)
        if 'rarity' in card:
            embed.add_field(name="Rarity", value=card['rarity'], inline=True)
        if 'manaCost' in card:
            embed.add_field(name="Mana Cost", value=card['manaCost'], inline=True)
        return embed

    @app_commands.command(name="mtgcard", description="Search for a Magic: The Gathering card")
    async def mtg_card(self, interaction: discord.Interaction, card_name: str):
        api_url = f"https://api.magicthegathering.io/v1/cards?name={card_name}"

        async with httpx.AsyncClient() as client:
            response = await client.get(api_url)
            if response.status_code == 200:
                cards = response.json()['cards']
                if cards:
                    card = cards[0]  # Assuming the first card is the most relevant
                    embed = self.create_magic_card_embed(card)
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message(f"No cards found matching '{card_name}'.")
            else:
                await interaction.response.send_message("Failed to retrieve card information. Please try again later.")

    def create_pokemon_card_embed(self, card):
        embed = discord.Embed(title=card['name'], description=f"Set: {card['set']['name']}", color=discord.Color.blue())
        if 'images' in card and 'large' in card['images']:
            embed.set_image(url=card['images']['large'])
        embed.add_field(name="Artist", value=card.get('artist', 'N/A'), inline=True)
        embed.add_field(name="Rarity", value=card.get('rarity', 'N/A'), inline=True)
        if 'flavorText' in card:
            embed.add_field(name="Flavor Text", value=card['flavorText'], inline=False)
        return embed

    @app_commands.command(name="tcgcard", description="Get information about a Pokémon TCG card")
    async def tcg_card(self, interaction: discord.Interaction, card_name: str):
        # Defer the interaction to give more processing time
        await interaction.response.defer()

        url = f"https://api.pokemontcg.io/v2/cards?q=name:{card_name}"
        headers = {"X-Api-Key": settings.POKEMON_TCG_API_KEY}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                cards = data['data']
                if cards:
                    card = cards[0]
                    embed = self.create_card_embed(card)
                    # Use follow-up since we deferred earlier
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send(f"No Pokémon TCG cards found matching '{card_name}'.")
            else:
                await interaction.followup.send(
                    "Failed to retrieve Pokémon TCG card information. Please try again later.")

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"{self.__class__.__name__} cog has been loaded.")

async def setup(bot):
    await bot.add_cog(Tabletop(bot))
    await bot.tree.sync()
