from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class CatalogueRequestMsg:
	store_code: str # HM / MS / ASOS

@dataclass_json
@dataclass
class DetailsRequestMsg:
	store_code: str
	url: dict
	read_time: str

