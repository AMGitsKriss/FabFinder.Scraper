from data.basepublisher import BasePublisher
from details_scraper.opensearch import OpenSearchWriter
from models.opensearch_models import InventoryItem


# TODO - Can this b abstracted with the catalog version?
# Only the number of publishers is different and types are different.
class DetailsPublisher(BasePublisher):
	def __init__(self, opensearch_writer: OpenSearchWriter):
		self.opensearch_writer = opensearch_writer

	def publish(self, data: InventoryItem):
		self.opensearch_writer.publish(data)
