class BaseManager:

	# For Files, write_to is a directory: eg C:\list.json
	# For Queues, write_to is a queue name: eg products
	def write_product_details(self, write_to: str, to_write):
		pass

	def read_products(self, file: str):
		pass
