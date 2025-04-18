from flask_sqlalchemy import SQLAlchemy
from models import Product

db = SQLAlchemy()

# Efficient query function with joins
def get_products_with_category(limit=None):
    products = Product.query.options(db.joinedload('category')).limit(limit).all() if limit else Product.query.options(db.joinedload('category')).all()
    return [p.to_dict() for p in products]

# A slow query that doesn't use indexes properly
def slow_product_search(keyword):
    from models import Product
    import time
    
    # Simulate slow query processing
    time.sleep(2)
    
    # Inefficient LIKE query without index
    products = Product.query.filter(
        (Product.name.like(f'%{keyword}%')) | 
        (Product.description.like(f'%{keyword}%'))
    ).all()
    
    return [p.to_dict() for p in products]

# Add indexes for user lookup
def find_user_by_email(email):
    from models import User
    return User.query.filter_by(email=email).first()

# Vulnerable to SQL injection (for demonstration only)
def unsafe_raw_query(user_input):
    from sqlalchemy import text
    
    # WARNING: This is deliberately unsafe!
    query = text(f"SELECT * FROM product WHERE name LIKE '%{user_input}%'")
    result = db.session.execute(query)
    
    return [dict(row._mapping) for row in result]