const API_URL = 'http://localhost:5000';
let token = localStorage.getItem('token');
let userRole = localStorage.getItem('role');
let refreshInterval = null;

// Initialize
if (token) {
    document.getElementById('navLinks').style.display = 'none';
    document.getElementById('navUser').style.display = 'flex';
    document.getElementById('userName').textContent = localStorage.getItem('name');
    showPage(userRole === 'ADMIN' ? 'admin' : (userRole === 'DRIVER' ? 'driver' : 'passenger'));
    if (userRole === 'PASSENGER') {
        loadRideHistory();
        loadPaymentHistory();
        loadEcoScore();
        startAutoRefresh();
    } else if (userRole === 'DRIVER') {
        loadDriverRides();
        loadAvailableRides();
        loadDriverVehicle();
        loadDriverEarnings();
        startAutoRefresh();
    } else if (userRole === 'ADMIN') {
        loadAdminStats();
    }
}

function startAutoRefresh() {
    if (refreshInterval) clearInterval(refreshInterval);
    refreshInterval = setInterval(() => {
        if (userRole === 'DRIVER') {
            loadAvailableRides();
            loadDriverRides();
        } else if (userRole === 'PASSENGER') {
            loadRideHistory();
        }
    }, 10000); // Refresh every 10 seconds
}

function showPage(page) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(page + 'Page').classList.add('active');
}

function showToast(message) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3000);
}

function toggleDriverFields() {
    const role = document.getElementById('regRole').value;
    const driverFields = document.getElementById('driverFields');
    const inputs = driverFields.querySelectorAll('input[type="text"], select');
    
    if (role === 'DRIVER') {
        driverFields.style.display = 'block';
        inputs.forEach(input => input.required = true);
    } else {
        driverFields.style.display = 'none';
        inputs.forEach(input => input.required = false);
    }
}

async function register(e) {
    e.preventDefault();
    const role = document.getElementById('regRole').value;
    const data = {
        name: document.getElementById('regName').value,
        email: document.getElementById('regEmail').value,
        password: document.getElementById('regPassword').value,
        role: role
    };

    if (role === 'DRIVER') {
        data.license_number = document.getElementById('regLicense').value;
        data.vehicle_number = document.getElementById('regVehicleNumber').value;
        data.vehicle_type = document.getElementById('regVehicleType').value;
        data.is_electric = document.getElementById('regIsElectric').checked;
    }

    try {
        const res = await fetch(`${API_URL}/api/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await res.json();
        
        if (result.success) {
            showToast(result.message);
            showPage('login');
        } else {
            showToast(result.error || 'Registration failed');
        }
    } catch (err) {
        showToast('Network error. Please check backend is running.');
        console.error('Register error:', err);
    }
}

async function login(e) {
    e.preventDefault();
    const data = {
        email: document.getElementById('loginEmail').value,
        password: document.getElementById('loginPassword').value
    };

    try {
        const res = await fetch(`${API_URL}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await res.json();
        
        if (result.success) {
            token = result.data.access_token;
            userRole = result.data.user.role;
            localStorage.setItem('token', token);
            localStorage.setItem('role', userRole);
            localStorage.setItem('name', result.data.user.name);
            
            document.getElementById('navLinks').style.display = 'none';
            document.getElementById('navUser').style.display = 'flex';
            document.getElementById('userName').textContent = result.data.user.name;
            
            showPage(userRole === 'ADMIN' ? 'admin' : (userRole === 'DRIVER' ? 'driver' : 'passenger'));
            showToast('Login successful');
            
            if (userRole === 'PASSENGER') {
                loadRideHistory();
                loadPaymentHistory();
                loadEcoScore();
                startAutoRefresh();
            } else if (userRole === 'DRIVER') {
                loadDriverRides();
                loadAvailableRides();
                loadDriverVehicle();
                loadDriverEarnings();
                startAutoRefresh();
            } else if (userRole === 'ADMIN') {
                loadAdminStats();
            }
        } else {
            showToast(result.error || 'Login failed');
        }
    } catch (err) {
        showToast('Network error. Please check backend is running.');
        console.error('Login error:', err);
    }
}

function logout() {
    if (refreshInterval) clearInterval(refreshInterval);
    localStorage.clear();
    token = null;
    userRole = null;
    document.getElementById('navLinks').style.display = 'flex';
    document.getElementById('navUser').style.display = 'none';
    showPage('login');
    showToast('Logged out');
}

async function requestRide(e) {
    e.preventDefault();
    const distance = parseFloat(document.getElementById('distance').value);
    const ecoMode = document.getElementById('ecoMode').checked;
    
    // Calculate estimated fare
    const baseFare = 50;
    const perKmRate = ecoMode ? 10 : 12;
    const estimatedFare = baseFare + (distance * perKmRate);
    
    document.getElementById('estimatedFare').textContent = `Estimated Fare: ₹${estimatedFare.toFixed(2)}`;
    
    const data = {
        pickup_location: document.getElementById('pickup').value,
        drop_location: document.getElementById('dropoff').value,
        distance: distance,
        eco_mode_enabled: ecoMode
    };

    try {
        const res = await fetch(`${API_URL}/api/rides/request`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(data)
        });
        const result = await res.json();
        
        if (result.success) {
            showToast(result.message);
            e.target.reset();
            document.getElementById('estimatedFare').textContent = '';
            loadRideHistory();
        } else {
            showToast(result.error || 'Failed to request ride');
        }
    } catch (err) {
        showToast('Network error. Failed to request ride.');
        console.error('Request ride error:', err);
    }
}

function calculateFare() {
    const distance = parseFloat(document.getElementById('distance').value) || 0;
    const ecoMode = document.getElementById('ecoMode').checked;
    const baseFare = 50;
    const perKmRate = ecoMode ? 10 : 12;
    const estimatedFare = baseFare + (distance * perKmRate);
    document.getElementById('estimatedFare').textContent = `Estimated Fare: ₹${estimatedFare.toFixed(2)}`;
}

function showTab(tab) {
    document.querySelectorAll('#passengerPage .tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('#passengerPage .tab-content').forEach(c => c.classList.remove('active'));
    event.target.classList.add('active');
    document.getElementById(tab + 'Tab').classList.add('active');
}

function showDriverTab(tab) {
    document.querySelectorAll('#driverPage .tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('#driverPage .tab-content').forEach(c => c.classList.remove('active'));
    event.target.classList.add('active');
    document.getElementById(tab + 'Tab').classList.add('active');
}

function filterRides() {
    const status = document.getElementById('filterStatus').value;
    loadRideHistory(status);
}

async function loadRideHistory(filterStatus = '') {
    try {
        const res = await fetch(`${API_URL}/api/users/rides`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const result = await res.json();
        const list = document.getElementById('ridesList');
        
        if (result.success && result.data.rides.length > 0) {
            let rides = result.data.rides;
            if (filterStatus) {
                rides = rides.filter(r => r.ride_status === filterStatus);
            }
            
            list.innerHTML = rides.map(ride => `
                <div class="ride-card">
                    <h4>Ride #${ride.ride_id}</h4>
                    <p><strong>From:</strong> ${ride.pickup_location}</p>
                    <p><strong>To:</strong> ${ride.drop_location}</p>
                    <p><strong>Distance:</strong> ${ride.distance} km</p>
                    <p><strong>Fare:</strong> ₹${ride.fare}</p>
                    <p><strong>Status:</strong> <span class="status-badge status-${ride.ride_status}">${ride.ride_status}</span></p>
                    <p><strong>Date:</strong> ${new Date(ride.created_at).toLocaleString()}</p>
                    ${ride.ride_status === 'REQUESTED' ? `<button onclick="cancelRide(${ride.ride_id})" class="cancel-btn">Cancel Ride</button>` : ''}
                    ${ride.ride_status === 'COMPLETED' ? `<button onclick="openRatingModal(${ride.ride_id})">Rate Driver</button>` : ''}
                </div>
            `).join('');
        } else {
            list.innerHTML = '<div class="empty-state">No rides yet. Book your first ride!</div>';
        }
    } catch (err) {
        console.error('Failed to load rides:', err);
        document.getElementById('ridesList').innerHTML = '<div class="empty-state">Error loading rides.</div>';
    }
}

async function cancelRide(rideId) {
    if (!confirm('Are you sure you want to cancel this ride?')) return;
    
    try {
        const res = await fetch(`${API_URL}/api/rides/${rideId}/cancel`, {
            method: 'PATCH',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const result = await res.json();
        
        if (result.success) {
            showToast('Ride cancelled successfully');
            loadRideHistory();
        } else {
            showToast(result.error || 'Failed to cancel ride');
        }
    } catch (err) {
        showToast('Network error. Failed to cancel ride.');
        console.error('Cancel ride error:', err);
    }
}

async function loadEcoScore() {
    try {
        const res = await fetch(`${API_URL}/api/users/profile`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const result = await res.json();
        
        if (result.success) {
            document.getElementById('ecoScore').textContent = `Eco Score: ${result.data.profile.eco_score}`;
        }
    } catch (err) {
        console.error('Failed to load eco score:', err);
    }
}

async function loadPaymentHistory() {
    try {
        const res = await fetch(`${API_URL}/api/payments/history`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const result = await res.json();
        const list = document.getElementById('paymentsList');
        
        if (result.success && result.data.payments.length > 0) {
            list.innerHTML = result.data.payments.map(payment => `
                <div class="payment-card">
                    <h4>Payment #${payment.payment_id}</h4>
                    <p><strong>Ride ID:</strong> ${payment.ride_id}</p>
                    <p><strong>Amount:</strong> ₹${payment.amount}</p>
                    <p><strong>Status:</strong> <span class="status-badge status-${payment.payment_status}">${payment.payment_status}</span></p>
                    <p><strong>Date:</strong> ${new Date(payment.payment_date).toLocaleString()}</p>
                </div>
            `).join('');
        } else {
            list.innerHTML = '<div class="empty-state">No payment history available.</div>';
        }
    } catch (err) {
        console.error('Failed to load payments:', err);
        document.getElementById('paymentsList').innerHTML = '<div class="empty-state">Error loading payments.</div>';
    }
}

async function loadDriverVehicle() {
    try {
        const res = await fetch(`${API_URL}/api/drivers/profile`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const result = await res.json();
        
        if (result.success) {
            const profile = result.data.profile;
            document.getElementById('vehicleInfo').innerHTML = `
                <p><strong>Vehicle:</strong> ${profile.vehicle_number || 'Not registered'}</p>
                <p><strong>Type:</strong> ${profile.vehicle_type || 'N/A'}</p>
                <p><strong>License:</strong> ${profile.license_number}</p>
            `;
        }
    } catch (err) {
        console.error('Failed to load vehicle info:', err);
    }
}

async function loadDriverEarnings() {
    try {
        const res = await fetch(`${API_URL}/api/drivers/earnings`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const result = await res.json();
        
        if (result.success) {
            document.getElementById('earnings').innerHTML = `
                <p><strong>Total Earnings:</strong> Rs.${result.data.total_earnings}</p>
                <p><strong>Completed Rides:</strong> ${result.data.completed_rides}</p>
            `;
        }
    } catch (err) {
        console.error('Failed to load earnings:', err);
    }
}

async function loadDriverRides() {
    try {
        const res = await fetch(`${API_URL}/api/drivers/rides`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const result = await res.json();
        const list = document.getElementById('driverRidesList');
        
        if (result.success && result.data.rides.length > 0) {
            list.innerHTML = result.data.rides.map(ride => `
                <div class="ride-card">
                    <h4>Ride #${ride.ride_id} - ${ride.passenger_name}</h4>
                    <p><strong>From:</strong> ${ride.pickup_location}</p>
                    <p><strong>To:</strong> ${ride.drop_location}</p>
                    <p><strong>Distance:</strong> ${ride.distance} km</p>
                    <p><strong>Fare:</strong> ₹${ride.fare}</p>
                    <p><strong>Status:</strong> <span class="status-badge status-${ride.ride_status}">${ride.ride_status}</span></p>
                    ${ride.ride_status === 'ACCEPTED' ? `<button onclick="completeRide(${ride.ride_id})">Complete Ride</button>` : ''}
                    ${ride.ride_status === 'COMPLETED' ? `<button onclick="openRatingModal(${ride.ride_id})">Rate Passenger</button>` : ''}
                </div>
            `).join('');
        } else {
            list.innerHTML = '<div class="empty-state">No rides accepted yet.</div>';
        }
    } catch (err) {
        console.error('Failed to load driver rides:', err);
        document.getElementById('driverRidesList').innerHTML = '<div class="empty-state">Error loading rides.</div>';
    }
}

async function loadAvailableRides() {
    try {
        const res = await fetch(`${API_URL}/api/rides/pending`);
        const result = await res.json();
        const list = document.getElementById('availableRides');
        
        if (result.success && result.data.rides.length > 0) {
            list.innerHTML = result.data.rides.map(ride => `
                <div class="ride-card">
                    <h4>Ride #${ride.ride_id} - ${ride.passenger_name}</h4>
                    <p><strong>From:</strong> ${ride.pickup_location}</p>
                    <p><strong>To:</strong> ${ride.drop_location}</p>
                    <p><strong>Distance:</strong> ${ride.distance} km</p>
                    <p><strong>Fare:</strong> ₹${ride.fare}</p>
                    <p><strong>Requested:</strong> ${new Date(ride.created_at).toLocaleString()}</p>
                    <button onclick="acceptRide(${ride.ride_id})">Accept Ride</button>
                </div>
            `).join('');
        } else {
            list.innerHTML = '<div class="empty-state">No pending rides available.</div>';
        }
    } catch (err) {
        console.error('Failed to load available rides:', err);
        document.getElementById('availableRides').innerHTML = '<div class="empty-state">Error loading rides.</div>';
    }
}

async function acceptRide(rideId) {
    try {
        const res = await fetch(`${API_URL}/api/rides/${rideId}/accept`, {
            method: 'PATCH',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const result = await res.json();
        
        if (result.success) {
            showToast(result.message);
            loadAvailableRides();
            loadDriverRides();
        } else {
            showToast(result.error || 'Failed to accept ride');
        }
    } catch (err) {
        showToast('Network error. Failed to accept ride.');
        console.error('Accept ride error:', err);
    }
}

async function completeRide(rideId) {
    try {
        const res = await fetch(`${API_URL}/api/rides/${rideId}/complete`, {
            method: 'PATCH',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const result = await res.json();
        
        if (result.success) {
            showToast(result.message);
            loadDriverRides();
            loadDriverEarnings();
        } else {
            showToast(result.error || 'Failed to complete ride');
        }
    } catch (err) {
        showToast('Network error. Failed to complete ride.');
        console.error('Complete ride error:', err);
    }
}

async function updateDriverStatus() {
    const status = document.getElementById('driverStatus').value;
    
    try {
        const res = await fetch(`${API_URL}/api/drivers/status`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ status })
        });
        const result = await res.json();
        
        if (result.success) {
            showToast(result.message);
            if (status === 'AVAILABLE') loadAvailableRides();
        } else {
            showToast(result.error || 'Failed to update status');
        }
    } catch (err) {
        showToast('Network error. Failed to update status.');
        console.error('Update status error:', err);
    }
}

let currentRideId = null;
let selectedRating = 0;

function openRatingModal(rideId) {
    currentRideId = rideId;
    selectedRating = 0;
    document.getElementById('ratingModal').style.display = 'block';
    document.getElementById('ratingComment').value = '';
    document.querySelectorAll('.star').forEach(s => s.classList.remove('active'));
}

function closeRatingModal() {
    document.getElementById('ratingModal').style.display = 'none';
}

function setRating(rating) {
    selectedRating = rating;
    document.querySelectorAll('.star').forEach((star, index) => {
        if (index < rating) {
            star.classList.add('active');
        } else {
            star.classList.remove('active');
        }
    });
}

async function submitRating() {
    if (selectedRating === 0) {
        showToast('Please select a rating');
        return;
    }

    try {
        const res = await fetch(`${API_URL}/api/ratings/ride/${currentRideId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                rating: selectedRating,
                comment: document.getElementById('ratingComment').value
            })
        });
        const result = await res.json();

        if (result.success) {
            showToast('Rating submitted successfully');
            closeRatingModal();
            if (userRole === 'PASSENGER') loadRideHistory();
            else loadDriverRides();
        } else {
            showToast(result.error || 'Failed to submit rating');
        }
    } catch (err) {
        showToast('Network error. Failed to submit rating.');
    }
}

function showAdminTab(tab) {
    document.querySelectorAll('#adminPage .tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('#adminPage .tab-content').forEach(c => c.classList.remove('active'));
    event.target.classList.add('active');
    document.getElementById(tab + 'Tab').classList.add('active');
    
    if (tab === 'stats') loadAdminStats();
    else if (tab === 'users') loadAdminUsers();
    else if (tab === 'rides') loadAdminRides();
}

async function loadAdminStats() {
    try {
        const res = await fetch(`${API_URL}/api/admin/stats`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const result = await res.json();
        
        if (result.success) {
            const stats = result.data;
            document.getElementById('adminStats').innerHTML = `
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                    <div class="info-card"><h3>${stats.total_passengers}</h3><p>Total Passengers</p></div>
                    <div class="info-card"><h3>${stats.total_drivers}</h3><p>Total Drivers</p></div>
                    <div class="info-card"><h3>${stats.total_rides}</h3><p>Total Rides</p></div>
                    <div class="info-card"><h3>${stats.completed_rides}</h3><p>Completed Rides</p></div>
                    <div class="info-card"><h3>₹${stats.total_revenue}</h3><p>Total Revenue</p></div>
                    <div class="info-card"><h3>${stats.active_drivers}</h3><p>Active Drivers</p></div>
                </div>
            `;
        }
    } catch (err) {
        console.error('Failed to load admin stats:', err);
    }
}

async function loadAdminUsers() {
    try {
        const res = await fetch(`${API_URL}/api/admin/users`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const result = await res.json();
        
        if (result.success) {
            document.getElementById('adminUsersList').innerHTML = result.data.users.map(user => `
                <div class="ride-card">
                    <h4>${user.name} - ${user.role}</h4>
                    <p><strong>Email:</strong> ${user.email}</p>
                    <p><strong>Eco Score:</strong> ${user.eco_score}</p>
                    <p><strong>Joined:</strong> ${new Date(user.created_at).toLocaleDateString()}</p>
                </div>
            `).join('');
        }
    } catch (err) {
        console.error('Failed to load users:', err);
    }
}

async function loadAdminRides() {
    try {
        const res = await fetch(`${API_URL}/api/admin/rides`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const result = await res.json();
        
        if (result.success) {
            document.getElementById('adminRidesList').innerHTML = result.data.rides.map(ride => `
                <div class="ride-card">
                    <h4>Ride #${ride.ride_id}</h4>
                    <p><strong>Passenger:</strong> ${ride.passenger}</p>
                    <p><strong>Driver:</strong> ${ride.driver}</p>
                    <p><strong>Route:</strong> ${ride.pickup} → ${ride.drop}</p>
                    <p><strong>Distance:</strong> ${ride.distance} km | <strong>Fare:</strong> ₹${ride.fare}</p>
                    <p><strong>Status:</strong> <span class="status-badge status-${ride.status}">${ride.status}</span></p>
                </div>
            `).join('');
        }
    } catch (err) {
        console.error('Failed to load rides:', err);
    }
}
