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

        room = roll_normal_room()

        if room is None:
            await interaction.response.send_message(
                "❌ There are no available normal rooms.",
                ephemeral=True
            )
            return

        room_name, room_data = room

        embed = discord.Embed(
            title="🎉 You Won!",
            description=f"You rolled **{room_name}**!",
            color=0x2ECC71
        )

        embed.add_field(
            name="⭐ Rarity",
            value=room_data.get("rarity", "Unknown"),
            inline=True
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    @discord.ui.button(
        label="✨ Lucky Spin",
        style=discord.ButtonStyle.success
    )
    async def lucky(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "🍀 Lucky Spin is coming soon!",
            ephemeral=True
        )

    @discord.ui.button(
        label="📊 Odds",
        style=discord.ButtonStyle.secondary
    )
    async def odds(self, interaction: discord.Interaction, button: discord.ui.Button):

        embed = discord.Embed(
            title="📊 Gacha Odds",
            description=(
                "Current drop chances are determined by each room's weight.\n\n"
                "These values are configurable through the Admin Panel."
            ),
            color=0x5865F2
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
