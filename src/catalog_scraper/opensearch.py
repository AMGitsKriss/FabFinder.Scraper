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

		# Create the client with SSL/TLS enabled, but hostname verification disabled.
		self.client = OpenSearch(
			hosts=[{'host': host, 'port': port}],
			http_compress=True,  # enables gzip compression for request bodies
			http_auth=auth,
			use_ssl=True,
			verify_certs=False,
			ssl_assert_hostname=False,
			ssl_show_warn=False
		)

		self.__create_index()

	def __create_index(self):
		mapping = {
			"mappings": {
				"properties": {
					"store_code": {"type": "keyword"},
					"url": {"type": "keyword"},
					"read_time": {"type": "date"}
				}
			}
		}
		self.client.indices.create(self.index, mapping)

	def publish(self, data: DetailsRequestMsg):
		response = self.client.index(self.index, data)
		if not response.is_valid:
			logging.error("Failed to write document to Opensearch", document=data)
