import urllib3
from playwright.sync_api import sync_playwright
import unittest

from file_manager import FileManager
from ms import MSScraper
from setup import LogInstaller


# python -m unittest hm_test.MyTestCase.test_tshirt

class MyTestCase(unittest.TestCase):
	def setUp(self):
		LogInstaller.install()
		urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
		self.scraper = MSScraper(FileManager())

	def test_catalogue_page(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			product_list = self.scraper._MSScraper__refresh_page_products(window, "https://www.marksandspencer.com/l/men/mens-hoodies-and-sweatshirts?page=1", 1)
		pass

	def test_jeans(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			product = self.scraper.get_product_details(window, "https://www.marksandspencer.com/straight-fit-pure-cotton-marbled-vintage-wash-jeans/p/clp60678186?color=LIGHTBLUE#intid=pid_pg1pip48g2r1c2|prodflag_New")
		pass

	def test_hoodie(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			product = self.scraper.get_product_details(window, "https://www.marksandspencer.com/pure-cotton-half-zip-sweatshirt/p/clp22590802#intid=pid_pg1pip48g4r1c2|prodflag_New")
		pass

	def test_polo(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			product = self.scraper.get_product_details(window, "https://www.marksandspencer.com/textured-polo-shirt/p/clp22586469?color=WHITE#intid=pid_pg2pip48g4r1c4|prodflag_New")
		pass
