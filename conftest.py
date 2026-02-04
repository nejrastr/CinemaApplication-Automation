import pytest
from playwright.sync_api import sync_playwright
import allure


@pytest.fixture(scope="session", params=["chromium"])
def browser(request):
    browser_name = request.param
    with sync_playwright() as playwright:
        browser = getattr(playwright, browser_name).launch(headless=True)
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

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        page = item.funcargs.get("page")
        if page:
            allure.attach(
                page.screenshot(full_page=True),
                name="FAILURE_SCREENSHOT",
                attachment_type=allure.attachment_type.PNG
            )
            allure.attach(page.content(), name="HTML_Source", attachment_type=allure.attachment_type.HTML)

@pytest.fixture(scope="session")
def db_connection():
    from utils.db_connector import DBConnector
    conn = DBConnector().get_connection()
    yield conn
    conn.close()
@pytest.fixture(autouse=True)
def inject_fixtures(request, db_connection):
    if request.cls is not None:
        request.cls.db = db_connection
@pytest.fixture(autouse=True)
def inject_page(request, page):
    if request.node.get_closest_marker("ui"):
            request.cls.page = page