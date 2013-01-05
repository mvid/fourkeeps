from os import environ

import bottle
import requests
from services.mongo import db
import json
from util import views
from pymongo import objectid

RENT_COST = "0.05"

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

  user_id = db.users.insert({"foursquare_token": token,
                             "foursquare_id": user['id'],
                             "name": user['firstName'] + ' ' + user['lastName'],
                             "foursquare_contact": user['contact'],
                             "owned_venue_ids": []})

  if game = fetch_game_for_user(user_id):
    # All set, say thanks
    game_users = db.users.find({'_id': game['user_ids']}, fields=['name'])
    return views.render_view('thanks', {'name': user['firstName'], 'users': game_users})
  else:
    # Make a new game
    game_id = objectid.ObjectId()
    return views.render_view('create_game', {
      'name': user['firstName'],
      'game_id': str(game_id),
      'base_url': environ['BASE_URL']
      })

def fetch_game_for_user(user_id):
  return db.games.find_one({'user_ids': user_id})


@app.post("/push")
def handle_checkin():
  push = bottle.request.params
  if push['secret'] != environ['FOURSQUARE_PUSH_SECRET']:
    return

  checkin = json.loads(push['checkin'])
  foursquare_user = checkin['user']
  foursquare_venue = checkin['venue']

  user = db.users.find_one({"foursquare_id": foursquare_user['id']})
  assert user
  if not user.get('game_id'):
    return # no game assigned to user

  retrieved_venue_id = retrieve_venue(foursquare_venue)
  owner = venue_owner(user['game_id'], retrieved_venue_id)

  if not owner:
    user['owned_venue_ids'].append(retrieved_venue_id)
    db.users.save(user)
    write_to_checkin(checkin['id'], user, "You just bought a venue!")
  else:
    contact_info = owner['foursquare_contact']
    contact_method = contact_info.get('email') or contact_info.get("phone") or None
    if contact_method:
      note = "Rent on %s" % checkin['venue']['name']
      venmo_url = "https://venmo.com/?txn=charge&amount=%s&note=%s&recipients=%s" % (RENT_COST, note, contact_method)
      write_to_checkin(checkin['id'], user, "Pay rent!", venmo_url)

def write_to_checkin(checkin_id, user, text, url=None):
  payload = {"text": text,
             "url": url,
             "oauth_token": user['foursquare_token']}
  if url:
    payload['url'] = url
  return requests.post("https://api.foursquare.com/v2/checkins/%s/reply" % checkin_id,
                       params=payload)

def retrieve_venue(venue):
  existing_venue = db.venues.find_one({"foursquare_id": venue['id']})
  if existing_venue:
    return existing_venue['_id']
  else:
    id = db.venues.insert({"foursquare_id": venue['id'],
                           "foursquare_name": venue['name']})
    return id

def venue_owner(game_id, venue_id):
  return db.users.find_one({"game_id": game_id,
                            "owned_venue_ids": {"$in": venue_id}})

application = app
