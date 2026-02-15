document.addEventListener('DOMContentLoaded', () => {
    
    // Smooth Scrolling for Anchors
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Navbar Scroll Effect
    const nav = document.querySelector('.glass-nav');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            nav.style.background = 'rgba(0, 0, 0, 0.8)'; // Darker bg on scroll
            nav.style.boxShadow = '0 5px 20px rgba(0,0,0,0.5)';
        } else {
            nav.style.background = 'var(--glass-bg)';
            nav.style.boxShadow = 'none';
        }
    });

    // Intersection Observer for Fade-In Animations
    const observerOptions = {
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Fade in elements
    const fadeElements = document.querySelectorAll('.feature-card, .step-item, .hero-content');
    fadeElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
        observer.observe(el);
    });
});

    // --- Dashboard Specific Logic ---
    
    // Category Selection
    const categoryChips = document.querySelectorAll('.category-chip');
    if (categoryChips.length > 0) {
        categoryChips.forEach(chip => {
            chip.addEventListener('click', () => {
                categoryChips.forEach(c => c.classList.remove('active'));
                chip.classList.add('active');
                
                // MOCK FILTER LOGIC
                const selectedCategory = chip.textContent.toLowerCase();
                console.log(`Filtering by category: ${selectedCategory}`);
                // In a real app, this would filter the food grid items
            });
        });
    }

    // Sidebar Navigation Highlighting
    const navItems = document.querySelectorAll('.nav-item');
    if (navItems.length > 0) {
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                navItems.forEach(n => n.classList.remove('active'));
                item.classList.add('active');
            });
        });
    }

    // --- API Integration ---
    const API_BASE = '/api/food/';
    // Elements are queried dynamically in functions to avoid DOM readyness issues

    // 0. Fetch Restaurants Logic
    async function fetchRestaurants() {
        console.log("fetchRestaurants called");
        const restaurantGrid = document.getElementById('restaurantGrid');
        if (!restaurantGrid) {
            // console.error("restaurantGrid not found"); // Supress if not on home
            return;
        }
        
        restaurantGrid.innerHTML = '<div style="color:var(--text-secondary); padding: 20px;"><i class="fas fa-spinner fa-spin"></i> Loading Restaurants...</div>';
        
        const searchInput = document.getElementById('searchInput');
        // const locationInput = document.getElementById('locationInput'); // Removed
        const query = searchInput ? searchInput.value : '';
        // const location = locationInput ? locationInput.value : ''; // Removed
        
        console.log(`Fetching restaurants: query="${query}", location="${location}"`);

        try {
            let url = `/api/restaurants/?`; 
            
            // STRICT GPS LOGIC
            // Use global userLat and userLng set by detectLocation
            if (window.userLat && window.userLng) {
                url = `/api/nearby-restaurants/?lat=${window.userLat}&lng=${window.userLng}&radius=20&`;
            } else {
                 // Fallback to all restaurants if no GPS
                 url = `/api/restaurants/?`;
            }

            if (query) url += `search=${encodeURIComponent(query)}&`;
            // Location param removed as per user request


            const response = await fetch(url);
            if (!response.ok) throw new Error("API Connection Failed");
            
            const data = await response.json();
            console.log("Restaurants loaded:", data);
            renderRestaurants(data.results || data);
            
        } catch (error) {
            console.error("Error loading restaurants:", error);
            if(restaurantGrid) {
                restaurantGrid.innerHTML = `<div style="color:red; padding:20px;">
                    <i class="fas fa-exclamation-triangle"></i> Failed to load restaurants.
                </div>`;
            }
        }
    }

    function renderRestaurants(restaurants) {
        const grid = document.getElementById('restaurantGrid');
        if (!grid) return;

        grid.innerHTML = '';

        if (restaurants.length === 0) {
            grid.innerHTML = `
                <div class="col-span-full text-center text-gray-400 py-10 bg-white/5 rounded-xl border border-white/10">
                    <i class="fas fa-map-marker-alt text-4xl mb-4 text-gray-600"></i>
                    <p class="text-lg">No open restaurants found near you.</p>
                    <p class="text-sm text-gray-500 mt-2">Try increasing the search radius or check back later.</p>
                </div>
            `;
            return;
        }

        const html = restaurants.map(restaurant => {
            // Default image fallback
            const imageUrl = restaurant.image_url || 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60';
            
            // Format time (remove seconds)
            const openTime = (restaurant.opening_time || '10:00').slice(0, 5);
            const closeTime = (restaurant.closing_time || '22:00').slice(0, 5);
            
            // Distance Badge Logic
            const distanceBadge = restaurant.distance_km 
                ? `<div class="absolute bottom-3 left-3 bg-black/70 backdrop-blur-md px-3 py-1 rounded-full text-xs font-bold text-white border border-white/10 flex items-center gap-1 shadow-sm">
                       <i class="fas fa-location-arrow text-[#FF6B35]"></i> ${restaurant.distance_km} km
                   </div>` 
                : '';

            return `
                <div class="bg-[#1a1a1a] border border-white/10 rounded-[18px] overflow-hidden hover:border-[#FF6B35]/50 transition-all group shadow-lg hover:shadow-[#FF6B35]/10">
                    <div class="relative h-48 overflow-hidden cursor-pointer" onclick="window.location.href='/restaurant/${restaurant.id}/'">
                        <img src="${imageUrl}" alt="${restaurant.name}" class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700">
                        <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-60"></div>
                        
                        <div class="absolute top-3 right-3 bg-black/70 backdrop-blur-md px-3 py-1 rounded-full text-xs font-bold text-white border border-white/10 shadow-sm">
                            <i class="fas fa-clock text-[#FF6B35] mr-1"></i> ${openTime} - ${closeTime}
                        </div>
                        ${distanceBadge}
                    </div>
                    
                    <div class="p-5">
                        <div class="flex justify-between items-start mb-2">
                            <h3 class="text-xl font-bold text-white group-hover:text-[#FF6B35] transition-colors cursor-pointer" onclick="window.location.href='/restaurant/${restaurant.id}/'">${restaurant.name}</h3>
                            <div class="flex items-center gap-1 bg-[#FF6B35]/10 px-2 py-0.5 rounded-lg border border-[#FF6B35]/20">
                                <span class="text-[#FF6B35] font-bold text-sm">${restaurant.rating || 'New'}</span>
                                <i class="fas fa-star text-[10px] text-[#FF6B35]"></i>
                            </div>
                        </div>
                        
                        <p class="text-gray-400 text-sm mb-4 line-clamp-1 flex items-center gap-1">
                            <i class="fas fa-map-pin text-gray-600"></i> ${restaurant.location || 'Location not available'}
                        </p>
                        
                        <div class="flex items-center justify-between pt-4 border-t border-white/10">
                            <div class="text-xs text-gray-400 font-medium bg-white/5 px-3 py-1 rounded-full border border-white/5 uppercase tracking-wide">
                                ${restaurant.cuisine_type || 'Multi-Cuisine'}
                            </div>
                            <a href="/restaurant/${restaurant.id}/" class="text-white text-sm font-semibold hover:text-[#FF6B35] transition-colors flex items-center gap-2 group/btn">
                                View Restaurant <i class="fas fa-arrow-right transform group-hover/btn:translate-x-1 transition-transform"></i>
                            </a>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        grid.innerHTML = html;
        grid.classList.add('animate-fade-in');
    }

    // 1. Fetch Food Logic
    async function fetchFood() {
        const foodGrid = document.getElementById('foodGrid');
        if (!foodGrid) return; // Safeguard for dashboard pages
        
        foodGrid.innerHTML = '<div style="color:var(--text-secondary); text-align:center; grid-column:1/-1;"><i class="fas fa-spinner fa-spin"></i> Loading Fresh Data...</div>';
        
        const searchInput = document.getElementById('searchInput');
        // const locationInput = document.getElementById('locationInput'); // Removed
        
        const query = searchInput ? searchInput.value : '';
        // const location = locationInput ? locationInput.value : ''; // Removed

        try {
            let url = `${API_BASE}?`;
            if (query) url += `search=${encodeURIComponent(query)}&`;
            // Location param removed as per user request


            console.log("Fetching:", url); // Debug
            const response = await fetch(url);
            
            if (!response.ok) throw new Error("API Connection Failed");
            
            const data = await response.json();
            renderFood(data.results || data); // Handle both paginated and flat lists
            
        } catch (error) {
            console.error(error);
            if(foodGrid) {
                foodGrid.innerHTML = `<div style="color:red; text-align:center; grid-column:1/-1;">
                    <i class="fas fa-exclamation-triangle"></i> Failed to connect to server.<br>
                    <small>Ensure 'python manage.py runserver' is running.</small>
                </div>`;
            }
        }
    }

    // 2. Render Cards
    window.allFoodItems = {}; // Global store for cart access

    function renderFood(items) {
        // Clear containers
        const foodGrid = document.getElementById('foodGrid');
        if(!foodGrid) return; 

        foodGrid.innerHTML = '';
        const trendingGrid = document.getElementById('trendingGrid');
        if(trendingGrid) trendingGrid.innerHTML = '';

        if (items.length === 0) {
            foodGrid.innerHTML = '<div style="text-align:center; grid-column:1/-1; color:gray;">No food found... try a different search or location! 🍔</div>';
            if(trendingGrid) trendingGrid.innerHTML = '<div style="color:gray; padding:20px;">No trending items in this area.</div>';
            return;
        }

        // Store items for lookup
        items.forEach(item => {
            window.allFoodItems[item.id] = item;
        });

        // Sort for Trending (High Trend Score first)
        const trendingItems = [...items].sort((a, b) => b.trend_score - a.trend_score).slice(0, 10);

        // Render Main Grid
        items.forEach(item => createCard(item, foodGrid));

        // Render Trending Section
        if(trendingGrid) {
            trendingItems.forEach(item => createCard(item, trendingGrid, true));
        }
    }

    function createCard(item, container, isTrendingSection = false) {
        const isAvailable = item.is_available;
        // Use currency from item (if flattened) or nested restaurant object
        const currency = item.currency_symbol || (item.restaurant ? item.restaurant.currency_symbol : '₹');
        
        // Determine availability status based on quantity
        const quantity = item.quantity_available || 100;
        let availabilityClass = 'available';
        let availabilityText = 'Available';
        
        if (!isAvailable || quantity === 0) {
            availabilityClass = 'sold-out';
            availabilityText = 'Sold Out';
        } else if (quantity < 20) {
            availabilityClass = 'limited';
            availabilityText = `Only ${quantity} left!`;
        }
        
        const card = document.createElement('div');
        card.className = `glass-card food-card ${!isAvailable ? 'sold-out-card' : ''}`;
        
         // AI Recommendation Logic (Mock + Real)
        const isAiRecommended = item.is_ai_recommended || (Math.random() > 0.8 && isAvailable && quantity > 0); 
        
        if (isAiRecommended) {
             card.classList.add('ai-border-gradient');
        }

        // Generate mock trend badge for high scores
        const trendBadge = item.trend_score > 6.0 ? '<div class="badge trending"><i class="fas fa-chart-line"></i> Trending</div>' : '';
        
        // AI Badge
        const aiBadge = isAiRecommended ? `
            <div class="absolute top-3 left-3 z-20 animate-pulse">
                <span class="bg-gradient-to-r from-blue-600 to-purple-600 text-white text-[10px] font-bold px-2 py-1 rounded-full flex items-center gap-1 shadow-lg border border-blue-400/30 backdrop-blur-md">
                    <i class="fas fa-robot"></i> AI Pick
                </span>
            </div>
        ` : '';

        const btnState = isAvailable && quantity > 0 ? '' : 'disabled';
        const btnText = isAvailable && quantity > 0 ? 'Order Now' : 'Unavailable';
        
        let userLat = null;
        let userLng = null;

// Cart State Matching - prioritize uploaded image
        const imgUrl = item.image || item.image_url || getFoodImage(item.name);
        
        // Media Content (Image or Video)
        let mediaContent;
        if (item.video_url) {
             mediaContent = `
                <div class="relative">
                    <video controls style="width:100%; height:200px; object-fit:cover; border-radius:12px 12px 0 0;" poster="${imgUrl}">
                        <source src="${item.video_url}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                    ${!isAvailable ? '<div class="badge sold-out" style="top:10px; right:10px;">Sold Out</div>' : trendBadge}
                    ${aiBadge}
                </div>
             `;
        } else {
            mediaContent = `
                <div class="card-img-container relative">
                    <img src="${imgUrl}" alt="${item.name}" onerror="this.onerror=null; this.src='https://placehold.co/600x400/222222/EDEDED?text=Deliciae+Food'">
                    ${!isAvailable ? '<div class="badge sold-out">Sold Out</div>' : trendBadge}
                    ${aiBadge}
                </div>
            `;
        }

        // Popularity score (0-100)
        const popularityScore = item.popularity_score || 0;
        const prepTime = item.preparation_time || 15;

        card.innerHTML = `
            ${mediaContent}
            <div class="card-details">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                    <h4 style="margin: 0;">${item.name}</h4>
                    <span class="availability-badge ${availabilityClass}">${availabilityText}</span>
                </div>
                <p class="restaurant-name" style="cursor: pointer;" onclick="openRestaurantProfile(${item.restaurant.id})">${item.restaurant.name} <span class="location-tag">| ${item.restaurant.location}</span></p>
                
                ${popularityScore > 0 ? `
                <div style="margin: 0.5rem 0;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.25rem;">
                        <span><i class="fas fa-fire"></i> Popularity</span>
                        <span>${Math.round(popularityScore)}%</span>
                    </div>
                    <div class="popularity-bar">
                        <div class="popularity-fill" style="width: ${popularityScore}%"></div>
                    </div>
                </div>
                ` : ''}
                
                <div class="card-meta">
                    <span class="price">${currency}${item.price}</span>
                    <span style="font-size: 0.8rem; color: var(--text-secondary);">
                        <i class="fas fa-clock"></i> ${prepTime} min
                    </span>
                </div>
                <button class="btn btn-primary btn-sm btn-full" ${btnState} onclick="placeQuickOrder(${item.id})">${btnText}</button>
            </div>
        `;
        container.appendChild(card);
    }

    // 3. Search & Location Listeners (Debounced)
    let searchTimeout;
    const triggerFetch = () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            fetchFood();
            fetchRestaurants(); // Fetch restaurants too
        }, 500);
    };

    // Search & Location Listeners will be attached in DOMContentLoaded

    // 4. Detect Location (Mock + API)
    // 4. Detect Location (Real Geocoding)
    // 4. Detect Location (Real Geocoding + Manual Input)
    window.handleManualLocationInput = function(event) {
        if (event.key === 'Enter') {
            const city = event.target.value.trim();
            if (city) {
                geocodeCity(city);
            }
        }
    };

    window.geocodeCity = async function(city) {
        const input = document.getElementById('manualLocationInput');
        if(input) input.disabled = true;
        
        try {
            // Using OpenStreetMap Nominatim for geocoding
            const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(city)}`);
            const data = await response.json();

            if (data && data.length > 0) {
                window.userLat = parseFloat(data[0].lat);
                window.userLng = parseFloat(data[0].lon);
                console.log(`Manual Location set to: ${city} (${window.userLat}, ${window.userLng})`);
                
                // Refresh Data
                fetchFood();
                fetchRestaurants();
                if (window.refreshHomeSections) window.refreshHomeSections();
                
                // Visual Feedback
                if(input) {
                    input.value = data[0].display_name.split(',')[0]; // Show detected city name
                    input.style.borderColor = '#4ade80'; // Green border
                    setTimeout(() => input.style.borderColor = '', 2000);
                }
            } else {
                alert("City not found! Please check spelling.");
                if(input) input.style.borderColor = '#ef4444'; // Red border
            }
        } catch (error) {
            console.error("Geocoding failed:", error);
            alert("Failed to find location. Please try again.");
        } finally {
             if(input) input.disabled = false;
             if(input) input.focus();
        }
    };

    window.detectLocation = function() {
        const input = document.getElementById('manualLocationInput');
        if(input) input.placeholder = "Locating...";
        
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                 async (position) => {
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    
                    window.userLat = lat;
                    window.userLng = lng;
                    
                    // Reverse Geocode for display name
                    try {
                        const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`);
                        const data = await response.json();
                        const cityName = data.address.city || data.address.town || data.address.village || "Current Location";
                        
                        if(input) input.value = cityName;
                    } catch (e) {
                         console.warn("Reverse geocoding failed:", e);
                         if(input) input.value = "Current Location";
                         // Ensure no alert is shown here
                    }

                    fetchFood(); 
                    fetchRestaurants(); 
                    if (window.refreshHomeSections) window.refreshHomeSections();
                },
                (error) => {
                    console.error(error);
                    alert("⚠️ Location access denied. Please enter manually.");
                    if(input) input.placeholder = "Enter City Name manually";
                }
            );
        } else {
            alert("Geolocation is not supported by this browser.");
        }
    }

    // Initialize on DOM Ready
    document.addEventListener('DOMContentLoaded', () => {
        const searchInput = document.getElementById('searchInput');
        // const locationInput = document.getElementById('locationInput'); // Removed
        
        if (searchInput) searchInput.addEventListener('input', triggerFetch);
        // if (locationInput) locationInput.addEventListener('input', triggerFetch); // Removed

        console.log("Script initializing...");
        DetectLocationOnLoad();
        
        function DetectLocationOnLoad() {
             // We can just call detectLocation() but maybe we want to avoid double fetch if it's fast?
             // Actually script.js detectLocation calls fetchRestaurants on success.
             // So let's NOT blindly call fetchRestaurants() here if we expect detectLocation to work?
             // But if detectLocation is denied, we need to show something.
             // detectLocation handles error/denial by calling fetch... 
             // So let's try calling ONLY detectLocation() and see.
             // But to be safe, we can call fetchRestaurants() immediately (shows 'loading' or 'all') and then detectLocation refreshes it.
             detectLocation();
        }
        
        // fetchFood(); // detectLocation calls this
        // fetchRestaurants(); // detectLocation calls this
        updateCartBadge(); // Init Badge
    });

    // Clean up restaurant dashboard mock just in case (Keep if needed)
    window.addItemMock = function() {
        document.getElementById('addFoodModal').style.display = 'none';
        alert('Items added successfully to the database!'); 
    }

    // --- Restaurant Dashboard Logic ---

    // Modal Functions
    window.openAddFoodModal = function() {
        const modal = document.getElementById('addFoodModal');
        if (modal) modal.style.display = 'block';
    }

    window.closeAddFoodModal = function() {
        const modal = document.getElementById('addFoodModal');
        if (modal) modal.style.display = 'none';
    }

    // Close modal if clicked outside
    window.onclick = function(event) {
        const modal = document.getElementById('addFoodModal');
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }

    // Availability Toggle Logic
    window.toggleAvailability = function(checkbox) {
        const row = checkbox.closest('tr');
        const itemName = row.querySelector('.item-cell span').textContent;
        const statusBadge = row.querySelector('td:nth-child(4)'); // Rough selection for demo
        
        if (checkbox.checked) {
            // console.log(`${itemName} marked as AVAILABLE`);
            alert(`${itemName} is now AVAILABLE for customers.`);
            // Mock visual update for status if needed
        } else {
            // console.log(`${itemName} marked as SOLD OUT`);
            alert(`${itemName} is now SOLD OUT.`);
    }
}

// 5. Smart Image Matcher
function getFoodImage(foodName) {
    if (!foodName) return 'https://placehold.co/600x400/222222/EDEDED?text=Deliciae+Food';
    const name = foodName.toLowerCase();
    
    // Keyword Matching
    if (name.includes('burger')) return 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=500&q=60';
    if (name.includes('pizza')) return 'https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=500&q=60';
    if (name.includes('salad') || name.includes('bowl')) return 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=500&q=60';
    if (name.includes('pasta') || name.includes('spaghetti')) return 'https://images.unsplash.com/photo-1473093295043-cdd812d0e601?auto=format&fit=crop&w=500&q=60';
    if (name.includes('sushi') || name.includes('roll')) return 'https://images.unsplash.com/photo-1579871494447-9811cf80d66c?auto=format&fit=crop&w=500&q=60';
    if (name.includes('chicken') || name.includes('tikka')) return 'https://images.unsplash.com/photo-1562967963-4d567089c670?auto=format&fit=crop&w=500&q=60';
    if (name.includes('curry')) return 'https://images.unsplash.com/photo-1565557623262-b51c2513a641?auto=format&fit=crop&w=500&q=60';
    if (name.includes('fish') || name.includes('karimeen')) return 'https://images.unsplash.com/photo-1587320038865-c89b398693c1?auto=format&fit=crop&w=500&q=60';
    if (name.includes('cake') || name.includes('dessert')) return 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=500&q=60';
    if (name.includes('ice cream')) return 'https://images.unsplash.com/photo-1497034825429-c343d7c6a68f?auto=format&fit=crop&w=500&q=60';
    if (name.includes('fries')) return 'https://images.unsplash.com/photo-1573080496987-a226b38c0340?auto=format&fit=crop&w=500&q=60';
    if (name.includes('biryani')) return 'https://images.unsplash.com/photo-1589302168068-964664d93dc0?auto=format&fit=crop&w=500&q=60';
    if (name.includes('sandwich')) return 'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?auto=format&fit=crop&w=500&q=60';
    if (name.includes('coffee') || name.includes('latte')) return 'https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=500&q=60';
    
    // Default fallback
    return 'https://placehold.co/600x400/222222/EDEDED?text=Deliciae+Eats';
}

// --- SOCIAL NETWORK LOGIC ---

// 1. Navigation
window.showDashboardSection = function(sectionId) {
    document.getElementById('home-view').style.display = 'none';
    document.getElementById('reels-view').style.display = 'none';
    const ordersView = document.getElementById('orders-view');
    if(ordersView) ordersView.style.display = 'none';
    const settingsView = document.getElementById('settings-view');
    if(settingsView) settingsView.style.display = 'none';
    
    document.getElementById(sectionId).style.display = 'block';
    
    // Update Sidebar Active State
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    if(sectionId === 'home-view') document.querySelector('.nav-item:nth-child(1)').classList.add('active');
    if(sectionId === 'reels-view') document.querySelector('.nav-item:nth-child(2)').classList.add('active');
    if(sectionId === 'orders-view') document.querySelector('.nav-item:nth-child(3)').classList.add('active');
    if(sectionId === 'settings-view') document.querySelector('.nav-item:nth-child(4)').classList.add('active');
}

// 2. Reels Logic
async function fetchReels() {
    const container = document.getElementById('reels-container');
    container.innerHTML = '<div style="text-align: center; padding-top: 50px; color: grey;"><i class="fas fa-spinner fa-spin fa-2x"></i></div>';
    
    try {
        const response = await fetch('/api/reels/');
        const data = await response.json();
        
        const reels = data.results || data;
        
        container.innerHTML = '';
        if (reels.length === 0) {
            container.innerHTML = '<div style="text-align:center; padding-top:100px; color:gray;"><h3>No Reels Yet 🎥</h3><p>Follow restaurants to see their latest updates!</p></div>';
            return;
        }
        
        reels.forEach(reel => {
            const reelCard = document.createElement('div');
            reelCard.className = 'glass-card';
            reelCard.style.cssText = 'margin-bottom: 2rem; position: relative; border-radius: 20px; overflow: hidden; background: #000;';
            
            const isFollowing = reel.is_following_restaurant;
            const followText = isFollowing ? 'Following' : 'Follow';
            const followStyle = isFollowing ? 'background: var(--accent-primary); border: none;' : 'background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.5);';

            reelCard.innerHTML = `
                <div class="reel-header" style="position: absolute; top: 15px; left: 15px; z-index: 10; display: flex; align-items: center; gap: 10px;">
                    <img src="${reel.restaurant_avatar || 'https://ui-avatars.com/api/?name=' + reel.restaurant_name}" style="width: 40px; height: 40px; border-radius: 50%; border: 2px solid var(--accent-primary); cursor: pointer;" onclick="openRestaurantProfile(${reel.restaurant})">
                    <div style="display: flex; flex-direction: column;">
                        <span style="font-weight: 600; text-shadow: 0 2px 4px rgba(0,0,0,0.8); cursor: pointer;" onclick="openRestaurantProfile(${reel.restaurant})">${reel.restaurant_name}</span>
                        <button onclick="toggleFollow(${reel.restaurant}, this)" class="follow-btn" style="${followStyle} color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.7rem; cursor: pointer; margin-top: 2px; backdrop-filter: blur(4px);">
                            ${followText}
                        </button>
                    </div>
                </div>
                
                <video src="${reel.video_url}" style="width: 100%; height: 600px; object-fit: cover;" controls loop muted></video>
                
                <div class="reel-actions" style="position: absolute; bottom: 80px; right: 15px; display: flex; flex-direction: column; gap: 1.5rem; align-items: center; z-index: 10;">
                    <div style="text-align: center;">
                        <button onclick="likeReel(${reel.id}, this)" style="background: rgba(0,0,0,0.5); border: none; color: white; width: 50px; height: 50px; border-radius: 50%; cursor: pointer; backdrop-filter: blur(5px); font-size: 1.5rem; transition: 0.2s;">
                            <i class="${likeIcon}" style="${isLiked}"></i>
                        </button>
                        <div class="like-count" style="font-size: 0.8rem; margin-top: 5px; text-shadow: 0 2px 4px black;">${reel.likes_count}</div>
                    </div>
                    
                    <div style="text-align: center;">
                        <button style="background: rgba(0,0,0,0.5); border: none; color: white; width: 50px; height: 50px; border-radius: 50%; cursor: pointer; backdrop-filter: blur(5px); font-size: 1.5rem;">
                            <i class="far fa-comment"></i>
                        </button>
                        <div style="font-size: 0.8rem; margin-top: 5px; text-shadow: 0 2px 4px black;">${reel.comments_count}</div>
                    </div>

                    <button onclick="shareReel(${reel.id})" style="background: rgba(0,0,0,0.5); border: none; color: white; width: 50px; height: 50px; border-radius: 50%; cursor: pointer; backdrop-filter: blur(5px); font-size: 1.5rem;">
                        <i class="fas fa-share"></i>
                    </button>
                </div>
                
                <div class="reel-caption" style="position: absolute; bottom: 0; left: 0; width: 100%; padding: 20px; background: linear-gradient(to top, rgba(0,0,0,0.9), transparent); pointer-events: none;">
                    <div style="pointer-events: auto;">
                        <p style="margin-bottom: 0.5rem; font-size: 0.95rem; text-shadow: 0 1px 2px black;">${reel.caption || ''}</p>
                        <small style="opacity: 0.7; display: block; margin-bottom: 5px;">${new Date(reel.created_at).toLocaleDateString()}</small>
                        
                        ${reel.food_item_id ? `
                        <button onclick="placeQuickOrder(${reel.food_item_id}, '${reel.food_item_name}')" style="margin-top: 5px; background: var(--accent-primary); color: white; border: none; padding: 10px 20px; border-radius: 30px; font-weight: 600; cursor: pointer; box-shadow: 0 4px 15px rgba(0,0,0,0.5); display: flex; align-items: center; gap: 8px; width: 100%; justify-content: center; backdrop-filter: blur(5px);">
                            <i class="fas fa-utensils"></i> Order ${reel.food_item_name}
                        </button>
                        ` : ''}
                    </div>
                </div>
            `;
            container.appendChild(reelCard);

            // Auto-play Observer
             const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    const video = entry.target.querySelector('video');
                    if(video) {
                        if (entry.isIntersecting) {
                            video.play().catch(e => console.log('Autoplay prevented', e));
                        } else {
                            video.pause();
                        }
                    }
                });
            }, { threshold: 0.6 });
            observer.observe(reelCard);
        });
        
    } catch (err) {
        console.error(err);
        container.innerHTML = '<div style="color:red; text-align:center; padding-top:50px;">Failed to load reels.</div>';
    }
}

// Global functions for Reels interactions

window.toggleFollow = async function(restaurantId, btn) {
    const isFollowing = btn.textContent.trim() === 'Following';
    const originalText = btn.textContent;
    const originalStyle = btn.style.background;
    
    // Optimistic Update
    btn.textContent = isFollowing ? 'Follow' : 'Following';
    btn.style.background = isFollowing ? 'rgba(255,255,255,0.2)' : 'var(--accent-primary)';
    if(isFollowing) btn.style.border = '1px solid rgba(255,255,255,0.5)';
    else btn.style.border = 'none';

    try {
        const response = await fetch('/api/follow/toggle/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ restaurant_id: restaurantId })
        });
        
        if (!response.ok) throw new Error('Failed');
        
        const data = await response.json();
        
        // Sync all buttons
        document.querySelectorAll(`.follow-btn[onclick*="${restaurantId}"]`).forEach(b => {
             if (data.status === 'followed') {
                b.textContent = 'Following';
                b.style.background = 'var(--accent-primary)';
                b.style.border = 'none';
            } else {
                b.textContent = 'Follow';
                b.style.background = 'rgba(255,255,255,0.2)';
                b.style.border = '1px solid rgba(255,255,255,0.5)';
            }
        });
        
    } catch (err) {
        console.error(err);
        btn.textContent = originalText;
        btn.style.background = originalStyle;
        alert('Action failed');
    }
};

window.likeReel = async function(reelId, btn) {
    const icon = btn.querySelector('i');
    const isLiked = icon.classList.contains('fas'); // fas = solid = liked
    const countDiv = btn.nextElementSibling; // div.like-count
    
    // Optimistic
    icon.className = isLiked ? 'far fa-heart' : 'fas fa-heart';
    icon.style.color = isLiked ? 'white' : '#e74c3c';
    let count = parseInt(countDiv.textContent);
    countDiv.textContent = isLiked ? count - 1 : count + 1;
    
    try {
        const res = await fetch(`/api/reels/${reelId}/like/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (!res.ok) throw new Error('Failed to like');
        
        const data = await res.json();
        // Sync with server count just in case
        countDiv.textContent = data.likes_count;
        
    } catch (err) {
        console.error(err);
        // Revert on error
        icon.className = isLiked ? 'fas fa-heart' : 'far fa-heart';
        icon.style.color = isLiked ? '#e74c3c' : 'white';
        countDiv.textContent = count;
    }
};

window.shareReel = function(reelId) {
    if (navigator.share) {
        navigator.share({
            title: 'Deliciae Reel',
            text: 'Check out this delicious food!',
            url: window.location.origin + '/reels/' + reelId
        });
    } else {
        alert('Link copied to clipboard!');
    }
};


// 3. Restaurant Profile Logic
// 3. Restaurant Profile Logic (Redirect to new page)
window.openRestaurantProfile = function(id) {
    window.location.href = `/restaurant/${id}/`;
};

// --- TAB SWITCHING (Refined) ---

// --- TAB SWITCHING (Refined) ---
window.switchProfileTab = function(tab, btn) {
    const content = document.getElementById('profileTabContent');
    const tabs = document.querySelectorAll('#profileTabsHeader button');
    
    // Update Tab Styles
    tabs.forEach(t => {
        t.className = 'flex-1 pb-4 text-gray-500 font-medium hover:text-white transition-colors focus:outline-none border-b-2 border-transparent';
    });
    btn.className = 'flex-1 pb-4 text-[#FF6B35] font-medium border-b-2 border-[#FF6B35] transition-colors focus:outline-none';
    
    // Animate Content Out/In
    content.style.opacity = '0';
    content.style.transform = 'translateY(10px)';
    
    setTimeout(() => {
        if(tab === 'posts') {
            renderProfilePosts(window.currentProfileData.posts, content);
        } else if (tab === 'menu') {
            renderProfileMenu(window.currentProfileData.menu, content);
        } else if (tab === 'reviews') {
             content.innerHTML = `
                <div class="flex flex-col items-center justify-center py-12 text-gray-500">
                     <div class="w-16 h-16 bg-gray-800/50 rounded-full flex items-center justify-center text-2xl mb-4 text-gray-400">
                        <i class="far fa-comment-alt"></i>
                    </div>
                    <p class="text-lg font-medium">No reviews yet</p>
                    <p class="text-sm opacity-60">Be the first to review this place!</p>
                </div>
            `;
        }
        
        // Animate In
        content.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        content.style.opacity = '1';
        content.style.transform = 'translateY(0)';
    }, 200);
}

// --- RENDER FUNCTIONS (Premium Grid) ---
function renderProfilePosts(posts, container) {
    if(!posts || posts.length === 0) {
        container.innerHTML = `
            <div class="flex flex-col items-center justify-center py-16 text-gray-500">
                <div class="w-20 h-20 bg-gray-800/50 rounded-full flex items-center justify-center text-4xl mb-4 text-gray-600">
                    <i class="fas fa-camera"></i>
                </div>
                <p class="text-lg font-medium text-white">No posts yet</p>
                <p class="text-sm text-gray-600">This restaurant hasn’t shared any reels yet.</p>
            </div>
        `;
        return;
    }
    
    let html = '<div class="grid grid-cols-3 gap-1">'; // Instagram style tight grid
    posts.forEach(p => {
        html += `
            <div class="aspect-[9/16] bg-gray-900 relative cursor-pointer group overflow-hidden" onclick="openVideoModal('${p.video_url}')">
                <video src="${p.video_url}" class="w-full h-full object-cover group-hover:scale-110 transition duration-700"></video>
                <div class="absolute inset-0 bg-black/20 group-hover:bg-black/40 transition-colors"></div>
                
                <div class="absolute bottom-2 left-2 text-white text-xs font-bold flex items-center gap-1 opacity-100 md:opacity-0 md:group-hover:opacity-100 transition-opacity">
                    <i class="fas fa-heart"></i> ${p.likes_count || 0}
                </div>
                 <div class="absolute top-2 right-2 text-white text-lg opacity-0 group-hover:opacity-100 transition-transform transform translate-y-2 group-hover:translate-y-0">
                    <i class="fas fa-play-circle"></i>
                </div>
            </div>
        `;
    });
    html += '</div>';
    container.innerHTML = html;
}

function renderProfileMenu(menu, container) {
    if(!menu || menu.length === 0) {
        container.innerHTML = `
             <div class="flex flex-col items-center justify-center py-16 text-gray-500">
                <div class="w-20 h-20 bg-gray-800/50 rounded-full flex items-center justify-center text-4xl mb-4 text-gray-600">
                    <i class="fas fa-utensils"></i>
                </div>
                <p class="text-lg font-medium text-white">Menu Unavailable</p>
            </div>
        `;
        return;
    }
    
    let html = '<div class="grid grid-cols-1 md:grid-cols-2 gap-4">';
    menu.forEach(item => {
        html += `
            <div class="bg-[#1e1e1e] p-4 rounded-xl flex gap-4 hover:bg-[#252525] transition-colors border border-white/5 group">
                <div class="w-20 h-20 rounded-lg overflow-hidden shrink-0">
                     <img src="${item.image_url || 'https://placehold.co/80'}" class="w-full h-full object-cover group-hover:scale-110 transition duration-500">
                </div>
                <div class="flex-1 min-w-0">
                    <div class="flex justify-between items-start mb-1">
                        <h4 class="font-medium text-white truncate pr-2">${item.name}</h4>
                        <span class="text-[#FF6B35] font-bold text-sm">₹${item.price}</span>
                    </div>
                    <p class="text-gray-500 text-xs line-clamp-2 mb-2 h-8">${item.description || 'No description available.'}</p>
                    
                    <div class="flex justify-between items-center">
                         <span class="text-[10px] px-2 py-0.5 rounded-full ${item.is_available ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'}">
                            ${item.is_available ? 'Available' : 'Sold Out'}
                        </span>
                        <button class="w-8 h-8 rounded-full bg-white text-black flex items-center justify-center hover:bg-[#FF6B35] hover:text-white transition-colors shadow-lg transform active:scale-95" onclick="addToCart(${item.id})">
                            <i class="fas fa-plus text-xs"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    html += '</div>';
    container.innerHTML = html;
}

// Add openVideoModal helper if not exists
window.openVideoModal = function(url) {
    const modal = document.createElement('div');
    modal.style.cssText = 'position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.9); z-index:10000; display:flex; align-items:center; justify-content:center;';
    modal.innerHTML = `
        <div style="position:relative; width:90%; max-width:500px; aspect-ratio:9/16;">
            <button onclick="this.closest('div').parentElement.remove()" style="position:absolute; top:-40px; right:-10px; background:none; border:none; color:white; font-size:2rem; cursor:pointer;">&times;</button>
            <video src="${url}" controls autoplay style="width:100%; height:100%; border-radius:10px;"></video>
        </div>
    `;
    document.body.appendChild(modal);
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// --- CART FUNCTIONS ---

window.addToCart = function(id, name, price, restaurantId, restaurantName, imageUrl) {
    // 1. Try to get full object from global store
    let item = window.allFoodItems[id];
    
    // 2. If not found, check if details were passed directly (Server-Rendered Pages)
    if (!item && name && price) {
        item = {
            id: id,
            name: name,
            price: parseFloat(price),
            restaurant: {
                id: restaurantId,
                name: restaurantName || 'Unknown Restaurant'
            },
            image: imageUrl || null
        };
    }

    if (!item) {
        console.error("Item not found:", id);
        // Fallback for profile page items if not in main list (TODO: improved lookup)
        // Check if currentProfileData exists
        if(window.currentProfileData && window.currentProfileData.menu) {
             const profileItem = window.currentProfileData.menu.find(i => i.id === id);
             if(profileItem) {
                 addItemToLocalStorage(profileItem);
                 return;
             }
        }
        return;
    }
    addItemToLocalStorage(item);
};

function addItemToLocalStorage(item) {
    const cart = JSON.parse(localStorage.getItem('deliciae_cart') || '[]');
    const existingIndex = cart.findIndex(i => i.id === item.id);

    if (existingIndex > -1) {
        cart[existingIndex].quantity += 1;
    } else {
        cart.push({
            id: item.id,
            name: item.name,
            price: parseFloat(item.price),
            quantity: 1,
            image: item.image || item.image_url || getFoodImage(item.name),
            restaurant: item.restaurant ? item.restaurant.name : (window.currentProfileData ? window.currentProfileData.restaurant.name : 'Deliciae Kitchen')
        });
    }

    localStorage.setItem('deliciae_cart', JSON.stringify(cart));
    
    // Dispatch event for other listeners
    window.dispatchEvent(new Event('storage'));

    // Visual Feedback (Toast)
    const toast = document.createElement('div');
    toast.className = 'fixed bottom-4 right-4 bg-[#FF6B35] text-white px-6 py-3 rounded-lg shadow-xl z-50 animate-bounce flex items-center gap-2 font-bold';
    toast.innerHTML = `<i class="fas fa-cart-plus"></i> Added ${item.name}!`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2000);
    
    // Update Badge
    updateCartBadge();
}

window.placeQuickOrder = function(id) {
    window.addToCart(id);
    setTimeout(() => {
        window.location.href = '/cart/';
    }, 500);
};

function updateCartBadge() {
    const cart = JSON.parse(localStorage.getItem('deliciae_cart') || '[]');
    const count = cart.reduce((acc, item) => acc + item.quantity, 0);
    const badge = document.getElementById('cart-badge');
    if(badge) {
        badge.textContent = count;
        if(count > 0) badge.classList.remove('hidden');
        else badge.classList.add('hidden');
    }
}
