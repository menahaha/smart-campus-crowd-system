print("Backend started") 
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb://localhost:27017/")
db = client["crowd_management"]
collection = db["crowd_data"]

@app.route("/")
def home():
    return "Crowd Management Backend Running"

if __name__ == "__main__":
    app.run(debug=True)