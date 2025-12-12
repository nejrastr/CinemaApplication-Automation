import pytest
from playwright.sync_api import sync_playwright




@pytest.fixture(scope="session", params=["chromium"])
def browser(request):
    browser_name = request.param
    with sync_playwright() as playwright:
        browser = getattr(playwright, browser_name).launch(headless=False)
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def context(browser):
    context = browser.new_context()
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context):
    page = context.new_page()
    yield page
    page.close()

