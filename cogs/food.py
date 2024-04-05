import discord
import httpx
from discord.ext import commands
from discord import app_commands
import settings

logger = settings.LOGGER


class Food(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="bacon", description="Sends a random bacon image")
    async def bacon(self, interaction: discord.Interaction):
        # Predefined dimensions for the bacon image
        width = 640
        height = 480
        bacon_image_url = f"https://baconmockup.com/{width}/{height}"

        embed = discord.Embed(title="Here's your bacon 🥓")
        embed.set_image(url=bacon_image_url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="coffee", description="Sends a random coffee image")
    async def coffee(self, interaction: discord.Interaction):
        # The API endpoint for fetching a random coffee image
        coffee_image_url = "https://coffee.alexflipnote.dev/random"

        # Creating an embed to display the coffee image
        embed = discord.Embed(title="Here's your coffee ☕", color=discord.Color.blurple())
        embed.set_image(url=coffee_image_url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="searchrecipe", description="Search for a recipe")
    async def search_recipe(self, interaction: discord.Interaction, query: str):
        # Constructing the API URL
        api_url = f"https://api.edamam.com/search?q={query}&app_id={settings.RECIPE_APP_ID}&app_key={settings.RECIPE_API_KEY}"

        async with httpx.AsyncClient() as client:
            response = await client.get(api_url)
            if response.status_code == 200:
                data = response.json()
                # Checking if there are any recipes found
                if data['hits']:
                    first_recipe = data['hits'][0]['recipe']
                    # Creating an embed with the first recipe found
                    embed = discord.Embed(title=first_recipe['label'], url=first_recipe['url'],
                                          color=discord.Color.green())
                    embed.set_image(url=first_recipe['image'])
                    embed.add_field(name="Ingredients", value='\n'.join(first_recipe['ingredientLines']), inline=False)
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message("No recipes found. Try a different search.")
            else:
                await interaction.response.send_message("Failed to retrieve recipes. Please try again later.")

    def get_ingredients(self, cocktail_data):
        ingredients = ""
        for i in range(1, 16):  # The API provides up to 15 ingredients
            ingredient = cocktail_data.get(f'strIngredient{i}', None)
            measure = cocktail_data.get(f'strMeasure{i}', "")
            if ingredient:
                ingredients += f"{ingredient} - {measure.strip()}\n"
        return ingredients.strip()

    def create_cocktail_embed(self, cocktail_data):
        embed = discord.Embed(title=cocktail_data['strDrink'], color=discord.Color.blue())
        embed.set_image(url=cocktail_data['strDrinkThumb'])
        embed.add_field(name="Instructions", value=cocktail_data['strInstructions'], inline=False)
        ingredients = self.get_ingredients(cocktail_data)
        if ingredients:
            embed.add_field(name="Ingredients", value=ingredients, inline=False)
        return embed

    @app_commands.command(name="cocktail", description="Search for a cocktail recipe")
    async def cocktail(self, interaction: discord.Interaction, query: str):
        # Replace spaces with underscores for multi-word queries as required by the API
        formatted_query = query.replace(' ', '_')
        api_url = f"https://www.thecocktaildb.com/api/json/v1/1/search.php?s={formatted_query}"

        async with httpx.AsyncClient() as client:
            response = await client.get(api_url)
            if response.status_code == 200:
                data = response.json()
                if data['drinks']:
                    first_drink = data['drinks'][0]
                    embed = self.create_cocktail_embed(first_drink)
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message("No cocktails found. Please try a different name.")
            else:
                await interaction.response.send_message("Failed to retrieve cocktail recipes. Please try again later.")

    def extract_ingredients(self, meal):
        ingredients = ""
        for i in range(1, 21):  # TheMealDB lists up to 20 ingredients
            ingredient = meal.get(f'strIngredient{i}')
            measure = meal.get(f'strMeasure{i}')
            if ingredient and ingredient.strip():
                ingredients += f"{ingredient}: {measure}\n"
        return ingredients.strip() or "No main ingredients listed."

    def create_meal_embed(self, meal):
        embed = discord.Embed(title=meal['strMeal'], color=discord.Color.green())
        embed.set_image(url=meal['strMealThumb'])
        embed.add_field(name="Category", value=meal['strCategory'], inline=True)
        embed.add_field(name="Cuisine", value=meal['strArea'], inline=True)

        ingredients = self.extract_ingredients(meal)
        embed.add_field(name="Main Ingredients", value=ingredients, inline=False)

        embed.add_field(name="Instructions", value=meal['strInstructions'][:1024], inline=False)
        embed.set_footer(text="For more details, check the instructions or watch the video linked.")
        return embed

    @app_commands.command(name="meal", description="Search for a meal recipe")
    async def meal(self, interaction: discord.Interaction, query: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://www.themealdb.com/api/json/v1/1/search.php?s={query}")
            if response.status_code == 200:
                data = response.json()
                meals = data.get("meals")
                if meals:
                    meal = meals[0]  # Let's take the first meal found
                    embed = self.create_meal_embed(meal)
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message("No meals found. Please try another query.")
            else:
                await interaction.response.send_message("Failed to retrieve meal recipes. Please try again later.")

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"{self.__class__.__name__} cog has been loaded.")

async def setup(bot):
    await bot.add_cog(Food(bot))
    await bot.tree.sync()
