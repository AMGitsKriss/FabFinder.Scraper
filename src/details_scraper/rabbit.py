import json
import logging
import time

from playwright.sync_api import sync_playwright, Page

from models.queue_models import CatalogueRequestMsg
from rabbit_subscriber import RabbitSubscriberBlocking
from scrapers.scraper import Scraper


# TODO - Same code as in catalog scraper. Share it.
class RabbitReader:
	scrapers: dict[str, Scraper]
	window: Page

	def __init__(self, exchange: str, queue: str, scrapers: dict[str, Scraper]):
		self.exchange = exchange
		self.queue = queue
		self.scrapers = scrapers

	def run(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			self.window = browser.new_page()

			subscriber = RabbitSubscriberBlocking(
				queue_name=self.queue,
				read_catalogue=self.catalogue_callback,
			)
			subscriber.start()

			while subscriber.is_running():
				time.sleep(5)  # TODO - Config

	def catalogue_callback(self, ch, method, properties, message_b):
		message = CatalogueRequestMsg(**json.loads(message_b))
		scraper = self.scrapers[message.store_code]
		self.read_store_catalogue(self.window, scraper)

	def read_store_catalogue(self, window: Page, scraper: Scraper):
		try:
			scraper.get_catalogue(window)
			return True
		except Exception as ex:
			store = type(scraper).__name__
			logging.exception("Failed to read {store} catalogue.", store)
			print(f"Failed to read {store} catalogue.")
		return False
