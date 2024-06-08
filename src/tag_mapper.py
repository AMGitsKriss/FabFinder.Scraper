import logging
from dataclasses import dataclass, is_dataclass

import requests
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class TagResponse:
	isBlacklisted: bool
	tags: list[str]


@dataclass_json
@dataclass
class TagCollection:
	categories: TagResponse
	colours: TagResponse
	tags: TagResponse
	pattern: str
	isBlacklisted: bool

	def __post_init__(self):
		self.categories = TagResponse(**self.categories)
		self.colours = TagResponse(**self.colours)
		self.tags = TagResponse(**self.tags)


class TagMapper:
	def resolve_tags(store_text: list[str]) -> TagCollection:
		url = f"https://localhost:44357/ClothingMapper"
		try:
			response = requests.post(url, json=store_text, verify=not __debug__)
			if (response.ok):
				return TagCollection(**response.json())
			else:
				logging.error(
					msg="Mapper Service responded with {responseCode}. {url}",
					responseCode=response.status_code,
					url=url)
		except Exception as ex:
			logging.exception("Failed to read tags from the Mapper Service {url}", url=url)
		return TagCollection()
