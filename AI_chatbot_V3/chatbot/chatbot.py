import re


# =========================================================
# MUSIC CATEGORIES
# =========================================================

MUSIC_CATEGORIES = [
    "60s",
    "70s",
    "80s",
    "90s",
    "early 2000s",
    "2010 onwards"
]


# =========================================================
# GENRES
# =========================================================

GENRES = [
    "pop",
    "rock",
    "classical",
    "jazz",
    "bollywood"
]


# =========================================================
# MOODS
# =========================================================

MOODS = [
    "romantic",
    "happy",
    "sad",
    "energetic",
    "nostalgic",
    "relaxing"
]


# =========================================================
# GREETING
# =========================================================

def greeting(name):

    return (
        f"Welcome back, {name}! 🎵 "
        "What kind of music would you like "
        "to listen to today?"
    )


# =========================================================
# RECOMMENDATION MESSAGE
# =========================================================

def recommendation_message(
    name,
    category,
    genre=None,
    mood=None
):

    if genre and mood:

        return (
            f"Great choice, {name}! 🎶 "
            f"Here are some {mood} "
            f"{genre} songs from {category}."
        )


    if genre:

        return (
            f"Great choice, {name}! 🎶 "
            f"Here are some {genre} songs "
            f"from {category}."
        )


    if mood:

        return (
            f"Great choice, {name}! 🎶 "
            f"Here are some {mood} songs "
            f"from {category}."
        )


    return (
        f"Great choice, {name}! 🎶 "
        f"Here are some recommendations "
        f"from {category}."
    )


# =========================================================
# CATEGORY DETECTION
# =========================================================

def detect_music_category(message):

    if not message:
        return None


    text = message.lower().strip()


    # -----------------------------------------------------
    # EARLY 2000s
    # -----------------------------------------------------

    early_2000_patterns = [
        r"\b2000s\b",
        r"\b2000's\b",
        r"\bearly 2000s\b",
        r"\bearly 2000's\b",
        r"\btwo thousands\b",
        r"\b2000\b",
        r"\b2001\b",
        r"\b2002\b",
        r"\b2003\b",
        r"\b2004\b",
        r"\b2005\b"
    ]


    for pattern in early_2000_patterns:

        if re.search(pattern, text):

            return "early 2000s"


    # -----------------------------------------------------
    # 2010 ONWARDS
    # -----------------------------------------------------

    onwards_patterns = [
        r"\b2010 onwards\b",
        r"\b2010 and onwards\b",
        r"\bafter 2010\b",
        r"\bfrom 2010\b",
        r"\b2010s\b",
        r"\b2010's\b",
        r"\b2020s\b",
        r"\b2020's\b",
        r"\bmodern music\b",
        r"\brecent music\b",
        r"\bnew music\b"
    ]


    for pattern in onwards_patterns:

        if re.search(pattern, text):

            return "2010 onwards"


    # -----------------------------------------------------
    # 90s
    # -----------------------------------------------------

    if re.search(
        r"\b90s\b|\b90's\b|\bnineties\b|\b1990s\b",
        text
    ):

        return "90s"


    # -----------------------------------------------------
    # 80s
    # -----------------------------------------------------

    if re.search(
        r"\b80s\b|\b80's\b|\beighties\b|\b1980s\b",
        text
    ):

        return "80s"


    # -----------------------------------------------------
    # 70s
    # -----------------------------------------------------

    if re.search(
        r"\b70s\b|\b70's\b|\bseventies\b|\b1970s\b",
        text
    ):

        return "70s"


    # -----------------------------------------------------
    # 60s
    # -----------------------------------------------------

    if re.search(
        r"\b60s\b|\b60's\b|\bsixties\b|\b1960s\b",
        text
    ):

        return "60s"


    return None


# =========================================================
# GENRE DETECTION
# =========================================================

def detect_genre(message):

    if not message:
        return None


    text = message.lower()


    for genre in GENRES:

        if re.search(
            rf"\b{re.escape(genre)}\b",
            text
        ):

            return genre


    return None


# =========================================================
# MOOD DETECTION
# =========================================================

def detect_mood(message):

    if not message:
        return None


    text = message.lower()


    for mood in MOODS:

        if re.search(
            rf"\b{re.escape(mood)}\b",
            text
        ):

            return mood


    # -----------------------------------------------------
    # Additional natural language expressions
    # -----------------------------------------------------

    if re.search(
        r"\bin love\b|\blove songs?\b",
        text
    ):

        return "romantic"


    if re.search(
        r"\bcheerful\b|\bjoyful\b|\bfeel good\b",
        text
    ):

        return "happy"


    if re.search(
        r"\bheartbroken\b|\bmelancholy\b",
        text
    ):

        return "sad"


    if re.search(
        r"\bhigh energy\b|\bworkout\b|\bparty\b",
        text
    ):

        return "energetic"


    if re.search(
        r"\bnostalgia\b|\bnostalgic\b",
        text
    ):

        return "nostalgic"


    if re.search(
        r"\bcalm\b|\bpeaceful\b|\bunwind\b",
        text
    ):

        return "relaxing"


    return None


# =========================================================
# INTENT DETECTION
# =========================================================

def detect_intent(message):

    if not message:
        return "unknown"


    text = message.lower()


    recommendation_words = [
        "recommend",
        "recommendation",
        "play",
        "listen",
        "music",
        "song",
        "songs",
        "give me",
        "suggest",
        "suggestion",
        "want"
    ]


    for word in recommendation_words:

        if word in text:

            return "recommendation"


    return "unknown"


# =========================================================
# COMPLETE MESSAGE ANALYSIS
# =========================================================

def analyze_music_request(message):

    category = detect_music_category(
        message
    )


    genre = detect_genre(
        message
    )


    mood = detect_mood(
        message
    )


    intent = detect_intent(
        message
    )


    return {
        "intent": intent,
        "category": category,
        "genre": genre,
        "mood": mood
    }