import json
import os
import sys
from pika.adapters.blocking_connection import BlockingChannel


def send(channel: BlockingChannel, message):
	message_str = json.dumps(message.to_dict())
	channel.basic_publish(exchange='',
						  routing_key='hello',
						  body=message_str)


if __name__ == '__main__':
	try:
		print()
		#main()
	except KeyboardInterrupt:
		print('Interrupted')
		try:
			sys.exit(0)
		except SystemExit:
			os._exit(0)
