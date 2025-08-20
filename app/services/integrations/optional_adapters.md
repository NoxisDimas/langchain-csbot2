# Optional Integrations

Pluggable adapters can be added under `app/services/integrations/`:
- WhatsApp Business (Cloud API)
- CRM internal (custom REST/GraphQL)
- Shopify / WooCommerce / Shopee / Tokopedia (order status, catalog)

Follow `app/services/ecommerce/base.py` protocol to add providers.