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

# SQL to create the historical_weather table if it doesn’t exist
sql_create_weather_table = text("""
    CREATE TABLE IF NOT EXISTS historical_weather (
        date DATE,
        time TIME,
        weather VARCHAR(128),
        temp FLOAT,
        humidity INT,
        wind_speed FLOAT,
        wind_deg INT,
        PRIMARY KEY (date, time)
    );
""")

# SQL to create the bike_stations table if it doesn’t exist
sql_create_bike_table = text("""
    CREATE TABLE IF NOT EXISTS bike_stations (
        number INT PRIMARY KEY,
        name VARCHAR(255),
        address VARCHAR(255),
        position_lat FLOAT,
        position_lng FLOAT,
        banking BOOLEAN,
        bike_stands INT,
        available_bikes INT,
        available_bike_stands INT,
        status VARCHAR(50),
        last_update BIGINT
    );
""")

# Execute SQL to create the table
with engine.connect() as connection:
    connection.execute(sql_create_weather_table)
    connection.execute(sql_create_bike_table)
    connection.commit()

# Run an example query to check the connection
with engine.connect() as connection:
    result = connection.execute(text("SHOW TABLES;"))
    print("Existing tables in the database:")
    for row in result:
        print(row)


# Slide: Connecting to RDS page 11

# from sqlalchemy import create_engine
# import pandas as pd

# # Define database connection URL (SQLAlchemy format)
# DB_USER = "alessiofer"  # Your RDS username
# DB_PASSWORD = "dublin.bus.123"  # Your RDS password
# DB_HOST = "127.0.0.1"  # Localhost because of SSH tunnel
# DB_PORT = "13306"  # Must match your tunnel port
# DB_NAME = "dublin_cycle"  # Change to your database name

# # Create SQLAlchemy engine
# engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# # Fetch data into a DataFrame
# query = "SELECT * FROM historical_weather"
# df = pd.read_sql(query, engine)

# # Print the data
# print(df)

# # Close the connection
# engine.dispose()