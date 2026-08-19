import csv
import os

from database.database import (
    initialize_database,
    add_song
)


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

CSV_PATH = os.path.join(
    BASE_DIR,
    "data",
    "songs.csv"
)


# =========================================================
# REQUIRED CSV COLUMNS
# =========================================================

REQUIRED_COLUMNS = [
    "title",
    "artist",
    "year",
    "category",
    "genre",
    "mood"
]


# =========================================================
# SEED DATABASE
# =========================================================

def seed_songs():

    # -----------------------------------------------------
    # Initialize / migrate database
    # -----------------------------------------------------

    initialize_database()


    # -----------------------------------------------------
    # Check CSV
    # -----------------------------------------------------

    if not os.path.exists(CSV_PATH):

        print(
            "[ERROR] songs.csv not found."
        )

        print(
            f"[ERROR] Expected location: "
            f"{CSV_PATH}"
        )

        return


    added = 0
    skipped = 0


    # -----------------------------------------------------
    # Open CSV
    # -----------------------------------------------------

    with open(
        CSV_PATH,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)


        # -------------------------------------------------
        # Validate CSV header
        # -------------------------------------------------

        if reader.fieldnames is None:

            print(
                "[ERROR] songs.csv has no header."
            )

            return


        actual_columns = [
            column.strip()
            for column in reader.fieldnames
        ]


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

                print(
                    f"  - {column}"
                )

            print()
            print(
                "[ERROR] Expected CSV format:"
            )

            print(
                "title,artist,year,"
                "category,genre,mood"
            )

            return


        # -------------------------------------------------
        # Start processing
        # -------------------------------------------------

        print()
        print(
            "Reading songs.csv..."
        )
        print()


        for line_number, row in enumerate(
            reader,
            start=2
        ):

            try:

                # -----------------------------------------
                # Read fields
                # -----------------------------------------

                title = row.get(
                    "title",
                    ""
                ).strip()


                artist = row.get(
                    "artist",
                    ""
                ).strip()


                year_value = row.get(
                    "year",
                    ""
                ).strip()


                category = row.get(
                    "category",
                    ""
                ).strip()


                genre = row.get(
                    "genre",
                    ""
                ).strip()


                mood = row.get(
                    "mood",
                    ""
                ).strip()


                # -----------------------------------------
                # Validate title
                # -----------------------------------------

                if not title:

                    raise ValueError(
                        "Missing song title"
                    )


                # -----------------------------------------
                # Validate artist
                # -----------------------------------------

                if not artist:

                    raise ValueError(
                        "Missing artist"
                    )


                # -----------------------------------------
                # Validate year
                # -----------------------------------------

                if not year_value:

                    raise ValueError(
                        "Missing year"
                    )


                try:

                    year = int(
                        float(year_value)
                    )

                except ValueError:

                    raise ValueError(
                        f"Invalid year: "
                        f"{year_value}"
                    )


                # -----------------------------------------
                # Validate category
                # -----------------------------------------

                if not category:

                    raise ValueError(
                        "Missing category"
                    )


                # -----------------------------------------
                # Validate genre
                # -----------------------------------------

                if not genre:

                    raise ValueError(
                        "Missing genre"
                    )


                # -----------------------------------------
                # Validate mood
                # -----------------------------------------

                if not mood:

                    raise ValueError(
                        "Missing mood"
                    )


                # -----------------------------------------
                # Add song
                # -----------------------------------------

                success = add_song(
                    title,
                    artist,
                    year,
                    category,
                    genre,
                    mood
                )


                # -----------------------------------------
                # Result
                # -----------------------------------------

                if success:

                    added += 1

                    print(
                        f"[ADDED] "
                        f"{title} - "
                        f"{artist} | "
                        f"{category} | "
                        f"{genre} | "
                        f"{mood}"
                    )

                else:

                    skipped += 1

                    print(
                        f"[SKIPPED] "
                        f"{title} - "
                        f"Unknown category: "
                        f"{category}"
                    )


            except Exception as error:

                skipped += 1

                print(
                    f"[SKIPPED] Line "
                    f"{line_number}: "
                    f"{error}"
                )


    # =====================================================
    # FINAL SUMMARY
    # =====================================================

    print()

    print(
        "================================"
    )

    print(
        "      DATABASE SEED COMPLETE"
    )

    print(
        "================================"
    )

    print(
        f"Songs added   : {added}"
    )

    print(
        f"Songs skipped : {skipped}"
    )

    print(
        "================================"
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    seed_songs()