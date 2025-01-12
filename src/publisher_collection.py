from opensearch import OpenSearchWriter
from rabbit_publisher import RabbitWriter


class RabbitPublisherCollection:
	publishers: dict[str, RabbitWriter]

	def __init__(self):
		self.publishers = dict()

	def add(self, name: str):
		self.publishers[name] = RabbitWriter("/", name)

	def get(self, name: str) -> RabbitWriter:
		if name not in self.publishers.keys():
			self.add(name)

		return self.publishers[name]


class OpenSearchPublisherCollection:
	publishers: dict[str, OpenSearchWriter]

	def __init__(self):
		self.publishers = dict()

	def add(self, index: str):
		self.publishers[index] = OpenSearchWriter(index) # TODO - Config
		# TODO - Can this be added as a callback, this is the only difference between the two collection objects

	def get(self, index: str) -> OpenSearchWriter:
		if index not in self.publishers.keys():
			self.add(index)

		return self.publishers[index]

