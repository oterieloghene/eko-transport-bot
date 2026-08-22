import os
import asyncio
import math
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

# Real calculated distance is used for fuel.
# Travel time is compressed for testing.
#
# 1 km = 2 seconds
#
# Minimum: 1 second
# Maximum: 60 seconds
TIME_PER_KM = 2

MIN_TRAVEL_TIME = 1
MAX_TRAVEL_TIME = 60

DEPARTURE_MESSAGE_DELETE_DELAY = 5


# =========================================================
# LOCATION REGISTRY
#
# These are the CODE NAMES.
#
# The "channel" value is the actual Discord channel.
# =========================================================

LOCATIONS = {

    # =====================================================
    # ISLAND
    # =====================================================

    "mayor-villa": {
        "display_name": "🏛️ Mayor's Villa",
        "channel": "mayor's-penthouse",
        "zone": "island",
        "x": 10,
        "y": 10,
    },

    "deputy-villa": {
        "display_name": "🏠 Deputy's Villa",
        "channel": "deputy's-residence",
        "zone": "island",
        "x": 12,
        "y": 10,
    },

    "guesthouse1": {
        "display_name": "🏡 Villa Guesthouse 1",
        "channel": "villa-guesthouse 1",
        "zone": "island",
        "x": 14,
        "y": 10,
    },

    "guesthouse2": {
        "display_name": "🏡 Villa Guesthouse 2",
        "channel": "villa-guesthouse 2",
        "zone": "island",
        "x": 14,
        "y": 12,
    },

    "chief-staff": {
        "display_name": "🏛️ Chief of Staff",
        "channel": "chief-of-staff",
        "zone": "island",
        "x": 10,
        "y": 14,
    },

    "council": {
        "display_name": "🏛️ Èko Council",
        "channel": "eko-council",
        "zone": "island",
        "x": 12,
        "y": 14,
    },

    "justice-ministry": {
        "display_name": "⚖️ Ministry of Justice",
        "channel": "minister-of-justice",
        "zone": "island",
        "x": 14,
        "y": 14,
    },

    "home-ministry": {
        "display_name": "🏠 Ministry of Home Affairs & Housing",
        "channel": "minister-of-home-affairs-housing",
        "zone": "island",
        "x": 16,
        "y": 14,
    },

    "agric-ministry": {
        "display_name": "🌾 Ministry of Agriculture",
        "channel": "minister-of-agriculture",
        "zone": "island",
        "x": 18,
        "y": 14,
    },

    "clerk-office": {
        "display_name": "⚖️ Clerk Office",
        "channel": "clerk-office",
        "zone": "island",
        "x": 10,
        "y": 18,
    },

    "bank": {
        "display_name": "🏦 Bank",
        "channel": "banking-hall",
        "zone": "island",
        "x": 12,
        "y": 18,
    },

    "hospital": {
        "display_name": "🏥 Hospital",
        "channel": "hospital-lobby",
        "zone": "island",
        "x": 14,
        "y": 18,
    },

    "police": {
        "display_name": "👮 Police",
        "channel": "precint-reception",
        "zone": "island",
        "x": 16,
        "y": 18,
    },

    "university": {
        "display_name": "🎓 University",
        "channel": "vice-chancellors-office",
        "zone": "island",
        "x": 18,
        "y": 18,
    },

    "lobby": {
        "display_name": "🟢 Èko Lobby",
        "channel": "eko-lobby",
        "zone": "island",
        "x": 10,
        "y": 22,
    },

    "clubhouse": {
        "display_name": "🏠 Èko Clubhouse",
        "channel": "eko-clubhouse",
        "zone": "island",
        "x": 14,
        "y": 22,
    },

    "chapel": {
        "display_name": "⛪ Èko City Chapel",
        "channel": "eko-city-chapel",
        "zone": "island",
        "x": 18,
        "y": 22,
    },


    # =====================================================
    # MAINLAND
    # =====================================================

    "mainland": {
        "display_name": "🌍 Mainland",
        "channel": "mainland",
        "zone": "mainland",
        "x": 0,
        "y": 0,
    },

    "immigration": {
        "display_name": "🛂 Immigration Office",
        "channel": "help-desk",
        "zone": "mainland",
        "x": 3,
        "y": 1,
    },

    "market": {
        "display_name": "🛒 Market",
        "channel": "eko-market",
        "zone": "mainland",
        "x": 5,
        "y": 2,
    },

    "restaurant": {
        "display_name": "🍽️ Èko Restaurant",
        "channel": "èko-restaurant",
        "zone": "mainland",
        "x": 7,
        "y": 2,
    },

    "fuel-station": {
        "display_name": "⛽ Fuel Station",
        "channel": "èko-oil-and-gas",
        "zone": "mainland",
        "x": 9,
        "y": 2,
    },

    "mall": {
        "display_name": "🏬 Èko Mall",
        "channel": "èko-mall",
        "zone": "mainland",
        "x": 11,
        "y": 2,
    },

    "depot": {
        "display_name": "📦 Depot",
        "channel": "depot",
        "zone": "mainland",
        "x": 5,
        "y": -2,
    },

    "dealership": {
        "display_name": "🚗 Car Dealership",
        "channel": "dealership",
        "zone": "mainland",
        "x": 7,
        "y": -2,
    },

    "taxi-company": {
        "display_name": "🚕 Taxi Company",
        "channel": "taxi-company",
        "zone": "mainland",
        "x": 9,
        "y": -2,
    },

    "auto-repair": {
        "display_name": "🔧 Auto Repair",
        "channel": "auto-repair",
        "zone": "mainland",
        "x": 11,
        "y": -2,
    },

    "travel-agency": {
        "display_name": "✈️ Travel Agency",
        "channel": "travel-agency",
        "zone": "mainland",
        "x": 3,
        "y": -2,
    },


    # =====================================================
    # GHETTO
    # =====================================================

    "ghetto": {
        "display_name": "🏚️ Ghetto",
        "channel": "ghetto",
        "zone": "ghetto",
        "x": -10,
        "y": -5,
    },


    # =====================================================
    # FARMLAND
    # =====================================================

    "farmland": {
        "display_name": "🌾 Farmland",
        "channel": "farmland",
        "zone": "farmland",
        "x": -15,
        "y": -10,
    },
}


# =========================================================
# OVERSEAS
#
# NOT PART OF !DRIVE
# =========================================================

OVERSEAS_LOCATIONS = {
    "dubai": {
        "display_name": "🇦🇪 Dubai",
        "channel": "dubai",
    },

    "maldives": {
        "display_name": "🇲🇻 Maldives",
        "channel": "maldives",
    },
}


# =========================================================
# TRANSIT CENTER
#
# IMPORTANT:
# Completely excluded from transportation.
# =========================================================

TRANSPORT_EXCLUDED_CHANNELS = {
    "transit-center"
}


# =========================================================
# PLAYER DATA
# =========================================================

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
# LOCATION LOOKUP
# =========================================================

def get_location_channel(guild, location_id):

    if location_id not in LOCATIONS:
        return None

    channel_name = LOCATIONS[
        location_id
    ]["channel"]

    return discord.utils.find(
        lambda channel:
            isinstance(channel, discord.TextChannel)
            and channel.name.lower() == channel_name.lower(),
        guild.channels
    )


def get_location_from_channel(channel):

    if not isinstance(channel, discord.TextChannel):
        return None

    for location_id, data in LOCATIONS.items():

        if (
            channel.name.lower()
            == data["channel"].lower()
        ):

            return location_id

    return None


# =========================================================
# DESTINATION RESOLVER
# =========================================================

def resolve_location(identifier):

    identifier = identifier.lower().strip()

    if identifier in LOCATIONS:
        return identifier

    aliases = {

        "mayor": "mayor-villa",

        "deputy": "deputy-villa",

        "guesthouse-1": "guesthouse1",
        "guesthouse-2": "guesthouse2",

        "chief": "chief-staff",

        "justice": "justice-ministry",

        "home": "home-ministry",

        "agriculture": "agric-ministry",
        "agric": "agric-ministry",

        "clerk": "clerk-office",

        "bank": "bank",

        "hospital": "hospital",

        "police": "police",

        "university": "university",

        "lobby": "lobby",

        "clubhouse": "clubhouse",

        "chapel": "chapel",

        "immigration": "immigration",

        "market": "market",

        "restaurant": "restaurant",

        "fuel": "fuel-station",
        "gas": "fuel-station",

        "mall": "mall",

        "depot": "depot",

        "cars": "dealership",
        "dealership": "dealership",

        "taxi": "taxi-company",

        "repair": "auto-repair",

        "travel": "travel-agency",

        "farm": "farmland",
    }

    return aliases.get(identifier)


# =========================================================
# DISTANCE
# =========================================================

def calculate_distance(origin, destination):

    origin_data = LOCATIONS[origin]
    destination_data = LOCATIONS[destination]

    dx = (
        destination_data["x"]
        - origin_data["x"]
    )

    dy = (
        destination_data["y"]
        - origin_data["y"]
    )

    return math.sqrt(
        dx ** 2 +
        dy ** 2
    )


# =========================================================
# DIRECT ROUTE RULES
# =========================================================

def is_direct_route(origin, destination):

    if origin not in LOCATIONS:
        return False

    if destination not in LOCATIONS:
        return False

    if origin == destination:
        return False

    origin_zone = LOCATIONS[
        origin
    ]["zone"]

    destination_zone = LOCATIONS[
        destination
    ]["zone"]

    # =====================================================
    # SAME ZONE
    # =====================================================

    if origin_zone == destination_zone:
        return True

    # =====================================================
    # ISLAND → MAINLAND
    #
    # Only the MAINLAND access point.
    # =====================================================

    if origin_zone == "island":
        if destination_zone == "mainland":
            return destination == "mainland"

    # =====================================================
    # MAINLAND → ISLAND
    # =====================================================

    if origin_zone == "mainland":
        if destination_zone == "island":
            return origin == "mainland"

    # =====================================================
    # ISLAND ↔ GHETTO
    # =====================================================

    if {
        origin_zone,
        destination_zone
    } == {"island", "ghetto"}:

        return (
            origin == "ghetto"
            or destination == "ghetto"
        )

    # =====================================================
    # ISLAND ↔ FARMLAND
    # =====================================================

    if {
        origin_zone,
        destination_zone
    } == {"island", "farmland"}:

        return (
            origin == "farmland"
            or destination == "farmland"
        )

    # =====================================================
    # MAINLAND ↔ GHETTO
    # =====================================================

    if {
        origin_zone,
        destination_zone
    } == {"mainland", "ghetto"}:

        return (
            origin == "mainland"
            or destination == "mainland"
        )

    # =====================================================
    # MAINLAND ↔ FARMLAND
    # =====================================================

    if {
        origin_zone,
        destination_zone
    } == {"mainland", "farmland"}:

        return (
            origin == "mainland"
            or destination == "mainland"
        )

    # =====================================================
    # GHETTO ↔ FARMLAND
    # =====================================================

    if {
        origin_zone,
        destination_zone
    } == {"ghetto", "farmland"}:

        return True

    return False


# =========================================================
# DIRECT DESTINATIONS
# =========================================================

def get_direct_destinations(origin):

    destinations = []

    for destination in LOCATIONS:

        if destination == origin:
            continue

        if is_direct_route(
            origin,
            destination
        ):

            destinations.append(
                destination
            )

    return destinations


# =========================================================
# PERMISSION SYSTEM
#
# During travel:
#     ALL channels = READ ONLY
#
# When arrived:
#     ONLY arrival channel = WRITABLE
#     EVERYTHING ELSE = READ ONLY
# =========================================================

async def update_location_permissions(
    guild,
    user,
    current_location=None
):

    for location_id in LOCATIONS:

        channel = get_location_channel(
            guild,
            location_id
        )

        if channel is None:
            continue

        overwrite = channel.overwrites_for(
            user
        )

        # Player can always see locations.
        overwrite.view_channel = True
        overwrite.read_message_history = True

        # =================================================
        # CURRENT LOCATION
        # =================================================

        if (
            current_location is not None
            and location_id == current_location
        ):

            overwrite.send_messages = True

        # =================================================
        # EVERY OTHER LOCATION
        # =================================================

        else:

            overwrite.send_messages = False

        try:

            await channel.set_permissions(
                user,
                overwrite=overwrite,
                reason="Èko location transportation system"
            )

        except discord.Forbidden:

            print(
                f"Permission denied for #{channel.name}."
            )

        except discord.HTTPException as error:

            print(
                f"Permission error for "
                f"#{channel.name}: {error}"
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

    except (
        discord.NotFound,
        discord.Forbidden
    ):

        pass

    except discord.HTTPException as error:

        print(
            f"Failed to delete message: {error}"
        )


# =========================================================
# BOT READY
# =========================================================

@bot.event
async def on_ready():

    print(
        f"Bot is online as {bot.user}"
    )

    print(
        "Transportation commands:"
    )

    for command in bot.commands:

        print(
            f"!{command.name}"
        )


# =========================================================
# !PING
# =========================================================

@bot.command()
async def ping(ctx):

    await ctx.send(
        "Pong!"
    )


# =========================================================
# !LOCATION
# =========================================================

@bot.command()
async def location(ctx):

    user_id = ctx.author.id

    current_location = get_player_location(
        user_id
    )

    # =====================================================
    # ESTABLISH INITIAL LOCATION
    # =====================================================

    if current_location is None:

        current_location = get_location_from_channel(
            ctx.channel
        )

        if current_location is None:

            await ctx.send(
                "📍 **LOCATION UNKNOWN**\n\n"
                "This is not a registered "
                "transportation location."
            )

            return

        set_player_location(
            user_id,
            current_location
        )

        if user_id not in player_vehicles:

            create_vehicle(
                user_id
            )

        vehicle = get_vehicle(
            user_id
        )

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

    vehicle = get_vehicle(
        user_id
    )

    if vehicle is None:

        create_vehicle(
            user_id
        )

        vehicle = get_vehicle(
            user_id
        )

    vehicle_location = vehicle[3]

    current_data = LOCATIONS[
        current_location
    ]

    vehicle_data = LOCATIONS.get(
        vehicle_location
    )

    await ctx.send(
        "📍 **YOUR CURRENT LOCATION**\n"
        "════════════════════\n\n"

        f"👤 Player Location:\n"
        f"**{current_data['display_name']}**\n\n"

        f"🗺️ Zone:\n"
        f"**{current_data['zone'].title()}**\n\n"

        f"🚗 Vehicle Location:\n"
        f"**{vehicle_data['display_name'] if vehicle_data else 'Unknown'}**\n\n"

        "════════════════════"
    )


# =========================================================
# !ROUTE
# =========================================================

@bot.command()
async def route(ctx):

    user_id = ctx.author.id

    current_location = get_player_location(
        user_id
    )

    if current_location is None:

        current_location = get_location_from_channel(
            ctx.channel
        )

        if current_location is None:

            await ctx.send(
                "📍 **LOCATION UNKNOWN**\n\n"
                "Use `!location` first."
            )

            return

        set_player_location(
            user_id,
            current_location
        )

    destinations = get_direct_destinations(
        current_location
    )

    current_data = LOCATIONS[
        current_location
    ]

    if not destinations:

        await ctx.send(
            "🗺️ **NO DIRECT ROUTES**\n\n"
            f"Current location:\n"
            f"**{current_data['display_name']}**"
        )

        return

    lines = []

    for destination in destinations:

        destination_data = LOCATIONS[
            destination
        ]

        distance = calculate_distance(
            current_location,
            destination
        )

        lines.append(
            f"• `{destination}` — "
            f"{destination_data['display_name']} "
            f"— **{distance:.1f} km**"
        )

    await ctx.send(
        "🗺️ **AVAILABLE DIRECT ROUTES**\n"
        "════════════════════\n\n"

        f"📍 From:\n"
        f"**{current_data['display_name']}**\n\n"

        + "\n".join(lines)

        + "\n\n"
        "Use:\n"
        "`!drive <code-name>`\n\n"

        "════════════════════"
    )


# =========================================================
# !DRIVE
# =========================================================

@bot.command()
async def drive(ctx, destination=None):

    user_id = ctx.author.id

    # =====================================================
    # DESTINATION REQUIRED
    # =====================================================

    if destination is None:

        await ctx.send(
            "🚗 **DRIVE**\n\n"
            "Please provide a destination.\n\n"
            "Example:\n"
            "`!drive bank`"
        )

        return

    # =====================================================
    # RESOLVE DESTINATION
    # =====================================================

    destination = resolve_location(
        destination
    )

    if destination is None:

        await ctx.send(
            "❌ **DESTINATION NOT FOUND**\n\n"
            "Use `!route` to see your "
            "available destinations."
        )

        return

    # =====================================================
    # GET CURRENT LOCATION
    # =====================================================

    current_location = get_player_location(
        user_id
    )

    if current_location is None:

        current_location = get_location_from_channel(
            ctx.channel
        )

        if current_location is None:

            await ctx.send(
                "📍 **LOCATION UNKNOWN**\n\n"
                "I cannot determine your "
                "current location."
            )

            return

        set_player_location(
            user_id,
            current_location
        )

    # =====================================================
    # ALREADY THERE
    # =====================================================

    if current_location == destination:

        await ctx.send(
            f"📍 You are already at "
            f"**{LOCATIONS[destination]['display_name']}**."
        )

        return

    # =====================================================
    # DIRECT ROUTE CHECK
    # =====================================================

    if not is_direct_route(
        current_location,
        destination
    ):

        await ctx.send(
            "🚧 **NO DIRECT ROUTE**\n"
            "════════════════════\n\n"

            f"📍 From:\n"
            f"**{LOCATIONS[current_location]['display_name']}**\n\n"

            f"📍 To:\n"
            f"**{LOCATIONS[destination]['display_name']}**\n\n"

            "You must first travel to the "
            "appropriate access location."
        )

        return

    # =====================================================
    # VEHICLE
    # =====================================================

    vehicle = get_vehicle(
        user_id
    )

    if vehicle is None:

        create_vehicle(
            user_id
        )

        vehicle = get_vehicle(
            user_id
        )

    (
        vehicle_name,
        current_fuel,
        fuel_capacity,
        vehicle_location
    ) = vehicle

    # =====================================================
    # VEHICLE MUST BE WITH PLAYER
    # =====================================================

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
            f"**{LOCATIONS[current_location]['display_name']}**\n\n"

            f"🚗 Vehicle location:\n"
            f"**{LOCATIONS.get(vehicle_location, {}).get('display_name', 'Unknown')}**\n\n"

            "Your vehicle must be at your "
            "current location."
        )

        return

    # =====================================================
    # DISTANCE
    # =====================================================

    distance = calculate_distance(
        current_location,
        destination
    )

    # =====================================================
    # FUEL
    # =====================================================

    fuel_used = (
        distance *
        FUEL_CONSUMPTION
    )

    if current_fuel < fuel_used:

        await ctx.send(
            "⛽ **NOT ENOUGH FUEL**\n\n"

            f"🚗 Vehicle: **{vehicle_name}**\n"
            f"⛽ Current fuel: **{current_fuel:.1f}L**\n"
            f"⛽ Required: **{fuel_used:.1f}L**\n\n"

            "Please refuel before travelling."
        )

        return

    remaining_fuel = (
        current_fuel -
        fuel_used
    )

    update_fuel(
        user_id,
        remaining_fuel
    )

    # =====================================================
    # TRAVEL TIME
    #
    # Distance remains real.
    # Time is compressed for testing.
    # =====================================================

    travel_time = (
        distance *
        TIME_PER_KM
    )

    travel_time = max(
        MIN_TRAVEL_TIME,
        min(
            MAX_TRAVEL_TIME,
            round(travel_time)
        )
    )

    # =====================================================
    # IMPORTANT:
    #
    # THE MOMENT THE JOURNEY STARTS,
    # ALL LOCATION CHANNELS BECOME READ-ONLY.
    #
    # current_location = None
    # =====================================================

    await update_location_permissions(
        ctx.guild,
        ctx.author,
        None
    )

    # =====================================================
    # JOURNEY MESSAGE
    # =====================================================

    departure_message = await ctx.send(
        "🚗 **JOURNEY STARTED**\n"
        "════════════════════\n\n"

        f"📍 From:\n"
        f"**{LOCATIONS[current_location]['display_name']}**\n\n"

        f"📍 To:\n"
        f"**{LOCATIONS[destination]['display_name']}**\n\n"

        f"🚗 Vehicle: **{vehicle_name}**\n"
        f"🛣️ Distance: **{distance:.1f} km**\n"
        f"⛽ Fuel used: **{fuel_used:.1f}L**\n"
        f"⛽ Remaining fuel: **{remaining_fuel:.1f}L**\n"
        f"⏱️ Travel Time: **{travel_time} seconds**\n\n"

        "🔒 All location channels are locked "
        "while you are travelling.\n\n"

        "🚗 You are now travelling..."
    )

    asyncio.create_task(
        delete_departure_message(
            departure_message
        )
    )

    # =====================================================
    # TRAVEL
    # =====================================================

    await asyncio.sleep(
        travel_time
    )

    # =====================================================
    # ARRIVAL
    # =====================================================

    set_player_location(
        user_id,
        destination
    )

    update_vehicle_location(
        user_id,
        destination
    )

    # =====================================================
    # UNLOCK ONLY DESTINATION
    # =====================================================

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

            f"Your location has been updated to "
            f"**{LOCATIONS[destination]['display_name']}**, "
            "but the Discord channel could not be found."
        )

        return

    # =====================================================
    # ARRIVAL MESSAGE
    # =====================================================

    await destination_channel.send(
        "✅ **ARRIVAL CONFIRMED**\n"
        "════════════════════\n\n"

        f"🚗 {ctx.author.mention} has arrived at:\n\n"

        f"**{LOCATIONS[destination]['display_name']}**\n\n"

        f"🛣️ Distance travelled: "
        f"**{distance:.1f} km**\n"

        f"⛽ Fuel remaining: "
        f"**{remaining_fuel:.1f}L**\n\n"

        "🔓 This location is now unlocked for you.\n"
        "💬 You can now interact with this channel.\n\n"

        "════════════════════"
    )


# =========================================================
# !VEHICLE
# =========================================================

@bot.command()
async def vehicle(ctx):

    user_id = ctx.author.id

    current_location = get_player_location(
        user_id
    )

    if current_location is None:

        current_location = get_location_from_channel(
            ctx.channel
        )

        if current_location is None:

            await ctx.send(
                "📍 **LOCATION UNKNOWN**"
            )

            return

        set_player_location(
            user_id,
            current_location
        )

    vehicle_data = get_vehicle(
        user_id
    )

    if vehicle_data is None:

        create_vehicle(
            user_id
        )

        vehicle_data = get_vehicle(
            user_id
        )

    (
        vehicle_name,
        fuel,
        fuel_capacity,
        vehicle_location
    ) = vehicle_data

    current_data = LOCATIONS[
        current_location
    ]

    vehicle_location_data = LOCATIONS.get(
        vehicle_location
    )

    await ctx.send(
        "🚘 **YOUR VEHICLE**\n"
        "════════════════════\n\n"

        f"🚗 Vehicle: **{vehicle_name}**\n"
        f"⛽ Fuel: **{fuel:.1f}L / {fuel_capacity:.1f}L**\n\n"

        f"👤 Player Location:\n"
        f"**{current_data['display_name']}**\n\n"

        f"🚗 Vehicle Location:\n"
        f"**{vehicle_location_data['display_name'] if vehicle_location_data else 'Unknown'}**\n\n"

        "🅿️ Status: **Parked**\n\n"

        "════════════════════"
    )


# =========================================================
# !REFUEL
# =========================================================

@bot.command()
async def refuel(ctx, confirmation=None):

    user_id = ctx.author.id

    player_location = get_player_location(
        user_id
    )

    if player_location is None:

        await ctx.send(
            "📍 **REFUEL FAILED**\n\n"
            "Use `!location` first."
        )

        return

    vehicle = get_vehicle(
        user_id
    )

    if vehicle is None:

        create_vehicle(
            user_id
        )

        vehicle = get_vehicle(
            user_id
        )

    (
        vehicle_name,
        current_fuel,
        fuel_capacity,
        vehicle_location
    ) = vehicle

    # =====================================================
    # PLAYER MUST BE AT FUEL STATION
    # =====================================================

    if player_location != "fuel-station":

        await ctx.send(
            "⛽ **REFUEL FAILED**\n\n"

            "You must be at the **Fuel Station** "
            "to refuel."
        )

        return

      # =====================================================
    # VEHICLE MUST BE THERE
    # =====================================================

    if vehicle_location != "fuel-station":

        await ctx.send(
            "⛽ **REFUEL FAILED**\n\n"

            "Your vehicle is not at the Fuel Station."
        )

        return

    # =====================================================
    # FULL TANK
    # =====================================================

    if current_fuel >= fuel_capacity:

        await ctx.send(
            "⛽ **TANK ALREADY FULL**\n\n"

            f"🚗 Vehicle: **{vehicle_name}**\n"
            f"⛽ Fuel: **{current_fuel:.1f}L / "
            f"{fuel_capacity:.1f}L**"
        )

        return

    # =====================================================
    # COST
    # =====================================================

    fuel_needed = (
        fuel_capacity -
        current_fuel
    )

    total_cost = (
        fuel_needed *
        FUEL_PRICE
    )

    balance = get_balance(
        user_id
    )

    if confirmation != "confirm":

        await ctx.send(
            "⛽ **REFUEL REQUEST**\n"
            "════════════════════\n\n"

            f"🚗 Vehicle: **{vehicle_name}**\n"

            f"⛽ Current fuel: "
            f"**{current_fuel:.1f}L**\n"

            f"⛽ Required: "
            f"**{fuel_needed:.1f}L**\n"

            f"💵 Price: "
            f"**₦{FUEL_PRICE:,.0f}/L**\n"

            f"💰 Total: "
            f"**₦{total_cost:,.0f}**\n\n"

            f"💳 Balance: "
            f"**₦{balance:,.0f}**\n\n"

            "Confirm with:\n"
            "`!refuel confirm`\n\n"

            "════════════════════"
        )

        return

    # =====================================================
    # BALANCE CHECK
    # =====================================================

    if balance < total_cost:

        await ctx.send(
            "❌ **INSUFFICIENT FUNDS**\n\n"

            f"Required: **₦{total_cost:,.0f}**\n"
            f"Balance: **₦{balance:,.0f}**"
        )

        return

    # =====================================================
    # PAYMENT
    # =====================================================

    new_balance = (
        balance -
        total_cost
    )

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

        f"⛽ Previous fuel: "
        f"**{current_fuel:.1f}L**\n"

        f"⛽ Added: "
        f"**{fuel_needed:.1f}L**\n"

        f"⛽ Current fuel: "
        f"**{fuel_capacity:.1f}L / "
        f"{fuel_capacity:.1f}L**\n\n"

        f"💰 Paid: "
        f"**₦{total_cost:,.0f}**\n"

        f"💳 Remaining balance: "
        f"**₦{new_balance:,.0f}**\n\n"

        "════════════════════"
    )


# =========================================================
# !BALANCE
# =========================================================

@bot.command()
async def balance(ctx):

    user_id = ctx.author.id

    current_balance = get_balance(
        user_id
    )

    await ctx.send(
        "💳 **TRANSPORT BALANCE**\n"
        "════════════════════\n\n"

        f"💰 Balance: **₦{current_balance:,.0f}**\n\n"

        "This is currently a temporary "
        "transport balance.\n\n"

        "════════════════════"
    )


# =========================================================
# VEHICLE ERROR HANDLER
# =========================================================

@vehicle.error
async def vehicle_error(ctx, error):

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
