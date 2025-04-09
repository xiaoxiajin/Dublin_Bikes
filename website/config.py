# config.py
import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from flask import jsonify
from dotenv import load_dotenv
load_dotenv()

class Config:
    def __init__(self):
        self.DB_USER = os.getenv("DB_USER")
        self.DB_PASSWORD = quote_plus(os.getenv("DB_PASSWORD"))
        self.DB_HOST = os.getenv("DB_HOST", "localhost")  # default: localhost
        self.DB_PORT = os.getenv("DB_PORT", "3306")  # default: 3306
        self.DB_NAME = "dublin_cycle"  # database name
        self.JCKEY = os.getenv("JCKEY")  # JCDecaux API Key
        self.NAME = os.getenv("NAME", "Dublin")  # default: Dublin
        self.STATIONS_URL = os.getenv("STATIONS_URL", "https://api.jcdecaux.com/vls/v1/stations")  # 默认值
        self.WEATHER_API = os.getenv("Weather_Api")  # Weather API Key
        self.GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")  # Google Maps API Key
        
        # create database engine
        # self.engine = create_engine(f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")
        self.base_engine = create_engine(f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}")
        
        # create database
        self.create_database_if_not_exists()

        # create database with data
        self.engine = create_engine(f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")

    def create_database_if_not_exists(self):
        """create database if not exists"""
        with self.base_engine.connect() as connection:
            connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {self.DB_NAME};"))
            connection.commit()

    def get_google_maps_api_key(self):
        return jsonify({"api_key": self.GOOGLE_MAPS_API_KEY})

    def get_jcdecaux_info(self):
        return {
            "JCKEY": self.JCKEY,
            "NAME": self.NAME,
            "STATIONS_URL": self.STATIONS_URL
        }
    
config = Config()