from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

db = SQLAlchemy()

# Efficient query using SQL joins
def get_products_with_category(limit=None):
    from models import Product, Category
    
    query = db.session.query(Product, Category) \
                        .outerjoin(Category, Product.category_id == Category.id)
    
    if limit:
        query = query.limit(limit)
    
    products = query.all()
    
    result = []
    for product, category in products:
        product_dict = product.to_dict()
        product_dict['category_name'] = category.name if category else None
        result.append(product_dict)
    
    return result

# Query with proper indexing
def slow_product_search(keyword):
    from models import Product
    
    # Use SQL function for case-insensitive search
    search_term = f'%{keyword}%'
    products = Product.query.filter(
        func.lower(Product.name).like(func.lower(search_term)) |
        func.lower(Product.description).like(func.lower(search_term))
    ).all()
    
    return [p.to_dict() for p in products]

# Add index for email column
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