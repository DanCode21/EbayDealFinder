from flask import Flask, render_template, request, jsonify
from ebay_api import search_items
from database import create_table, save_listing, get_listings
from main import (
    calculate_total,
    get_deal_scores,
    get_n_cheapest_listings,
    get_average_price,
    get_average_shipping,
)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    query = (data.get("query") or "").strip()
    max_price = float(data.get("max_price") or 500)
    n_deals = int(data.get("n_deals") or 5)
    n_cheapest = int(data.get("n_cheapest") or 5)

    if not query:
        return jsonify({"error": "Search query is required."}), 400

    search_words = query.lower().split()
    create_table()

    try:
        listings = search_items(query)
        source = "live"
    except Exception as e:
        listings = get_listings()
        if not listings:
            return jsonify({"error": f"eBay unavailable and no saved listings: {e}"}), 503
        source = "database"

    average_price = get_average_price(listings, search_words, max_price)
    average_shipping = get_average_shipping(listings, search_words, max_price)

    best_deals = get_deal_scores(listings, search_words, max_price)
    for listing in best_deals[:n_deals]:
        save_listing(listing)

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
