import os
from datetime import datetime

from file_manager import FileManager
from models import *
from playwright.sync_api import Page, Locator
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
	new_session = True

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
			'cookies': '#onetrust-reject-all-handler',
			'product_code': 'main div div div p:has-text("Product code")',
			'title': 'main div h1',
			'brand': 'main > div[class*=page-container] > div[class*=eco-box] > div#product-info a[class*=brand-title]',
			'price': 'main div div div p:has-text("£")',
			'fits_sizes': 'div[class*=size-selector] > ul > li > label >  input[name="size-select"]',
			'description': '#product-info > div:nth-child(23) > p"]',
			'selected_colour': 'div#product-info > div[class*="eco-box"] > p[class*="eco-box"] > span#selected-colour-option-text',
			'cards': 'meta[property="og:image"]',
			'images': 'div[data-tagg=image-container] img',
			'composition': 'details > div > div > div> p:has-text("%")',
			'categories': 'nav > ul[class*=breadcrumb] > li[class*=breadcrumb] > a[class*=media]'
		})

		window.goto(url)
		window.wait_for_selector(selectors["title"])

		if self.new_session:
			window.wait_for_selector(selectors["cookies"])
			window.locator(selectors["cookies"]).click()

		store_id = window.locator(selectors["product_code"]).text_content().split(":")[-1].strip()
		title = window.locator(selectors["title"]).text_content().strip()
		store = brand = "M&S"
		price = float(window.locator(selectors["price"]).all()[0].text_content().strip().replace("£", ""))

		fit_sizes = window.locator(selectors["fits_sizes"])
		size_dict = dict()
		for size_label in fit_sizes.all():
			# "M Regular", "L Tall", etc.
			val = size_label.get_attribute('value').split(' ')
			fit = val[1].lower() if len(val) > 1 else "regular"  # TODO - Get the default fit from the page!
			size = val[0]
			if fit not in size_dict:
				size_dict[fit] = []
			size_dict[fit].append(size)

		description = ""
		for text in window.locator('#product-info > div > p').all():
			description += text.text_content()
			description += " "
		raw_categories = [category.text_content().strip().lower() for category in
					  window.locator(selectors["categories"]).all()[1:]]

		raw_info = []
		raw_info += raw_categories
		raw_info.append(window.locator(selectors["selected_colour"]).text_content().lower())
		raw_info.append(title)
		raw_info.append(description)
		mapper_response = TagMapper.resolve_tags(raw_info)

		image_urls = [image.get_attribute("content") for image in window.locator(selectors["cards"]).all()]
		image_urls += [image.get_attribute("src") for image in window.locator(selectors["images"]).all()]

		origin = "unknown"

		if window.locator(selectors["brand"]).count() > 0:
			brand = window.locator(selectors["brand"]).text_content().strip()

		# 98% cotton, 2% elastane (exclusive of trimmings) , Jacket lining - 100% cotton , Sleeve lining - 100% polyester
		# 52% viscose lenzing™ ecovero™, 28% polyester and 20% nylon

		raw_composition = ""
		for element in window.locator(selectors["composition"]).all():
			raw_composition += element.text_content()
			raw_composition += " "
		composition_detail = self.parse_composition(raw_composition)

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

	def parse_composition(self, raw_composition: str) -> list[CompositionDetail]:
		# 98% cotton, 2% elastane (exclusive of trimmings) , Jacket lining - 100% cotton , Sleeve lining - 100% polyester
		# 52% viscose lenzing™ ecovero™, 28% polyester and 20% nylon

		composition_detail = []

		for layer in raw_composition.split(' , '): # comma with extra spacing seems to indicate a layer seperator
			info = dict()

			title = None
			if ' - ' in layer:
				title = layer.split(' - ')[0].strip()

			for material in re.split(',|and', layer):
				name = re.sub('[0-9%]', '', material).lower().strip()
				percentage = float(re.sub('[^0-9.]', '', material)) / 100
				info[name] = percentage
			composition_detail.append(CompositionDetail(None, info))

		return composition_detail
