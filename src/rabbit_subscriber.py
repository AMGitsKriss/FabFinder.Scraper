import pika
import time

from pika.adapters.select_connection import SelectConnection
from pika.channel import Channel


class RabbitSubscriberBlocking:
	connection: SelectConnection
	channel: Channel

	def __init__(self, queue_name: str, queue_callback):
		self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
		self.channel = self.connection.channel()

		self.channel.queue_declare(queue = queue_name, durable=True, exclusive=False, auto_delete=False)
		self.channel.basic_consume(queue=queue_name,
								   auto_ack=False,
								   on_message_callback=queue_callback)

	def start(self):
		self.channel.start_consuming()

	def stop(self):
		self.connection.close()

	def is_running(self) -> bool:
		return self.connection.is_open()


class RabbitSubscriberNonBlock:
	connection: SelectConnection
	channel: Channel

	def __init__(self, *callbacks):
		self.connection = pika.SelectConnection(pika.ConnectionParameters('localhost'), on_open_callback=self.on_open)
		self.callbacks = {}

		for (q_name, callback) in callbacks:
			self.callbacks[q_name] = callback

	def on_open(self, connection):
		connection.channel(on_open_callback=self.on_channel_open)

	def on_channel_open(self, channel):
		for (q_name, callback) in self.callbacks:
			channel.basic_consume(queue=q_name, auto_ack=True, on_message_callback=callback)

	def start(self):
		self.connection.ioloop.start()

	def stop(self):
		self.connection.close()

	def is_running(self) -> bool:
		return self.connection.is_open()
