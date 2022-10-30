from flask import Blueprint, json, request,render_template,redirect,jsonify,make_response
from app.extensions import mongo,db,hook,server_connect,suffix,convert,last_id
from flask_pymongo import PyMongo
import datetime

webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

@webhook.route('/receiver', methods=["POST"])
def receiver():
    """Receive the data from Github webhook and Insert the data into mongoDB"""
    if request.headers["Content-Type"]  ==  "application/json":           #check if received content type is json type
      info = json.dumps(request.json) #set variable to received data
      #print(info)                    #check received data
      data = request.json             #Getting the webhook data in form of dictionary                                
      try:
        """#assigning variables to received data for tansfering into MongoDB"""
        action = data["action"]                            #which action is performed
        author = data["pull_request"]["user"]["login"]     #author of the action
        to_branch = data["pull_request"]["base"]["ref"]    #to which branch the action is performed
        from_branch = data["pull_request"]["head"]["ref"]  #from which branch the action is performed
        request_id = data["pull_request"]["id"]            #id of the action performed
        merge = data["pull_request"]["merged"]             #Boolean value of merge request
      except KeyError as ker:
        """Handling error if the received data does not have required data"""
        #print(ker)                                        #verify error
        action="pushed"                                    #if there is no data on action then action is set to pushed
        author = data["pusher"]['name']                    #author of action
        from_branch = data["base_ref"]                     #from branch of the action
        to_branch = data['ref']                            #to branch of the action
        request_id = data["head_commit"]["id"]             #id of the action
        merge = "false"                                    #False for merge as no merge operation is being performed

      timestamp = datetime.datetime.now()                  #variable for time
      
      print(request_id,action,author,from_branch,to_branch,merge)      #verify variables value
      print(server_connect())                                          #verify mongodb connection
      
      #Adding Data to MongoDB
      db.webhook.insert_one({
        "request_id":request_id,                 #insert request_id variable into mongodb as request_id
        "author":author,
        "action":action,
        "from_branch":from_branch,
        "to_branch":to_branch,
        "merge": merge,
        "timestamp":timestamp,})
    else:
      print("No data Received")                  #if the data received is incorrect
    return info, 200                              

@webhook.route('/ui',methods=["GET"])
def webhook_home():
  """retriving data from mongodb to create a ui
  return latest 5 mongodb entries to render as HTML 
  """
  #getting data from webhook collection
  tasks=convert(hook.find().sort("timestamp",-1).limit(5))    #retrive latest 3 entries in hook collection and converting it into list
  last = last_id(hook.find().sort("timestamp",-1).limit(1))   #retrive last id from mongodb 
  global id 
  id = last[0]["_id"]                                         #assigning last id as global variable id
  #print(last[0]["_id"])                                       #verify id
  return render_template("base.html",Title="TRX Assessment",tasks=tasks)   



@webhook.route('/ui/update',methods=["GET"])
def webhook_update():
  """return HTML content with mongodb content whose id are greater than global variable id"""
  
  tasks=convert(hook.find({"_id":{"$gte":id}}).sort("timestamp",-1))        #retrieve entries whose id is greater than global id and convert it into list
  page = render_template("base.html",Title="TRX Assessment",tasks=tasks)    #convert the list into HTML format
  return {"task":page}
  