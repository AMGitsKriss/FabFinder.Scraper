import pika
from pika.adapters.select_connection import SelectConnection
from pika.channel import Channel


class RabbitSubscriber:
	connection: SelectConnection
	channel: Channel

	def __init__(self, callback):
		self.connection = pika.SelectConnection(pika.ConnectionParameters('localhost'), on_open_callback=self.on_open)
		self.callback = callback

	def on_open(self, connection):
		connection.channel(on_open_callback=self.on_channel_open)

	def on_channel_open(self, channel):
		channel.basic_consume(queue='read_product', auto_ack=True, on_message_callback=self.callback)

	def start(self):
		self.connection.ioloop.start()

	def stop(self):
		self.connection.close()

	def is_running(self) -> bool:
		return self.connection.is_open()