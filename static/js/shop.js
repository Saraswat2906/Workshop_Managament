// --- Global State ---
let allProducts = []; // To store product data from API
let cart = {}; // { product_id: quantity }
let currentSellerId = null;
let currentSellerName = null;

const cartBar = document.getElementById('cart-bar');
const cartItemCount = document.getElementById('cart-item-count');
const cartSeller = document.getElementById('cart-seller');
const productList = document.getElementById('product-list');
const modal = document.getElementById('modal');
const modalMessage = document.getElementById('modal-message');
const modalButtons = document.getElementById('modal-buttons');

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    loadProducts();
    updateProfileIcon();
    updateCartBar();
});

function updateProfileIcon() {
    const username = localStorage.getItem('username');
    const profileLink = document.getElementById('profile-link');
    if (username) {
        profileLink.textContent = username.charAt(0).toUpperCase();
    } else {
        profileLink.textContent = '?'; // Default
    }
}

async function loadProducts() {
    const customer_id = localStorage.getItem('customer_id');
    if (!customer_id) {
        window.location.href = '/'; // Redirect to login if not logged in
        return;
    }

    try {
        const response = await fetch('/api/products');
        const data = await response.json();

        if (data.status === 'success') {
            allProducts = data.products;
            renderProducts();
        } else {
            productList.innerHTML = '<p>Could not load products.</p>';
        }
    } catch (error) {
        productList.innerHTML = '<p>Error loading products. Please try again.</p>';
    }
}

function renderProducts() {
    productList.innerHTML = ''; // Clear existing
    allProducts.forEach(product => {
        const productEl = document.createElement('div');
        productEl.className = 'product';
        productEl.innerHTML = `
            <div>
                <h3>${product.product_name}</h3>
                <div class="product-price">$${product.price}</div>
                <div class="product-seller">Sold by: <strong>${product.seller_name}</strong></div>
            </div>
            <div id="controls-${product.product_id}">
                ${renderControls(product)}
            </div>
        `;
        productList.appendChild(productEl);
    });
}

function renderControls(product) {
    const quantityInCart = cart[product.product_id] || 0;

    // NOTE: product.price is a string from the API (a float/decimal). 
    // It's used for display, so it's fine.
    if (product.stock_remaining === 0) {
        return `<button class="notify-btn" onclick="notifyMe(${product.product_id})">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>
                    Notify Me
                </button>`;
    }

    if (quantityInCart > 0) {
        return `
            <div class="quantity-controls">
                <button class="quantity-btn" onclick="updateQuantity(${product.product_id}, -1)">-</button>
                <div class="quantity-display">${quantityInCart}</div>
                <button class="quantity-btn" onclick="addToCart(${product.product_id})">+</button>
            </div>
        `;
    } else {
        return `
            <button class="add-btn" onclick="addToCart(${product.product_id})">
                <span class="add-btn-plus">+</span> ADD
            </button>
        `;
    }
}

// --- Cart Logic ---

function addToCart(productId) {
    const product = allProducts.find(p => p.product_id === productId);
    if (!product) return;

    // 1. Check Seller Conflict
    if (cartIsEmpty() || product.seller_id === currentSellerId) {
        currentSellerId = product.seller_id;
        currentSellerName = product.seller_name;
        updateQuantity(productId, 1);
    } else {
        // Seller conflict! Show modal.
        showModal(
            `Your cart contains items from <strong>${currentSellerName}</strong>. Do you want to clear your cart and add this item from <strong>${product.seller_name}</strong>?`,
            () => { // On Confirm
                clearCart();
                updateQuantity(productId, 1); // Add the new item
            }
        );
    }
}

function updateQuantity(productId, change) {
    const product = allProducts.find(p => p.product_id === productId);
    let quantityInCart = cart[product.product_id] || 0;

    const newQuantity = quantityInCart + change;

    // Check stock limit
    if (newQuantity > product.stock_remaining) {
        showModal(`Sorry, you can only add up to ${product.stock_remaining} of this item.`, null, 'OK');
        return;
    }

    if (newQuantity <= 0) {
        delete cart[product.product_id];
        if (cartIsEmpty()) {
            currentSellerId = null;
            currentSellerName = null;
        }
    } else {
        cart[product.product_id] = newQuantity;
    }

    // Re-render controls for this product
    document.getElementById(`controls-${productId}`).innerHTML = renderControls(product);
    updateCartBar();
}

function clearCart() {
    cart = {};
    currentSellerId = null;
    currentSellerName = null;
    renderProducts(); // Re-render all products to show "ADD" buttons
    updateCartBar();
}

function cartIsEmpty() {
    return Object.keys(cart).length === 0;
}

function updateCartBar() {
    if (cartIsEmpty()) {
        cartBar.classList.remove('visible');
        return;
    }

    let totalItems = 0;
    let totalPrice = 0;
    for (const productId in cart) {
        const quantity = cart[productId];
        const product = allProducts.find(p => p.product_id == productId);
        
        totalItems += quantity;
        totalPrice += (parseFloat(product.price) * quantity); // Use parseFloat for safety
    }

    cartItemCount.textContent = `${totalItems} Item${totalItems > 1 ? 's' : ''} | $${totalPrice.toFixed(2)}`;
    cartSeller.textContent = `from ${currentSellerName}`;
    cartBar.classList.add('visible');
}

// --- API Calls ---

async function proceedToCheckout() {
    const customer_id = localStorage.getItem('customer_id');
    const itemsForAPI = Object.keys(cart).map(productId => ({
        product_id: parseInt(productId),
        quantity: cart[productId]
    }));

    const payload = {
        customer_id: parseInt(customer_id),
        seller_id: currentSellerId,
        items: itemsForAPI
    };

    try {
        const response = await fetch('/api/checkout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const result = await response.json();

        if (result.status === 'success') {
            // Success! Redirect to payment page
            window.location.href = `/payment?order_id=${result.order_id}&amount=${result.total_price}`;
        } else {
            // e.g., "Not enough stock" if someone bought it first
            showModal(result.message, null, 'OK');
            // We should reload products to get latest stock
            loadProducts();
        }
    } catch (err) {
        showModal('Could not connect to server. Please try again.', null, 'OK');
    }
}

async function notifyMe(productId) {
    const customer_id = localStorage.getItem('customer_id');
    const response = await fetch('/api/notify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            customer_id: parseInt(customer_id),
            product_id: productId
        })
    });
    const result = await response.json();
    showModal(result.message, null, 'OK');
}

// --- Modal Utility ---
function showModal(message, onConfirm, confirmText = 'Yes') {
    modalMessage.innerHTML = message;
    
    // Clear old buttons/events
    modalButtons.innerHTML = '';
    
    if (onConfirm) {
        // Confirm/Cancel buttons
        const confirmBtn = document.createElement('button');
        confirmBtn.id = 'modal-confirm';
        confirmBtn.className = 'modal-btn';
        confirmBtn.textContent = confirmText;
        confirmBtn.onclick = () => {
            onConfirm();
            modal.style.display = 'none';
        };
        
        const cancelBtn = document.createElement('button');
        cancelBtn.id = 'modal-cancel';
        cancelBtn.className = 'modal-btn';
        cancelBtn.textContent = 'No';
        cancelBtn.onclick = () => {
            modal.style.display = 'none';
        };
        
        modalButtons.appendChild(confirmBtn);
        modalButtons.appendChild(cancelBtn);
    } else {
        // OK-only button
        const okBtn = document.createElement('button');
        okBtn.id = 'modal-cancel';
        okBtn.className = 'modal-btn';
        okBtn.textContent = confirmText; // 'OK'
        okBtn.onclick = () => {
            modal.style.display = 'none';
        };
        modalButtons.appendChild(okBtn);
    }
    
    modal.style.display = 'flex';
}

