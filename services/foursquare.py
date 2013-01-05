import bottle
import requests

app = bottle.Bottle()

@app.get("/")
def oauth_endpoint():
  code = bottle.request.query['code']
  user = requests.get("https://foursquare.com/oauth2/access_token", )

application = app