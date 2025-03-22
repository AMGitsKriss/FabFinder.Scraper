from datetime import datetime

from config import CATALOGUE_TRIGGER, DETAILS_TRIGGER, CATALOGUE_INDEX, DETAILS_INDEX
from models.opensearch_models import *
from models.queue_models import DetailsRequestMsg, CatalogueRequestMsg
from parsers import Size_Parser
from publisher_collection import RabbitPublisherCollection, OpenSearchPublisherCollection
from scrapers.scraper import Scraper
from tag_mapper_client import *
from playwright.sync_api import Page
import re
import logging
import random
import time


class HMScraper(Scraper):
	directory = "../../DATA/stores/hm"
	store_code = "hm"
	products_per_page = 36
	product_collections = {
		'men': 'https://www2.hm.com/en_gb/men/shop-by-product/view-all.html',
		'women': 'https://www2.hm.com/en_gb/ladies/shop-by-product/view-all.html',
		'boys_young': 'https://www2.hm.com/en_gb/kids/boys/all.html',
		'boys_teen': 'https://www2.hm.com/en_gb/kids/boys-9-14y/view-all.html',
		'girls_young': 'https://www2.hm.com/en_gb/kids/girls/all.html',
		'girls_teen': 'https://www2.hm.com/en_gb/kids/girls-9-14y/view-all.html'
	}
	new_session = True

	def __init__(self, rabbit_publisher: RabbitPublisherCollection,
				 opensearch_publisher: OpenSearchPublisherCollection):
		self.rabbit_publisher = rabbit_publisher
		self.opensearch_publisher = opensearch_publisher
		self.logger = logging.getLogger(__name__)
		self.size_parser = Size_Parser(True)

	def get_categories(self):
		results = []

		for category_name, category_value in self.product_collections.items():
			category_msg = CatalogueRequestMsg(
				self.store_code,
				category_name,
				category_value,
				1
			)
			self.rabbit_publisher.get(CATALOGUE_TRIGGER).publish(category_msg)
			results.append(category_msg)

		return self.product_collections

	def get_catalogue(self, window: Page, category_msg: CatalogueRequestMsg) -> list[str]:
		product_urls = []
		for n, url in self.product_collections.items():
			product_urls += self.__refresh_category_products(window, url)

		print(f"Found {len(product_urls)} products on page {category_msg.page}.")

		# Next Page!
		if len(product_urls) == self.products_per_page:
			category_msg.page += 1
			self.rabbit_publisher.get(DETAILS_TRIGGER).publish(category_msg)

		return product_urls

	def __check_session(self, window: Page):
		cookies = '#onetrust-accept-btn-handler'
		if self.new_session:
			window.wait_for_selector(cookies)
			window.locator(cookies).click()
			self.new_session = False

	def __get_page_url(self, url: str, page_no: int) -> str:
		return f'{url}?sort=newProduct&page={page_no}'

	def __refresh_category_products(self, window: Page, url: str) -> list[str]:
		product_urls = []
		page_no = 1

		while True:
			results = list(self.__refresh_category_products_page(window, url, page_no))

			product_urls += results
			page_no += 1

			if len(results) < self.products_per_page:
				break

		return product_urls

	def __refresh_category_products_page(self, window: Page, url: str, page_no: int):
		product_selector = "#products-listing-section ul li .splide ul li:first-of-type a"
		page_no_selector = '#products-listing-section nav[role="navigation"] ul li a[aria-current="true"]'

		time.sleep(random.randint(2, 5))
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
				details_msg = DetailsRequestMsg(
					self.store_code,
					product_url,
					datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
				)
				self.rabbit_publisher.get(DETAILS_TRIGGER).publish(details_msg)
				self.opensearch_publisher.get(CATALOGUE_INDEX).publish(details_msg)
			logging.info(f"Successfully read page {url}")
		except:
			logging.exception(f"Failed to load page {url}")
			print(f"Failed to load page {url}")

		return products

	def get_product_details(self, window: Page, url: str) -> list[InventoryItem]:
		selectors = dict({
			'title': 'main h1',
			'brand': '#__next > main > div.rOGz > div > div > div:nth-child(2) > div > div > div.ddd474 > a',
			'price': '#__next > main > div.rOGz > div > div > div > div > div > div > span:has-text("£")',
			'sizes': '[data-testid="size-selector"] label',  ## id^=sizeButton-*
			'images': 'ul[data-testid="grid-gallery"] img',
			'materials_accordion': '#toggle-materialsAndSuppliersAccordion',
			'origin_button': '#section-materialsAndSuppliersAccordion > div > div > button',
			'origin_text': '#section-materialsAndSuppliersAccordion > div > div > div.db9e00 > div > div.ca411a > h3',
			'composition': '#section-materialsAndSuppliersAccordion div div div:first-of-type ul li',
			'fit': 'dt:has-text("Fit:") + dd',
			'length': 'dt:has-text("Length:") + dd',
			'style': 'dt:has-text("Style:") + dd',
			'selected_colour': '#__next > main > div.rOGz > div > div > div > div > div > div > section > div > div > a[aria-checked="true"]',
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

		self.__check_session(window)

		hm_product_id = url.split(".")[-2]
		id = f"hm-{hm_product_id}"

		title = window.locator(selectors["title"]).text_content().strip()
		store = brand = "H&M"

		all_prices = window.locator(selectors["price"]).all()
		price_txt = all_prices[0].text_content()
		price_txt= price_txt.strip().replace("£", "")
		price = float(price_txt)

		sizes = [self.size_parser.parse(sizes.text_content().lower()
				 .replace('few pieces left', '')
				 .replace('sold out', '')
				 .strip()
				)
				 for sizes
				 in window.locator(selectors["sizes"]).all()]

		image_urls = [image.get_attribute("content") for image in window.locator(selectors["cards"]).all()]

		origin = []
		window.evaluate("() => window.scrollBy(0, 4000)")
		window.wait_for_selector(selectors['materials_accordion'])
		window.locator(selectors['materials_accordion']).click()
		try:
			window.wait_for_selector(selectors['origin_button'], timeout=5000)
			if window.locator(selectors['origin_button']).count() > 0:
				window.locator(selectors['origin_button']).click()
				window.wait_for_selector(selectors['origin_text'])
				if window.locator(selectors["origin_text"]).count() > 0:
					for possible_origin in window.locator(selectors['origin_text']).all():
						origin.append(possible_origin.text_content())
		except Exception as ex:
			self.logger.exception("Failed to identify origin on {url}", url=url)
		if len(origin) == 0:
			origin = ["unknown"]

		fit = "regular fit"
		if window.locator(selectors["fit"]).count() > 0:
			fit = window.locator(selectors["fit"]).text_content().strip().lower()

		style = ""
		if window.locator(selectors["style"]).count() > 0:
			style = window.locator(selectors["style"]).all()[0].text_content().strip().lower()

		if window.locator(selectors["brand"]).count() > 0:
			brand = window.locator(selectors["brand"]).text_content().strip()

		raw_categories = [hm_product_id]
		raw_categories += [category.text_content().strip().lower() for category in
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
			layer_text = layer.text_content()
			if ':' in layer_text: # Boldly assuming there's only ever 1 title per <li>
				comp_title = layer_text.split(':')[0]
				layer_text = layer_text.split(':')[1]

			for material in layer_text.strip().split(','):
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
		else:
			audiences.append("unisex")

		products = [InventoryItem(
			id,
			"hm",
			hm_product_id,
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
			colour,
			tags,
			origin,
			creation_time=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
		)]

		for p in products:
			self.opensearch_publisher.get(DETAILS_INDEX).publish(p)

		return products
