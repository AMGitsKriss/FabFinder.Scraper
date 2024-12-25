import dataclasses
import json
import logging

from opensearchpy import OpenSearch

from models.queue_models import DetailsRequestMsg
from data.basepublisher import BasePublisher


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

	def __create_index(self):
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

	def publish(self, data: DetailsRequestMsg):
		message = json.dumps(dataclasses.asdict(data), ensure_ascii=False, indent=4)
		response = self.client.index(self.index, id=data.store_id, body=message)

		# TODO - Error handling.
		if response is None:
			logging.error("Failed to write document to Opensearch", document=data)
