from playwright.sync_api import sync_playwright
from hm import *
import unittest

# python -m unittest hm_test.MyTestCase.test_tshirt

class MyTestCase(unittest.TestCase):

	def test_tshirt(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			product = MSScraper().get_product_details(window, "https://www.marksandspencer.com/straight-fit-pure-cotton-marbled-vintage-wash-jeans/p/clp60678186?color=LIGHTBLUE#intid=pid_pg1pip48g2r1c2|prodflag_New")
		pass

	def test_joggers(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			product = MSScraper().get_product_details(window, "https://www.marksandspencer.com/pure-cotton-half-zip-sweatshirt/p/clp22590802#intid=pid_pg1pip48g4r1c2|prodflag_New")
		pass

	def test_cargo_joggers(self):
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=False)
			context = browser.new_context(viewport={"width": 1280, "height": 720})
			window = context.new_page()
			product = MSScraper().get_product_details(window, "https://www.marksandspencer.com/textured-polo-shirt/p/clp22586469?color=WHITE#intid=pid_pg2pip48g4r1c4|prodflag_New")
		pass
