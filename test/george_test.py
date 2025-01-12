import unittest

import urllib3
from playwright.sync_api import sync_playwright

from data.basepublisher import BasePublisher
from data.file_manager import FileManager
from scrapers.george import GeorgeScraper
from setup import LogInstaller


# python -m test ms_test.MyTestCase.test_sequence

class MyTestCase(unittest.TestCase):
	def setUp(self):
		LogInstaller.install()
		urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
		self.scraper = GeorgeScraper(FileManager(), BasePublisher())

	def test_adsa_api_query(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			product_list = self.scraper._GeorgeScraper__refresh_category_products_page(1, 'D2M1G10')
		pass

	def test_composition_parser_1(self):
		composition = "70% Polyester 30% Viscose"
		output = self.scraper._GeorgeScraper__parse_composition(composition)

		for layer in output:
			assert sum(layer.composition.values()) == 1

	def test_tights(self):
		product = self.scraper.get_product_details(
			None,
			"H4sIAF8krmYC/2WS3WobMRCFX2UQpFfG69/EDqFQmpCrpIEUchGHRZbGa2GtpEqjlm3Ju1eS7Sx2bhZ29syZ+c7sPxa9ZtfAtkQuXFeVVB4FDXmQfChsWzVofYPV/d3DeDxezq4uBxI3PGoaODncUqvZAJiI3qOh2nklMLnNUs15K6OgWsls3/dnveFtlrFH/ruD2Qhu0Sj08MPxXxHhp2q2FGAKT1zsir3VNvrUYKLW6T2ov9i/HQdR54rpvj33Bep0Lr2yh7Swcge7kzHsLVXWnpv9moU2i7Q1TS0xCK8cKWvy11WcjCaTFU0hW92sPVRfV+ZYvdM8kBKcUMIfrgKdCw5zz8uJXxZ+VmBUy31Xp2dTaOaj+XK8vJovRovpokChsEZ+aELhO1HV3wpUq4KoldnYPqoNX6cL1emuzgZ1xFpOLuCxS8CwuIBCwU3JoEEjMefOXmyLpmS6jmKHVJ+f5Bj+XgjPVuwCfIH+FhpNQ9u+Ye/9PaXVWN8ViMOQsntaAv3nf+f9P3ZrmgWwAgAA"
		)
		pass
