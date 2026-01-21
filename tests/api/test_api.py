from typing import Any

import allure
from data.test_data import TEST_USER
from tasks.api_tasks import ApiTasks
from data.data import get_api_filters, get_movie_projections

@allure.epic("Cinema Application")
@allure.feature("Api Smoke Suite")
class TestApi(ApiTasks):
    db: Any
    @allure.story("Full end-to-end movie discovery and authentication flow")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_api_flow(self):
        with allure.step("Step 1: Test data setup"):
            api_filters_data = get_api_filters(self.db)
            api_movie_projections_data = get_movie_projections(self.db)
        with allure.step("Step 2: Retrieve currently showing movies"):
            self.get_currently_showing_movies(**api_filters_data["current"])
        with allure.step("Step 2: Explore movie metadata (Cities, Venues, Genres)"):
            self.get_cities()
            self.get_venues_by_city(api_filters_data["filters"]["cityId"])
            self.get_genres()
        with allure.step("Step 4: Filter and verify upcoming movies"):
            self.get_upcoming_movies(**api_filters_data["filters"])
        with allure.step("Step 5: Verify specific movie projections by ID and Date"):
            self.get_movies_projections_by_movieId(**api_movie_projections_data)
        with allure.step("Step 6: Register and Verify New User via Gmail"):
            user_payload = TEST_USER.copy()
            email_used = self.register_and_verify_user(user_payload)
        with allure.step("Step 7: Authenticate with registered credentials"):
            self.login(email=email_used, password=TEST_USER["password"])
        with allure.step("Step 8: Validate user profile information"):
            self.get_user_profile(expected_email=email_used)
        with allure.step("Step 9: Logout and terminate session"):
            self.logout()