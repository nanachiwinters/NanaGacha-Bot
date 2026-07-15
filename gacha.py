import discord

# ============================================================
# GACHA MENU
# ============================================================

class GachaMenu(discord.ui.View):

    def __init__(self, main_menu):
        super().__init__()
        self.main_menu = main_menu

    @discord.ui.button(
        label="🎲 Normal Spin",
        style=discord.ButtonStyle.primary
    )
    async def normal(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "🎰 Normal Gacha coming soon!",
            ephemeral=True
        )

    @discord.ui.button(
        label="✨ Lucky Spin",
        style=discord.ButtonStyle.success
    )
    async def lucky(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "🍀 Lucky Gacha coming soon!",
            ephemeral=True
        )

    @discord.ui.button(
        label="📊 Odds",
        style=discord.ButtonStyle.secondary
    )
    async def odds(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "📊 Odds coming soon!",
            ephemeral=True
        )

    @discord.ui.button(
        label="⬅ Back",
        style=discord.ButtonStyle.danger
    )
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):

        embed = discord.Embed(
            title="Main Menu",
            description="Choose an option below.",
            color=0x5865F2
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self.main_menu
        )
