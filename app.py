from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
from datetime import datetime
from dotenv import load_dotenv
from flask_cors import CORS

import certifi

load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB Setup
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    MONGO_URI = "mongodb://localhost:27017/webhook_db"

if 'localhost' in MONGO_URI:
     client = MongoClient(MONGO_URI)
else:
    # Use certifi for Atlas connections to avoid SSL errors
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())

# Use 'webhook_db' explicitly since Atlas connection string might not specify one
# Use 'webhook_db' explicitly since Atlas connection string might not specify one
db = client.webhook_db
events_collection = db.events

def get_ordinal_date_string(dt):
    suffix = 'th' if 11 <= dt.day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(dt.day % 10, 'th')
    return dt.strftime(f"{dt.day}{suffix} %B %Y - %I:%M %p UTC")

@app.route('/')
def home():
    return "GitHub Webhook Receiver is Running"

@app.route('/webhook/receiver', methods=['POST'])
def handle_github_webhook():
    data = request.json
    headers = request.headers
    event_type = headers.get('X-GitHub-Event')

    if not data:
        return jsonify({"msg": "Invalid payload"}), 400

    event_data = None
    
    # Common timestamp for all events
    # "1st April 2021 - 9:30 PM UTC"
    now = datetime.utcnow()
    timestamp_str = get_ordinal_date_string(now)

    if event_type == 'push':
        # Handle Push Event
        # Author: pusher.name or sender.login
        author = data.get('pusher', {}).get('name') or data.get('sender', {}).get('login')
        to_branch = data.get('ref', '').replace('refs/heads/', '')
        request_id = data.get('after') # commit hash

        event_data = {
            "request_id": request_id,
            "author": author,
            "action": "PUSH",
            "from_branch": "", # Not applicable for PUSH
            "to_branch": to_branch,
            "timestamp": timestamp_str
        }

    elif event_type == 'pull_request':
        action = data.get('action')
        pr = data.get('pull_request', {})
        author = pr.get('user', {}).get('login')
        from_branch = pr.get('head', {}).get('ref')
        to_branch = pr.get('base', {}).get('ref')
        request_id = str(pr.get('id'))

        if action == 'opened':
            # Handle PR Open
             event_data = {
                "request_id": request_id,
                "author": author,
                "action": "PULL_REQUEST",
                "from_branch": from_branch,
                "to_branch": to_branch,
                "timestamp": timestamp_str
            }
        
        elif action == 'closed' and pr.get('merged') is True:
            # Handle Merge (Bonus)
            # Detect merger
            merger = data.get('sender', {}).get('login') or author
            
            event_data = {
                "request_id": request_id,
                "author": merger,
                "action": "MERGE",
                "from_branch": from_branch,
                "to_branch": to_branch,
                "timestamp": timestamp_str
            }

    if event_data:
        try:
            # Schema Requirement: Only store fields required by the UI (and specified schema)
            # Schema: _id, request_id, author, action, from_branch, to_branch, timestamp
            events_collection.insert_one(event_data)
            return jsonify({"msg": "Event stored successfully"}), 201
        except Exception as e:
            print(f"Error saving to MongoDB: {e}")
            return jsonify({"msg": "Internal Server Error"}), 500

    return jsonify({"msg": "Event received but ignored"}), 200

@app.route('/events', methods=['GET'])
def get_events():
    try:
        # Fetch latest events, sorted by timestamp (latest first).
        # Since we are not storing a raw timestamp for strict schema compliance,
        # we rely on MongoDB ObjectId's natural creation time property for sorting.
        cursor = events_collection.find({}, {'_id': 0}).sort("_id", -1).limit(10)
        events = list(cursor)
        return jsonify(events), 200
    except Exception as e:
        print(f"Error fetching events: {e}")
        return jsonify({"msg": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
