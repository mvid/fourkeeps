from bottle import route, run, get
import os

@route('/')
def index():
  return "FourKeeps. Bitch."

@get('/privacy')
def privacy():
  return "You have a sick sense of humor."

port = os.environ.get('PORT', '3000')
run(host='0.0.0.0', port=port)

