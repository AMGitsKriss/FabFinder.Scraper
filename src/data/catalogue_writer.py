from datetime import datetime

from catalog_scraper.rabbit import RabbitWriter
from data.opensearch_manager import OpensearchManager
from models.opensearch_models import InventoryItem
from models.queue_models import DetailsRequestMsg

class CatalogueWriter:
	def __init__(self, rabbit_writer: RabbitWriter, opensearch: OpensearchManager):
		self.rabbit_writer = rabbit_writer
		self.opensearch = opensearch

	def push_product_url(self, store: str, product_url: str, read_time: datetime):
		# TODO - Update the given products in OpenSearch (to keep a full - basic - product list)
		# TODO - Push the given products to Rabbit for importing
		product = DetailsRequestMsg(
			store,
			product_url,
			read_time.strftime('%Y-%m-%dT%H:%M:%S')
		)
		self.rabbit_writer.publish(product)
		self.opensearch.write_product_url(product)

	def push_product_details(self, product: InventoryItem):
		self.opensearch.write_product_details(product)
