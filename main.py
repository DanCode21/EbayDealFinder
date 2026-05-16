# User input for search query and maximum price
def get_user_input():
    search_query = input("What are you looking for? ")
    while True:
        try:
            max_price = float(input("What is your maximum price? "))
            break
        except ValueError:
            print("Please enter a valid number for the maximum price.")
    search_words = search_query.lower.split()
    return search_words, max_price

listings = [
    {"title": "Wireless Mouse", "price": 15.99, "shipping": 5.00, "condition": "New"},
    {"title": "Bluetooth Headphones", "price": 45.00, "shipping": 10.00, "condition": "New"},
    {"title": "GPU", "price": 399.99, "shipping": 20.00, "condition": "New"},

]
def calculate_total(listing):
    total_price = listing['price'] + listing['shipping']
    return total_price

def search_match(listing, search_words):
    return all(word in listing['title'].lower() for word in search_words)
    #check that all words from search words (already lower case ) are in listing['title].lower()

def listing_within_budget(listing, max_price):
    return calculate_total(listing) < max_price

def print_listing(listing):
    print(f"Listing Details: Title: {listing['title']}, Price: ${listing['price']:.2f}, Shipping: ${listing['shipping']:.2f}, Condition: {listing['condition']}")

    
# Filter listings based on price
# search_words = search_query.lower().split()
# found_any = False
# cheapest_price = float('inf') # Initialize cheapest price to infinity
# for listing in listings:
#     title_words = listing["title"].lower().split()
#     if all(word in title_words for word in search_words):
#         print(f"Checking listing: {listing['title']} with price ${listing['price']:.2f} and shipping ${listing['shipping']:.2f}")  # Debug print
#         total_price = listing["price"]+listing["shipping"]
#         if total_price < cheapest_price:
#             cheapest_price = total_price  # Update cheapest price if current listing is cheaper
#         if total_price <= max_price:
#             print(f"Found a deal: {listing['title']} for ${total_price:.2f} (Price: ${listing['price']:.2f}, Shipping: ${listing['shipping']:.2f})")
#             found_any = True
# if not found_any:
#     print("No deals found within your price range.")
# print(f"The cheapest deal found is for ${cheapest_price:.2f}")
    
def main():
    print("Program started")
    print("Testing get_user_input, expected output: (['wireless', 'mouse'], 20.00)")
    get_user_input = lambda: (['wireless', 'mouse'], 20.00)  # Mocking user input for testing
    print("Testing calculate_total, expected output: 20.99")
    print(calculate_total(listings[0]))  # Should return 20.99
    print("Testing search_match, expected output: True")
    print(search_match(listings[0], [" mouse"])) # Should return True
    print("Testing listing_within_budget, expected output: True")
    print(listing_within_budget(listings[0], 5.00)) # True
    print("Testing listing_within_budget, expected output: False")
    print(listing_within_budget(listings[1], 50.00)) # False
    print("Testing print_listing, expected output: Listing Details: Title: Wireless Mouse, Price: $15.99, Shipping: $5.00, Condition: New")
    print_listing(listings[0])

main()