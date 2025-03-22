import logging
import re

from models.opensearch_models import Size


class Size_Parser:
	KIND_SIZE = "size"
	KIND_MONTHS = "months"
	KIND_YEARS = "years"
	KIND_SHOE = "shoes"
	KIND_BRA = "bras"

	def __init__(self, enable_logging: bool):
		self.logger = logging.getLogger(__name__)
		self.enable_logging = enable_logging

	def parse(self, size_text: str) -> list[Size]:
		results: list[Size] = list()
		size_range_regex = r"^([0-9]*[.])?[0-9]+-([0-9]*[.])?[0-9]+"
		# size_range_regex = r"^\d{1,2}-\d{1,2}"
		bra_size_regex = r"^\d+[A-Ka-k]{1,3}$"
		size_with_fit = r"^\d+[L-Zl-z]$"
		letter_size_regex = r"^[smlxSMLX]*$"
		number_size_regex = r"^\d{1,2}$"

		# Account for size ranges "10-12"
		if re.match(size_range_regex, size_text):
			size_type = "size"
			if any(y in size_text.lower() for y in ["yrs", "years"]):
				size_type = self.KIND_YEARS
			elif any(m in size_text.lower() for m in ["mths", "months"]):
				size_type = self.KIND_MONTHS

			size_range = re.sub(r"[^0-9\-.]", "", size_text)
			size_from_to = size_range.split("-")
			size_from = int(float(size_from_to[0]))
			size_to = int(float(size_from_to[1]))
			for size in range(size_from, size_to + 1):
				results.append(Size(size, "regular", size_type))

		# Account for shoes "uk8 eu42"
		elif "uk" in size_text and "eu" in size_text:
			size_units = size_text.split(" ")
			for unit in size_units:
				number = re.sub("[^0-9]", "", unit)
				country = re.sub("[^a-zA-Z]", "", unit)
				results.append(Size(number, country, self.KIND_SHOE))

		# Account for bra sizes up to K
		# Do this before fits, because L is a fit-type
		elif re.match(bra_size_regex, size_text):
			number = re.sub("[^0-9]", "", size_text)
			cup = re.sub("[^a-zA-Z]", "", size_text)
			results.append(Size(number, cup, self.KIND_BRA))

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
				if self.enable_logging: self.logger.warning(f"There was no mapped fit for the string '{fit}'")
				fit = "regular"
			results.append(Size(number, fit, self.KIND_SIZE))

		# Account for letters "M"
		elif re.match(letter_size_regex, size_text):
			results.append(Size(size_text, "regular", self.KIND_SIZE))

		# Account for numbers "10"
		elif re.match(number_size_regex, size_text):
			results.append(Size(size_text, "regular", self.KIND_SIZE))

		elif size_text.lower() == "one size":
			results.append(Size("one size", "regular", self.KIND_SIZE))

		# TODO - Bras

		else:
			if self.enable_logging: self.logger.warning(f"There was no mapped size for the size '{size_text}'")

		return results