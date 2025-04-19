from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from models import Product, Category

db = SQLAlchemy()

# Optimized query function using joins
def get_products_with_category_optimized(limit=None):
    query = db.session.query(Product, Category).join(Category, Product.category_id == Category.id)
    if limit:
        query = query.limit(limit)
    products = query.all()
    
    result = []
    for product, category in products:
        product_dict = product.to_dict()
        product_dict['category_name'] = category.name
        result.append(product_dict)
    
    return result

# Optimized query with proper indexing
def product_search_optimized(keyword):
    # Make sure there is an index on Product.name and Product.description columns
    products = Product.query.filter(
        (Product.name.like(f'%{keyword}%')) |
        (Product.description.like(f'%{keyword}%'))
    ).all()
    
    return [p.to_dict() for p in products]

# Optimized user lookup with indexing
def find_user_by_email_optimized(email):
    from models import User
    # Make sure there is an index on User.email column
    return User.query.filter_by(email=email).first()