import unittest

from parsers import Size_Parser


class SizeParserTests(unittest.TestCase):

	def setUp(self):
		self.parser = Size_Parser(False)

	def test_32r_size(self): self.__test_sizes(			"32r", 		1, 	Size_Parser.KIND_SIZE)
	def test_8uk_42eu_size(self): self.__test_sizes(	"8uk 42eu", 	2, 	Size_Parser.KIND_SHOE)
	def test_32c_size(self): self.__test_sizes(			"32c", 		1, 	Size_Parser.KIND_BRA)
	def test_32dd_size(self): self.__test_sizes(		"32dd", 		1, 	Size_Parser.KIND_BRA)
	def test_32ddd_size(self): self.__test_sizes(		"32ddd", 		1, 	Size_Parser.KIND_BRA)
	def test_32dddd_size(self): self.__test_sizes(		"32dddd", 		0, 	Size_Parser.KIND_BRA)
	def test_0_3_mths_size(self): self.__test_sizes(	"0-3 mths", 	4, 	Size_Parser.KIND_MONTHS)
	def test_0_3_months_size(self): self.__test_sizes(	"0-3 months", 	4, 	Size_Parser.KIND_MONTHS)
	def test_12_14_yrs_size(self): self.__test_sizes(	"12-14 yrs", 	3, 	Size_Parser.KIND_YEARS)
	def test_12_14_years_size(self): self.__test_sizes(	"12-14 years",	3, 	Size_Parser.KIND_YEARS)

	def __test_sizes(self, text: str, expected_count: int, expected_kind: str):
		output = self.parser.parse(text)
		assert len(output) is expected_count
		if(len(output) > 0):
			assert output[0].kind is expected_kind
