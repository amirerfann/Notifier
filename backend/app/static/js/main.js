document.addEventListener('DOMContentLoaded', function() {
    // Global alert container
    const alertContainer = document.createElement('div');
    alertContainer.id = 'alert-container';
    document.body.appendChild(alertContainer);

    // Check if we are on the dashboard page by looking for specific elements
    const bitcoinPriceElement = document.getElementById('bitcoin-price');
    const goldPriceElement = document.getElementById('gold-price');
    const notifyBitcoinButton = document.getElementById('notify-bitcoin');
    const notifyGoldButton = document.getElementById('notify-gold');

    if (bitcoinPriceElement && goldPriceElement) {
        fetchData('bitcoin', bitcoinPriceElement);
        fetchData('gold', goldPriceElement);
    }

    if (notifyBitcoinButton) {
        notifyBitcoinButton.addEventListener('click', () => sendNotification('bitcoin'));
    }

    if (notifyGoldButton) {
        notifyGoldButton.addEventListener('click', () => sendNotification('gold'));
    }

    // Handle login form submission if it exists on the page
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(event) {
            event.preventDefault();
            const formData = new FormData(loginForm);
            const data = Object.fromEntries(formData.entries());

            try {
                // Note: Flask-Login uses session cookies, direct API login for SPA is different.
                // This example assumes the form POSTs to Flask, which handles session.
                // If building a true SPA with token auth, this would be an API call.
                // For now, this JS won't hijack the form if it's a simple Flask form.
                // If we want JS-driven login, the HTML should not have action/method,
                // and we'd use fetch to POST to /auth/login API endpoint.
                // The current backend /auth/login expects form data and redirects.
                // To make it work with JS fetch, it should return JSON.
                // For now, we assume standard form submission for login/register.
                showAlert('Login form submitted (standard POST, not via JS fetch).', 'info');

            } catch (error) {
                console.error('Login error:', error);
                showAlert(`Login failed: ${error.message}`, 'danger');
            }
        });
    }
});

async function fetchData(asset, element) {
    try {
        const response = await fetch(`/api/data/${asset}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        if (data.success) {
            element.textContent = `$${data.price_usd.toFixed(2)}`;
        } else {
            element.textContent = 'Error';
            showAlert(`Error fetching ${asset} price: ${data.message}`, 'danger');
            console.error(`Error fetching ${asset} price:`, data.message);
        }
    } catch (error) {
        element.textContent = 'Error';
        showAlert(`Error fetching ${asset} price: ${error.message}`, 'danger');
        console.error(`Error fetching ${asset} price:`, error);
    }
}

async function sendNotification(asset) {
    showAlert(`Sending ${asset} notification...`, 'info', 2000);
    try {
        const response = await fetch(`/api/notify/${asset}`, { method: 'POST' });
        const data = await response.json(); // Always parse JSON, even for errors
        if (response.ok && data.success) {
            showAlert(data.message || `${asset.charAt(0).toUpperCase() + asset.slice(1)} notification sent successfully!`, 'success');
        } else {
            // Prefer message from backend if available
            const errorMessage = data.message || `Failed to send ${asset} notification. Status: ${response.status}`;
            showAlert(errorMessage, 'danger');
            console.error(`Error sending ${asset} notification:`, data.message || response.statusText);
        }
    } catch (error) {
        showAlert(`Client-side error sending ${asset} notification: ${error.message}`, 'danger');
        console.error(`Client-side error sending ${asset} notification:`, error);
    }
}

function showAlert(message, type = 'info', duration = 5000) {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) {
        console.error("Alert container not found!");
        // Fallback to browser alert if container is missing
        alert(`${type.toUpperCase()}: ${message}`);
        return;
    }

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;

    alertContainer.appendChild(alertDiv);

    setTimeout(() => {
        alertDiv.style.opacity = '0';
        setTimeout(() => {
            alertDiv.remove();
        }, 600); // Allow time for fade out animation
    }, duration);
}

// Example: If there's a 'Link Telegram' form that we want to handle with JS
// const linkTelegramForm = document.getElementById('link-telegram-form');
// if (linkTelegramForm) {
//     linkTelegramForm.addEventListener('submit', async function(event) {
//         event.preventDefault();
//         const formData = new FormData(linkTelegramForm);
//         const chat_id = formData.get('chat_id');
//
//         try {
//             // This endpoint should be created in the backend if it doesn't exist
//             // or if the existing /auth/link_telegram needs to return JSON for JS clients
//             const response = await fetch('/api/user/link_telegram', { // Assuming an API endpoint
//                 method: 'POST',
//                 headers: { 'Content-Type': 'application/json' },
//                 body: JSON.stringify({ chat_id })
//             });
//             const data = await response.json();
//             if (response.ok && data.success) {
//                 showAlert('Telegram account linked successfully!', 'success');
//                 // Optionally, update UI or redirect
//                 window.location.href = '/dashboard'; // Or update parts of the page
//             } else {
//                 showAlert(data.message || 'Failed to link Telegram account.', 'danger');
//             }
//         } catch (error) {
//             showAlert(`Error linking Telegram: ${error.message}`, 'danger');
//         }
//     });
// }
