from data.basepublisher import BasePublisher
from catalog_scraper.opensearch import OpenSearchWriter
from models.queue_models import DetailsRequestMsg


# TODO - Can this b abstracted with the catalog version?
# Only the number of publishers is different and types are different.
class CatalogPublisher(BasePublisher):
	def __init__(self, opensearch_writer: OpenSearchWriter):
		self.opensearch_writer = opensearch_writer

	def publish(self, data: DetailsRequestMsg):
		self.opensearch_writer.publish(data)
