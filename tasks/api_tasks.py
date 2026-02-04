import os
import allure
import json
import time
import pytest
from api_client import ApiClient
from conftest import db_connection
from database.repositories import MovieRepository
from utils.email_util import EmailHelper
from utils.logger import log_info
from data.data import get_api_filters, get_movie_projections, get_movie_details_data

class ApiTasks(ApiClient):
    def setup_method(self):
        log_info("Initializing ApiTasks")
        self.session = None
        self.init_client()
        self.app_password = os.getenv("GMAIL_APP_PASSWORD")

    @pytest.fixture(autouse=True)
    def inject_db(self, db_connection):
        self.repo = MovieRepository(db_connection)

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
        data = res.json()

        self._attach_details("Login Response", res.json())
        assert res.status_code == 200
        assert "access_token" in res.cookies or "access_token" in res.json()
        token = res.cookies.get("access_token")
        if token:
            self.session.headers = {
                **self.session.headers,
                "Authorization": f"Bearer {token}"
            }

            log_info("Login successful and Bearer token applied to session.")
        else:
            log_info("Login successful, but no token found in JSON body.")

        return res

    @allure.step("Logout")
    def logout(self):
        log_info("Logging out current user")
        self.post("auth/logout")
        self.session.headers.pop("Authorization", None)
        self.session.cookies.clear()

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

        assert api_times == db_times
        log_info(f"Projections match for movie_id {movie_id}.")
        return res

    @allure.step("Movie Details")
    def get_movie_details(self, api_test_data):
        log_info(f"Fetching movie details ")
        movie_id = api_test_data["id"]
        res = self.get(f"movies/{movie_id}")
        data = res.json()
        assert res.status_code == 200
        self.verify_movie_data(data, api_test_data)


    @allure.step("Get booking session")
    def get_booking_session(self, projection_id):
        log_info(f"Fetching booking session for projection_id: {projection_id}")
        res = self.post("booking", params={'projectionId': projection_id})
        data = res.json()
        assert res.status_code == 200
        assert data["success"]
        return res

    def verify_movie_data(self, api_data, db_data):
        log_info("Normalizing API data and comparing with DB records...")
        api_writers = [f"{w['firstName']} {w['lastName']}" for w in api_data.get('writers', [])]
        api_cast = []
        for actor in api_data.get('cast', []):
            api_cast.append({
                "name": f"{actor['firstName']} {actor['lastName']}",
                "character": actor['characterFullName']
            })
        assert api_data['id'] == db_data['id']
        assert api_data['title'] == db_data['title']
        assert api_data['language'] == db_data['language']
        assert api_data['pgRating'] == db_data['pgRating']
        assert api_data['durationInMinutes'] == db_data['duration']
        assert api_data['synopsis'] == db_data['synopsis']
        assert api_data['directorFullName'] == db_data['director']
        assert api_data['projectionStartDate'] == db_data['projectionStartDate']
        assert api_data['projectionEndDate'] == db_data['projectionEndDate']

        assert sorted(api_writers) == sorted(db_data['writers']), \
            f"Writers mismatch! API: {api_writers} vs DB: {db_data['writers']}"

        log_info("Data verification successful: API and DB match perfectly.")

    def get_movie_ticket_reservation(self, api_test_data):
        booking_response = self.get_booking_session(api_test_data["movie_projection_id"])
        booking_data = booking_response.json()
        booking_id = booking_data.get("bookingId")
        status = self.repo.get_reservation_status(booking_id)
        assert status['status'] == "locked"
        log_info("Reservation status: locked")
        print(f"Current Auth Header: {self.session.headers.get('Authorization')}")
        reserved_ticket_response = self.post(f"booking/reserve/{booking_id}")
        assert reserved_ticket_response.status_code == 200
        time.sleep(2)
        status_2 = self.repo.get_reservation_status(booking_id)
        assert status_2['status'] == "reserved"
        log_info("Reservation status: reserved")

    @allure.step("Buy movie tickets with Stripe")
    def buy_movie_tickets(self, api_test_data):
        booking_response = self.get_booking_session(api_test_data["movie_projection_id"])
        booking_data = booking_response.json()
        booking_id = booking_data.get("bookingId")
        status = self.repo.get_reservation_status(booking_id)
        assert status['status'] == "locked"
        log_info(f"Initiating payment for booking: {booking_id}")
        self.post(f"booking/pay/{booking_id}")
        time.sleep(3)
        final_status = self.repo.get_reservation_status(booking_id)
        log_info(f"Final DB Status: {final_status['status']}")
        assert final_status['status'] == "paid", f"Expected 'paid' but got {final_status['status']}"

    def setup_test_data(self):
        try:
            db_conn = self.repo.db
            filters = get_api_filters(db_conn)
            projections = get_movie_projections(db_conn)
            details = get_movie_details_data(db_conn)
            log_info("setup test data")
            return filters, projections, details
        except Exception as e:
            pytest.fail(f"Critical Setup Failure: Could not retrieve test data from DB. Error: {e}")
