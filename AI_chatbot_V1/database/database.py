import sqlite3
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "database", "music_ai.db")


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            nationality TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS music_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            year INTEGER,
            category_id INTEGER NOT NULL,
            FOREIGN KEY (category_id)
                REFERENCES music_categories(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            song_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id)
                REFERENCES users(id),
            FOREIGN KEY (song_id)
                REFERENCES songs(id)
        )
    """)

    categories = [
        "60s",
        "70s",
        "80s",
        "90s",
        "early 2000s",
        "2010 onwards"
    ]

    for category in categories:
        cursor.execute("""
            INSERT OR IGNORE INTO music_categories (category_name)
            VALUES (?)
        """, (category,))

    connection.commit()
    connection.close()


def get_category_id(category_name):
    connection = get_connection()

    result = connection.execute("""
        SELECT id
        FROM music_categories
        WHERE category_name = ?
    """, (category_name,)).fetchone()

    connection.close()

    if result:
        return result["id"]

    return None


def add_song(title, artist, year, category_name):
    connection = get_connection()

    category_id = get_category_id(category_name)

    if category_id is None:
        connection.close()
        return False

    connection.execute("""
        INSERT INTO songs
        (title, artist, year, category_id)
        VALUES (?, ?, ?, ?)
    """, (
        title,
        artist,
        year,
        category_id
    ))

    connection.commit()
    connection.close()

    return True


def get_user_by_id(user_id):
    connection = get_connection()

    user = connection.execute("""
        SELECT *
        FROM users
        WHERE id = ?
    """, (user_id,)).fetchone()

    connection.close()

    return user


def get_user_by_name(name):
    connection = get_connection()

    user = connection.execute("""
        SELECT *
        FROM users
        WHERE name = ?
    """, (name,)).fetchone()

    connection.close()

    return user


def create_user(name, age, nationality, password_hash):
    connection = get_connection()

    cursor = connection.execute("""
        INSERT INTO users
        (name, age, nationality, password_hash)
        VALUES (?, ?, ?, ?)
    """, (
        name,
        age,
        nationality,
        password_hash
    ))

    connection.commit()

    user_id = cursor.lastrowid

    connection.close()

    return user_id


def save_history(user_id, song_id, action):
    connection = get_connection()

    connection.execute("""
        INSERT INTO user_history
        (user_id, song_id, action)
        VALUES (?, ?, ?)
    """, (
        user_id,
        song_id,
        action
    ))

    connection.commit()
    connection.close()