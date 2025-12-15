document.addEventListener('DOMContentLoaded', loadOrders);

const tabs = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');
const loadingEl = document.getElementById('loading');

const lists = {
    current: document.getElementById('current-orders-list'),
    previous: document.getElementById('previous-orders-list'),
    cancelled: document.getElementById('cancelled-orders-list')
};
const emptyStates = {
    current: document.getElementById('current-empty'),
    previous: document.getElementById('previous-empty'),
    cancelled: document.getElementById('cancelled-empty')
};

function openTab(tabName) {
    tabs.forEach(tab => tab.classList.remove('active'));
    tabContents.forEach(content => content.classList.remove('active'));
    
    document.querySelector(`.tab-btn[onclick="openTab('${tabName}')"]`).classList.add('active');
    document.getElementById(tabName).classList.add('active');
}

async function loadOrders() {
    const customer_id = localStorage.getItem('customer_id');
    if (!customer_id) {
        window.location.href = '/'; // Not logged in
        return;
    }

    try {
        const response = await fetch('/api/get_orders', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ customer_id: parseInt(customer_id) })
        });
        const data = await response.json();
        loadingEl.style.display = 'none';

        if (data.status === 'success' && data.orders.length > 0) {
            sortAndRenderOrders(data.orders);
        } else if (data.status === 'success') {
            // No orders found
            showAllEmptyStates();
        } else {
            document.getElementById('current').innerHTML = `<p>Error loading orders: ${data.message}</p>`;
        }
    } catch (err) {
        loadingEl.style.display = 'none';
        document.getElementById('current').innerHTML = `<p>Could not connect to server.</p>`;
    }
}

function sortAndRenderOrders(orders) {
    let counts = { current: 0, previous: 0, cancelled: 0 };
    
    // Clear lists
    lists.current.innerHTML = '';
    lists.previous.innerHTML = '';
    lists.cancelled.innerHTML = '';

    orders.forEach(order => {
        const orderCardHtml = createOrderCard(order);
        
        if (['Cancelled', 'Returned'].includes(order.order_status)) {
            lists.cancelled.innerHTML += orderCardHtml;
            counts.cancelled++;
        } else if (['Shipped', 'Delivered'].includes(order.order_status)) {
            lists.previous.innerHTML += orderCardHtml;
            counts.previous++;
        } else {
            // 'Pending', 'Processing'
            lists.current.innerHTML += orderCardHtml;
            counts.current++;
        }
    });

    // Show empty states if no orders in a category
    if (counts.current === 0) emptyStates.current.style.display = 'block';
    if (counts.previous === 0) emptyStates.previous.style.display = 'block';
    if (counts.cancelled === 0) emptyStates.cancelled.style.display = 'block';
}

function showAllEmptyStates() {
    loadingEl.style.display = 'none';
    emptyStates.current.style.display = 'block';
    emptyStates.previous.style.display = 'block';
    emptyStates.cancelled.style.display = 'block';
}

function createOrderCard(order) {
    const itemsHtml = order.items.map(item => `
        <div class="order-item">
            <div class="order-item-name"><span>${item.quantity}</span> x ${item.name}</div>
            <div class="order-item-price">$${item.price.toFixed(2)}</div>
        </div>
    `).join('');

    const statusClass = `status-${order.order_status.toLowerCase()}`;
    let footerButtons = '';
    
    // Add "Cancel" button for 'Pending' or 'Processing' orders
    if (['Pending', 'Processing'].includes(order.order_status)) {
        footerButtons = `<button class="btn btn-danger" onclick="cancelOrder(${order.order_id})">Cancel Order</button>`;
    }
    
    // Add "Return" button for 'Shipped' or 'Delivered' orders
    if (['Shipped', 'Delivered'].includes(order.order_status)) {
        footerButtons = `<button class="btn btn-secondary" onclick="returnOrder(${order.order_id})">Return Order</button>`;
    }
    
    return `
    <div class="order-card" id="order-card-${order.order_id}">
        <div class="order-header">
            <div class="order-header-info">
                <strong>Order #${order.order_id}</strong><br>
                Placed on: ${order.order_date}
            </div>
            <div class="order-status ${statusClass}">${order.order_status}</div>
        </div>
        <div class="order-body">
            <div class="order-shipping-info">
                <strong>Sold by:</strong> ${order.seller_name}<br>
                <strong>Est. Arrival:</strong> ${order.shipping_info?.estimated_arrival || 'N/A'}
                ${order.shipping_info?.return_date ? `<br><strong>Return Pickup:</strong> ${order.shipping_info.return_date}` : ''}
            </div>
            <hr style="border:0; border-top: 1px dashed #eee; margin: 1rem 0;">
            ${itemsHtml}
            <div class="order-total">
                Total: $${order.total_price.toFixed(2)}
            </div>
        </div>
        <div class="order-footer">
            ${footerButtons}
        </div>
    </div>
    `;
}

// --- API Actions ---

async function cancelOrder(orderId) {
    if (!confirm(`Are you sure you want to cancel Order #${orderId}? This cannot be undone.`)) {
        return;
    }

    const response = await fetch('/api/cancel_order', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ order_id: orderId })
    });
    
    const result = await response.json();
    if (result.status === 'success') {
        alert(result.message);
        loadOrders(); // Refresh all orders
    } else {
        alert(`Error: ${result.message}`);
    }
}

async function returnOrder(orderId) {
    if (!confirm(`Are you sure you want to return Order #${orderId}?`)) {
        return;
    }
    
    const response = await fetch('/api/return_order', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ order_id: orderId })
    });
    
    const result = await response.json();
    if (result.status === 'success') {
        alert(result.message);
        loadOrders(); // Refresh all orders
    } else {
        alert(`Error: ${result.message}`);
    }
}

