import allure

filters = {
    "title": "Inception",
    "cityId": "8ee13b28-c27b-4b3b-84cb-0b6e5a7ee3f9",
    "venueId": "63f814e5-5fc0-4449-b2bd-81f58302c42c",
    "genreId": "34932aae-f555-4f60-9e03-27adc5a642f1",
    "startDate": "2026-01-28",
    "endDate": "2026-04-08",
    "page": 0,
    "size": 4
}

current = {
    "title": "Afterburn",
    "projectionDate": "2026-01-04",
    "time": "16:00",
    "page": 0,
    "size": 5
}


@allure.epic("Cinema Application")
@allure.feature("Api Smoke Suite")
class TestApi:
    @allure.story("Full end-to-end movie discovery and authentication flow")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_api_flow(self, user_data, api):
        with allure.step("Step 1: Retrieve currently showing movies"):

            api.get_currently_showing_movies(**current)
        with allure.step("Step 2: Explore movie metadata (Cities, Venues, Genres)"):
            api.get_cities()
            api.get_venues_by_city(filters['cityId'])
            api.get_genres()

        with allure.step("Step 3: Filter and verify upcoming movies"):
            api.get_upcoming_movies(**filters)

        with allure.step("Step 4: Verify specific movie projections by ID and Date"):
            movie_id = "72123b6a-185c-4961-8b81-54031025a9c3"
            projection_date = "2026-01-04"
            api.get_movies_projections_by_movieId(movie_id, projection_date)

        with allure.step("Step 5: Register a new user account"):
            email = user_data['email']
            api.register_user(user_data)

        with allure.step("Step 6: Handle email verification code"):
            api.send_verification_code(email_used=email)

        with allure.step("Step 7: Authenticate with registered credentials"):
            login_payload = {
                "email": email,
                "password": user_data['password']
            }
            api.login(login_payload)

        with allure.step("Step 8: Validate user profile information"):
            profile_response = api.get_user_profile()
            assert profile_response.status_code == 200, f"Expected 200, got {profile_response.status_code}"

            profile_data = profile_response.json()
            assert profile_data["email"] == email, "Profile email mismatch with registered email"

        with allure.step("Step 9: Logout and terminate session"):
            api.logout()