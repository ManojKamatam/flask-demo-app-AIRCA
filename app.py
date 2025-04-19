# Add to the top of app.py
from ddtrace import patch_all
patch_all()
from flask import Flask, request, jsonify, abort
import time
import random
import logging
import json
import os
import redis
from datetime import datetime
from config import Config
from database import db, get_products_with_category_optimized, safe_product_search, find_user_by_email_indexed, safe_raw_query
from models import User, Product, Category, Order, OrderItem
from utils import (
    heavy_calculation, 
    start_background_task,
    timed_function
)
# Add to the top of app.py
from dynatrace.oneagent.sdk.python import OneAgentSDK

# Initialize Dynatrace SDK after Flask app creation
dynatrace_sdk = OneAgentSDK()

# Optionally add custom request tracking 
@app.before_request
def before_request():
   request.dynatrace_tracer = dynatrace_sdk.trace_incoming_web_request(
      url=request.url,
     method=request.method,
    headers=dict(request.headers)
 )
    request.dynatrace_tracer.start()

@app.after_request
def after_request(response):
    if hasattr(request, 'dynatrace_tracer'):
        request.dynatrace_tracer.end(response.status_code)
    return response

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Initialize Redis connection
try:
    redis_client = redis.from_url(Config.REDIS_URL)
except redis.ConnectionError:
    logger.warning("Redis connection failed, caching disabled")
    redis_client = None

@app.before_first_request
def initialize_database():
    db.create_all()
    # Add sample data if database is empty
    if not User.query.first():
        create_sample_data()

# ... (create_sample_data function remains the same) ...

@app.route('/api/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})

@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        abort(404, description="User not found")
    return jsonify(user.to_dict())

@app.route('/api/users/search', methods=['GET'])
def search_user_by_email():
    email = request.args.get('email')
    if not email:
        abort(400, description="Email parameter is required")
    
    user = find_user_by_email_indexed(email)
    if not user:
        abort(404, description="User not found")
    return jsonify(user.to_dict())

@app.route('/api/products', methods=['GET'])
@timed_function
def get_products():
    limit = request.args.get('limit', type=int)
    
    # Use the optimized query function that avoids N+1 problem
    products = get_products_with_category_optimized(limit)
    
    return jsonify(products)

@app.route('/api/products/search', methods=['GET'])
def search_products():
    keyword = request.args.get('keyword', '')
    
    # Use optimized query with proper indexing
    products = safe_product_search(keyword)
    
    return jsonify(products)

@app.route('/api/products/unsafe-search', methods=['GET'])
def unsafe_search():
    # Use safe query to prevent SQL injection
    keyword = request.args.get('keyword', '')
    results = safe_raw_query(keyword)
    return jsonify(results)

# ... (remaining endpoints remain the same) ...

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))