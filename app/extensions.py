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

def suffix(day):
    suffix = ""
    if 4 <= day <= 20 or 24 <= day <= 30:
      suffix = "th"
    else:
      suffix = ["st", "nd", "rd"][day % 10 - 1]
    return suffix
def convert(tasks): 
  logs=[]
  for task in tasks :
    task['_id'] = str(task['_id'])
    task['author']=str(task['author'])
    task['request_id']  = str(task['request_id']) 
    task['from_branch'] = str(task['from_branch'])
    task['to_branch'] = str(task['to_branch'])
    task['action'] = str(task['action'])
    task['merge'] = str(task['merge'])
    time = task['timestamp'] = task['timestamp'].strftime("%d{} %B %Y - %I:%M:%S %p %z UTC".format(suffix(task['timestamp'].day)))
    logs.append(task)
  return logs   

def last_id(tasks):
  last=[]
  for task in tasks: 
    last.append(task)
  return last