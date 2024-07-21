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
	product_collections = {
		'men_chinos': 'https://www.marksandspencer.com/l/men/mens-trousers/fs5/chinos',
		'men_jackets': 'https://www.marksandspencer.com/l/men/mens-coats-and-jackets',
		'men_coords': 'https://www.marksandspencer.com/l/men/mens-coords',
		'men_holiday': 'https://www.marksandspencer.com/l/men/mens-holiday-shop',
		'men_hoodies': 'https://www.marksandspencer.com/l/men/mens-hoodies-and-sweatshirts',
		'men_jeans': 'https://www.marksandspencer.com/l/men/mens-jeans',
		'men_joggers': 'https://www.marksandspencer.com/l/men/mens-joggers',
		'men_knitwear': 'https://www.marksandspencer.com/l/men/mens-knitwear',
		'men_loungewear': 'https://www.marksandspencer.com/l/men/loungewear',
		'men_occasion': 'https://www.marksandspencer.com/l/men/occasionwear',
		'men_polo': 'https://www.marksandspencer.com/l/men/mens-tops/mens-polo-shirts',
		'men_shirts': 'https://www.marksandspencer.com/l/men/mens-shirts',
		'men_shorts': 'https://www.marksandspencer.com/l/men/mens-shorts',
		'men_sports': 'https://www.marksandspencer.com/l/men/mens-sportswear',
		'men_swim': 'https://www.marksandspencer.com/l/men/mens-swimwear',
		'men_tops': 'https://www.marksandspencer.com/l/men/mens-tops',
		'men_trousers': 'https://www.marksandspencer.com/l/men/mens-trousers',
		'men_blazers': 'https://www.marksandspencer.com/l/men/mens-blazers',
		'men_formal_shirt': 'https://www.marksandspencer.com/l/men/mens-shirts/formal-shirts',
		'men_smart': 'https://www.marksandspencer.com/l/men/mens-smartwear',
		'men_formal_trousers': 'https://www.marksandspencer.com/l/men/mens-trousers/smart-trousers',
		'men_suits': 'https://www.marksandspencer.com/l/men/mens-suits',
		'men_ties': 'https://www.marksandspencer.com/l/men/mens-accessories/mens-ties',
		'men_tux': 'https://www.marksandspencer.com/l/men/mens-suits/mens-tuxedos',
		'men_waistcoats': 'https://www.marksandspencer.com/l/men/mens-waistcoats',
		'men_shoes': 'https://www.marksandspencer.com/l/men/mens-shoes',
		'men_accessories': 'https://www.marksandspencer.com/l/men/mens-accessories',
		'men_nightwear': 'https://www.marksandspencer.com/l/men/mens-nightwear',
		'school': 'https://www.marksandspencer.com/l/kids/school-uniform',
		'boys': 'https://www.marksandspencer.com/l/kids/boys',
		'girls': 'https://www.marksandspencer.com/l/kids/girls',
		'kids_characters': 'https://www.marksandspencer.com/l/kids/all-characters',
		'baby': 'https://www.marksandspencer.com/l/kids/baby',
		'women_accessories': 'https://www.marksandspencer.com/l/women/accessories',
		'women_shoes': 'https://www.marksandspencer.com/l/women/footwear',
		'women_plus': 'https://www.marksandspencer.com/l/women/plus-size-clothing',
		'women_maternity': 'https://www.marksandspencer.com/l/women/maternity',
		'women_petite': 'https://www.marksandspencer.com/l/women/petite',
		'women_tall': 'https://www.marksandspencer.com/l/women/tall',
		'women_nightwear': 'https://www.marksandspencer.com/l/lingerie/nightwear',
		'women_bras': 'https://www.marksandspencer.com/l/lingerie/bras',
		'women_pants': 'https://www.marksandspencer.com/l/lingerie/knickers',
		'women_rosie': 'https://www.marksandspencer.com/l/lingerie/rosie-exclusively-for-mands-lingerie',
		'women_socks': 'https://www.marksandspencer.com/l/lingerie/socks',
		'women_tights': 'https://www.marksandspencer.com/l/lingerie/tights',
		'women_sports': 'https://www.marksandspencer.com/l/women/sportswear',
		'women_cardigans': 'https://www.marksandspencer.com/l/women/knitwear/cardigans',
		'women_dresses': 'https://www.marksandspencer.com/l/women/dresses',
		'women_holiday': 'https://www.marksandspencer.com/l/women/holiday-shop',
		'women_hoodies': 'https://www.marksandspencer.com/l/women/knitwear/hoodies',
		'women_coats': 'https://www.marksandspencer.com/l/women/coats-and-jackets',
		'women_jeans': 'https://www.marksandspencer.com/l/women/jeans',
		'women_joggers': 'https://www.marksandspencer.com/l/women/trousers/joggers',
		'women_jumpers': 'https://www.marksandspencer.com/l/women/knitwear/jumpers',
		'women_leggings': 'https://www.marksandspencer.com/l/women/trousers/leggings',
		'women_loungewear': 'https://www.marksandspencer.com/l/women/loungewear',
		'women_blouses': 'https://www.marksandspencer.com/l/women/tops/shirts-and-blouses',
		'women_shorts': 'https://www.marksandspencer.com/l/women/shorts',
		'women_skirts': 'https://www.marksandspencer.com/l/women/skirts',
		'women_sweatshirts': 'https://www.marksandspencer.com/l/women/knitwear/sweatshirts',
		'women_swim': 'https://www.marksandspencer.com/l/women/swimwear',
		'women_tops': 'https://www.marksandspencer.com/l/women/tops',
		'women_trousers': 'https://www.marksandspencer.com/l/women/trousers',
		'women_work': 'https://www.marksandspencer.com/l/women/workwear'
	}
	new_session = True

	def __init__(self, file_manager: FileManager):
		self.file_manager = file_manager

	def get_catalogue(self, window: Page) -> list[str]:
		product_urls = []

		for n, url in self.product_collections.items():
			product_urls += self.__refresh_category_products(window, url)
			product_urls = list(set(product_urls))
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
		product_selector = "div.grid_container__flAnn a[class*=product-card]"
		# #\36 0502727 > div > a
		# #\36 0555869 > div > a
		# div.grid_container__flAnn div > div > a

		window.goto(url)  # go to url
		window.wait_for_selector(product_grid)  # wait for content to load

		self.__check_session(window)

		products = []

		product_boxes = window.locator(product_selector)
		for box in product_boxes.all():
			product_url = box.get_attribute("href")
			products.append(self.base_url + product_url)
		products = set(products)

		return products

	def __check_session(self, window: Page):
		cookies = '#onetrust-reject-all-handler'
		if self.new_session:
			window.wait_for_selector(cookies)
			window.locator(cookies).click()
			self.new_session = False

	def get_product_details(self, window: Page, url: str) -> list[InventoryItem]:
		selectors = dict({
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

		self.__check_session(window)

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

		for layer in raw_composition.split(' , '):  # comma with extra spacing seems to indicate a layer seperator
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
