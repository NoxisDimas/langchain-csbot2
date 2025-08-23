from typing import Dict, Any, List
from .base import OrderStatus, ProductCatalog


class MockEcommerce(OrderStatus, ProductCatalog):
	def get_order_status(self, order_id: str) -> Dict[str, Any]:
		return {"order_id": order_id, "status": "in_transit", "eta": "tomorrow"}

	def search_products(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
		print(f"Mock search for products with query: {query}")
		return [
			{"id": "sku-blue-shirt", "title": "Blue Casual Shirt", "size": "L", "url": "https://example.com/product/blue-shirt"}
		]