from os import environ
from pymongo import MongoClient

mongo_uri = environ.get("MONGOHQ_URL")

if mongo_uri:
  connection = MongoClient(mongo_uri)
else:
  connection = MongoClient()

db = connection.fourkeeps