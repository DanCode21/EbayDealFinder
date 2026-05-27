from ebay_api import search_items

items = search_items("rtx 3070", limit=3)

print(items)

