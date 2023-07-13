import os
from dotenv import load_dotenv
import pyrebase
import sys
from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    redirect,
    url_for,
    session,
    flash,
)
from flask_session import Session
from AnilistPython import Anilist
from AnilistPython import DatabaseSearcher
import firebase_admin
from firebase_admin import credentials, auth
from PyMovieDb import IMDB
from imdb import IMDb
import secrets
import time

load_dotenv()

config = {
    "apiKey": os.getenv("API_KEY"),
    "authDomain": os.getenv("AUTH_DOMAIN"),
    "projectId": "showtrac-1",
    "storageBucket": "showtrac-1.appspot.com",
    "messagingSenderId": "890339240647",
    "appId": os.getenv("APP_ID"),
    "measurementId": "G-HLGSH0TPD5",
    "databaseURL": os.getenv("DATABASE_URL"),
    # "serviceAccount": "/Users/margaretrivas/Desktop/cop4521/ShowTrack2/showtrac-1-firebase-adminsdk-ks879-0de599aff8.json",
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

# Initialize Firebase Admin SDK
# cred = credentials.Certificate(config["serviceAccount"])
# firebase_admin.initialize_app(cred)
# auth = auth

# Adding a new table to store admin email addresses
admin_emails = [
    "hogwarts0500@gmail.com",
    "magylutzkanov@gmail.com",
    "admin3@domain.com",
    "admintest@gmail.com",
    "sos@gmail.com",
    "yuh@gmail.com",
]

db.child("admin_emails").set(admin_emails)

# Initializing API's
anilist = Anilist()
anime_db = DatabaseSearcher()
imbd = IMDB()
imdb2 = IMDb()

app = Flask(__name__, template_folder="templates")

secret_key = secrets.token_hex(16)
app.secret_key = secret_key
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

"""
Page Routes
"""


def stream_handler(message):
    print(message["event"])  # put
    print(message["path"])  # /-K7yGTTEp7O549EzTYtI
    print(message["data"])  # {'title': 'Pyrebase', "body": "etc..."}


@app.route("/")
def index():
    return render_template("index.html", show_popup=False)


@app.route("/signup", methods=["POST"])
def signup():
    try:
        email = request.form.get("email")
        password = request.form.get("password")
        username = request.form.get("username")
        user = auth.create_user_with_email_and_password(email, password)
        timestamp = time.time()
        data = {
            "email": email,
            "username": username,
            "anime": {},
            "movies": {},
            "shows": {},
            "isPremium": False,
            "admin": False,
            "dateAdded": timestamp,
        }
        # Check if the user is an admin - makes them premium automatically
        admin_emails = db.child("admin_emails").get().val()
        if email in admin_emails:
            data["isPremium"] = True
            data["admin"] = True

        # auth.send_email_verification(user['idToken'])
        session["user"] = user

        if user:
            user_id = user["localId"]

        db.child("users").child(user_id).set(data)

        return redirect(url_for("main"))
    except Exception as e:
        print("Error", e, file=sys.stderr)
        return redirect(url_for("index"))


@app.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        try:
            email = request.form.get("email")
            password = request.form.get("password")
            user = auth.sign_in_with_email_and_password(email, password)

            auth.refresh(user["refreshToken"])

            # Retrieve user's data
            user_data = db.child("users").child(user["localId"]).get().val()

            session["user"] = user

            userr = session["user"]

            if userr:
                user_id = user["localId"]

            if not user_data:
                return render_template("ban.html")
            else:
                admin_emails = db.child("admin_emails").get().val()

                if (email in admin_emails) and user_data:
                    db.child("users").child(user_id).update({"isPremium": True})
                    db.child("users").child(user_id).update({"admin": True})

                elif user_data:
                    db.child("users").child(user_id).update({"admin": False})

                return redirect("/app")
        except Exception as e:
            print("Error", e, file=sys.stderr)
            return redirect(url_for("index"))


@app.route("/changeUsername", methods=["POST"])
def changeUsername():
    if request.method == "POST":
        try:
            # get user data from current session
            user = session["user"]
            newname = request.form["NewUserName"]

            # only send data of the currently logged in user
            if user:
                user_id = user["localId"]

            db.child("users").child(user_id).update({"username": newname})
            data = db.child("users").child(user_id).get()

            sessionUser = auth.get_account_info(user["idToken"])

            return render_template("profile.html", data=data, session=sessionUser)
        except Exception as e:
            print("Error", e, file=sys.stderr)
            return redirect(url_for("main"))


@app.route("/app")
def main():
    check = True

    # get user data from current session
    user = session["user"]

    # only send data of the currently logged in user
    if user:
        user_id = user["localId"]

    data = db.child("users").child(user_id).get()

    if data.val() is None:
        check = False

    sessionUser = auth.get_account_info(user["idToken"])

    return render_template("app.html", data=data, session=sessionUser, check=check)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if request.method == "GET":
        try:
            # get user data from current session
            user = session["user"]

            # only send data of the currently logged in user
            if user:
                user_id = user["localId"]

            data = db.child("users").child(user_id).get()

            sessionUser = auth.get_account_info(user["idToken"])

            return render_template("profile.html", data=data, session=sessionUser)
        except Exception as e:
            print("Error", e, file=sys.stderr)
            return redirect(url_for("main"))


@app.route("/admin", methods=["GET", "POST"])
def admin():
    try:
        # get user data from current session
        user = session["user"]

        all_users = db.child("users").get().val()

        # for key, value in all_users.items():
        #     print("{}: {}".format(key, value), end=" | ")

        # only send data of the currently logged in user
        if user:
            user_id = user["localId"]

        data = db.child("users").child(user_id).get()

        sessionUser = auth.get_account_info(user["idToken"])

        return render_template(
            "admin.html", data=data, session=sessionUser, all_users=all_users
        )
    except Exception as e:
        print("Error", e, file=sys.stderr)
        return redirect(url_for("main"))


@app.route("/admin/deleteUser", methods=["GET", "POST"])
def deleteUser():
    if request.method == "POST":
        try:
            userID = request.form.get("user_id")
            print("userID:", userID)
            userEmail = request.form.get("user_email")
            db.child("banned_emails").child(userID).set(userEmail)

            # Delete users
            db.child("users").child(userID).remove()
            # auth.update_user(userID,disabled = True)

            # Currently not working, will not let users create another account with same email after deletion
            # try:
            #     auth.delete_user(userID)
            # except Exception as e:
            #     print("Error deleting user: ", e)

            print("Successfully banned user")

            return redirect(url_for("admin"))
        except Exception as e:
            print("Error banning user: ", e)


@app.route("/admin/makePremium", methods=["GET", "POST"])
def adminPremium():
    if request.method == "POST":
        try:
            userID = request.form.get("user_id")

            # Make user premium
            db.child("users").child(userID).update({"isPremium": True})

            print("Successfully made user premium")

            return redirect(url_for("admin"))
        except Exception as e:
            print("Error deleting user: ", e)


@app.route("/admin/removePremium", methods=["GET", "POST"])
def removeAdminPremium():
    # Function for admins to remove user's premium access
    if request.method == "POST":
        try:
            userID = request.form.get("user_id")

            # Make user premium
            db.child("users").child(userID).update({"isPremium": False})

            print("Successfully removed user premium access")

            return redirect(url_for("admin"))
        except Exception as e:
            print("Error deleting user: ", e)


@app.route("/app/top", methods=["GET"])
def topShows():
    if request.method == "GET":
        try:
            check = True

            # get user data from current session
            user = session["user"]

            # only send data of the currently logged in user
            if user:
                user_id = user["localId"]

            topShows = db.child("topShows").get()

            if topShows.val() is None:
                check = False

            sessionUser = auth.get_account_info(user["idToken"])
            data = db.child("users").child(user_id).get()

            for i in topShows.each():
                print(i.val(), file=sys.stderr)

            return render_template(
                "topShows.html", topShows=topShows, session=sessionUser, data=data
            )
        except Exception as e:
            print("Error", e, file=sys.stderr)
            return redirect(url_for("main"))


"""
API Routes
"""


@app.route("/api/addAnime", methods=["GET", "POST"])
def addAnime():
    if request.method == "GET":
        try:
            # get user data from current session
            user = session["user"]

            # only send data of the currently logged in user
            if user:
                user_id = user["localId"]

            # get input from user from search bar
            userInput = request.args.get("animeName")

            # Check if input is name or anime ID
            # ID case
            if userInput.isdigit():
                anime = anilist.get_anime_with_id(userInput)
                # add anime to user's database

            else:
                anime = anilist.get_anime(userInput)

            name = anime["name_english"]
            avg_score = anime["average_score"]

            if anime["airing_episodes"] is None:
                episode = anime["next_airing_ep"]["episode"]
            else:
                episode = anime["airing_episodes"]

            image = anime["cover_image"]

            # add to users database
            db.child("users").child(user_id).child("anime").push(
                {
                    "name": name,
                    "avgScore": avg_score,
                    "episodes": episode,
                    "status": "Watching",
                    "image": image,
                    "UserScore": float("0.0"),
                }
            )

            print(anime, file=sys.stderr)
            print(name, file=sys.stderr)

            return redirect(url_for("main"))
        except Exception as e:
            print("Error", e, file=sys.stderr)
            return redirect(url_for("main"))


@app.route("/api/changeToCompleted/<anime_id>", methods=["GET", "POST"])
def changeCompleted(anime_id):
    if request.method == "GET":
        try:
            # get user data from current session
            user = session["user"]

            # only send data of the currently logged in user
            if user:
                user_id = user["localId"]

            # change status to completed
            db.child("users").child(user_id).child("anime").child(anime_id).update(
                {"status": "Completed"}
            )

            return redirect(url_for("main"))
        except Exception as e:
            app.logger.error("Error", e)
            return redirect(url_for("main"))


@app.route("/api/changeToWatching/<anime_id>", methods=["GET", "POST"])
def changeWatching(anime_id):
    if request.method == "GET":
        try:
            # get user data from current session
            user = session["user"]

            # only send data of the currently logged in user
            if user:
                user_id = user["localId"]

            # change status to completed
            db.child("users").child(user_id).child("anime").child(anime_id).update(
                {"status": "Watching"}
            )

            return redirect(url_for("main"))
        except Exception as e:
            app.logger.error("Error", e)
            return redirect(url_for("main"))


@app.route("/api/changeToPlanWatch/<anime_id>", methods=["GET", "POST"])
def planToWatch(anime_id):
    if request.method == "GET":
        try:
            # get user data from current session
            user = session["user"]

            # only send data of the currently logged in user
            if user:
                user_id = user["localId"]

            # change status to completed
            db.child("users").child(user_id).child("anime").child(anime_id).update(
                {"status": "Plan to Watch"}
            )

            return redirect(url_for("main"))
        except Exception as e:
            app.logger.error("Error", e)
            return redirect(url_for("main"))


@app.route("/api/changeToDropped/<anime_id>", methods=["GET", "POST"])
def changeDropped(anime_id):
    if request.method == "GET":
        try:
            # get user data from current session
            user = session["user"]

            # only send data of the currently logged in user
            if user:
                user_id = user["localId"]

            # change status to completed
            db.child("users").child(user_id).child("anime").child(anime_id).update(
                {"status": "Dropped"}
            )

            return redirect(url_for("main"))
        except Exception as e:
            app.logger.error("Error", e)
            return redirect(url_for("main"))


@app.route("/api/changeToOnHold/<anime_id>", methods=["GET", "POST"])
def changeOnHold(anime_id):
    if request.method == "GET":
        try:
            # get user data from current session
            user = session["user"]

            # only send data of the currently logged in user
            if user:
                user_id = user["localId"]

            # change status to completed
            db.child("users").child(user_id).child("anime").child(anime_id).update(
                {"status": "On Hold"}
            )

            return redirect(url_for("main"))
        except Exception as e:
            app.logger.error("Error", e)
            return redirect(url_for("main"))


@app.route("/api/deleteAnime/<anime_id>", methods=["GET"])
def deleteAnime(anime_id):
    if request.method == "GET":
        try:
            # get user data from current session
            user = session["user"]

            # only send data of the currently logged in user
            if user:
                user_id = user["localId"]

            # change status to completed
            db.child("users").child(user_id).child("anime").child(anime_id).remove()

            return redirect(url_for("main"))
        except Exception as e:
            app.logger.error("Error", e)
            return redirect(url_for("main"))


@app.route("/app/SaveUserRating/<anime_id>", methods=["GET", "POST"])
def SaveUserRating(anime_id):
    if request.method == "POST":
        try:
            # save the pages ratings
            rate = request.form["User Rating"]
            user = session["user"]
            if user:
                user_id = user["localId"]
                db.child("users").child(user_id).child("anime").child(anime_id).update(
                    {"UserScore": "{:.2f}".format(float(rate))}
                )
            return redirect(url_for("main"))
        except Exception as e:
            app.logger.error("Error", e)
            return redirect(url_for("main"))


@app.route("/app/searchAnime", methods=["GET", "POST"])
def searchAnime():
    if request.method == "GET":
        try:
            check = True
            # get user data from current session
            user = session["user"]

            # only send data of the currently logged in user
            if user:
                user_id = user["localId"]

            data = db.child("users").child(user_id).get()

            if data.val() is None:
                check = False

            sessionUser = auth.get_account_info(user["idToken"])

            return render_template("search.html", data=data, session=sessionUser)

        except Exception as e:
            app.logger.error("Error", e)


@app.route("/app/displaySearch", methods=["GET", "POST"])
def displaySearch():
    if request.method == "POST":
        try:
            check = True
            # get user data from current session
            user = session["user"]

            # only send data of the currently logged in user
            if user:
                user_id = user["localId"]

            data = db.child("users").child(user_id).get()

            if data.val() is None:
                check = False

            sessionUser = auth.get_account_info(user["idToken"])

            year = "2019"
            # season = None
            genre = "Action"
            score = 50

            # get input from user
            year = request.form.get("year")
            genre = request.form.get("genre")
            score = request.form.get("score")

            # Search anime by release year, season, genre or score
            anime_list_results = anilist.search_anime(
                genre=[genre],
                year=[year],
                score=range(int(score), 100),
            )
            # print("search:")
            # for anime in anime_list_results:
            #     print(anime)
            # # Search anime by release season

            return render_template(
                "displaySearch.html",
                searchResults=anime_list_results,
                session=sessionUser,
                data=data,
                check=check,
            )
        except Exception as e:
            print("Error", e, file=sys.stderr)
            return redirect(url_for("main"))


######################
### SHOWTRACKPLUS ###
######################


# ST+ Page
@app.route("/app/stplus", methods=["GET", "POST"])
def stplus():
    if request.method == "GET":
        try:
            check = True
            # get user data from current session
            user = session["user"]

            # only send data of the currently logged in user
            if user:
                user_id = user["localId"]

            data = db.child("users").child(user_id).get()

            if data.val() is None:
                check = False

            sessionUser = auth.get_account_info(user["idToken"])

            return render_template(
                "app.html",
                data=data,
                session=sessionUser,
                check=check,
                show_popup=False,
            )

        except Exception as e:
            app.logger.error("Error", e)


# Bring in API for Movies and Shows
@app.route("/api/addTV", methods=["GET", "POST"])
def addTVnMovie():
    if request.method == "GET":
        try:
            check = True
            # get user data from current session
            user = session["user"]

            # only send data of the currently logged in user
            if user:
                user_id = user["localId"]

            sessionUser = auth.get_account_info(user["idToken"])

            # get input from user from search bar
            userInput = request.args.get("tvName")

            movie = imdb2.search_movie(userInput)

            if movie:
                try:
                    m = imdb2.get_movie(movie[0].movieID)
                    name = m["title"]
                    avg_score = m["rating"]
                    image = m["cover url"]
                    episodes = m["seasons"]
                except KeyError:
                    name = movie[0]["title"]
                    avg_score = "0.0"  # assign default value of 0.0
                    image = movie[0]["full-size cover url"]
                    episodes = 0

            # Check if user input valid movie
            if movie:
                db.child("users").child(user_id).child("anime").push(
                    {
                        "name": name,
                        "avgScore": avg_score,
                        "episodes": episodes,
                        "status": "Watching",
                        "image": image,
                        "UserScore": float("0.0"),
                    }
                )
                # print(m.data)

                data = db.child("users").child(user_id).get()

                if data.val() is None:
                    check = False

                return render_template(
                    "app.html",
                    data=data,
                    session=sessionUser,
                    check=check,
                    show_popup=False,
                )

            else:
                data = db.child("users").child(user_id).get()

                if data.val() is None:
                    check = False

                return render_template(
                    "app.html",
                    data=data,
                    session=sessionUser,
                    check=check,
                    show_popup=True,
                )

        except Exception as e:
            app.logger.error("Error", e)


@app.route("/app/premiumSubscription", methods=["GET", "POST"])
def premiumSub():
    if request.method == "GET":
        try:
            check = True
            # get user data from current session
            user = session["user"]

            # only send data of the currently logged in user
            if user:
                user_id = user["localId"]

            data = db.child("users").child(user_id).get()

            if data.val() is None:
                check = False

            sessionUser = auth.get_account_info(user["idToken"])

            return render_template(
                "premiumSub.html",
                data=data,
                session=sessionUser,
                check=check,
                show_popup=False,
            )

        except Exception as e:
            app.logger.error("Error", e)


@app.route("/app/makePremium", methods=["GET", "POST"])
def makePremium():
    if request.method == "POST":
        try:
            check = True
            # get user data from current session
            user = session["user"]

            # only send data of the currently logged in user
            if user:
                user_id = user["localId"]
            sessionUser = auth.get_account_info(user["idToken"])
            data = db.child("users").child(user_id).get()

            mail = request.form.get("email")
            password = request.form.get("password")
            card = request.form.get("card")
            exp = request.form.get("exp")

            user_check = auth.sign_in_with_email_and_password(mail, password)

            print(user_check)
            print(mail)
            if user["email"] == user_check["email"]:
                db.child("users").child(user_id).update({"isPremium": True})

            db.child("users").child(user["localId"]).set(data)

            # auth.send_email_verification(user['idToken'])
            session["user"] = user

            return render_template(
                "app.html",
                data=data,
                session=sessionUser,
                check=check,
                show_popup=False,
            )
        except Exception as e:
            print("Error", e, file=sys.stderr)
            return redirect(url_for("main"))


@app.route("/app/unsub", methods=["GET", "POST"])
def unsub():
    if request.method == "GET":
        try:
            check = True
            # get user data from current session
            user = session["user"]

            # only send data of the currently logged in user
            if user:
                user_id = user["localId"]
            sessionUser = auth.get_account_info(user["idToken"])
            data = db.child("users").child(user_id).get()

            db.child("users").child(user_id).update({"isPremium": False})

            db.child("users").child(user["localId"]).set(data)

            session["user"] = user

            return render_template(
                "app.html",
                data=data,
                session=sessionUser,
                check=check,
                show_popup=False,
            )
        except Exception as e:
            print("Error", e, file=sys.stderr)
            return redirect(url_for("main"))


if __name__ == "__main__":
    app.run(host="0.0.0.0")
