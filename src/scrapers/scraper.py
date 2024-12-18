from playwright.sync_api import Page

from models.opensearch_models import InventoryItem
from data.basepublisher import BasePublisher


class Scraper:
	def get_catalogue(self, window: Page, writer_callback, publisher: BasePublisher) -> list[str]:
		pass

	def get_product_details(self, window: Page, url: str) -> list[InventoryItem]:
		pass
