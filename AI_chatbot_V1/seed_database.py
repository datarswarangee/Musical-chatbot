import csv
import os

from database.database import (
    initialize_database,
    add_song
)


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

CSV_PATH = os.path.join(
    BASE_DIR,
    "data",
    "songs.csv"
)


def seed_songs():

    initialize_database()

    if not os.path.exists(CSV_PATH):

        print("[ERROR] songs.csv not found.")

        return


    added = 0
    skipped = 0


    with open(
        CSV_PATH,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)


        print()
        print("Reading songs.csv...")
        print()


        for line_number, row in enumerate(
            reader,
            start=2
        ):

            try:

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


                try:

                    year = int(
                        float(year_value)
                    )

                except ValueError:

                    raise ValueError(
                        f"Invalid year: {year_value}"
                    )


                success = add_song(
                    title,
                    artist,
                    year,
                    category
                )


                if success:

                    added += 1

                    print(
                        f"[ADDED] {title} - {artist}"
                    )

                else:

                    skipped += 1

                    print(
                        f"[SKIPPED] {title} - "
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


    print()
    print("================================")
    print("      DATABASE SEED COMPLETE")
    print("================================")
    print(f"Songs added   : {added}")
    print(f"Songs skipped : {skipped}")
    print("================================")


if __name__ == "__main__":
    seed_songs()