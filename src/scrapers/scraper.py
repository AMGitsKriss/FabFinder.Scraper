from playwright.sync_api import Page

from models.opensearch_models import InventoryItem
from data.basepublisher import BasePublisher
from models.queue_models import CatalogueRequestMsg


class Scraper:

	def get_categories(self) -> list[CatalogueRequestMsg]:
		# We're hitting this with a trigger to start scraping this store.
		# This will look at all of the categories for the store, and queue up a catalogue scrape
		# starting with the first page of each category. Those should then self-propogate 1 -> 2 -> 3...
		pass

	def get_catalogue(self, window: Page, category: CatalogueRequestMsg) -> list[str]:
		# We're hitting this with a category url and a page number. It will get all the products on a
		# page, saving them to opensearch and queueing the products for details checks.
		# If the page is full, it will then auto-queue the next page.
		pass

	def get_product_details(self, window: Page, url: str) -> InventoryItem:
		pass
