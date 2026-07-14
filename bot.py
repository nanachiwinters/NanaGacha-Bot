import discord
from discord import app_commands

from config import TOKEN

intents = discord.Intents.default()

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


# -----------------------------
# PERSONAL MENU
# -----------------------------

class MainMenu(discord.ui.View):

    @discord.ui.button(
        label="🎰 Gacha",
        style=discord.ButtonStyle.primary
    )
    async def gacha(self, interaction: discord.Interaction, button: discord.ui.Button):

        embed = discord.Embed(
            title="🎰 Gacha",
            description="Choose an option below.",
            color=0x5865F2
        )

        await interaction.response.edit_message(
            embed=embed,
            view=GachaMenu()
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

# -----------------------------
# GachaMenu
# -----------------------------

class GachaMenu(discord.ui.View):

    @discord.ui.button(
        label="Normal Spin",
        style=discord.ButtonStyle.primary
    )
    async def normal(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "🎰 Normal Gacha coming soon!",
            ephemeral=True
        )

    @discord.ui.button(
        label="Lucky Spin",
        style=discord.ButtonStyle.success
    )
    async def lucky(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "🍀 Lucky Gacha coming soon!",
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

# ============================================================
# ECONOMY MENU
# ============================================================

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
        style=discord.ButtonStyle.success
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
        
# -----------------------------
# OPEN MENU BUTTON
# -----------------------------

class OpenMenu(discord.ui.View):

    @discord.ui.button(
        label="📋 Open Menu",
        style=discord.ButtonStyle.primary
    )
    async def open_menu(self, interaction: discord.Interaction, button: discord.ui.Button):

        embed = discord.Embed(
            title="Main Menu",
            description="Choose an option below.",
            color=0x5865F2
        )

        await interaction.response.send_message(
            embed=embed,
            view=MainMenu(),
            ephemeral=True
        )


# -----------------------------
# SETUP COMMAND
# -----------------------------

@tree.command(
    name="setup",
    description="Creates or updates the Nachi menu."
)
@app_commands.default_permissions(administrator=True)
async def setup(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🤖 Nachi",
        description="Access Nachi's features using the button below.",
        color=0x5865F2
    )

    async for message in interaction.channel.history(limit=50):
        if (
            message.author == client.user
            and message.embeds
            and message.embeds[0].title == "🤖 Nachi"
        ):
            await message.edit(
                embed=embed,
                view=OpenMenu()
            )

            await interaction.response.send_message(
                "✅ Existing Nachi menu updated!",
                ephemeral=True
            )
            return

    await interaction.channel.send(
        embed=embed,
        view=OpenMenu()
    )

    await interaction.response.send_message(
        "✅ Nachi menu created!",
        ephemeral=True
        
    )
@client.event
async def on_ready():
    await tree.sync()
    print(f"✅ {client.user} is online!")


client.run(TOKEN)
