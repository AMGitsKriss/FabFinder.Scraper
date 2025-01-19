import base64
import gzip
import json
import logging
import re
import urllib
from datetime import datetime

import requests
from playwright.sync_api import Page

from helpers import Helpers
from models.opensearch_models import *
from models.queue_models import DetailsRequestMsg, CatalogueRequestMsg
from publisher_collection import RabbitPublisherCollection, OpenSearchPublisherCollection
from scrapers.scraper import Scraper
from config import *
from tag_mapper_client import TagMapper


class GeorgeScraper(Scraper):
	store_code = "george"
	products_per_page = 20
	product_collections = {
		'men': 'D2M1G10',
		'women': 'D1M1G20',
		'boys': 'D25M1G1',
		'girls': 'D25M2G1',
		'baby-boys': 'D5M9G1',
		'baby-girls': 'D5M10G1',
		'baby-unisex': 'D5M20G1C1'
	}
	new_session = True

	def __init__(self, rabbit_publisher: RabbitPublisherCollection,
				 opensearch_publisher: OpenSearchPublisherCollection):
		self.rabbit_publisher = rabbit_publisher
		self.opensearch_publisher = opensearch_publisher
		self.logger = logging.getLogger(__name__)

	@dataclass_json
	@dataclass
	class AsdaProduct:
		url: str
		current_price: int
		product_id: str
		name: str
		colour: str
		size: str
		product_type: str
		style: list[str]
		brand: str
		long_description: str
		primary_image: str
		secondary_images: list[str]
		misc_info: str
		fabric_composition: str
		gender: str
		bucket_colour: str
		type: str
		length: str
		genderCategory: list[str]
		master_id: str

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
		product_zips = self.__refresh_category_products_page(
			category_msg
		)

		# Next Page!
		if len(product_zips) == self.products_per_page:
			category_msg.page += 1
			self.rabbit_publisher.get(CATALOGUE_TRIGGER).publish(category_msg)

		return product_zips

	def __refresh_category_products_page(self, category_msg: CatalogueRequestMsg) -> list:
		parsed_products = self.__query_products(category_msg.page, category_msg.url)

		products = []

		for item in parsed_products:
			item_json = item.to_json()
			item_bytes = item_json.encode(encoding="utf-8")
			item_gzip = gzip.compress(item_bytes)
			item_b64 = base64.b64encode(item_gzip)

			details_msg = DetailsRequestMsg(
				self.store_code,
				item.product_id,
				str(item_b64, "utf-8"),
				datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
			)

			products.append(details_msg.url)
			self.rabbit_publisher.get(DETAILS_TRIGGER).publish(details_msg)
			self.opensearch_publisher.get(CATALOGUE_INDEX).publish(details_msg)

		self.logger.info("Read {scraper}. {category_name}: {category_url}. Page: {page}. Products: {product_count}",
						 scraper=self.store_code,
						 category_name=category_msg.name,
						 category_url=category_msg.url,
						 page=category_msg.page,
						 product_count=len(products))

		return products

	def __query_products(self, page_no: int, category: str) -> list:
		url = f"https://1kbyj8sz65-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.19.0)%3B%20Browser%20(lite)&x-algolia-api-key=dd461e21f405d468acf940750f588f80&x-algolia-application-id=1KBYJ8SZ65"
		try:
			headers = {
				"Accept-Encoding": "gzip, deflate, br, zstd",
				"Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8,ja;q=0.7",
				"Content-Type": "application/x-www-form-urlencoded",
				"Origin": "https://direct.asda.com",
				"Referer": "https://direct.asda.com/"
			}
			params = {
				"getRankingInfo": "true",
				"hitsPerPage": f"{self.products_per_page}",
				"page": f"{page_no}",
				"facets": "[\"*\"]",
				"facetFilters": "[]",
				"facetingAfterDistinct": "false",
				"explain": "*",
				"clickAnalytics": "true",
				"userToken": "",
				"filters": f"online:true AND (in_stock:true OR searchable_if_unavailable:true) AND searchable:true AND hasVG:false AND online_from<=1722679787647 AND (online_to=0 OR online_to >= 1722679787647) AND categories:{category}"
			}

			data = {
				"requests": [
					{
						"indexName": "asda_production_index",
						"params": urllib.parse.urlencode(params)
					}
				]
			}
			response = requests.post(url, json=data, headers=headers)
			if (response.ok):
				results = []
				for item in response.json()["results"][0]["hits"]:
					product_url = f"https://direct.asda.com/george/{item.get('product_id', None)},default,pd.html"
					product = self.AsdaProduct(
						current_price=item.get('current_price', None),
						product_id=item.get('product_id', None),
						url=product_url,
						name=item.get('name', None),
						colour=item.get('colour', None),
						size=item.get('size', None),
						product_type=item.get('product_type', None),
						style=item.get('style', None),
						brand=item.get('brand', None),
						long_description=item.get('long_description', None),
						primary_image=item.get('primary_image', None),
						secondary_images=item.get('secondary_images', None),
						misc_info=item.get('misc_info', None),
						fabric_composition=item.get('fabric_composition', None),
						gender=item.get('gender', None),
						bucket_colour=item.get('bucket_colour', None),
						type=item.get('type', None),
						length=item.get('length', None),
						genderCategory=item.get('genderCategory', None),
						master_id=item.get('master_id', None),
					)
					results.append(product)
				return results
			else:
				self.logger.error(
					msg="Asda returned with {ResponseCode}.",
					ResponseCode=response.status_code,
					Payload=data)

		except Exception as ex:
			self.logger.exception("Failed to parse Asda's response.", Url=url, Payload=data)
			return []

	def get_product_details(self, window: Page, item_string: str) -> InventoryItem:
		selectors = dict({
			'sizes': '#main-region > div.main-page-wrapper > div > div > div> div > div > div.buying-block > div.attributes-wrapper > div > div > div[data-id="button-attribute-selector-size"] > span',
			'colours': '#main-region > div.main-page-wrapper > div > div > div:nth-child(2) > div > div.buying-block-wrapper > div.buying-block > div.attributes-wrapper > div.product-colour-selector.image-swatches-selector.image-swatches-selector-grid-4 > div.colour-wrapper > div.colour.colour-swatch.selected.selectableUnavailable > img'
		})

		item_bytes = bytes(item_string, encoding="utf-8")
		item_gzip = base64.b64decode(item_bytes)
		item_json = gzip.decompress(item_gzip)
		item = self.AsdaProduct(**json.loads(item_json))
		store = "Asda"

		window.goto(item.url)
		self.__check_session(window)
		fit_sizes = Helpers.query_and_wait_for_selector(window, selectors["sizes"])
		if not fit_sizes:
			self.logger.error(
				msg='Product "{name}" could no longer be read.',
				name = item.name,
				url = item.url,
				store=store)
			return None

		all_size_combinations = []
		# fit_sizes = window.locator(selectors["sizes"])
		for size_label in fit_sizes.all():
			size_label_txt = size_label.inner_text().lower()
			parsed_size = self.__parse_size(size_label_txt, item)
			all_size_combinations.extend(parsed_size)

		colours = []
		raw_colours = window.locator(selectors["colours"])
		for colour in raw_colours.all():
			colours.append(colour.get_attribute("alt"))

		raw_info = [item.product_id]
		raw_info.append(item.name)
		raw_info.append(item.product_type)
		raw_info += item.style or []
		raw_info.append(item.long_description)
		raw_info.append(item.misc_info)
		raw_info.append(item.type)
		raw_info.append(item.length)
		raw_info += item.genderCategory
		raw_info += colours
		mapper_response = TagMapper.resolve_tags(raw_info)

		image_base_url = "https://asda.scene7.com/is/image/Asda/"
		image_urls = []
		if item.primary_image is not None:
			image_urls.append(image_base_url + item.primary_image)
		if item.secondary_images is not None:
			for img in item.secondary_images:
				image_urls.append(image_base_url + img)

		for i in range(len(item.genderCategory)):
			audience = item.genderCategory[i].lower()
			if audience == "womens":
				item.genderCategory[i] = "women"
			elif audience == "mens":
				item.genderCategory[i] = "men"
			else:
				item.genderCategory[i] = audience.lower()

		product = InventoryItem(
			f"george-{item.product_id}",
			"george",
			item.product_id,
			item.url,
			item.name,
			store,
			item.brand,
			item.current_price,
			self.__parse_composition(item.fabric_composition), # TODO - If none, get from page.
			mapper_response.pattern,
			mapper_response.categories.tags,
			image_urls,
			item.genderCategory,
			all_size_combinations,
			mapper_response.colours.tags,
			mapper_response.tags.tags,
			"unknown",
			creation_time=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
		)

		self.opensearch_publisher.get(DETAILS_INDEX).publish(product)

		return product

	def __parse_size(self, size_text: str, item: InventoryItem) -> list[Size]:
		results: list[Size] = list()
		child_sizes_regex = r"^\d{1,2}-\d{1,2}$"
		size_with_fit = r"^\d+[A-Za-z]$"
		letter_size_regex = r"^[a-zA-Z]$"
		number_size_regex = r"^\d{1,2}$"

		# Account for size ranges "10-12"
		if re.match(child_sizes_regex, size_text):
			size_type = "size"
			if "Yrs" in size_text: size_type = "years"
			elif "Mths" in size_text: size_type = "months"

			size_from_to = size_text.split("-")
			size_from = int(size_from_to[0])
			size_to = int(size_from_to[1])
			for size in range(size_from, size_to+1):
				results.append(Size(size, "regular", size_type))

		# Account for shoes "uk8 eu42"
		elif "uk" in size_text and "eu" in size_text:
			size_units = size_text.split(" ")
			for unit in size_units:
				number = re.sub("[^0-9]", "", unit)
				country = re.sub("[^a-zA-Z]", "", unit)
				results.append(Size(number, country, "shoes"))

		# Account for fits "32R"
		elif re.match(size_with_fit, size_text):
			number = re.sub("[^0-9]", "", size_text)
			fit = re.sub("[^a-zA-Z]", "", size_text)
			if number != "" and fit == "r":
				fit = "regular"
			elif number != "" and fit == "s":
				fit = "short"
			elif number != "" and fit == "t":
				fit = "tall"
			elif number != "" and fit == "l":
				fit = "long"
			else:
				self.logger.warning(f"There was no mapped fit for the string '{fit}' on {item.url}")
				fit = "regular"
			results.append(Size(number, fit, "size"))

		# Account for letters "M"
		elif re.match(letter_size_regex, size_text):
			results.append(Size(size_with_fit, "regular", "size"))

		# Account for numbers "10"
		elif re.match(number_size_regex, size_text):
			results.append(Size(size_with_fit, "regular", "size"))

		else:
			self.logger.warning(f"There was no mapped size for the size '{size_text}' on {item.url}")

		return results

	def __parse_composition(self, composition: str) -> list[CompositionDetail]:
		results = []
		composition = composition or ""

		material_indexes = re.findall(r'\d+% [A-Za-z]+', composition)
		material_dict = dict()
		for raw_material in material_indexes:
			split_comp = raw_material.split(" ")
			percent = split_comp[0].strip().replace("%", "")
			name = split_comp[1].strip().lower()
			material_dict[name] = float(percent) / 100

		layer = CompositionDetail(None, material_dict)
		results.append(layer)
		return results

	def __check_session(self, window: Page):
		cookies = '#onetrust-accept-btn-handler'
		if self.new_session:
			window.wait_for_selector(cookies)
			window.locator(cookies).click()
			self.new_session = False
