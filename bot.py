import discord
from discord import app_commands

from config import TOKEN
from storage import (
    load_coins,
    save_coins,
    load_roles,
    save_roles
)

intents = discord.Intents.default()

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

coins = load_coins()
roles_data = load_roles()

# ============================================================
# MAIN MENU
# ============================================================

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
        label="💰 Balance",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def balance(self, interaction: discord.Interaction, button: discord.ui.Button):

        user_id = str(interaction.user.id)

        if user_id not in coins:
            coins[user_id] = 0
            save_coins(coins)

        embed = discord.Embed(
            title="💰 Your Balance",
            description=(
                f"🪙 **Coins:** {coins[user_id]}\n\n"
                "Use your coins to purchase Gacha spins."
            ),
            color=0xFFD700
        )

        embed.set_footer(text="Nachi Economy")

        await interaction.response.edit_message(
            embed=embed,
            view=BalanceMenu()
        )
        
    @discord.ui.button(
        label="🎁 Daily",
        style=discord.ButtonStyle.success
    )
    async def daily(self, interaction: discord.Interaction, button: discord.ui.Button):

        user_id = str(interaction.user.id)

        if user_id not in coins:
            coins[user_id] = 0

        coins[user_id] += 1
        save_coins(coins)

        embed = discord.Embed(
            title="🎁 Daily Reward",
            description=(
                "You received **1 coin!**\n\n"
                f"💰 Balance: **{coins[user_id]}** coin(s)"
            ),
            color=0xFFD700
        )

        await interaction.response.edit_message(
            embed=embed,
            view=EconomyMenu()
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

# ============================================================
# BALANCE MENU
# ============================================================

class BalanceMenu(discord.ui.View):

    @discord.ui.button(
        label="⬅ Back",
        style=discord.ButtonStyle.primary
    )
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):

        embed = discord.Embed(
            title="🪙 Economy",
            description="Manage your coins and claim daily rewards.",
            color=0x2ECC71
        )

        await interaction.response.edit_message(
            embed=embed,
            view=EconomyMenu()
        )

# ============================================================
# ROLES MENU
# ============================================================

class RolesMenu(discord.ui.View):

    @discord.ui.button(
        label="👤 My Role",
        style=discord.ButtonStyle.primary
    )
    async def my_role(self, interaction: discord.Interaction, button: discord.ui.Button):

        member = interaction.user

        if len(member.roles) > 1:
            role_name = member.top_role.name
        else:
            role_name = "No Role"

        embed = discord.Embed(
            title="👤 Your Role",
            description=(
                f"**Current Role:** {role_name}\n\n"
                "*Role descriptions coming soon.*"
            ),
            color=0x9B59B6
        )

        await interaction.response.edit_message(
            embed=embed,
            view=MyRoleMenu()
        )

    @discord.ui.button(
        label="🔎 Search Role",
        style=discord.ButtonStyle.success
    )
    async def search_role(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "🔎 Search Role coming soon!",
            ephemeral=True
        )

    @discord.ui.button(
        label="📜 Role Hierarchy",
        style=discord.ButtonStyle.secondary
    )
    async def hierarchy(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "📜 Role Hierarchy coming soon!",
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
            view=MainMenu()
        )
        
# ============================================================
# MY ROLE MENU
# ============================================================

class MyRoleMenu(discord.ui.View):

    @discord.ui.button(
        label="⬅ Back",
        style=discord.ButtonStyle.danger
    )
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):

        embed = discord.Embed(
            title="👤 Roles",
            description="View your role, search for roles, or browse the role hierarchy.",
            color=0x9B59B6
        )

        await interaction.response.edit_message(
            embed=embed,
            view=RolesMenu()
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
