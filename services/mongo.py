from urlparse import urlparse
from os import environ
from pymongo import MongoClient

mongo_uri = environ.get("MONGOHQ_URL")

if mongo_uri:
  parsed = urlparse(mongo_uri)
  connection = MongoClient(mongo_uri)
  db = connection[parsed.path[1:]]
  db.authenticate(parsed.username, parsed.password)
else:
  connection = MongoClient()
  db = connection.fourkeeps

