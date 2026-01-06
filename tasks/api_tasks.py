import os
import allure
import json
from bs4 import BeautifulSoup
from mailslurp_client import Configuration, ApiClient as MSClient, WaitForControllerApi
from api_client import ApiClient

TEST_INBOX_ID = "df1f4339-c0dc-46dc-98b6-b70679ee3a0c"
TEST_EMAIL_ADDRESS = "df1f4339-c0dc-46dc-98b6-b70679ee3a0c@mailslurp.biz"


class ApiTasks(ApiClient):
    def __init__(self, db_connection):
        super().__init__()
        self.db = db_connection

    def _attach_details(self, name, data, attachment_type=allure.attachment_type.JSON):
        content = json.dumps(data, indent=2) if isinstance(data, (dict, list)) else str(data)
        allure.attach(content, name=name, attachment_type=attachment_type)

    @allure.step("Registration")
    def register_user(self, user_payload):
        target_email = user_payload.get('email')
        res = self.post("auth/register", json=user_payload)
        self._attach_details("API Response - Register", res.json())

        assert res.status_code == 200
        with self.db.cursor() as cursor:
            cursor.execute("SELECT is_verified FROM users WHERE email = %s", (target_email,))
            user_in_db = cursor.fetchone()
            self._attach_details("DB Verification Check", user_in_db)
            assert user_in_db['is_verified'] is False
        return res

    @allure.step("Verification")
    def get_verification_code(self):
        configuration = Configuration()
        api_key = os.environ.get("MAILSLURP_API_KEY")
        configuration.api_key['x-api-key'] = api_key
        ms_client = MSClient(configuration)
        wait_controller = WaitForControllerApi(ms_client)

        email = wait_controller.wait_for_latest_email(inbox_id=TEST_INBOX_ID, timeout=60000)
        soup = BeautifulSoup(email.body, 'html.parser')

        code_label = soup.find('p', string=lambda text: text and 'Your Activation Code' in text)
        if not code_label:
            allure.attach(email.body, name="Email Body Error", attachment_type=allure.attachment_type.HTML)
            raise ValueError("'Your Activation Code' label not found in email")

        code_p = code_label.find_next_sibling('p')
        if not code_p:
            raise ValueError("Activation code <p> not found after label")

        activation_code = code_p.get_text(strip=True)
        allure.attach(activation_code, name="Extracted Code", attachment_type=allure.attachment_type.TEXT)
        return activation_code

    @allure.step("Verification code")
    def send_verification_code(self, email_used):
        activation_code = self.get_verification_code()

        res = self.post("auth/verify", json={
            "email": email_used,
            "verificationCode": activation_code
        })
        self._attach_details("API Response - Verify", res.json())

        assert res.status_code == 200
        with self.db.cursor() as cursor:
            cursor.execute("SELECT is_verified FROM users WHERE email = %s", (email_used,))
            status = cursor.fetchone()
            self._attach_details("DB Final Verification Status", status)
            assert status['is_verified'] is True

    @allure.step("Login")
    def login(self, user_payload):
        res = self.post("auth/login", json=user_payload)
        self._attach_details("API Response - Login", res.json())

        assert res.status_code == 200
        cookies = res.cookies
        assert "access_token" in cookies
        assert "refresh_token" in cookies

    @allure.step("Logout")
    def logout(self):
        res = self.post("auth/logout")
        allure.attach("Logout action triggered", name="Logout Info", attachment_type=allure.attachment_type.TEXT)

    @allure.step("User profile")
    def get_user_profile(self):
        user_profile_response = self.get("auth/profile")
        self._attach_details("API Response - Profile", user_profile_response.json())
        assert user_profile_response.json().get("email") == TEST_EMAIL_ADDRESS
        return user_profile_response

    @allure.step("Currently showing movies")
    def get_currently_showing_movies(self, **filters):
        res = self.get("movies/currently-showing", params=filters)
        self._attach_details("API Response - Currently Showing", res.json())

        api_payload = res.json()
        assert res.status_code == 200
        api_movies = api_payload.get('content', api_payload)
        api_total = api_payload.get('totalElements', len(api_movies))

        query = """
        SELECT DISTINCT m.id FROM movies m 
        JOIN movie_projections mp ON m.id = mp.movie_id
        WHERE 1=1
        """
        query_params = []
        if filters.get('title'):
            query += " AND m.title ILIKE %s"
            query_params.append(f"%{filters.get('title')}%")
        if filters.get('projectionDate'):
            query += " AND mp.projection_date = %s"
            query_params.append(filters.get('projectionDate'))
        if filters.get('time'):
            query += " AND mp.projection_time = %s"
            query_params.append(filters.get('time'))

        with self.db.cursor() as cursor:
            cursor.execute(query, tuple(query_params))
            db_movies = cursor.fetchall()
            db_total = len(db_movies)
            self._attach_details("DB Check Results", {"db_count": db_total, "api_count": api_total})

        assert db_total == api_total
        return api_payload

    @allure.step("Upcoming movies")
    def get_upcoming_movies(self, **filters):
        res = self.get("movies/upcoming", params=filters)
        self._attach_details("API Response - Upcoming", res.json())
        assert res.status_code == 200
        api_payload = res.json()

        api_movies = api_payload.get('content', api_payload)
        api_total = api_payload.get('totalElements', len(api_movies))

        query = """
        SELECT DISTINCT m.id FROM movies m 
        LEFT JOIN movie_projections mp ON m.id = mp.movie_id
        LEFT JOIN cinema_halls ch ON mp.cinema_hall_id = ch.id
        LEFT JOIN venues v ON ch.venue_id = v.id
        LEFT JOIN movie_genres mg ON m.id = mg.movie_id
        WHERE m.projection_start_date > CURRENT_DATE
        """
        query_params = []
        if filters.get('title'):
            query += " AND m.title ILIKE %s"
            query_params.append(f"%{filters['title']}%")
        if filters.get('cityId'):
            query += " AND v.city_id = %s"
            query_params.append(filters.get('cityId'))
        if filters.get('venueId'):
            query += " AND v.id = %s"
            query_params.append(filters.get('venueId'))
        if filters.get('genreId'):
            query += " AND mg.genre_id = %s"
            query_params.append(filters.get('genreId'))
        if filters.get('startDate') and filters.get('endDate'):
            query += " AND m.projection_start_date BETWEEN %s AND %s"
            query_params.extend([filters['startDate'], filters['endDate']])

        with self.db.cursor() as cursor:
            cursor.execute(query, tuple(query_params))
            db_movies = cursor.fetchall()
            db_total = len(db_movies)
            self._attach_details("DB Comparison", {"db_total": db_total, "api_total": api_total})

        assert api_total == db_total
        return api_payload

    @allure.step("Venues")
    def get_venues(self, page=0, size=10):
        res = self.get("venues", params={'page': page, 'size': size})
        self._attach_details("API Response - Venues", res.json())
        assert res.status_code == 200

        api_data = res.json()
        api_venues = api_data.get('content', [])
        api_ids = [v['id'] for v in api_venues]

        with self.db.cursor() as cursor:
            cursor.execute("SELECT id, name FROM venues WHERE id = ANY(%s::uuid[])", (api_ids,))
            db_venues = cursor.fetchall()
            db_venues_set = {(v['id'], v['name']) for v in db_venues}

        for venue in api_venues:
            assert (venue['id'], venue['name']) in db_venues_set

        return api_data

    @allure.step("Cities")
    def get_cities(self):
        res = self.get("cities")
        self._attach_details("API Response - Cities", res.json())
        assert res.status_code == 200

        with self.db.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM cities")
            cities_count = cursor.fetchone()['count']

        assert cities_count == len(res.json())
        return res

    @allure.step("Genres")
    def get_genres(self):
        res = self.get("genres")
        self._attach_details("API Response - Genres", res.json())
        assert res.status_code == 200

        with self.db.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as genre_count FROM genres")
            genres_count = cursor.fetchone()['genre_count']

        assert genres_count == len(res.json())
        return res

    @allure.step("Get cinema by citId")
    def get_venues_by_city(self, cityId):
        res = self.get("venues/by-city", params={'cityId': cityId})
        self._attach_details("API Response - Venues by City", res.json())
        assert res.status_code == 200

        data = res.json()
        with self.db.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM venues WHERE city_id = %s::uuid", (cityId,))
            venues_count = cursor.fetchone()['count']

        assert venues_count == len(data)
        for venue in data:
            assert venue['city']['id'] == cityId

        return res

    @allure.step("Get movie projections by date and time")
    def get_movies_projections_by_movieId(self, movieId, projectionDate):
        res = self.get("movie-projections", params={'movieId': movieId, 'projectionDate': projectionDate})
        self._attach_details("API Response - Projections", res.json())
        assert res.status_code == 200

        data = res.json()
        api_times = {p['projectionTime'] for p in data}

        with self.db.cursor() as cursor:
            cursor.execute("""
                SELECT projection_time 
                FROM movie_projections 
                WHERE movie_id = %s AND projection_date = %s
            """, (movieId, projectionDate))
            db_times = {str(row['projection_time']) for row in cursor.fetchall()}

        self._attach_details("Time Comparison", {"api": list(api_times), "db": list(db_times)})
        assert len(data) == len(db_times)
        assert api_times == db_times

        return res