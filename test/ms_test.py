import urllib3
from playwright.sync_api import sync_playwright
import unittest

from data.basepublisher import BasePublisher
from data.file_manager import FileManager
from scrapers.ms import MSScraper
from setup import LogInstaller


# python -m test ms_test.MyTestCase.test_sequence

class MyTestCase(unittest.TestCase):
	def setUp(self):
		LogInstaller.install()
		urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
		self.scraper = MSScraper(FileManager(), BasePublisher())

	def test_catalogue_page(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			product_list = self.scraper._MSScraper__refresh_page_products(
				window,
				"https://www.marksandspencer.com/l/men/mens-hoodies-and-sweatshirts?page=1",
				1)
		pass

	def test_composition_parser_1(self):
		composition = "70% polyamide, 20% silk and 10% elastane (exclusive of trimmings) , Gusset (of underwear) - 100% cotton"
		output = self.scraper._MSScraper__parse_composition(composition)

		for layer in output:
			assert sum(layer.composition.values()) == 1

	def test_composition_parser_2(self):
		composition = "70% polyamide, 20% silk and 10% elastane (exclusive of trimmings), Gusset (of underwear) - 100% cotton"
		output = self.scraper._MSScraper__parse_composition(composition)

		for layer in output:
			assert sum(layer.composition.values()) == 1

	def test_composition_parser_3(self):
		composition = "Outer - 84% recycled polyester, 16% spandex™"
		output = self.scraper._MSScraper__parse_composition(composition)

		for layer in output:
			assert sum(layer.composition.values()) == 1

	def test_composition_parser_4(self):
		composition = "100% viscose lenzing™ ecovero™"
		output = self.scraper._MSScraper__parse_composition(composition)

		for layer in output:
			assert sum(layer.composition.values()) == 1

	def test_composition_parser_5(self):
		composition = "Upper: Textile, Lining: Textile & Leather, Sole: Other Materials"
		output = self.scraper._MSScraper__parse_composition(composition, False)

		for layer in output:
			assert sum(layer.composition.values()) == 1

	def test_jeans(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			product = self.scraper.get_product_details(
				window,
				"https://www.marksandspencer.com/straight-fit-pure-cotton-marbled-vintage-wash-jeans/p/clp60678186?color=LIGHTBLUE#intid=pid_pg1pip48g2r1c2|prodflag_New")
		pass

	def test_hoodie(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			product = self.scraper.get_product_details(
				window,
				"https://www.marksandspencer.com/pure-cotton-half-zip-sweatshirt/p/clp22590802#intid=pid_pg1pip48g4r1c2|prodflag_New")
		pass

	def test_polo(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			product = self.scraper.get_product_details(
				window,
				"https://www.marksandspencer.com/textured-polo-shirt/p/clp22586469?color=WHITE#intid=pid_pg2pip48g4r1c4|prodflag_New")
		pass

	def test_linen_blouse(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			product = self.scraper.get_product_details(window,
													   "https://www.marksandspencer.com/pure-linen-collared-popover-blouse/p/clp60640501?color=BRIGHTBLUE#intid=pid_pg118pip48g4r5c3")
		pass

	def test_kids_backpack(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			products = self.scraper.get_product_details(window,
														"https://www.marksandspencer.com/kids-4pc-printed-backpack-bundle-3-yrs-/p/hbp22589489#intid=pid_pg18pip48g4r10c4|prodflag_New")
		pass

	def test_socks(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			products = self.scraper.get_product_details(
				window,
				"https://www.marksandspencer.com/5pk-cotton-rich-ankle-stripe-socks-6-small-7-large-/p/clp60695859#intid=pid_pg42pip48g4r3c3")
		assert products[0].composition[0].composition['cotton'] == 0.7

	def test_shoes(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			products = self.scraper.get_product_details(
				window,
				"https://www.marksandspencer.com/leather-lace-up-trainers/p/clp22547389?color=TAN#intid=pid_pg17pip48g4r3c2|prodflag_Online%20Only")
		assert products[0].composition[0].composition['upper: textile'] == 1

	def test_bikini(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			products = self.scraper.get_product_details(
				window,
				"https://www.marksandspencer.com/printed-reversible-halterneck-bikini-top/p/clp22588288#intid=pid_pg35pip48g4r1c2|prodflag_Online%20Only")
		assert products[0].composition[0].composition['recycled nylon'] == 0.79

	def test_bikini2(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			products = self.scraper.get_product_details(
				window,
				"https://www.marksandspencer.com/suzie-belted-high-waisted-bikini-bottoms/p/clp23007282#intid=pid_pg97pip48g4r7c3")
		assert products[0].composition[0].composition['recycled polyester'] == 0.84
		assert products[0].composition[0].composition['spandex'] == 0.16

	def test_printed_knickers(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			products = self.scraper.get_product_details(
				window,
				"https://www.marksandspencer.com/peony-silk-and-lace-high-leg-knickers/p/clp60638388#intid=pid_pg1pip48g4r7c3")
		assert products[0].composition[0].composition['polyamide'] == 0.7
		assert products[0].composition[0].composition['silk'] == 0.2

	def test_printed_blouse(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			products = self.scraper.get_product_details(
				window,
				"https://www.marksandspencer.com/printed-tie-neck-shirred-detail-blouse/p/clp23008599#intid=pid_pg7pip48g4r9c3")
		assert products[0].composition[0].composition['viscose lenzing™ ecovero™'] == 1

	def test_printed_midi_dress(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			products = self.scraper.get_product_details(
				window,
				"https://www.marksandspencer.com/jersey-printed-v-neck-midi-waisted-dress/p/clp22581635#intid=pid_pg1pip48g4r10c3%7Cprodflag_Online%2520Only")
		assert products[0].composition[0].composition['cotton'] == 1
