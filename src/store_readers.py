import json
import logging
import os
import time

from playwright.sync_api import sync_playwright, Page

from hm import HMScraper
from models import DetailRequestMsg, CatalogueRequestMsg
from rabbit_subscriber import RabbitSubscriberBlocking


class LoopReader:
	def run(self, scrapers):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			window = browser.new_page()

			refresh_products = False
			if refresh_products:
				for store, scraper in scrapers.items():
					scraper.get_catalogue(window)

			# make the pending-list global
			remaining_product_urls = self.read_pending()
			if len(remaining_product_urls) == 0:
				for store, scraper in scrapers.items():
					remaining_product_urls = remaining_product_urls | scraper.load_products()
				self.write_pending(remaining_product_urls)

			# Get and save each product.
			all_product_urls = remaining_product_urls.copy()
			for url, s in all_product_urls.items():
				if self.read_product_details(window, scrapers[s], url):
					remaining_product_urls.pop(url)
					self.write_pending(remaining_product_urls)

	def read_pending(self):
		file = "../../DATA/stores/pending_products.json"
		result = {}
		try:
			if os.path.isfile(file):
				with open(file, 'r', encoding="utf-8") as f:
					result = json.load(f)
		except:
			logging.exception(f"Failed to read file {file}")
			print(f"Failed to read file {file}")
		return result

	def write_pending(self, obj):
		file = "../../DATA/stores/pending_products.json"
		try:
			with open(file, 'w', encoding="utf-8") as f:
				json.dump(obj, f, ensure_ascii=False, indent=4)
		except:
			logging.exception(f"Failed to write file {file}")
			print(f"Failed to write file {file}")

	def read_product_details(self, window: Page, scraper: HMScraper, url: str) -> bool:
		try:
			scraper.get_product_details(window, url)
			return True
		except Exception as ex:
			logging.exception(f"Failed to parse page {url}")
			print(f"Failed to parse page {url}")
		return False


class RabbitReader:
	scrapers: dict[str, HMScraper]
	window: Page

	def run(self, scrapers: dict[str, HMScraper]):
		self.scrapers = scrapers

		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			self.window = browser.new_page()

			subscriber = RabbitSubscriberBlocking(
				read_catalogue=self.catalogue_callback,
				read_product=self.details_callback
			)
			subscriber.start()

			while subscriber.is_running():
				time.sleep(5)

		# refresh_products = False
		# if refresh_products:
		# 	for store, scraper in scrapers.items():
		# 		scraper.refresh_all_products(self.window)

	def catalogue_callback(self, ch, method, properties, message_b):
		message = CatalogueRequestMsg(**json.loads(message_b))
		s = self.scrapers[message.store]
		self.read_store_catalogue(self.window, s)

	def read_store_catalogue(self, window: Page, scraper: HMScraper):
		try:
			scraper.get_catalogue(window)
			return True
		except Exception as ex:
			store = type(scraper).__name__
			logging.exception("Failed to read {store} catalogue.", store)
			print(f"Failed to read {store} catalogue.")
		return False

	def details_callback(self, ch, method, properties, message_b):
		message = DetailRequestMsg(**json.loads(message_b))
		s = self.scrapers[message.store]
		self.read_product_details(self.window, s, message.url)

	def read_product_details(self, window: Page, scraper: HMScraper, url: str) -> bool:
		try:
			scraper.get_product_details(window, url)
			return True
		except Exception as ex:
			logging.exception(f"Failed to parse page {url}")
			print(f"Failed to parse page {url}")
		return False
