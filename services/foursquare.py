from os import environ

import bottle
import requests
from services.mongo import db
import json
from util import views
import bson
from urllib import quote
import itertools

RENT_COST = "5.00"

app = bottle.Bottle()

@app.get("/")
def oauth_endpoint():
  code = bottle.request.query['code']
  game_id = bottle.request.query.get('game_id')
  game_found = True
  if not game_id:
    game_id = bson.ObjectId()
    game_found = False
  else:
    game_id = bson.ObjectId(game_id)

  new_game = bottle.request.query.get('new_game')

  token_request = requests.get("https://foursquare.com/oauth2/access_token",
                      params={"client_id": environ['FOURSQUARE_CLIENT_ID'],
                              "client_secret": environ['FOURSQUARE_CLIENT_SECRET'],
                              "grant_type": "authorization_code",
                              "redirect_uri": environ['FOURSQUARE_REDIRECT_URI'],
                              "code": code})

  if token_request.json().get('error'):
    return views.render_view('error', {'error': 'Failed to authenticate with foursquare.'})

  token = token_request.json()['access_token']

  user_request = requests.get("https://api.foursquare.com/v2/users/self", params={"oauth_token": token})
  user = user_request.json()['response']['user']

  user_id = None
  mongo_user = db.users.find_one({"foursquare_id": user['id']})
  if not mongo_user:
    print "IN NEW USER PATH"
    user_id = db.users.insert({"foursquare_token": token,
                               "foursquare_id": user['id'],
                               "name": user['firstName'] + ' ' + user['lastName'],
                               "foursquare_contact": user['contact'],
                               "game_id": game_id,
                               "owned_venue_ids": []})
  elif new_game:
    print "IN NEW GAME PATH"
    mongo_user['owned_venue_ids'] = []
    mongo_user['game_id'] = bson.ObjectId()
    db.users.save(mongo_user)
    return views.render_view('create_game', {
      'name': mongo_user['name'],
      'base_url': environ['BASE_URL'],
      'game_id': str(mongo_user['game_id'])
      })

  if game_found:
    print "IN CHANGE GAME PATH"
    if mongo_user: user_id = mongo_user['_id']
    db.users.update({'_id': user_id}, {'$set': {'owned_venue_ids': [], 'game_id': game_id}})
    friends = db.users.find({'game_id': game_id}, fields=['name'])
    return views.render_view('thanks', {
      'name': user['firstName'],
      'users': friends
      })
  elif mongo_user:
    print "IN DASHBOARD PATH"
    return show_dashboard_for_user(mongo_user)
  else:
    print "IN NEW USER NEW GAME PATH"
    return views.render_view('create_game', {
      'name': user['firstName'],
      'game_id': str(game_id),
      'base_url': environ['BASE_URL']
      })

def show_dashboard_for_user(user):
  friends = list(db.users.find({'game_id': user['game_id']}))
  venues = list(itertools.chain(*map(lambda x: x['owned_venue_ids'], friends)))
  venues = db.venues.find({'_id': {'$in': venues}})
  venues_by_id = {}
  for venue in venues:
    venues_by_id[venue['_id']] = venue
  data = []
  for friend in friends:
    obj = {
      'name': friend['name'],
      'venues': ", ".join(map(lambda x: venues_by_id[x]['foursquare_name'], friend['owned_venue_ids']))
      }
    data.append(obj)

  redirect_uri = quote(environ['FOURSQUARE_REDIRECT_URI'] + '?new_game=1')
  return views.render_view('dashboard', {
    'data': data,
    'client_id': environ['FOURSQUARE_CLIENT_ID'],
    'redirect_uri': redirect_uri,
    'base_url': environ['BASE_URL'],
    'game_id': str(user['game_id'])
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
      venmo_url = "https://venmo.com/?txn=charge&amount=%s&note=%s&recipients=%s" % (RENT_COST, quote(note), contact_method)
      write_to_checkin(checkin['id'], user, "Pay rent!", venmo_url)
    else:
      note = "The landlord didn't leave any contact info. You got lucky."
      write_to_checkin(checkin['id'], user, note)

def write_to_checkin(checkin_id, user, text, url=None):
  payload = {"text": text,
             "url": url,
             "oauth_token": user['foursquare_token'],
             "v": "20130105"}
  response = requests.post("https://api.foursquare.com/v2/checkins/%s/reply" % checkin_id,
                          params=payload)
  return response

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
                            "owned_venue_ids": venue_id})

application = app
