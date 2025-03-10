import dataclasses
import json
import logging
import sys

import pika

from data.basepublisher import BasePublisher


class RabbitWriter(BasePublisher):
	def __init__(self, exchange: str, queue: str):
		try:
			self.logger = logging.getLogger(__name__)
			self.exchange = exchange
			self.queue = queue
			self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
			self.channel = self.connection.channel()
			self.channel.confirm_delivery()
			self.channel.exchange_declare(exchange=self.exchange, exchange_type='direct')
			self.channel.queue_declare(queue=self.queue, durable=True, exclusive=False, auto_delete=False)
			self.channel.queue_bind(exchange=exchange, queue=queue)

			pika_logger = logging.getLogger('pika')
			pika_logger.propagate = True
		except Exception as ex:
			self.logger.exception(ex, "Failed to connected to RabbitMQ")
			logging.shutdown()
			sys.exit(1)

	def publish(self, data):
		try:
			message = json.dumps(dataclasses.asdict(data), ensure_ascii=False, indent=4)
			self.pub_result = self.channel.basic_publish(exchange=self.exchange, routing_key=self.queue, body=message)
		except Exception as ex:
			self.logger.exception(ex, f"Failed to write file {message}")
			logging.shutdown()
			sys.exit(1)
		# TODO - Chanel closed errors?
		pass
