from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload

# Create the SQLAlchemy instance. Other files will import this.
db = SQLAlchemy()

# --- WARNING ---
# The class names and field names below MUST match your existing
# database tables and columns *perfectly* for the app to work.
# (e.g., if your table is "customers" not "Customers", you must change it)

class customers(db.Model):
    __tablename__ = 'customers'
    customer_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    f_name = db.Column(db.Text)
    l_name = db.Column(db.Text)
    state = db.Column(db.Text)
    address = db.Column(db.Text)
    phone_no = db.Column(db.String(20), nullable=False, unique=True)
    orders = db.relationship('orders', backref='customer')

class sellers(db.Model):
    __tablename__ = 'sellers'
    seller_id = db.Column(db.Integer, primary_key=True)
    seller_name = db.Column(db.Text, nullable=False)
    inventory = db.relationship('inventory', backref='seller')
    orders = db.relationship('orders', backref='seller')

class category(db.Model):
    __tablename__ = 'category'
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.Text, nullable=False)
    products = db.relationship('products', backref='category')

class products(db.Model):
    __tablename__ = 'products'
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    cogs = db.Column(db.Numeric(10, 2))
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'))
    inventory = db.relationship('inventory', backref='product')
    order_items = db.relationship('order_items', backref='product')

class inventory(db.Model):
    __tablename__ = 'inventory'
    inventory_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'))
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.seller_id'))
    stock_remaining = db.Column(db.Integer, nullable=False, default=0)
    ware_house_id = db.Column(db.Text)
    restock_date = db.Column(db.Date)

class orders(db.Model):
    __tablename__ = 'orders'
    order_id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, server_default=db.func.now())
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'))
    order_status = db.Column(db.String(50), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.seller_id'))
    order_items = db.relationship('order_items', backref='order', cascade="all, delete-orphan")
    payment = db.relationship('payments', backref='order', cascade="all, delete-orphan")

class order_items(db.Model):
    __tablename__ = 'order_items'
    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'))
    quantity = db.Column(db.Integer, nullable=False)
    price_per_unit = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)

class shipping(db.Model):
    __tablename__ = 'shipping'
    shipping_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'))
    delivery_status = db.Column(db.String(50))
    shipping_date = db.Column(db.Date)
    return_date = db.Column(db.Date)
    order = db.relationship('orders', backref=db.backref('shipping', uselist=False))


class payments(db.Model):
    __tablename__ = 'payments'
    payment_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), unique=True)
    payment_date = db.Column(db.DateTime, server_default=db.func.now())
    payment_mode = db.Column(db.String(50))
    payment_status = db.Column(db.String(50))
    # This column is required for the refund simulation
    payment_identifier = db.Column(db.Text)

class transaction_log(db.Model):
    __tablename__ = 'transaction_log'
    transaction_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'))
    payment_hash = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

class notify(db.Model):
    __tablename__ = 'notify'
    Notif_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'))
    status = db.Column(db.String(50), default='Pending')
