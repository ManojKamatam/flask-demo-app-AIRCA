from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload

db = SQLAlchemy()

# Efficient query function that uses joins
def get_products_with_category(limit=None):
    from models import Product

    query = Product.query.options(joinedload(Product.category))

    if limit:
        query = query.limit(limit)

    products = query.all()

    return [product.to_dict_with_category() for product in products]

# A query that uses indexes properly
def slow_product_search(keyword):
    from models import Product
    import time
    
    # Simulate slow query processing
    time.sleep(2)
    
    # Efficient LIKE query with index
    products = Product.query.filter(
        (Product.name.op('%%')("%{}%".format(keyword))) |
        (Product.description.op('%%')("%{}%".format(keyword)))
    ).all()
    
    return [p.to_dict() for p in products]

# Index added on user lookup
def find_user_by_email(email):
    from models import User
    return User.query.filter_by(email=email).first()

# SQL injection vulnerability fixed by using parameterized queries
def safe_product_search(user_input):
    from models import Product
    
    # Use parameterized queries
    products = Product.query.filter(
        (Product.name.like('%' + user_input + '%')) |
        (Product.description.like('%' + user_input + '%'))
    ).all()
    
    return [p.to_dict() for p in products]