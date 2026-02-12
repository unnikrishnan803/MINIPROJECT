// Order Tracking Logic

let activeOrdersInterval;

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    // If we are on the dashboard and not a restaurant
    if (document.getElementById('orders-view')) {
         // Initial fetch is triggered when tab is clicked or view is shown
    }
});

function initOrderTracking() {
    fetchOrders();
    // Poll for updates every 15 seconds
    if (activeOrdersInterval) clearInterval(activeOrdersInterval);
    activeOrdersInterval = setInterval(fetchOrders, 15000);
}

function stopOrderTracking() {
    if (activeOrdersInterval) clearInterval(activeOrdersInterval);
}

// Global variable to store orders
let currentOrders = [];

function fetchOrders() {
    const container = document.getElementById('activeOrdersContainer');
    const historyContainer = document.getElementById('orderHistoryContainer');
    
    // Don't wipe content on refresh if we already have data (to prevent flashing)
    // specific logic handled inside render
    
    const headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken') // Function from script.js
    };
    const token = localStorage.getItem('authToken') || localStorage.getItem('token');
    if (token) headers['Authorization'] = `Token ${token}`;

    fetch('/api/dining-orders/', {
        headers: headers
    })
    .then(res => {
        if (res.status === 401 || res.status === 403) {
            console.warn("Unauthorized to fetch orders. User might need to login.");
            return [];
        }
        return res.json();
    })
    .then(data => {
        const orders = data.results || data;
        currentOrders = orders;
        renderOrders(orders);
    })
    .catch(err => {
        console.error('Error fetching orders:', err);
        if(container) container.innerHTML = '<div style="text-align:center; padding:2rem; color:red;">Failed to load orders.</div>';
    });
}

function renderOrders(orders) {
    const activeContainer = document.getElementById('activeOrdersContainer');
    const historyContainer = document.getElementById('orderHistoryContainer');
    
    if (!activeContainer || !historyContainer) return;

    // Filter Actve vs History
    // Active: Ordered, Preparing, Served (Active until Paid?)
    // Actually, let's say: Ordered, Preparing -> Active. Served, Paid -> History.
    // Or maybe Served is Active? Usually tracking ends when food is served.
    // Let's stick to: Active = ['Ordered', 'Preparing']. History = ['Served', 'Paid', 'Cancelled']
    
    // But wait, if I am eating, I might want to see my current bill/order status?
    // Let's include 'Served' in Active?
    // The prompt says "Order Tracking". Usually distinct from "Order History".
    // I'll put 'Served' in Active for now, and 'Paid' in History.
    
    const activeOrders = orders.filter(o => ['Ordered', 'Preparing', 'Served'].includes(o.status));
    const pastOrders = orders.filter(o => ['Paid', 'Cancelled'].includes(o.status));

    
    // Render Active
    if (activeOrders.length === 0) {
        activeContainer.innerHTML = `
            <div style="text-align: center; padding: 3rem; color: var(--text-secondary);">
                <i class="fas fa-utensils fa-3x" style="opacity: 0.3; margin-bottom: 1rem;"></i>
                <p>No active orders right now.</p>
                <button class="btn btn-primary btn-sm" onclick="showDashboardSection('home-view')">Explore Menu</button>
            </div>
        `;
    } else {
        activeContainer.innerHTML = activeOrders.map(order => createOrderCard(order)).join('');
    }

    // Render History
    if (pastOrders.length === 0) {
        historyContainer.innerHTML = `
            <div style="text-align: center; padding: 3rem; color: var(--text-secondary);">
                <p>No past orders found.</p>
            </div>
        `;
    } else {
        // Calculate Stats
        const totalSpent = pastOrders.reduce((sum, order) => sum + parseFloat(order.total_amount), 0);
        const totalOrders = pastOrders.length;
        
        const statsHtml = `
            <div style="display: flex; gap: 1rem; margin-bottom: 1.5rem;">
                <div class="glass-card" style="flex: 1; padding: 1rem; text-align: center;">
                    <div style="font-size: 0.8rem; color: var(--text-secondary);">Total Orders</div>
                    <div style="font-size: 1.2rem; font-weight: 700; color: white;">${totalOrders}</div>
                </div>
                <div class="glass-card" style="flex: 1; padding: 1rem; text-align: center;">
                    <div style="font-size: 0.8rem; color: var(--text-secondary);">Total Spent</div>
                    <div style="font-size: 1.2rem; font-weight: 700; color: var(--accent-primary);">₹${totalSpent.toFixed(2)}</div>
                </div>
            </div>
        `;
        
        historyContainer.innerHTML = statsHtml + pastOrders.map(order => createOrderCard(order, true)).join('');
    }
}

function createOrderCard(order, isHistory = false) {
    // Format Date
    const date = new Date(order.created_at).toLocaleString();
    
    // Calculate Total Items
    const totalItems = order.items_details.length; // Simplified, assuming 1 qty per item entry or distinct items
    // If the serializer returns a list of items, we might have duplicates if quantity > 1?
    // The model uses ManyToMany. Usually typical usage is ManyToMany for simple "tags".
    // Real order usage would have a "Through" model/association with Quantity.
    // Looking at the code: models.py Line 138: items = models.ManyToManyField(FoodItem)
    // This simple structure doesn't support quantity per item easily unless added multiple times.
    // Assuming serializer returns list of all items (even duplicates).
    
    // Group items for display
    const itemMap = {};
    order.items_details.forEach(item => {
        if(itemMap[item.id]) {
            itemMap[item.id].count++;
        } else {
            itemMap[item.id] = { ...item, count: 1 };
        }
    });
    
    let itemsHtml = '';
    for (const [id, item] of Object.entries(itemMap)) {
        itemsHtml += `
            <div class="order-item-row">
                <span><span class="item-qty">${item.count}x</span> ${item.name}</span>
                <span>${item.currency_symbol || '₹'}${item.price * item.count}</span>
            </div>
        `;
    }

    // Timeline HTML (Only for Active Orders usually, but nice for history too)
    const steps = ['Ordered', 'Preparing', 'Served', 'Paid'];
    let timelineHtml = '';
    
    if (!isHistory) {
        let currentStepIndex = steps.indexOf(order.status);
        if (currentStepIndex === -1 && order.status === 'Ordered') currentStepIndex = 0; // Default
        
        timelineHtml = '<div class="status-timeline">';
        
        const displaySteps = ['Ordered', 'Preparing', 'Served']; // Don't show Paid on active timeline?
        
        displaySteps.forEach((step, index) => {
            let className = 'timeline-step';
            let icon = '';
            
            // Determine Icon
            if (step === 'Ordered') icon = 'fa-clipboard-check';
            if (step === 'Preparing') icon = 'fa-fire';
            if (step === 'Served') icon = 'fa-check';
            
            // Determine Status
            if (index < currentStepIndex) className += ' completed';
            if (index === currentStepIndex) className += ' active';
            if (index === currentStepIndex && step === 'Preparing') className += ' pulse';

            timelineHtml += `
                <div class="${className}">
                    <div class="step-dot">
                        <i class="fas ${icon}"></i>
                    </div>
                    <div class="step-label">${step}</div>
                </div>
            `;
        });
        
        timelineHtml += '</div>';
    } else {
        // Simple Status Badge for History
        timelineHtml = `
            <div style="margin-top: 1rem; text-align: right;">
                <span class="status-badge ${order.status.toLowerCase()}">${order.status}</span>
            </div>
        `;
    }

    return `
        <div class="order-card">
            <div class="order-header">
                <div>
                    <div class="order-id">Order #${order.id}</div>
                    <div class="order-date">${date}</div>
                </div>
                ${!isHistory ? `<span class="status-badge ${order.status.toLowerCase()}">${order.status}</span>` : ''}
            </div>
            
            <div class="restaurant-info">
                <div class="restaurant-icon">
                    <i class="fas fa-store"></i>
                </div>
                <div>
                    <div style="font-weight: 600;">${order.restaurant_name}</div>
                    <div style="font-size: 0.8rem; color: var(--text-secondary);">${order.restaurant_location || ''}</div>
                </div>
            </div>
            
            <div class="order-items">
                ${itemsHtml}
            </div>
            
            <div class="order-total">
                <span>Total Amount</span>
                <span>₹${order.total_amount}</span>
            </div>
            
            ${timelineHtml}
        </div>
    `;
}

function switchOrderTab(tab) {
    const activeBtn = document.querySelectorAll('.tab-btn')[0];
    const historyBtn = document.querySelectorAll('.tab-btn')[1];
    const activeContainer = document.getElementById('activeOrdersContainer');
    const historyContainer = document.getElementById('orderHistoryContainer');
    
    if (tab === 'active') {
        activeBtn.classList.add('active');
        historyBtn.classList.remove('active');
        activeContainer.style.display = 'flex'; // from orders.css .orders-container is flex-col
        historyContainer.style.display = 'none';
    } else {
        activeBtn.classList.remove('active');
        historyBtn.classList.add('active');
        activeContainer.style.display = 'none';
        historyContainer.style.display = 'flex';
    }
}

// Mock/Quick Order Placement for Demo
// Mock/Quick Order Placement for Demo
function placeQuickOrder(foodId) {
    if (!confirm('Place a quick order for this item?')) return;
    
    // Use Session Auth (CSRF) primarily, fallback to Token if exists
    const headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    };
    
    const token = localStorage.getItem('authToken') || localStorage.getItem('token');
    if (token) headers['Authorization'] = `Token ${token}`;

    
    // Fetch item details first
    fetch(`/api/food-items/${foodId}/`, { headers: headers })
    .then(res => {
        if(!res.ok) throw new Error("Failed to fetch item details");
        return res.json();
    })
    .then(item => {
        // Construct basic order payload
        const orderData = {
            restaurant: item.restaurant.id, 
            items: [item.id],
            total_amount: item.price,
            status: 'Ordered'
        };
        
        return fetch('/api/dining-orders/', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(orderData)
        });
    })
    .then(async res => {
        if (res.ok) {
            alert('Order placed successfully! Track it in the Orders tab.');
            // Refresh order view if visible
            const activeContainer = document.getElementById('activeOrdersContainer');
             if (activeContainer && activeContainer.offsetParent !== null) {
                fetchOrders();
            }
            // Update notification count if function exists
            if (window.fetchNotifications) window.fetchNotifications();
        } else {
            const errData = await res.json();
            console.error('Order failed:', errData);
            alert('Failed to place order: ' + (errData.detail || JSON.stringify(errData)));
        }
    })
    .catch(err => {
        console.error(err);
        alert('Error placing order. See console for details.');
    });
}
