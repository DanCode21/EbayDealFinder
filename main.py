import json
from ebay_api import search_items
from database import create_table, save_listing, get_listings

# User input for search query and maximum price
def get_user_input():
    search_query = input("What are you looking for? ")
    while True:
        try:
            max_price = float(input("What is your maximum price? "))
            break
        except ValueError:
            print("Please enter a valid number for the maximum price.")
    while True:
        try:
            n = int(input("How many listings do you want to see? "))
            break
        except ValueError:
            print("Please enter a valid number for the number of listings.")
    search_words = search_query.lower().split()
    return search_query, search_words, max_price, n

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
    print(f"\nListing Details: Title: {listing['title']} \nPrice: ${listing['price']:.2f} CAD \nShipping: ${listing['shipping']:.2f} \nCondition: {listing['condition']}")
    if listing.get("url"):
        print(f"URL: {listing['url']}")

def get_cheapest_listing(listings, search_words, max_price):
    cheapest_price = float('inf') # set cheapest price to infinity
    cheapest_listing = None # no cheapest listing initially
    for listing in listings:   # go through each listing, match search? yes -> match price? yes -> 
        if(search_match(listing, search_words) and price_match(listing, max_price)):
            if calculate_total(listing) < cheapest_price:
                cheapest_price = calculate_total(listing) #lower than cheapest price? -> update cheapest price
                cheapest_listing = listing        # and cheapest listing
    return cheapest_listing

def get_n_cheapest_listings(listings, search_words, max_price, n):
    valid_listings = [listing for listing in listings if search_match(listing, search_words) and price_match(listing, max_price)]
    sorted_listings = sorted(valid_listings, key=calculate_total)
    return sorted_listings[:n]

def get_average_price(listings, search_words, max_price):
    total_price = 0
    count = 0
    for listing in listings:
        if search_match(listing, search_words) and price_match(listing, max_price):
            total_price += calculate_total(listing)
            count += 1
    average_price =  total_price / count if count > 0 else 0
    return average_price

def get_deal_score(listing, average_price):
    score = 100
    
     # Calculate deal score based on price difference from average price, 1 Percent cheaper ->  + 1point 
    total_price = calculate_total(listing)
    # Calculate Avg Price of valid listings to compare against
    score += 100 *(1 - (total_price / average_price)) if average_price > 0 else 0

    # Condition score
    if listing['condition'].lower() == 'new':
        score += 20 # add points for new condition
    elif listing['condition'].lower() == 'for parts or not working':
        score -= 70 # Subtract points for poor condition

    # Shipping Cost Missing Penalty
    if listing['shipping'] == 0:
        score -= 10

    # Score Floor
    if score < 0:
        score = 0
    listing ['deal_score'] = score
    return score

def get_deal_scores(listings, search_words, max_price):
    valid_listings = [listing for listing in listings if search_match(listing, search_words) and price_match(listing, max_price)]
    average_price=get_average_price(valid_listings, search_words, max_price)
    for listing in valid_listings:
        if listing['price'] < average_price * 0.3:  # Skip listings that are significantly cheaper than average
            listing['deal_score'] = 0
        else:
            get_deal_score(listing, average_price)
    sorted_listings = sorted(valid_listings, key=lambda x: x['deal_score'], reverse=True)
    return sorted_listings

def main():
    search_query, search_words, max_price, n = get_user_input()
    

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

    few_cheapest_listings = get_n_cheapest_listings(listings, search_words, max_price, n)
    print("\n Cheapest Listings:")
    for listing in few_cheapest_listings:
        print_listing(listing)

    print("\n Average Price:")
    average_price = get_average_price(listings, search_words, max_price)
    print(f"Average Price: ${average_price:.2f}")

    print("\n Best Deals :")
    number_of_deals_to_show = user_input = input("How many best deals do you want to see? ")
    try:
        number_of_deals_to_show = int(number_of_deals_to_show)
    except ValueError:
        print("Invalid input for number of deals, showing all deals instead.")
        number_of_deals_to_show = None
    best_deals = get_deal_scores(listings, search_words, max_price)
    for listing in best_deals[:number_of_deals_to_show]:
        print_listing(listing)
        print(f"Deal Score: {listing['deal_score']:.2f}")

if __name__ == "__main__":
    main()
