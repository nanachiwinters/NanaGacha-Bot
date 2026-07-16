import discord
import random

from storage import load_rooms, save_rooms

# ============================================================
# RARITIES
# ============================================================

RARITY_LEVELS = {
    "Common": 0,
    "Rare": 1,
    "Epic": 2,
    "Legendary": 3
}

LEVEL_TO_RARITY = {
    0: "Common",
    1: "Rare",
    2: "Epic",
    3: "Legendary"
}


# ============================================================
# ROOM ROLL
# ============================================================

def roll_room(lucky=False):

    rooms = load_rooms()

    available = []

    for room_name, room in rooms.items():

        if room.get("used", False):
            continue

        if lucky and not room.get("lucky", False):
            continue

        available.append((room_name, room))

    if not available:
        return None

    weights = [room["weight"] for _, room in available]

    room_name, room = random.choices(
        available,
        weights=weights,
        k=1
    )[0]

    return {
        "name": room_name,
        "code": room["code"],
        "rarity": room["rarity"]
    }
    
# ============================================================
# GACHA HELPERS
# ============================================================

def roll_normal_room():

    rooms = load_rooms()

    normal_rooms = []
    weights = []

    for room_name, room in rooms.items():

        if room.get("lucky", False):
            continue

        normal_rooms.append((room_name, room))
        weights.append(room.get("weight", 1))

    if not normal_rooms:
        return None

    return random.choices(
        normal_rooms,
        weights=weights,
        k=1
    )[0]

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

        reward = roll_room()

        if reward is None:

            await interaction.response.send_message(
                "❌ There are no available rooms.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="🎁 Mystery Room",
            color=0x5865F2
        )

        embed.description = (
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Current Rarity\n"
            "❔ ???\n\n"
            "Upgrades Remaining\n"
            "★★★"
        )

        await interaction.response.edit_message(
            embed=embed,
            view=UpgradeView(
                reward,
                self.main_menu
            )
        )

    @discord.ui.button(
        label="✨ Lucky Spin",
        style=discord.ButtonStyle.success
    )
    async def lucky(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "🍀 Lucky Spin coming soon!",
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

# ============================================================
# UPGRADE VIEW
# ============================================================

class UpgradeView(discord.ui.View):

    def __init__(self, reward, main_menu):

        super().__init__(timeout=None)

        self.reward = reward
        self.main_menu = main_menu

        self.final_level = RARITY_LEVELS[reward["rarity"]]

        self.current_level = 0

        self.revealed = False

        self.upgrades_used = 0

    def stars(self):
        return "☆" * self.upgrades_used + "★" * (3 - self.upgrades_used)

    def embed(self):

        embed = discord.Embed(
            title="🎁 Mystery Room",
            color=0x5865F2
        )

        if not self.revealed:

            embed.description = (
                "━━━━━━━━━━━━━━━━━━\n\n"
                "Press **Reveal** to discover\n"
                "your starting rarity."
            )

        else:

            rarity = LEVEL_TO_RARITY[self.current_level]

            emoji = {
                "Common": "🟢",
                "Rare": "🔵",
                "Epic": "🟣",
                "Legendary": "👑"
            }[rarity]

            embed.description = (
                "━━━━━━━━━━━━━━━━━━\n\n"
                f"Current Rarity\n"
                f"{emoji} {rarity}\n\n"
                f"Upgrades Remaining\n"
                f"{self.stars()}"
            )

        return embed

    @discord.ui.button(
        label="🔍 Reveal",
        style=discord.ButtonStyle.success
    )
    async def reveal(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.revealed = True
        self.current_level = 0

        # Disable Reveal
        button.disabled = True

        # Enable Upgrade
        self.children[1].disabled = False

        await interaction.response.edit_message(
            embed=self.embed(),
            view=self
        )

    @discord.ui.button(
        label="⚡ Upgrade",
        style=discord.ButtonStyle.primary,
        disabled=True
    )
    async def upgrade(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "⚡ Upgrade animation coming next!",
            ephemeral=True
        )
