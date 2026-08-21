import os import asyncio

import discord from discord.ext import commands

import database

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

if not TOKEN: raise RuntimeError( "DISCORD_BOT_TOKEN is missing. Add it as a Replit Secret, then run the bot again." )

intents = discord.Intents.default() intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

=========================
EKO LOCATIONS
=========================
LOCATIONS = { "help-desk": "🛂 Immigration Office", "èko-lobby": "🟢 Èko Green Zone", "mayors-penthouse": "🏛️ Mayor's Penthouse", "deputys-residence": "🏠 Deputy's Residence", "banking-hall": "🏦 Banking Hall", "mainland": "🌍 Mainland", "èko-oil-and-gas": "⛽ Èko Oil & Gas", }

=========================
DATABASE
=========================
database.setup_database()

=========================
ROUTES
=========================
ROUTES = { ("banking-hall", "èko-lobby"): { "distance": 3, "time": 10, },

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

=========================
BOT READY
=========================
@bot.event async def on_ready(): print(f"Bot is online as {bot.user}")

=========================
PING
=========================
@bot.command() async def ping(ctx: commands.Context): """Reply when someone uses !ping.""" await ctx.send("Pong!")

=========================
LOCATION
=========================
@bot.command() async def location(ctx: commands.Context): """Show the player's current location."""

user_id = ctx.author.id
current_location = database.get_player_location(user_id)
if current_location is None:
    if ctx.channel.name in LOCATIONS:
        current_location = ctx.channel.name
        database.set_player_location(user_id, current_location)
    else:
        await ctx.send(
            "📍 **LOCATION UNKNOWN**\n\n"
            "This channel has not been registered as an Èko location."
        )
        return
await ctx.send(
    f"📍 **YOUR CURRENT LOCATION**\n\n"
    f"You are currently at:\n"
    f"**{LOCATIONS[current_location]}**"
)
=========================
ROUTES
=========================
@bot.command() async def route(ctx: commands.Context): """Show available transportation locations."""

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
    "Use `!drive <destination>` to travel.\n"
    "════════════════════"
)
=========================
DRIVE
=========================
@bot.command() async def drive(ctx: commands.Context, destination=None): """Drive from the current location to another location."""

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
current_location = database.get_player_location(user_id)
if current_location is None:
    if ctx.channel.name in LOCATIONS:
        current_location = ctx.channel.name
        database.set_player_location(user_id, current_location)
    else:
        await ctx.send(
            "📍 I don't know your current location yet."
        )
        return
if current_location == destination:
    await ctx.send(
        f"📍 You are already at {LOCATIONS[destination]}."
    )
    return
route_key = (current_location, destination)
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
await ctx.send(
    "🚗 **JOURNEY STARTED**\n"
    "════════════════════\n\n"
    f"📍 From: {LOCATIONS[current_location]}\n"
    f"📍 To: {LOCATIONS[destination]}\n\n"
    f"🛣️ Distance: {distance} km\n"
    f"⏱️ Travel Time: {travel_time} seconds\n\n"
    "🚗 You are now travelling..."
)
await asyncio.sleep(travel_time)
database.set_player_location(user_id, destination)
await ctx.send(
    "✅ **ARRIVAL CONFIRMED**\n"
    "════════════════════\n\n"
    f"🚗 {ctx.author.mention} has arrived at:\n\n"
    f"**{LOCATIONS[destination]}**\n\n"
    "📍 Your current location has been updated."
)
=========================
START BOT
=========================
@bot.command() async def vehicle(ctx: commands.Context): """Show the player's vehicle."""

user_id = ctx.author.id
# Check if the player already has a vehicle
vehicle = database.get_vehicle(user_id)
# If they don't, give them the test vehicle
if vehicle is None:
    database.create_vehicle(user_id)
    vehicle = database.get_vehicle(user_id)
vehicle_name, fuel, fuel_capacity = vehicle
await ctx.send(
    "🚘 **YOUR VEHICLE**\n"
    "════════════════════\n\n"
    f"🚗 Vehicle: **{vehicle_name}**\n"
    f"⛽ Fuel: **{fuel:.1f}L / {fuel_capacity:.1f}L**\n"
    "🅿️ Status: **Parked**\n"
    "════════════════════"
)
@vehicle.error async def vehicle_error(ctx: commands.Context, error): await ctx.send(f"❌ Vehicle error: {error}") print(f"Vehicle error: {error}")

if name == "main": bot.run(TOKEN)
  
