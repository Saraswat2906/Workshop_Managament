document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const order_id = urlParams.get('order_id');
    const amount = urlParams.get('amount');

    if (!order_id || !amount) {
        document.getElementById('payment-form').innerHTML = '<h2>Error: Invalid order details.</h2>';
        return;
    }

    document.getElementById('order_id').textContent = order_id;
    document.getElementById('amount').textContent = amount;
});

async function pay() {
    const order_id = document.getElementById('order_id').textContent;
    const upiId = document.getElementById('upi_id').value;
    const messageEl = document.getElementById('payment-message');
    
    if (!upiId) {
        messageEl.textContent = 'Please enter a UPI ID.';
        return;
    }

    messageEl.textContent = 'Processing payment...';

    const response = await fetch('/api/pay', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            order_id: order_id,
            payment_mode: 'UPI',
            payment_identifier: upiId
        })
    });

    const result = await response.json();
    messageEl.textContent = result.message;

    if (result.status === 'success') {
        document.getElementById('payment-form').innerHTML = `
            <h2>Payment Successful!</h2>
            <p>Your order is being processed.</p>
            <p>Transaction Hash: ${result.transaction_hash}</p>
            <a href="/shop">Back to Shop</a>
        `;
    }
}
