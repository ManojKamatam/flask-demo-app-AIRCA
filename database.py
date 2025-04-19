from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from models import Product, Category

db = SQLAlchemy()

# Optimized query function that uses joins
def get_products_with_category_optimized(limit=None):
    query = db.session.query(Product, Category).join(Category, Product.category_id == Category.id)
    if limit:
        query = query.limit(limit)
    
    products = []
    for product, category in query:
        product_dict = product.to_dict()
        product_dict['category_name'] = category.name
        products.append(product_dict)
    
    return products

# Query with proper indexing
def safe_product_search(keyword):
    from models import Product
    
    # Query with indexes on name and description columns
    products = Product.query.filter(
        (Product.name.like(f'%{keyword}%')) | 
        (Product.description.like(f'%{keyword}%'))
    ).all()
    
    return [p.to_dict() for p in products]

# User lookup with index on email column
def find_user_by_email_indexed(email):
    from models import User
    return User.query.filter_by(email=email).first()

# Safe query to prevent SQL injection
def safe_raw_query(user_input):
    from sqlalchemy import text
    
    query = text(f"SELECT * FROM product WHERE name LIKE :keyword")
    result = db.session.execute(query, {"keyword": f"%{user_input}%"})
    
    return [dict(row._mapping) for row in result]