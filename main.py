import os
import asyncio
import discord
from discord.ext import commands


# =========================================================
# DISCORD TOKEN
# =========================================================

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_BOT_TOKEN is missing.")


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
# TEMPORARY TEST DATA
# =========================================================

player_locations = {}
player_vehicles = {}
player_balances = {}

STARTING_BALANCE = 200_000
FUEL_PRICE = 1_300
FUEL_CONSUMPTION = 0.5

# How long the departure message remains visible
DEPARTURE_MESSAGE_DELETE_DELAY = 5


# =========================================================
# PLAYER LOCATION
# =========================================================

def get_player_location(user_id):

    return player_locations.get(user_id)


def set_player_location(user_id, location):

    player_locations[user_id] = location


# =========================================================
# VEHICLE
# =========================================================

def create_vehicle(user_id, vehicle_name="Toyota Camry"):

    if user_id not in player_vehicles:

        player_vehicles[user_id] = {
            "vehicle_name": vehicle_name,
            "fuel": 50.0,
            "fuel_capacity": 60.0,
            "location": get_player_location(user_id),
        }


def get_vehicle(user_id):

    vehicle = player_vehicles.get(user_id)

    if vehicle is None:
        return None

    return (
        vehicle["vehicle_name"],
        vehicle["fuel"],
        vehicle["fuel_capacity"],
        vehicle["location"],
    )


def update_fuel(user_id, fuel):

    if user_id in player_vehicles:
        player_vehicles[user_id]["fuel"] = fuel


def update_vehicle_location(user_id, location):

    if user_id in player_vehicles:
        player_vehicles[user_id]["location"] = location


# =========================================================
# BALANCE
# =========================================================

def get_balance(user_id):

    if user_id not in player_balances:
        player_balances[user_id] = STARTING_BALANCE

    return player_balances[user_id]


def update_balance(user_id, amount):

    player_balances[user_id] = amount


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
# CHANNEL LOCKING
# =========================================================

async def lock_travel_channels(guild, user, destination):

    for location_channel_name in LOCATIONS:

        channel = discord.utils.get(
            guild.text_channels,
            name=location_channel_name
        )

        if channel is None:
            continue

        # Destination stays accessible.
        if location_channel_name == destination:
            continue

        try:

            await channel.set_permissions(
                user,
                view_channel=False,
                send_messages=False
            )

        except discord.Forbidden:

            print(
                f"Could not lock #{location_channel_name} "
                f"for {user}."
            )

        except discord.HTTPException as error:

            print(
                f"Discord error locking "
                f"#{location_channel_name}: {error}"
            )


async def unlock_travel_channels(guild, user):

    for location_channel_name in LOCATIONS:

        channel = discord.utils.get(
            guild.text_channels,
            name=location_channel_name
        )

        if channel is None:
            continue

        try:

            # Remove our user-specific override.
            await channel.set_permissions(
                user,
                overwrite=None
            )

        except discord.Forbidden:

            print(
                f"Could not unlock #{location_channel_name} "
                f"for {user}."
            )

        except discord.HTTPException as error:

            print(
                f"Discord error unlocking "
                f"#{location_channel_name}: {error}"
            )


# =========================================================
# DELETE DEPARTURE MESSAGE
# =========================================================

async def delete_departure_message(message):

    await asyncio.sleep(
        DEPARTURE_MESSAGE_DELETE_DELAY
    )

    try:

        await message.delete()

    except discord.NotFound:
        pass

    except discord.Forbidden:
        print(
            "Bot does not have permission "
            "to delete the departure message."
        )

    except discord.HTTPException as error:
        print(
            f"Could not delete departure message: {error}"
        )


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

            # Create vehicle at the same location.
            if user_id not in player_vehicles:
                create_vehicle(user_id)

        else:

            await ctx.send(
                "📍 **LOCATION UNKNOWN**\n\n"
                "This channel has not been registered "
                "as an Èko location."
            )

            return

    await ctx.send(
        "📍 **YOUR CURRENT LOCATION**\n"
        "════════════════════\n\n"
        f"You are currently at:\n"
        f"**{LOCATIONS[current_location]}**\n\n"
        "════════════════════"
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
async def drive(ctx: commands.Context, destination=None):

    user_id = ctx.author.id

    # =====================================================
    # DESTINATION CHECK
    # =====================================================

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
            f"`{destination}` is not a registered Èko location."
        )

        return

    # =====================================================
    # CURRENT PLAYER LOCATION
    # =====================================================

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

    # =====================================================
    # ALREADY THERE
    # =====================================================

    if current_location == destination:

        await ctx.send(
            f"📍 You are already at "
            f"{LOCATIONS[destination]}."
        )

        return

    # =====================================================
    # ROUTE CHECK
    # =====================================================

    route_key = (
        current_location,
        destination
    )

    if route_key not in ROUTES:

        await ctx.send(
            "🚧 **NO DIRECT ROUTE**\n\n"
            f"There is currently no direct route from "
            f"{LOCATIONS[current_location]} "
            f"to {LOCATIONS[destination]}."
        )

        return

    route_data = ROUTES[route_key]

    distance = route_data["distance"]
    travel_time = route_data["time"]

    # =====================================================
    # GET VEHICLE
    # =====================================================

    vehicle = get_vehicle(user_id)

    if vehicle is None:

        create_vehicle(user_id)

        vehicle = get_vehicle(user_id)

    vehicle_name, current_fuel, fuel_capacity, vehicle_location = vehicle

    # =====================================================
    # VEHICLE LOCATION CHECK
    # =====================================================

    if vehicle_location is None:

        update_vehicle_location(
            user_id,
            current_location
        )

        vehicle_location = current_location

    # =====================================================
    # VEHICLE MUST BE WITH PLAYER
    # =====================================================

    if vehicle_location != current_location:

        await ctx.send(
            "🚗 **VEHICLE LOCATION ERROR**\n"
            "════════════════════\n\n"

            f"👤 Player location:\n"
            f"**{LOCATIONS.get(current_location, 'Unknown')}**\n\n"

            f"🚗 Vehicle location:\n"
            f"**{LOCATIONS.get(vehicle_location, 'Unknown')}**\n\n"

            "Your vehicle must be at your current "
            "location before you can drive it."
        )

        return

    # =====================================================
    # CALCULATE FUEL
    # =====================================================

    fuel_used = distance * FUEL_CONSUMPTION

    if current_fuel < fuel_used:

        await ctx.send(
            "⛽ **NOT ENOUGH FUEL**\n\n"
            f"🚗 Vehicle: **{vehicle_name}**\n"
            f"⛽ Current fuel: **{current_fuel:.1f}L**\n"
            f"⛽ Required fuel: **{fuel_used:.1f}L**\n\n"
            "Please refuel before travelling."
        )

        return

    remaining_fuel = current_fuel - fuel_used

    update_fuel(
        user_id,
        remaining_fuel
    )

    # =====================================================
    # LOCK ALL LOCATION CHANNELS EXCEPT DESTINATION
    # =====================================================

    if ctx.guild is not None:

        await lock_travel_channels(
            ctx.guild,
            ctx.author,
            destination
        )

    # =====================================================
    # JOURNEY STARTED
    # =====================================================

    departure_message = await ctx.send(
        "🚗 **JOURNEY STARTED**\n"
        "════════════════════\n\n"

        f"📍 From: **{LOCATIONS[current_location]}**\n"
        f"📍 To: **{LOCATIONS[destination]}**\n\n"

        f"🚗 Vehicle: **{vehicle_name}**\n"
        f"🛣️ Distance: **{distance} km**\n"
        f"⛽ Fuel used: **{fuel_used:.1f}L**\n"
        f"⛽ Remaining fuel: **{remaining_fuel:.1f}L**\n"
        f"⏱️ Travel Time: **{travel_time} seconds**\n\n"

        "🚗 You are now travelling..."
    )

    # Delete departure message after 5 seconds.
    asyncio.create_task(
        delete_departure_message(
            departure_message
        )
    )

    # =====================================================
    # TRAVEL TIME
    # =====================================================

    await asyncio.sleep(travel_time)

    # =====================================================
    # UPDATE PLAYER LOCATION
    # =====================================================

    set_player_location(
        user_id,
        destination
    )

    # =====================================================
    # UPDATE VEHICLE LOCATION
    # =====================================================

    update_vehicle_location(
        user_id,
        destination
    )

    # =====================================================
    # ARRIVAL CHANNEL
    # =====================================================

    destination_channel = discord.utils.get(
        ctx.guild.text_channels,
        name=destination
    )

    if destination_channel is None:

        # Unlock channels if destination channel doesn't exist.
        if ctx.guild is not None:

            await unlock_travel_channels(
                ctx.guild,
                ctx.author
            )

        await ctx.send(
            "⚠️ **ARRIVAL CHANNEL NOT FOUND**\n\n"
            f"I could not find `#{destination}`.\n\n"
            "Your player and vehicle locations have "
            "still been updated."
        )

        return

    # =====================================================
    # UNLOCK ALL LOCATION CHANNELS
    # =====================================================

    if ctx.guild is not None:

        await unlock_travel_channels(
            ctx.guild,
            ctx.author
        )

    # =====================================================
    # ARRIVAL CONFIRMED
    # =====================================================

    await destination_channel.send(
        "✅ **ARRIVAL CONFIRMED**\n"
        "════════════════════\n\n"

        f"🚗 {ctx.author.mention} has arrived at:\n\n"
        f"**{LOCATIONS[destination]}**\n\n"

        f"⛽ Fuel remaining: **{remaining_fuel:.1f}L**\n\n"

        "👤 Player location: **Updated**\n"
        "🚗 Vehicle location: **Updated**\n\n"

        "📍 Your current location has been updated."
    )


# =========================================================
# !VEHICLE
# =========================================================

@bot.command()
async def vehicle(ctx: commands.Context):

    user_id = ctx.author.id

    # =====================================================
    # GET PLAYER LOCATION
    # =====================================================

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
                "Your current game location has not been established."
            )

            return

    # =====================================================
    # GET VEHICLE
    # =====================================================

    vehicle_data = get_vehicle(user_id)

    if vehicle_data is None:

        create_vehicle(user_id)

        vehicle_data = get_vehicle(user_id)

    vehicle_name, fuel, fuel_capacity, vehicle_location = vehicle_data

    player_location_name = LOCATIONS.get(
        current_location,
        "📍 Unknown"
    )

    vehicle_location_name = LOCATIONS.get(
        vehicle_location,
        "📍 Unknown"
    )

    await ctx.send(
        "🚘 **YOUR VEHICLE**\n"
        "════════════════════\n\n"

        f"🚗 Vehicle: **{vehicle_name}**\n"
        f"⛽ Fuel: **{fuel:.1f}L / {fuel_capacity:.1f}L**\n\n"

        f"👤 Player Location:\n"
        f"**{player_location_name}**\n\n"

        f"🚗 Vehicle Location:\n"
        f"**{vehicle_location_name}**\n\n"

        "🅿️ Status: **Parked**\n\n"

        "════════════════════"
    )


# =========================================================
# !REFUEL
# =========================================================

@bot.command()
async def refuel(ctx: commands.Context, confirmation=None):

    user_id = ctx.author.id

    # =====================================================
    # GET PLAYER LOCATION
    # =====================================================

    player_location = get_player_location(user_id)

    if player_location is None:

        await ctx.send(
            "📍 **REFUEL FAILED**\n"
            "════════════════════\n\n"

            "Your current player location is unknown.\n\n"

            "Use `!location` first."
        )

        return

    # =====================================================
    # GET VEHICLE
    # =====================================================

    vehicle = get_vehicle(user_id)

    if vehicle is None:

        create_vehicle(user_id)

        vehicle = get_vehicle(user_id)

    vehicle_name, current_fuel, fuel_capacity, vehicle_location = vehicle

    # =====================================================
    # PLAYER MUST BE AT ÈKO OIL & GAS
    # =====================================================

    if player_location != "èko-oil-and-gas":

        await ctx.send(
            "⛽ **REFUEL FAILED**\n"
            "════════════════════\n\n"

            "You must be at **Èko Oil & Gas** "
            "to refuel your vehicle.\n\n"

            f"👤 Your location:\n"
            f"**{LOCATIONS.get(player_location, 'Unknown')}**\n\n"

            "Required location:\n"
            "**⛽ Èko Oil & Gas**"
        )

        return

    # =====================================================
    # VEHICLE MUST ALSO BE AT ÈKO OIL & GAS
    # =====================================================

    if vehicle_location != "èko-oil-and-gas":

        await ctx.send(
            "⛽ **REFUEL FAILED**\n"
            "════════════════════\n\n"

         
