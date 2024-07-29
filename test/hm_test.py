from playwright.sync_api import sync_playwright
import urllib3
import unittest

from src.hm import *
from setup import LogInstaller


# python -m test hm_test.MyTestCase.test_tshirt

class MyTestCase(unittest.TestCase):
	def setUp(self):
		LogInstaller.install()
		urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
		self.scraper = HMScraper(FileManager())

	def test_tshirt(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			details = self.scraper.get_product_details(window, "https://www2.hm.com/en_gb/productpage.0685816053.html")[0]
		assert details is not None
		assert 'men' in details.audiences
		assert 'H&M' == details.brand
		assert 'grey' in details.colour
		assert 't-shirts' in details.categories
		assert len(details.composition) == 1
		assert len(details.composition[0].composition) == 2
		assert 'Bangladesh' == details.origin
		assert len(details.sizes) == 8
		assert 'Regular Fit T-shirt' == details.title

	def test_bandeau_dress(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			details = self.scraper.get_product_details(window, "https://www2.hm.com/en_gb/productpage.1191089003.html")[0]
		assert details is not None
		assert 'men' not in details.audiences
		assert 'women' in details.audiences
		assert 'H&M' == details.brand
		assert 'black' in details.colour
		assert 'midi dresses' in details.categories
		assert 'strapless dresses' in details.categories
		assert len(details.composition) == 1
		assert len(details.composition[0].composition) == 4
		assert 'China' == details.origin
		assert len(details.sizes) == 6
		assert 'Knitted bandeau dress' == details.title

	def test_print_tshirt(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			details = self.scraper.get_product_details(window, "https://www2.hm.com/en_gb/productpage.0973277053.html")[0]
		pass

	def test_joggers(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			details = self.scraper.get_product_details(window, "https://www2.hm.com/en_gb/productpage.1002227001.html")[0]
		pass

	def test_cargo_joggers(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			details = self.scraper.get_product_details(window, "https://www2.hm.com/en_gb/productpage.1002227011.html")[0]
		pass

	def test_shirt(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			details = self.scraper.get_product_details(window, "https://www2.hm.com/en_gb/productpage.0976709001.html")[0]
		pass

	def test_sunglasses(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			details = self.scraper.get_product_details(window, "https://www2.hm.com/en_gb/productpage.1044667012.html")
		pass

	def test_shoes(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			details = self.scraper.get_product_details(window, "https://www2.hm.com/en_gb/productpage.1127533002.html")[0]
		pass

	def test_hat(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			details = self.scraper.get_product_details(window, "https://www2.hm.com/en_gb/productpage.1048600010.html")[0]
		pass

	def test_bag(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			details = self.scraper.get_product_details(window, "https://www2.hm.com/en_gb/productpage.1227469001.html")
		pass

	def test_belt(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			self.scraper.get_product_details(window, "https://www2.hm.com/en_gb/productpage.1232911001.html")
		pass


	def test_no_description_name_brand(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			details = self.scraper.get_product_details(window, "https://www2.hm.com/en_gb/productpage.1017271001.html")[0]
		assert details is not None
		assert details.brand == "Weekday"

