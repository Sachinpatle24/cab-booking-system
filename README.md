# Cab Booking System

A complete cab booking REST API with eco-friendly features, built with Flask and SQL Server.

## Features

- **User Management**: Passenger, Driver, and Admin roles
- **Ride Booking**: Request, accept, complete, and cancel rides
- **Real-time Updates**: Auto-refresh for available rides
- **Eco Mode**: Discounted fares for electric vehicles
- **Rating System**: Passengers rate drivers and vice versa
- **Payment Tracking**: Payment history and status
- **Admin Dashboard**: Statistics, user management, ride monitoring
- **Driver Earnings**: Track completed rides and total earnings
- **JWT Authentication**: Secure token-based authentication

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: Microsoft SQL Server
- **Authentication**: JWT (JSON Web Tokens)
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **API Documentation**: Swagger/Flasgger

## Installation

### Prerequisites
- Python 3.8+
- SQL Server (with ODBC Driver 17 or 18)
- pip

### Setup Steps

1. **Clone the repository**
```bash
cd cab-booking-system
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure database**
- Update `.env` file with your SQL Server details:
```
DB_SERVER=localhost\MSSQLSERVER01
DB_NAME=CabBookingDB
DB_DRIVER=ODBC Driver 18 for SQL Server
SECRET_KEY=your_secret_key_here
```

4. **Create database**
- Run the SQL script in `app/database/schema.sql` to create tables

5. **Run the application**
```bash
python run.py
```

Backend runs on: `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login

### Rides
- `POST /api/rides/request` - Request a ride (Passenger)
- `GET /api/rides/pending` - Get available rides (Driver)
- `PATCH /api/rides/{id}/accept` - Accept ride (Driver)
- `PATCH /api/rides/{id}/complete` - Complete ride (Driver)
- `PATCH /api/rides/{id}/cancel` - Cancel ride (Passenger)

### Drivers
- `PATCH /api/drivers/status` - Update driver status
- `GET /api/drivers/rides` - Get driver's rides
- `GET /api/drivers/earnings` - Get earnings summary
- `GET /api/drivers/profile` - Get driver profile

### Users
- `GET /api/users/profile` - Get user profile
- `GET /api/users/rides` - Get user ride history

### Payments
- `GET /api/payments/history` - Get payment history

### Admin
- `GET /api/admin/stats` - Dashboard statistics
- `GET /api/admin/users` - All users list
- `GET /api/admin/rides` - All rides list

### Ratings
- `POST /api/ratings/ride/{id}` - Submit rating
- `GET /api/ratings/ride/{id}` - Get ride rating

## API Documentation

Access Swagger UI at: `http://localhost:5000/apidocs/`

## Database Schema

### Tables
- **Users**: User accounts (Passenger, Driver, Admin)
- **Drivers**: Driver-specific data (license, vehicle, rating)
- **Cabs**: Vehicle information
- **Rides**: Ride requests and history
- **Payments**: Payment records
- **Ratings**: Ride ratings (passenger ↔ driver)

## Usage

### Using Frontend
1. Open `cab-booking-frontend/index.html` in browser
2. Register as Passenger or Driver
3. Login and use the dashboard

### Using API Directly
**Example: Login**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'
```

**Example: Request Ride (with JWT token)**
```bash
curl -X POST http://localhost:5000/api/rides/request \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "pickup_location": "Location A",
    "drop_location": "Location B",
    "distance": 10.5,
    "eco_mode_enabled": true
  }'
```

## Project Structure

```
cab-booking-system/
├── app/
│   ├── database/
│   │   ├── db_connection.py    # Database connection
│   │   └── schema.sql          # Database schema
│   ├── routes/                 # API endpoints
│   │   ├── auth_routes.py
│   │   ├── ride_routes.py
│   │   ├── driver_routes.py
│   │   ├── user_routes.py
│   │   ├── payment_routes.py
│   │   ├── admin_routes.py
│   │   └── rating_routes.py
│   ├── services/               # Business logic
│   │   ├── auth_service.py
│   │   ├── ride_service.py
│   │   ├── driver_service.py
│   │   ├── fare_service.py
│   │   └── eco_service.py
│   ├── utils/                  # Helper functions
│   │   ├── jwt_handler.py
│   │   ├── response_handler.py
│   │   ├── validators.py
│   │   └── logger.py
│   ├── __init__.py             # Flask app initialization
│   └── config.py               # Configuration
├── cab-booking-frontend/       # Frontend files
│   ├── index.html
│   ├── app.js
│   └── style.css
├── logs/                       # Application logs
├── .env                        # Environment variables
├── requirements.txt            # Python dependencies
├── run.py                      # Application entry point
└── README.md                   # Documentation

```

## Key Features Explained

### Eco Mode
- Electric vehicles get ₹2/km discount
- Base fare: ₹50
- Normal rate: ₹12/km
- Eco rate: ₹10/km
- Eco score increases for passengers using eco mode

### Ride Flow
1. Passenger requests ride → Status: REQUESTED
2. Driver accepts ride → Status: ACCEPTED, Driver: BUSY
3. Driver completes ride → Status: COMPLETED, Driver: AVAILABLE
4. Either can cancel → Status: CANCELLED

### Rating System
- Only completed rides can be rated
- Passengers rate drivers (1-5 stars)
- Drivers rate passengers (1-5 stars)
- Driver average rating auto-calculated

### Admin Features
- View total passengers, drivers, rides
- Monitor total revenue
- Track active drivers
- Manage all users and rides

## Default Admin Account

After running the database schema, create admin user:
```sql
INSERT INTO Users (name, email, password_hash, role, eco_score)
VALUES ('Admin', 'admin@gmail.com', 'HASHED_PASSWORD', 'ADMIN', 0);
```

Or register through frontend and update role:
```sql
UPDATE Users SET role = 'ADMIN' WHERE email = 'your@email.com';
```

## Security

- Passwords hashed with bcrypt
- JWT tokens expire after 12 hours
- CORS enabled for cross-origin requests
- SQL injection prevention with parameterized queries

## Dependencies

```
Flask==3.1.3
Flask-JWT-Extended==4.7.1
Flask-CORS==5.0.0
pyodbc==5.3.0
bcrypt==5.0.0
python-dotenv==1.2.1
flasgger==0.9.7.1
```

## Troubleshooting

### Database Connection Issues
- Verify SQL Server is running
- Check ODBC driver version in `.env`
- Ensure Windows Authentication or SQL Auth is configured

### CORS Errors
- Backend must run on `http://localhost:5000`
- Frontend can run from any origin

### JWT Token Errors
- Token expires after 12 hours
- Re-login to get new token

## License

MIT License

## Contact

For issues or questions, please create an issue in the repository.
