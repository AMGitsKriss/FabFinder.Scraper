import base64
import gzip
import json
import logging
import os
import re
import urllib
from datetime import datetime

import requests
from playwright.sync_api import Page

from data.file_manager import FileManager
from models.opensearch_models import *
from data.basepublisher import BasePublisher
from models.queue_models import DetailsRequestMsg
from scrapers.scraper import Scraper
from tag_mapper_client import TagMapper


class GeorgeScraper(Scraper):
	directory = "../../DATA/stores/george"
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

	def __init__(self, file_manager: FileManager, publisher: BasePublisher):
		self.publisher = publisher
		self.file_manager = file_manager

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

	def get_catalogue(self, window: Page) -> list[str]:
		product_zips = []

		for n, category in self.product_collections.items():
			product_zips += self.__refresh_category_products(category)
			product_zips = list(set(product_zips))
			# Update the big product list after each collection iteration. We don't want an all-or-nothing update
			self.file_manager.write_product_details(os.path.join(self.directory, "all_products.json"), product_zips)

		print(f"Found {len(product_zips)} products.")

		return product_zips

	def __refresh_category_products(self, category: str) -> list[str]:
		product_gzip = []
		page_no = 1

		while True:
			results = list(self.__refresh_category_products_page(page_no, category))
			product_gzip += results
			page_no += 1

			if len(results) < self.products_per_page:
				break

		return product_gzip

	def __refresh_category_products_page(self, page_no: int, category: str):
		parsed_products = self.__query_products(page_no, category)

		products = []

		for item in parsed_products:
			item_json = item.to_json()
			item_bytes = item_json.encode(encoding="utf-8")
			item_gzip = gzip.compress(item_bytes)
			item_b64 = base64.b64encode(item_gzip)
			products.append(str(item_b64, "utf-8"))

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
					subproduct = DetailsRequestMsg(
						"hm",
						product_url,
						datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
					)
					self.publisher.publish(subproduct)
				return results
			else:
				logging.error(
					msg="Asda returned with {ResponseCode}.",
					ResponseCode=response.status_code,
					Payload=data)

		except Exception as ex:
			logging.exception("Failed to parse Asda's response.", Url=url, Payload=data)
			return []

	def load_products(self):
		results = {}
		products = self.file_manager.read_products(os.path.join(self.directory, "all_products.json"))
		for p in products:
			results[p] = "george"
		return results

	def get_product_details(self, window: Page, item: str) -> list[InventoryItem]:
		selectors = dict({
			'sizes': '#main-region > div.main-page-wrapper > div > div > div> div > div > div.buying-block > div.attributes-wrapper > div > div > div[data-id="button-attribute-selector-size"] > span',
			'colours': '#main-region > div.main-page-wrapper > div > div > div:nth-child(2) > div > div.buying-block-wrapper > div.buying-block > div.attributes-wrapper > div.product-colour-selector.image-swatches-selector.image-swatches-selector-grid-4 > div.colour-wrapper > div.colour.colour-swatch.selected.selectableUnavailable > img'
		})

		item_bytes = bytes(item, encoding="utf-8")
		item_gzip = base64.b64decode(item_bytes)
		item_json = gzip.decompress(item_gzip)
		item = self.AsdaProduct(**json.loads(item_json))
		store = "Asda"

		window.goto(item.url)
		window.wait_for_selector(selectors["sizes"])

		self.__check_session(window)

		fit_sizes = window.locator(selectors["sizes"])
		size_dict = dict()
		for size_label in fit_sizes.all():
			raw = size_label.inner_text().lower()
			fit = "regular"

			# shoes
			if "uk" in raw and "eu" in raw:
				size_dict[fit] = raw
				continue

			# Limit splitting to "32R" style sizes
			if re.match(r'\d+[A-Za-z]$', raw):
				number = re.sub("[^0-9]", "", raw)
				fit = re.sub("[^a-zA-Z]", "", raw)
				if number != "" and fit == "r":
					fit = "regular"
				elif number != "" and fit == "s":
					fit = "short"
				elif number != "" and fit == "t":
					fit = "tall"
				elif number != "" and fit == "l":
					fit = "long"
				elif number != "" and fit != "":
					logging.warning(f"There was no fit mapped to the string '{fit}' on {item.url}")
					fit = "regular"
				else:
					logging.warning(f"There was no mapped fit for the string '{fit}' on {item.url}")
					fit = "regular"

				if fit not in size_dict:
					size_dict[fit] = []
				size_dict[fit].append(number)

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

		products = []
		for fit, sizes in size_dict.items():
			products.append(InventoryItem(
				f"george-{item.product_id}-{fit}",
				"george",
				item.product_id,
				item.url,
				item.name,
				store,
				item.brand,
				item.current_price,
				self.__parse_composition(item.fabric_composition),
				mapper_response.pattern,
				mapper_response.categories.tags,
				image_urls,
				item.genderCategory,
				sizes,
				fit,
				mapper_response.colours.tags,
				mapper_response.tags.tags,
				"unknown",
				creation_time=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
			))

		for p in products:
			self.file_manager.write_product_details(
				os.path.join(self.directory, f"products/{p.id}.json"), p.to_dict())

		return products

	def __parse_composition(self, composition: str) -> list[CompositionDetail]:
		results = []

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
