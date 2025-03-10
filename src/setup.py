import json
import logging
import traceback
import seqlog

from publisher_collection import RabbitPublisherCollection, OpenSearchPublisherCollection
from scrapers.george import GeorgeScraper
from scrapers.hm import HMScraper
from scrapers.mock import MockScraper
from scrapers.ms import MSScraper
from scrapers.scraper import Scraper

class LogInstaller:
	@staticmethod
	def install():
		seqlog.log_to_seq(
			server_url="http://localhost:5341/",
			api_key="hXvwBIJLTrvAURu3kbnU",
			level=logging.INFO,
			batch_size=10,
			auto_flush_timeout=10,  # seconds
			override_root_logger=True,
			json_encoder_class=json.encoder.JSONEncoder,
			# Optional; only specify this if you want to use a custom JSON encoder
			support_extra_properties=True
			# Optional; only specify this if you want to pass additional log record properties via the "extra" argument.

		)
		seqlog.set_callback_on_failure(LogInstaller.log_to_console)
		seqlog.set_global_log_properties(
			Application="FabFinder.Scraper"
		)

		# seq_handler = seqlog.SeqLogHandler(
		# 	server_url="http://localhost:5341/",
		# 	api_key="hXvwBIJLTrvAURu3kbnU",
		# 	batch_size=10,
		# 	auto_flush_timeout=10,  # seconds
		# 	json_encoder_class=json.encoder.JSONEncoder
		# )
		#
		# seqlog.set_callback_on_failure(LogInstaller.log_to_console)
		# seqlog.set_global_log_properties(
		# 	Application="FabFinder.Scraper"
		# )
		#
		# root_logger = logging.getLogger()
		# root_logger.propagate = True
		# while root_logger.handlers:
		# 	root_logger.handlers.pop()
		# root_logger.addHandler(seq_handler)
		# root_logger.setLevel(logging.INFO)

	@staticmethod
	def log_to_console(e):  # type: (requests.RequestException) -> None
		traceback.format_exc()

class ScraperSetup:
	def get_scrapers(self) -> dict[str, Scraper]:
		rabbit_publisher = RabbitPublisherCollection()
		opensearch_publisher = OpenSearchPublisherCollection()

		scrapers = {
			"mock": MockScraper(rabbit_publisher, opensearch_publisher),
			"george": GeorgeScraper(rabbit_publisher, opensearch_publisher),
			"hm": HMScraper(rabbit_publisher, opensearch_publisher),
			"ms": MSScraper(rabbit_publisher, opensearch_publisher)
		}
		return scrapers

