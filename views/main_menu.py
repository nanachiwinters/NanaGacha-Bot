import discord

from views.gacha import GachaMenu
from views.economy import EconomyMenu
from views.roles import RolesMenu

class MainMenu(discord.ui.View):

    @discord.ui.button(
        label="🎰 Gacha",
        style=discord.ButtonStyle.primary
    )
    async def gacha(self, interaction: discord.Interaction, button: discord.ui.Button):

        embed = discord.Embed(
            title="🎰 Gacha",
            description="Spend your 🪙 coins to spin for exclusive rewards.",
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
            description="Manage your coins and claim daily rewards.",
            color=0x2ECC71
        )

        await interaction.response.edit_message(
            embed=embed,
            view=EconomyMenu()
        )
        
    @discord.ui.button(
        label="👤 Roles",
        style=discord.ButtonStyle.primary
    )
    async def roles(self, interaction: discord.Interaction, button: discord.ui.Button):

        embed = discord.Embed(
            title="👤 Roles",
            description="View your role, search for roles, or browse the role hierarchy.",
            color=0x9B59B6
        )

        await interaction.response.edit_message(
            embed=embed,
            view=RolesMenu()
        )
