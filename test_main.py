from main import calculate_total, search_match, price_match, print_listing, get_n_cheapest_listings, get_average_price, get_deal_scores

#           CALCULATE_TOTAL TESTS

def test_calculate_total_normal():
    listing = {"price": 12.34, "shipping": 5.67}
    assert round(calculate_total(listing), 2) == 18.01

def test_calculate_total_zero_shipping():
    listing = {"price": 12.34, "shipping": 0}
    assert round(calculate_total(listing), 2) == 12.34

def test_calculate_total_zero_price():
    listing = {"price": 0, "shipping": 5.67}
    assert round(calculate_total(listing), 2) == 5.67


#           SEARCH_MATCH TESTS

def test_search_match_exact_match():
    listings = {"title": "Apple Macbook Air M1"}
    search_words = ["apple", "macbook", "air", "m1"]
    assert search_match(listings, search_words) == True

def test_search_match_exact_match_case_sensative():
    listings = {"title": "apple MACBOOK AiR M1"}
    search_words = ["apple", "macbook", "air", "m1"]
    assert search_match(listings, search_words) == True

def test_search_extra_words_in_title():
    listings = {"title": "Apple Macbook Air M1"}
    search_words = ["apple"]
    assert search_match(listings, search_words) == True

def test_search_match_partial_match():
    listings = {"title": "Apple Macbook Air M1"}
    search_words = ["apple", "macbook", "air", "m1", "nonexistent"]
    assert search_match(listings, search_words) == False

def test_search_match_none_match():
    listings = {"title": "Apple Macbook Air M1"}
    search_words = ["Samsung", "tablet", "Note11", "black"]
    assert search_match(listings, search_words) == False

#           PRICE_MATCH TESTS
def test_price_match_under_max():
    listing = {"price": 9.99, "shipping": 10.00}
    max_price = 20.00
    assert price_match(listing, max_price) == True

def test_price_match_exact_max():
    listing = {"price": 20.00, "shipping": 0}
    max_price = 20.00
    assert price_match(listing, max_price) == True

def test_price_match_over_max():
    listing = {"price": 0.01, "shipping": 20}
    max_price = 20.00
    assert price_match(listing, max_price) == False
