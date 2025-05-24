#!/usr/bin/env python3
"""
Web application for displaying Devin credit usage data.
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, 
            template_folder=os.path.abspath('templates'),
            static_folder=os.path.abspath('static'))

def load_credit_data():
    """Load the credit data from the JSON file."""
    data_file = os.path.join("data", "credit_data.json")
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            return json.load(f)
    return []

def process_credit_data(data):
    """Process the raw credit data into a format suitable for the UI."""
    processed_data = []
    
    for entry in data:
        timestamp = entry.get("timestamp", "")
        
        current_usage = entry.get("current_usage", {})
        available_acus = current_usage.get("available_acus", "Unknown")
        
        usage_history = entry.get("usage_history", [])
        
        processed_entry = {
            "timestamp": timestamp,
            "available_acus": available_acus,
            "usage_history": usage_history
        }
        
        processed_data.append(processed_entry)
    
    return processed_data

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/api/credit-data')
def get_credit_data():
    """API endpoint to get all credit data."""
    data = load_credit_data()
    processed_data = process_credit_data(data)
    return jsonify(processed_data)

@app.route('/api/latest-credit-data')
def get_latest_credit_data():
    """API endpoint to get the latest credit data."""
    data = load_credit_data()
    if data:
        processed_data = process_credit_data([data[-1]])
        return jsonify(processed_data[0])
    return jsonify({})

@app.route('/api/usage-history')
def get_usage_history():
    """API endpoint to get the usage history from the latest data."""
    data = load_credit_data()
    if data and len(data) > 0:
        latest_data = data[-1]
        usage_history = latest_data.get("usage_history", [])
        return jsonify(usage_history)
    return jsonify([])

if __name__ == '__main__':
    port = int(os.getenv("PORT", "5000"))
    app.run(host='0.0.0.0', port=port, debug=True)
