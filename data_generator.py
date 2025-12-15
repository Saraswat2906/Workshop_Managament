import pandas as pd
import random

def generate_csv_data():
    """
    Generates a small, fixed, interconnected set of manual data for all 11 tables
    and saves each one to a separate CSV file.
    """
    print("Starting data generation with manual examples...")

    # --- 1. Sellers ---
    sellers_data = [
        {'seller_id': 1, 'seller_name': 'Workshop A'},
        {'seller_id': 2, 'seller_name': 'Workshop B'}
    ]
    seller_ids = [s['seller_id'] for s in sellers_data]
    pd.DataFrame(sellers_data).to_csv('Sellers.csv', index=False)
    print("Generated Sellers.csv")

    # --- 2. Category ---
    categories_data = [
        {'category_id': 1, 'category_name': 'Tools'},
        {'category_id': 2, 'category_name': 'Engine Parts'}
    ]
    category_ids = [c['category_id'] for c in categories_data]
    pd.DataFrame(categories_data).to_csv('Category.csv', index=False)
    print("Generated Category.csv")

    # --- 3. Customers ---
    customers_data = [
        {
            'customer_id': 1, 'username': 'johndoe', 'f_name': 'John', 'l_name': 'Doe',
            'state': 'CA', 'address': '123 Main St', 'phone_no': 5551234567
        },
        {
            'customer_id': 2, 'username': 'janefoe', 'f_name': 'Jane', 'l_name': 'Foe',
            'state': 'NY', 'address': '456 Oak Ave', 'phone_no': 5557654321
        },
        {
            'customer_id': 3, 'username': 'bobbrown', 'f_name': 'Bob', 'l_name': 'Brown',
            'state': 'TX', 'address': '789 Pine Ln', 'phone_no': 5559876543
        }
    ]
    customer_ids = [c['customer_id'] for c in customers_data]
    pd.DataFrame(customers_data).to_csv('Customers.csv', index=False)
    print("Generated Customers.csv")

    # --- 4. Products ---
    products_data = [
        {'product_id': 1, 'product_name': 'Hammer', 'price': 15.99, 'cogs': 8.00, 'category_id': 1},
        {'product_id': 2, 'product_name': 'Screwdriver Set', 'price': 25.50, 'cogs': 12.50, 'category_id': 1},
        {'product_id': 3, 'product_name': 'Spark Plug', 'price': 5.75, 'cogs': 2.50, 'category_id': 2}
    ]
    # We'll save prices to use in Order_Items
    product_prices = {p['product_id']: p['price'] for p in products_data}
    product_ids = [p['product_id'] for p in products_data]
    pd.DataFrame(products_data).to_csv('Products.csv', index=False)
    print("Generated Products.csv")

    # --- 5. Inventory ---
    inventory_data = [
        {'inventory_id': 1, 'product_id': 1, 'seller_id': 1, 'stock_remaining': 100, 'ware_house_id': 'WH-1', 'restock_date': '2023-01-15'},
        {'inventory_id': 2, 'product_id': 2, 'seller_id': 1, 'stock_remaining': 50, 'ware_house_id': 'WH-1', 'restock_date': '2023-01-20'},
        {'inventory_id': 3, 'product_id': 3, 'seller_id': 2, 'stock_remaining': 200, 'ware_house_id': 'WH-2', 'restock_date': '2023-01-10'},
        {'inventory_id': 4, 'product_id': 1, 'seller_id': 2, 'stock_remaining': 5, 'ware_house_id': 'WH-2', 'restock_date': '2023-02-01'} # Limited stock
    ]
    pd.DataFrame(inventory_data).to_csv('Inventory.csv', index=False)
    print("Generated Inventory.csv")

    # --- 6. Orders ---
    orders_data = [
        {'order_id': 1, 'order_date': '2023-03-01', 'customer_id': 1, 'order_status': 'Completed', 'seller_id': 1},
        {'order_id': 2, 'order_date': '2023-03-05', 'customer_id': 2, 'order_status': 'Shipped', 'seller_id': 2},
        {'order_id': 3, 'order_date': '2023-03-10', 'customer_id': 1, 'order_status': 'Pending', 'seller_id': 1}
    ]
    order_ids = [o['order_id'] for o in orders_data]
    pd.DataFrame(orders_data).to_csv('Orders.csv', index=False)
    print("Generated Orders.csv")

    # --- 7. Order_Items ---
    order_items_data = [
        {'order_item_id': 1, 'order_id': 1, 'product_id': 1, 'quantity': 2, 'price_per_unit': 15.99, 'total_price': 31.98},
        {'order_item_id': 2, 'order_id': 1, 'product_id': 2, 'quantity': 1, 'price_per_unit': 25.50, 'total_price': 25.50},
        {'order_item_id': 3, 'order_id': 2, 'product_id': 3, 'quantity': 10, 'price_per_unit': 5.75, 'total_price': 57.50},
        {'order_item_id': 4, 'order_id': 3, 'product_id': 1, 'quantity': 1, 'price_per_unit': 15.99, 'total_price': 15.99}
    ]
    pd.DataFrame(order_items_data).to_csv('Order_Items.csv', index=False)
    print("Generated Order_Items.csv")

    # --- 8. Payments ---
    payments_data = [
        {'payment_id': 1, 'order_id': 1, 'payment_date': '2023-03-01', 'payment_mode': 'Card', 'payment_status': 'Completed', 'payment_identifier': '4242...4242'},
        {'payment_id': 2, 'order_id': 2, 'payment_date': '2023-03-05', 'payment_mode': 'UPI', 'payment_status': 'Completed', 'payment_identifier': 'janefoe@okbank'}
    ]
    pd.DataFrame(payments_data).to_csv('Payments.csv', index=False)
    print("Generated Payments.csv")

    # --- 9. Transaction_Log ---
    transactions_data = [
        {'Transaction_ID': 1, 'order_id': 1, 'payment_hash': 'abc123hash', 'time_stamp': '2023-03-01'},
        {'Transaction_ID': 2, 'order_id': 2, 'payment_hash': 'def456hash', 'time_stamp': '2023-03-05'}
    ]
    pd.DataFrame(transactions_data).to_csv('Transaction_Log.csv', index=False)
    print("Generated Transaction_Log.csv")

    # --- 10. Shipping ---
    shipping_data = [
        {'shipping_id': 1, 'order_id': 1, 'delivery_status': 'Delivered', 'shipping_date': '2023-03-02', 'return_date': None},
        {'shipping_id': 2, 'order_id': 2, 'delivery_status': 'Shipped', 'shipping_date': '2023-03-06', 'return_date': None}
    ]
    pd.DataFrame(shipping_data).to_csv('Shipping.csv', index=False)
    print("Generated Shipping.csv")

    # --- 11. Notify ---
    notify_data = [
        {'Notif_id': 1, 'customer_id': 3, 'product_id': 1, 'status': 'Pending'}
    ]
    pd.DataFrame(notify_data).to_csv('Notify.csv', index=False)
    print("Generated Notify.csv")

    print("\nAll CSV files generated successfully with manual data!")

# --- This makes the script runnable ---
if __name__ == "__main__":
    generate_csv_data()

