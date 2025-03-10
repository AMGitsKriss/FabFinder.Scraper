import json
import logging
import sys
import time
import traceback

from playwright.sync_api import sync_playwright, Page

from models.queue_models import DetailsRequestMsg
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
		self.logger = logging.getLogger(__name__)

	def run(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			self.window = browser.new_page()
			self.window.add_init_script(script='Object.defineProperty(navigator,"webdriver",{get: () => undefined})')

			subscriber = RabbitSubscriberBlocking(
				queue_name=self.queue,
				queue_callback=self.catalogue_callback
			)
			subscriber.start()

			pika_logger = logging.getLogger('pika')
			pika_logger.propagate = True

			while subscriber.is_running():
				time.sleep(5)  # TODO - Config

	def catalogue_callback(self, channel, method, properties, message_b):
		message = DetailsRequestMsg(**json.loads(message_b))
		self.logger.info("Getting details for product: {storeCode} {storeId}", storeCode=message.store_code,
						 storeId=message.store_id)
		scraper = self.scrapers[message.store_code]
		try:
			if not self.read_product_details(self.window, scraper, message):
				channel.basic_reject(method.delivery_tag)
			else:
				channel.basic_ack(method.delivery_tag)
		except Exception as ex:
			store = type(scraper).__name__
			handlers = self.logger.handlers
			self.logger.exception("Failed to read {store} catalogue.", store)
			logging.shutdown()
			sys.exit(1)

	def read_product_details(self, window: Page, scraper: Scraper, message: DetailsRequestMsg):
		try:
			scraper.get_product_details(window, message.url)
			return True
		except Exception as ex:
			store = type(scraper).__name__
			self.logger.exception("Failed to read {store} catalogue.", store)
			print(traceback.format_exc())
		return False
