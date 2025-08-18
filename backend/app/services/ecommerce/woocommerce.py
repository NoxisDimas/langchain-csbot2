import requests
from typing import Dict, Any, List
from app.config import get_settings
from .base import OrderStatus, ProductCatalog


settings = get_settings()


class WooCommerceAdapter(OrderStatus, ProductCatalog):
	def __init__(self):
		if not (settings.WOO_BASE_URL and settings.WOO_CONSUMER_KEY and settings.WOO_CONSUMER_SECRET):
			raise RuntimeError("WooCommerce not configured")

	def _auth_params(self) -> Dict[str, str]:
		return {"consumer_key": settings.WOO_CONSUMER_KEY or "", "consumer_secret": settings.WOO_CONSUMER_SECRET or ""}

	def get_order_status(self, order_id: str) -> Dict[str, Any]:
		url = f"{settings.WOO_BASE_URL}/wp-json/wc/v3/orders/{order_id}"
		r = requests.get(url, params=self._auth_params(), timeout=20)
		r.raise_for_status()
		data = r.json()
		return {"order_id": order_id, "status": data.get("status"), "total": data.get("total")}

	def search_products(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
		url = f"{settings.WOO_BASE_URL}/wp-json/wc/v3/products"
		params = {**self._auth_params(), "search": query, "per_page": limit}
		r = requests.get(url, params=params, timeout=20)
		r.raise_for_status()
		items = r.json()
		return [
			{"id": str(p.get("id")), "title": p.get("name"), "url": p.get("permalink")}
			for p in items
		]