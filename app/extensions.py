from flask_pymongo import PyMongo
from flask import Flask
from pymongo import MongoClient
import os
#mongo_uri_details in .env file as mongo_uri_details="your id"
mg_uri = os.environ.get("mongo_uri_details")
#creating a client
mongo = MongoClient(mg_uri,serverSelectionTimeoutMS=5000)
#create a database as "data" and collection as "webhook" using mongoDB site
#get database and collection
db = mongo.get_database("data") 
hook = db.get_collection("webhook")

#getting server details
def server_connect():
  try:
    db_details=mongo.server_info()
  except Exception:
    db_details = "Unable to connect to the server."
  return db_details