from typing import Any
import allure
from data.test_data import TEST_USER
from tasks.api_tasks import ApiTasks


@allure.epic("Cinema Application")
@allure.feature("Api Smoke Suite")
class TestApi(ApiTasks):
    db: Any
    @allure.story("Full end-to-end movie discovery, authentication and reservation flow")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_movie_reservation_api_flow(self):
        with allure.step("Step 1: Test data setup"):
            api_filters_data, api_movie_projections_data, api_test_data = self.setup_test_data()
        with allure.step("Step 2: Retrieve currently showing movies"):
            self.get_currently_showing_movies(**api_filters_data["current"])
        with allure.step("Step 2: Explore movie metadata (Cities, Venues, Genres)"):
            self.get_cities()
            self.get_venues_by_city(api_filters_data["filters"]["cityId"])
            self.get_genres()
        with allure.step("Step 4: Filter and verify upcoming movies"):
            self.get_upcoming_movies(**api_filters_data["filters"])
        with allure.step("Step 5: Verify specific movie projections by ID and Date"):
            self.get_movies_projections_by_movieId(api_movie_projections_data["movie_id"], api_movie_projections_data["projection_date"])
        with allure.step("Step 6: Register and Verify New User via Gmail"):
            user_payload = TEST_USER.copy()
            email_used = self.register_and_verify_user(user_payload)
        with allure.step("Step 7: Authenticate with registered credentials"):
            self.login(email=email_used, password=TEST_USER["password"])
        with allure.step("Step 8: Validate user profile information"):
            self.get_user_profile(expected_email=email_used)
        with allure.step("Step 9: Validate movie details information"):
            self.get_movie_details(api_test_data)
        with allure.step("Step 10: Reserve movie ticket"):
            self.get_movie_ticket_reservation(api_test_data)
        with allure.step("Step 11: Logout and terminate session"):
            self.logout()

    @allure.story("Full end-to-end movie discovery, authentication and ticket purchase flow")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_movie_payment_api_flow(self):
        with allure.step("Step 1: Test data setup"):
            api_filters_data, api_movie_projections_data, api_test_data = self.setup_test_data()
        with allure.step("Step 2: Retrieve currently showing movies"):
            self.get_currently_showing_movies(**api_filters_data["current"])
        with allure.step("Step 2: Explore movie metadata (Cities, Venues, Genres)"):
            self.get_cities()
            self.get_venues_by_city(api_filters_data["filters"]["cityId"])
            self.get_genres()
        with allure.step("Step 4: Filter and verify upcoming movies"):
            self.get_upcoming_movies(**api_filters_data["filters"])
        with allure.step("Step 5: Verify specific movie projections by ID and Date"):
            self.get_movies_projections_by_movieId(api_movie_projections_data["movie_id"],
                                                   api_movie_projections_data["projection_date"])
        with allure.step("Step 6: Register and Verify New User via Gmail"):
            user_payload = TEST_USER.copy()
            email_used = self.register_and_verify_user(user_payload)
        with allure.step("Step 7: Authenticate with registered credentials"):
            self.login(email=email_used, password=TEST_USER["password"])
        with allure.step("Step 8: Validate user profile information"):
            self.get_user_profile(expected_email=email_used)
        with allure.step("Step 9: Validate movie details information"):
            self.get_movie_details(api_test_data)
        with allure.step("Step 10: Buy movie ticket"):
            self.buy_movie_tickets(api_test_data)
        with allure.step("Step 11: Logout and terminate session"):
            self.logout()



