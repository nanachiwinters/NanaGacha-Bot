import discord


def setup_gacha():
    pass


# ============================================================
# GACHA MENU
# ============================================================

class GachaMenu(discord.ui.View):

    @discord.ui.button(
        label="🎲 Normal Spin",
        style=discord.ButtonStyle.primary
    )
    async def normal_spin(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "🎲 Normal Spin coming soon!",
            ephemeral=True
        )

    @discord.ui.button(
        label="✨ Lucky Spin",
        style=discord.ButtonStyle.success
    )
    async def lucky_spin(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "✨ Lucky Spin coming soon!",
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

        # We'll hook this back into MainMenu later.
        await interaction.response.edit_message(
            content="Back button coming soon.",
            embed=None,
            view=None
        )
