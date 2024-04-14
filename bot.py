import settings
import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound, ExtensionNotLoaded, ExtensionNotFound, NoEntryPointError, \
    ExtensionFailed

logger = settings.LOGGER


def run():
    intents = discord.Intents.all()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        logger.info(f'{bot.user.name} {bot.user.id} has connected to Discord!')
        logger.info(f'Guild ID: {bot.guilds[0].id}')
        for cog_file in settings.COGS_DIR.iterdir():
            if cog_file.name != "__init__.py" and cog_file.is_file():
                try:
                    await bot.load_extension(f"cogs.{cog_file.stem}")
                except Exception as e:
                    logger.error(f"Failed to load cog {cog_file.stem}: {e}")
        await bot.tree.sync()



    # Ping command
    @bot.tree.command()
    async def ping(interaction: discord.Interaction):
        # Calculate the latency
        latency = round(bot.latency * 1000)  # Convert to milliseconds
        await interaction.response.send_message(f'Pong! {latency}ms')

    bot.run(settings.DISCORD_API_SECRET)


if __name__ == "__main__":
    run()
