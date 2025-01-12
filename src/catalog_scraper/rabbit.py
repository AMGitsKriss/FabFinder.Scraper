import json
import logging
import time

from playwright.sync_api import sync_playwright, Page

from models.queue_models import CatalogueRequestMsg
from rabbit_subscriber import RabbitSubscriberBlocking
from scrapers.scraper import Scraper


class RabbitReader:
	scrapers: dict[str, Scraper]
	window: Page  # Storign the window here is a bit of a smell...

	def __init__(self, exchange: str, queue: str, scrapers: dict[str, Scraper]):
		self.exchange = exchange
		self.queue = queue
		self.scrapers = scrapers
		self.logger = logging.getLogger(__name__)

	def run(self):
		with sync_playwright() as pw:
			try:
				browser = pw.chromium.launch(headless=False)
				self.window = browser.new_page()

				subscriber = RabbitSubscriberBlocking(
					queue_name=self.queue,
					queue_callback=self.queue_callback,
				)
				subscriber.start()

				while subscriber.is_running():
					time.sleep(5)  # TODO - Config
			except Exception as ex:
				self.logger.exception("Something fell over in the subscriber.")

	def queue_callback(self, channel, method, properties, message_b):
		message = CatalogueRequestMsg(**json.loads(message_b))
		scraper = self.scrapers[message.store_code]

		if not self.read_store_catalogue(self.window, scraper, message):
			channel.basic_nack(delivery_tag=method.delivery_tag)
		else:
			channel.basic_ack(delivery_tag=method.delivery_tag)

	def read_store_catalogue(self, window: Page, scraper: Scraper, message: CatalogueRequestMsg):
		try:
			scraper.get_catalogue(window, message)
			return True
		except Exception as ex:
			self.logger.exception("Failed to read {store} catalogue.", store=type(scraper).__name__)
			print(f"Failed to read {store} catalogue.")
		return False
