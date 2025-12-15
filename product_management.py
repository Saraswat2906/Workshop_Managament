from flask import jsonify
from models import db, products, inventory, sellers

def handle_get_products():
    # Fetches all available products from all sellers.
    try:
        # Query products that have inventory
        products_query = products.query.join(inventory).join(sellers).filter(
            inventory.stock_remaining > 0
        ).all()
        
        # Structure the data for the frontend
        products_list = []
        for p in products_query:
            # For each product, find its inventory listings
            for inv in p.inventory:
                if inv.stock_remaining > 0:
                    products_list.append({
                        'product_id': p.product_id,
                        'product_name': p.product_name,
                        'price': float(p.price),
                        'seller_name': inv.seller.seller_name,
                        'seller_id': inv.seller.seller_id,
                        'stock_remaining': inv.stock_remaining
                    })

        return jsonify({'status': 'success', 'products': products_list})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
