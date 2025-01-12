from datetime import datetime

from playwright.sync_api import Page

from models.opensearch_models import InventoryItem
from models.queue_models import DetailsRequestMsg, CatalogueRequestMsg
from publisher_collection import RabbitPublisherCollection, OpenSearchPublisherCollection
from scrapers.scraper import Scraper
from config import *


class MockScraper(Scraper):
	def __init__(self, rabbit_publisher: RabbitPublisherCollection, opensearch_publisher: OpenSearchPublisherCollection):
		self.rabbit_publisher = rabbit_publisher
		self.opensearch_publisher = opensearch_publisher

	def get_categories(self) -> list:
		results = [
			CatalogueRequestMsg("mock", "Cat Name", "http://localhost/CAT", 1)
		]

		for r in results:
			self.rabbit_publisher.get(CATALOGUE_TRIGGER).publish(r)
		return results

	def get_catalogue(self, window: Page, category: CatalogueRequestMsg) -> list[DetailsRequestMsg]:
		results = [
			DetailsRequestMsg("mock", "123", f"{category.url}/123", datetime.now().strftime('%Y-%m-%dT%H:%M:%S')),
			DetailsRequestMsg("mock", "456", f"{category.url}/456", datetime.now().strftime('%Y-%m-%dT%H:%M:%S')),
			DetailsRequestMsg("mock", "789", f"{category.url}/789", datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
		]

		for product in results:
			self.rabbit_publisher.get(DETAILS_TRIGGER).publish(product)
			self.opensearch_publisher.get(CATALOGUE_INDEX).publish(product)

		return results

	def get_product_details(self, window: Page, url: str) -> list[InventoryItem]:
		mock_id = url.replace("http://localhost/", "")
		results = [
			InventoryItem(
				f"mock-{mock_id}",
				"mock",
				mock_id,
				url,
				f"Test {mock_id}",
				"Mock Store",
				"Mock Brand",
				6.99,
				[],
				"plain",
				[],
				[],
				[],
				["s", "m", "l"],
				"regular",
				"black",
				[],
				"UK",
				datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
			)
		]

		for item in results:
			self.opensearch_publisher.get(DETAILS_INDEX).publish(item)

		return results
