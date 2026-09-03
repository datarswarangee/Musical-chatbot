import random

from database.database import (
    get_connection,
    get_user_history
)


# ============================================================
# GET MUSIC CATEGORIES
# ============================================================

def get_categories():

    connection = get_connection()

    categories = connection.execute("""
        SELECT
            id,
            category_name
        FROM music_categories
        ORDER BY id
    """).fetchall()

    connection.close()

    return categories


# ============================================================
# BUILD USER PREFERENCES
# ============================================================

def get_user_preferences(user_id):

    history = get_user_history(
        user_id,
        limit=100
    )

    preferences = {
        "genres": {},
        "moods": {},
        "categories": {},
        "artists": {}
    }

    for item in history:

        action = item["action"]

        if action == "liked":
            weight = 1

        elif action == "skipped":
            weight = -1

        else:
            continue

        # ----------------------------------------------------
        # GENRE
        # ----------------------------------------------------

        genre = item["genre"]

        if genre:

            preferences["genres"][genre.lower()] = (
                preferences["genres"].get(
                    genre.lower(),
                    0
                ) + weight
            )

        # ----------------------------------------------------
        # MOOD
        # ----------------------------------------------------

        mood = item["mood"]

        if mood:

            preferences["moods"][mood.lower()] = (
                preferences["moods"].get(
                    mood.lower(),
                    0
                ) + weight
            )

        # ----------------------------------------------------
        # CATEGORY
        # ----------------------------------------------------

        category = item["category_name"]

        if category:

            preferences["categories"][category.lower()] = (
                preferences["categories"].get(
                    category.lower(),
                    0
                ) + weight
            )

        # ----------------------------------------------------
        # ARTIST
        # ----------------------------------------------------

        artist = item["artist"]

        if artist:

            preferences["artists"][artist.lower()] = (
                preferences["artists"].get(
                    artist.lower(),
                    0
                ) + weight
            )

    return preferences


# ============================================================
# GET USER HISTORY SONG IDS
# ============================================================

def get_user_history_song_ids(user_id):

    history = get_user_history(
        user_id,
        limit=100
    )

    liked_ids = set()
    skipped_ids = set()

    for item in history:

        song_id = item["song_id"]
        action = item["action"]

        if action == "liked":
            liked_ids.add(song_id)

        elif action == "skipped":
            skipped_ids.add(song_id)

    return liked_ids, skipped_ids


# ============================================================
# SCORE SONG
# ============================================================

def score_song(
    song,
    preferences,
    requested_genre=None,
    requested_mood=None
):

    score = 0

    # ========================================================
    # EXPLICIT USER REQUEST
    # ========================================================

    song_genre = song["genre"]
    song_mood = song["mood"]

    if requested_genre:

        if (
            song_genre
            and song_genre.lower()
            == requested_genre.lower()
        ):
            score += 5

    if requested_mood:

        if (
            song_mood
            and song_mood.lower()
            == requested_mood.lower()
        ):
            score += 4

    # ========================================================
    # USER HISTORY — GENRE
    # ========================================================

    if song_genre:

        score += preferences["genres"].get(
            song_genre.lower(),
            0
        ) * 3

    # ========================================================
    # USER HISTORY — MOOD
    # ========================================================

    if song_mood:

        score += preferences["moods"].get(
            song_mood.lower(),
            0
        ) * 2

    # ========================================================
    # USER HISTORY — CATEGORY
    # ========================================================

    category = song["category_name"]

    if category:

        score += preferences["categories"].get(
            category.lower(),
            0
        ) * 2

    # ========================================================
    # USER HISTORY — ARTIST
    # ========================================================

    artist = song["artist"]

    if artist:

        score += preferences["artists"].get(
            artist.lower(),
            0
        ) * 2

    return score


# ============================================================
# GET PERSONALIZED RECOMMENDATIONS
# ============================================================

def get_recommendations(
    user_id,
    category_name,
    genre=None,
    mood=None,
    limit=5
):

    connection = get_connection()

    # ========================================================
    # BASE QUERY
    # ========================================================

    query = """
        SELECT
            songs.id,
            songs.title,
            songs.artist,
            songs.year,
            songs.genre,
            songs.mood,
            songs.link,
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

    # ========================================================
    # EXPLICIT GENRE FILTER
    # ========================================================

    if genre:

        query += """
            AND LOWER(songs.genre) = LOWER(?)
        """

        parameters.append(genre)

    # ========================================================
    # EXPLICIT MOOD FILTER
    # ========================================================

    if mood:

        query += """
            AND LOWER(songs.mood) = LOWER(?)
        """

        parameters.append(mood)

    # ========================================================
    # FETCH SONGS
    # ========================================================

    songs = connection.execute(
        query,
        parameters
    ).fetchall()

    connection.close()

    songs = list(songs)

    # ========================================================
    # NO SONGS FOUND
    # ========================================================

    if not songs:
        return []

    # ========================================================
    # GET USER PREFERENCES
    # ========================================================

    preferences = get_user_preferences(
        user_id
    )

    # ========================================================
    # GET PREVIOUSLY INTERACTED SONGS
    # ========================================================

    liked_ids, skipped_ids = get_user_history_song_ids(
        user_id
    )

    # ========================================================
    # SCORE SONGS
    # ========================================================

    scored_songs = []

    for song in songs:

        song_id = song["id"]

        # ----------------------------------------------------
        # Do not recommend songs the user has already liked.
        # ----------------------------------------------------

        if song_id in liked_ids:
            continue

        # ----------------------------------------------------
        # Calculate personalization score
        # ----------------------------------------------------

        score = score_song(
            song,
            preferences,
            requested_genre=genre,
            requested_mood=mood
        )

        # ----------------------------------------------------
        # Strong penalty for previously skipped songs.
        # ----------------------------------------------------

        if song_id in skipped_ids:
            score -= 10

        scored_songs.append(
            (
                score,
                song
            )
        )

    # ========================================================
    # FALLBACK
    # ========================================================

    # If every song was previously liked, allow liked songs
    # rather than returning an empty recommendation list.

    if not scored_songs:

        for song in songs:

            score = score_song(
                song,
                preferences,
                requested_genre=genre,
                requested_mood=mood
            )

            scored_songs.append(
                (
                    score,
                    song
                )
            )

    # ========================================================
    # SORT BY SCORE
    # ========================================================

    scored_songs.sort(
        key=lambda item: item[0],
        reverse=True
    )

    # ========================================================
    # RANDOMIZE EQUAL SCORES
    # ========================================================

    grouped = {}

    for score, song in scored_songs:

        grouped.setdefault(
            score,
            []
        ).append(song)

    final_songs = []

    for score in sorted(
        grouped.keys(),
        reverse=True
    ):

        group = grouped[score]

        random.shuffle(group)

        final_songs.extend(group)

    # ========================================================
    # RETURN TOP RESULTS
    # ========================================================

    return final_songs[:limit]