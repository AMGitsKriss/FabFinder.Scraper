import json
import logging
import traceback
import seqlog


class LogInstaller:
	@staticmethod
	def install():
		seqlog.log_to_seq(
			server_url="http://atlas:5341/",
			api_key="lAr93RAGSr1iILEr1Kta",
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

	@staticmethod
	def log_to_console(e):  # type: (requests.RequestException) -> None
		traceback.format_exc()
