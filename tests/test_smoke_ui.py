import allure

from data.test_data import SMOKE_UI_FILTERS
from tasks.ui_tasks import Tasks

@allure.feature("Smoke Tests")
class TestSmokeUi:
    @allure.title("End-to-End Smoke Test: Registration, Login, and Movie Filtering")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Movie Discovery and Filtering")

    def test_smoke_ui(self, page, user_data):
        tasks = Tasks(page)
        tasks.complete_registration(user_data)
        tasks.complete_login(user_data)

        tasks.verify_search_and_filtering_currently_showing(**SMOKE_UI_FILTERS["currently_showing"])
        tasks.verify_search_and_filtering_upcoming_movies(**SMOKE_UI_FILTERS["upcoming_movies"])

        tasks.complete_logout()
