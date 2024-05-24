from playwright.sync_api import sync_playwright
import urllib3
import unittest

from src.hm import *
from setup import LogInstaller


# python -m unittest hm_test.MyTestCase.test_tshirt

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
			details = self.scraper.get_product_details(window, "https://www2.hm.com/en_gb/productpage.0685816053.html")
		assert details is not None

	def test_bandeau_dress(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			details = self.scraper.get_product_details(window, "https://www2.hm.com/en_gb/productpage.1191089003.html")
		assert details is not None

	def test_print_tshirt(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			details = self.scraper.get_product_details(window, "https://www2.hm.com/en_gb/productpage.0973277053.html")
		pass

	def test_joggers(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			details = self.scraper.get_product_details(window, "https://www2.hm.com/en_gb/productpage.1002227001.html")
		pass

	def test_cargo_joggers(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			details = self.scraper.get_product_details(window, "https://www2.hm.com/en_gb/productpage.1002227011.html")
		pass

	def test_shirt(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			details = self.scraper.get_product_details(window, "https://www2.hm.com/en_gb/productpage.0976709001.html")
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
			details = self.scraper.get_product_details(window, "https://www2.hm.com/en_gb/productpage.1127533002.html")
		pass

	def test_hat(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			details = self.scraper.get_product_details(window, "https://www2.hm.com/en_gb/productpage.1048600010.html")
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


	def test_no_description(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			details = self.scraper.get_product_details(window, "https://www2.hm.com/en_gb/productpage.1017271001.html")
		pass

