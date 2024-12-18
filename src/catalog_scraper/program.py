import sys
import urllib3

from catalog_scraper.opensearch import OpenSearchWriter
from data.file_manager import FileManager
from catalog_scraper.publish import CatalogPublisher
from catalog_scraper.rabbit import RabbitReader, RabbitWriter
from scrapers.george import GeorgeScraper
from scrapers.hm import HMScraper
from scrapers.mock import MockScraper
from scrapers.ms import MSScraper
from setup import LogInstaller


def run():
	rabbit_writer = RabbitWriter("details_trigger") # TODO - Config
	opensearch_writer = OpenSearchWriter("")
	catalog_publisher = CatalogPublisher(rabbit_writer, opensearch_writer)
	file_manager = FileManager() # TODO - Remove

	scrapers = {
		"mock": MockScraper(file_manager, catalog_publisher),
		"hm": HMScraper(file_manager, catalog_publisher),
		"ms": MSScraper(file_manager, catalog_publisher),
		"george": GeorgeScraper(file_manager, catalog_publisher)
	}

	rabbit_reader = RabbitReader("catalogue_trigger", scrapers) # TODO - Config
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
