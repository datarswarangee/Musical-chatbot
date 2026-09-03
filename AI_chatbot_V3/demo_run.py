from database.database import get_connection

connection = get_connection()

songs = connection.execute("""
    SELECT
        id,
        title,
        artist,
        link
    FROM songs
    LIMIT 20
""").fetchall()

connection.close()

for song in songs:
    print(
        song["id"],
        "|",
        song["title"],
        "|",
        song["artist"],
        "|",
        song["link"]
    )