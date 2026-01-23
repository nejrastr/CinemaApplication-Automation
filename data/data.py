from datetime import date

from data.db_client import DBClient
def get_currently_showing_filters(db_connection):
    client = DBClient(db_connection)

    row = client.fetch_one("""
    SELECT
    c.name AS city,
    v.name AS cinema,
    g.name AS genre,
    m.title AS title,
    mp.projection_time AS projection_time,
    mp.projection_date AS show_date
    FROM movies m
    JOIN movie_projections mp ON m.id = mp.movie_id
    JOIN cinema_halls ch ON mp.cinema_hall_id = ch.id
    JOIN venues v ON ch.venue_id = v.id
    JOIN movie_genres mg ON m.id = mg.movie_id
    JOIN genres g ON mg.genre_id = g.id
    JOIN cities c ON v.city_id = c.id
    WHERE mp.projection_date >= CURRENT_DATE
    ORDER BY mp.projection_date ASC, mp.projection_time ASC
    LIMIT 1;

    """)

    if not row:
        raise RuntimeError("No currently showing movies found — smoke test blocked")
    projection_date = row["show_date"]

    today = date.today()

    return {
        "city": row["city"],
        "cinema": row["cinema"],
        "genre": row["genre"],
        "search_term": row["title"],
        "projection": row["projection_time"].strftime("%H:%M"),
        "month": projection_date.strftime("%b"),
        "day": projection_date.strftime("%d"),
        "weekday": "Today" if projection_date == today else projection_date.strftime("%A"),
        "date_val": row["show_date"].isoformat(),
    }


def get_upcoming_movies_filters(db_connection):
    with db_connection.cursor() as cur:
        cur.execute("""
          SELECT
    c.name AS city,
    v.name AS cinema,
    g.name AS genre,
    m.title AS title,
    m.projection_start_date AS start_date,
    m.projection_end_date AS end_date
FROM movies m
JOIN movie_projections mp ON m.id = mp.movie_id
JOIN cinema_halls ch ON mp.cinema_hall_id = ch.id
JOIN venues v ON ch.venue_id = v.id
JOIN movie_genres mg ON m.id = mg.movie_id
JOIN genres g ON mg.genre_id = g.id
JOIN cities c ON v.city_id = c.id
WHERE m.projection_start_date > CURRENT_DATE
            GROUP BY
                c.name, v.name, g.name, m.title, m.projection_start_date, m.projection_end_date
            ORDER BY m.projection_start_date ASC
LIMIT 1;
        """)
        row = cur.fetchone()

    if not row:
        raise RuntimeError("No upcoming movies found — smoke test blocked")

    return {
        "city": row["city"],
        "cinema": row["cinema"],
        "genre": row["genre"],
        "search_term": row["title"],
        "start_date_val": row["start_date"].isoformat(),
        "end_date_val": row["end_date"].isoformat(),
        "start_date_aria": row["start_date"].strftime("%A, %B %d, %Y"),
        "end_date_aria": row["end_date"].strftime("%A, %B %d, %Y"),
    }
def get_movie_projections(db_connection):
    client = DBClient(db_connection)
    candidate_movie = client.fetch_one("""
            SELECT m.id, mp.projection_date, m.title
            FROM movies m
            JOIN movie_projections mp ON m.id = mp.movie_id
            WHERE (mp.projection_date > CURRENT_DATE) 
               OR (mp.projection_date = CURRENT_DATE AND mp.projection_time > CURRENT_TIME)
            ORDER BY mp.projection_date ASC, mp.projection_time ASC
            LIMIT 1;
        """)
    movie_id = candidate_movie["id"]
    movie_date = candidate_movie["projection_date"]
    return {
        "movie_id": movie_id,
        "projection_date": movie_date,
        "movie_title": candidate_movie["title"],
    }
def get_movie_details_data(db_connection):
    client = DBClient(db_connection)
    movie_row = client.fetch_one("""
        SELECT 
            m.id,
            m.title,
            m.language,
            m.pg_rating,
            m.duration_in_minutes,
            m.projection_start_date,
            m.projection_end_date,
            m.director_full_name,
            m.synopsis,
            mp.projection_time,
            mp.id AS projection_id,
            v.name AS cinema_name,
            c.name AS city_name
        FROM movies m
        JOIN movie_projections mp ON m.id = mp.movie_id
        JOIN cinema_halls ch ON mp.cinema_hall_id = ch.id
        JOIN venues v ON ch.venue_id = v.id
        JOIN cities c ON v.city_id = c.id
        WHERE mp.projection_date >= CURRENT_DATE
        AND mp.projection_time >= CURRENT_TIME
        ORDER BY mp.projection_date ASC, mp.projection_time ASC
        LIMIT 1;
    """)

    if not movie_row:
        raise RuntimeError("No active movies found for Movie Details Test")

    movie_id = movie_row["id"]
    with db_connection.cursor() as cur:
        cur.execute("""
            SELECT g.name 
            FROM genres g
            JOIN movie_genres mg ON g.id = mg.genre_id
            WHERE mg.movie_id = %s
            ORDER BY g.name
        """, (movie_id,))
        genres = [row["name"] for row in cur.fetchall()]

        cur.execute("""
            SELECT first_name, last_name
            FROM movie_writers
            WHERE movie_id = %s
        """, (movie_id,))
        writers = [f"{r['first_name']} {r['last_name']}" for r in cur.fetchall()]

        cur.execute("""
            SELECT c.first_name, c.last_name, c.character_full_name
            FROM movie_cast c
            WHERE c.movie_id = %s
        """, (movie_id,))

        cast_list = []
        for r in cur.fetchall():
            cast_list.append({
                "name": f"{r['first_name']} {r['last_name']}",
                "character": r["character_full_name"],
            })

    return {
        "id": movie_id,
        "title": movie_row["title"],
        "language": movie_row["language"],
        "pgRating": movie_row["pg_rating"],
        "duration": movie_row["duration_in_minutes"],
        "synopsis": movie_row["synopsis"],
        "projectionStartDate": movie_row["projection_start_date"].strftime("%Y-%m-%d"),
        "projectionEndDate": movie_row["projection_end_date"].strftime("%Y-%m-%d"),
        "director": movie_row["director_full_name"],
        "genres": genres,
        "writers": writers,
        "cast": cast_list,
        "city": movie_row["city_name"],
        "cinema": movie_row["cinema_name"],
        "projection_time": movie_row["projection_time"].strftime("%H:%M"),
        "movie_projection_id": movie_row["projection_id"],
    }


def get_api_filters(db_connection):
    client = DBClient(db_connection)
    current_row = client.fetch_one("""
        SELECT 
            m.title, 
            mp.projection_date, 
            mp.projection_time
        FROM movies m
        JOIN movie_projections mp ON m.id = mp.movie_id
        WHERE 
            (mp.projection_date = CURRENT_DATE AND mp.projection_time > CURRENT_TIME)
            OR 
            (mp.projection_date > CURRENT_DATE)
        ORDER BY mp.projection_date ASC, mp.projection_time ASC
        LIMIT 1;
    """)

    if not current_row:

        raise RuntimeError("No active/future movies found for API Smoke Test")


    filters_row = client.fetch_one("""
        SELECT
            m.title,
            c.id AS city_id,
            v.id AS venue_id,
            g.id AS genre_id,
            m.projection_start_date,
            m.projection_end_date
        FROM movies m
        JOIN movie_projections mp ON m.id = mp.movie_id
        JOIN cinema_halls ch ON mp.cinema_hall_id = ch.id
        JOIN venues v ON ch.venue_id = v.id
        JOIN movie_genres mg ON m.id = mg.movie_id
        JOIN genres g ON mg.genre_id = g.id
        JOIN cities c ON v.city_id = c.id
        WHERE m.projection_start_date > CURRENT_DATE
        LIMIT 1;
    """)

    if not filters_row:
        raise RuntimeError("No upcoming movies found for API Smoke Test")

    return {
        "filters": {
            "title": filters_row["title"],
            "cityId": str(filters_row["city_id"]),
            "venueId": str(filters_row["venue_id"]),
            "genreId": str(filters_row["genre_id"]),
            "startDate": filters_row["projection_start_date"].isoformat(),
            "endDate": filters_row["projection_end_date"].isoformat(),
            "page": 0,
            "size": 4
        },
        "current": {
            "title": current_row["title"],

            "projectionDate": current_row["projection_date"].isoformat(),
            "time": current_row["projection_time"].strftime("%H:%M"),
            "page": 0,
            "size": 5
        }
    }