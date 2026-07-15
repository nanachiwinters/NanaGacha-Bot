import discord
from discord import app_commands

def setup_admin(tree):

    @tree.command(
        name="admin",
        description="Open the admin panel."
    )
    @app_commands.default_permissions(administrator=True)
    async def admin(interaction: discord.Interaction):
        ...
