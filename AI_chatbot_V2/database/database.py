import sqlite3
import os


# =========================================================
# DATABASE PATH
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATABASE_PATH = os.path.join(
    BASE_DIR,
    "database",
    "music_ai.db"
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    # Enable foreign key support
    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


# =========================================================
# INITIALIZE DATABASE
# =========================================================

def initialize_database():

    os.makedirs(
        os.path.dirname(DATABASE_PATH),
        exist_ok=True
    )

    connection = get_connection()

    cursor = connection.cursor()


    # -----------------------------------------------------
    # USERS
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # MUSIC CATEGORIES
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS music_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT UNIQUE NOT NULL
        )
    """)


    # -----------------------------------------------------
    # SONGS
    #
    # genre and mood are new in Version 2.
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            year INTEGER,
            category_id INTEGER NOT NULL,
            genre TEXT,
            mood TEXT,
            FOREIGN KEY (category_id)
                REFERENCES music_categories(id)
        )
    """)


    # -----------------------------------------------------
    # USER HISTORY
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # DATABASE MIGRATION
    #
    # If the songs table was created using Version 1,
    # add the new columns automatically.
    # -----------------------------------------------------

    cursor.execute("""
        PRAGMA table_info(songs)
    """)

    columns = [
        row["name"]
        for row in cursor.fetchall()
    ]


    if "genre" not in columns:

        cursor.execute("""
            ALTER TABLE songs
            ADD COLUMN genre TEXT
        """)


    if "mood" not in columns:

        cursor.execute("""
            ALTER TABLE songs
            ADD COLUMN mood TEXT
        """)


    # -----------------------------------------------------
    # MUSIC CATEGORIES
    # -----------------------------------------------------

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
            INSERT OR IGNORE INTO music_categories
            (category_name)
            VALUES (?)
        """, (category,))


    connection.commit()

    connection.close()


# =========================================================
# CATEGORY FUNCTIONS
# =========================================================

def get_category_id(category_name):

    connection = get_connection()


    result = connection.execute("""
        SELECT id
        FROM music_categories
        WHERE category_name = ?
    """, (
        category_name,
    )).fetchone()


    connection.close()


    if result:
        return result["id"]


    return None


def get_categories():

    connection = get_connection()


    categories = connection.execute("""
        SELECT id, category_name
        FROM music_categories
        ORDER BY id
    """).fetchall()


    connection.close()


    return categories


# =========================================================
# SONG FUNCTIONS
# =========================================================

def add_song(
    title,
    artist,
    year,
    category_name,
    genre=None,
    mood=None
):

    connection = get_connection()


    category_id = get_category_id(
        category_name
    )


    if category_id is None:

        connection.close()

        return False


    connection.execute("""
        INSERT INTO songs
        (
            title,
            artist,
            year,
            category_id,
            genre,
            mood
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        title,
        artist,
        year,
        category_id,
        genre,
        mood
    ))


    connection.commit()

    connection.close()


    return True


# =========================================================
# RECOMMENDATIONS
# =========================================================

def get_recommendations(
    category_name,
    genre=None,
    mood=None,
    limit=5
):

    connection = get_connection()


    query = """
        SELECT
            songs.id,
            songs.title,
            songs.artist,
            songs.year,
            songs.genre,
            songs.mood,
            music_categories.category_name
        FROM songs

        INNER JOIN music_categories
            ON songs.category_id =
               music_categories.id

        WHERE music_categories.category_name = ?
    """


    parameters = [
        category_name
    ]


    # -----------------------------------------------------
    # GENRE FILTER
    # -----------------------------------------------------

    if genre:

        query += """
            AND LOWER(songs.genre) = LOWER(?)
        """

        parameters.append(
            genre
        )


    # -----------------------------------------------------
    # MOOD FILTER
    # -----------------------------------------------------

    if mood:

        query += """
            AND LOWER(songs.mood) = LOWER(?)
        """

        parameters.append(
            mood
        )


    # -----------------------------------------------------
    # LIMIT
    # -----------------------------------------------------

    query += """
        ORDER BY RANDOM()
        LIMIT ?
    """

    parameters.append(
        limit
    )


    songs = connection.execute(
        query,
        parameters
    ).fetchall()


    connection.close()


    return songs


# =========================================================
# USERS
# =========================================================

def get_user_by_id(user_id):

    connection = get_connection()


    user = connection.execute("""
        SELECT *
        FROM users
        WHERE id = ?
    """, (
        user_id,
    )).fetchone()


    connection.close()


    return user


def get_user_by_name(name):

    connection = get_connection()


    user = connection.execute("""
        SELECT *
        FROM users
        WHERE name = ?
    """, (
        name,
    )).fetchone()


    connection.close()


    return user


def create_user(
    name,
    age,
    nationality,
    password_hash
):

    connection = get_connection()


    cursor = connection.execute("""
        INSERT INTO users
        (
            name,
            age,
            nationality,
            password_hash
        )
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


# =========================================================
# USER HISTORY
# =========================================================

def save_history(
    user_id,
    song_id,
    action
):

    connection = get_connection()


    connection.execute("""
        INSERT INTO user_history
        (
            user_id,
            song_id,
            action
        )
        VALUES (?, ?, ?)
    """, (
        user_id,
        song_id,
        action
    ))


    connection.commit()

    connection.close()


# =========================================================
# USER PREFERENCES
# =========================================================

def get_user_history(
    user_id,
    limit=20
):

    connection = get_connection()


    history = connection.execute("""
        SELECT
            user_history.id,
            user_history.action,
            user_history.timestamp,

            songs.id AS song_id,
            songs.title,
            songs.artist,
            songs.year,
            songs.genre,
            songs.mood,

            music_categories.category_name

        FROM user_history

        INNER JOIN songs
            ON user_history.song_id =
               songs.id

        INNER JOIN music_categories
            ON songs.category_id =
               music_categories.id

        WHERE user_history.user_id = ?

        ORDER BY user_history.timestamp DESC

        LIMIT ?
    """, (
        user_id,
        limit
    )).fetchall()


    connection.close()


    return history