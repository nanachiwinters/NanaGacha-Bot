import discord
import random

from storage import load_rooms, save_rooms

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

        rooms = load_rooms()

        if not rooms:
            await interaction.response.send_message(
                "❌ No rooms have been configured.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"✅ Loaded {len(rooms)} room(s)!",
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
