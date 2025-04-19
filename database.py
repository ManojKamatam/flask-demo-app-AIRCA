from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload

db = SQLAlchemy()

# Efficient query function that uses joins
def get_products_with_category(limit=None):
    from models import Product, Category

    query = Product.query.options(joinedload(Product.category))

    if limit:
        query = query.limit(limit)

    products = query.all()

    result = []
    for product in products:
        product_dict = product.to_dict()
        category_name = product.category.name if product.category else None
        product_dict['category_name'] = category_name
        result.append(product_dict)

    return result

# A query that uses indexes properly
def product_search(keyword):
    from models import Product
    from sqlalchemy import or_

    products = Product.query.filter(
        or_(
            Product.name.ilike(f'%{keyword}%'),
            Product.description.ilike(f'%{keyword}%')
        )
    ).all()

    return [p.to_dict() for p in products]

# Index added on email field
def find_user_by_email(email):
    from models import User
    return User.query.filter_by(email=email).first()

# Use parameterized queries to prevent SQL injection
def search_products_by_name(keyword):
    from models import Product
    from sqlalchemy import or_

    products = Product.query.filter(
        or_(
            Product.name.ilike(f'%{keyword}%'),
            Product.description.ilike(f'%{keyword}%')
        )
    ).all()

    return [p.to_dict() for p in products]