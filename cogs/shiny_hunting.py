from discord.ui import Select, Modal, View
from discord import SelectOption, Interaction, Embed, Button, ButtonStyle
from discord.ext import commands
import settings
import sqlite3

class CounterButton(Button):
    def __init__(self, label, hunt_id, increment):
        super().__init__(style=ButtonStyle.primary, label=label)
        self.hunt_id = hunt_id
        self.increment = increment

    async def callback(self, interaction: Interaction):
        conn = sqlite3.connect('shiny_hunts.db')
        c = conn.cursor()
        # Update the hunt counter by the increment amount
        c.execute('UPDATE hunts SET counter = counter + ? WHERE id = ?', (self.increment, self.hunt_id))
        conn.commit()
        conn.close()
        # Send an updated message or edit the existing one
        await interaction.response.edit_message(content=f"Counter updated by {self.increment}.", view=self.view)

class CounterView(View):
    def __init__(self, hunt_id):
        super().__init__()
        # Add increment and decrement buttons
        self.add_item(CounterButton(label="Increment", hunt_id=hunt_id, increment=1))
        self.add_item(CounterButton(label="Decrement", hunt_id=hunt_id, increment=-1))


class StartHuntModal(Modal):
    def __init__(self, pokemon_list, hunt_types, pokemon_games, *args, **kwargs):
        super().__init__(title="Start New Shiny Hunt", *args, **kwargs)

        # Pokémon dropdown
        self.add_item(Select(
            placeholder='Choose a Pokémon',
            options=[SelectOption(label=pokemon, value=pokemon) for pokemon in settings.POKEMON_LIST],
            custom_id='pokemon_select'
        ))

        # Hunt type dropdown
        self.add_item(Select(
            placeholder='Choose the type of hunt',
            options=[SelectOption(label=hunt, value=hunt) for hunt in settings.HUNT_TYPES],
            custom_id='hunt_type_select'
        ))

        # Game dropdown
        self.add_item(Select(
            placeholder='Choose the game',
            options=[SelectOption(label=game, value=game) for game in settings.POKEMON_GAMES],
            custom_id='game_select'
        ))

    async def callback(self, interaction: Interaction):
        pokemon = self.children[0].values[0]  # Assuming the first child is the Pokémon select
        hunt_type = self.children[1].values[0]  # Assuming the second child is the hunt type select
        game = self.children[2].values[0]  # Assuming the third child is the game select
        # Database insertion logic here
        await interaction.response.send_message(f'Started shiny hunt for {pokemon} in {game} using {hunt_type}.')

class ShinyHunting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def start_hunt(self, ctx, game, pokemon, hunt_type):
        """Starts a new shiny hunt."""
        conn = sqlite3.connect('shiny_hunts.db')
        c = conn.cursor()
        c.execute('INSERT INTO hunts (user_id, game, pokemon, hunt_type) VALUES (?, ?, ?, ?)',
                  (str(ctx.author.id), game, pokemon, hunt_type))
        conn.commit()
        conn.close()
        embed = Embed(title="New Shiny Hunt Started",
                              description=f"Shiny hunt for **{pokemon}** in **{game}** ({hunt_type}) has been started.",
                              color=0x00ff00)
        await ctx.send(embed=embed)

    @commands.command()
    async def count(self, ctx, increment: int):
        """Increment or decrement the counter for the current hunt."""
        conn = sqlite3.connect('shiny_hunts.db')
        c = conn.cursor()
        c.execute('UPDATE hunts SET counter = counter + ? WHERE user_id = ?', (increment, str(ctx.author.id)))
        conn.commit()
        conn.close()
        await ctx.send(f"Counter updated by {increment}.")

    @commands.command()
    async def edit_hunt(self, ctx, hunt_id: int, game=None, pokemon=None, hunt_type=None):
        """Edit an existing hunt."""
        conn = sqlite3.connect('shiny_hunts.db')
        c = conn.cursor()
        query = 'UPDATE hunts SET '
        params = []
        if game:
            query += 'game = ?, '
            params.append(game)
        if pokemon:
            query += 'pokemon = ?, '
            params.append(pokemon)
        if hunt_type:
            query += 'hunt_type = ?, '
            params.append(hunt_type)
        query = query.rstrip(', ')
        query += ' WHERE id = ? AND user_id = ?'
        params.extend([hunt_id, str(ctx.author.id)])
        c.execute(query, tuple(params))
        conn.commit()
        conn.close()
        embed = Embed(title="Hunt Updated",
                              description="The shiny hunt details have been successfully updated.", color=0x00ff00)
        await ctx.send(embed=embed)

    @commands.command()
    async def complete_hunt(self, ctx, hunt_id: int):
        """Mark a hunt as complete."""
        conn = sqlite3.connect('shiny_hunts.db')
        c = conn.cursor()
        c.execute('UPDATE hunts SET completed = 1 WHERE id = ? AND user_id = ?', (hunt_id, str(ctx.author.id)))
        conn.commit()
        conn.close()
        await ctx.send("Hunt marked as complete.")

    @commands.command()
    async def show_hunt(self, ctx):
        """Shows the current shiny hunt details."""
        conn = sqlite3.connect('shiny_hunts.db')
        c = conn.cursor()
        c.execute(
            'SELECT id, game, pokemon, hunt_type, counter, completed FROM hunts WHERE user_id = ? AND completed = 0',
            (str(ctx.author.id),))
        hunts = c.fetchall()
        conn.close()
        if hunts:
            for hunt in hunts:
                embed = Embed(title="Active Shiny Hunt",
                                      description=f"**Pokemon:** {hunt[2]} \n**Game:** {hunt[1]} \n**Type:** {hunt[3]}",
                                      color=0x0000ff)
                embed.add_field(name="Counter", value=str(hunt[4]), inline=False)
                embed.add_field(name="Status", value="Completed" if hunt[5] else "Active", inline=True)
                embed.add_field(name="Hunt ID", value=str(hunt[0]), inline=True)
                await ctx.send(embed=embed)
        else:
            await ctx.send("You do not have any active hunts.")

    @commands.command()
    async def manage_hunt(self, ctx, hunt_id: int):
        """Command to manage the hunt counter."""
        # Make sure the hunt exists and the user has access to it
        conn = sqlite3.connect('shiny_hunts.db')
        c = conn.cursor()
        c.execute('SELECT * FROM hunts WHERE id = ? AND user_id = ?', (hunt_id, str(ctx.author.id)))
        hunt = c.fetchone()
        conn.close()

        if hunt:
            # Send message with counter management view
            await ctx.send(f"Manage your hunt for {hunt[3]} (ID: {hunt_id}):", view=CounterView(hunt_id))
        else:
            await ctx.send("Hunt not found or you don't have access to this hunt.")


def setup(bot):
    bot.add_cog(ShinyHunting(bot))