import dataclasses
import logging
import sys

from opensearchpy import OpenSearch

from config import *
from data.basepublisher import BasePublisher
from models.opensearch_models import InventoryItem
from models.queue_models import DetailsRequestMsg


class OpenSearchWriter(BasePublisher):
	def __init__(self, index: str):
		self.logger = logging.getLogger(__name__)
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
			self.logger.exception(ex, "Failed to connected to Opensearch")
			logging.shutdown()
			sys.exit(1)

	def __create_index(self):
		if self.index is CATALOGUE_INDEX:
			self.__create_index_catalogue()
		elif self.index is DETAILS_INDEX:
			self.__create_index_details()

	def __create_index_catalogue(self):
		if not self.client.indices.exists(index=self.index):
			mapping = {
				"mappings": {
					"properties": {
						"store_code": {"type": "keyword"},
						"store_id": {"type": "keyword"},
						"url": {"type": "keyword"},
						"read_time": {"type": "date"}
					}
				}
			}
			self.client.indices.create(self.index, mapping)

	# TODO - Other than the mappings, this file is the same as the catalog one.
	# Can the create index call be passed in?
	def __create_index_details(self):
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
						# "sizes": {"type": "array"},
						"colour": {"type": "keyword"},
						"origin": {"type": "keyword"},
						"creation_time": {"type": "date"}
					}
				}
			}
			self.client.indices.create(self.index, mapping)

	def publish(self, data):
		try:
			identity_field: str = ""
			if type(data) is DetailsRequestMsg:
				identity_field = data.store_id
			elif type(data) is InventoryItem:
				identity_field = data.id

			response = self.client.update(
				index=self.index,
				id=identity_field,
				body={"doc": dataclasses.asdict(data),
					  "doc_as_upsert": True},
				refresh=True)

			# TODO - Error handling.
			if response is None:
				self.logger.error("Failed to write document to Opensearch", document=data)
		except Exception as ex:
			self.logger.exception("Opensearch client threw an exception")
