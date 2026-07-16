import discord
import random
import asyncio

from storage import (
    load_rooms,
    save_rooms
)

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

RARITY_EMOJIS = {
    "Common": "🟢",
    "Rare": "🔵",
    "Epic": "🟣",
    "Legendary": "👑"
}

# ============================================================
# REACTOR
# ============================================================

MAX_POWER = 120

COMMON_THRESHOLD = 40
EPIC_THRESHOLD = 80
LEGENDARY_THRESHOLD = 120

# Every upgrade adds a random amount of power.
POWER_GAIN = (
    20,
    45
)

# ============================================================
# ROOM HELPERS
# ============================================================

def roll_room_from_rarity(rarity):

    rooms = load_rooms()

    available = []
    weights = []

    for room_name, room in rooms.items():

        if room.get("used", False):
            continue

        if room.get("rarity") != rarity:
            continue

        available.append((room_name, room))
        weights.append(room.get("weight", 1))

    if not available:
        return None

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


def claim_room(room_name):

    rooms = load_rooms()

    if room_name in rooms:

        rooms[room_name]["used"] = True

        save_rooms(rooms)

# ============================================================
# GACHA MENU
# ============================================================

class GachaMenu(discord.ui.View):

    def __init__(self, main_menu):
        super().__init__(timeout=None)
        self.main_menu = main_menu

    @discord.ui.button(
        label="🎲 Normal Spin",
        style=discord.ButtonStyle.primary
    )
    async def normal(self, interaction: discord.Interaction, button: discord.ui.Button):

        embed = discord.Embed(
            title="🎁 Mystery Room",
            color=0x5865F2
        )

        embed.description = (
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Press **Reveal** to begin\n"
            "charging the reactor.\n\n"
            "Current Rarity\n"
            "❔ ???\n\n"
            "Reactor Charge\n"
            "░░░░░░░░░░"
        )

        await interaction.response.edit_message(
            embed=embed,
            view=UpgradeView(self.main_menu)
        )

    @discord.ui.button(
        label="✨ Lucky Spin",
        style=discord.ButtonStyle.success
    )
    async def lucky(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "🍀 Lucky Reactor coming soon!",
            ephemeral=True
        )

    @discord.ui.button(
        label="📊 Odds",
        style=discord.ButtonStyle.secondary
    )
    async def odds(self, interaction: discord.Interaction, button: discord.ui.Button):

        embed = discord.Embed(
            title="📊 Reactor Odds",
            color=0x5865F2
        )

        embed.description = (
            "Upgrade Chances are determined\n"
            "by Reactor Power.\n\n"
            "⚡ More details coming soon!"
        )

        await interaction.response.send_message(
            embed=embed,
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
# PART 3A
#
# REPLACE THE BEGINNING OF UpgradeView
# THROUGH THE END OF embed()
# ============================================================

class UpgradeView(discord.ui.View):

    def __init__(self, main_menu):

        super().__init__(timeout=None)

        self.main_menu = main_menu

        self.revealed = False

        self.power = 0

        self.current_level = 0

        self.upgrades_used = 0

    def stars(self):

        return "☆" * self.upgrades_used + "★" * (3 - self.upgrades_used)

    def power_bar(self):

        bars = 10

        filled = int((self.power / MAX_POWER) * bars)

        if filled > bars:
            filled = bars

        return "█" * filled + "░" * (bars - filled)

    def update_rarity(self):

        if self.power >= LEGENDARY_THRESHOLD:
            self.current_level = 3

        elif self.power >= EPIC_THRESHOLD:
            self.current_level = 2

        elif self.power >= COMMON_THRESHOLD:
            self.current_level = 1

        else:
            self.current_level = 0

    def embed(self, status=None):

        embed = discord.Embed(
            title="🎁 Mystery Room",
            color=0x5865F2
        )

        if not self.revealed:

            embed.description = (
                "━━━━━━━━━━━━━━━━━━\n\n"
                "Press **Reveal** to begin\n"
                "charging the reactor.\n\n"
                "Current Rarity\n"
                "❔ ???\n\n"
                "Reactor Charge\n"
                "░░░░░░░░░░"
            )

            return embed

        rarity = LEVEL_TO_RARITY[self.current_level]

        emoji = RARITY_EMOJIS[rarity]

        description = (
            "━━━━━━━━━━━━━━━━━━\n\n"
        )

        if status:

            description += status + "\n\n"

        description += (
            "Current Rarity\n"
            f"{emoji} {rarity}\n\n"
            "Reactor Charge\n"
            f"{self.power_bar()}\n\n"
            "Upgrades Remaining\n"
            f"{self.stars()}"
        )

        embed.description = description

        return embed
        
    @discord.ui.button(
        label="🔍 Reveal",
        style=discord.ButtonStyle.success
    )
    async def reveal(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.revealed = True

        button.disabled = True

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

        if self.upgrades_used >= 3:
            return

        self.upgrades_used += 1

        button.disabled = True

        await interaction.response.edit_message(
            embed=self.embed("⚡ Charging."),
            view=self
        )

        await asyncio.sleep(0.5)

        await interaction.edit_original_response(
            embed=self.embed("⚡⚡ Charging.."),
            view=self
        )

        await asyncio.sleep(0.5)

        await interaction.edit_original_response(
            embed=self.embed("⚡⚡⚡ Charging..."),
            view=self
        )

        await asyncio.sleep(0.7)

        gain = random.randint(*POWER_GAIN)

        old_level = self.current_level

        self.power += gain

        if self.power > MAX_POWER:
            self.power = MAX_POWER

        self.update_rarity()
        
        if self.upgrades_used < 3:

            button.disabled = False

            await interaction.edit_original_response(
                embed=self.embed(status),
                view=self
            )

        else:

            rarity = LEVEL_TO_RARITY[self.current_level]

            reward = roll_room_from_rarity(rarity)

            if reward is None:

                embed = discord.Embed(
                    title="❌ No Rooms Left",
                    description=f"There are no unused **{rarity}** rooms remaining.",
                    color=discord.Color.red()
                )

                await interaction.edit_original_response(
                    embed=embed,
                    view=None
                )

                return

            claim_room(reward["name"])

            emoji = RARITY_EMOJIS[rarity]

            if rarity == "Legendary":
                color = discord.Color.gold()
            else:
                color = discord.Color.blurple()

            embed = discord.Embed(
                title="🎉 ROOM ACQUIRED",
                color=color
            )

            embed.description = (
                "━━━━━━━━━━━━━━━━━━\n\n"
                f"{emoji} **{rarity}**\n\n"
                f"🏠 **{reward['name']}**\n\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                f"🔑 **{reward['code']}**"
            )

            await interaction.edit_original_response(
                embed=embed,
                view=None
            )
