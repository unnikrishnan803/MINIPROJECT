/**
 * Location Services for Deliciae
 * Handles geolocation and fetching nearby restaurants.
 */

const LocationService = {
    // Configuration
    API_URL: '/api/nearby-restaurants/',
    DEFAULT_RADIUS_KM: 200, // Increased radius to ensure matches if user is far (e.g. testing)

    init: function() {
        console.log("LocationService Initialized");
        // Alert to verify it loads (remove later)
        // alert("Location Service Loaded"); 
        this.cacheDom();
        this.bindEvents();
        this.getUserLocation();
    },

    cacheDom: function() {
        this.locationDisplay = document.getElementById('locationDisplay');
        this.restaurantGrid = document.getElementById('restaurantGrid');
    },

    bindEvents: function() {
        // If there was a specific "Use my location" button, we'd bind it here
    },

    getUserLocation: function() {
        if (!navigator.geolocation) {
            this.updateLocationStatus("Geolocation not supported");
            return;
        }

        this.updateLocationStatus("Locating...");

        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                this.updateLocationStatus(`Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}`);
                this.fetchNearbyRestaurants(lat, lng);
            },
            (error) => {
                let msg = "Location access denied";
                if (error.code === 2) msg = "Position unavailable";
                if (error.code === 3) msg = "Connection timeout";
                this.updateLocationStatus(msg);
                console.error("Geolocation error:", error);
                
                // Fallback to Kochi for demo/testing if geolocation fails or is denied
                console.warn("Geolocation failed, using fallback (Kochi)");
                this.updateLocationStatus("Locating (Fallback)...");
                const kochiLat = 9.9312;
                const kochiLng = 76.2673;
                this.fetchNearbyRestaurants(kochiLat, kochiLng);
            },
            { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
        );
    },

    updateLocationStatus: function(statusText) {
        if (this.locationDisplay) {
            // Keep the icon, just update text
            this.locationDisplay.innerHTML = `Displaying for: ${statusText}`;
        }
    },

    fetchNearbyRestaurants: function(lat, lng) {
        const url = `${this.API_URL}?lat=${lat}&lng=${lng}&radius=${this.DEFAULT_RADIUS_KM}`;
        
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                this.renderRestaurants(data);
            })
            .catch(error => {
                console.error('Error fetching nearby restaurants:', error);
                if (this.restaurantGrid) {
                    this.restaurantGrid.innerHTML = `
                        <div class="col-span-full text-center text-gray-500 py-10">
                            <i class="fas fa-exclamation-triangle text-2xl mb-2"></i>
                            <p>Failed to load nearby restaurants.</p>
                            <p class="text-xs text-red-500 mt-2">${error.message}</p>
                        </div>
                    `;
                }
            });
    },

    renderRestaurants: function(restaurants) {
        if (!this.restaurantGrid) return;

        if (restaurants.length === 0) {
            this.restaurantGrid.innerHTML = `
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
            
            return `
                <div class="bg-[#1a1a1a] border border-white/10 rounded-[18px] overflow-hidden hover:border-[#FF6B35]/50 transition-all group">
                    <div class="relative h-48 overflow-hidden">
                        <img src="${imageUrl}" alt="${restaurant.name}" class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500">
                        <div class="absolute top-3 right-3 bg-black/70 backdrop-blur-md px-3 py-1 rounded-full text-xs font-bold text-white border border-white/10">
                            <i class="fas fa-clock text-[#FF6B35] mr-1"></i> ${restaurant.opening_time || '10:00'} - ${restaurant.closing_time || '22:00'}
                        </div>
                        <div class="absolute bottom-3 left-3 bg-black/70 backdrop-blur-md px-3 py-1 rounded-full text-xs font-bold text-white border border-white/10 flex items-center gap-1">
                            <i class="fas fa-location-arrow text-[#FF6B35]"></i> ${restaurant.distance_km} km away
                        </div>
                    </div>
                    
                    <div class="p-5">
                        <div class="flex justify-between items-start mb-2">
                            <h3 class="text-xl font-bold text-white group-hover:text-[#FF6B35] transition-colors">${restaurant.name}</h3>
                            <div class="flex items-center gap-1 bg-green-500/20 px-2 py-0.5 rounded-lg border border-green-500/30">
                                <span class="text-green-400 font-bold text-sm">${restaurant.rating}</span>
                                <i class="fas fa-star text-[10px] text-green-400"></i>
                            </div>
                        </div>
                        
                        <p class="text-gray-400 text-sm mb-4 line-clamp-1">${restaurant.location}</p>
                        
                        <div class="flex items-center justify-between pt-4 border-t border-white/10">
                            <div class="text-xs text-gray-500 font-mono bg-white/5 px-2 py-1 rounded">
                                ${restaurant.cuisine_type}
                            </div>
                            <a href="/search/?q=${encodeURIComponent(restaurant.name)}" class="text-[#FF6B35] text-sm font-semibold hover:underline">
                                View Menu <i class="fas fa-arrow-right ml-1"></i>
                            </a>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        this.restaurantGrid.innerHTML = html;
        
        // Add animation class
        this.restaurantGrid.classList.add('animate-fade-in');
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    LocationService.init();
});
