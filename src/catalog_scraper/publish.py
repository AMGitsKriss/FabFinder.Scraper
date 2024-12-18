from data.basepublisher import BasePublisher
from catalog_scraper.opensearch import OpenSearchWriter
from catalog_scraper.rabbit import RabbitWriter
from models.queue_models import DetailsRequestMsg


class CatalogPublisher(BasePublisher):
	def __init__(self, rabbit_writer: RabbitWriter, opensearch_writer: OpenSearchWriter):
		self.rabbit_writer = rabbit_writer
		self.opensearch_writer = opensearch_writer

	def publish(self, data: DetailsRequestMsg):
		self.rabbit_writer.publish(data)
		self.opensearch_writer.publish(data)
