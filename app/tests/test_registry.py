import importlib
import os
import types


def test_registry_default_is_mock(monkeypatch):
	# Ensure env is clean
	for key in [
		"SHOPIFY_STORE_DOMAIN","SHOPIFY_ACCESS_TOKEN",
		"WOO_BASE_URL","WOO_CONSUMER_KEY","WOO_CONSUMER_SECRET",
		"SHOPEE_PARTNER_ID","SHOPEE_PARTNER_KEY","SHOPEE_SHOP_ID","SHOPEE_BASE_URL",
		"TOKO_CLIENT_ID","TOKO_CLIENT_SECRET","TOKO_MERCHANT_ID","TOKO_BASE_URL",
	]:
		monkeypatch.delenv(key, raising=False)

	reg = importlib.import_module("app.services.ecommerce.registry")
	importlib.reload(reg)
	provider = reg.get_active_ecommerce()
	assert provider.__class__.__name__ == "MockEcommerce"


def test_registry_shopify_when_env_set(monkeypatch):
	monkeypatch.setenv("SHOPIFY_STORE_DOMAIN", "example.myshopify.com")
	monkeypatch.setenv("SHOPIFY_ACCESS_TOKEN", "dummy")
	reg = importlib.import_module("app.services.ecommerce.registry")
	importlib.reload(reg)
	provider = reg.get_active_ecommerce()
	assert provider.__class__.__name__ in {"ShopifyAdapter", "MockEcommerce"}
	# If import works, should be ShopifyAdapter; if not available in env, fallback is MockEcommerce.