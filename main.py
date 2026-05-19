import json

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
    return search_words, max_price

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
    print(f"Listing Details: Title: {listing['title']}, Price: ${listing['price']:.2f}, Shipping: ${listing['shipping']:.2f}, Condition: {listing['condition']}")

def get_cheapest_listing(listings, search_words, max_price):
    cheapest_price = float('inf') # set cheapest price to infinity
    print(f"Set cheaptest price to {cheapest_price}")
    cheapest_listing = None # no cheapest listing initially
    print(f"Set cheapest listing to {cheapest_listing}")
    print("STARTING LOOP")
    for listing in listings:   # go through each listing, match search? yes -> match price? yes -> 
        print(f"Checking listing: {listing['title']} with price ${listing['price']:.2f} and shipping ${listing['shipping']:.2f}")  # Debug print
        if(search_match(listing, search_words) and price_match(listing, max_price)):
            print("CONDITION MET: within price and search words")
            if calculate_total(listing) < cheapest_price:
                cheapest_price = calculate_total(listing) #lower than cheapest price? -> update cheapest price
                print(f"Updated cheapest price to {cheapest_price}")
                cheapest_listing = listing        # and cheapest listing
                print(f"Updated cheapest listing to {cheapest_listing}")
            else:
                print(f"Did not update cheapest listing, current cheapest price is {cheapest_price} and listing total is {calculate_total(listing)}")
        else:
            print("CONDITION NOT MET: either price or search words do not match")
            
    print("DEBUG cheapest_listing =", cheapest_listing)
    print("DEBUG type =", type(cheapest_listing))
    return cheapest_listing



def main():
    #load listings from json file:
    with open("listings.json", 'r') as file:
        listings = json.load(file)

    print("Program started")
    search_words, max_price = get_user_input()
    cheapest_listing = get_cheapest_listing(listings, search_words, max_price)  # Should find the GPU listing
    print_listing(cheapest_listing)
    print(f"Cheapest listing found: {cheapest_listing['title']} \nTotal: ${calculate_total(cheapest_listing):.2f}")  # Debug print to show the cheapest listing found
    print("Program ended")
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


main() 