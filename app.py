import bottle
import os

app = bottle.Bottle()

@app.route('/')
def index():
  return "FourKeeps. Bitch."



port = os.environ.get('PORT', '3000')
app.run(host='0.0.0.0', port=port)