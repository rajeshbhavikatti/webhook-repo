from flask import Blueprint, json, request,render_template,redirect
from app.extensions import mongo,db,hook
from flask_pymongo import PyMongo
import datetime

webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

@webhook.route('/receiver', methods=["POST"])
def receiver():
    if request.headers["Content-Type"]  ==  "application/json":
      info = json.dumps(request.json)
      #Getting the webhook data in form of dictionary
      data = request.json 
      #declaring variables for MongoDB
      action = data["action"]
      author = data["pull_request"]["user"]["login"]
      to_branch = data["pull_request"]["base"]["ref"]
      from_branch = data["pull_request"]["head"]["ref"]
      #timestamp = data["pull_request"]["created_at"]
      timestamp = datetime.datetime.now()
      request_id = data["pull_request"]["id"]
      print(request_id,action,author,from_branch,to_branch)
      
      
      #prevIndex=users.count_documents({})
      #Adding Data to MongoDB
      hook.insert_one({
        "request_id":request_id,
        "author":author,
        "action":action,
        "from_branch":from_branch,
        "to_branch":to_branch,
        "timestamp":timestamp,
        #"dateTime":datetime.datetime.now(),
        #"index":prevIndex+1,
      })
    else:
      info = "Fail"
    print(info)
    return info, 200

@webhook.route('/')
def webhook_home():
  tasks=[]
  def suffix(day):
    suffix = ""
    if 4 <= day <= 20 or 24 <= day <= 30:
      suffix = "th"
    else:
      suffix = ["st", "nd", "rd"][day % 10 - 1]
    return suffix

  for task in hook.find().sort("timestamp"):
    task['author']=str(task['author'])
    task['request_id']  = str(task['request_id']) 
    task['from_branch'] = str(task['from_branch'])
    task['to_branch'] = str(task['to_branch'])
    task['action'] = str(task['action'])
    print(task['action'])
    time = task['timestamp'] = task['timestamp'].strftime("%d{} %B %Y".format(suffix(task['timestamp'].day)))
    #time = task['timestamp']
    #time = task['timestamp'].strftime("%b %d" + suffix(timestamp.day))
    tasks.append(task)
    
  return render_template("base.html",Title="TRX Assessment",tasks=tasks)
