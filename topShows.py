from PyMovieDb import IMDB
import json
import os
from dotenv import load_dotenv
import pyrebase

imdb = IMDB()
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
    "serviceAccount": "/Users/margaretrivas/Desktop/cop4521/ShowTrack2/static/showtrac-1-firebase-adminsdk-ks879-0de599aff8.json",  # Authenticate as admin
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

topShows = imdb.popular_tv(start_id=1, sort_by="popularity.desc")

# convert to json dictionary from string object

top = json.loads(topShows)

for i in top["results"]:
    print(i)

# delete topShows from firebase
db.child("topShows").remove()

# add new data to firebase
db.child("topShows").set(top)
