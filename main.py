# User input for search query and maximum price
search_query = input("What are you looking for? ")
max_price = float(input("What is your maximum price? "))
#Debug prints:
print(f"Searching for '{search_query}' with a maximum price of ${max_price}...")

listings = [
    {"title": "Wireless Mouse", "price": 15.99, "shipping": 5.00, "condition": "New"},
    {"title": "Bluetooth Headphones", "price": 45.00, "shipping": 10.00, "condition": "New"},
    {"title": "GPU", "price": 399.99, "shipping": 20.00, "condition": "New"},
]

# Filter listings based on price
search_words = search_query.lower().split()
found_any = False
cheapest_price = float('inf') # Initialize cheapest price to infinity
for listing in listings:
    title_words = listing["title"].lower().split()
    if all(word in title_words for word in search_words):
        print(f"Checking listing: {listing['title']} with price ${listing['price']:.2f} and shipping ${listing['shipping']:.2f}")  # Debug print
        total_price = listing["price"]+listing["shipping"]
        if total_price < cheapest_price:
            cheapest_price = total_price  # Update cheapest price if current listing is cheaper
        if total_price <= max_price:
            print(f"Found a deal: {listing['title']} for ${total_price:.2f} (Price: ${listing['price']:.2f}, Shipping: ${listing['shipping']:.2f})")
            found_any = True
if not found_any:
    print("No deals found within your price range.")
print(f"The cheapest deal found is for ${cheapest_price:.2f}")
    


