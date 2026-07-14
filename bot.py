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

        await interaction.response.send_message(
            "🎰 Gacha coming soon!",
            ephemeral=True
        )

    @discord.ui.button(
        label="🪙 Economy",
        style=discord.ButtonStyle.success
    )
    async def economy(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "🪙 Economy coming soon!",
            ephemeral=True
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
