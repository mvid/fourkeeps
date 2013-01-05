import bottle
import os
from services import foursquare
from util import views

app = bottle.Bottle()

@app.route('/')
def index():
  return views.render_view('index', {
    'client_id': os.environ['FOURSQUARE_CLIENT_ID'],
    'redirect_uri': os.environ['FOURSQUARE_REDIRECT_URI']
    })

@app.get('/privacy')
def privacy():
  return "You have a sick sense of humor."

@app.route('/assets/<path:path>')
def static(path):
  return bottle.static_file(path, 'assets/')

# service points
app.mount("/foursquare", foursquare.application)

bottle.debug()

port = os.environ.get('PORT', '3000')
app.run(host='0.0.0.0', port=port)

