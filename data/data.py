from datetime import date
from data.db_client import DBClient

def get_next_available_projection(db_connection):

    client = DBClient(db_connection)
    row = client.fetch_one("""
        SELECT 
            m.id AS movie_id, 
            m.title, 
            mp.id AS projection_id, 
            mp.projection_date, 
            mp.projection_time
        FROM movies m
        JOIN movie_projections mp ON m.id = mp.movie_id
        WHERE 
            (mp.projection_date = CURRENT_DATE AND mp.projection_time > CURRENT_TIME)
            OR (mp.projection_date > CURRENT_DATE)
        ORDER BY mp.projection_date ASC, mp.projection_time ASC
        LIMIT 1;
    """)
    if not row:
        raise RuntimeError("No future movie projections found in the database.")
    return row

def get_currently_showing_filters(db_connection):
    next_proj = get_next_available_projection(db_connection)
    client = DBClient(db_connection)

    enriched = client.fetch_one("""
        SELECT
            c.name AS city,
            v.name AS cinema,
            g.name AS genre
        FROM movie_projections mp
        JOIN cinema_halls ch ON mp.cinema_hall_id = ch.id
        JOIN venues v ON ch.venue_id = v.id
        JOIN cities c ON v.city_id = c.id
        JOIN movie_genres mg ON mg.movie_id = %s
        JOIN genres g ON mg.genre_id = g.id
        WHERE mp.id = %s
        LIMIT 1;
    """, (next_proj["movie_id"], next_proj["projection_id"]))

    projection_date = next_proj["projection_date"]
    today = date.today()

    return {
        "city": enriched["city"],
        "cinema": enriched["cinema"],
        "genre": enriched["genre"],
        "search_term": next_proj["title"],
        "projection": next_proj["projection_time"].strftime("%H:%M"),
        "month": projection_date.strftime("%b"),
        "day": projection_date.strftime("%d"),
        "weekday": "Today" if projection_date == today else projection_date.strftime("%A"),
        "date_val": projection_date.isoformat(),
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
            GROUP BY c.name, v.name, g.name, m.title, m.projection_start_date, m.projection_end_date
            ORDER BY m.projection_start_date ASC
            LIMIT 1;
        """)
        row = cur.fetchone()

    if not row:
        raise RuntimeError("No movies with a future start date found.")

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
    row = get_next_available_projection(db_connection)
    return {
        "movie_id": row["movie_id"],
        "projection_date": row["projection_date"],
        "movie_title": row["title"],
    }

def get_movie_details_data(db_connection):

    next_proj = get_next_available_projection(db_connection)
    client = DBClient(db_connection)

    movie_row = client.fetch_one("""
        SELECT 
            m.id, m.title, m.language, m.pg_rating, m.duration_in_minutes,
            m.projection_start_date, m.projection_end_date, m.director_full_name,
            m.synopsis, mp.projection_time, mp.id AS projection_id,
            v.name AS cinema_name, c.name AS city_name
        FROM movies m
        JOIN movie_projections mp ON m.id = mp.movie_id
        JOIN cinema_halls ch ON mp.cinema_hall_id = ch.id
        JOIN venues v ON ch.venue_id = v.id
        JOIN cities c ON v.city_id = c.id
        WHERE mp.id = %s
        LIMIT 1;
    """, (next_proj["projection_id"],))

    if not movie_row:
        raise RuntimeError("Could not find details for the selected projection.")

    movie_id = movie_row["id"]
    with db_connection.cursor() as cur:
        # Genres
        cur.execute("SELECT g.name FROM genres g JOIN movie_genres mg ON g.id = mg.genre_id WHERE mg.movie_id = %s ORDER BY g.name", (movie_id,))
        genres = [r["name"] for r in cur.fetchall()]

        # Writers
        cur.execute("SELECT first_name, last_name FROM movie_writers WHERE movie_id = %s", (movie_id,))
        writers = [f"{r['first_name']} {r['last_name']}" for r in cur.fetchall()]

        # Cast
        cur.execute("SELECT first_name, last_name, character_full_name FROM movie_cast WHERE movie_id = %s", (movie_id,))
        cast_list = [{"name": f"{r['first_name']} {r['last_name']}", "character": r["character_full_name"]} for r in cur.fetchall()]

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
        "movie_projection_id": movie_row["projection_id"]
    }

def get_api_filters(db_connection):

    next_proj = get_next_available_projection(db_connection)
    client = DBClient(db_connection)

    # Get specific IDs for the filters
    filters_row = client.fetch_one("""
        SELECT
            c.id AS city_id, v.id AS venue_id, g.id AS genre_id,
            m.projection_start_date, m.projection_end_date
        FROM movies m
        JOIN movie_projections mp ON m.id = mp.movie_id
        JOIN cinema_halls ch ON mp.cinema_hall_id = ch.id
        JOIN venues v ON ch.venue_id = v.id
        JOIN movie_genres mg ON m.id = mg.movie_id
        JOIN genres g ON mg.genre_id = g.id
        JOIN cities c ON v.city_id = c.id
        WHERE mp.id = %s
        LIMIT 1;
    """, (next_proj["projection_id"],))

    return {
        "filters": {
            "title": next_proj["title"],
            "cityId": str(filters_row["city_id"]),
            "venueId": str(filters_row["venue_id"]),
            "genreId": str(filters_row["genre_id"]),
            "startDate": filters_row["projection_start_date"].isoformat(),
            "endDate": filters_row["projection_end_date"].isoformat(),
            "page": 0,
            "size": 4
        },
        "current": {
            "title": next_proj["title"],
            "date": next_proj["projection_date"].isoformat(),
            "time": next_proj["projection_time"].strftime("%H:%M"),
            "page": 0,
            "size": 5
        }
    }