import logging
from os import environ

import bottle
import requests
from services.mongo import db

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

  token = token_request.json()['access_token']

  user_request = requests.get("https://api.foursquare.com/v2/users/self", params={"oauth_token": token})
  user = user_request.json()['response']['user']

  users = db.users
  users.insert({"foursquare_token": token,
                "foursquare_id": user['id'],
                "foursquare_contact": user['contact']})

@app.post("/push")
def handle_checkin():
  push = bottle.request.json
  if push['secret'] != environ['FOURSQUARE_PUSH_SECRET']:
    return

  checkin = push['checkin']
  user_id = checkin['user']['id']
  venue_id = checkin['venue']['id']

  logging.info("user %s venue %s", user_id, venue_id)

def retrieve_venue(venue_id):

  venue = db.venues.find_one({"foursquare_id": venue_id})
  if venue:
    pass # test to see if one of your friends owns this
  else:
    pass # create the venue, mark for sale


application = app
