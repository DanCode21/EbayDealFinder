import sqlite3
from datetime import datetime

def create_table():
    conn = sqlite3.connect("deals.db")
    conn.row_factory = sqlite3.Row
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
    conn = sqlite3.connect("deals.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO listings (item_id, title, price, price_currency, shipping, shipping_currency, condition, url, image_url, seller_username, location_country, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        listing.get('item_id'),
        listing.get('title'),
        listing.get('price'),
        listing.get('price_currency'),
        listing.get('shipping'),
        listing.get('shipping_currency'),
        listing.get('condition'),
        listing.get('url'),
        listing.get('image_url'),
        listing.get('seller_username'),
        listing.get('location_country'),
        timestamp
    ))
    conn.commit()
    conn.close()

def get_listings():
    conn = sqlite3.connect("deals.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM listings")
    listings = cursor.fetchall()
    conn.close()
    return [dict(row) for row in listings]
