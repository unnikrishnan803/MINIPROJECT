/**
 * Deliciae Order Flow Logic
 * Handles Cart, Checkout Mode, and Payment Simulation
 */

document.addEventListener('DOMContentLoaded', () => {
    // Determine page context and init accordingly
    if (window.location.pathname.includes('cart')) initCartPage();
    if (window.location.pathname.includes('checkout')) initCheckoutPage();
});

// --- CART LOGIC ---

function initCartPage() {
    renderCart();
    // Re-render on storage change (sync tabs)
    window.addEventListener('storage', (e) => {
        if(e.key === 'deliciae_cart') renderCart();
    });
}

function renderCart() {
    const cart = JSON.parse(localStorage.getItem('deliciae_cart') || '[]');
    const container = document.getElementById('cartItemsContainer');
    const emptyState = document.getElementById('emptyCartState');
    const content = document.getElementById('cartContent');
    
    if(!container || !emptyState || !content) return;

    if (cart.length === 0) {
        emptyState.classList.remove('hidden');
        emptyState.classList.add('flex');
        content.classList.add('hidden');
        return;
    }

    emptyState.classList.add('hidden');
    emptyState.classList.remove('flex');
    content.classList.remove('hidden');
    
    container.innerHTML = '';
    let subtotal = 0;

    cart.forEach((item, index) => {
        const itemTotal = item.price * item.quantity;
        subtotal += itemTotal;
        
        container.innerHTML += `
            <div class="glass-panel p-4 flex gap-4 items-center animate-fade-in">
                <img src="${item.image || 'https://placehold.co/80'}" class="cart-item-image">
                <div class="flex-1">
                    <h4 class="font-bold text-lg text-white">${item.name}</h4>
                    <p class="text-sm text-gray-500">${item.restaurant || 'Deliciae Kitchen'}</p>
                    <div class="mt-2 font-bold text-[#FF6B35]">₹${item.price}</div>
                </div>
                
                <div class="flex items-center gap-3 bg-[#151515] rounded-lg p-1 border border-white/5">
                    <button onclick="updateQty(${index}, -1)" class="w-8 h-8 flex items-center justify-center text-gray-400 hover:text-white hover:bg-white/10 rounded transition-colors">-</button>
                    <span class="font-bold w-4 text-center text-sm">${item.quantity}</span>
                    <button onclick="updateQty(${index}, 1)" class="w-8 h-8 flex items-center justify-center text-[#FF6B35] hover:bg-white/10 rounded transition-colors">+</button>
                </div>
            </div>
        `;
    });

    // Update Bill
    const taxes = subtotal * 0.05; // 5% Tax
    const platformFee = 5;
    const total = subtotal + taxes + platformFee;

    document.getElementById('billSubtotal').textContent = `₹${subtotal.toFixed(2)}`;
    document.getElementById('billTax').textContent = `₹${taxes.toFixed(2)}`;
    document.getElementById('billTotal').textContent = `₹${total.toFixed(2)}`;
}

function updateQty(index, change) {
    const cart = JSON.parse(localStorage.getItem('deliciae_cart') || '[]');
    if (cart[index].quantity + change <= 0) {
        if(confirm('Remove item from cart?')) {
            cart.splice(index, 1);
        } else {
            return;
        }
    } else {
        cart[index].quantity += change;
    }
    localStorage.setItem('deliciae_cart', JSON.stringify(cart));
    renderCart(); // Re-render immediately
}

function addSuggestionToCart(name, price) {
    const cart = JSON.parse(localStorage.getItem('deliciae_cart') || '[]');
    // Check if exists
    const existing = cart.find(i => i.name === name);
    if(existing) {
        existing.quantity++;
    } else {
        cart.push({
            id: Date.now(), // Mock ID
            name: name,
            price: price,
            quantity: 1,
            image: `https://source.unsplash.com/random/100x100/?${name.split(' ')[0]}`,
            restaurant: 'Deliciae Extras'
        });
    }
    localStorage.setItem('deliciae_cart', JSON.stringify(cart));
    renderCart();
    
    // Toast
    const toast = document.createElement('div');
    toast.className = 'fixed bottom-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-xl z-50 animate-slide-up flex items-center gap-2';
    toast.innerHTML = '<i class="fas fa-check-circle"></i> Item Added!';
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2000);
}

// --- CHECKOUT LOGIC ---

function initCheckoutPage() {
    renderCheckoutSummary();
    
    // Select default mode
    const defaultModeBtn = document.querySelector('.mode-tab');
    if(defaultModeBtn) selectMode('delivery', defaultModeBtn);
}

function renderCheckoutSummary() {
    const cart = JSON.parse(localStorage.getItem('deliciae_cart') || '[]');
    const container = document.getElementById('checkoutItems');
    let subtotal = 0;
    
    container.innerHTML = '';
    cart.forEach(item => {
        const itemTotal = item.price * item.quantity;
        subtotal += itemTotal;
        container.innerHTML += `
            <div class="flex justify-between items-center text-sm mb-2">
                <div class="flex items-center gap-2">
                    <span class="text-[#FF6B35] font-bold">${item.quantity}x</span>
                    <span class="text-gray-300">${item.name}</span>
                </div>
                <span class="font-medium">₹${itemTotal}</span>
            </div>
        `;
    });
    
    const total = subtotal * 1.05 + 5;
     document.getElementById('checkoutTotal').textContent = '₹' + total.toFixed(2);
}

function selectMode(mode, btn) {
    document.querySelectorAll('.mode-tab').forEach(t => t.classList.remove('active'));
    btn.classList.add('active');
    
    const section = document.getElementById('dynamicSection');
    
    // Animate transition
    section.style.opacity = '0';
    section.style.transform = 'translateY(5px)';
    
    setTimeout(() => {
        if(mode === 'delivery') {
            section.innerHTML = `
                <h3 class="font-bold text-lg mb-4">Delivery Address</h3>
                <div class="flex gap-4 mb-4 overflow-x-auto pb-2 custom-scrollbar">
                    <div class="min-w-[200px] p-4 border border-[#FF6B35] bg-[#FF6B35]/10 rounded-xl cursor-pointer relative transition-all ring-2 ring-[#FF6B35]/20">
                        <div class="absolute top-2 right-2 text-[#FF6B35]"><i class="fas fa-check-circle"></i></div>
                        <div class="font-bold mb-1"><i class="fas fa-home mr-2"></i> Home</div>
                        <p class="text-xs text-gray-400">Flat 4B, Skyline Apts, Kakkanad, Kochi</p>
                    </div>
                    <div class="min-w-[200px] p-4 border border-white/10 bg-white/5 rounded-xl cursor-pointer hover:border-white/30 transition-all">
                        <div class="font-bold mb-1"><i class="fas fa-briefcase mr-2"></i> Work</div>
                        <p class="text-xs text-gray-400">Infopark Phase 2, Kochi</p>
                    </div>
                    <div class="min-w-[150px] p-4 border border-dashed border-white/20 bg-transparent rounded-xl flex flex-col items-center justify-center cursor-pointer hover:bg-white/5 transition-all">
                        <i class="fas fa-plus mb-2 text-gray-400"></i>
                        <span class="text-sm text-gray-400">Add New</span>
                    </div>
                </div>
                
                <!-- Google Maps Placeholder -->
                <div class="map-placeholder">
                    <div class="text-center">
                        <i class="fas fa-map-marked-alt text-3xl mb-2 text-[#FF6B35]"></i>
                        <p class="text-sm text-gray-400">Live Tracking Enabled</p>
                    </div>
                </div>
            `;
        } else if (mode === 'pickup') {
            section.innerHTML = `
                 <h3 class="font-bold text-lg mb-4">Pickup Location</h3>
                 <div class="p-4 border border-white/20 bg-white/5 rounded-xl flex gap-4 items-center">
                    <div class="w-16 h-16 bg-gray-700 rounded-lg flex items-center justify-center">
                        <i class="fas fa-store text-2xl text-white"></i>
                    </div>
                    <div>
                        <div class="font-bold text-white">Deliciae Central Kitchen</div>
                        <p class="text-sm text-gray-400">Edapally, Kochi - 682024</p>
                        <div class="text-green-400 text-xs mt-1 bg-green-400/10 px-2 py-1 rounded inline-block">
                            <i class="fas fa-clock"></i> Ready in 20 mins
                        </div>
                    </div>
                 </div>
            `;
        } else if (mode === 'dining') {
            section.innerHTML = `
                <h3 class="font-bold text-lg mb-4">Table Booking</h3>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="text-xs text-gray-400 mb-1 block">Date</label>
                        <input type="date" class="w-full bg-[#151515] border border-white/10 rounded-lg p-3 text-white focus:border-[#FF6B35] outline-none transition-colors">
                    </div>
                    <div>
                        <label class="text-xs text-gray-400 mb-1 block">Time</label>
                        <input type="time" class="w-full bg-[#151515] border border-white/10 rounded-lg p-3 text-white focus:border-[#FF6B35] outline-none transition-colors">
                    </div>
                     <div class="col-span-2">
                         <label class="text-xs text-gray-400 mb-1 block">Guests</label>
                         <select class="w-full bg-[#151515] border border-white/10 rounded-lg p-3 text-white focus:border-[#FF6B35] outline-none transition-colors">
                            <option>2 People</option>
                            <option>4 People</option>
                            <option>6+ People</option>
                         </select>
                     </div>
                </div>
                <div class="mt-4 p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg flex items-start gap-3">
                    <i class="fas fa-info-circle text-blue-400 mt-1"></i>
                    <p class="text-xs text-blue-200">AI Prediction: This restaurant is usually busy at your selected time. We recommend booking 2 hours in advance.</p>
                </div>
            `;
        }
        
        section.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        section.style.opacity = '1';
        section.style.transform = 'translateY(0)';
    }, 200);
}

function placeOrder() {
    const btn = document.querySelector('button[onclick="placeOrder()"]');
    if(!btn) return;
    
    // Loading State
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Processing Payment...';
    btn.disabled = true;
    btn.classList.add('opacity-75', 'cursor-not-allowed');
    
    // Mock Delay
    setTimeout(() => {
        // Show Success Modal
        const modal = document.getElementById('successModal');
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        
        // Trigger Confetti (Mock function if library not present)
        if(window.confetti) {
            confetti({
                particleCount: 100,
                spread: 70,
                origin: { y: 0.6 }
            });
        }
        
        // Clear Cart
        localStorage.removeItem('deliciae_cart');
        
        // Update Button (Optional, since model covers it)
        btn.innerHTML = '<i class="fas fa-check"></i> Done';
        
    }, 2500);
}

// Ensure global access
window.updateQty = updateQty;
window.addSuggestionToCart = addSuggestionToCart;
window.selectMode = selectMode;
window.placeOrder = placeOrder;
