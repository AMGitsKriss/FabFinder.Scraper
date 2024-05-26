from dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class CompositionDetail:
	title: str
	composition: dict

@dataclass_json
@dataclass
class InventoryItem:
	id: str
	store_id: int
	url: str
	title: str
	store: str
	brand: str
	price: float
	composition: list[CompositionDetail]
	pattern: str
	categories: list[str]
	image_urls: list[str]
	audiences: list[str]
	sizes: list[str]
	fit: str
	colour: list[str]
	origin: str
	creation_time: str


@dataclass_json
@dataclass
class Category:
	singular: str
	plural: str


@dataclass_json
@dataclass
class DetailRequestMsg:
	store: str # HM / MS / ASOS
	url: str