from catalog_scraper.opensearch import OpenSearchWriter
from catalog_scraper.rabbit import RabbitWriter

class BasePublisher:
	def publish(self, data):
		pass

class Publisher(BasePublisher):
	def __init__(self, rabbit_writer: RabbitWriter, opensearch_writer:OpenSearchWriter):
		self.rabbit_writer = rabbit_writer
		self.opensearch_writer = opensearch_writer

	def publish(self, data:ProductUrl):
		self.rabbit_writer.publish(data)
		self.opensearch_writer.publish(data)
