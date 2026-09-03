from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


# ============================================================
# DATABASE FUNCTIONS
# ============================================================

from database.database import (
    initialize_database,
    create_user,
    get_user_by_id,
    get_user_by_name,
    save_history
)


# ============================================================
# RECOMMENDER FUNCTIONS
# ============================================================

from recommender.recommender import (
    get_categories,
    get_recommendations
)


# ============================================================
# CHATBOT FUNCTIONS
# ============================================================

from chatbot.chatbot import (
    greeting,
    recommendation_message,
    analyze_music_request
)


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)

app.secret_key = "music-ai-development-key"


# ============================================================
# INITIALIZE DATABASE
# ============================================================

initialize_database()


# ============================================================
# HOME
# ============================================================

@app.route("/")
def index():

    if "user_id" in session:

        return redirect(
            url_for("chat")
        )

    return render_template(
        "index.html"
    )


# ============================================================
# REGISTER PAGE
# ============================================================

@app.route("/register")
def register():

    return render_template(
        "register.html"
    )


# ============================================================
# REGISTER USER
# ============================================================

@app.route(
    "/register",
    methods=["POST"]
)
def register_user():

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "Invalid request."
        }), 400

    name = data.get(
        "name",
        ""
    ).strip()

    age = data.get(
        "age"
    )

    nationality = data.get(
        "nationality",
        ""
    ).strip()

    password = data.get(
        "password",
        ""
    )


    # ========================================================
    # VALIDATION
    # ========================================================

    if (
        not name
        or age is None
        or not nationality
        or not password
    ):

        return jsonify({
            "success": False,
            "message": (
                "Please provide all "
                "required information."
            )
        }), 400


    # ========================================================
    # AGE VALIDATION
    # ========================================================

    try:

        age = int(age)

    except (
        ValueError,
        TypeError
    ):

        return jsonify({
            "success": False,
            "message": "Age must be a number."
        }), 400


    if age <= 0:

        return jsonify({
            "success": False,
            "message": "Please enter a valid age."
        }), 400


    # ========================================================
    # CHECK EXISTING USER
    # ========================================================

    existing_user = get_user_by_name(
        name
    )

    if existing_user:

        return jsonify({
            "success": False,
            "message": (
                "A user with this name "
                "already exists."
            )
        }), 409


    # ========================================================
    # HASH PASSWORD
    # ========================================================

    password_hash = generate_password_hash(
        password
    )


    # ========================================================
    # CREATE USER
    # ========================================================

    user_id = create_user(
        name,
        age,
        nationality,
        password_hash
    )


    # ========================================================
    # CREATE LOGIN SESSION
    # ========================================================

    session["user_id"] = user_id


    return jsonify({
        "success": True,
        "redirect": url_for("chat")
    })


# ============================================================
# LOGIN PAGE
# ============================================================

@app.route("/login")
def login():

    return render_template(
        "login.html"
    )


# ============================================================
# LOGIN USER
# ============================================================

@app.route(
    "/login",
    methods=["POST"]
)
def login_user():

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "Invalid request."
        }), 400


    name = data.get(
        "name",
        ""
    ).strip()

    password = data.get(
        "password",
        ""
    )


    # ========================================================
    # VALIDATION
    # ========================================================

    if not name or not password:

        return jsonify({
            "success": False,
            "message": (
                "Please enter your name "
                "and password."
            )
        }), 400


    # ========================================================
    # FIND USER
    # ========================================================

    user = get_user_by_name(
        name
    )


    if not user:

        return jsonify({
            "success": False,
            "message": (
                "Invalid name or password."
            )
        }), 401


    # ========================================================
    # CHECK PASSWORD
    # ========================================================

    if not check_password_hash(
        user["password_hash"],
        password
    ):

        return jsonify({
            "success": False,
            "message": (
                "Invalid name or password."
            )
        }), 401


    # ========================================================
    # CREATE SESSION
    # ========================================================

    session["user_id"] = user["id"]


    return jsonify({
        "success": True,
        "redirect": url_for("chat")
    })


# ============================================================
# CHAT PAGE
# ============================================================

@app.route("/chat")
def chat():

    # --------------------------------------------------------
    # LOGIN REQUIRED
    # --------------------------------------------------------

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    # --------------------------------------------------------
    # GET USER
    # --------------------------------------------------------

    user = get_user_by_id(
        session["user_id"]
    )


    if not user:

        session.clear()

        return redirect(
            url_for("login")
        )


    # --------------------------------------------------------
    # GET CATEGORIES
    # --------------------------------------------------------

    categories = get_categories()


    return render_template(
        "chat.html",
        user=user,
        categories=categories
    )


# ============================================================
# CATEGORY RECOMMENDATIONS
# ============================================================

@app.route(
    "/recommend",
    methods=["POST"]
)
def recommend():

    # --------------------------------------------------------
    # LOGIN REQUIRED
    # --------------------------------------------------------

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401


    # --------------------------------------------------------
    # READ REQUEST
    # --------------------------------------------------------

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "Invalid request."
        }), 400


    category = data.get(
        "category",
        ""
    ).strip()


    # --------------------------------------------------------
    # CATEGORY VALIDATION
    # --------------------------------------------------------

    if not category:

        return jsonify({
            "success": False,
            "message": (
                "Please select a music category."
            )
        }), 400


    # --------------------------------------------------------
    # GET USER
    # --------------------------------------------------------

    user = get_user_by_id(
        session["user_id"]
    )


    if not user:

        session.clear()

        return jsonify({
            "success": False,
            "message": "User session expired."
        }), 401


    # ========================================================
    # V3 PERSONALIZED RECOMMENDATIONS
    # ========================================================

    try:

        songs = get_recommendations(
            user_id=session["user_id"],
            category_name=category,
            limit=5
        )

    except Exception as error:

        print(
            "[RECOMMEND ERROR]",
            error
        )

        return jsonify({
            "success": False,
            "message": (
                "Unable to generate "
                "recommendations."
            )
        }), 500


    # ========================================================
    # RESPONSE
    # ========================================================

    return jsonify({

        "success": True,

        "message": recommendation_message(
            user["name"],
            category
        ),

        "songs": [

            {
                "id": song["id"],
                "title": song["title"],
                "artist": song["artist"],
                "year": song["year"],
                "genre": song["genre"],
                "mood": song["mood"],
                "link": song["link"]
            }

            for song in songs

        ]
    })


# ============================================================
# CHAT MESSAGE
# ============================================================

@app.route(
    "/chat_message",
    methods=["POST"]
)
def chat_message():

    # --------------------------------------------------------
    # LOGIN REQUIRED
    # --------------------------------------------------------

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401


    # --------------------------------------------------------
    # READ REQUEST
    # --------------------------------------------------------

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "Invalid request."
        }), 400


    message = data.get(
        "message",
        ""
    ).strip()


    if not message:

        return jsonify({
            "success": False,
            "message": (
                "Please enter a message."
            )
        }), 400


    # ========================================================
    # ANALYZE USER MESSAGE
    # ========================================================

    analysis = analyze_music_request(
        message
    )


    category = analysis["category"]
    genre = analysis["genre"]
    mood = analysis["mood"]
    intent = analysis["intent"]


    # ========================================================
    # CATEGORY REQUIRED
    # ========================================================

    if category is None:

        return jsonify({

            "success": True,

            "detected": False,

            "message": (
                "I couldn't identify a music era "
                "from your message. Please try "
                "something like 60s, 70s, 80s, "
                "90s, early 2000s, or 2010 onwards."
            )

        })


    # ========================================================
    # GET USER
    # ========================================================

    user = get_user_by_id(
        session["user_id"]
    )


    if not user:

        session.clear()

        return jsonify({
            "success": False,
            "message": (
                "User session expired. "
                "Please login again."
            )
        }), 401


    # ========================================================
    # V3 PERSONALIZED RECOMMENDATIONS
    # ========================================================

    try:

        # ----------------------------------------------------
        # FIRST:
        # Category + Genre + Mood
        # ----------------------------------------------------

        songs = get_recommendations(

            user_id=session["user_id"],

            category_name=category,

            genre=genre,

            mood=mood,

            limit=5

        )


        # ----------------------------------------------------
        # FALLBACK 1:
        # Category + Genre
        # ----------------------------------------------------

        if (
            not songs
            and genre
            and mood
        ):

            songs = get_recommendations(

                user_id=session["user_id"],

                category_name=category,

                genre=genre,

                limit=5

            )


        # ----------------------------------------------------
        # FALLBACK 2:
        # Category + Mood
        # ----------------------------------------------------

        if (
            not songs
            and mood
        ):

            songs = get_recommendations(

                user_id=session["user_id"],

                category_name=category,

                mood=mood,

                limit=5

            )


        # ----------------------------------------------------
        # FALLBACK 3:
        # Category only
        # ----------------------------------------------------

        if not songs:

            songs = get_recommendations(

                user_id=session["user_id"],

                category_name=category,

                limit=5

            )


    except Exception as error:

        print(
            "[CHAT RECOMMENDER ERROR]",
            error
        )

        return jsonify({

            "success": False,

            "message": (
                "Sorry, I couldn't generate "
                "recommendations right now."
            )

        }), 500


    # ========================================================
    # RESPONSE
    # ========================================================

    return jsonify({

        "success": True,

        "detected": True,

        "category": category,

        "genre": genre,

        "mood": mood,

        "intent": intent,

        "message": recommendation_message(

            user["name"],

            category,

            genre,

            mood

        ),

        "songs": [

            {
                "id": song["id"],
                "title": song["title"],
                "artist": song["artist"],
                "year": song["year"],
                "genre": song["genre"],
                "mood": song["mood"],
                "link": song["link"]
            }

            for song in songs

        ]

    })


# ============================================================
# SAVE USER HISTORY
# ============================================================

@app.route(
    "/history",
    methods=["POST"]
)
def history():

    # --------------------------------------------------------
    # LOGIN REQUIRED
    # --------------------------------------------------------

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401


    # --------------------------------------------------------
    # READ REQUEST
    # --------------------------------------------------------

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "Invalid request."
        }), 400


    song_id = data.get(
        "song_id"
    )

    action = data.get(
        "action"
    )


    # --------------------------------------------------------
    # VALIDATE SONG ID
    # --------------------------------------------------------

    if song_id is None:

        return jsonify({
            "success": False,
            "message": "Song ID is required."
        }), 400


    try:

        song_id = int(song_id)

    except (
        ValueError,
        TypeError
    ):

        return jsonify({
            "success": False,
            "message": "Invalid song ID."
        }), 400


    if song_id <= 0:

        return jsonify({
            "success": False,
            "message": "Invalid song ID."
        }), 400


    # --------------------------------------------------------
    # VALIDATE ACTION
    # --------------------------------------------------------

    if action not in [
        "liked",
        "skipped"
    ]:

        return jsonify({
            "success": False,
            "message": "Invalid action."
        }), 400


    # --------------------------------------------------------
    # SAVE HISTORY
    # --------------------------------------------------------

    try:

        save_history(
            session["user_id"],
            song_id,
            action
        )

    except Exception as error:

        print(
            "[HISTORY ERROR]",
            error
        )

        return jsonify({

            "success": False,

            "message": (
                "Could not save song history."
            )

        }), 500


    return jsonify({
        "success": True
    })


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("index")
    )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )