from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

db = SQLAlchemy()

# Optimized query using joins
def get_products_with_category_optimized(limit=None):
    from models import Product, Category
    
    query = Product.query.join(Category, Product.category_id == Category.id)
    
    if limit:
        query = query.limit(limit)
    
    products = query.all()
    
    result = [
        {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'stock': product.stock,
            'category_id': product.category_id,
            'category_name': product.category.name,
            'created_at': product.created_at.isoformat()
        }
        for product in products
    ]
    
    return result

# Optimized query using indexes
def slow_product_search_optimized(keyword):
    from models import Product
    import time
    
    # Simulate slow query processing
    time.sleep(2)
    
    # Efficient LIKE query with index
    products = Product.query.filter(
        Product.name.ilike(f'%{keyword}%')
    ).all()
    
    return [p.to_dict() for p in products]

# Using index on user lookup
def find_user_by_email_optimized(email):
    from models import User
    return User.query.filter(func.lower(User.email) == email.lower()).first()

# Vulnerable to SQL injection (for demonstration only)
def unsafe_raw_query(user_input):
    from sqlalchemy import text
    
    # WARNING: This is deliberately unsafe!
    query = text(f"SELECT * FROM product WHERE name LIKE '%{user_input}%'")
    result = db.session.execute(query)
    
    return [dict(row._mapping) for row in result]