import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    JWT_SECRET_KEY = os.environ.get("SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
    DB_SERVER = os.environ.get("DB_SERVER", "localhost")
    DB_NAME = os.environ.get("DB_NAME", "CabBookingDB")
    DB_DRIVER = os.environ.get("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

class TestingConfig(Config):
    TESTING = True
    DB_NAME = "CabBookingDB_Test"

config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig
}
