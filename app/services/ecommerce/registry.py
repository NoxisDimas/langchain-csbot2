from typing import Union
from app.config import get_settings
from .mock import MockEcommerce

from .shopify import ShopifyAdapter
from .woocommerce import WooCommerceAdapter
from .shopee import ShopeeAdapter
from .tokopedia import TokopediaAdapter
from .airtable import AirtableEcommerceAdapter

settings = get_settings()


def get_active_ecommerce():
	# Priority: Shopify -> WooCommerce -> Shopee -> Tokopedia -> Mock
	if ShopifyAdapter and settings.SHOPIFY_STORE_DOMAIN and settings.SHOPIFY_ACCESS_TOKEN:
		try:
			return ShopifyAdapter()
		except Exception:
			pass
	if WooCommerceAdapter and settings.WOO_BASE_URL and settings.WOO_CONSUMER_KEY and settings.WOO_CONSUMER_SECRET:
		try:
			return WooCommerceAdapter()
		except Exception:
			pass
	if ShopeeAdapter and settings.SHOPEE_PARTNER_ID and settings.SHOPEE_PARTNER_KEY and settings.SHOPEE_SHOP_ID and settings.SHOPEE_BASE_URL:
		try:
			return ShopeeAdapter()
		except Exception:
			pass
	if TokopediaAdapter and settings.TOKO_CLIENT_ID and settings.TOKO_CLIENT_SECRET and settings.TOKO_MERCHANT_ID and settings.TOKO_BASE_URL:
		try:
			return TokopediaAdapter()
		except Exception:
			pass
	if AirtableEcommerceAdapter and settings.AIRTABLE_TABLE_NAME and settings.AIRTABLE_BASE_ID and settings.AIRTABLE_API_KEY:
		try:
			return AirtableEcommerceAdapter()
		except Exception:
			pass
	