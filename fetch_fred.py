import httpx
import datetime
from db import connect_db
import os

FRED_API_KEY = os.environ.get("FRED_API_KEY")

INDICATORS = [
    {"name": "GDP Growth", "series_id": "GDP", "unit": "%"},
    {"name": "Inflation Rate", "series_id": "CPIAUCSL", "unit": "%"},
    {"name": "Unemployment Rate", "series_id": "UNRATE", "unit": "%"},
    {"name": "Interest Rate (Fed)", "series_id": "FEDFUNDS", "unit": "%"},
    {"name": "Retail Sales (MoM)", "series_id": "RSAFS", "unit": "%"},
    {"name": "Industrial Production", "series_id": "INDPRO", "unit": "%"}
]

async def fetch_latest_value(series_id):
    url = f"https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "sort_order": "desc",
        "limit": 1
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()
            latest = data["observations"][0]
            return float(latest["value"])
    except Exception as e:
        print(f"❌ Error fetching {series_id}: {e}")
        return None

async def update_macro_data():
    conn = await connect_db()
    if not conn:
        print("❌ DB connection failed.")
        return

    try:
        cur = await conn.cursor()

        # ✅ Delete all existing rows
        await conn.execute("DELETE FROM macro_data")

        # ✅ Insert new data
        for indicator in INDICATORS:
            value = await fetch_latest_value(indicator["series_id"])
            if value is not None:
                await conn.execute("""
                    INSERT INTO macro_data (indicator, value, unit, country, source, last_updated)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, (
                    indicator["name"],
                    value,
                    indicator["unit"],
                    "USA",
                    "FRED API",
                    datetime.datetime.now()
                ))
                print(f"✅ Saved: {indicator['name']} = {value}")

        print("✅ Macro data updated successfully.")
    except Exception as e:
        print(f"❌ Error updating DB: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(update_macro_data())
