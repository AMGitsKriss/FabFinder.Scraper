import os
from datetime import datetime

from file_manager import FileManager
from models import *
from playwright.sync_api import Page
import re

from scraper import Scraper


class MSScraper(Scraper):
	directory = "../../DATA/stores/ms"
	products_per_page = 48
	base_url = 'https://www.marksandspencer.com'
	product_collections = [
		'https://www.marksandspencer.com/l/men/mens-hoodies-and-sweatshirts',
		'https://www.marksandspencer.com/l/men/mens-jeans',
		'https://www.marksandspencer.com/l/men/mens-tops'
	]

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

	def __get_page_url(self, url: str, page_no: int):
		return f'{url}?page={page_no}'

	def __refresh_category_products(self, window: Page, url: str) -> list[str]:
		product_urls = []
		page_no = 1

		while True:
			paginated_url = self.__get_page_url(url, page_no)

			results = list(self.__refresh_page_products(window, paginated_url))
			product_urls += results
			page_no += 1

			if len(results) < 48:
				break

		return product_urls

	def __refresh_page_products(self, window: Page, url: str):
		product_grid = "div.grid_container__flAnn"
		product_selector = "div.grid_container__flAnn a[class^='product-card_linkWrapper']"

		window.goto(url)  # go to url
		window.wait_for_selector(product_grid)  # wait for content to load

		products = []

		product_boxes = window.locator(product_selector)
		for box in product_boxes.all():
			product_url = box.get_attribute("href")
			products.append(self.base_url + product_url)
		products = set(products)

		return products

	def get_product_details(self, window: Page, url: str):
		selectors = dict({
			'product_code' : 'main div div div p:has-text("Product code")',
			'title': 'main div h1',
			'brand': 'main div div div p[style="text-transform:uppercase"]',
			'price': 'main div div div p:has-text("£")',
			'fits_sizes' : '.ejht3ye2 li inport[name="size-select"]',
			'composition': '#section-materialsAndSuppliersAccordion div div div:first-of-type ul li',
			'fit': 'dt:has-text("Fit:") + dd',
			'available_colours' : '.column2 .inner .product-colors .mini-slider ul li ul li a',
			'pattern': 'dt:has-text("Description:") + dd',
			'categories' : 'nav ol li a',
			'images' : '.column1 .sticky-candidate figure img'
		})

		# Container: .ejht3ye2
		# Fit: .ejht3ye2 h2
		# Sizes .ejht3ye2 h2 + ul

		window.goto(url)
		window.wait_for_selector(selectors["title"]) 

		store_id = window.locator(selectors["product_code"]).text_content().split(":")[-1].strip()

		id = f"ms-{store_id}"
		title = window.locator(selectors["title"]).text_content().strip()
		store = brand = "M&S"
		price = float(window.locator(selectors["price"]).text_content().strip().replace("£", ""))

		fit_sizes = window.locator(selectors["fits_sizes"])
		size_dict = dict()
		for size in li.all():
			val = size.get_attribute('value').split(' ')
			fit = val[1].lower() if len(val) > 1 else "regular"
			if fit not in size_dict:
				size_dict[fit] = []
			size_dict[fit].append(size[0])



		available_colours = [colour.get_attribute("title").lower() for colour in window.locator(selectors["available_colours"]).all()]
		categories = [category.text_content().strip().lower() for category in window.locator(selectors["categories"]).all()]
		image_urls = [image.get_attribute("src") for image in window.locator(selectors["images"]).all()]
		origin = window.evaluate(f"() => productArticleDetails['{store_id}'].productAttributes.values.productCountryOfProduction")
		if origin is None:
			origin = "unknown"

		fit = None
		if window.locator(selectors["fit"]).count() > 0: 
			fit = window.locator(selectors["fit"]).text_content().strip().lower()

		if window.locator(selectors["brand"]).count() > 0 and True:
			brand = window.locator(selectors["brand"]).text_content().strip()

		composition_detail = []
		for layer in window.locator(selectors["composition"]).all():
			comp_title = None
			info = dict()
			if layer.locator('h4').count() > 0:
				comp_title = layer.locator('h4').text_content().strip().lower().replace(":", "")
			for material in layer.locator('p').text_content().strip().split(','):
				name = re.sub('[0-9%]', '', material).lower()
				percentage = float(re.sub('[a-zA-Z%]', '', material))/100
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
		if "men" in categories or "men" in title.lower():
			audiences.append("men")
		if "women" in categories or "women" in title.lower():
			audiences.append("women")
		if "boys" in categories or "boys" in title.lower():
			audiences.append("boys")
		if "girls" in categories or "girls" in title.lower():
			audiences.append("girls")
		if "unisex" in categories or "unisex" in title.lower():
			audiences.append("unisex")

		return InventoryItem(
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
			available_colours,
			origin,
			creation_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
		)