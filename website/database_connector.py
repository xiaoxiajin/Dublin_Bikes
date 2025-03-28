import sys
import os
from sqlalchemy import create_engine, text

# Get the absolute path of the 'swe' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import dbinfo
import pymysql

DB_NAME = "dublin_cycle"  # database name

# Create SQLAlchemy engine, connect to AWS RDS 
engine = create_engine(f"mysql+pymysql://{dbinfo.DB_USER}:{dbinfo.DB_PASSWORD}@{dbinfo.DB_HOST}:{dbinfo.DB_PORT}", echo=True)

# Create the database if it doesn’t exist
with engine.connect() as connection:
    connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME};"))
    connection.commit()

# Update the engine to connect specifically to the new database
engine = create_engine(f"mysql+pymysql://{dbinfo.DB_USER}:{dbinfo.DB_PASSWORD}@{dbinfo.DB_HOST}:{dbinfo.DB_PORT}/{DB_NAME}", echo=True)

# SQL to create the `current` table
sql_create_current_table = text("""
    CREATE TABLE IF NOT EXISTS current_weather (
        dt DATETIME NOT NULL,
        feels_like FLOAT,
        humidity INTEGER,
        pressure INTEGER,
        sunrise DATETIME,
        sunset DATETIME,
        temp FLOAT,
        uvi FLOAT,
        weather_id INTEGER,
        wind_gust FLOAT,
        wind_speed FLOAT,
        rain_1h FLOAT,
        snow_1h FLOAT,
        PRIMARY KEY (dt)
    );
""")

# SQL to create the `hourly` table
sql_create_hourly_table = text("""
    CREATE TABLE IF NOT EXISTS hourly_weather (
        dt DATETIME NOT NULL,
        future_dt DATETIME NOT NULL,
        feels_like FLOAT,
        humidity INTEGER,
        pop FLOAT,
        pressure INTEGER,
        temp FLOAT,
        uvi FLOAT,
        weather_id INTEGER,
        wind_speed FLOAT,
        wind_gust FLOAT,
        rain_1h FLOAT,
        snow_1h FLOAT,
        PRIMARY KEY (dt, future_dt)
    );
""")

# SQL to create the `daily` table
sql_create_daily_table = text("""
    CREATE TABLE IF NOT EXISTS daily_weather (
        dt DATETIME NOT NULL,
        future_dt DATETIME NOT NULL,
        humidity INTEGER,
        pop FLOAT,
        pressure INTEGER,
        temp_max FLOAT,
        temp_min FLOAT,
        uvi FLOAT,
        weather_id INTEGER,
        wind_speed FLOAT,
        wind_gust FLOAT,
        rain FLOAT,
        snow FLOAT,
        PRIMARY KEY (dt, future_dt)
    );
""")


# SQL to create the `station` table
sql_create_station_table = text("""
    CREATE TABLE IF NOT EXISTS station (
        number INTEGER NOT NULL,
        address VARCHAR(128),
        banking INTEGER,
        bike_stands INTEGER,
        name VARCHAR(128),
        position_lat FLOAT,
        position_lng FLOAT,
        PRIMARY KEY (number)
    );
""")

# SQL to create the `availability` table
sql_create_availability_table = text("""
    CREATE TABLE IF NOT EXISTS availability (
        number INTEGER NOT NULL,
        last_update DATETIME NOT NULL,
        available_bikes INTEGER,
        available_bike_stands INTEGER,
        status VARCHAR(128),
        PRIMARY KEY (number) 
    );
""")

# Execute SQL to create the table
with engine.connect() as connection:
    connection.execute(sql_create_current_table)
    connection.execute(sql_create_hourly_table)
    connection.execute(sql_create_daily_table)
    connection.execute(sql_create_availability_table)
    connection.execute(sql_create_station_table)
    connection.commit()

# Run an example query to check the connection
with engine.connect() as connection:
    result = connection.execute(text("SHOW TABLES;"))
    print("Existing tables in the database:")
    for row in result:
        print(row)


