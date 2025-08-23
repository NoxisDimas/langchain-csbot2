from app.config import get_settings
import logging
import requests
import os
import json
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
_setting = get_settings()

class AirtableEcommerceAdapter:
    def __init__(self):
        self.TABLE_NAME = _setting.AIRTABLE_TABLE_NAME
        self.BASE_ID = _setting.AIRTABLE_BASE_ID
        self.API_KEY = _setting.AIRTABLE_API_KEY

    def checker(self):
        if not self.TABLE_NAME or not self.BASE_ID or not self.API_KEY:
            raise ValueError("AirtableEcommerceAdapter requires TABLE_NAME, BASE_ID, and API_KEY to be set.")
        if not self.query:
            raise ValueError("Query must be provided to AirtableEcommerceAdapter.")
        return True
    
    def search_products(self, query: str) -> list:
        """Fetch products from Airtable based on the query."""
        ischeck = self.checker()
        if not ischeck:
            raise ValueError("AirtableEcommerceAdapter is not properly initialized.")
        if not query:
            raise ValueError("Query must be provided to search products in Airtable.")
        
        url = f"https://api.airtable.com/v0/{self.BASE_ID}/{self.TABLE_NAME}"
        headers = {
            "Authorization": f"Bearer{self.API_KEY}",
        }
        logging.info(f"Fetching products with query: {query}")
        try:
            response = requests.get(
            url, 
            headers=headers,
            params={
                "filterByFormula": f"SEARCH(LOWER('{query}'), (CONCATENATE({{Nama Produk}}, ' ', {{Kategori}}, ' ', {{Harga}}, ' ', {{Deskripsi}})))"
            }
            )
            if response.status_code != 200:
                logging.error(f"Failed to fetch products: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            records = data.get("records", [])
            products = []
            for record in records:
                fields = record.get("fields", {})
                product_text = "".join([
                    fields.get("Nama Produk", ""),
                    fields.get("Kategori", ""),
                    fields.get("Harga", ""),
                    fields.get("Deskripsi", "")
                ]).lower()
                if query.lower() not in product_text:
                    continue
                
                products.append({
                    "id": record.get("id"),
                    "name": fields.get("Nama Produk", ""),
                    "category": fields.get("Kategori", ""),
                    "price": fields.get("Harga", ""),
                    "description": fields.get("Deskripsi", "")
                })
            return products
        
        except requests.RequestException as e:
            logging.error(f"Error fetching products: {e}")
            return []

