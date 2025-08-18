import time
import hmac
import hashlib
import requests
from typing import Dict, Any, List
from app.config import get_settings
from .base import OrderStatus, ProductCatalog


settings = get_settings()


def _sign(path: str, timestamp: int, body: str = "") -> str:
	if not settings.SHOPEE_PARTNER_KEY:
		raise RuntimeError("Shopee not configured")
	base_string = f"{settings.SHOPEE_PARTNER_ID}{path}{timestamp}{settings.SHOPEE_ACCESS_TOKEN if hasattr(settings,'SHOPEE_ACCESS_TOKEN') else ''}{settings.SHOPEE_SHOP_ID}{body}"
	return hmac.new(settings.SHOPEE_PARTNER_KEY.encode(), base_string.encode(), hashlib.sha256).hexdigest()


class ShopeeAdapter(OrderStatus, ProductCatalog):
	def __init__(self):
		if not (settings.SHOPEE_PARTNER_ID and settings.SHOPEE_PARTNER_KEY and settings.SHOPEE_SHOP_ID and settings.SHOPEE_BASE_URL):
			raise RuntimeError("Shopee not configured")
		self.base_url = settings.SHOPEE_BASE_URL.rstrip("/")

	def get_order_status(self, order_id: str) -> Dict[str, Any]:
		# Placeholder: Shopee OpenAPI requires order list/query endpoints. Implement as needed.
		return {"order_id": order_id, "status": "unknown", "note": "Shopee adapter stub"}

	def search_products(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
		# Placeholder: Shopee product search API may require partner-level permissions.
		return []