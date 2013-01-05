import bottle
import os
from services import venmo, foursquare

app = bottle.Bottle()

@app.route('/')
def index():
  return "FourKeeps. Bitch."

@app.get('/privacy')
def privacy():
  return "You have a sick sense of humor."

@app.route('/assets/<path:path>')
def static(path):
  return bottle.static_file(path, 'assets/')

app.mount("/venmo", venmo.application)
app.mount("/foursquare", foursquare.application)

port = os.environ.get('PORT', '3000')
app.run(host='0.0.0.0', port=port)

