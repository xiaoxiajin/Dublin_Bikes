import sys
import os
# Get the absolute path of the 'swe' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import dbinfo
import requests
import traceback
from datetime import datetime, timezone
from sqlalchemy import create_engine, text


DB_NAME = "dublin_cycle"
engine = create_engine(f"mysql+pymysql://{dbinfo.DB_USER}:{dbinfo.DB_PASSWORD}@{dbinfo.DB_HOST}:{dbinfo.DB_PORT}/{DB_NAME}")

def fetch_bike_stations():
    # while True:  # Keep the scraper running indefinitely
    try:
        # print("\n🚲 Fetching Dublin Bikes Data...\n")
        response = requests.get(dbinfo.STATIONS_URL, params={"apiKey": dbinfo.JCKEY, "contract": dbinfo.NAME})  
        response.raise_for_status()  # Raise an exception for failed requests

        # Parse JSON response
        if response.status_code == 200: 
            stations = response.json()
        else:
            print(f"API Request Failed, status code: {response.status_code}")
            print(response.text)  
            return  
        
        insert_station_data(stations)
        insert_availability_data(stations)
        print("\n Dublin bike data updated. \n")

    except requests.exceptions.RequestException as e:
        print(f"\n API Request Failed: {e}")
        print(traceback.format_exc())  # Print detailed error message
        
def insert_station_data(stations):
    """ Insert or update station static information """
    sql_insert = text("""
        INSERT INTO station (number, name, address, position_lat, position_lng, banking, bike_stands)
        VALUES (:number, :name, :address, :position_lat, :position_lng, :banking, :bike_stands)
        ON DUPLICATE KEY UPDATE 
            name = VALUES(name),
            address = VALUES(address),
            position_lat = VALUES(position_lat),
            position_lng = VALUES(position_lng),
            banking = VALUES(banking),
            bike_stands = VALUES(bike_stands);
    """)

    with engine.connect() as connection:
        for station in stations:
            connection.execute(sql_insert, {
                "number": station["number"],
                "name": station["name"],
                "address": station.get("address", "Unknown"), # avoid unknown address
                "position_lat": station["position"]["lat"],
                "position_lng": station["position"]["lng"],
                "banking": int(station["banking"]),
                "bike_stands": station["bike_stands"]
            })
        connection.commit()

# def insert_availability_data(stations):
#     """ Insert or update bike station availability data """
#     sql_insert = text("""
#         INSERT INTO availability (number, last_update, available_bikes, available_bike_stands, status)
#         VALUES (:number, :last_update, :available_bikes, :available_bike_stands, :status)
#         ON DUPLICATE KEY UPDATE 
#             available_bikes = VALUES(available_bikes),
#             available_bike_stands = VALUES(available_bike_stands),
#             status = VALUES(status);
#     """)

#     with engine.connect() as connection:
#         for station in stations:
#             # last_update = datetime.strptime(station["lastUpdate"], "%Y-%m-%dT%H:%M:%SZ")
#             if "last_update" in station:  # check if last_update exists
#                 last_update = datetime.fromtimestamp(station["last_update"] / 1000, tz=timezone.utc)
#             else:
#                 # print(f"⚠️ Warning: Station {station['number']} has no 'last_update' field.")
#                 continue  # skip this station

#             connection.execute(sql_insert, {
#                 "number": station["number"],
#                 "last_update": last_update,
#                 "available_bikes": station["available_bikes"],
#                 "available_bike_stands": station["available_bike_stands"],
#                 "status": station["status"]
#             })
#         connection.commit()
def insert_availability_data(stations):
    try:
        with engine.connect() as connection:
            for station in stations:
                # 添加安全的时间戳处理
                last_update = station.get('last_update')
                
                # 如果 last_update 存在且不为 None
                if last_update is not None:
                    # 使用安全的类型转换
                    try:
                        timestamp = datetime.fromtimestamp(float(last_update) / 1000, tz=timezone.utc)
                    except (TypeError, ValueError) as e:
                        print(f"Error processing timestamp for station {station.get('number')}: {e}")
                        timestamp = datetime.now(timezone.utc)
                else:
                    # 如果没有时间戳，使用当前时间
                    timestamp = datetime.now(timezone.utc)
                
                # 插入可用性数据
                availability_query = text("""
                    INSERT INTO availability 
                    (number, available_bikes, available_bike_stands, last_update) 
                    VALUES (:number, :available_bikes, :available_bike_stands, :last_update)
                    ON DUPLICATE KEY UPDATE 
                    available_bikes = :available_bikes,
                    available_bike_stands = :available_bike_stands,
                    last_update = :last_update
                """)
                
                connection.execute(availability_query, {
                    
                    "number": station["number"],
                    "last_update": timestamp,
                    "available_bikes": station["available_bikes"],
                    "available_bike_stands": station["available_bike_stands"],
                    "status": station["status"]
                })
            
            connection.commit()
    
    except Exception as e:
        print(f"Error inserting availability data: {e}")
        

