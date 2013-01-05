from bottle import route, run
import os

@route('/')
def index():
  return "FourKeeps. Bitch."

port = os.environ.get('PORT', '3000')
run(host='0.0.0.0', port=port)

