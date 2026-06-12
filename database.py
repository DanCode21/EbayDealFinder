import sqlite3
from datetime import datetime
timestamp = datetime.now().isoformat()

def create_table():
    conn = sqlite3.connect("deals.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id TEXT,
            title TEXT,
            price REAL,
            price_currency TEXT,
            shipping REAL,
            shipping_currency TEXT,
            condition TEXT,
            url TEXT,
            image_url TEXT,
            seller_username TEXT,
            location_country TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_listing(listing):




def get_listings():
