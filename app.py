# from flask import Flask, request, render_template
# from Database_config import config
# from models import db

# # 1. Import all your function handlers
# from user_authentication import handle_register
# from product_management import handle_get_products
# from order_management import handle_create_order, handle_cancel_order, handle_notify_me
# from payment import handle_pay

# # --- App Setup ---
# app = Flask(__name__)
# app.config.from_object(config)

# # Connect SQLAlchemy to the Flask app
# db.init_app(app)

# # --- Static HTML Page Routes ---
# # These routes just serve your HTML files
# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/shop')
# def shop():
#     return render_template('shop.html')

# @app.route('/payment')
# def payment():
#     return render_template('payment.html')

# # --- API Routes (The "Brain") ---
# # These routes connect your frontend to your backend functions.

# @app.route('/api/register', methods=['POST'])
# def register_customer():
#     return handle_register(request.json)

# @app.route('/api/products', methods=['GET'])
# def get_products():
#     return handle_get_products()

# @app.route('/api/create_order', methods=['POST'])
# def create_order():
#     return handle_create_order(request.json)

# @app.route('/api/notify', methods=['POST'])
# def notify_me():
#     return handle_notify_me(request.json)

# @app.route('/api/cancel_order', methods=['POST'])
# def cancel_order():
#     return handle_cancel_order(request.json)

# @app.route('/api/pay', methods=['POST'])
# def pay():
#     return handle_pay(request.json)

# # --- Run the Application ---
# if __name__ == '__main__':
#     # We DO NOT run db.create_all() or init_dummy_data()
#     # because your database already exists.
#     app.run(debug=True)
from flask import Flask, request, jsonify, render_template
from Database_config import config
from models import db

# Import all your new functions
from user_authentication import handle_register
from product_management import handle_get_products
from order_management import (
    handle_checkout, 
    handle_get_orders, 
    handle_cancel_order, 
    handle_return_order
)
from payment import handle_pay

# --- App Setup ---
app = Flask(__name__)
app.config.from_object(config)

# Connect SQLAlchemy to the Flask app
db.init_app(app)

# --- Static HTML Page Routes ---
# These routes just serve your HTML files
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shop')
def shop():
    return render_template('shop.html')

@app.route('/payment')
def payment():
    return render_template('payment.html')

@app.route('/profile')
def profile():
    """Serves the new profile page."""
    return render_template('profile.html')

# --- API Routes (The "Brain") ---
# These routes do the work. They call your imported functions.

@app.route('/api/register', methods=['POST'])
def register_customer():
    return handle_register(request.json)

@app.route('/api/products', methods=['GET'])
def get_products():
    return handle_get_products()

@app.route('/api/checkout', methods=['POST'])
def checkout():
    """New route for cart checkout."""
    return handle_checkout(request.json)

@app.route('/api/pay', methods=['POST'])
def pay():
    return handle_pay(request.json)

@app.route('/api/get_orders', methods=['POST'])
def get_orders():
    """New route for profile page."""
    return handle_get_orders(request.json)

@app.route('/api/cancel_order', methods=['POST'])
def cancel_order():
    """Route for cancelling an order (from profile or payment page)."""
    return handle_cancel_order(request.json)

@app.route('/api/return_order', methods=['POST'])
def return_order():
    """New route for profile page returns."""
    return handle_return_order(request.json)

# --- Run the Application ---
if __name__ == '__main__':
    # This block runs only when you execute `python app.py`
    with app.app_context():
        # We DO NOT run db.create_all() or init_dummy_data()
        # because your database and data already exist.
        pass
        
    app.run(debug=True)

