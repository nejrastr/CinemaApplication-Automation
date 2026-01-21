from typing import Any
import allure
import pytest
from playwright.sync_api import Page
from tasks.ui_tasks import Tasks
from data.data import get_currently_showing_filters, get_upcoming_movies_filters
from data.test_data import TEST_USER

@allure.feature("Smoke Tests")
@pytest.mark.ui
class TestSmokeUi:
    page: Page
    db: Any
    @allure.title("End-to-End Smoke Test: Registration, Login, and Movie Filtering")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Movie Discovery and Filtering")

    def test_smoke_ui(self):
        tasks = Tasks(self.page)
        tasks.complete_registration(TEST_USER)
        tasks.complete_login(TEST_USER)
        ui_filter_test_data ={
            "currently_showing": get_currently_showing_filters(self.db),
            "upcoming_movies": get_upcoming_movies_filters(self.db),
        }
        tasks.verify_search_and_filtering_currently_showing(**ui_filter_test_data["currently_showing"])
        tasks.verify_search_and_filtering_upcoming_movies(**ui_filter_test_data["upcoming_movies"])
        tasks.complete_logout()
