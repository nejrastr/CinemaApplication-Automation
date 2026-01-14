import os
import allure
import json
import time
import pytest
from api_client import ApiClient
from database.repositories import MovieRepository
from utils.email_util import EmailHelper
from utils.logger import log_info


class ApiTasks(ApiClient):

    @pytest.fixture(autouse=True)
    def setup_api_tasks(self, db_connection):
        log_info("Initializing ApiTasks and DB Repository")
        self.init_client()
        self.repo = MovieRepository(db_connection)
        self.app_password = os.getenv("GMAIL_APP_PASSWORD")

    def _attach_details(self, name, data, attachment_type=allure.attachment_type.JSON):
        log_info(f"Attaching details: {name}")
        content = json.dumps(data, indent=2, default=str) if isinstance(data, (dict, list)) else str(data)
        allure.attach(content, name=name, attachment_type=attachment_type)

    @allure.step("Complete Registration & Verification Flow")
    def register_and_verify_user(self, user_payload):
        timestamp = int(time.time())
        unique_email = f"strsevicnejra+{timestamp}@gmail.com"
        user_payload['email'] = unique_email
        log_info(f"Starting registration for: {unique_email}")

        res_reg = self.post("auth/register", json=user_payload)
        self._attach_details("Registration Response", res_reg.json())
        assert res_reg.status_code == 200
        log_info("Registration POST request successful")

        log_info("Checking DB for unverified status...")
        user_in_db = self.repo.get_user_verification_status(unique_email)
        assert user_in_db['is_verified'] is False

        log_info("Sleeping 10s for email delivery...")
        time.sleep(10)

        log_info(f"Fetching verification code from Gmail for {unique_email}")
        activation_code = EmailHelper.get_verification_code(
            target_email=unique_email,
            app_password=self.app_password
        )
        log_info(f"Extracted activation code: {activation_code}")
        allure.attach(activation_code, name="Extracted Code", attachment_type=allure.attachment_type.TEXT)

        log_info("Sending verification request")
        res_verify = self.post("auth/verify", json={
            "email": unique_email,
            "verificationCode": activation_code
        })
        assert res_verify.status_code == 200

        time.sleep(2)
        log_info("Verifying 'is_verified' flag in Database")
        status = self.repo.get_user_verification_status(unique_email)
        assert status['is_verified'] is True

        log_info("User registration and verification flow completed.")
        return unique_email

    @allure.step("Login")
    def login(self, email, password):
        log_info(f"Logging in user: {email}")
        payload = {"email": email, "password": password}
        res = self.post("auth/login", json=payload)

        self._attach_details("Login Response", res.json())
        assert res.status_code == 200
        assert "access_token" in res.cookies or "access_token" in res.json()

        log_info("Login successful and token received.")
        return res

    @allure.step("Logout")
    def logout(self):
        log_info("Logging out current user")
        self.post("auth/logout")

    @allure.step("User profile")
    def get_user_profile(self, expected_email):
        log_info("Fetching user profile")
        res = self.get("auth/profile")
        self._attach_details("Profile Response", res.json())
        assert res.json().get("email") == expected_email
        return res

    @allure.step("Currently showing movies")
    def get_currently_showing_movies(self, **filters):
        log_info(f"Fetching currently showing movies with filters: {filters}")
        res = self.get("movies/currently-showing", params=filters)
        api_payload = res.json()
        self._attach_details("API Response", api_payload)

        api_total = api_payload.get('totalElements', len(api_payload.get('content', [])))

        log_info("Comparing API results with Database...")
        db_movies = self.repo.get_filtered_movies(filters, is_upcoming=False)

        assert len(db_movies) == api_total
        log_info(f"Success: Found {api_total} movies matching in both API and DB.")
        return api_payload

    @allure.step("Upcoming movies")
    def get_upcoming_movies(self, **filters):
        log_info(f"Fetching upcoming movies with filters: {filters}")
        res = self.get("movies/upcoming", params=filters)
        api_payload = res.json()
        self._attach_details("API Response", api_payload)

        api_total = api_payload.get('totalElements', len(api_payload.get('content', [])))

        log_info("Comparing API results with Database...")
        db_movies = self.repo.get_filtered_movies(filters, is_upcoming=True)

        assert api_total == len(db_movies)
        log_info(f"Success: Found {api_total} upcoming movies.")
        return api_payload

    @allure.step("Cities List")
    def get_cities(self):
        log_info("Fetching list of cities")
        res = self.get("cities")
        db_count = self.repo.get_city_count()
        assert db_count == len(res.json())
        log_info(f"Validated {db_count} cities against DB.")
        return res

    @allure.step("Genres List")
    def get_genres(self):
        log_info("Fetching list of genres")
        res = self.get("genres")
        db_count = self.repo.get_genre_count()
        assert db_count == len(res.json())
        log_info(f"Validated {db_count} genres against DB.")
        return res

    @allure.step("Venues by City")
    def get_venues_by_city(self, city_id):
        log_info(f"Fetching venues for city_id: {city_id}")
        res = self.get("venues/by-city", params={'cityId': city_id})
        data = res.json()
        assert res.status_code == 200

        db_count = self.repo.get_venue_count_by_city(city_id)
        assert db_count == len(data)
        log_info(f"Found {len(data)} venues in city.")
        return res

    @allure.step("Movie Projections")
    def get_movies_projections_by_movieId(self, movie_id, projection_date):
        log_info(f"Fetching projections for movie_id: {movie_id} on {projection_date}")
        res = self.get("movie-projections", params={'movieId': movie_id, 'projectionDate': projection_date})
        data = res.json()
        assert res.status_code == 200

        api_times = {p['projectionTime'] for p in data}
        log_info("Checking projection times against DB...")
        db_times = self.repo.get_projection_times(movie_id, projection_date)

        assert len(data) == len(db_times)
        assert api_times == db_times
        log_info(f"Projections match for movie_id {movie_id}.")
        return res