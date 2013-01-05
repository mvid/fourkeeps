from os import environ
from pymongo import MongoClient

connection = MongoClient(environ.get("MONGO_HOST", "localhost"), environ.get("MONGO_PORT", 27017))
db = connection.fourkeeps