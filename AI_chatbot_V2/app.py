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

from database.database import (
    initialize_database,
    create_user,
    get_user_by_id,
    get_user_by_name,
    save_history,
    get_recommendations
)

from recommender.recommender import (
    get_categories,
)

from chatbot.chatbot import (
    greeting,
    recommendation_message,
    analyze_music_request
)


app = Flask(__name__)

app.secret_key = "music-ai-development-key"

initialize_database()


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("chat"))

    return render_template("index.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register_user():

    data = request.get_json()

    name = data.get("name", "").strip()
    age = data.get("age")
    nationality = data.get("nationality", "").strip()
    password = data.get("password", "")

    if not name or not age or not nationality or not password:
        return jsonify({
            "success": False,
            "message": "Please provide all required information."
        }), 400

    try:
        age = int(age)
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Age must be a number."
        }), 400

    existing_user = get_user_by_name(name)

    if existing_user:
        return jsonify({
            "success": False,
            "message": "A user with this name already exists."
        }), 409

    password_hash = generate_password_hash(password)

    user_id = create_user(
        name,
        age,
        nationality,
        password_hash
    )

    session["user_id"] = user_id

    return jsonify({
        "success": True,
        "redirect": url_for("chat")
    })


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_user():

    data = request.get_json()

    name = data.get("name", "").strip()
    password = data.get("password", "")

    user = get_user_by_name(name)

    if not user:
        return jsonify({
            "success": False,
            "message": "Invalid name or password."
        }), 401

    if not check_password_hash(
        user["password_hash"],
        password
    ):
        return jsonify({
            "success": False,
            "message": "Invalid name or password."
        }), 401

    session["user_id"] = user["id"]

    return jsonify({
        "success": True,
        "redirect": url_for("chat")
    })


@app.route("/chat")
def chat():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = get_user_by_id(session["user_id"])

    categories = get_categories()

    return render_template(
        "chat.html",
        user=user,
        categories=categories
    )


@app.route("/recommend", methods=["POST"])
def recommend():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    data = request.get_json()

    category = data.get("category", "").strip()

    if not category:
        return jsonify({
            "success": False,
            "message": "Please select a music category."
        }), 400

    user = get_user_by_id(session["user_id"])

    songs = get_recommendations(category)

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
                "year": song["year"]
            }
            for song in songs
        ]
    })

@app.route("/chat_message", methods=["POST"])
def chat_message():

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401


    data = request.get_json()


    message = data.get(
        "message",
        ""
    ).strip()


    if not message:

        return jsonify({
            "success": False,
            "message": "Please enter a message."
        }), 400


    # =====================================================
    # ANALYZE USER MESSAGE
    # =====================================================

    analysis = analyze_music_request(
        message
    )


    category = analysis["category"]

    genre = analysis["genre"]

    mood = analysis["mood"]

    intent = analysis["intent"]


    # =====================================================
    # CATEGORY REQUIRED
    # =====================================================

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


    # =====================================================
    # GET USER
    # =====================================================

    user = get_user_by_id(
        session["user_id"]
    )


    # =====================================================
    # GET RECOMMENDATIONS
    # =====================================================

    songs = get_recommendations(
        category_name=category,
        genre=genre,
        mood=mood,
        limit=5
    )


    # =====================================================
    # FALLBACK
    #
    # If no songs match the complete combination,
    # progressively relax the filters.
    # =====================================================

    if not songs and genre and mood:

        songs = get_recommendations(
            category_name=category,
            genre=genre,
            limit=5
        )


    if not songs and mood:

        songs = get_recommendations(
            category_name=category,
            mood=mood,
            limit=5
        )


    if not songs:

        songs = get_recommendations(
            category_name=category,
            limit=5
        )


    # =====================================================
    # RESPONSE
    # =====================================================

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
                "mood": song["mood"]
            }

            for song in songs

        ]

    })

@app.route("/history", methods=["POST"])
def history():

    if "user_id" not in session:
        return jsonify({
            "success": False
        }), 401

    data = request.get_json()

    song_id = data.get("song_id")
    action = data.get("action")

    if action not in ["liked", "skipped"]:
        return jsonify({
            "success": False,
            "message": "Invalid action."
        }), 400

    save_history(
        session["user_id"],
        song_id,
        action
    )

    return jsonify({
        "success": True
    })


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )