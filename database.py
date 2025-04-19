from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Efficient query function using joins
def get_products_with_category(limit=None):
    from models import Product, Category
    
    query = Product.query.join(Category, Product.category_id == Category.id)
    if limit:
        query = query.limit(limit)
    
    products = query.all()
    
    return [{
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'stock': product.stock,
        'category_name': product.category.name
    } for product in products]

# A query that uses indexes properly
def slow_product_search(keyword):
    from models import Product
    import time
    
    # Simulate slow query processing
    time.sleep(2)
    
    # Efficient LIKE query with index
    products = Product.query.filter(Product.name.like(f'%{keyword}%')).all()
    
    return [p.to_dict() for p in products]

# Add index on user lookup
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