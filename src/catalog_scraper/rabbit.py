import json
import logging
import os
import time

import pika
from playwright.sync_api import sync_playwright, Page

from data.basepublisher import BasePublisher
from data.base_manager import BaseManager
from models.queue_models import CatalogueRequestMsg
from rabbit_subscriber import RabbitSubscriberBlocking
from scrapers.scraper import Scraper


class RabbitReader:
	scrapers: dict[str, Scraper]
	window: Page

	def __init__(self, exchange: str, scrapers: dict[str, Scraper]):
		self.exchange = exchange
		self.scrapers = scrapers

	def run(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			self.window = browser.new_page()

			subscriber = RabbitSubscriberBlocking(
				read_catalogue=self.catalogue_callback,
			)
			subscriber.start()

			while subscriber.is_running():
				time.sleep(5)  # TODO - Config

	def catalogue_callback(self, ch, method, properties, message_b):
		message = CatalogueRequestMsg(**json.loads(message_b))
		scraper = self.scrapers[message.store_code]
		self.read_store_catalogue(self.window, scraper)

	def catalogue_write_callback(self, data_manager: BaseManager, directory: str, product_urls: list[str]):
		data_manager.write_product_details(os.path.join(directory, "all_products.json"), product_urls)

	def read_store_catalogue(self, window: Page, scraper: Scraper):
		try:
			scraper.get_catalogue(window)
			return True
		except Exception as ex:
			store = type(scraper).__name__
			logging.exception("Failed to read {store} catalogue.", store)
			print(f"Failed to read {store} catalogue.")
		return False


class RabbitWriter(BasePublisher):
	def __init__(self, exchange: str):
		self.exchange = exchange
		self.connection = pika.BlockingConnection(
			pika.ConnectionParameters(host='localhost'))
		self.channel = self.connection.channel()
		self.channel.exchange_declare(exchange='logs', exchange_type='fanout')

	def publish(self, data):
		try:
			message: str = json.dumps(data, ensure_ascii=False, indent=4)
			self.channel.basic_publish(exchange=self.exchange, routing_key='', body=message)
		except:
			logging.exception(f"Failed to write file {message}")
			print(f"Failed to write file {message}")
