import discord

# ============================================================
# GACHA MENU
# ============================================================

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

        await interaction.response.send_message(
            "⬅ Back coming soon.",
            ephemeral=True
        )
