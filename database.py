from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import orm

db = SQLAlchemy()

# Optimized query function using joins
def get_products_with_category_optimized(limit=None):
    from models import Product, Category
    
    query = (
        db.session.query(Product, Category)
        .outerjoin(Category, Product.category_id == Category.id)
        .options(orm.contains_eager(Product.category))
    )
    
    if limit:
        query = query.limit(limit)
    
    products = query.all()
    
    result = []
    for product, category in products:
        product_dict = product.to_dict()
        if category:
            product_dict['category_name'] = category.name
        else:
            product_dict['category_name'] = None
        result.append(product_dict)
    
    return result

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

# Add index on user email for faster lookup
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