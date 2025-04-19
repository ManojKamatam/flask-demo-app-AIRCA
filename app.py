# Add to the top of app.py
import logging
from ddtrace import patch_all
patch_all()

from flask import Flask, request, jsonify, abort
import time
import random
import json
import os
import redis
from datetime import datetime
from config import Config
from database import db, get_products_with_category, slow_product_search, find_user_by_email, unsafe_raw_query
from models import User, Product, Category, Order, OrderItem
from utils import (
    simulate_memory_leak, 
    slow_external_api_call, 
    heavy_calculation, 
    sometimes_fails,
    start_background_task,
    timed_function
)

# Add to the top of app.py
from dynatrace.oneagent.sdk.python import OneAgentSDK

# Initialize Dynatrace SDK after Flask app creation
dynatrace_sdk = OneAgentSDK()

# Add custom request tracking 
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

def create_sample_data():
    # Create sample categories
    categories = [
        Category(name="Electronics"),
        Category(name="Books"),
        Category(name="Clothing")
    ]
    db.session.add_all(categories)
    db.session.commit()
    
    # Create sample products
    products = [
        Product(name="Laptop", description="High-performance laptop", price=999.99, stock=10, category_id=1),
        Product(name="Smartphone", description="Latest smartphone", price=699.99, stock=20, category_id=1),
        Product(name="Python Book", description="Learn Python programming", price=29.99, stock=50, category_id=2),
        Product(name="T-Shirt", description="Cotton t-shirt", price=19.99, stock=100, category_id=3),
    ]
    db.session.add_all(products)
    
    # Create sample users
    users = [
        User(username="alice", email="alice@example.com"),
        User(username="bob", email="bob@example.com")
    ]
    db.session.add_all(users)
    db.session.commit()
    
    # Create sample orders
    order = Order(user_id=1, total=1029.98, status="completed")
    db.session.add(order)
    db.session.commit()
    
    # Add order items
    items = [
        OrderItem(order_id=1, product_id=1, quantity=1, price=999.99),
        OrderItem(order_id=1, product_id=4, quantity=1, price=29.99)
    ]
    db.session.add_all(items)
    db.session.commit()
    
    logger.info("Sample data created successfully")

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
    
    user = find_user_by_email(email)
    if not user:
        abort(404, description="User not found")
    return jsonify(user.to_dict())

@app.route('/api/products', methods=['GET'])
@timed_function
def get_products():
    limit = request.args.get('limit', type=int)
    
    # Use the more efficient join query from the database module
    products = db.get_products_with_category(limit)
    
    # Occasional memory leak
    simulate_memory_leak()
    
    return jsonify(products)

@app.route('/api/products/search', methods=['GET'])
def search_products():
    keyword = request.args.get('keyword', '')
    
    # Use slow query if enabled in config
    if Config.SLOW_QUERY_ENABLED:
        products = slow_product_search(keyword)
    else:
        products = [p.to_dict() for p in Product.query.filter(Product.name.ilike(f'%{keyword}%')).all()]
    
    return jsonify(products)

@app.route('/api/products/unsafe-search', methods=['GET'])
def unsafe_search():
    # Vulnerability: directly passing user input to SQL query
    keyword = request.args.get('keyword', '')
    logger.warning("Unsafe raw query used with user input: %s", keyword)
    results = unsafe_raw_query(keyword)
    return jsonify(results)

@app.route('/api/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    return jsonify([order.to_dict() for order in orders])

@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        abort(404, description="Order not found")
    return jsonify(order.to_dict())

@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([category.to_dict() for category in categories])

@app.route('/api/slow-endpoint', methods=['GET'])
def slow_endpoint():
    # Simulate slow API response
    time.sleep(3)
    
    # Make a slow external API call
    external_data = slow_external_api_call()
    
    return jsonify({
        "message": "Slow endpoint response",
        "external_data": external_data
    })

@app.route('/api/cpu-intensive', methods=['GET'])
def cpu_intensive():
    # CPU-intensive calculation
    result = heavy_calculation()
    return jsonify({"result": result})

@app.route('/api/background-task', methods=['POST'])
def start_task():
    # Start a background task
    thread = start_background_task()
    return jsonify({"message": "Background task started"})

@app.route('/api/error-prone', methods=['GET'])
def error_prone():
    try:
        # Function that sometimes fails
        result = sometimes_fails()
        return jsonify({"message": result})
    except Exception as e:
        logger.error(f"Error in error_prone endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {str(e)}")
    return jsonify(error="Internal server error"), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))