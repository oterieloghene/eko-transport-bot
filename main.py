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
        }


def get_vehicle(user_id):

    vehicle = player_vehicles.get(user_id)

    if vehicle is None:
        return None

    return (
        vehicle["vehicle_name"],
        vehicle["fuel"],
        vehicle["fuel_capacity"],
    )


def update_fuel(user_id, fuel):

    if user_id in player_vehicles:
        player_vehicles[user_id]["fuel"] = fuel


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

    # Get vehicle
    vehicle = get_vehicle(user_id)

    if vehicle is None:

        create_vehicle(user_id)

        vehicle = get_vehicle(user_id)

    vehicle_name, current_fuel, fuel_capacity = vehicle

    # Calculate fuel
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

    await ctx.send(
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

    await asyncio.sleep(travel_time)

    set_player_location(
        user_id,
        destination
    )

    destination_channel = discord.utils.get(
        ctx.guild.text_channels,
        name=destination
    )

    if destination_channel is None:

        await ctx.send(
            "⚠️ **ARRIVAL CHANNEL NOT FOUND**\n\n"
            f"I could not find `#{destination}`.\n\n"
            "Your game location has still been updated."
        )

        return

    await destination_channel.send(
        "✅ **ARRIVAL CONFIRMED**\n"
        "════════════════════\n\n"

        f"🚗 {ctx.author.mention} has arrived at:\n\n"
        f"**{LOCATIONS[destination]}**\n\n"

        f"⛽ Fuel remaining: **{remaining_fuel:.1f}L**\n\n"

        "📍 Your current location has been updated."
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

    current_location = get_player_location(user_id)

    if current_location in LOCATIONS:

        location_name = LOCATIONS[current_location]

    else:

        location_name = "📍 Unknown"

    await ctx.send(
        "🚘 **YOUR VEHICLE**\n"
        "════════════════════\n\n"

        f"🚗 Vehicle: **{vehicle_name}**\n"
        f"⛽ Fuel: **{fuel:.1f}L / {fuel_capacity:.1f}L**\n"
        f"📍 Location: **{location_name}**\n"
        "🅿️ Status: **Parked**\n\n"

        "════════════════════"
    )


# =========================================================
# !REFUEL
# =========================================================

@bot.command()
async def refuel(ctx: commands.Context, confirmation=None):

    user_id = ctx.author.id

    # Must be at the fuel station
    if ctx.channel.name != "èko-oil-and-gas":

        current_location = get_player_location(user_id)

        if current_location in LOCATIONS:

            location_name = LOCATIONS[current_location]

        else:

            location_name = "📍 Unknown"

        await ctx.send(
            "⛽ **REFUEL FAILED**\n"
            "════════════════════\n\n"

            "You must be at **Èko Oil & Gas** "
            "to refuel your vehicle.\n\n"

            f"📍 Current location: **{location_name}**\n\n"

            "════════════════════"
        )

        return

    vehicle = get_vehicle(user_id)

    if vehicle is None:

        create_vehicle(user_id)

        vehicle = get_vehicle(user_id)

    vehicle_name, current_fuel, fuel_capacity = vehicle

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

    # Confirmation
    if confirmation != "confirm":

        await ctx.send(
            "⛽ **REFUEL REQUEST**\n"
            "════════════════════\n\n"

            f"🚗 Vehicle: **{vehicle_name}**\n"
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

    # Check balance
    if balance < total_cost:

        await ctx.send(
            "❌ **INSUFFICIENT FUNDS**\n"
            "════════════════════\n\n"

            f"💰 Required: **₦{total_cost:,.0f}**\n"
            f"💳 Your balance: **₦{balance:,.0f}**\n\n"

            "You cannot afford this refuel."
        )

        return

    # Deduct money
    new_balance = balance - total_cost

    update_balance(
        user_id,
        new_balance
    )

    # Fill tank
    update_fuel(
        user_id,
        fuel_capacity
    )

    await ctx.send(
        "⛽ **REFUEL COMPLETE**\n"
        "════════════════════\n\n"

        f"🚗 Vehicle: **{vehicle_name}**\n"

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
# =========================================================

if __name__ == "__main__":

    bot.run(TOKEN)
