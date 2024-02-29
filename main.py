import settings
import discord
from discord.ext import commands

logger = settings.LOGGER


def run():
    intents = discord.Intents.default()
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        logger.info(f'{bot.user.name} has connected to Discord!')

    bot.run(settings.DISCORD_API_SECRET)


if __name__ == "__main__":
    run()
