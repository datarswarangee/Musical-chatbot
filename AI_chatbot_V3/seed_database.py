import csv
import os

from database.database import (
    initialize_database,
    add_song,
    get_connection
)


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

CSV_PATH = os.path.join(
    BASE_DIR,
    "data",
    "songs.csv"
)


# ============================================================
# REQUIRED CSV COLUMNS
# ============================================================

REQUIRED_COLUMNS = [
    "title",
    "artist",
    "year",
    "category",
    "genre",
    "mood",
    "link"
]


# ============================================================
# SEED SONGS
# ============================================================

def seed_songs():

    # --------------------------------------------------------
    # Initialize database
    # --------------------------------------------------------

    initialize_database()

    # --------------------------------------------------------
    # Check CSV
    # --------------------------------------------------------

    if not os.path.exists(CSV_PATH):

        print("[ERROR] songs.csv not found.")
        print(
            f"[ERROR] Expected location: "
            f"{CSV_PATH}"
        )

        return

    added = 0
    updated = 0
    skipped = 0

    # --------------------------------------------------------
    # Open CSV
    # --------------------------------------------------------

    with open(
        CSV_PATH,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        if reader.fieldnames is None:

            print(
                "[ERROR] songs.csv has no header."
            )

            return

        # Clean column names
        actual_columns = [
            column.strip()
            for column in reader.fieldnames
        ]

        # ----------------------------------------------------
        # Check required columns
        # ----------------------------------------------------

        missing_columns = [
            column
            for column in REQUIRED_COLUMNS
            if column not in actual_columns
        ]

        if missing_columns:

            print()
            print(
                "[ERROR] songs.csv is missing "
                "the following columns:"
            )

            for column in missing_columns:
                print(f"  - {column}")

            print()
            print(
                "[ERROR] Expected CSV format:"
            )
            print(
                "title,artist,year,category,"
                "genre,mood,link"
            )

            return

        print()
        print("================================")
        print("       SEEDING MUSIC DATABASE")
        print("================================")
        print()
        print(
            f"CSV File: {CSV_PATH}"
        )
        print()

        # ----------------------------------------------------
        # Process every song
        # ----------------------------------------------------

        for line_number, row in enumerate(
            reader,
            start=2
        ):

            try:

                # ------------------------------------------------
                # Read values
                # ------------------------------------------------

                title = (
                    row.get("title", "")
                    .strip()
                )

                artist = (
                    row.get("artist", "")
                    .strip()
                )

                year_value = (
                    row.get("year", "")
                    .strip()
                )

                category = (
                    row.get("category", "")
                    .strip()
                )

                genre = (
                    row.get("genre", "")
                    .strip()
                )

                mood = (
                    row.get("mood", "")
                    .strip()
                )

                link = (
                    row.get("link", "")
                    .strip()
                )

                # ------------------------------------------------
                # Validate required fields
                # ------------------------------------------------

                if not title:
                    raise ValueError(
                        "Missing song title"
                    )

                if not artist:
                    raise ValueError(
                        "Missing artist"
                    )

                if not year_value:
                    raise ValueError(
                        "Missing year"
                    )

                if not category:
                    raise ValueError(
                        "Missing category"
                    )

                if not genre:
                    raise ValueError(
                        "Missing genre"
                    )

                if not mood:
                    raise ValueError(
                        "Missing mood"
                    )

                # ------------------------------------------------
                # Convert year
                # ------------------------------------------------

                try:

                    year = int(
                        float(year_value)
                    )

                except ValueError:

                    raise ValueError(
                        f"Invalid year: "
                        f"{year_value}"
                    )

                # ------------------------------------------------
                # Open database
                # ------------------------------------------------

                connection = get_connection()

                # ------------------------------------------------
                # Check whether song already exists
                # ------------------------------------------------

                existing_song = connection.execute(
                    """
                    SELECT
                        id
                    FROM songs
                    WHERE
                        LOWER(title) = LOWER(?)
                        AND
                        LOWER(artist) = LOWER(?)
                    LIMIT 1
                    """,
                    (
                        title,
                        artist
                    )
                ).fetchone()

                # ------------------------------------------------
                # UPDATE EXISTING SONG
                # ------------------------------------------------

                if existing_song:

                    connection.execute(
                        """
                        UPDATE songs
                        SET
                            year = ?,

                            category_id = (
                                SELECT id
                                FROM music_categories
                                WHERE
                                    LOWER(category_name)
                                    =
                                    LOWER(?)
                            ),

                            genre = ?,
                            mood = ?,
                            link = ?

                        WHERE id = ?
                        """,
                        (
                            year,
                            category,
                            genre,
                            mood,
                            link if link else None,
                            existing_song["id"]
                        )
                    )

                    connection.commit()
                    connection.close()

                    updated += 1

                    print(
                        f"[UPDATED] "
                        f"{title} - {artist}"
                    )

                    print(
                        f"           Link: "
                        f"{link if link else 'NO LINK'}"
                    )

                # ------------------------------------------------
                # ADD NEW SONG
                # ------------------------------------------------

                else:

                    connection.close()

                    success = add_song(
                        title,
                        artist,
                        year,
                        category,
                        genre,
                        mood,
                        link if link else None
                    )

                    if success:

                        added += 1

                        print(
                            f"[ADDED] "
                            f"{title} - {artist}"
                        )

                        print(
                            f"         Link: "
                            f"{link if link else 'NO LINK'}"
                        )

                    else:

                        skipped += 1

                        print(
                            f"[SKIPPED] "
                            f"{title} - {artist}"
                        )

                        print(
                            f"           "
                            f"Unknown category: "
                            f"{category}"
                        )

            # ----------------------------------------------------
            # Handle individual row errors
            # ----------------------------------------------------

            except Exception as error:

                skipped += 1

                print(
                    f"[SKIPPED] Line "
                    f"{line_number}: "
                    f"{error}"
                )

    # ============================================================
    # FINAL SUMMARY
    # ============================================================

    print()
    print("================================")
    print("      DATABASE SEED COMPLETE")
    print("================================")
    print(
        f"Songs added   : {added}"
    )
    print(
        f"Songs updated : {updated}"
    )
    print(
        f"Songs skipped : {skipped}"
    )
    print("================================")
    print()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    seed_songs()