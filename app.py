import os
from flask import Flask, render_template, request, jsonify
from flask_limiter import Limiter
from ebay_api import search_items
from database import create_table, save_listing, get_listings
from ebay_api import search_items, get_category_suggestions
from main import (
    calculate_total,
    get_deal_scores,
    get_n_cheapest_listings,
    get_average_price,
    get_average_shipping,
    normalize_query,
)

app = Flask(__name__)

def client_ip():
    # Behind the Cloudflare Tunnel every request appears to come from 127.0.0.1,
    # so use the real visitor IP that Cloudflare passes along.
    return request.headers.get("CF-Connecting-IP") or request.remote_addr

limiter = Limiter(
    key_func=client_ip,
    app=app,
    default_limits=["200 per hour"],
    storage_uri="memory://",
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/categories")
@limiter.limit("30 per minute")
def categories():
    query = normalize_query(request.args.get("q") or "")
    if not query:
        return jsonify([])
    try:
        return jsonify(get_category_suggestions(query))
    except Exception:
        return jsonify([])  # eBay unreachable: dropdown stays at "All categories"

@app.route("/search", methods=["POST"])
@limiter.limit("10 per minute")
def search():
    data = request.get_json()
    query = (data.get("query") or "").strip()
    max_price = float(data.get("max_price") or 500)
    n_deals = int(data.get("n_deals") or 5)
    n_cheapest = int(data.get("n_cheapest") or 5)
    category_id = data.get("category_id") or None

    if not query:
        return jsonify({"error": "Search query is required."}), 400

    search_query = normalize_query(query)
    search_words = search_query.lower().split()
    create_table()

    try:
        listings = search_items(search_query, category_id=category_id)
        source = "live"
        for listing in listings:
            save_listing(listing)
    except Exception as e:
        listings = get_listings()
        if not listings:
            return jsonify({"error": f"eBay unavailable and no saved listings: {e}"}), 503
        source = "database"

    average_price = get_average_price(listings, search_words)
    average_shipping = get_average_shipping(listings, search_words)

    best_deals = get_deal_scores(listings, search_words, max_price)

    cheapest = get_n_cheapest_listings(listings, search_words, max_price, n_cheapest)

    def fmt(listing, include_score=False):
        out = {
            "title": listing["title"],
            "price": listing["price"],
            "shipping": listing["shipping"],
            "total": round(calculate_total(listing), 2),
            "condition": listing["condition"],
            "url": listing.get("url", ""),
        }
        if include_score:
            out["deal_score"] = round(listing.get("deal_score", 0), 1)
        return out

    return jsonify({
        "source": source,
        "average_price": round(average_price, 2),
        "average_shipping": round(average_shipping, 2),
        "best_deals": [fmt(l, include_score=True) for l in best_deals[:n_deals]],
        "cheapest": [fmt(l) for l in cheapest],
    })

@app.errorhandler(429)
def too_many_requests(e):
    return jsonify({"error": "Too many searches. Wait a minute and try again."}), 429


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=os.getenv("FLASK_DEBUG") == "1")
