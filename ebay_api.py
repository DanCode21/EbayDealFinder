import base64
import json
import os
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


TOKEN_URL = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"
BROWSE_SEARCH_URL = "https://api.sandbox.ebay.com/buy/browse/v1/item_summary/search"
DEFAULT_SCOPE = "https://api.ebay.com/oauth/api_scope"


def load_dotenv(path=".env"):
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def get_app_token():
    client_id = os.getenv("EBAY_CLIENT_ID")
    client_secret = os.getenv("EBAY_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise RuntimeError(
            "Missing EBAY_CLIENT_ID or EBAY_CLIENT_SECRET. Add them to .env first."
        )

    credentials = f"{client_id}:{client_secret}".encode("utf-8")
    auth_header = base64.b64encode(credentials).decode("ascii")
    body = urlencode(
        {
            "grant_type": "client_credentials",
            "scope": os.getenv("EBAY_SCOPE", DEFAULT_SCOPE),
        }
    ).encode("utf-8")

    request = Request(
        TOKEN_URL,
        data=body,
        headers={
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )

    return _open_json(request)["access_token"]


def search_items(query, limit=50):
    load_dotenv()
    token = get_app_token()
    params = urlencode({"q": query, "limit": limit})
    marketplace_id = os.getenv("EBAY_MARKETPLACE_ID", "EBAY_US")

    request = Request(
        f"{BROWSE_SEARCH_URL}?{params}",
        headers={
            "Authorization": f"Bearer {token}",
            "X-EBAY-C-MARKETPLACE-ID": marketplace_id,
        },
    )

    data = _open_json(request)
    return [_normalize_item(item) for item in data.get("itemSummaries", [])]


def _normalize_item(item):
    return {
        "title": item.get("title", ""),
        "price": _money_value(item.get("price")),
        "shipping": _shipping_value(item.get("shippingOptions", [])),
        "condition": item.get("condition", "Unknown"),
        "url": item.get("itemWebUrl", ""),
    }


def _money_value(money):
    if not money:
        return 0.0
    return float(money.get("value", 0) or 0)


def _shipping_value(shipping_options):
    shipping_costs = [
        _money_value(option.get("shippingCost"))
        for option in shipping_options
        if option.get("shippingCost") is not None
    ]
    return min(shipping_costs) if shipping_costs else 0.0


def _open_json(request):
    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"eBay API request failed: {error.code} {details}") from error
