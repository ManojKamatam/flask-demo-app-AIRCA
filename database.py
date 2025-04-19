from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()

# Efficient query function using joins
def get_products_with_category(limit=None):
    from models import Product, Category
    
    # Use a join to fetch products and categories in a single query
    query = Product.query.join(Category, Product.category_id == Category.id)
    
    if limit:
        query = query.limit(limit)
    
    products = query.all()
    
    result = []
    for product in products:
        result.append({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'stock': product.stock,
            'category_id': product.category_id,
            'category_name': product.category.name,
            'created_at': product.created_at.isoformat()
        })
    
    return result

# Use indexes for efficient query
def slow_product_search(keyword):
    from models import Product
    import time
    
    # Simulate slow query processing
    time.sleep(2)
    
    # Use index on name and description columns
    products = Product.query.filter(
        (Product.name.ilike(f'%{keyword}%')) | 
        (Product.description.ilike(f'%{keyword}%'))
    ).all()
    
    return [p.to_dict() for p in products]

# Add index on email column
def find_user_by_email(email):
    from models import User
    return User.query.filter_by(email=email).first()

# Vulnerable to SQL injection (for demonstration only)
def unsafe_raw_query(user_input):
    # WARNING: This is deliberately unsafe!
    query = text(f"SELECT * FROM product WHERE name LIKE '%{user_input}%'")
    result = db.session.execute(query)
    
    return [dict(row._mapping) for row in result]