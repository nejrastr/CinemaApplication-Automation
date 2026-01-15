import allure
from data.test_data import API_FILTERS, MOVIE_PROJECTION_FILTERS, TEST_USER
from tasks.api_tasks import ApiTasks

@allure.epic("Cinema Application")
@allure.feature("Api Smoke Suite")
class TestApi(ApiTasks):
    @allure.story("Full end-to-end movie discovery and authentication flow")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_api_flow(self):
        with allure.step("Step 1: Retrieve currently showing movies"):
            self.get_currently_showing_movies(**API_FILTERS["filters"])
        with allure.step("Step 2: Explore movie metadata (Cities, Venues, Genres)"):
            self.get_cities()
            self.get_venues_by_city(API_FILTERS["filters"]["cityId"])
            self.get_genres()
        with allure.step("Step 3: Filter and verify upcoming movies"):
            self.get_upcoming_movies(**API_FILTERS["filters"])
        with allure.step("Step 4: Verify specific movie projections by ID and Date"):
            self.get_movies_projections_by_movieId(MOVIE_PROJECTION_FILTERS["movie_id"], MOVIE_PROJECTION_FILTERS["projection_date"])
        with allure.step("Step 5: Register and Verify New User via Gmail"):
            user_payload = TEST_USER.copy()
            email_used = self.register_and_verify_user(user_payload)
        with allure.step("Step 6: Authenticate with registered credentials"):
            self.login(email=email_used, password=TEST_USER["password"])
        with allure.step("Step 7: Validate user profile information"):
            self.get_user_profile(expected_email=email_used)
        with allure.step("Step 8: Logout and terminate session"):
            self.logout()