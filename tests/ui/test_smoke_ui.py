import os
import allure
import pytest
from tasks.ui_tasks import Tasks
from data.test_data import TEST_USER
from tasks.api_tasks import ApiTasks

@allure.feature("Smoke Tests")
@pytest.mark.ui
class TestSmokeUi(ApiTasks):
    def prepare_data(self):
        tasks = Tasks(self.page)
        ui_filter_test_data = tasks.setup_ui_test_data(self.db)
        api_filters_data, api_movie_projections_data, api_test_data = self.setup_test_data()
        return {
            "ui": ui_filter_test_data,
            "api": {
                "filters": api_filters_data,
                "projections": api_movie_projections_data,
                "details": api_test_data
            }
        }
    @pytest.fixture(scope="function")
    def smoke_data_setup(self):
        return self.prepare_data()

    @allure.title("End-to-End Smoke Test: Registration, Login, Movie Filtering, Ticket reservation")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_smoke_ui_ticket_reservation(self, smoke_data_setup):
        tasks = Tasks(self.page)
        ui_filter_test_data = smoke_data_setup["ui"]
        tasks.complete_registration(TEST_USER)
        tasks.complete_login(TEST_USER)
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

    allure.title("End-to-End Smoke Test: Registration, Login, Movie Filtering, Ticket purchase")

    @allure.severity(allure.severity_level.CRITICAL)
    def test_smoke_ui_ticket_payment(self, smoke_data_setup):
        tasks = Tasks(self.page)
        ui_filter_test_data = smoke_data_setup["ui"]
        api_data = smoke_data_setup["api"]

        with allure.step("Step 2: Retrieve currently showing movies"):
            self.get_currently_showing_movies(**api_data["filters"]["current"])

        with allure.step("Step 3: Explore movie metadata"):
            self.get_cities()
            self.get_venues_by_city(api_data["filters"]["filters"]["cityId"])
            self.get_genres()

        with allure.step("Step 4: Filter and verify upcoming movies"):
            self.get_upcoming_movies(**api_data["filters"]["filters"])

        with allure.step("Step 5: Verify specific movie projections"):
            self.get_movies_projections_by_movieId(
                api_data["projections"]["movie_id"],
                api_data["projections"]["projection_date"]
            )

        with allure.step("Step 6: Register and Verify New User via Gmail"):
            user_payload = TEST_USER.copy()
            email_used = self.register_and_verify_user(user_payload)
            base_url = os.getenv("BASE_URL").rstrip('/')

            self.page.goto(base_url)
            tasks.complete_login({"email": email_used, "password": user_payload["password"]})
            playwright_cookies = self.page.context.cookies()
            cookie_string = "; ".join([f"{c['name']}={c['value']}" for c in playwright_cookies])
            token = next((c['value'] for c in playwright_cookies if c['name'] == 'access_token'), None)

            if token:
                self.session.headers.update({
                    "Authorization": f"Bearer {token}",
                    "Cookie": cookie_string
                })
            else:
                pytest.fail("Access_token not found in browser cookies.")

        with allure.step("Step 8: Validate user profile information"):
            self.get_user_profile(expected_email=email_used)

        with allure.step("Step 9: Validate movie details information"):
            self.get_movie_details(api_data["details"])

        with allure.step("Step 10: UI Ticket Purchase Flow"):
            clean_day = ui_filter_test_data["currently_showing"]["day"].lstrip('0')
            movie_id = api_data["details"]["id"]
            target_url = f"{base_url}/movie-details/{movie_id}"

            self.page.goto(target_url)
            self.page.wait_for_load_state("domcontentloaded")

            tasks.verify_movie_ticket_payment(
                city_name=ui_filter_test_data["movie_details"]["city"],
                cinema_name=ui_filter_test_data["movie_details"]["cinema"],
                movie_title=ui_filter_test_data["movie_details"]["title"],
                projection_time=ui_filter_test_data["movie_details"]["projection_time"],
                day=clean_day,
                month=ui_filter_test_data["currently_showing"]["month"],
                weekday=ui_filter_test_data["currently_showing"]["weekday"]
            )
        tasks.complete_logout()