from typing import Any
import allure
import pytest
from playwright.sync_api import Page
from tasks.ui_tasks import Tasks
from data.data import get_currently_showing_filters, get_upcoming_movies_filters, get_movie_projections, get_movie_details_data
from data.test_data import TEST_USER

@allure.feature("Smoke Tests")
@pytest.mark.ui
class TestSmokeUi:
    page: Page
    db: Any
    @allure.title("End-to-End Smoke Test: Registration, Login, Movie Filtering, Ticket reservation")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_smoke_ui_ticket_reservation(self):
        tasks = Tasks(self.page)
        tasks.complete_registration(TEST_USER)
        tasks.complete_login(TEST_USER)
        ui_filter_test_data = tasks.setup_ui_test_data(self.db)
        tasks.verify_search_and_filtering_currently_showing(**ui_filter_test_data["currently_showing"])
        tasks.verify_movie_details(
            movie_data=ui_filter_test_data["movie_details"],
            current_showing=ui_filter_test_data["currently_showing"]
        )
        tasks.verify_movie_ticket_reservation(ui_filter_test_data["movie_details"]["city"],
                                              ui_filter_test_data["movie_details"]["cinema"],
                                              ui_filter_test_data["movie_details"]["title"],
                                              ui_filter_test_data["movie_details"]["projection_time"],
                                              ui_filter_test_data["currently_showing"]["day"],
                                              ui_filter_test_data["currently_showing"]["month"],
                                              ui_filter_test_data["currently_showing"]["weekday"])
        tasks.verify_search_and_filtering_upcoming_movies(**ui_filter_test_data["upcoming_movies"])
        tasks.complete_logout()

    @allure.title("End-to-End Smoke Test: Registration, Login, Movie Filtering, Ticket purchase")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_smoke_ui_ticket_payment(self):
        tasks = Tasks(self.page)
        tasks.complete_registration(TEST_USER)
        tasks.complete_login(TEST_USER)
        ui_filter_test_data = {
            "currently_showing": get_currently_showing_filters(self.db),
            "upcoming_movies": get_upcoming_movies_filters(self.db),
            "movie_projections": get_movie_projections(self.db),
            "movie_details": get_movie_details_data(self.db),
        }
        tasks.verify_search_and_filtering_currently_showing(**ui_filter_test_data["currently_showing"])
        tasks.verify_movie_details(**ui_filter_test_data["movie_details"])
        tasks.verify_movie_ticket_payment(ui_filter_test_data["movie_details"]["city"],
                                              ui_filter_test_data["movie_details"]["cinema"],
                                              ui_filter_test_data["movie_details"]["title"],
                                              ui_filter_test_data["movie_details"]["projection_time"])
        tasks.verify_search_and_filtering_upcoming_movies(**ui_filter_test_data["upcoming_movies"])
        tasks.complete_logout()
