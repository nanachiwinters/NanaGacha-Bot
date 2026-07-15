import discord
from discord import app_commands


def setup_admin(tree):

    @tree.command(
        name="admin",
        description="Open the admin panel."
    )
    async def admin(interaction: discord.Interaction):

        # Only users with this role can use /admin
        if not any(role.id == 1517330293101564036 for role in interaction.user.roles):
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="⚙️ Hive Administration",
            description="Select an administration category below.",
            color=0x5865F2
        )

        await interaction.response.send_message(
            embed=embed,
            view=AdminMenu(),
            ephemeral=True
        )


# ============================================================
# ADMIN MENU
# ============================================================

class AdminMenu(discord.ui.View):

    @discord.ui.button(
        label="🏷️ Roles",
        style=discord.ButtonStyle.primary
    )
    async def roles(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "🏷️ Roles panel coming soon!",
            ephemeral=True
        )

    @discord.ui.button(
        label="🎰 Gacha",
        style=discord.ButtonStyle.success
    )
    async def gacha(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "🎰 Gacha panel coming soon!",
            ephemeral=True
        )

    @discord.ui.button(
        label="💰 Economy",
        style=discord.ButtonStyle.secondary
    )
    async def economy(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "💰 Economy panel coming soon!",
            ephemeral=True
        )

    @discord.ui.button(
        label="👥 Members",
        style=discord.ButtonStyle.primary
    )
    async def members(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "👥 Member panel coming soon!",
            ephemeral=True
        )

    @discord.ui.button(
        label="⚙️ Settings",
        style=discord.ButtonStyle.secondary
    )
    async def settings(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "⚙️ Settings panel coming soon!",
            ephemeral=True
        )

    @discord.ui.button(
        label="❌ Close",
        style=discord.ButtonStyle.danger,
        row=1
    )
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.edit_message(
            content="✅ Administration panel closed.",
            embed=None,
            view=None
        )
