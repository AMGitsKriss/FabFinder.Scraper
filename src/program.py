import json
import os
import sys

from playwright.sync_api import *
import urllib3 # Supress SSL errors for debugging

from hm import *
from setup import LogInstaller


def read_pending():
	file = "../../DATA/stores/pending_products.json"
	result = {}
	try:
		if os.path.isfile(file):
			with open(file, 'r', encoding="utf-8") as f:
				result = json.load(f)
	except:
		logging.exception(f"Failed to read file {file}")
		print(f"Failed to read file {file}")
	return result

def write_pending(obj):
	file = "../../DATA/stores/pending_products.json"
	try:
		with open(file, 'w', encoding="utf-8") as f:
			json.dump(obj, f, ensure_ascii=False, indent=4)
	except:
		logging.exception(f"Failed to write file {file}")
		print(f"Failed to write file {file}")

def read_product_details(window: Page, scraper: HMScraper, url: str):
	try:
		scraper.get_product_details(window, url)
		return True
	except Exception as ex:
		logging.exception(f"Failed to parse page {url}")
		print(f"Failed to parse page {url}")
	return False

def run():
	LogInstaller.install()

	if __debug__:
		urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

	with sync_playwright() as pw:
		browser = pw.chromium.launch(headless=False)
		window = browser.new_page()

		file_manager = FileManager()
		scrapers = {
			"hm": HMScraper(file_manager)
		}

		refresh_products = False
		if refresh_products:
			for store, scraper in scrapers.items():
				scraper.refresh_all_products(window)

		# make the pending-list global
		remaining_product_urls = read_pending()
		if len(remaining_product_urls) == 0:
			for store, scraper in scrapers.items():
				remaining_product_urls = remaining_product_urls | scraper.load_products()
			write_pending(remaining_product_urls)

		# Get and save each product.
		all_product_urls = remaining_product_urls.copy()
		for url, s in all_product_urls.items():
			if read_product_details(window, scrapers[s], url):
				remaining_product_urls.pop(url)
				write_pending(remaining_product_urls)


def main():
	try:
		run()
	except KeyboardInterrupt as ex:
		sys.exit(0)

if __name__ == "__main__":
	main()
