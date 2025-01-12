from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
# Step 01
class CategoryRequestMsg:
	store_code: str # HM / MS / ASOS

@dataclass_json
@dataclass
# Step 02
class CatalogueRequestMsg:
	store_code: str  # HM / MS / ASOS
	name: str
	url: str
	page: int

@dataclass_json
@dataclass
# Step 03
class DetailsRequestMsg:
	store_code: str # HM / MS / ASOS
	store_id: str
	url: str
	read_time: str

