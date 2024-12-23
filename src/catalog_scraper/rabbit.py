import dataclasses
import json
import logging
import os
import time

import pika
from playwright.sync_api import sync_playwright, Page

from data.basepublisher import BasePublisher
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

	def run(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			self.window = browser.new_page()

			subscriber = RabbitSubscriberBlocking(
				queue_name=self.queue,
				queue_callback=self.queue_callback,
			)
			subscriber.start()

			while subscriber.is_running():
				time.sleep(5)  # TODO - Config

	def queue_callback(self, channel, method, properties, message_b):
		# TODO - Error handle this callback. The desired scraper may not be loaded.
		message = CatalogueRequestMsg(**json.loads(message_b))
		scraper = self.scrapers[message.store_code]
		if not self.read_store_catalogue(self.window, scraper):
			channel.basic_reject(method.delivery_tag)
		else:
			channel.basic_ack(method.delivery_tag)

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
	def __init__(self, exchange: str, queue: str):
		self.exchange = exchange
		self.queue = queue
		self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
		self.channel = self.connection.channel()
		self.channel.confirm_delivery()
		self.channel.exchange_declare(exchange=self.exchange, exchange_type='fanout')
		self.channel.queue_declare(queue = self.queue, durable=True, exclusive=False, auto_delete=False)
		self.channel.queue_bind(exchange=exchange, queue=queue)

	def publish(self, data):
		try:
			message = json.dumps(dataclasses.asdict(data), ensure_ascii=False, indent=4)
			self.pub_result = self.channel.basic_publish(exchange=self.exchange, routing_key=self.queue, body=message)
		except Exception as ex:
			logging.exception(ex, f"Failed to write file {message}")
			print(f"Failed to write file {message}")
			# TODO - Chanel closed errors?
		pass
