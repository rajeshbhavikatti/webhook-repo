from flask import Blueprint, json, request,render_template,redirect
from app.extensions import mongo,db,logs,server_connect
from flask_pymongo import PyMongo
import datetime

webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

@webhook.route('/receiver', methods=["POST"])
def receiver():
    if request.headers["Content-Type"]  ==  "application/json":
      info = json.dumps(request.json)
      print(info)
      #Getting the webhook data in form of dictionary
      data = request.json 
      #declaring variables for MongoDB
      try:
        action = data["action"]
        author = data["pull_request"]["user"]["login"]
        to_branch = data["pull_request"]["base"]["ref"]
        from_branch = data["pull_request"]["head"]["ref"]
        request_id = data["pull_request"]["id"]
      except KeyError: #when data[action] is not present
        action="pushed"
        author = data["pusher"]['name']
        from_branch = data["base_ref"]
        to_branch = data['ref']
        request_id = data["head_commit"]["id"]
      except: #when data has different values
        print("No proper Data")

      timestamp = datetime.datetime.now()
      
      print(request_id,action,author,from_branch,to_branch)
      print(server_connect())
      
      #Adding Data to MongoDB
      db.webhook.insert_one({
        "request_id":request_id,
        "author":author,
        "action":action,
        "from_branch":from_branch,
        "to_branch":to_branch,
        "timestamp":timestamp,})
    else:
      print("No data Received")
    return info, 200

@webhook.route('/ui',methods=["GET"])
def webhook_home():
  tasks=[]
  def suffix(day):
    suffix = ""
    if 4 <= day <= 20 or 24 <= day <= 30:
      suffix = "th"
    else:
      suffix = ["st", "nd", "rd"][day % 10 - 1]
    return suffix
  #getting data from webhook collection
  for task in logs.find().sort("timestamp",-1):
    task['author']=str(task['author'])
    task['request_id']  = str(task['request_id']) 
    task['from_branch'] = str(task['from_branch'])
    task['to_branch'] = str(task['to_branch'])
    task['action'] = str(task['action'])
    time = task['timestamp'] = task['timestamp'].strftime("%d{} %B %Y - %I %M:%p %z UTC".format(suffix(task['timestamp'].day)))
    tasks.append(task)
  for task in tasks:
    print(task['action'],time)
    
  return render_template("base.html",Title="TRX Assessment",tasks=tasks)
