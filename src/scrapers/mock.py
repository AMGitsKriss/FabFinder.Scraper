from datetime import datetime

from playwright.sync_api import Page

from data.basepublisher import BasePublisher
from models.opensearch_models import InventoryItem
from models.queue_models import DetailsRequestMsg
from scrapers.scraper import Scraper


class MockScraper(Scraper):
	def __init__(self, publisher: BasePublisher):
		self.publisher = publisher

	def get_catalogue(self, window: Page) -> list[DetailsRequestMsg]:
		results = [
			DetailsRequestMsg("mock", "http://localhost/123", datetime.now().strftime('%Y-%m-%dT%H:%M:%S')),
			DetailsRequestMsg("mock", "http://localhost/456", datetime.now().strftime('%Y-%m-%dT%H:%M:%S')),
			DetailsRequestMsg("mock", "http://localhost/789", datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
		]

		for product in results:
			self.publisher.publish(product)

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

		self.publisher.publish(results)

		return results
