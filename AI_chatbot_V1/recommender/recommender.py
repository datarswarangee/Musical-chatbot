import random

from database.database import get_connection


def get_categories():
    connection = get_connection()

    categories = connection.execute("""
        SELECT id, category_name
        FROM music_categories
        ORDER BY category_name
    """).fetchall()

    connection.close()

    return categories


def get_recommendations(category_name, limit=5):
    connection = get_connection()

    songs = connection.execute("""
        SELECT
            songs.id,
            songs.title,
            songs.artist,
            songs.year,
            music_categories.category_name
        FROM songs
        JOIN music_categories
            ON songs.category_id = music_categories.id
        WHERE music_categories.category_name = ?
    """, (category_name,)).fetchall()

    connection.close()

    songs = list(songs)

    random.shuffle(songs)

    return songs[:limit]