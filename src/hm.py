import os.path
from datetime import datetime

from file_manager import FileManager
from models import *
from scraper import Scraper
from tag_mapper import *
from playwright.sync_api import Page
import re
import logging
import random
import time


class HMScraper(Scraper):
	directory = "../../DATA/stores/hm"
	products_per_page = 36
	product_collections = {
		'men': 'https://www2.hm.com/en_gb/men/shop-by-product/view-all.html',
		'women': 'https://www2.hm.com/en_gb/ladies/shop-by-product/view-all.html',
		'boys_young': 'https://www2.hm.com/en_gb/kids/boys/all.html',
		'boys_teen': 'https://www2.hm.com/en_gb/kids/boys-9-14y/view-all.html',
		'girls_young': 'https://www2.hm.com/en_gb/kids/girls/all.html',
		'girls_teen': 'https://www2.hm.com/en_gb/kids/girls-9-14y/view-all.html'
	}

	def __init__(self, file_manager: FileManager):
		self.file_manager = file_manager

	def get_catalogue(self, window: Page) -> list[str]:
		product_urls = []

		for n, url in self.product_collections.items():
			product_urls += self.__refresh_category_products(window, url)
			# Update the big product list after each collection iteration. We don't want an all-or-nothing update
			self.file_manager.write_products(os.path.join(self.directory, "all_products.json"), product_urls)

		print(f"Found {len(product_urls)} products.")

		return product_urls

	def __get_page_url(self, url: str, page_no: int) -> str:
		return f'{url}?sort=newProduct&page={page_no}'

	def __refresh_category_products(self, window: Page, url: str) -> list[str]:
		product_urls = []
		page_no = 1

		while True:
			results = list(self.__refresh_page_products(window, url, page_no))

			product_urls += results
			page_no += 1

			if len(results) < self.products_per_page:
				break

		return product_urls

	def __refresh_page_products(self, window: Page, url: str, page_no: int):
		product_selector = "#products-listing-section ul li .splide ul li:first-of-type a"
		page_no_selector = '#products-listing-section nav[role="navigation"] ul li a[aria-current="true"]'

		# time.sleep(random.randint(2, 5))
		url = self.__get_page_url(url, page_no)
		products = []

		try:
			window.goto(url, wait_until='load')  # go to url

			window.wait_for_selector(page_no_selector)
			if page_no != int(window.locator(page_no_selector).text_content()):
				return products

			product_boxes = window.locator(product_selector)
			for box in product_boxes.all():
				product_url = box.get_attribute("href")
				products.append(product_url)
			logging.info(f"Successfully read page {url}")
		except:
			logging.exception(f"Failed to load page {url}")
			print(f"Failed to load page {url}")

		return products

	def load_products(self):
		results = {}
		products = self.file_manager.read_products(os.path.join(self.directory, "all_products.json"))
		for p in products:
			results[p] = "hm"
		return results

	def get_product_details(self, window: Page, url: str) -> list[InventoryItem]:
		selectors = dict({
			'title': 'h1',
			'brand': '#__next > div.b0981f.d0fdd1 > div.rOGz > div > div > div.c58e1c.fe1f77.d12085.c9ee6e > div > div > div.ff0cbd.aef620 > div > h2 > a',
			'price': '#__next > div.b0981f.d0fdd1 > div.rOGz > div > div > div.c58e1c.fe1f77.d12085.c9ee6e > div > div > div.e26896 > span',
			'sizes': '[data-testid="size-selector"] label', ## id^=sizeButton-*
			'images': 'ul[data-testid="grid-gallery"] img',
			'materials_accordion': '#toggle-materialsAndSuppliersAccordion',
			'origin_button': '#section-materialsAndSuppliersAccordion > div > div > button',
			'origin_text': '#section-materialsAndSuppliersAccordion > div > div > div.db9e00 > div > div.ca411a > div:nth-child(4) > h3',
			'composition': '#section-materialsAndSuppliersAccordion div div div:first-of-type ul li',
			'fit': 'dt:has-text("Fit:") + dd',
			'length': 'dt:has-text("Length:") + dd',
			'style': 'dt:has-text("Style:") + dd',
			'selected_colour': '#__next > div > div.rOGz > div > div > div > div > div > div > div > div > div > a[aria-checked="true"]',
			'pattern': 'dt:has-text("Description:") + dd',
			'categories': 'nav ol li a',
			'cards': 'meta[property="og:image"]'
		})

		try:
			window.goto(url, wait_until='load')
			time.sleep(random.randint(2, 5))
		except Exception as ex:
			logging.exception("Network issue. Failed to go to {url}.", url=url)
			return None

		window.wait_for_selector(selectors["title"])

		store_id = url.split(".")[-2]
		id = f"hm-{store_id}"

		title = window.locator(selectors["title"]).text_content().strip()
		store = brand = "H&M"
		price = float(window.locator(selectors["price"]).all()[0].text_content().strip().replace("£", ""))

		sizes = [sizes.text_content().lower()
				 .replace('few pieces left', '')
				 .replace('sold out', '')
				 .strip()
				 for sizes
				 in window.locator(selectors["sizes"]).all()]

		image_urls = [image.get_attribute("content") for image in window.locator(selectors["cards"]).all()]

		origin = "unknown"
		window.evaluate("() => window.scrollBy(0, 2000)")
		window.wait_for_selector(selectors['materials_accordion'])
		window.locator(selectors['materials_accordion']).click()
		try:
			window.wait_for_selector(selectors['origin_button'], timeout=5000)
			if window.locator(selectors['origin_button']).count() > 0:
				window.locator(selectors['origin_button']).click()
				window.wait_for_selector(selectors['origin_text'])
				if window.locator(selectors["origin_text"]).count() > 0:
					origin = window.locator(selectors['origin_text']).text_content()
		except:
			pass

		fit = "regular fit"
		if window.locator(selectors["fit"]).count() > 0:
			fit = window.locator(selectors["fit"]).text_content().strip().lower()

		style = ""
		if window.locator(selectors["style"]).count() > 0:
			style = window.locator(selectors["style"]).text_content().strip().lower()

		if window.locator(selectors["brand"]).count() > 0:
			brand = window.locator(selectors["brand"]).text_content().strip()

		raw_categories = [category.text_content().strip().lower() for category in
						  window.locator(selectors["categories"]).all()]
		raw_categories += [info.text_content().strip().lower() for info in window.locator(selectors["length"]).all()]
		raw_categories.append(window.locator(selectors["selected_colour"]).get_attribute("title").lower())
		raw_categories.append(fit)
		raw_categories.append(style)
		raw_categories.append(title)
		mapper_response = TagMapper.resolve_tags(raw_categories)

		categories = mapper_response.categories.tags
		if len(categories) == 0:
			logging.warning("Product {url} did not map to any categories.", categories=raw_categories, url=url)
			return None

		colour = mapper_response.colours.tags
		if colour is None or len(colour) == 0:
			logging.warning("Product {url} did not map to any colours.", categories=raw_categories, url=url)
			return None

		tags = []
		if mapper_response.tags is not None and mapper_response.tags.tags is not None:
			tags = mapper_response.tags.tags

		composition_detail = []
		for layer in window.locator(selectors["composition"]).all():
			comp_title = None
			info = dict()
			if layer.locator('h4').count() > 0:
				comp_title = layer.locator('h4').text_content().lower().replace(":", "").strip()
			for material in layer.locator('p').text_content().strip().split(','):
				name = re.sub('[0-9%]', '', material).lower().strip()
				percentage = float(re.sub('[a-zA-Z%]', '', material)) / 100
				info[name] = percentage
			composition_detail.append(CompositionDetail(comp_title, info))

		description_detail = window.locator(selectors["pattern"])
		pattern = "solid"
		if description_detail.count() > 0:
			description = description_detail.text_content().strip().lower()
			if "floral" in description.lower():
				pattern = "floral"
			elif "striped" in description.lower():
				pattern = "striped"
		elif "printed" in title.lower():
			pattern = "printed"
		elif "floral" in title.lower():
			pattern = "floral"

		audiences = []
		if any("men" == cat for cat in raw_categories):
			audiences.append("men")
		if any("women" == cat for cat in raw_categories):
			audiences.append("women")
		if any("boys" in cat for cat in raw_categories) or "boys" in title.lower():
			audiences.append("boys")
		if any("girls" in cat for cat in raw_categories) or "girls" in title.lower():
			audiences.append("girls")
		if any("unisex" in cat for cat in raw_categories) or "unisex" in title.lower():
			audiences.append("unisex")

		products = [InventoryItem(
			id,
			store_id,
			url,
			title,
			store,
			brand,
			price,
			composition_detail,
			pattern,
			categories,
			image_urls,
			audiences,
			sizes,
			fit,
			colour,
			tags,
			origin,
			creation_time=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
		)]

		for p in products:
			self.file_manager.write_products(
				os.path.join(self.directory, f"products/{p.store_id}.json"), p.to_dict())

		return products