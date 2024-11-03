import json
import logging
import os

class FileManager(DataManager):
	def write_products(self, file: str, to_write):
		try:
			dir = os.path.dirname(file)
			if not os.path.exists(dir):
				os.makedirs(dir)
			with open(file, 'w', encoding="utf-8") as f:
				json.dump(to_write, f, ensure_ascii=False, indent=4)
		except:
			logging.exception(f"Failed to write file {file}")
			print(f"Failed to write file {file}")

	def read_products(self, file: str):
		result = []
		try:
			if os.path.isfile(file):
				with open(file, 'r', encoding="utf-8") as f:
					result = json.load(f)
		except:
			logging.exception(f"Failed to read file {file}")
			print(f"Failed to read file {file}")
		return result