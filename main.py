import os
import asyncio
import sqlite3

import discord
from discord.ext import commands


# =========================================================
# DISCORD TOKEN
# =========================================================

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "DISCORD_BOT_TOKEN is missing."
    )


# =========================================================
# DISCORD SETUP
# =========================================================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# =========================================================
# DATABASE
# =========================================================

DATABASE_NAME = "/tmp/eko_transport.db"


def connect():
    return sqlite3.connect(DATABASE_NAME)


def setup_database():

    connection = connect()
    cursor = connection.cursor()

    # Player locations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            user_id INTEGER PRIMARY KEY,
            location TEXT NOT NULL
        )
    """)

    # Player vehicles
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            user_id INTEGER PRIMARY KEY,
            vehicle_name TEXT NOT NULL,
            fuel REAL NOT NULL DEFAULT 50,
            fuel_capacity REAL NOT NULL DEFAULT 60
        )
    """)

    connection.commit()
    connection.close()


def get_player_location(user_id):

    connection = connect()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT location FROM players WHERE user_id = ?",
        (user_id,)
    )

    result = cursor.fetchone()

    connection.close()

    if result:
        return result[0]

    return None


def set_player_location(user_id, location):

    connection = connect()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO players (user_id, location)
        VALUES (?, ?)

        ON CONFLICT(user_id)
        DO UPDATE SET location = excluded.location
    """, (user_id, location))

    connection.commit()
    connection.close()


def create_vehicle(user_id, vehicle_name="Toyota Camry"):

    connection = connect()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO vehicles
        (user_id, vehicle_name, fuel, fuel_capacity)

        VALUES (?, ?, 50, 60)
    """, (user_id, vehicle_name))

    connection.commit()
    connection.close()


def get_vehicle(user_id):

    connection = connect()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT vehicle_name, fuel, fuel_capacity

        FROM vehicles

        WHERE user_id = ?
    """, (user_id,))

    result = cursor.fetchone()

    connection.close()

    return result


def update_fuel(user_id, fuel):

    connection = connect()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE vehicles

        SET fuel = ?

        WHERE user_id = ?
    """, (fuel, user_id))

    connection.commit()
    connection.close()


# Create database tables when bot starts
setup_database()


# =========================================================
# EKO LOCATIONS
# =========================================================

LOCATIONS = {

    "help-desk":
        "🛂 Immigration Office",

    "èko-lobby":
        "🟢 Èko Green Zone",

    "mayors-penthouse":
        "🏛️ Mayor's Penthouse",

    "deputys-residence":
        "🏠 Deputy's Residence",

    "banking-hall":
        "🏦 Banking Hall",

    "mainland":
        "🌍 Mainland",

    "èko-oil-and-gas":
        "⛽ Èko Oil & Gas",
}


# =========================================================
# ROUTES
# =========================================================

ROUTES = {

    ("banking-hall", "èko-lobby"): {
        "distance": 3,
        "time": 10,
    },

    ("banking-hall", "mainland"): {
        "distance": 8,
        "time": 15,
    },

    ("mainland", "èko-oil-and-gas"): {
        "distance": 6,
        "time": 12,
    },

    ("èko-lobby", "help-desk"): {
        "distance": 2,
        "time": 8,
    },

    ("èko-lobby", "banking-hall"): {
        "distance": 3,
        "time": 10,
    },

    ("mainland", "banking-hall"): {
        "distance": 8,
        "time": 15,
    },

    ("èko-oil-and-gas", "mainland"): {
        "distance": 6,
        "time": 12,
    },

    ("help-desk", "èko-lobby"): {
        "distance": 2,
        "time": 8,
    },
}


# =========================================================
# BOT READY
# =========================================================

@bot.event
async def on_ready():

    print(f"Bot is online as {bot.user}")

    print("Commands loaded:")

    for command in bot.commands:

        print(f"!{command.name}")


# =========================================================
# !PING
# =========================================================

@bot.command()
async def ping(ctx: commands.Context):

    await ctx.send("Pong!")


# =========================================================
# !LOCATION
# =========================================================

@bot.command()
async def location(ctx: commands.Context):

    user_id = ctx.author.id

    current_location = get_player_location(user_id)

    if current_location is None:

        if ctx.channel.name in LOCATIONS:

            current_location = ctx.channel.name

            set_player_location(
                user_id,
                current_location
            )

        else:

            await ctx.send(
                "📍 **LOCATION UNKNOWN**\n\n"
                "This channel has not been registered "
                "as an Èko location."
            )

            return

    await ctx.send(
        f"📍 **YOUR CURRENT LOCATION**\n\n"
        f"You are currently at:\n"
        f"**{LOCATIONS[current_location]}**"
    )


# =========================================================
# !ROUTE
# =========================================================

@bot.command()
async def route(ctx: commands.Context):

    await ctx.send(
        "🗺️ **ÈKO TRANSPORT ROUTES**\n"
        "════════════════════\n\n"

        "🛂 **Immigration Office**\n"
        "🟢 **Èko Green Zone**\n"
        "🏛️ **Mayor's Penthouse**\n"
        "🏠 **Deputy's Residence**\n"
        "🏦 **Banking Hall**\n"
        "🌍 **Mainland**\n"
        "⛽ **Èko Oil & Gas**\n\n"

        "Use `!drive <destination>` "
        "to travel.\n"

        "════════════════════"
    )


# =========================================================
# !DRIVE
# =========================================================

@bot.command()
async def drive(
    ctx: commands.Context,
    destination=None
):

    user_id = ctx.author.id

    if destination is None:

        await ctx.send(
            "🚗 **DRIVE**\n\n"

            "Please provide a destination.\n\n"

            "Example:\n"
            "`!drive mainland`"
        )

        return

    destination = destination.lower()

    if destination not in LOCATIONS:

        await ctx.send(
            "❌ **DESTINATION NOT FOUND**\n\n"

            f"`{destination}` is not a registered "
            "Èko location."
        )

        return

    current_location = get_player_location(user_id)

    if current_location is None:

        if ctx.channel.name in LOCATIONS:

            current_location = ctx.channel.name

            set_player_location(
                user_id,
                current_location
            )

        else:

            await ctx.send(
                "📍 I don't know your current location yet."
            )

            return

    if current_location == destination:

        await ctx.send(
            f"📍 You are already at "
            f"{LOCATIONS[destination]}."
        )

        return

    route_key = (
        current_location,
        destination
    )

    if route_key not in ROUTES:

        await ctx.send(
            "🚧 **NO DIRECT ROUTE**\n\n"

            f"There is currently no direct route "
            f"from {LOCATIONS[current_location]} "

            f"to {LOCATIONS[destination]}."
        )

        return

    route_data = ROUTES[route_key]

    distance = route_data["distance"]

    travel_time = route_data["time"]

    await ctx.send(

        "🚗 **JOURNEY STARTED**\n"
        "════════════════════\n\n"

        f"📍 From: "
        f"{LOCATIONS[current_location]}\n"

        f"📍 To: "
        f"{LOCATIONS[destination]}\n\n"

        f"🛣️ Distance: "
        f"{distance} km\n"

        f"⏱️ Travel Time: "
        f"{travel_time} seconds\n\n"

        "🚗 You are now travelling..."
    )

    await asyncio.sleep(travel_time)

    set_player_location(
        user_id,
        destination
    )

    await ctx.send(

        "✅ **ARRIVAL CONFIRMED**\n"
        "════════════════════\n\n"

        f"🚗 {ctx.author.mention} "
        "has arrived at:\n\n"

        f"**{LOCATIONS[destination]}**\n\n"

        "📍 Your current location "
        "has been updated."
    )


# =========================================================
# !VEHICLE
# =========================================================

@bot.command()
async def vehicle(ctx: commands.Context):

    user_id = ctx.author.id

    vehicle = get_vehicle(user_id)

    if vehicle is None:

        create_vehicle(user_id)

        vehicle = get_vehicle(user_id)

    vehicle_name, fuel, fuel_capacity = vehicle

    await ctx.send(

        "🚘 **YOUR VEHICLE**\n"
        "════════════════════\n\n"

        f"🚗 Vehicle: "
        f"**{vehicle_name}**\n"

        f"⛽ Fuel: "
        f"**{fuel:.1f}L / "
        f"{fuel_capacity:.1f}L**\n"

        "🅿️ Status: **Parked**\n"

        "════════════════════"
    )


# =========================================================
# VEHICLE ERROR HANDLER
# =========================================================

@vehicle.error
async def vehicle_error(
    ctx: commands.Context,
    error
):

    await ctx.send(
        f"❌ Vehicle error: `{error}`"
    )

    print(
        f"Vehicle error: {error}"
    )


# =========================================================
# START BOT
# =========================================================

if __name__ == "__main__":

    bot.run(TOKEN)
