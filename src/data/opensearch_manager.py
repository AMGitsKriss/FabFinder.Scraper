from data.base_manager import BaseManager
from models.opensearch_models import InventoryItem
from models.queue_models import DetailsRequestMsg


class OpensearchManager(BaseManager):

	def write_product_url(self, file: DetailsRequestMsg):
		pass

	def write_product_details(self, product: InventoryItem):
		pass
