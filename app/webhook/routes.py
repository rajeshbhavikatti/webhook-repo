from flask import Blueprint, json, request,render_template,redirect,jsonify,make_response
from app.extensions import mongo,db,hook,server_connect,suffix,convert,last_id
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
        merge = data["pull_request"]["merged"]
      except KeyError as ker:
        print(ker)
        action="pushed"
        author = data["pusher"]['name']
        from_branch = data["base_ref"]
        to_branch = data['ref']
        request_id = data["head_commit"]["id"]
        merge = "false"

      #timestamp = data["pull_request"]["created_at"]
      timestamp = datetime.datetime.now()
      
      print(request_id,action,author,from_branch,to_branch,merge)
      print(server_connect())
      
      #Adding Data to MongoDB
      db.webhook.insert_one({
        "request_id":request_id,
        "author":author,
        "action":action,
        "from_branch":from_branch,
        "to_branch":to_branch,
        "merge": merge,
        "timestamp":timestamp,})
    else:
      print("No data Received")
    return info, 200

@webhook.route('/ui',methods=["GET"])
def webhook_home():
  #getting data from webhook collection
  tasks=convert(hook.find().sort("timestamp",-1).limit(5))
  last = last_id(hook.find().sort("timestamp",-1).limit(1))
  global id 
  id = last[0]["_id"]
  print(last[0]["_id"])
  return render_template("base.html",Title="TRX Assessment",tasks=tasks,update=webhook_update)



@webhook.route('/ui/update',methods=["GET"])
def webhook_update():
  tasks=convert(hook.find({"_id":{"$gte":id}}).sort("timestamp",-1))
  page = render_template("base.html",Title="TRX Assessment",tasks=tasks,update=webhook_update)
  return {"task":page}
  