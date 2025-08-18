import requests
from typing import Dict, Any, List
from app.config import get_settings
from .base import OrderStatus, ProductCatalog


settings = get_settings()


class TokopediaAdapter(OrderStatus, ProductCatalog):
	def __init__(self):
		if not (settings.TOKO_CLIENT_ID and settings.TOKO_CLIENT_SECRET and settings.TOKO_MERCHANT_ID and settings.TOKO_BASE_URL):
			raise RuntimeError("Tokopedia not configured")
		self.base_url = settings.TOKO_BASE_URL.rstrip("/")

	def get_order_status(self, order_id: str) -> Dict[str, Any]:
		# Placeholder: implement once OAuth token retrieval is available.
		return {"order_id": order_id, "status": "unknown", "note": "Tokopedia adapter stub"}

	def search_products(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
		return []