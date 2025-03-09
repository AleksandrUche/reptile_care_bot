import os
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()


# Data Base

DATABASE_ENV = os.environ.get('DATABASE_ENV', 'postgres')

DB_USER = os.environ.get('DB_USER')
DB_NAME = os.environ.get('DB_NAME')
DB_PASS = os.environ.get('DB_PASS')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')

POSTGRES_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
SQLITE_URL = 'sqlite+aiosqlite:///./test.db'

DATABASE_URL = SQLITE_URL if DATABASE_ENV == "sqlite" else POSTGRES_URL

# TOKEN
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# TIME ZONE
TIME_ZONE = ZoneInfo("Europe/Moscow")

URL_API_GEO = os.environ.get('URL_API_GEO')
API_KEY_GEO = os.environ.get('API_KEY_GEO')