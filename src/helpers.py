from playwright.sync_api import TimeoutError, Page


class Helpers:
	def query_and_wait_for_selector(page: Page, selector: str, timeout=10000):
		try:
			element = page.wait_for_selector(selector, timeout=timeout)
			if element:
				print("Element exists and is visible!")
			return element
		except TimeoutError:
			print("Element does not exist or is not visible within the given timeout.")
			return None