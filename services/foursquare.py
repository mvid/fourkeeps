from os import environ

import bottle
from pymongo import MongoClient
import requests

app = bottle.Bottle()

@app.get("/")
def oauth_endpoint():
  code = bottle.request.query['code']
  token_request = requests.get("https://foursquare.com/oauth2/access_token",
                      params={"client_id": environ['FOURSQUARE_CLIENT_ID'],
                              "client_secret": environ['FOURSQUARE_CLIENT_SECRET'],
                              "grant_type": "authorization_code",
                              "redirect_uri": environ['FOURSQUARE_REDIRECT_URI'],
                              "code": code})

  token = token_request.json['token']

  user_request = requests.get("https://api.foursquare.com/v2/users/self", params={"oauth_token": token})
  user = user_request.json['response']['user']

  connection = MongoClient(environ.get("MONGO_HOST", ""), environ.get("MONGO_PORT", 27017))
  db = connection.fourkeeps
  users = db.users
  users.insert({"foursquare_token": token,
                "foursquare_id": user['id'],
                "foursquare_contact": user['contact']})

application = app