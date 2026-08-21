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

DEPARTURE_MESSAGE_DELETE_DELAY = 5


def get_player_location(user_id):
    return player_locations.get(user_id)


def set_player_location(user_id, location):
    player_locations[user_id] = location


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
# FIND LOCATION CHANNEL
# =========================================================

def get_location_channel(guild, location):

    return discord.utils.find(
        lambda channel:
            isinstance(channel, discord.TextChannel)
            and channel.name == location,
        guild.channels
    )


# =========================================================
# SET PLAYER LOCATION ACCESS
# =========================================================

async def update_location_permissions(
    guild,
    user,
    allowed_location
):

    for location_name in LOCATIONS:

        channel = get_location_channel(
            guild,
            location_name
        )

        if channel is None:
            continue

        overwrite = channel.overwrites_for(user)

        if location_name == allowed_location:

            overwrite.view_channel = True
            overwrite.send_messages = True
            overwrite.read_message_history = True

        else:

            overwrite.view_channel = False
            overwrite.send_messages = False
            overwrite.read_message_history = False

        try:

            await channel.set_permissions(
                user,
                overwrite=overwrite,
                reason="Èko player location system"
            )

        except discord.Forbidden:

            print(
                f"Permission denied for #{channel.name}. "
                "Check the bot role and Manage Channels permission."
            )

        except discord.HTTPException as error:

            print(
                f"Failed to update #{channel.name}: {error}"
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
            "Bot cannot delete the departure message."
        )

    except discord.HTTPException as error:

        print(
            f"Failed to delete departure message: {error}"
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

        if ctx.channel.name not in LOCATIONS:

            await ctx.send(
                "📍 **LOCATION UNKNOWN**\n\n"
                "This channel has not been registered "
                "as an Èko location."
            )

            return

        current_location = ctx.channel.name

        set_player_location(
            user_id,
            current_location
        )

        if user_id not in player_vehicles:

            create_vehicle(user_id)

        vehicle = get_vehicle(user_id)

        if vehicle[3] is None:

            update_vehicle_location(
                user_id,
                current_location
            )

        await update_location_permissions(
            ctx.guild,
            ctx.author,
            current_location
        )

    vehicle = get_vehicle(user_id)

    if vehicle is None:

        create_vehicle(user_id)

        vehicle = get_vehicle(user_id)

    vehicle_location = vehicle[3]

    await ctx.send(
        "📍 **YOUR CURRENT LOCATION**\n"
        "════════════════════\n\n"

        f"👤 Player:\n"
        f"**{LOCATIONS.get(current_location, 'Unknown')}**\n\n"

        f"🚗 Vehicle:\n"
        f"**{LOCATIONS.get(vehicle_location, 'Unknown')}**\n\n"

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
        "to travel.\n\n"

        "════════════════════"
    )


# =========================================================
# !DRIVE
# =========================================================

@bot.command()
async def drive(ctx: commands.Context, destination=None):

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
            f"`{destination}` is not a registered Èko location."
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
            f"There is currently no direct route from "
            f"{LOCATIONS[current_location]} "
            f"to {LOCATIONS[destination]}."
        )

        return

    route_data = ROUTES[route_key]

    distance = route_data["distance"]
    travel_time = route_data["time"]

    vehicle = get_vehicle(user_id)

    if vehicle is None:

        create_vehicle(user_id)

        vehicle = get_vehicle(user_id)

    vehicle_name, current_fuel, fuel_capacity, vehicle_location = vehicle

    if vehicle_location is None:

        update_vehicle_location(
            user_id,
            current_location
        )

        vehicle_location = current_location

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

    # Lock every location except the destination.
    await update_location_permissions(
        ctx.guild,
        ctx.author,
        destination
    )

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

    asyncio.create_task(
        delete_departure_message(
            departure_message
        )
    )

    await asyncio.sleep(travel_time)

    set_player_location(
        user_id,
        destination
    )

    update_vehicle_location(
        user_id,
        destination
    )

    # Destination remains the ONLY accessible location.
    await update_location_permissions(
        ctx.guild,
        ctx.author,
        destination
    )

    destination_channel = get_location_channel(
        ctx.guild,
        destination
    )

    if destination_channel is None:

        await ctx.send(
            "⚠️ **ARRIVAL CHANNEL NOT FOUND**\n\n"
            f"I could not find `#{destination}`.\n\n"
            "Your player and vehicle locations "
            "have still been updated."
        )

        return

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

    vehicle_data = get_vehicle(user_id)

    if vehicle_data is None:

        create_vehicle(user_id)

        vehicle_data = get_vehicle(user_id)

    vehicle_name, fuel, fuel_capacity, vehicle_location = vehicle_data

    await ctx.send(
        "🚘 **YOUR VEHICLE**\n"
        "════════════════════\n\n"

        f"🚗 Vehicle: **{vehicle_name}**\n"
        f"⛽ Fuel: **{fuel:.1f}L / {fuel_capacity:.1f}L**\n\n"

        f"👤 Player Location:\n"
        f"**{LOCATIONS.get(current_location, 'Unknown')}**\n\n"

        f"🚗 Vehicle Location:\n"
        f"**{LOCATIONS.get(vehicle_location, 'Unknown')}**\n\n"

        "🅿️ Status: **Parked**\n\n"

        "════════════════════"
    )


# =========================================================
# !REFUEL
# =========================================================

@bot.command()
async def refuel(ctx: commands.Context, confirmation=None):

    user_id = ctx.author.id

    player_location = get_player_location(user_id)

    if player_location is None:

        await ctx.send(
            "📍 **REFUEL FAILED**\n"
            "════════════════════\n\n"

            "Your current player location is unknown.\n\n"

            "Use `!location` first."
        )

        return

    vehicle = get_vehicle(user_id)

    if vehicle is None:

        create_vehicle(user_id)

        vehicle = get_vehicle(user_id)

    vehicle_name, current_fuel, fuel_capacity, vehicle_location = vehicle

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

    if vehicle_location != "èko-oil-and-gas":

        await ctx.send(
            "⛽ **REFUEL FAILED**\n"
            "════════════════════\n\n"

            "Your vehicle is not at **Èko Oil & Gas**.\n\n"

            f"👤 Player location:\n"
            f"**{LOCATIONS.get(player_location, 'Unknown')}**\n\n"

            f"🚗 Vehicle location:\n"
            f"**{LOCATIONS.get(vehicle_location, 'Unknown')}**\n\n"

            "Both you and your vehicle must be at "
            "**⛽ Èko Oil & Gas** to refuel."
        )

        return

    if current_fuel >= fuel_capacity:

        await ctx.send(
            "⛽ **TANK ALREADY FULL**\n\n"
            f"🚗 Vehicle: **{vehicle_name}**\n"
            f"⛽ Fuel: **{current_fuel:.1f}L / "
            f"{fuel_capacity:.1f}L**"
        )

        return

    fuel_needed = fuel_capacity - current_fuel

    total_cost = fuel_needed * FUEL_PRICE

    balance = get_balance(user_id)

    if confirmation != "confirm":

        await ctx.send(
            "⛽ **REFUEL REQUEST**\n"
            "════════════════════\n\n"

            f"🚗 Vehicle: **{vehicle_name}**\n\n"

            f"👤 Player location:\n"
            f"**{LOCATIONS[player_location]}**\n\n"

            f"🚗 Vehicle location:\n"
            f"**{LOCATIONS[vehicle_location]}**\n\n"

            f"⛽ Current fuel: **{current_fuel:.1f}L**\n"
            f"⛽ Capacity: **{fuel_capacity:.1f}L**\n"
            f"⛽ Required: **{fuel_needed:.1f}L**\n\n"

            f"💵 Fuel price: **₦{FUEL_PRICE:,.0f}/L**\n"
            f"💰 Total cost: **₦{total_cost:,.0f}**\n\n"

            f"💳 Balance: **₦{balance:,.0f}**\n\n"

            "To confirm, use:\n"
            "`!refuel confirm`\n\n"

            "════════════════════"
        )

        return

    if balance < total_cost:

        await ctx.send(
            "❌ **INSUFFICIENT FUNDS**\n"
            "════════════════════\n\n"

            f"💰 Required: **₦{total_cost:,.0f}**\n"
            f"💳 Your balance: **₦{balance:,.0f}**\n\n"

            "You cannot afford this refuel."
        )

        return

    new_balance = balance - total_cost

    update_balance(
        user_id,
        new_balance
    )

    update_fuel(
        user_id,
        fuel_capacity
    )

    await ctx.send(
        "⛽ **REFUEL COMPLETE**\n"
        "════════════════════\n\n"

        f"🚗 Vehicle: **{vehicle_name}**\n\n"

        f"👤 Player location:\n"
        f"**{LOCATIONS[player_location]}**\n\n"

        f"🚗 Vehicle location:\n"
        f"**{LOCATIONS[vehicle_location]}**\n\n"

        f"⛽ Previous fuel: **{current_fuel:.1f}L**\n"
        f"⛽ Added: **{fuel_needed:.1f}L**\n"
        f"⛽ Current fuel: **{fuel_capacity:.1f}L / "
        f"{fuel_capacity:.1f}L**\n\n"

        f"💰 Paid: **₦{total_cost:,.0f}**\n"
        f"💳 Remaining balance: **₦{new_balance:,.0f}**\n\n"

        "════════════════════"
    )


# =========================================================
# !BALANCE
# =========================================================

@bot.command()
async def balance(ctx: commands.Context):

    user_id = ctx.author.id

    current_balance = get_balance(user_id)

    await ctx.send(
        "💳 **TEST TRANSPORT BALANCE**\n"
        "════════════════════\n\n"

        f"💰 Balance: **₦{current_balance:,.0f}**\n\n"

        "This is a temporary Transport Bot balance.\n"
        "It is NOT connected to the actual Èko economy.\n\n"

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
# ===============
