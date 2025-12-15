from flask import jsonify
from models import db, orders, payments, transaction_log
import hashlib

def handle_pay(request_data):
    # Checks the payment of the order 
    order_id = request_data.get('order_id')
    payment_mode = request_data.get('payment_mode')
    payment_identifier = request_data.get('payment_identifier') # e.g., UPI ID
    
    if not payment_identifier:
        return jsonify({'status': 'error', 'message': 'Payment identifier (e.g., UPI ID) is required.'}), 400

    hashed_data = hashlib.sha256(payment_identifier.encode()).hexdigest()

    try:
        order = orders.query.get(order_id)
        if not order:
             return jsonify({'status': 'error', 'message': 'Order not found'}), 404

        # 1. Create the Payment record
        new_payment = payments(
            order_id=order_id,
            payment_mode=payment_mode,
            payment_status='Completed',
            payment_identifier=payment_identifier
        )
        db.session.add(new_payment)
        
        # 2. Create the Transaction log with the hash
        new_log = transaction_log(
            order_id=order_id,
            payment_hash=hashed_data
        )
        db.session.add(new_log)

        # 3. Update the Order status
        order.order_status = 'Processing'
        
        db.session.commit()
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
    return jsonify({
        'status': 'success',
        'message': 'Payment successful! Your order is being processed.',
        'transaction_hash': hashed_data
    })
