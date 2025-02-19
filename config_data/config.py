import os
from multiprocessing.managers import Token

from dotenv import load_dotenv

load_dotenv()

# Secret key
SECRET_KEY = b"SECRET_KEY"

if not SECRET_KEY:
    SECRET_KEY = os.urandom(32)

# Token 60 minutes * 24 hours * 8 days = 8 days
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 8

# Data Base
DB_USER = os.environ.get('DB_USER')
DB_NAME = os.environ.get('DB_NAME')
DB_PASS = os.environ.get('DB_PASS')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
SQLITE_ASYNC_URL = 'sqlite+aiosqlite:///./test.db'

BOT_TOKEN = os.environ.get('BOT_TOKEN')
