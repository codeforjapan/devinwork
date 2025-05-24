#!/usr/bin/env python3
"""
Web application for displaying Devin credit usage data.
"""

import os
import json
import secrets
from datetime import datetime
from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
from dotenv import load_dotenv
from src.scraper.scraper import DevinCreditScraper

# Load environment variables
load_dotenv()

app = Flask(__name__, 
            template_folder=os.path.abspath('templates'),
            static_folder=os.path.abspath('static'))

app.secret_key = os.getenv("FLASK_SECRET_KEY", secrets.token_hex(16))

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

def is_admin():
    """Check if the current session user is an admin."""
    return session.get('is_admin', False)

@app.route('/')
def index():
    """Render the main page."""
    organization = os.getenv("ORGANIZATION_NAME", "Organization")
    return render_template('index.html', organization=organization)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle login requests."""
    if request.method == 'POST':
        step = request.form.get('step', '1')
        
        if step == '1':
            user_id = request.form.get('user_id')
            
            if not user_id:
                return render_template('login.html', error="User ID is required", step=1)
            
            session['user_id'] = user_id
            return render_template('login.html', step=2, user_id=user_id)
            
        elif step == '2':
            confirmation_code = request.form.get('confirmation_code')
            
            if not confirmation_code:
                return render_template('login.html', error="Confirmation code is required", 
                                     step=2, user_id=session.get('user_id'))
            
            session['confirmation_code'] = confirmation_code
            session['logged_in'] = True
            
            admin_user = os.getenv("ADMIN_USER", "false").lower() == "true"
            session['is_admin'] = admin_user
            
            return redirect(url_for('index'))
    
    return render_template('login.html', step=1)

@app.route('/logout')
def logout():
    """Handle logout requests."""
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/run-scrape', methods=['POST'])
def run_scrape():
    """API endpoint to manually run the scraper (admin only)."""
    if not is_admin():
        return jsonify({"success": False, "error": "Admin access required"})
    
    if not session.get('logged_in'):
        return jsonify({"success": False, "error": "Authentication required"})
    
    try:
        scraper = DevinCreditScraper()
        
        scraper.username = session.get('user_id')
        os.environ["DEVIN_CONFIRMATION_CODE"] = session.get('confirmation_code')
        
        success = scraper.run()
        
        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Scraper failed to run"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

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
