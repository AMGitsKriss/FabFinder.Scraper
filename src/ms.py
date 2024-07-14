import os
from datetime import datetime

from file_manager import FileManager
from models import *
from playwright.sync_api import Page
import re

from scraper import Scraper
from tag_mapper import TagMapper


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

	def get_product_details(self, window: Page, url: str) -> list[InventoryItem]:
		selectors = dict({
			'product_code' : 'main div div div p:has-text("Product code")',
			'title': 'main div h1',
			'brand': 'main > div[class*=page-container] > div[class*=eco-box] > div#product-info a[class*=brand-title]',
			'price': 'main div div div p:has-text("£")',
			'fits_sizes' : 'div[class*=size-selector] > ul > li > label >  input[name="size-select"]',
			'description': 'div[class*="page-container"] > div[class*="eco-box"] > div[class*="eco-box"] > div[class*="css"] > p[class*="media-0_body"]',
			'selected_colour' : 'div#product-info > div[class*="eco-box"] > p[class*="eco-box"] > span#selected-colour-option-text',
			'cards': 'meta[property="og:image"]',
			'images' : 'div[data-tagg=image-container] img',
			'composition': 'div[class*=accordion] > details > div[class*=accordion] > div[class*=css] > div[class*=css] > p[class*=media-0_body]:has-text("%")',
			'categories' : 'nav > ul[class*=breadcrumb] > li[class*=breadcrumb] > a[class*=media]'
		})

		window.goto(url)
		window.wait_for_selector(selectors["title"])

		store_id = window.locator(selectors["product_code"]).text_content().split(":")[-1].strip()
		title = window.locator(selectors["title"]).text_content().strip()
		store = brand = "M&S"
		price = float(window.locator(selectors["price"]).all()[0].text_content().strip().replace("£", ""))

		fit_sizes = window.locator(selectors["fits_sizes"])
		size_dict = dict()
		for size_label in fit_sizes.all():
			# "M Regular", "L Tall", etc.
			val = size_label.get_attribute('value').split(' ')
			fit = val[1].lower() if len(val) > 1 else "regular" # TODO - Get the default fit from the page!
			size = val[0]
			if fit not in size_dict:
				size_dict[fit] = []
			size_dict[fit].append(size)

		description = window.locator(selectors["description"]).text_content()
		categories = [category.text_content().strip().lower() for category in
						  window.locator(selectors["categories"]).all()[1:]]

		raw_info = []
		raw_info += categories
		raw_info.append(window.locator(selectors["selected_colour"]).text_content().lower())
		raw_info.append(title)
		raw_info.append(description)
		mapper_response = TagMapper.resolve_tags(raw_info)

		image_urls = [image.get_attribute("content") for image in window.locator(selectors["cards"]).all()]
		image_urls += [image.get_attribute("src") for image in window.locator(selectors["images"]).all()]

		origin = "unknown"

		if window.locator(selectors["brand"]).count() > 0:
			brand = window.locator(selectors["brand"]).text_content().strip()

		composition_detail = []
		raw_composition = window.locator(selectors["composition"]).text_content()
		for layer in raw_composition.split(' - '):
			info = dict()
			for material in re.split(',|and', layer):
				name = re.sub('[0-9%]', '', material).lower().strip()
				percentage = float(re.sub('[^0-9.]', '', material))/100
				info[name] = percentage
			composition_detail.append(CompositionDetail(None, info))

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

		products = []
		for fit, sizes in size_dict.items():
			products.append(InventoryItem(
				f"ms-{store_id}-{fit}",
				store_id,
				url,
				title,
				store,
				brand,
				price,
				composition_detail,
				mapper_response.pattern,
				mapper_response.categories.tags,
				image_urls,
				audiences,
				sizes,
				fit,
				mapper_response.colours.tags,
				mapper_response.tags.tags,
				origin,
				creation_time=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
			))

		for p in products:
			self.file_manager.write_products(
				os.path.join(self.directory, f"products/{p.id}.json"), p.to_dict())

		return products