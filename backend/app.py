# ============================================================
# Smart Campus Crowd Management System - Backend
# Tech Stack: Python, Flask, MongoDB, PyMongo, Flask-CORS
# ============================================================

from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime, timezone

# ============================================================
# App Initialization
# ============================================================

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for all routes

# ============================================================
# MongoDB Connection
# Database  : crowd_management
# Collection: crowd_data
# ============================================================

try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["crowd_management"]
    crowd_collection = db["crowd_data"]
    print("✅ Connected to MongoDB successfully.")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")


# ============================================================
# API 1: Home Route
# GET /
# Returns a simple status message confirming the server is up.
# ============================================================

@app.route("/", methods=["GET"])
def home():
    return "Smart Campus Crowd Backend Running", 200


# ============================================================
# API 2: Add Crowd Data
# POST /add_crowd
# Accepts JSON: { "location": "canteen", "count": 120 }
# Stores location, count, and current UTC timestamp in MongoDB.
# ============================================================

@app.route("/add_crowd", methods=["POST"])
def add_crowd():
    try:
        data = request.get_json()

        # Validate that required fields are present
        if not data or "location" not in data or "count" not in data:
            return jsonify({"error": "Missing required fields: 'location' and 'count'"}), 400

        location = data["location"]
        count = data["count"]

        # Validate types
        if not isinstance(location, str) or not location.strip():
            return jsonify({"error": "'location' must be a non-empty string"}), 400
        if not isinstance(count, (int, float)) or count < 0:
            return jsonify({"error": "'count' must be a non-negative number"}), 400

        # Build the document to insert
        crowd_entry = {
            "location": location.strip().lower(),  # Normalize location to lowercase
            "count": int(count),
            "timestamp": datetime.now(timezone.utc).isoformat()  # ISO 8601 UTC timestamp
        }

        # Insert into MongoDB
        crowd_collection.insert_one(crowd_entry)

        return jsonify({"message": "Crowd data added successfully"}), 201

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


# ============================================================
# API 3: Get All Live Crowd Data
# GET /live_crowd
# Returns all crowd records from MongoDB, excluding the _id field.
# ============================================================

@app.route("/live_crowd", methods=["GET"])
def live_crowd():
    try:
        # Fetch all records, exclude MongoDB's internal _id field
        records = list(crowd_collection.find({}, {"_id": 0}))

        return jsonify(records), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


# ============================================================
# API 4: Get Crowd History for a Specific Location
# GET /history/<location>
# Example: GET /history/canteen
# Returns all crowd records for the given location.
# ============================================================

@app.route("/history/<string:location>", methods=["GET"])
def crowd_history(location):
    try:
        # Normalize location to lowercase to match stored data
        normalized_location = location.strip().lower()

        # Query MongoDB for all records matching the location
        records = list(
            crowd_collection.find(
                {"location": normalized_location},
                {"_id": 0}  # Exclude _id from results
            )
        )

        if not records:
            return jsonify({"message": f"No crowd data found for location: '{normalized_location}'", "data": []}), 200

        return jsonify(records), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


# ============================================================
# Run the Flask Development Server
# ============================================================

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)