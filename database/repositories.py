class MovieRepository:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_user_verification_status(self, email):
        with self.db.cursor() as cursor:
            cursor.execute("SELECT is_verified FROM users WHERE email = %s", (email,))
            return cursor.fetchone()

    def get_city_count(self):
        with self.db.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM cities")
            return cursor.fetchone()['count']

    def get_genre_count(self):
        with self.db.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM genres")
            return cursor.fetchone()['count']

    def get_venue_count_by_city(self, city_id):
        with self.db.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM venues WHERE city_id = %s::uuid", (city_id,))
            return cursor.fetchone()['count']

    def get_venues_by_ids(self, venue_ids):
        with self.db.cursor() as cursor:
            cursor.execute("SELECT id, name FROM venues WHERE id = ANY(%s::uuid[])", (venue_ids,))
            return cursor.fetchall()

    def get_projection_times(self, movie_id, date):
        with self.db.cursor() as cursor:
            cursor.execute("""
                SELECT projection_time 
                FROM movie_projections 
                WHERE movie_id = %s AND projection_date = %s
                AND projection_time > CURRENT_TIME
            """, (movie_id, date))
            return {str(row['projection_time']) for row in cursor.fetchall()}

    def get_movie_details(self, movie_id):
        with self.db.cursor() as cursor:
            cursor.execute("""
            
            """)

    def get_filtered_movies(self, filters, is_upcoming=False):

        query = """
            SELECT DISTINCT m.id 
            FROM movies m 
            LEFT JOIN movie_projections mp ON m.id = mp.movie_id
            LEFT JOIN cinema_halls ch ON mp.cinema_hall_id = ch.id
            LEFT JOIN venues v ON ch.venue_id = v.id
            LEFT JOIN movie_genres mg ON m.id = mg.movie_id
            WHERE 1=1
        """

        if is_upcoming:
            query += " AND m.projection_start_date > CURRENT_DATE"

        params = []

        filter_map = {
            'title': ("AND m.title ILIKE %s", lambda v: f"%{v}%"),
            'projectionDate': ("AND mp.projection_date = %s", lambda v: v),
            'time': ("AND mp.projection_time = %s", lambda v: v),
            'cityId': ("AND v.city_id = %s", lambda v: v),
            'venueId': ("AND v.id = %s", lambda v: v),
            'genreId': ("AND mg.genre_id = %s", lambda v: v),
        }

        for key, value in filters.items():
            if key in filter_map and value:
                sql_part, val_func = filter_map[key]
                query += f" {sql_part}"
                params.append(val_func(value))

        if is_upcoming and filters.get('startDate') and filters.get('endDate'):
            query += " AND m.projection_start_date BETWEEN %s AND %s"
            params.extend([filters['startDate'], filters['endDate']])

        with self.db.cursor() as cursor:
            cursor.execute(query, tuple(params))
            return cursor.fetchall()

    def get_reservation_status(self, booking_id):

        query = """
        SELECT status
        FROM bookings
        WHERE id = %s::uuid
        """
        with self.db.cursor() as cursor:
            cursor.execute(query, (booking_id,))
            return cursor.fetchone()