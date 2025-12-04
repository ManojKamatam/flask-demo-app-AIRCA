from flask_sqlalchemy import SQLAlchemy
import logging

db = SQLAlchemy()
logger = logging.getLogger(__name__)

# Deliberately inefficient query function that doesn't use joins
def get_products_with_category(limit=None):
    from models import Product
    
    try:
        # This will cause N+1 query problem
        products = Product.query.limit(limit).all() if limit else Product.query.all()
        
        result = []
        for product in products:
            product_dict = product.to_dict()
            # Causes additional query for each product
            category = product.category
            if category:
                product_dict['category_name'] = category.name
            else:
                product_dict['category_name'] = None
            result.append(product_dict)
        
        return result
    except Exception as e:
        logger.error(f"Error in get_products_with_category: {e}")
        db.session.rollback()
        raise

# A slow query that doesn't use indexes properly
def slow_product_search(keyword):
    from models import Product
    import time
    
    try:
        # Simulate slow query processing
        time.sleep(2)
        
        # Inefficient LIKE query without index
        products = Product.query.filter(
            (Product.name.like(f'%{keyword}%')) | 
            (Product.description.like(f'%{keyword}%'))
        ).all()
        
        return [p.to_dict() for p in products]
    except Exception as e:
        logger.error(f"Error in slow_product_search: {e}")
        db.session.rollback()
        raise

# Missing index on user lookup
def find_user_by_email(email):
    from models import User
    try:
        return User.query.filter_by(email=email).first()
    except Exception as e:
        logger.error(f"Error in find_user_by_email: {e}")
        db.session.rollback()
        raise

# Vulnerable to SQL injection (for demonstration only)
def unsafe_raw_query(user_input):
    from sqlalchemy import text
    
    try:
        # WARNING: This is deliberately unsafe!
        query = text(f"SELECT * FROM product WHERE name LIKE '%{user_input}%'")
        result = db.session.execute(query)
        
        return [dict(row._mapping) for row in result]
    except Exception as e:
        logger.error(f"Error in unsafe_raw_query: {e}")
        db.session.rollback()
        raise