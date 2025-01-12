import sys

import urllib3

from catalog_scraper.rabbit import RabbitReader
from config import CATALOGUE_TRIGGER
from setup import LogInstaller, ScraperSetup


def run():
	scrapers = ScraperSetup().get_scrapers()

	rabbit_reader = RabbitReader("/", CATALOGUE_TRIGGER, scrapers) # TODO - Config
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
