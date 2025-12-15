# # # from flask import jsonify
# # # from models import db, products, inventory, sellers, orders, order_items, shipping, payments
# # # from sqlalchemy.orm import joinedload
# # # import datetime

# # # def handle_checkout(request_data):
# # #     """
# # #     Handles the checkout of an entire cart of items from a single seller.
# # #     """
# # #     customer_id = request_data.get('customer_id')
# # #     seller_id = request_data.get('seller_id')
# # #     cart_items = request_data.get('items') # Expects a list of {'product_id': X, 'quantity': Y}

# # #     if not all([customer_id, seller_id, cart_items]):
# # #         return jsonify({'status': 'error', 'message': 'Missing checkout data'}), 400

# # #     session = db.session()
# # #     try:
# # #         total_price = 0
# # #         order_items_to_create = []
        
# # #         # --- 1. Validate cart and lock inventory ---
# # #         for item in cart_items:
# # #             product_id = item['product_id']
# # #             quantity_to_buy = int(item['quantity'])

# # #             # Lock the inventory row for this specific product and seller
# # #             inv_item = session.query(inventory).filter(
# # #                 inventory.product_id == product_id,
# # #                 inventory.seller_id == seller_id
# # #             ).with_for_update().first() # with_for_update() locks the row

# # #             # Check stock
# # #             if not inv_item or inv_item.stock_remaining < quantity_to_buy:
# # #                 session.rollback()
# # #                 product = session.query(products).get(product_id)
# # #                 product_name = product.product_name if product else f"Product ID {product_id}"
# # #                 return jsonify({
# # #                     'status': 'error', 
# # #                     'message': f'Not enough stock for {product_name}. Please update your cart.'
# # #                 }), 400
            
# # #             # Update inventory
# # #             inv_item.stock_remaining -= quantity_to_buy
            
# # #             # Get product details for order
# # #             product = session.query(products).get(product_id)
# # #             price_per_unit = product.price
# # #             item_total_price = price_per_unit * quantity_to_buy
# # #             total_price += item_total_price

# # #             # Prepare the Order_Item object
# # #             order_items_to_create.append(
# # #                 order_items(
# # #                     product_id=product_id,
# # #                     product_name=product.product_name, # Store product name for history
# # #                     quantity=quantity_to_buy,
# # #                     price_per_unit=price_per_unit,
# # #                     total_price=item_total_price
# # #                 )
# # #             )

# # #         # --- 2. Create the main Order ---
# # #         new_order = orders(
# # #             customer_id=customer_id,
# # #             order_status='Pending', # 'Pending' means payment is needed
# # #             seller_id=seller_id
# # #         )
# # #         session.add(new_order)
        
# # #         # --- 3. Create shipping Record ---
# # #         # Calculate estimated shipping date (4-5 days from now)
# # #         # Simple 4 or 5 day logic
# # #         shipping_days = 4 + (datetime.datetime.now().microsecond % 2) 
# # #         est_shipping_date = datetime.date.today() + datetime.timedelta(days=shipping_days)
        
# # #         new_shipping = shipping(
# # #             order=new_order, # Link to the new order
# # #             delivery_status='Processing', # Not yet shipped
# # #             shipping_date=est_shipping_date
# # #         )
# # #         session.add(new_shipping)

# # #         # --- 4. Add order_items to the Order ---
# # #         for oi in order_items_to_create:
# # #             oi.order = new_order # Link each item to the new order
# # #             session.add(oi)

# # #         # --- 5. Commit the entire transaction ---
# # #         session.commit()
        
# # #         return jsonify({
# # #             'status': 'success',
# # #             'message': 'Order created! Proceed to payment.',
# # #             'order_id': new_order.order_id,
# # #             'total_price': float(total_price)
# # #         })

# # #     except Exception as e:
# # #         session.rollback() # Rollback all changes if any step failed
# # #         return jsonify({'status': 'error', 'message': str(e)}), 500
# # #     finally:
# # #         session.close()


# # # def handle_get_orders(request_data):
# # #     """Fetches all orders for a specific customer."""
# # #     customer_id = request_data.get('customer_id')
# # #     if not customer_id:
# # #         return jsonify({'status': 'error', 'message': 'Missing customer ID'}), 400
    
# # #     try:
# # #         # Eagerly load all related data we need for the profile page
# # #         orders = orders.query.options(
# # #             joinedload(orders.order_items),
# # #             joinedload(orders.shipping),
# # #             joinedload(orders.payment),
# # #             joinedload(orders.seller)
# # #         ).filter(orders.customer_id == customer_id).order_by(orders.order_date.desc()).all()

# # #         orders_list = []
# # #         for order in orders:
# # #             orders_list.append({
# # #                 'order_id': order.order_id,
# # #                 'order_date': order.order_date.strftime('%Y-%m-%d %H:%M'),
# # #                 'order_status': order.order_status,
# # #                 'seller_name': order.seller.seller_name if order.seller else 'N/A',
# # #                 'items': [{
# # #                     'name': item.product_name,
# # #                     'quantity': item.quantity,
# # #                     'price': float(item.total_price)
# # #                 } for item in order.order_items],
# # #                 'shipping_info': {
# # #                     'status': order.shipping.delivery_status if order.shipping else 'N/A',
# # #                     'estimated_arrival': order.shipping.shipping_date.strftime('%Y-%m-%d') if order.shipping and order.shipping.shipping_date else 'N/A',
# # #                     'return_date': order.shipping.return_date.strftime('%Y-%m-%d') if order.shipping and order.shipping.return_date else None
# # #                 } if order.shipping else None,
# # #                 'payment_status': order.payment.payment_status if order.payment else 'N/A',
# # #                 'total_price': float(sum(item.total_price for item in order.order_items))
# # #             })

# # #         return jsonify({'status': 'success', 'orders': orders_list})
    
# # #     except Exception as e:
# # #         return jsonify({'status': 'error', 'message': str(e)}), 500


# # # def handle_cancel_order(request_data):
# # #     """Cancels an order that is 'Pending' or 'Processing'."""
# # #     order_id = request_data.get('order_id')
# # #     if not order_id:
# # #         return jsonify({'status': 'error', 'message': 'Missing order ID'}), 400

# # #     session = db.session()
# # #     try:
# # #         order = session.query(orders).options(
# # #             joinedload(orders.order_items),
# # #             joinedload(orders.payment)
# # #         ).get(order_id)

# # #         if not order:
# # #             return jsonify({'status': 'error', 'message': 'Order not found'}), 404
        
# # #         if order.order_status not in ['Pending', 'Processing']:
# # #             return jsonify({'status': 'error', 'message': f'Cannot cancel an order with status: {order.order_status}'}), 400
        
# # #         # --- 1. Restore inventory ---
# # #         # Our new checkout logic removes stock immediately, so we must always restock.
# # #         for item in order.order_items:
# # #             inv_item = session.query(inventory).filter(
# # #                 inventory.product_id == item.product_id,
# # #                 inventory.seller_id == order.seller_id
# # #             ).with_for_update().first()
# # #             if inv_item:
# # #                 inv_item.stock_remaining += item.quantity
        
# # #         # --- 2. Update Order Status ---
# # #         order.order_status = 'Cancelled'

# # #         # --- 3. Update Payment Status (if paid) ---
# # #         if order.payment and order.payment.payment_status == 'Completed':
# # #             order.payment.payment_status = 'Refunded'
# # #             # (In a real app, this would trigger a call to the payment gateway API)
            
# # #         # --- 4. Update shipping Status ---
# # #         if order.shipping:
# # #             order.shipping.delivery_status = 'Cancelled'

# # #         session.commit()
# # #         return jsonify({'status': 'success', 'message': f'Order {order_id} has been cancelled and refunded.'})

# # #     except Exception as e:
# # #         session.rollback()
# # #         return jsonify({'status': 'error', 'message': str(e)}), 500
# # #     finally:
# # #         session.close()


# # # def handle_return_order(request_data):
# # #     """Processes a return for a 'Shipped' or 'Delivered' order."""
# # #     order_id = request_data.get('order_id')
# # #     if not order_id:
# # #         return jsonify({'status': 'error', 'message': 'Missing order ID'}), 400

# # #     session = db.session()
# # #     try:
# # #         order = session.query(orders).options(
# # #             joinedload(orders.payment),
# # #             joinedload(orders.shipping)
# # #         ).get(order_id)

# # #         if not order:
# # #             return jsonify({'status': 'error', 'message': 'Order not found'}), 404

# # #         # Business logic: Only 'Shipped' or 'Delivered' orders can be returned
# # #         if order.order_status not in ['Shipped', 'Delivered']:
# # #             return jsonify({'status': 'error', 'message': f'Cannot return an order with status: {order.order_status}'}), 400

# # #         # --- 1. Update Order Status ---
# # #         order.order_status = 'Returned'
        
# # #         # --- 2. Update Payment Status ---
# # #         if order.payment:
# # #             order.payment.payment_status = 'Refunded'
# # #             # (Trigger refund API)

# # #         # --- 3. Update shipping Status & Set Return Date ---
# # #         if order.shipping:
# # #             order.shipping.delivery_status = 'Returned'
# # #             # Set return pickup date 6-7 days from now
# # #             return_days = 6 + (datetime.datetime.now().microsecond % 2) # 6 or 7 days
# # #             order.shipping.return_date = datetime.date.today() + datetime.timedelta(days=return_days)
        
# # #         # --- 4. NOTE: We DO NOT restock inventory for a return ---
# # #         # The items are used/opened, unlike a cancellation.
        
# # #         session.commit()
# # #         return_date_str = order.shipping.return_date.strftime('%Y-%m-%d') if order.shipping else 'N/A'
# # #         return jsonify({
# # #             'status': 'success', 
# # #             'message': f'Order {order_id} return processed. Refund initiated. Pickup scheduled for {return_date_str}.'
# # #         })

# # #     except Exception as e:
# # #         session.rollback()
# # #         return jsonify({'status': 'error', 'message': str(e)}), 500
# # #     finally:
# # #         session.close()

# # from flask import jsonify
# # from models import db, products, inventory, sellers, orders, order_items, shipping, payments
# # from sqlalchemy.orm import joinedload
# # import datetime

# # def handle_checkout(request_data):
# #     """
# #     Handles the checkout of an entire cart, compatible with the strict original schema.
# #     """
# #     customer_id = request_data.get('customer_id')
# #     seller_id = request_data.get('seller_id')
# #     cart_items = request_data.get('items') # Expects a list of {'product_id': X, 'quantity': Y}

# #     if not all([customer_id, seller_id, cart_items]):
# #         return jsonify({'status': 'error', 'message': 'Missing checkout data'}), 400

# #     session = db.session()
# #     try:
# #         total_price = 0
# #         order_items_to_create = []
        
# #         # --- 1. Validate cart and lock inventory ---
# #         for item in cart_items:
# #             product_id = item['product_id']
# #             quantity_to_buy = int(item['quantity'])

# #             inv_item = session.query(inventory).filter(
# #                 inventory.product_id == product_id,
# #                 inventory.seller_id == seller_id
# #             ).with_for_update().first() 

# #             if not inv_item or inv_item.stock_remaining < quantity_to_buy:
# #                 session.rollback()
# #                 product = session.query(products).get(product_id)
# #                 product_name = product.product_name if product else f"Product ID {product_id}"
# #                 return jsonify({
# #                     'status': 'error', 
# #                     'message': f'Not enough stock for {product_name}. Please update your cart.'
# #                 }), 400
            
# #             inv_item.stock_remaining -= quantity_to_buy
            
# #             product = session.query(products).get(product_id)
# #             # product.price is Numeric (Decimal), but order_items.price_per_unit is Float
# #             # We must cast to float() to match the database schema
# #             price_per_unit = float(product.price) 
# #             item_total_price = price_per_unit * quantity_to_buy
# #             total_price += item_total_price

# #             order_items_to_create.append(
# #                 order_items(
# #                     product_id=product_id,
# #                     # We CANNOT save product_name as it's not in the strict schema
# #                     quantity=quantity_to_buy,
# #                     price_per_unit=price_per_unit, # This is now a float
# #                     total_price=item_total_price  # This is also a float
# #                 )
# #             )

# #         # --- 2. Create the main Order ---
# #         new_order = orders(
# #             customer_id=customer_id,
# #             order_status='Pending', 
# #             seller_id=seller_id,
# #             order_date=datetime.date.today() # Use DATE object to match schema
# #         )
# #         session.add(new_order)
        
# #         # --- 3. Create shipping Record ---
# #         shipping_days = 4 + (datetime.datetime.now().microsecond % 2) # 4 or 5 days
# #         est_shipping_date = datetime.date.today() + datetime.timedelta(days=shipping_days) # This is a DATE object
        
# #         new_shipping = shipping(
# #             order=new_order, 
# #             delivery_status='Processing',
# #             shipping_date=est_shipping_date
# #         )
# #         session.add(new_shipping)

# #         # --- 4. Add order_items to the Order ---
# #         for oi in order_items_to_create:
# #             oi.order = new_order 
# #             session.add(oi)

# #         # --- 5. Commit the entire transaction ---
# #         session.commit()
        
# #         return jsonify({
# #             'status': 'success',
# #             'message': 'Order created! Proceed to payment.',
# #             'order_id': new_order.order_id,
# #             'total_price': float(total_price)
# #         })

# #     except Exception as e:
# #         session.rollback() 
# #         return jsonify({'status': 'error', 'message': str(e)}), 500
# #     finally:
# #         session.close()


# # def handle_get_orders(request_data):
# #     """Fetches all orders, joining to products to get item names."""
# #     customer_id = request_data.get('customer_id')
# #     if not customer_id:
# #         return jsonify({'status': 'error', 'message': 'Missing customer ID'}), 400
    
# #     try:
# #         # MODIFIED: We must now JOIN on products via order_items
# #         orders = orders.query.options(
# #             joinedload(orders.order_items).joinedload(order_items.product), # <-- This is the new JOIN
# #             joinedload(orders.shipping),
# #             joinedload(orders.payment), # This will be a list
# #             joinedload(orders.seller)
# #         ).filter(orders.customer_id == customer_id).order_by(orders.order_date.desc()).all()

# #         orders_list = []
# #         for order in orders:
# #             # Get payment status from the list of payments
# #             payment_status = 'N/A'
# #             if order.payment:
# #                 # Get the most recent payment's status
# #                 payment_status = order.payment[-1].payment_status 
            
# #             orders_list.append({
# #                 'order_id': order.order_id,
# #                 'order_date': order.order_date.strftime('%Y-%m-%d') if order.order_date else 'N/A',
# #                 'order_status': order.order_status,
# #                 'seller_name': order.seller.seller_name if order.seller else 'N/A',
# #                 'items': [{
# #                     'name': item.product.product_name, # <-- Get name from joined product
# #                     'quantity': item.quantity,
# #                     'price': float(item.total_price) # Cast Float to float
# #                 } for item in order.order_items],
# #                 'shipping_info': {
# #                     'status': order.shipping.delivery_status if order.shipping else 'N/A',
# #                     'estimated_arrival': order.shipping.shipping_date.strftime('%Y-%m-%d') if order.shipping and order.shipping.shipping_date else 'N/A',
# #                     'return_date': order.shipping.return_date.strftime('%Y-%m-%d') if order.shipping and order.shipping.return_date else None
# #                 } if order.shipping else None,
# #                 'payment_status': payment_status,
# #                 'total_price': float(sum(item.total_price for item in order.order_items))
# #             })

# #         return jsonify({'status': 'success', 'orders': orders_list})
    
# #     except Exception as e:
# #         return jsonify({'status': 'error', 'message': str(e)}), 500


# # def handle_cancel_order(request_data):
# #     """Cancels an order, compatible with strict schema."""
# #     order_id = request_data.get('order_id')
# #     if not order_id:
# #         return jsonify({'status': 'error', 'message': 'Missing order ID'}), 400

# #     session = db.session()
# #     try:
# #         order = session.query(orders).options(
# #             joinedload(orders.order_items),
# #             joinedload(orders.payment)
# #         ).get(order_id)

# #         if not order:
# #             return jsonify({'status': 'error', 'message': 'Order not found'}), 404
        
# #         if order.order_status not in ['Pending', 'Processing']:
# #             return jsonify({'status': 'error', 'message': f'Cannot cancel an order with status: {order.order_status}'}), 400
        
# #         # --- 1. Restore inventory ---
# #         for item in order.order_items:
# #             inv_item = session.query(inventory).filter(
# #                 inventory.product_id == item.product_id,
# #                 inventory.seller_id == order.seller_id
# #             ).with_for_update().first()
# #             if inv_item:
# #                 inv_item.stock_remaining += item.quantity
        
# #         # --- 2. Update Order Status ---
# #         order.order_status = 'Cancelled'

# #         # --- 3. Update Payment Status (if paid) ---
# #         if order.payment:
# #             # Loop through payments and update them
# #             for payment in order.payment:
# #                 if payment.payment_status == 'Completed':
# #                     payment.payment_status = 'Refunded'
            
# #         # --- 4. Update shipping Status ---
# #         if order.shipping:
# #             order.shipping.delivery_status = 'Cancelled'

# #         session.commit()
# #         return jsonify({'status': 'success', 'message': f'Order {order_id} has been cancelled and refunded.'})

# #     except Exception as e:
# #         session.rollback()
# #         return jsonify({'status': 'error', 'message': str(e)}), 500
# #     finally:
# #         session.close()


# # def handle_return_order(request_data):
# #     """Processes a return, compatible with strict schema."""
# #     order_id = request_data.get('order_id')
# #     if not order_id:
# #         return jsonify({'status': 'error', 'message': 'Missing order ID'}), 400

# #     session = db.session()
# #     try:
# #         order = session.query(orders).options(
# #             joinedload(orders.payment),
# #             joinedload(orders.shipping)
# #         ).get(order_id)

# #         if not order:
# #             return jsonify({'status': 'error', 'message': 'Order not found'}), 404

# #         if order.order_status not in ['Shipped', 'Delivered']:
# #             return jsonify({'status': 'error', 'message': f'Cannot return an order with status: {order.order_status}'}), 400

# #         # --- 1. Update Order Status ---
# #         order.order_status = 'Returned'
        
# #         # --- 2. Update Payment Status ---
# #         if order.payment:
# #             for payment in order.payment:
# #                 payment.payment_status = 'Refunded'

# #         # --- 3. Update shipping Status & Set Return Date ---
# #         if order.shipping:
# #             order.shipping.delivery_status = 'Returned'
# #             return_days = 6 + (datetime.datetime.now().microsecond % 2) # 6 or 7 days
# #             order.shipping.return_date = datetime.date.today() + datetime.timedelta(days=return_days)
        
# #         session.commit()
# #         return_date_str = order.shipping.return_date.strftime('%Y-%m-%d') if order.shipping and order.shipping.return_date else 'N/A'
# #         return jsonify({
# #             'status': 'success', 
# #             'message': f'Order {order_id} return processed. Refund initiated. Pickup scheduled for {return_date_str}.'
# #         })

# #     except Exception as e:
# #         session.rollback()
# #         return jsonify({'status': 'error', 'message': str(e)}), 500
# #     finally:
# #         session.close()

# from flask import jsonify
# # Import lowercase models consistent with your models.py
# from models import db, products, inventory, sellers, orders, order_items, shipping, payments
# from sqlalchemy.orm import joinedload
# from sqlalchemy import func # Import func for now()
# import datetime

# def handle_checkout(request_data):
#     """
#     Handles the checkout of an entire cart, compatible with the strict original schema.
#     """
#     customer_id = request_data.get('customer_id')
#     seller_id = request_data.get('seller_id')
#     cart_items = request_data.get('items') # Expects a list of {'product_id': X, 'quantity': Y}

#     if not all([customer_id, seller_id, cart_items]):
#         return jsonify({'status': 'error', 'message': 'Missing checkout data'}), 400

#     session = db.session()
#     try:
#         total_price = 0.0 # Use float explicitly
#         order_items_to_create = []

#         # --- 1. Validate cart and lock inventory ---
#         for item in cart_items:
#             product_id = item['product_id']
#             quantity_to_buy = int(item['quantity'])

#             inv_item = session.query(inventory).filter(
#                 inventory.product_id == product_id,
#                 inventory.seller_id == seller_id
#             ).with_for_update().first()

#             if not inv_item or inv_item.stock_remaining < quantity_to_buy:
#                 session.rollback()
#                 product = session.query(products).get(product_id)
#                 product_name = product.product_name if product else f"Product ID {product_id}"
#                 return jsonify({
#                     'status': 'error',
#                     'message': f'Not enough stock for {product_name}. Please update your cart.'
#                 }), 400

#             inv_item.stock_remaining -= quantity_to_buy

#             product = session.query(products).get(product_id)
#             # product.price is Numeric (Decimal), but order_items.price_per_unit is Float
#             # We must cast to float() to match the database schema
#             price_per_unit = float(product.price)
#             item_total_price = price_per_unit * quantity_to_buy
#             total_price += item_total_price

#             order_items_to_create.append(
#                 order_items(
#                     product_id=product_id,
#                     # We CANNOT save product_name as it's not in the strict schema
#                     quantity=quantity_to_buy,
#                     price_per_unit=price_per_unit, # This is now a float
#                     total_price=item_total_price  # This is also a float
#                 )
#             )

#         # --- 2. Create the main Order ---
#         new_order = orders(
#             customer_id=customer_id,
#             order_status='Pending',
#             seller_id=seller_id,
#             order_date=datetime.date.today() # Use DATE object to match schema
#         )
#         session.add(new_order)
#         # We need to flush to get the new_order.order_id before creating shipping
#         session.flush()

#         # --- 3. Create shipping Record ---
#         shipping_days = 4 + (datetime.datetime.now().microsecond % 2) # 4 or 5 days
#         est_shipping_date = datetime.date.today() + datetime.timedelta(days=shipping_days) # This is a DATE object

#         # *** FIX: Set order_id directly, not the 'order' object ***
#         new_shipping = shipping(
#             order_id=new_order.order_id, # <-- Use the ID here
#             delivery_status='Processing',
#             shipping_date=est_shipping_date
#         )
#         session.add(new_shipping)

#         # --- 4. Add order_items to the Order ---
#         for oi in order_items_to_create:
#             # *** FIX: Also set order_id directly here ***
#             oi.order_id = new_order.order_id
#             # oi.order = new_order # This would also work after flushing
#             session.add(oi)

#         # --- 5. Commit the entire transaction ---
#         session.commit()

#         return jsonify({
#             'status': 'success',
#             'message': 'Order created! Proceed to payment.',
#             'order_id': new_order.order_id,
#             'total_price': float(total_price) # Ensure total price is float
#         })

#     except Exception as e:
#         session.rollback()
#         import traceback
#         traceback.print_exc() # Print detailed error to console
#         return jsonify({'status': 'error', 'message': str(e)}), 500
#     finally:
#         session.close()


# def handle_get_orders(request_data):
#     """Fetches all orders, joining to products to get item names."""
#     customer_id = request_data.get('customer_id')
#     if not customer_id:
#         return jsonify({'status': 'error', 'message': 'Missing customer ID'}), 400

#     try:
#         # Fetch orders and related data
#         # Ensure relationships match the lowercase model names
#         orders_query = orders.query.options(
#             joinedload(orders.order_items).joinedload(order_items.product),
#             joinedload(orders.shipping), # Load the single shipping record
#             joinedload(orders.payment), # Load the single payment record
#             joinedload(orders.seller)
#         ).filter(orders.customer_id == customer_id).order_by(orders.order_date.desc()).all()

#         orders_list = []
#         for order in orders_query: # Use orders_query here
#             print(f"Processing order instance: {type(order)}, ID: {order.order_id}")
#             # Correctly access the single payment record
#             payment_status = order.payment.payment_status if order.payment else 'N/A'
#             # Calculate total price correctly
#             current_total_price = sum(float(item.total_price) for item in order.order_items)

#             orders_list.append({
#                 'order_id': order.order_id,
#                  # Use .date() if order_date is DateTime, else just access if it's Date
#                 'order_date': order.order_date.strftime('%Y-%m-%d') if order.order_date else 'N/A',
#                 'order_status': order.order_status,
#                 'seller_name': order.seller.seller_name if order.seller else 'N/A',
#                 'items': [{
#                     'name': item.product.product_name if item.product else 'Unknown Product', # Added check
#                     'quantity': item.quantity,
#                     'price': float(item.total_price) # Cast Float to float
#                 } for item in order.order_items],
#                  # Correctly access the single shipping record
#                 'shipping_info': {
#                     'status': order.shipping.delivery_status if order.shipping else 'N/A',
#                     'estimated_arrival': order.shipping.shipping_date.strftime('%Y-%m-%d') if order.shipping and order.shipping.shipping_date else 'N/A',
#                     'return_date': order.shipping.return_date.strftime('%Y-%m-%d') if order.shipping and order.shipping.return_date else None
#                 } if order.shipping else None,
#                 'payment_status': payment_status,
#                 'total_price': float(current_total_price) # Use calculated total price
#             })

#         return jsonify({'status': 'success', 'orders': orders_list})

#     except Exception as e:
#         import traceback
#         traceback.print_exc() # Print detailed error to console
#         return jsonify({'status': 'error', 'message': str(e)}), 500


# def handle_cancel_order(request_data):
#     """Cancels an order, compatible with strict schema."""
#     order_id = request_data.get('order_id')
#     if not order_id:
#         return jsonify({'status': 'error', 'message': 'Missing order ID'}), 400

#     session = db.session()
#     try:
#         # Load order with items and payment
#         order = session.query(orders).options(
#             joinedload(orders.order_items),
#             joinedload(orders.payment), # Load the single payment
#             joinedload(orders.shipping) # Load the single shipping
#         ).get(order_id)


#         if not order:
#             return jsonify({'status': 'error', 'message': 'Order not found'}), 404

#         if order.order_status not in ['Pending', 'Processing']:
#             return jsonify({'status': 'error', 'message': f'Cannot cancel an order with status: {order.order_status}'}), 400

#         # --- 1. Restore inventory ---
#         for item in order.order_items:
#             inv_item = session.query(inventory).filter(
#                 inventory.product_id == item.product_id,
#                 inventory.seller_id == order.seller_id
#             ).with_for_update().first()
#             if inv_item:
#                 inv_item.stock_remaining += item.quantity

#         # --- 2. Update Order Status ---
#         order.order_status = 'Cancelled'

#         # --- 3. Update Payment Status (if paid) ---
#         # Access the single payment record correctly
#         if order.payment and order.payment.payment_status == 'Completed':
#              order.payment.payment_status = 'Refunded'


#         # --- 4. Update shipping Status ---
#          # Access the single shipping record correctly
#         if order.shipping:
#              order.shipping.delivery_status = 'Cancelled'


#         session.commit()
#         return jsonify({'status': 'success', 'message': f'Order {order_id} has been cancelled and refunded.'})

#     except Exception as e:
#         session.rollback()
#         import traceback
#         traceback.print_exc() # Print detailed error to console
#         return jsonify({'status': 'error', 'message': str(e)}), 500
#     finally:
#         session.close()


# def handle_return_order(request_data):
#     """Processes a return, compatible with strict schema."""
#     order_id = request_data.get('order_id')
#     if not order_id:
#         return jsonify({'status': 'error', 'message': 'Missing order ID'}), 400

#     session = db.session()
#     try:
#         # Load order with payment and shipping
#         order = session.query(orders).options(
#             joinedload(orders.payment), # Load the single payment
#             joinedload(orders.shipping) # Load the single shipping
#         ).get(order_id)


#         if not order:
#             return jsonify({'status': 'error', 'message': 'Order not found'}), 404

#         if order.order_status not in ['Shipped', 'Delivered']:
#             return jsonify({'status': 'error', 'message': f'Cannot return an order with status: {order.order_status}'}), 400

#         # --- 1. Update Order Status ---
#         order.order_status = 'Returned'

#         # --- 2. Update Payment Status ---
#         # Access the single payment record correctly
#         if order.payment:
#              order.payment.payment_status = 'Refunded'


#         # --- 3. Update shipping Status & Set Return Date ---
#          # Access the single shipping record correctly
#         if order.shipping:
#              order.shipping.delivery_status = 'Returned'
#              return_days = 6 + (datetime.datetime.now().microsecond % 2) # 6 or 7 days
#              order.shipping.return_date = datetime.date.today() + datetime.timedelta(days=return_days)


#         session.commit()
#          # Access the single shipping record correctly
#         return_date_str = order.shipping.return_date.strftime('%Y-%m-%d') if order.shipping and order.shipping.return_date else 'N/A'

#         return jsonify({
#             'status': 'success',
#             'message': f'Order {order_id} return processed. Refund initiated. Pickup scheduled for {return_date_str}.'
#         })

#     except Exception as e:
#         session.rollback()
#         import traceback
#         traceback.print_exc() # Print detailed error to console
#         return jsonify({'status': 'error', 'message': str(e)}), 500
#     finally:
#         session.close()






from flask import jsonify
# Import lowercase models consistent with your models.py
from models import db, products, inventory, sellers, orders, order_items, shipping, payments
# *** MODIFIED: Removed contains_eager from imports ***
from sqlalchemy.orm import joinedload
from sqlalchemy import func # Import func for now()
import datetime
import traceback # Import traceback for detailed error logging

def handle_checkout(request_data):
    """
    Handles the checkout of an entire cart, compatible with the strict original schema.
    """
    customer_id = request_data.get('customer_id')
    seller_id = request_data.get('seller_id')
    cart_items = request_data.get('items') # Expects a list of {'product_id': X, 'quantity': Y}

    if not all([customer_id, seller_id, cart_items]):
        return jsonify({'status': 'error', 'message': 'Missing checkout data'}), 400

    session = db.session()
    try:
        total_price = 0.0 # Use float explicitly
        order_items_to_create = []

        # --- 1. Validate cart and lock inventory ---
        for item in cart_items:
            product_id = item['product_id']
            quantity_to_buy = int(item['quantity'])

            inv_item = session.query(inventory).filter(
                inventory.product_id == product_id,
                inventory.seller_id == seller_id
            ).with_for_update().first()

            if not inv_item or inv_item.stock_remaining < quantity_to_buy:
                session.rollback()
                product = session.query(products).get(product_id)
                product_name = product.product_name if product else f"Product ID {product_id}"
                return jsonify({
                    'status': 'error',
                    'message': f'Not enough stock for {product_name}. Please update your cart.'
                }), 400

            inv_item.stock_remaining -= quantity_to_buy

            product = session.query(products).get(product_id)
            price_per_unit = float(product.price)
            item_total_price = price_per_unit * quantity_to_buy
            total_price += item_total_price

            order_items_to_create.append(
                order_items(
                    product_id=product_id,
                    quantity=quantity_to_buy,
                    price_per_unit=price_per_unit, # float
                    total_price=item_total_price  # float
                )
            )

        # --- 2. Create the main Order ---
        new_order = orders(
            customer_id=customer_id,
            order_status='Pending',
            seller_id=seller_id,
            order_date=datetime.date.today() # DATE
        )
        session.add(new_order)
        session.flush()

        # --- 3. Create shipping Record ---
        shipping_days = 4 + (datetime.datetime.now().microsecond % 2)
        est_shipping_date = datetime.date.today() + datetime.timedelta(days=shipping_days) # DATE

        new_shipping = shipping(
            order_id=new_order.order_id, # Link via ID
            delivery_status='Processing',
            shipping_date=est_shipping_date
        )
        session.add(new_shipping)

        # --- 4. Add order_items to the Order ---
        for oi in order_items_to_create:
            oi.order_id = new_order.order_id # Link via ID
            session.add(oi)

        # --- 5. Commit the entire transaction ---
        session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Order created! Proceed to payment.',
            'order_id': new_order.order_id,
            'total_price': float(total_price)
        })

    except Exception as e:
        session.rollback()
        print("--- ERROR during checkout ---")
        traceback.print_exc()
        print("-----------------------------")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        session.close()


def handle_get_orders(request_data):
    """Fetches all orders, joining to products to get item names."""
    customer_id = request_data.get('customer_id')
    if not customer_id:
        return jsonify({'status': 'error', 'message': 'Missing customer ID'}), 400

    print(f"\n[handle_get_orders] Fetching orders for customer_id: {customer_id}") # DEBUG
    try:
        # *** MODIFIED: Use LAZY loading for shipping, REMOVE outerjoin and contains_eager ***
        orders_query = orders.query.options(
            joinedload(orders.order_items).joinedload(order_items.product),
            # REMOVED contains_eager(orders.shipping)
            joinedload(orders.payment), # Eager load payment
            joinedload(orders.seller)
        # REMOVED outerjoin(shipping, ...)
        ).filter(orders.customer_id == customer_id).order_by(orders.order_date.desc()).all()


        print(f"[handle_get_orders] Found {len(orders_query)} orders for customer.") # DEBUG

        orders_list = []
        for i, order in enumerate(orders_query): # 'order' is an INSTANCE
            print(f"\n[handle_get_orders] --- Processing order index {i}, ID={order.order_id}, Type={type(order)} ---") # DEBUG

            # Safely process payment
            payment_status = 'N/A'
            try:
                # Access payment relationship on the INSTANCE 'order'
                if hasattr(order, 'payment') and order.payment is not None:
                     if isinstance(order.payment, list) and len(order.payment) > 0:
                         payment_status = order.payment[0].payment_status
                     elif not isinstance(order.payment, list):
                          payment_status = order.payment.payment_status
            except Exception as payment_err:
                 print(f"[!!! handle_get_orders] Error accessing payment for Order ID {order.order_id}: {payment_err}")
                 traceback.print_exc()


            # Safely calculate total price
            current_total_price = 0.0
            try:
                current_total_price = sum(float(item.total_price) for item in order.order_items)
            except Exception as price_err:
                 print(f"[!!! handle_get_orders] Error calculating total price for Order ID {order.order_id}: {price_err}")
                 traceback.print_exc()


            # --- Safely Prepare shipping_info dictionary (Lazy Loaded) ---
            shipping_info_dict = None
            print(f"[handle_get_orders] Attempting to LAZILY access shipping for order ID {order.order_id}...") # DEBUG
            try:
                # *** Access order.shipping HERE to trigger lazy load ***
                # This relies on the backref='shipping' in the shipping model
                # Use getattr for extra safety, though direct access should work
                order_shipping_instance = getattr(order, 'shipping', None)

                if order_shipping_instance is not None:
                    print(f"[handle_get_orders] Shipping instance LAZILY loaded for Order ID {order.order_id}: Type={type(order_shipping_instance)}") # DEBUG
                    shipping_info_dict = {
                         'status': getattr(order_shipping_instance, 'delivery_status', 'N/A'),
                         'estimated_arrival': order_shipping_instance.shipping_date.strftime('%Y-%m-%d') if getattr(order_shipping_instance, 'shipping_date', None) else 'N/A',
                         'return_date': order_shipping_instance.return_date.strftime('%Y-%m-%d') if getattr(order_shipping_instance, 'return_date', None) else None
                     }
                else:
                    print(f"[handle_get_orders] No associated shipping record found (lazy load) for Order ID {order.order_id}.") # DEBUG

            # --- CATCH THE SPECIFIC ERROR ---
            except AttributeError as ae_shipping:
                 print(f"[!!! CRITICAL ATTRIBUTE ERROR accessing shipping details for Order ID {order.order_id} !!!]")
                 print(f"Object causing error: repr={repr(order)}")
                 print(f"Type of object: {type(order)}")
                 # Check the CLASS again, just in case
                 print(f"Does 'orders' CLASS have 'shipping' attribute? {hasattr(orders, 'shipping')}")
                 traceback.print_exc() # Print full traceback
                 print("----------------------------------------------------------------------------------")
                 shipping_info_dict = {'status': 'Error Loading Shipping', 'estimated_arrival': 'N/A', 'return_date': None}
            except Exception as ship_err:
                 print(f"[!!! UNEXPECTED ERROR preparing shipping info for Order ID {order.order_id} !!!]")
                 traceback.print_exc()
                 shipping_info_dict = {'status': 'Error Loading Shipping', 'estimated_arrival': 'N/A', 'return_date': None}

            # --- End safe preparation ---

            # Safely prepare items list
            items_list = []
            try:
                 items_list = [{
                    'name': item.product.product_name if hasattr(item, 'product') and item.product else 'Unknown Product',
                    'quantity': getattr(item, 'quantity', 0),
                    'price': float(getattr(item, 'total_price', 0.0))
                } for item in order.order_items]
            except Exception as item_err:
                 print(f"[!!! handle_get_orders] Error processing items for Order ID {order.order_id}: {item_err}")
                 traceback.print_exc()


            # --- Assemble final dictionary ---
            order_data = {
                'order_id': order.order_id,
                'order_date': order.order_date.strftime('%Y-%m-%d') if order.order_date else 'N/A',
                'order_status': order.order_status,
                'seller_name': order.seller.seller_name if hasattr(order, 'seller') and order.seller else 'N/A',
                'items': items_list,
                'shipping_info': shipping_info_dict,
                'payment_status': payment_status,
                'total_price': float(current_total_price)
            }
            orders_list.append(order_data)

        print(f"\n[handle_get_orders] Finished processing. Returning {len(orders_list)} orders.") # DEBUG
        return jsonify({'status': 'success', 'orders': orders_list})

    except AttributeError as ae:
        print(f"--- TOP LEVEL ATTRIBUTE ERROR in handle_get_orders ---")
        traceback.print_exc()
        print("------------------------------------------------------")
        return jsonify({'status': 'error', 'message': f"Attribute error: {str(ae)}"}), 500
    except Exception as e:
        print(f"--- GENERAL ERROR in handle_get_orders for customer {customer_id} ---")
        traceback.print_exc()
        print("---------------------------------------")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# --- handle_cancel_order ---
# (Keep previous version - logic seems correct for lazy loading too)
def handle_cancel_order(request_data):
    """Cancels an order, compatible with strict schema."""
    order_id = request_data.get('order_id')
    if not order_id:
        return jsonify({'status': 'error', 'message': 'Missing order ID'}), 400

    session = db.session()
    try:
        # Load order with items, payment, and shipping (will lazy load if not specified)
        order = session.query(orders).options(
            joinedload(orders.order_items),
            # Let payment and shipping lazy load when accessed
        ).get(order_id)

        if not order:
            return jsonify({'status': 'error', 'message': 'Order not found'}), 404

        if order.order_status not in ['Pending', 'Processing']:
            return jsonify({'status': 'error', 'message': f'Cannot cancel an order with status: {order.order_status}'}), 400

        # --- 1. Restore inventory ---
        for item in order.order_items:
            inv_item = session.query(inventory).filter(
                inventory.product_id == item.product_id,
                inventory.seller_id == order.seller_id
            ).with_for_update().first()
            if inv_item:
                inv_item.stock_remaining += item.quantity

        # --- 2. Update Order Status ---
        order.order_status = 'Cancelled'

        # --- 3. Update Payment Status (if paid) ---
        if hasattr(order, 'payment') and order.payment:
             payment_list = order.payment if isinstance(order.payment, list) else [order.payment]
             for payment_to_update in payment_list:
                 if payment_to_update and payment_to_update.payment_status == 'Completed':
                      payment_to_update.payment_status = 'Refunded'

        # --- 4. Update shipping Status ---
        if hasattr(order, 'shipping') and order.shipping:
             order.shipping.delivery_status = 'Cancelled'

        session.commit()
        return jsonify({'status': 'success', 'message': f'Order {order_id} has been cancelled and refunded.'})

    except Exception as e:
        session.rollback()
        print(f"--- ERROR cancelling order {order_id} ---")
        traceback.print_exc()
        print("------------------------------------")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        session.close()


# --- handle_return_order ---
# (Keep previous version - logic seems correct for lazy loading too)
def handle_return_order(request_data):
    """Processes a return, compatible with strict schema."""
    order_id = request_data.get('order_id')
    if not order_id:
        return jsonify({'status': 'error', 'message': 'Missing order ID'}), 400

    session = db.session()
    try:
        # Load order with payment and shipping (will lazy load)
        order = session.query(orders).options(
             # Let relationships lazy load
        ).get(order_id)

        if not order:
            return jsonify({'status': 'error', 'message': 'Order not found'}), 404

        if order.order_status not in ['Shipped', 'Delivered']:
            return jsonify({'status': 'error', 'message': f'Cannot return an order with status: {order.order_status}'}), 400

        # --- 1. Update Order Status ---
        order.order_status = 'Returned'

        # --- 2. Update Payment Status ---
        if hasattr(order, 'payment') and order.payment:
             payment_list = order.payment if isinstance(order.payment, list) else [order.payment]
             for payment_to_update in payment_list:
                  if payment_to_update:
                       payment_to_update.payment_status = 'Refunded'


        # --- 3. Update shipping Status & Set Return Date ---
        if hasattr(order, 'shipping') and order.shipping:
             order.shipping.delivery_status = 'Returned'
             return_days = 6 + (datetime.datetime.now().microsecond % 2) # 6 or 7 days
             order.shipping.return_date = datetime.date.today() + datetime.timedelta(days=return_days)

        session.commit()
        return_date_str = order.shipping.return_date.strftime('%Y-%m-%d') if hasattr(order, 'shipping') and order.shipping and order.shipping.return_date else 'N/A'

        return jsonify({
            'status': 'success',
            'message': f'Order {order_id} return processed. Refund initiated. Pickup scheduled for {return_date_str}.'
        })

    except Exception as e:
        session.rollback()
        print(f"--- ERROR returning order {order_id} ---")
        traceback.print_exc()
        print("-----------------------------------")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        session.close()



