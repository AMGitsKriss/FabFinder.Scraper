from playwright.sync_api import Page

from models import InventoryItem


class Scraper:
	def get_catalogue(self, window: Page) -> list[str]:
		pass

	def get_product_details(self, window: Page, url: str) -> list[InventoryItem]:
		pass

	def load_products(self):
		pass
