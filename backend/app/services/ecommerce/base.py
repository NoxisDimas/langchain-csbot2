from typing import Protocol, Optional, Dict, Any, List


class OrderStatus(Protocol):
	def get_order_status(self, order_id: str) -> Dict[str, Any]:
		...


class ProductCatalog(Protocol):
	def search_products(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
		...