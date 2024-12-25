import dataclasses
import json
import logging

from opensearchpy import OpenSearch
from data.basepublisher import BasePublisher
from models.opensearch_models import InventoryItem


class OpenSearchWriter(BasePublisher):
	def __init__(self, index: str):
		self.index = index
		host = 'localhost'  # TODO - Config
		port = 9200  # TODO - Config
		auth = ('admin', '!UL234zxc')  # TODO - Config

		try:
			self.client = OpenSearch(
				hosts=[{'host': host, 'port': port}],
				http_compress=True,  # enables gzip compression for request bodies
				http_auth=auth,
				use_ssl=False,
				verify_certs=False,
				ssl_assert_hostname=False,
				ssl_show_warn=False
			)
			self.__create_index()

		except Exception as ex:
			logging.exception(ex, "Failed to connected to Opensearch")

	# TODO - Other than the mappings, this file is the same as the catalog one.
	# Can the create index call be passed in?
	def __create_index(self):
		if not self.client.indices.exists(index=self.index):
			mapping = {
				"mappings": {
					"properties": {
						"id": {"type": "keyword"},
						"store_id": {"type": "keyword"},
						"store_product_id": {"type": "keyword"},
						"url": {"type": "keyword"},
						"title": {"type": "keyword"},
						"store": {"type": "keyword"},
						"brand": {"type": "keyword"},
						"pattern": {"type": "keyword"},
						"categories": {"type": "keyword"},
						"audiences": {"type": "keyword"},
						"sizes": {"type": "keyword"},
						"fit": {"type": "keyword"},
						"colour": {"type": "keyword"},
						"origin": {"type": "keyword"},
						"creation_time": {"type": "date"}
					}
				}
			}
			self.client.indices.create(self.index, mapping)

	def publish(self, data: InventoryItem):
		message = json.dumps(dataclasses.asdict(data), ensure_ascii=False, indent=4)
		response = self.client.index(self.index, id=data.id, body=message)

		if response is None:
			logging.error("Failed to write document to Opensearch", document=data)
