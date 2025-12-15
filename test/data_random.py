import pandas as pd
from faker import Faker
import random
from datetime import datetime

# Initialize Faker
fake = Faker()

def generate_csv_data(
    num_customers=100,
    num_sellers=10,
    num_categories=5,
    num_products=150,
    num_orders=300
):
    """
    Generates realistic, interconnected dummy data for all 11 tables
    and saves each one to a separate CSV file.
    """
    print("Starting data generation...")

    # --- 1. Sellers ---
    sellers_data = []
    for i in range(1, num_sellers + 1):
        sellers_data.append({
            'seller_id': i,
            'seller_name': f"Workshop {fake.company_suffix()} {fake.last_name()}"
        })
    seller_ids = [s['seller_id'] for s in sellers_data]
    pd.DataFrame(sellers_data).to_csv('Sellers.csv', index=False)
    print("Generated Sellers.csv")

    # --- 2. Category ---
    categories_data = []
    categories = ['Tools', 'Engine Parts', 'Fluids & Chemicals', 'Safety Gear', 'Accessories']
    for i in range(1, len(categories) + 1):
        categories_data.append({
            'category_id': i,
            'category_name': categories[i-1]
        })
    category_ids = [c['category_id'] for c in categories_data]
    pd.DataFrame(categories_data).to_csv('Category.csv', index=False)
    print("Generated Category.csv")

    # --- 3. Customers ---
    customers_data = []
    for i in range(1, num_customers + 1):
        customers_data.append({
            'customer_id': i,
            'username': fake.unique.user_name(),
            'f_name': fake.first_name(),
            'l_name': fake.last_name(),
            'state': fake.state_abbr(),
            'address': fake.street_address(),
            'phone_no': fake.numerify(text='##########') # Matches BIGINT
        })
    customer_ids = [c['customer_id'] for c in customers_data]
    pd.DataFrame(customers_data).to_csv('Customers.csv', index=False)
    print("Generated Customers.csv")

    # --- 4. Products ---
    products_data = []
    # We'll save prices to use in Order_Items
    product_prices = {} 
    for i in range(1, num_products + 1):
        price = round(random.uniform(5.99, 499.99), 2)
        cogs = round(price * random.uniform(0.4, 0.7), 2)
        products_data.append({
            'product_id': i,
            'product_name': f"{fake.color_name().capitalize()} {fake.bs().split(' ')[0]}",
            'price': price,
            'cogs': cogs,
            'category_id': random.choice(category_ids)
        })
        product_prices[i] = price # Save price for later
    product_ids = [p['product_id'] for p in products_data]
    pd.DataFrame(products_data).to_csv('Products.csv', index=False)
    print("Generated Products.csv")

    # --- 5. Inventory ---
    inventory_data = []
    inv_id_counter = 1
    # Ensure each product is in inventory at least once
    for pid in product_ids:
        # Assign to 1-3 sellers
        sellers_for_this_product = random.sample(seller_ids, k=random.randint(1, 3))
        for sid in sellers_for_this_product:
            inventory_data.append({
                'inventory_id': inv_id_counter,
                'product_id': pid,
                'seller_id': sid,
                'stock_remaining': random.randint(0, 500),
                'ware_house_id': f"WH-{random.randint(1, 5)}",
                'restock_date': fake.date_between(start_date='-1y', end_date='today')
            })
            inv_id_counter += 1
    pd.DataFrame(inventory_data).to_csv('Inventory.csv', index=False)
    print("Generated Inventory.csv")

    # --- 6. Orders ---
    orders_data = []
    for i in range(1, num_orders + 1):
        orders_data.append({
            'order_id': i,
            'order_date': fake.date_between(start_date='-2y', end_date='today'), # Matches DATE
            'customer_id': random.choice(customer_ids),
            'order_status': random.choice(['Completed', 'Shipped', 'Pending', 'Cancelled']),
            'seller_id': random.choice(seller_ids)
        })
    order_ids = [o['order_id'] for o in orders_data]
    pd.DataFrame(orders_data).to_csv('Orders.csv', index=False)
    print("Generated Orders.csv")

    # --- 7. Order_Items ---
    order_items_data = []
    oi_id_counter = 1 # Manually increment to match your SQL (not serial)
    for oid in order_ids:
        # Each order gets 1-5 items
        for _ in range(random.randint(1, 5)):
            pid = random.choice(product_ids)
            qty = random.randint(1, 10)
            price_per_unit = product_prices[pid]
            total_price = round(price_per_unit * qty, 2)
            
            order_items_data.append({
                'order_item_id': oi_id_counter, 
                'order_id': oid,
                'product_id': pid,
                'quantity': qty,
                'price_per_unit': price_per_unit, # Matches Float
                'total_price': total_price # Matches Float
            })
            oi_id_counter += 1
    pd.DataFrame(order_items_data).to_csv('Order_Items.csv', index=False)
    print("Generated Order_Items.csv")

    # --- 8. Payments ---
    payments_data = []
    pay_id_counter = 1
    # 80% of orders have a payment record
    paid_orders = random.sample(order_ids, k=int(num_orders * 0.8)) 
    for oid in paid_orders:
        pmode = random.choice(['UPI', 'Card'])
        payments_data.append({
            'payment_id': pay_id_counter,
            'order_id': oid,
            'payment_date': fake.date_between(start_date='-2y', end_date='today'), # Matches DATE
            'payment_mode': pmode, # Matches varchar(10)
            'payment_status': random.choice(['Completed', 'Refunded']),
            'payment_identifier': (f"{fake.user_name()}@okbank" if pmode == 'UPI' else fake.credit_card_number())[:50]
        })
        pay_id_counter += 1
    pd.DataFrame(payments_data).to_csv('Payments.csv', index=False)
    print("Generated Payments.csv")

    # --- 9. Transaction_Log ---
    transactions_data = []
    trans_id_counter = 1
    # Create transactions for the same paid orders
    for oid in paid_orders: 
        transactions_data.append({
            'Transaction_ID': trans_id_counter,
            'order_id': oid,
            'payment_hash': fake.sha1()[:50], # Matches Varchar(50)
            'time_stamp': fake.date_between(start_date='-2y', end_date='today') # Matches DATE
        })
        trans_id_counter += 1
    pd.DataFrame(transactions_data).to_csv('Transaction_Log.csv', index=False)
    print("Generated Transaction_Log.csv")

    # --- 10. Shipping ---
    shipping_data = []
    ship_id_counter = 1
    # 90% of orders have shipping info
    shipped_orders = random.sample(order_ids, k=int(num_orders * 0.9))
    for oid in shipped_orders:
         shipping_data.append({
            'shipping_id': ship_id_counter,
            'order_id': oid,
            'delivery_status': random.choice(['Shipped', 'Delivered', 'Returned']),
            'shipping_date': fake.date_between(start_date='-2y', end_date='today'),
            'return_date': None if random.random() < 0.9 else fake.date_between(start_date='-1y', end_date='today')
        })
         ship_id_counter +=1
    pd.DataFrame(shipping_data).to_csv('Shipping.csv', index=False)
    print("Generated Shipping.csv")

    # --- 11. Notify ---
    notify_data = []
    # 20 users are on a notification list
    for i in range(1, 21): 
        notify_data.append({
            'Notif_id': i,
            'customer_id': random.choice(customer_ids),
            'product_id': random.choice(product_ids),
            'status': 'Pending'
        })
    pd.DataFrame(notify_data).to_csv('Notify.csv', index=False)
    print("Generated Notify.csv")

    print("\nAll CSV files generated successfully!")

# --- This makes the script runnable ---
if __name__ == "__main__":
    # You can change the numbers here if you want
    generate_csv_data(
        num_customers=100,
        num_sellers=10,
        num_products=150,
        num_orders=300
    )
