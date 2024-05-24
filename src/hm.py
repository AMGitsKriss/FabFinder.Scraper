import os.path
from datetime import datetime

from file_manager import FileManager
from models import *
from tag_mapper import *
from playwright.sync_api import Page
import re
import logging
import random
import time


class HMScraper:
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

	def get_page_url(self, url: str, page_no: int) -> str:
		return f'{url}?sort=newProduct&page={page_no}'

	def refresh_all_products(self, window: Page) -> list[str]:
		product_urls = []

		for n, url in HMScraper.product_collections.items():
			product_urls += self.refesh_category_products(window, url)
			self.file_manager.write_products(os.path.join(self.directory, "all_products.json"), product_urls)

		print(f"Found {len(product_urls)} products.")
		return product_urls

	def refesh_category_products(self, window: Page, url: str) -> list[str]:
		product_urls = []
		page_no = 1

		while True:
			results = list(self.refresh_page_products(window, url, page_no))

			product_urls += results
			page_no += 1

			if len(results) < self.products_per_page:
				break

		return product_urls

	def refresh_page_products(self, window: Page, url: str, page_no: int):
		product_selector = "#products-listing-section ul li .splide ul li:first-of-type a"
		page_no_selector = '#products-listing-section nav[role="navigation"] ul li a[aria-current="true"]'

		# time.sleep(random.randint(2, 5))
		url = self.get_page_url(url, page_no)
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
		products = self.file_manager.read_products(os.path.join(self.directory, "hm_all_products.json"))
		for p in products:
			results[p] = "hm"
		return results

	def get_product_details(self, window: Page, url: str):
		selectors = dict({
			'title': 'section.product-name-price h1',
			'brand': 'section.product-name-price h2 a',
			'price': 'section.product-name-price .price hm-product-price div :first-child',
			'composition': '#section-materialsAndSuppliersAccordion div div div:first-of-type ul li',
			'fit': 'dt:has-text("Fit:") + dd',
			'length': 'dt:has-text("Length:") + dd',
			'style': 'dt:has-text("Style:") + dd',
			'sizes': '#size-selector ul li label',
			'available_colours': '.column2 .inner .product-colors .mini-slider ul li ul li a[aria-checked="true"]',
			'pattern': 'dt:has-text("Description:") + dd',
			'categories': 'nav ol li a',
			'cards': 'meta[property="og:image"]',
			'images': '.column1 .sticky-candidate figure img'
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
		price = float(window.locator(selectors["price"]).text_content().strip().replace("£", ""))

		sizes = [sizes.text_content().lower().replace('few pieces left', '').strip() for sizes in
				 window.locator(selectors["sizes"]).all()]

		raw_colours = window.locator(selectors["available_colours"]).get_attribute("title").lower()
		colour = TagMapper.resolve_colours([], re.split('[,/]', raw_colours))
		image_urls = [image.get_attribute("src") for image in window.locator(selectors["images"]).all()]
		image_urls += [image.get_attribute("content") for image in window.locator(selectors["cards"]).all()]

		origin = window.evaluate(
			f"() => productArticleDetails['{store_id}'].productAttributes.values.productCountryOfProduction")
		if origin is None:
			origin = "unknown"

		fit = "regular fit"
		if window.locator(selectors["fit"]).count() > 0:
			fit = window.locator(selectors["fit"]).text_content().strip().lower()

		length = [info.text_content().strip().lower() for info in window.locator(selectors["length"]).all()]

		style = ""
		if window.locator(selectors["style"]).count() > 0:
			fit = window.locator(selectors["style"]).text_content().strip().lower()

		if window.locator(selectors["brand"]).count() > 0:
			brand = window.locator(selectors["brand"]).text_content().strip()

		raw_categories = [category.text_content().strip().lower() for category in
						  window.locator(selectors["categories"]).all()]
		raw_categories += length
		raw_categories.append(fit)
		raw_categories.append(style)
		categories = TagMapper.resolve_categories(title, raw_categories)

		if len(categories) == 0:
			logging.warning("The raw categories {categories} for product {url} did not map to anything we want to keep.", categories=raw_categories, url=url)
			return None

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
		if any("men" in cat for cat in raw_categories) or "men" in title.lower():
			audiences.append("men")
		if any("women" in cat for cat in raw_categories) or "women" in title.lower():
			audiences.append("women")
		if any("boys" in cat for cat in raw_categories) or "boys" in title.lower():
			audiences.append("boys")
		if any("girls" in cat for cat in raw_categories) or "girls" in title.lower():
			audiences.append("girls")
		if any("unisex" in cat for cat in raw_categories) or "unisex" in title.lower():
			audiences.append("unisex")

		product = InventoryItem(
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
			origin,
			creation_time=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
		)

		self.file_manager.write_products(
			os.path.join(self.directory, f"products/{product.store_id}.json"), product.to_dict())

		return product