import logging
import requests

class TagMapper:

	def resolve_categories(title: str, store_categories: list[str]):
		url = f"https://localhost:44357/Category?text={title} {', '.join(store_categories)}"
		try:
			response = requests.get(url, verify=not __debug__)
			if (response.ok):
				return response.json()
			else:
				logging.error("Mapper Service responded with {responseCode}. {url}", responseCode=response.status_code, url=url)
		except:
			logging.error("Failed to read categories from the Mapper Service {url}", url=url)
		return []

	def resolve_colours(colours: list[str], new_colours: list[str]):
		url = f"https://localhost:44357/Colour?text={', '.join(new_colours)}"
		try:
			response = requests.get(url, verify=not __debug__)
			if (response.ok):
				colours += response.json()
			else:
				logging.error("Mapper Service responded with {responseCode}. {url}", responseCode=response.status_code, url=url)
		except Exception as ex:
			logging.exception("Failed to read colours from the Mapper Service {url}", url=url)

		return colours
