import sqlite3

DATABASE_NAME = "eko_transport.db"

def connect(): return sqlite3.connect(DATABASE_NAME)

def setup_database(): connection = connect() cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        user_id INTEGER PRIMARY KEY,
        location TEXT NOT NULL
    )
""")
connection.commit()
connection.close()
def get_player_location(user_id): connection = connect() cursor = connection.cursor()

cursor.execute(
    "SELECT location FROM players WHERE user_id = ?",
    (user_id,)
)
result = cursor.fetchone()
connection.close()
if result:
    return result[0]
return None
def set_player_location(user_id, location): connection = connect() cursor = connection.cursor()

cursor.execute("""
    INSERT INTO players (user_id, location)
    VALUES (?, ?)
    ON CONFLICT(user_id)
    DO UPDATE SET location = excluded.location
""", (user_id, location))
connection.commit()
connection.close()

def create_vehicle(user_id, vehicle_name="Toyota Camry"): connection = connect() cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS vehicles (
        user_id INTEGER PRIMARY KEY,
        vehicle_name TEXT NOT NULL,
        fuel REAL NOT NULL DEFAULT 50,
        fuel_capacity REAL NOT NULL DEFAULT 60
    )
""")
cursor.execute("""
    INSERT OR IGNORE INTO vehicles
    (user_id, vehicle_name, fuel, fuel_capacity)
    VALUES (?, ?, 50, 60)
""", (user_id, vehicle_name))
connection.commit()
connection.close()
def get_vehicle(user_id): connection = connect() cursor = connection.cursor()

cursor.execute("""
    SELECT vehicle_name, fuel, fuel_capacity
    FROM vehicles
    WHERE user_id = ?
""", (user_id,))
result = cursor.fetchone()
connection.close()
return result
def update_fuel(user_id, fuel): connection = connect() cursor = connection.cursor()

cursor.execute("""
    UPDATE vehicles
    SET fuel = ?
    WHERE user_id = ?
""", (fuel, user_id))
connection.commit()
connection.close()
