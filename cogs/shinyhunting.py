from discord.ui import Select, Modal, View
from discord import SelectOption, Interaction, Embed, Button, ButtonStyle, File
from discord.ext import commands
from sklearn.linear_model import LinearRegression
import settings
import sqlite3
import statistics
import matplotlib.pyplot as plt
import numpy as np


def get_basic_stats(user_id):
    conn = sqlite3.connect('shiny_hunts.db')
    c = conn.cursor()
    c.execute('SELECT counter FROM hunts WHERE user_id = ? AND completed = 1', (user_id,))
    counters = [row[0] for row in c.fetchall()]
    conn.close()

    if counters:
        average = statistics.mean(counters)
        median = statistics.median(counters)
        mode = statistics.mode(counters) if len(set(counters)) > 1 else 'No mode'
        return average, median, mode
    else:
        return None, None, None


def plot_hunt_distribution(user_id):
    conn = sqlite3.connect('shiny_hunts.db')
    c = conn.cursor()
    c.execute('SELECT counter FROM hunts WHERE user_id = ? AND completed = 1', (user_id,))
    counters = [row[0] for row in c.fetchall()]
    conn.close()

    plt.hist(counters, bins=20, alpha=0.75, color='blue')
    plt.title('Distribution of Hunt Attempts')
    plt.xlabel('Number of Attempts')
    plt.ylabel('Frequency')
    plt.show()


def predict_attempts(user_id):
    conn = sqlite3.connect('shiny_hunts.db')
    c = conn.cursor()
    c.execute('SELECT counter FROM hunts WHERE user_id = ? AND completed = 1', (user_id,))
    data = [row[0] for row in c.fetchall()]
    conn.close()

    if len(data) > 5:  # Ensure there is enough data to model
        # Reshape data for sklearn
        X = np.array(range(len(data))).reshape(-1, 1)
        y = np.array(data).reshape(-1, 1)

        # Fit model
        model = LinearRegression()
        model.fit(X, y)

        # Predict next attempt count
        predicted = model.predict([[len(data)]])
        return predicted[0][0]
    else:
        return None


def compare_hunts_by_type(user_id):
    conn = sqlite3.connect('shiny_hunts.db')
    c = conn.cursor()
    c.execute('SELECT hunt_type, counter FROM hunts WHERE user_id = ? AND completed = 1', (user_id,))
    results = c.fetchall()
    conn.close()

    by_type = {}
    for hunt_type, counter in results:
        if hunt_type in by_type:
            by_type[hunt_type].append(counter)
        else:
            by_type[hunt_type] = [counter]

    averages = {ht: statistics.mean(counts) for ht, counts in by_type.items()}
    return averages


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

    @commands.command()
    async def set_daily_goal(self, ctx, hunt_id: int, goal: int):
        """Sets a daily goal for the number of encounters for a specific hunt."""
        if goal < 1:
            await ctx.send("Please set a positive number as your goal.")
            return

        conn = sqlite3.connect('shiny_hunts.db')
        c = conn.cursor()
        c.execute('UPDATE hunts SET daily_goal = ? WHERE id = ? AND user_id = ?', (goal, hunt_id, str(ctx.author.id)))
        changes = c.rowcount
        conn.commit()
        conn.close()

        if changes > 0:
            await ctx.send(f"Daily goal set to {goal} for hunt ID {hunt_id}.")
        else:
            await ctx.send("Hunt not found or you don't have access to this hunt.")

    @commands.command()
    async def view_daily_goal(self, ctx, hunt_id: int):
        """Views the daily goal and current progress for a specific hunt."""
        conn = sqlite3.connect('shiny_hunts.db')
        c = conn.cursor()
        c.execute('SELECT pokemon, daily_goal, counter FROM hunts WHERE id = ? AND user_id = ?',
                  (hunt_id, str(ctx.author.id)))
        hunt = c.fetchone()
        conn.close()

        if hunt:
            pokemon, daily_goal, counter = hunt
            if daily_goal > 0:
                progress = min((counter % daily_goal) / daily_goal * 100, 100)
                await ctx.send(
                    f"Daily goal for {pokemon}: {daily_goal} hunts. Current progress: {counter} hunts today ({progress:.2f}%).")
            else:
                await ctx.send(f"No daily goal set for {pokemon}.")
        else:
            await ctx.send("Hunt not found or you don't have access to this hunt.")

    @commands.command()
    async def reset_daily_goal(self, ctx, hunt_id: int):
        """Resets the daily goal for a specific hunt."""
        conn = sqlite3.connect('shiny_hunts.db')
        c = conn.cursor()
        # Set the daily_goal to 0 indicating no goal is set
        c.execute('UPDATE hunts SET daily_goal = 0 WHERE id = ? AND user_id = ?', (hunt_id, str(ctx.author.id)))
        changes = c.rowcount
        conn.commit()
        conn.close()

        if changes > 0:
            await ctx.send(f"Daily goal for hunt ID {hunt_id} has been reset.")
        else:
            await ctx.send("Hunt not found or you don't have access to this hunt.")

    @commands.command()
    async def hunt_stats(self, ctx, hunt_id: int = None):
        """Displays statistics for the current or specified hunt."""
        conn = sqlite3.connect('shiny_hunts.db')
        c = conn.cursor()
        if hunt_id:
            c.execute('SELECT game, pokemon, hunt_type, counter, completed FROM hunts WHERE id = ? AND user_id = ?',
                      (hunt_id, str(ctx.author.id)))
        else:
            c.execute(
                'SELECT game, pokemon, hunt_type, counter, completed FROM hunts WHERE user_id = ? AND completed = 0 ORDER BY id DESC LIMIT 1',
                (str(ctx.author.id),))
        hunt = c.fetchone()
        conn.close()
        if hunt:
            embed = Embed(title=f"Statistics for {hunt[1]}",
                          description=f"Game: {hunt[0]}\nHunt Type: {hunt[2]}\nCounter: {hunt[3]}\nStatus: {'Completed' if hunt[4] else 'Active'}",
                          color=0x00ff00)
            # Add more statistical insights here
            await ctx.send(embed=embed)
        else:
            await ctx.send("No active or specified hunt found.")

    @commands.command()
    async def set_hunt_status(self, ctx, hunt_id: int, status: str):
        """Sets the status of a hunt to 'active' or 'paused'."""
        if status.lower() not in ['active', 'paused']:
            await ctx.send("Invalid status. Please use 'active' or 'paused'.")
            return

        conn = sqlite3.connect('shiny_hunts.db')
        c = conn.cursor()
        # Assuming a 'status' column exists, or you could use the 'completed' column with more status options.
        c.execute('UPDATE hunts SET status = ? WHERE id = ? AND user_id = ?',
                  (status.lower(), hunt_id, str(ctx.author.id)))
        conn.commit()
        conn.close()
        await ctx.send(f"Hunt {hunt_id} has been set to {status}.")

    @commands.command()
    async def show_statistics(self, ctx):
        """Shows comprehensive statistics about the user's shiny hunts."""
        user_id = str(ctx.author.id)
        average, median, mode = get_basic_stats(user_id)
        distribution_image = plot_hunt_distribution(user_id)

        if average is not None:
            embed = Embed(title="Your Shiny Hunting Statistics",
                          description="Here are your shiny hunting statistics:", color=0x00ff00)
            embed.add_field(name="Average Attempts", value=f"{average:.2f}", inline=True)
            embed.add_field(name="Median Attempts", value=str(median), inline=True)
            embed.add_field(name="Mode of Attempts", value=str(mode), inline=True)
            await ctx.send(embed=embed)

            if distribution_image:
                file = File(distribution_image, filename="distribution.png")
                await ctx.send("Distribution of your hunt attempts:", file=file)
        else:
            await ctx.send("No completed hunts to analyze.")


def setup(bot):
    bot.add_cog(ShinyHunting(bot))
