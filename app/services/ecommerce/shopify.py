import requests
from typing import Dict, Any, List
from app.config import get_settings
from .base import OrderStatus, ProductCatalog


settings = get_settings()


def _shopify_headers():
	if not settings.SHOPIFY_ACCESS_TOKEN:
		raise RuntimeError("Shopify not configured")
	return {"X-Shopify-Access-Token": settings.SHOPIFY_ACCESS_TOKEN, "Content-Type": "application/json"}


class ShopifyAdapter(OrderStatus, ProductCatalog):
	base_url: str

	def __init__(self):
		if not (settings.SHOPIFY_STORE_DOMAIN and settings.SHOPIFY_ACCESS_TOKEN):
			raise RuntimeError("Shopify not configured")
		self.base_url = f"https://{settings.SHOPIFY_STORE_DOMAIN}/admin/api/2024-01"

	def get_order_status(self, order_id: str) -> Dict[str, Any]:
		url = f"{self.base_url}/orders/{order_id}.json"
		r = requests.get(url, headers=_shopify_headers(), timeout=20)
		r.raise_for_status()
		order = r.json().get("order", {})
		fulfill = order.get("fulfillment_status")
		financial = order.get("financial_status")
		return {"order_id": order_id, "fulfillment_status": fulfill, "financial_status": financial}

	def search_products(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
		url = f"{self.base_url}/products.json?limit={limit}&title={requests.utils.quote(query)}"
		r = requests.get(url, headers=_shopify_headers(), timeout=20)
		r.raise_for_status()
		products = r.json().get("products", [])
		return [
			{
				"id": str(p.get("id")),
				"title": p.get("title"),
				"url": f"https://{settings.SHOPIFY_STORE_DOMAIN}/products/{(p.get('handle') or '')}",
			}
			for p in products
		]