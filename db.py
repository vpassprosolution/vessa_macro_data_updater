import asyncpg
import os

DB_URL = os.getenv("DB_URL")  # Make sure you set this in Railway variables

async def connect_db():
    try:
        conn = await asyncpg.connect(DB_URL)
        return conn
    except Exception as e:
        print(f"❌ DB Connection Error: {e}")
        return None
