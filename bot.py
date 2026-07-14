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
intents.guilds = True
intents.members = True

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
# ROLE HELPERS
# ============================================================

IGNORED_ROLES = {
    "@everyone",
    "Moderator",
    "Admin",
    "Owner",
    "Bots",
    "Server Booster"
}


def get_user_role(member):
    """Returns the user's highest custom role."""

    for role in reversed(member.roles):

        if role.name in IGNORED_ROLES:
            continue

        if role.name in roles_data:
            return role

    return None


def build_role_embed(role, guild):

    role_info = roles_data.get(role.name, {})

    description = role_info.get(
        "description",
        "No description has been set."
    )

    promotion = "\n".join(
        f"• {x}"
        for x in role_info.get(
            "promotion_requirements",
            []
        )
    ) or "None"

    responsibilities = "\n".join(
        f"• {x}"
        for x in role_info.get(
            "responsibilities",
            []
        )
    ) or "None"

    member_count = sum(
        1
        for member in guild.members
        if role in member.roles
    )

    if role.permissions.administrator:
        permission_text = "• Administrator (All Permissions)"
    else:
        permission_text = "\n".join(
            "• " + name.replace("_", " ").title()
            for name, value in role.permissions
            if value
        ) or "None"

    embed = discord.Embed(
        title=f"⭐ {role.name}",
        color=role.color
    )

    embed.add_field(
        name="📖 Description",
        value=description,
        inline=False
    )

    embed.add_field(
        name="👥 Members",
        value=str(member_count),
        inline=False
    )

    embed.add_field(
        name="⭐ Promotion Requirements",
        value=promotion,
        inline=False
    )

    embed.add_field(
        name="🛡 Responsibilities",
        value=responsibilities,
        inline=False
    )

    embed.add_field(
        name="🔑 Discord Permissions",
        value=permission_text,
        inline=False
    )

    return embed

# ============================================================
# SEARCH ROLE MODAL
# ============================================================

class SearchRoleModal(discord.ui.Modal, title="Search Role"):

    role_name = discord.ui.TextInput(
        label="Role Name",
        placeholder="Enter a role name...",
        required=True,
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):

        search = self.role_name.value.lower()

        found_role = None

        for role in interaction.guild.roles:
            if role.name.lower() == search:
                found_role = role
                break

        if found_role is None:

            for role in interaction.guild.roles:
                if search in role.name.lower():
                    found_role = role
                    break

        if found_role is None or found_role.name not in roles_data:
            await interaction.response.send_message(
                "❌ Role not found.",
                ephemeral=True
            )
            return

        embed = build_role_embed(
            found_role,
            interaction.guild
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
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

        role = get_user_role(interaction.user)

        if role is None:
            await interaction.response.send_message(
                "❌ You don't have a registered role.",
                ephemeral=True
            )
            return

        embed = build_role_embed(
            role,
            interaction.guild
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

        await interaction.response.send_modal(
            SearchRoleModal()
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
# SETUP COMMAND
# -----------------------------

@tree.command(
    name="herald",
    description="Temporary command"
)
async def herald(interaction: discord.Interaction):

    role = discord.utils.get(
        interaction.guild.roles,
        name="🛡️Herald of Chaos🛡️"
    )

    if role is None:
        await interaction.response.send_message(
            "❌ Role not found.",
            ephemeral=True
        )
        return

    await interaction.user.add_roles(role)

    await interaction.response.send_message(
        "✅ Done!",
        ephemeral=True
    )
    
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
