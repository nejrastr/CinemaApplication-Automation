from unittest.mock import DEFAULT

from playwright.sync_api import Page, Locator, expect

DEFAULT_TIMEOUT = 30000

class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def wait_until_ready(self, locator: Locator, timeout=DEFAULT_TIMEOUT ):
        locator.wait_for(state="attached", timeout=timeout)
        expect(locator).to_be_visible(timeout=timeout)
        expect(locator).to_be_enabled(timeout=timeout)
        return locator
    def click(self, locator: Locator, timeout=DEFAULT_TIMEOUT):
        self.wait_until_ready(locator)
        locator.click(timeout=timeout)

    ##TODO Adjust timeouts
    def fill(self, locator: Locator, value: str, timeout=DEFAULT_TIMEOUT):
        self.wait_until_ready(locator)
        locator.fill(value=value, timeout=timeout)

    def select_dropdown(self, element, value: str, timeout=DEFAULT_TIMEOUT):
        if isinstance(element, str):
            element = self.page.locator(element)

        element.wait_for(state="attached", timeout=timeout)
        element.wait_for(state="visible", timeout=timeout)

        option_locator = element.locator(f"option[value='{value}']")
        option_locator.wait_for(state="attached", timeout=timeout)

        element.select_option(value=value)


