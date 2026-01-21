import json
import pytest
from playwright.sync_api import sync_playwright
import os
import allure
from data.data import get_api_filters, get_movie_projections, get_upcoming_movies_filters, get_currently_showing_filters




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


@pytest.fixture(scope="session")
def user_data():
    data_folder = os.path.join(os.path.dirname(__file__), "./data")
    data_file = os.path.join(data_folder, "registrated_user.json")
    with open(data_file) as f:
        user_data = json.load(f)
    return user_data


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


@pytest.fixture
def api_filters_data(db_connection):
    return get_api_filters(db_connection)
@pytest.fixture
def api_movie_projections_data(db_connection):
    return get_movie_projections(db_connection)
@pytest.fixture
def ui_filters_data(db_connection):
    return {
        "currently_showing": get_currently_showing_filters(db_connection),
        "upcoming_movies": get_upcoming_movies_filters(db_connection),
    }