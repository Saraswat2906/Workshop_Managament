from flask import jsonify
from models import db, customers

def handle_register(request_data):
    #Handles user registration and login.
    username = request_data.get('username')
    phone_no = request_data.get('phone_no')

    if not username or not phone_no:
        return jsonify({'status': 'error', 'message': 'Username and phone number are required'}), 400

    # Check if user already exists
    existing_user = db.session.query(customers).filter(
        (customers.username == username) | (customers.phone_no == phone_no)
    ).first()

    if existing_user:
        return jsonify({
            'status': 'existing',
            'message': 'Account is already registered',
            'customer_id': existing_user.customer_id
        })
    
    # Create new user
    new_user = customers(username=username, phone_no=phone_no)
    db.session.add(new_user)
    try:
        db.session.commit()
        return jsonify({
            'status': 'created',
            'message': 'Account created successfully',
            'customer_id': new_user.customer_id
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Database error: {str(e)}'}), 500