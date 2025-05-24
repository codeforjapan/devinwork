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

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/api/credit-data')
def get_credit_data():
    """API endpoint to get the credit data."""
    data = load_credit_data()
    return jsonify(data)

@app.route('/api/latest-credit-data')
def get_latest_credit_data():
    """API endpoint to get the latest credit data."""
    data = load_credit_data()
    if data:
        return jsonify(data[-1])
    return jsonify({})

if __name__ == '__main__':
    port = int(os.getenv("PORT", "5000"))
    app.run(host='0.0.0.0', port=port, debug=True)
