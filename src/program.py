import sys
import urllib3  # Supress SSL errors for debugging

from hm import *
from setup import LogInstaller
from store_readers import LoopReader, RabbitReader



def run():
	file_manager = FileManager()
	scrapers = {
		"hm": HMScraper(file_manager)
	}

	#LoopReader().run(scrapers)
	RabbitReader().run(scrapers)


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
