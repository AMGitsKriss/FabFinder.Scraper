import sys

import urllib3

from data.file_manager import FileManager
from details_scraper.opensearch import OpenSearchWriter
from details_scraper.publish import CatalogPublisher
from details_scraper.rabbit import RabbitReader
from scrapers.george import GeorgeScraper
from scrapers.hm import HMScraper
from scrapers.mock import MockScraper
from scrapers.ms import MSScraper
from setup import LogInstaller


def run():
	opensearch_writer = OpenSearchWriter("")
	details_publisher = CatalogPublisher(opensearch_writer)

	scrapers = {
		"mock": MockScraper(details_publisher),
		"hm": HMScraper(None, details_publisher),
		"ms": MSScraper(None, details_publisher),
		"george": GeorgeScraper(None, details_publisher)
	}

	rabbit_reader = RabbitReader("details_trigger", scrapers) # TODO - Config
	rabbit_reader.run()

def setup():
	LogInstaller.install()
	if __debug__:
		urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
	try:
		setup()
		run()
	except KeyboardInterrupt as ex:
		sys.exit(0)

if __name__ == "__main__":
	main()
