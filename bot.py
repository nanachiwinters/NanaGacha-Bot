import discord
from discord import app_commands

from config import TOKEN

intents = discord.Intents.default()

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


# -----------------------------
# MAIN MENU
# -----------------------------

class MainMenu(discord.ui.View):

    @discord.ui.button(
        label="🎰 Gacha",
        style=discord.ButtonStyle.primary
    )
    async def gacha(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "🎰 Gacha coming soon!",
            ephemeral=True
        )

    @discord.ui.button(
        label="🪙 Economy",
        style=discord.ButtonStyle.success
    )
    async def economy(self, interaction: discord.Interaction, button: discord.ui.Button):

        embed = discord.Embed(
            title="🪙 Economy",
            description="Choose an option below.",
            color=0x2ECC71
        )

        await interaction.response.edit_message(
            embed=embed,
            view=EconomyMenu()
        )


class EconomyMenu(discord.ui.View):

    @discord.ui.button(
        label="🎁 Daily",
        style=discord.ButtonStyle.primary
    )
    async def daily(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "🎁 Daily coming soon!",
            ephemeral=True
        )

    @discord.ui.button(
        label="🏆 Leaderboard",
        style=discord.ButtonStyle.secondary
    )
    async def leaderboard(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "🏆 Leaderboard coming soon!",
            ephemeral=True
        )

    @discord.ui.button(
        label="⬅ Back",
        style=discord.ButtonStyle.secondary
    )
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):

        embed = discord.Embed(
            title="Main Menu",
            description="Choose an option below.",
            color=0x5865F2
        )

        await interaction.response.edit_message(
            embed=embed,
            view=MainMenu()
        )


@tree.command(name="menu", description="Open the main menu")
async def menu(interaction: discord.Interaction):

    embed = discord.Embed(
        title="Main Menu",
        description="Choose an option below.",
        color=0x5865F2
    )

    await interaction.response.send_message(
        embed=embed,
        view=MainMenu()
    )


@client.event
async def on_ready():
    await tree.sync()
    print(f"✅ {client.user} is online!")


client.run(TOKEN)
