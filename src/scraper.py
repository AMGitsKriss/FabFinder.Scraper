from playwright.sync_api import Page


class Scraper:
	def get_catalogue(self, window: Page) -> list[str]:
		pass

	def get_product_details(self, window: Page, url: str):
		pass

	def load_products(self):
		pass
