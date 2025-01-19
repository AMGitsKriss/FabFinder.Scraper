import unittest

import urllib3
from playwright.sync_api import sync_playwright

from publisher_collection import OpenSearchPublisherCollection, RabbitPublisherCollection
from scrapers.george import GeorgeScraper
from setup import LogInstaller


# python -m test ms_test.MyTestCase.test_sequence

class MyTestCase(unittest.TestCase):
	def setUp(self):
		LogInstaller.install()
		urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
		rabbit_publisher = RabbitPublisherCollection()
		opensearch_publisher = OpenSearchPublisherCollection()
		self.scraper = GeorgeScraper(rabbit_publisher, opensearch_publisher)

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

	def test_pyjamas(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			details = self.scraper.get_product_details(
				window,
				"H4sIAG0Xg2cC/2VSwa7TMBD8FSvS41S1adrS5AkhQXlwAVSpEhwoilx7k5g6tmVvXhUQ/47tEErTS6zMjHd2x/sr6axMHknSIBr3uFhwYYHhnDpO50y3ixq0rWHxIU23Rb5e5ZsZh4p2EmeGzxtsZTIjCeusBYWlsYKBr5Zl89TDxmreMSwFDw7XEuGKom1QJnuhzuQLSN1Z8lGrmhwkwDOQff+DttTF6jqwozggTvyMlw/LbZ78Z4S9GYpeLzvsZcBUJ6X/PVmqhm7iXEEhvWvJwTErDAqtAnvssjTLjrizcCEK2PnVyZLF66Maidgq66oKOHGx46nivUD0ZAPtlDnoCsnzMHJFTz6zqeJJUoeC0VDgQoXDqSAjTnDwzsIQo9kZ0N35+4GJBFVj4496Su+G3qk6SxgiFC21fem/dcxwk26KZVGsVttsm8YkgWnF/2mcF327VZVvgu4WensP7e6hd8l3j7XCsVKoSl/fa8in9JtotBPj8xTrB7LXsgeHYMnLBxIDoypOUoPiENflq25BxS04dSGj8naTIjOuzKAln0Xd4AWoJS/8JgpjwEbZEOS1r8Fk51+o1raPUfx1i4PQ0Ni490+flst8nRer5PcfcpbJym8DAAA="
			)
		assert details is not None

	def test_tights(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			product = self.scraper.get_product_details(
				window,
				"H4sIAF8krmYC/2WS3WobMRCFX2UQpFfG69/EDqFQmpCrpIEUchGHRZbGa2GtpEqjlm3Ju1eS7Sx2bhZ29syZ+c7sPxa9ZtfAtkQuXFeVVB4FDXmQfChsWzVofYPV/d3DeDxezq4uBxI3PGoaODncUqvZAJiI3qOh2nklMLnNUs15K6OgWsls3/dnveFtlrFH/ruD2Qhu0Sj08MPxXxHhp2q2FGAKT1zsir3VNvrUYKLW6T2ov9i/HQdR54rpvj33Bep0Lr2yh7Swcge7kzHsLVXWnpv9moU2i7Q1TS0xCK8cKWvy11WcjCaTFU0hW92sPVRfV+ZYvdM8kBKcUMIfrgKdCw5zz8uJXxZ+VmBUy31Xp2dTaOaj+XK8vJovRovpokChsEZ+aELhO1HV3wpUq4KoldnYPqoNX6cL1emuzgZ1xFpOLuCxS8CwuIBCwU3JoEEjMefOXmyLpmS6jmKHVJ+f5Bj+XgjPVuwCfIH+FhpNQ9u+Ye/9PaXVWN8ViMOQsntaAv3nf+f9P3ZrmgWwAgAA"
			)
		assert product is not None

	def test_baby_sleep_bag(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			window.add_init_script(script='Object.defineProperty(navigator,"webdriver",{get: () => undefined})')
			product = self.scraper.get_product_details(
				window,
				"H4sIALMXg2cC/11SXWsbMRD8K0LQN+c+e8YNpRCH4Ly4L+lbUw6dtJZFdNKxWj1cS/97JeGkcUAINDs7mh3pD49o+S3jZ6Il3Na1MgiSKhGUqKSfaw0eNdTN0PbDrh+GjYKTiJY2i6rONFu+YVxGRHA0LmgkJLF2qJoEL+hVlDQalS94U8gdTsyZyA8IK3sigewYgzWOPVmAhe2FZl01sB9eF31vfcRXfkaC+V36291Nv2VH7+gc+LsraV1KvcgZp7NiIQRaba64aG06TihccXcoY7JHn3wl3HqnRwVBolnIeJcpz7Fruo5lC18nZPW3Z3eBslXy+gPaNs0nJj1Rai/WzCxwHdOui7eh2fbN7kvX7vptCSWA9E69cUIi/bxmjXeZdw3t+a+EzSbI0biT/z/bSUzpPcb0iIsP5jLFpabBKSiJ7sVUEp2ifAEar6Mukb1mmZlsD0qlPEtG4DSdP2reCwLtcS3mS8v3iAESUGyKQICXH3F4OLbN8Dkt/vcf87k/UogCAAA="
			)
		assert product is not None
