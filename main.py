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
                await bot.load_extension(f"cogs.{cog_file.stem}")
        if bot.guilds:  # Check if the bot is in any guilds
            guild_id = bot.guilds[0].id  # Get the first guild's ID
            logger.info(f"Syncing commands to the guild ID: {guild_id}")
            bot.tree.copy_global_to(guild=discord.Object(id=guild_id))
            await bot.tree.sync(guild=discord.Object(id=guild_id))
        else:
            logger.warning("Bot is not in any guilds.")

    # Greeting Command
    @bot.tree.command(description="Greets the user", name="greetings")
    async def hello(interaction: discord.Interaction):
        await interaction.response.send_message(f"Greetings human!")

    # Reload command
    @bot.hybrid_command(alias=['r'],
                 name='reload',
                 help='Reloads the bot\'s Cogs',
                 brief='Reload Cogs',
                 enabled=True,
                 hidden=True)
    @commands.is_owner()
    async def reload(ctx, cog: str):
        cog_path = f"cogs.{cog.lower()}"
        try:
            await bot.reload_extension(cog_path)
            await ctx.send(f"✅ Successfully reloaded cog: `{cog}`")
        except ExtensionNotLoaded:
            await ctx.send(f"⚠️ Extension `{cog}` was not loaded.")
        except ExtensionNotFound:
            await ctx.send(f"⚠️ Extension `{cog}` not found.")
        except NoEntryPointError:
            await ctx.send(f"⚠️ Extension `{cog}` does not have a setup function.")
        except ExtensionFailed as e:
            await ctx.send(f"⚠️ Extension `{cog}` could not be reloaded. Error: {e.original}")
        except CommandNotFound:
            await ctx.send(f"⚠️ Command `{cog}` not found.")
        except commands.NotOwner:
            await ctx.send("⚠️ This command can only be used by the bot owner.")
        except Exception as e:
            # Generic catch-all for any other exception
            await ctx.send(f"⚠️ An unexpected error occurred: {e}")

    # Unloads Cogs
    @bot.hybrid_command(aliases=['u'],
                 name='unload',
                 help="Unloads the bot's Cogs",
                 brief='Unload Cogs',
                 enabled=True,
                 hidden=True)
    @commands.is_owner()
    async def unload(ctx, cog: str):
        cog_path = f"cogs.{cog.lower()}"
        try:
            await bot.unload_extension(cog_path)
            await ctx.send(f"✅ Successfully unloaded cog: `{cog}`")
        except ExtensionNotLoaded:
            await ctx.send(f"⚠️ Extension `{cog}` was not loaded, so it cannot be unloaded.")
        except ExtensionNotFound:
            await ctx.send(f"⚠️ Extension `{cog}` not found.")
        except NoEntryPointError:
            await ctx.send(f"⚠️ Extension `{cog}` does not have a setup function.")
        except ExtensionFailed as e:
            await ctx.send(f"⚠️ Extension `{cog}` could not be unloaded. Error: {e.original}")
        except CommandNotFound:
            await ctx.send(f"⚠️ Command `{cog}` not found.")
        except commands.NotOwner:
            await ctx.send("⚠️ This command can only be used by the bot owner.")
        except Exception as e:
            # Generic catch-all for any other exception
            await ctx.send(f"⚠️ An unexpected error occurred: {e}")

    # Ping command
    @bot.tree.command()
    async def ping(interaction: discord.Interaction):
        # Calculate the latency
        latency = round(bot.latency * 1000)  # Convert to milliseconds
        await interaction.response.send_message(f'Pong! {latency}ms')

    bot.run(settings.DISCORD_API_SECRET)


if __name__ == "__main__":
    run()
