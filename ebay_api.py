import base64
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


PRODUCTION_BASE_URL = "https://api.ebay.com"
DEFAULT_SCOPE = "https://api.ebay.com/oauth/api_scope"
DEFAULT_MARKETPLACE_ID = "EBAY_CA"


class EbayApiError(Exception):
    """Base exception for eBay API wrapper failures."""


class EbayConfigError(EbayApiError):
    """Raised when required eBay configuration is missing or invalid."""


class EbayRequestError(EbayApiError):
    """Raised when an eBay request fails."""


@dataclass(frozen=True)
class Money:
    value: float
    currency: str | None = None

    @classmethod
    def from_api(cls, data: dict[str, Any] | None) -> "Money | None":
        if not data:
            return None

        try:
            value = float(data.get("value", 0) or 0)
        except (TypeError, ValueError) as error:
            raise EbayRequestError(f"Invalid money value from eBay: {data!r}") from error

        return cls(value=value, currency=data.get("currency"))


@dataclass(frozen=True)
class EbayListing:
    item_id: str
    title: str
    price: Money
    shipping: Money | None
    condition: str
    url: str
    image_url: str | None = None
    seller_username: str | None = None
    location_country: str | None = None

    @property
    def total(self) -> float:
        return self.price.value + (self.shipping.value if self.shipping else 0.0)

    def to_legacy_dict(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "title": self.title,
            "price": self.price.value,
            "price_currency": self.price.currency,
            "shipping": self.shipping.value if self.shipping else 0.0,
            "shipping_currency": self.shipping.currency if self.shipping else None,
            "condition": self.condition,
            "url": self.url,
            "image_url": self.image_url,
            "seller_username": self.seller_username,
            "location_country": self.location_country,
        }


@dataclass(frozen=True)
class EbayConfig:
    client_id: str
    client_secret: str
    marketplace_id: str = DEFAULT_MARKETPLACE_ID
    scope: str = DEFAULT_SCOPE
    base_url: str = PRODUCTION_BASE_URL

    @classmethod
    def from_env(cls, env_path: str | Path = ".env") -> "EbayConfig":
        load_dotenv(env_path)

        client_id = os.getenv("EBAY_CLIENT_ID")
        client_secret = os.getenv("EBAY_CLIENT_SECRET")
        if not client_id or not client_secret:
            raise EbayConfigError(
                "Missing EBAY_CLIENT_ID or EBAY_CLIENT_SECRET. Add them to .env first."
            )

        return cls(
            client_id=client_id,
            client_secret=client_secret,
            marketplace_id=os.getenv("EBAY_MARKETPLACE_ID", DEFAULT_MARKETPLACE_ID),
            scope=os.getenv("EBAY_SCOPE", DEFAULT_SCOPE),
        )


class EbayClient:
    def __init__(self, config: EbayConfig):
        self.config = config
        self._access_token: str | None = None
        self._token_expires_at = 0.0

    @classmethod
    def from_env(cls, env_path: str | Path = ".env") -> "EbayClient":
        return cls(EbayConfig.from_env(env_path))

    def search_items(self, query: str, limit: int = 50) -> list[EbayListing]:
        if not query.strip():
            raise ValueError("Search query cannot be empty.")
        if not 1 <= limit <= 200:
            raise ValueError("limit must be between 1 and 200.")

        data = self._request_json(
            "GET",
            "/buy/browse/v1/item_summary/search",
            params={"q": query, "limit": str(limit)},
        )

        return [
            self._parse_listing(item)
            for item in data.get("itemSummaries", [])
            if item.get("price")
        ]

    def _get_access_token(self) -> str:
        if self._access_token and time.time() < self._token_expires_at - 60:
            return self._access_token

        credentials = f"{self.config.client_id}:{self.config.client_secret}".encode(
            "utf-8"
        )
        auth_header = base64.b64encode(credentials).decode("ascii")
        body = urlencode(
            {
                "grant_type": "client_credentials",
                "scope": self.config.scope,
            }
        ).encode("utf-8")

        data = self._open_json(
            Request(
                f"{self.config.base_url}/identity/v1/oauth2/token",
                data=body,
                headers={
                    "Authorization": f"Basic {auth_header}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                method="POST",
            )
        )

        self._access_token = data["access_token"]
        self._token_expires_at = time.time() + int(data.get("expires_in", 7200))
        return self._access_token

    def _request_json(
        self,
        method: str,
        path: str,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.config.base_url}{path}"
        if params:
            url = f"{url}?{urlencode(params)}"

        return self._open_json(
            Request(
                url,
                headers={
                    "Authorization": f"Bearer {self._get_access_token()}",
                    "X-EBAY-C-MARKETPLACE-ID": self.config.marketplace_id,
                },
                method=method,
            )
        )

    def _open_json(self, request: Request) -> dict[str, Any]:
        try:
            with urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            details = error.read().decode("utf-8", errors="replace")
            raise EbayRequestError(
                f"eBay API request failed with HTTP {error.code}: {details}"
            ) from error
        except URLError as error:
            raise EbayRequestError(f"Could not reach eBay API: {error.reason}") from error
        except json.JSONDecodeError as error:
            raise EbayRequestError("eBay API returned invalid JSON.") from error

    def _parse_listing(self, item: dict[str, Any]) -> EbayListing:
        price = Money.from_api(item.get("price"))
        if price is None:
            raise EbayRequestError(f"Listing is missing price: {item!r}")

        shipping = self._lowest_shipping_cost(item.get("shippingOptions", []))
        seller = item.get("seller") or {}
        location = item.get("itemLocation") or {}
        image = item.get("image") or {}

        return EbayListing(
            item_id=item.get("itemId", ""),
            title=item.get("title", ""),
            price=price,
            shipping=shipping,
            condition=item.get("condition", "Unknown"),
            url=item.get("itemWebUrl", ""),
            image_url=image.get("imageUrl"),
            seller_username=seller.get("username"),
            location_country=location.get("country"),
        )

    @staticmethod
    def _lowest_shipping_cost(shipping_options: list[dict[str, Any]]) -> Money | None:
        costs = [
            cost
            for cost in (
                Money.from_api(option.get("shippingCost"))
                for option in shipping_options if option.get("type") != "LOCAL_PICKUP"
            )
            if cost is not None
        ]
        if not costs:
            return None
        return min(costs, key=lambda money: money.value)


def load_dotenv(path: str | Path = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), _clean_env_value(value))


def search_items(query: str, limit: int = 50) -> list[dict[str, Any]]:
    """Compatibility helper for the current CLI code."""
    return [
        listing.to_legacy_dict()
        for listing in EbayClient.from_env().search_items(query, limit=limit)
    ]


def _clean_env_value(value: str) -> str:
    cleaned = value.strip().strip('"').strip("'")
    if " #" in cleaned:
        cleaned = cleaned.split(" #", 1)[0].strip()
    return cleaned
