import discord
import openai
from discord.ext import commands
from discord import app_commands
import settings

logger = settings.LOGGER
openai.api_key = settings.OPENAI_API_KEY

class GPT(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Greeting Command
    @app_commands.command(name='ask', description='Asks ChatGPT a question.')
    @app_commands.describe(question='The question to ask ChatGPT.')
    async def ask(self, interaction: discord.Interaction, question: str):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": question}]
        )
        await interaction.response.send_message(response.choices[0].message['content'])
        logger.info(f"Asked ChatGPT: \"{question}\" in {interaction.guild.name}.")

    @app_commands.command(name='generate_image', description='Generates an image from a prompt.')
    @app_commands.describe(prompt='The prompt to generate an image from.')
    async def generate_image(self, interaction: discord.Interaction, prompt: str):
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_url = response.data[0].url
        await interaction.response.send_message(image_url)
        logger.info(f"Generated an image for \"{prompt}\" in {interaction.guild.name}.")

    @app_commands.command(name='personality_chat', description='Talks to a ChatGPT personality.')
    @app_commands.describe(prompt='What you want to say.', personality='The ChatGPT personality to talk to.')
    async def personality_chat(self, interaction: discord.Interaction, prompt: str, personality: str):
        # This is a placeholder for personality-specific handling. The actual implementation will depend on how you define and use personalities.
        # For simplicity, we're sending the prompt directly to ChatGPT, but you might want to modify this based on your personality setup.
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are now talking to {personality}."},
                {"role": "user", "content": prompt}
            ]
        )
        await interaction.response.send_message(response.choices[0].message['content'])
        logger.info(f"Personality \"{personality}\" responded to \"{prompt}\" in {interaction.guild.name}.")

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"{self.__class__.__name__} cog has been loaded.")

async def setup(bot):
    await bot.add_cog(GPT(bot))
    await bot.tree.sync()
