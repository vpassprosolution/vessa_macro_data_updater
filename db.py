import asyncpg
import os

DB_URL = os.environ.get("DB_URL")

async def connect_db():
    try:
        conn = await asyncpg.connect(DB_URL)
        return conn
    except Exception as e:
        print(f"❌ DB Connection Error: {e}")
        return None
