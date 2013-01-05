import bottle
import os
import pystache
from services import venmo, foursquare

app = bottle.Bottle()
views = {}

def render_view(view, data):
  data = pystache.render(view, data)
  return pystache.render(views['layout'], {'page': data})

@app.route('/')
def index():
  return render_view('index', {})

@app.get('/privacy')
def privacy():
  return "You have a sick sense of humor."

@app.route('/assets/<path:path>')
def static(path):
  return bottle.static_file(path, 'assets/')

<<<<<<< HEAD
for (dirpath, _, filenames) in os.walk('views'):
  for fname in filenames:
    path = dirpath + '/' + fname
    view = open(path, 'r').read()
    name = path[6:]
    if name.endswith('.stache'): name = name[0:len(name)-7]
    views[name] = pystache.parse(unicode(view))
=======
app.mount("/venmo", venmo.application)
app.mount("/foursquare", foursquare.application)
>>>>>>> f92ec7ef79da2c59c52bb2068cd7e6a48f5549ac

port = os.environ.get('PORT', '3000')
app.run(host='0.0.0.0', port=port)

