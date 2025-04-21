from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()

# Optimized query that uses joins
def get_products_with_category_optimized(limit=None):
    from models import Product, Category
    
    query = db.session.query(Product, Category).join(Category).limit(limit).all() if limit else db.session.query(Product, Category).join(Category).all()
    
    result = []
    for product, category in query:
        product_dict = product.to_dict()
        product_dict['category_name'] = category.name
        result.append(product_dict)
    
    return result

# Optimized query that uses indexes
def product_search_optimized(keyword):
    from models import Product
    from sqlalchemy import or_
    
    # Use indexed column search
    products = Product.query.filter(
        or_(Product.name.ilike(f'%{keyword}%'), Product.description.ilike(f'%{keyword}%'))
    ).all()
    
    return [p.to_dict() for p in products]

# Index added to user email column
def find_user_by_email_indexed(email):
    from models import User
    return User.query.filter_by(email=email).first()

# Safe raw query to prevent SQL injection
def safe_raw_query(user_input):
    query = text(f"SELECT * FROM product WHERE name LIKE '%{user_input}%' ESCAPE '\\'")
    result = db.session.execute(query)
    
    return [dict(row._mapping) for row in result]