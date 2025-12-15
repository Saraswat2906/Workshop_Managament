async function login() {
    const username = document.getElementById('username').value;
    const phone = document.getElementById('phone').value;
    const messageEl = document.getElementById('message');

    // Basic validation
    if (!username || !phone) {
        messageEl.textContent = 'Please enter both username and phone number.';
        return;
    }
    
    // Check if phone number is numeric (to match BIGINT)
    if (isNaN(phone) || phone.includes('.')) {
        messageEl.textContent = 'Phone number must contain only digits.';
        return;
    }


    const response = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: username, phone_no: phone })
    });

    const result = await response.json();
    messageEl.textContent = result.message;

    if (result.status === 'created' || result.status === 'existing') {
        localStorage.setItem('customer_id', result.customer_id);
        localStorage.setItem('username', username); // <-- SAVES USERNAME
        window.location.href = '/shop';
    }
}

