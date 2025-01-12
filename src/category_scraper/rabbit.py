import json
import logging
import time

from models.queue_models import CategoryRequestMsg
from rabbit_subscriber import RabbitSubscriberBlocking
from scrapers.scraper import Scraper


class RabbitReader:
	scrapers: dict[str, Scraper]

	def __init__(self, exchange: str, queue: str, scrapers: dict[str, Scraper]):
		self.exchange = exchange
		self.queue = queue
		self.scrapers = scrapers
		self.logger = logging.getLogger(__name__)

	def run(self):
		try:
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
		message = CategoryRequestMsg(**json.loads(message_b))
		scraper = self.scrapers[message.store_code]

		if not self.read_store_categories(scraper):
			channel.basic_nack(delivery_tag=method.delivery_tag)
		else:
			channel.basic_ack(delivery_tag=method.delivery_tag)

	def read_store_categories(self, scraper: Scraper):
		try:
			scraper.get_categories()
			return True
		except Exception as ex:
			self.logger.exception("Failed to read {store} catalogue.", store=type(scraper).__name__)
		return False
