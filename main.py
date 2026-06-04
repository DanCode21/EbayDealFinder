import json

from ebay_api import search_items

# User input for search query and maximum price
def get_user_input():
    search_query = input("What are you looking for? ")
    while True:
        try:
            max_price = float(input("What is your maximum price? "))
            break
        except ValueError:
            print("Please enter a valid number for the maximum price.")
    search_words = search_query.lower().split()
    return search_query, search_words, max_price

def calculate_total(listing):
    total_price = listing['price'] + listing['shipping'] 
    return total_price

def search_match(listing, search_words):
    return all(word in listing['title'].lower() for word in search_words)
    #check that all words from search words (already lower case ) are in listing['title].lower()

def price_match(listing, max_price):
    return calculate_total(listing) <= max_price

def print_listing(listing):
    if listing is None:
        print("No valid listing to print.")
        return
    currency = listing.get("price_currency") or "CAD"
    print(f"\nListing Details: Title: {listing['title']} \nPrice: ${listing['price']:.2f} {currency} \nShipping: ${listing['shipping']:.2f} \nCondition: {listing['condition']}")
    if listing.get("url"):
        print(f"URL: {listing['url']}")

def get_cheapest_listing(listings, search_words, max_price):
    cheapest_price = float('inf') # set cheapest price to infinity
    print(f"Set cheaptest price to {cheapest_price}")
    cheapest_listing = None # no cheapest listing initially
    print(f"Set cheapest listing to {cheapest_listing}")
    print("STARTING LOOP")
    for listing in listings:   # go through each listing, match search? yes -> match price? yes -> 
        print(f"Checking listing: {listing['title']} with price ${listing['price']:.2f} and shipping ${listing['shipping']:.2f}")  # Debug print
        if(search_match(listing, search_words) and price_match(listing, max_price)):
            if calculate_total(listing) < cheapest_price:
                cheapest_price = calculate_total(listing) #lower than cheapest price? -> update cheapest price
                cheapest_listing = listing        # and cheapest listing
            
    print("DEBUG cheapest_listing =", cheapest_listing)
    return cheapest_listing

def get_n_cheapest_listings(listings, search_words, max_price, n=None):
    if n is None:
        while True:
            try:
                n = int(input("How many other listings do you want to see? (Enter a number, or press Enter to skip) "))
                break
            except ValueError:
                print("Please enter a valid number.")
    valid_listings = [listing for listing in listings if search_match(listing, search_words) and price_match(listing, max_price)]
    sorted_listings = sorted(valid_listings, key=calculate_total)
    return sorted_listings[:n]

def ignore_broken(listings):
    return [listing for listing in listings if listing.get('title') and listing.get('price') is not None]

def main():
    search_query, search_words, max_price = get_user_input()

    try:
        listings = search_items(search_query)
        print(f"Loaded {len(listings)} live listings from eBay.")
    except Exception as error:
        print(f"Could not load live eBay listings: {error}")
        print("Using local listings.json sample data instead.")
        with open("listings.json", 'r') as file:
            listings = json.load(file)

    cheapest_listing = get_cheapest_listing(listings, search_words, max_price)  # Should find the GPU listing
    print_listing(cheapest_listing)
    if cheapest_listing is not None:
        print(f"Cheapest listing found: {cheapest_listing['title']} \nTotal: ${calculate_total(cheapest_listing):.2f}")  # Debug print to show the cheapest listing found
    # print("Testing calculate_total, expected output: 20.99")
    # print(calculate_total(listings[0]))  # Should return 20.99
    # print("Testing search_match, expected output: True")
    # print(search_match(listings[0], [" mouse"])) # Should return True
    # print("Testing price_match, expected output: True")
    # print(price_match(listings[0], 20.00)) # True
    # print("Testing price_match, expected output: False")
    # print(price_match(listings[1], 50.00)) # False
    # print("Testing print_listing, expected output: Listing Details: Title: Wireless Mouse, Price: $15.99, Shipping: $5.00, Condition: New")
    # print_listing(listings[0])

    few_cheapest_listings = get_n_cheapest_listings(listings, search_words, max_price)
    print("\n Cheapest Listings:")
    for listing in few_cheapest_listings:
        print_listing(listing)


main() 
