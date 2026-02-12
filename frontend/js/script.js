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
            console.error("restaurantGrid not found");
            return;
        }
        
        restaurantGrid.innerHTML = '<div style="color:var(--text-secondary); padding: 20px;"><i class="fas fa-spinner fa-spin"></i> Loading Restaurants...</div>';
        
        const searchInput = document.getElementById('searchInput');
        const locationInput = document.getElementById('locationInput');
        const query = searchInput ? searchInput.value : '';
        const location = locationInput ? locationInput.value : '';
        
        console.log(`Fetching restaurants: query="${query}", location="${location}"`);

        try {
            let url = `/api/restaurants/?`; // Note: adjust if your URL path is different
            if (query) url += `search=${encodeURIComponent(query)}&`;
            if (location) url += `location=${encodeURIComponent(location)}&`;

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

    function renderRestaurants(items) {
        const restaurantGrid = document.getElementById('restaurantGrid');
        if(!restaurantGrid) return;
        restaurantGrid.innerHTML = '';
        if (items.length === 0) {
            restaurantGrid.innerHTML = '<div style="color:gray; padding:20px;">No restaurants found in this area.</div>';
            return;
        }

        items.forEach(rest => {
            const card = document.createElement('div');
            card.className = 'glass-card food-card'; // Reusing food card style for simplicity
            
            // Image Fallback
            const imgUrl = rest.image_url || 'https://placehold.co/600x400/111/FFF?text=' + encodeURIComponent(rest.name);
            const cuisine = rest.cuisine_type || 'Restaurant';
            const loc = rest.location || 'Unknown';
            const rating = rest.rating || 'N/A';

            card.innerHTML = `
                <div class="card-img-container" style="cursor: pointer;" onclick="openRestaurantProfile(${rest.id})">
                    <img src="${imgUrl}" alt="${rest.name}" style="height: 150px; object-fit: cover;">
                    <div class="badge" style="top:10px; right:10px; background: rgba(0,0,0,0.7);"><i class="fas fa-star" style="color:gold;"></i> ${rating}</div>
                </div>
                <div class="card-details">
                    <h4 style="cursor: pointer;" onclick="openRestaurantProfile(${rest.id})">${rest.name}</h4>
                    <p class="restaurant-name" style="color: var(--accent-primary);">${cuisine}</p>
                    <div class="card-meta">
                         <span><i class="fas fa-map-marker-alt"></i> ${loc}</span>
                    </div>
                </div>
            `;
            restaurantGrid.appendChild(card);
        });
    }

    // 1. Fetch Food Logic
    async function fetchFood() {
        const foodGrid = document.getElementById('foodGrid');
        if (!foodGrid) return; // Safeguard for dashboard pages
        
        foodGrid.innerHTML = '<div style="color:var(--text-secondary); text-align:center; grid-column:1/-1;"><i class="fas fa-spinner fa-spin"></i> Loading Fresh Data...</div>';
        
        const searchInput = document.getElementById('searchInput');
        const locationInput = document.getElementById('locationInput');
        
        const query = searchInput ? searchInput.value : '';
        const location = locationInput ? locationInput.value : '';

        try {
            let url = `${API_BASE}?`;
            if (query) url += `search=${encodeURIComponent(query)}&`;
            if (location) url += `location=${encodeURIComponent(location)}&`;

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
    function renderFood(items) {
        // Clear containers
        foodGrid.innerHTML = '';
        const trendingGrid = document.getElementById('trendingGrid');
        if(trendingGrid) trendingGrid.innerHTML = '';

        if (items.length === 0) {
            foodGrid.innerHTML = '<div style="text-align:center; grid-column:1/-1; color:gray;">No food found... try a different search or location! 🍔</div>';
            if(trendingGrid) trendingGrid.innerHTML = '<div style="color:gray; padding:20px;">No trending items in this area.</div>';
            return;
        }

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
        
        // Generate mock trend badge for high scores
        const trendBadge = item.trend_score > 6.0 ? '<div class="badge trending"><i class="fas fa-chart-line"></i> Trending</div>' : '';
        const btnState = isAvailable && quantity > 0 ? '' : 'disabled';
        const btnText = isAvailable && quantity > 0 ? 'Order Now' : 'Unavailable';
        
        // Smart Image Matching
        const imgUrl = item.image_url || getFoodImage(item.name);
        
        // Media Content (Image or Video)
        let mediaContent;
        if (item.video_url) {
             mediaContent = `
                <video controls style="width:100%; height:200px; object-fit:cover; border-radius:12px 12px 0 0;" poster="${imgUrl}">
                    <source src="${item.video_url}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
                ${!isAvailable ? '<div class="badge sold-out" style="top:10px; right:10px;">Sold Out</div>' : trendBadge}
             `;
        } else {
            mediaContent = `
                <div class="card-img-container">
                    <img src="${imgUrl}" alt="${item.name}" onerror="this.onerror=null; this.src='https://placehold.co/600x400/222222/EDEDED?text=Deliciae+Food'">
                    ${!isAvailable ? '<div class="badge sold-out">Sold Out</div>' : trendBadge}
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
    window.detectLocation = function() {
        const btn = document.querySelector('button[onclick="detectLocation()"]');
        const originalHtml = btn ? btn.innerHTML : '<i class="fas fa-location-arrow"></i>';
        if(btn) btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                async (position) => {
                    const { latitude, longitude } = position.coords;
                    try {
                        const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`);
                        const data = await response.json();
                        // Prioritize city > town > village > county
                        const detectedLoc = data.address.city || data.address.town || data.address.village || data.address.county || "Kochi";
                        
                        if(locationInput) locationInput.value = detectedLoc;
                        fetchFood(); 
                        fetchRestaurants(); 
                        // alert(`📍 Location Detected: ${detectedLoc}`);
                    } catch (err) {
                        console.error(err);
                        alert("⚠️ Failed to fetch address. Falling back to default.");
                        if(locationInput) locationInput.value = "Kochi";
                    } finally {
                        if(btn) btn.innerHTML = originalHtml;
                    }
                },
                (error) => {
                    console.error(error);
                    alert("⚠️ Location access denied. Falling back to 'Kochi'.");
                    if(locationInput) locationInput.value = "Kochi";
                    fetchFood();
                    fetchRestaurants();
                    if(btn) btn.innerHTML = originalHtml;
                }
            );
        } else {
            alert("Geolocation is not supported by this browser.");
            if(btn) btn.innerHTML = originalHtml;
        }
    }

    // Initialize on DOM Ready
    document.addEventListener('DOMContentLoaded', () => {
        const searchInput = document.getElementById('searchInput');
        const locationInput = document.getElementById('locationInput');
        
        if (searchInput) searchInput.addEventListener('input', triggerFetch);
        if (locationInput) locationInput.addEventListener('input', triggerFetch);

        console.log("Script initializing...");
        fetchFood();
        fetchRestaurants();
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
    
    document.getElementById(sectionId).style.display = 'block';
    
    // Update Sidebar Active State
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    if(sectionId === 'home-view') document.querySelector('.nav-item:nth-child(1)').classList.add('active');
    if(sectionId === 'reels-view') document.querySelector('.nav-item:nth-child(2)').classList.add('active');
    if(sectionId === 'orders-view') document.querySelector('.nav-item:nth-child(5)').classList.add('active');
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
window.openRestaurantProfile = async function(id) {
    const modal = document.getElementById('restaurantProfileModal');
    const header = document.getElementById('profile-header');
    const body = document.getElementById('profile-body');
    
    modal.style.display = 'block';
    header.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading Profile...';
    body.innerHTML = '';

    try {
        // Fetch Restaurant Details (reuse list endpoint with filter or new detail endpoint?)
        // Assuming we can get detail from ID: /api/restaurants/?id=X or just filter
        // Better: create detail endpoint or just find from cached list locally? 
        // Let's assume list for now or fetch specific.
        // Actually RestaurantViewSet supports retrieving by ID: /api/restaurants/ID/ if it's ModelViewSet or similar.
        // My RestaurantListView is ListAPIView. 
        // I might need to update backend to support Detail View? 
        // Or just use the existing list API and filter in JS if data is there?
        // But for fresh stats (followers), better to fetch.
        // Wait, RestaurantListView is ListAPIView. It doesn't support /id/ retrieval by default unless configured.
        // I'll assume I can fetch list with ?search=NAME or similar, or better: 
        // I should have added a RetrieveAPIView or ViewSet.
        // For now, let's use the list endpoint with a filter if possible, or just hack it:
        // Actually I can just fetch all and find? No inefficient.
        // I will add a quick detail view logic or just assume I can pass data?
        // Let's add `Retrieve` to `RestaurantListView`? No.
        // I will use client side data from the click if possible, but stats need fetch.
        // Lets try fetching from `/api/restaurants/?search=` and hope name is unique? Risky.
        // *Self-Correction*: I should have added a Detail View. 
        // **Workaround**: I will use a simple fetch to `/api/restaurants/` (list) and find the ID in JS. Not ideal but works for small app.
        
        const res = await fetch('/api/restaurants/'); // This is inefficient for real app
        const all = await res.json();
        const restaurant = (all.results || all).find(r => r.id == id);
        
        if (!restaurant) throw new Error("Restaurant not found");
        
        // Render Header
        const isFollowing = restaurant.is_following;
        const btnText = isFollowing ? 'Following' : 'Follow';
        const btnClass = isFollowing ? 'btn-secondary' : 'btn-primary';
        
        header.innerHTML = `
            <img src="${restaurant.image_url || 'https://placehold.co/100'}" style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 4px solid var(--accent-primary); margin-bottom: 1rem;">
            <h2 style="margin-bottom: 0.5rem;">${restaurant.name} <i class="fas fa-check-circle" style="color: #3498db; font-size: 1rem;"></i></h2>
            <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">${restaurant.cuisine_type} • ${restaurant.location}</p>
            
            <div style="display: flex; justify-content: center; gap: 3rem; margin-bottom: 1.5rem;">
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: 700;">${restaurant.stats.posts}</div>
                    <div style="font-size: 0.8rem; opacity: 0.7;">Posts</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: 700;" id="follower-count-${id}">${restaurant.stats.followers}</div>
                    <div style="font-size: 0.8rem; opacity: 0.7;">Followers</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: 700;">${restaurant.rating}</div>
                    <div style="font-size: 0.8rem; opacity: 0.7;">Rating</div>
                </div>
            </div>
            
            <button class="btn ${btnClass} btn-sm" onclick="followRestaurant(${id}, this)">${btnText}</button>
            <button class="btn btn-glass btn-sm"><i class="fas fa-paper-plane"></i> Message</button>
        `;
        
        // Save current restaurant for tab switching
        window.currentProfileId = id;
        switchProfileTab('posts'); // Default load posts
        
    } catch (err) {
        console.error(err);
        header.innerHTML = 'Error loading profile.';
    }
}

window.followRestaurant = async function(id, btn) {
    // Optimistic
    const isFollowing = btn.textContent.trim() === 'Following';
    const countEl = document.getElementById(`follower-count-${id}`);
    
    if (isFollowing) {
        btn.textContent = 'Follow';
        btn.className = 'btn btn-primary btn-sm';
        if(countEl) countEl.textContent = parseInt(countEl.textContent) - 1;
    } else {
        btn.textContent = 'Following';
        btn.className = 'btn btn-secondary btn-sm';
        if(countEl) countEl.textContent = parseInt(countEl.textContent) + 1;
    }
    
    try {
        await fetch('/api/follow/toggle/', {
            method: 'POST',
            headers: { 'X-CSRFToken': getCookie('csrftoken'), 'Content-Type': 'application/json' },
            body: JSON.stringify({ restaurant_id: id })
        });
    } catch (err) {
        console.error(err);
    }
}

window.switchProfileTab = async function(tab) {
    const body = document.getElementById('profile-body');
    const links = document.querySelectorAll('.tab-link');
    links.forEach(l => l.classList.remove('active'));
    
    if(tab === 'posts') {
        links[0].classList.add('active');
        body.innerHTML = '<div style="padding:10px;"><i class="fas fa-spinner fa-spin"></i> Loading Posts...</div>';
        // Fetch Reels for this restaurant
        // Assuming filtered endpoint or filtering in JS. 
        // Note: Backend ReelViewSet didn't explicitly implement filter by restaurant, but standard ModelViewSet might support ?restaurant=ID if filter backend enabled.
        // If not, I'll filter client side from all reels (inefficient but OK for prototype).
        const res = await fetch('/api/reels/');
        const data = await res.json();
         // Filter manually since I didn't add DjangoFilterBackend
        const posts = data.filter(r => r.restaurant == window.currentProfileId);
        
        if(posts.length === 0) {
            body.innerHTML = '<div style="text-align:center; padding: 40px; color:gray;">No posts yet.</div>';
            return;
        }
        
        let html = '<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">';
        posts.forEach(p => {
            html += `
                <div style="aspect-ratio: 9/16; background: #000; position: relative; cursor: pointer;">
                    <video src="${p.video_url}" style="width: 100%; height: 100%; object-fit: cover;"></video>
                </div>
            `;
        });
        html += '</div>';
        body.innerHTML = html;
        
    } else {
        links[1].classList.add('active');
        body.innerHTML = '<div style="padding:10px;"><i class="fas fa-spinner fa-spin"></i> Loading Menu...</div>';
        // Fetch Menu
        const res = await fetch('/api/food-items/'); // Retrieve all and filter
        const data = await res.json();
        const menu = (data.results || data).filter(f => f.restaurant.id == window.currentProfileId);
        
        if(menu.length === 0) {
            body.innerHTML = '<div style="text-align:center; padding: 40px; color:gray;">No menu items found.</div>';
            return;
        }
        
        let html = '<div style="display: flex; flex-direction: column; gap: 10px;">';
        menu.forEach(item => {
            html += `
                <div class="glass-card" style="padding: 1rem; display: flex; gap: 1rem; align-items: center;">
                    <img src="${item.image_url || 'https://placehold.co/80'}" style="width: 60px; height: 60px; border-radius: 8px; object-fit: cover;">
                    <div>
                        <h4>${item.name}</h4>
                        <div style="color: var(--accent-primary); font-weight: bold;">₹${item.price}</div>
                    </div>
                </div>
            `;
        });
        html += '</div>';
        body.innerHTML = html;
    }
}

// Utility for CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// --- BOOKINGS & ORDERS LOGIC ---
async function fetchBookings() {
    const container = document.getElementById('bookingsContainer');
    if (!container) return;
    
    container.innerHTML = '<div style="text-align: center; padding: 2rem; color: var(--text-secondary);"><i class="fas fa-spinner fa-spin fa-2x"></i><br>Loading your bookings...</div>';
    
    try {
        const response = await fetch('/api/bookings/');
        if (!response.ok) throw new Error('Failed to fetch bookings');
        
        const bookings = await response.json();
        
        if (bookings.length === 0) {
            container.innerHTML = `
                <div class="glass-card" style="padding: 3rem; text-align: center;">
                    <i class="fas fa-calendar-times" style="font-size: 3rem; color: var(--text-secondary); margin-bottom: 1rem;"></i>
                    <h3 style="color: var(--text-secondary);">No Bookings Yet</h3>
                    <p style="color: var(--text-secondary); opacity: 0.7;">Your table reservations will appear here.</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = '';
        bookings.forEach(booking => {
            const bookingCard = document.createElement('div');
            bookingCard.className = 'glass-card';
            bookingCard.style.cssText = 'padding: 1.5rem; margin-bottom: 1rem;';
            
            const bookingDate = new Date(booking.date_time);
            const formattedDate = bookingDate.toLocaleDateString('en-US', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
            });
            const formattedTime = bookingDate.toLocaleTimeString('en-US', { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
            
            const statusColor = booking.status === 'Confirmed' ? '#4cd137' : 
                               booking.status === 'Cancelled' ? '#e74c3c' : '#f39c12';
            
            bookingCard.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                    <div>
                        <h3 style="margin-bottom: 0.5rem;">${booking.restaurant_name || 'Restaurant'}</h3>
                        <p style="color: var(--text-secondary); font-size: 0.9rem;">
                            <i class="fas fa-calendar"></i> ${formattedDate}
                        </p>
                        <p style="color: var(--text-secondary); font-size: 0.9rem;">
                            <i class="fas fa-clock"></i> ${formattedTime}
                        </p>
                    </div>
                    <div style="text-align: right;">
                        <span style="background: ${statusColor}; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem; font-weight: 600;">
                            ${booking.status}
                        </span>
                    </div>
                </div>
                <div style="display: flex; gap: 2rem; color: var(--text-secondary); font-size: 0.9rem;">
                    <span><i class="fas fa-users"></i> ${booking.people_count} ${booking.people_count === 1 ? 'Person' : 'People'}</span>
                    ${booking.table_number ? `<span><i class="fas fa-chair"></i> Table ${booking.table_number}</span>` : ''}
                </div>
            `;
            
            container.appendChild(bookingCard);
        });
        
    } catch (error) {
        console.error('Error fetching bookings:', error);
        container.innerHTML = `
            <div class="glass-card" style="padding: 2rem; text-align: center;">
                <i class="fas fa-exclamation-triangle" style="font-size: 2rem; color: #e74c3c; margin-bottom: 1rem;"></i>
                <p style="color: #e74c3c;">Failed to load bookings. Please try again later.</p>
            </div>
        `;
    }
}
