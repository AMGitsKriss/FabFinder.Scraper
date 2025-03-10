import logging

from playwright.sync_api import TimeoutError, Page


class Helpers:
	def query_and_wait_for_selector(page: Page, selector: str, timeout=10000):
		try:
			page.wait_for_selector(selector, timeout=timeout)
			element = page.query_selector_all(selector)
			return element
		except TimeoutError:
			logging.exception("Element does not exist or is not visible within the given timeout.")
			return None