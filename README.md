# Cab Booking System - Backend API

A RESTful backend API for a cab booking platform built with Flask and Microsoft SQL Server. Supports role-based access for Passengers, Drivers, and Admins with JWT authentication, dynamic fare calculation, eco-friendly ride incentives, and a bidirectional rating system.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
- [Database Design](#database-design)
- [Fare Calculation Logic](#fare-calculation-logic)
- [Ride Lifecycle](#ride-lifecycle)
- [Security](#security)
- [Environment Configuration](#environment-configuration)
- [Dependencies](#dependencies)

---

## Overview

This project demonstrates backend API development with a focus on clean architecture, relational database design, authentication, role-based authorization, and business logic implementation.

The API serves three user roles — Passenger, Driver, and Admin — each with distinct permissions and capabilities. It also features an eco-scoring system that rewards passengers for choosing environmentally friendly ride options.

---

## Key Features

- User registration and login with JWT-based authentication
- Role-based access control (Passenger, Driver, Admin)
- Complete ride lifecycle management (request, accept, complete, cancel)
- Dynamic fare calculation with eco and electric vehicle discounts
- Eco score tracking that rewards green ride choices
- Bidirectional rating system between passengers and drivers
- Driver availability and earnings management
- Admin dashboard with platform-wide statistics
- Payment record tracking for completed rides
- Interactive Swagger API documentation
- Structured logging with rotating file handler
- Environment-based configuration (development, production, testing)
- CORS support for cross-origin access

---

## Tech Stack

| Layer          | Technology                            |
|----------------|---------------------------------------|
| Language       | Python 3.8+                           |
| Framework      | Flask 3.1.3                           |
| Database       | Microsoft SQL Server (via pyodbc)     |
| Authentication | JWT (Flask-JWT-Extended)              |
| API Docs       | Swagger UI (Flasgger)                 |
| Server         | HTTPS (ad-hoc SSL for development)    |

---

## Architecture

The application follows a layered architecture with clear separation of concerns:

```
Routes (API Layer)  -->  Services (Business Logic)  -->  Database (Data Access)
        |
   Middlewares (Auth and Role Validation)
        |
   Utils (Logging, Validation, Response Formatting)
```

- **Routes** define API endpoints and handle HTTP request/response
- **Services** contain all business logic and database operations
- **Middlewares** enforce authentication and role-based authorization
- **Utils** provide reusable helpers for logging, input validation, and standardized responses
- **Config** manages environment-specific settings

---

## Project Structure

```
cab-booking-system/
├── app/
│   ├── database/
│   │   ├── db_connection.py        # Connection pooling and cursor context manager
│   │   └── schema.sql              # SQL Server table definitions
│   ├── middlewares/
│   │   └── auth_middleware.py       # Role-based access control decorator
│   ├── routes/
│   │   ├── auth_routes.py          # Registration and login
│   │   ├── ride_routes.py          # Ride request, accept, complete, cancel
│   │   ├── driver_routes.py        # Driver status, rides, earnings, profile
│   │   ├── user_routes.py          # User profile and ride history
│   │   ├── payment_routes.py       # Payment status and history
│   │   ├── admin_routes.py         # Admin statistics, user and ride management
│   │   └── rating_routes.py        # Submit and retrieve ride ratings
│   ├── services/
│   │   ├── auth_service.py         # User registration and login logic
│   │   ├── ride_service.py         # Ride lifecycle management
│   │   ├── driver_service.py       # Driver-specific operations
│   │   ├── user_service.py         # User profile and history queries
│   │   ├── payment_service.py      # Payment record queries
│   │   ├── admin_service.py        # Admin dashboard aggregation queries
│   │   ├── rating_service.py       # Bidirectional rating logic
│   │   ├── fare_service.py         # Dynamic fare calculation
│   │   └── eco_service.py          # Eco score calculation and updates
│   ├── utils/
│   │   ├── logger.py               # Rotating file logger configuration
│   │   ├── response_handler.py     # Standardized success/error JSON responses
│   │   └── validators.py           # Input validation (email, password, role, rating)
│   ├── __init__.py                 # Flask application factory
│   ├── config.py                   # Environment-based configuration classes
│   └── exceptions.py               # Custom exception hierarchy
├── logs/                           # Application log files (auto-generated)
├── .env                            # Environment variables (not committed)
├── .envexample                     # Environment variable template
├── .gitignore
├── requirements.txt
├── run.py                          # Application entry point
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Microsoft SQL Server (with ODBC Driver 17 or 18)
- pip

### Installation

1. Clone the repository
   ```bash
   git clone <repository-url>
   cd cab-booking-system
   ```

2. Create and activate a virtual environment
   ```bash
   python -m venv venv
   venv\Scripts\activate          # Windows
   # source venv/bin/activate     # macOS / Linux
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables

   Copy `.envexample` to `.env` and update the values:
   ```
   SECRET_KEY=<your-secret-key>
   DB_SERVER=<your-server-name>
   DB_NAME=<your-database-name>
   DB_DRIVER=ODBC Driver 18 for SQL Server
   ```

5. Set up the database

   Execute `app/database/schema.sql` on your SQL Server instance to create all required tables.

6. Start the server
   ```bash
   python run.py
   ```
   The API will be available at `https://localhost:8000`.

7. Access API documentation

   Swagger UI is available at `https://localhost:8000/apidocs/`.

---

## API Reference

All endpoints are prefixed with `/api`. Protected routes require a JWT token passed via the `Authorization: Bearer <token>` header.

### Authentication

| Method | Endpoint             | Description       | Access  |
|--------|----------------------|-------------------|---------|
| POST   | /api/auth/register   | Register new user | Public  |
| POST   | /api/auth/login      | Login and get JWT | Public  |

### Rides

| Method | Endpoint                    | Description           | Access    |
|--------|-----------------------------|-----------------------|-----------|
| POST   | /api/rides/request          | Request a new ride    | Passenger |
| GET    | /api/rides/pending          | List pending rides    | Driver    |
| PATCH  | /api/rides/{id}/accept      | Accept a ride         | Driver    |
| PATCH  | /api/rides/{id}/complete    | Complete a ride       | Driver    |
| PATCH  | /api/rides/{id}/cancel      | Cancel a ride         | Passenger |

### Drivers

| Method | Endpoint               | Description             | Access |
|--------|------------------------|-------------------------|--------|
| PATCH  | /api/drivers/status    | Update availability     | Driver |
| GET    | /api/drivers/rides     | Get assigned rides      | Driver |
| GET    | /api/drivers/earnings  | Get earnings summary    | Driver |
| GET    | /api/drivers/profile   | Get driver profile      | Driver |
| GET    | /api/drivers/available | List available drivers  | Public |

### Users

| Method | Endpoint           | Description       | Access        |
|--------|--------------------|-------------------|---------------|
| GET    | /api/users/profile | Get user profile  | Authenticated |
| GET    | /api/users/rides   | Get ride history  | Authenticated |

### Payments

| Method | Endpoint                   | Description             | Access        |
|--------|----------------------------|-------------------------|---------------|
| GET    | /api/payments/ride/{id}    | Get payment for a ride  | Authenticated |
| GET    | /api/payments/history      | Get payment history     | Authenticated |

### Admin

| Method | Endpoint          | Description          | Access |
|--------|-------------------|----------------------|--------|
| GET    | /api/admin/stats  | Platform statistics  | Admin  |
| GET    | /api/admin/users  | List all users       | Admin  |
| GET    | /api/admin/rides  | List all rides       | Admin  |

### Ratings

| Method | Endpoint                  | Description      | Access        |
|--------|---------------------------|------------------|---------------|
| POST   | /api/ratings/ride/{id}    | Submit a rating  | Authenticated |
| GET    | /api/ratings/ride/{id}    | Get ride ratings | Authenticated |

### Health Check

| Method | Endpoint | Description          | Access |
|--------|----------|----------------------|--------|
| GET    | /        | Service status       | Public |
| GET    | /health  | Health check         | Public |

---

## Database Design

The application uses six relational tables with foreign key constraints:

| Table    | Purpose                                                       |
|----------|---------------------------------------------------------------|
| Users    | User accounts with role assignment (Passenger, Driver, Admin) |
| Drivers  | Driver-specific data: license, availability status, rating    |
| Cabs     | Vehicle details: number, type, electric vehicle flag          |
| Rides    | Ride records with status, fare, eco mode, and timestamps      |
| Payments | Payment records linked to completed rides                     |
| Ratings  | Bidirectional ratings between passengers and drivers          |

The database connects via Windows Authentication (Trusted Connection) using the pyodbc driver.

---

## Fare Calculation Logic

Fares are calculated dynamically based on distance and ride options:

```
Fare = (Base Fare + Distance x Per-KM Rate) x Eco Discount x Electric Discount
```

| Parameter         | Value   |
|-------------------|---------|
| Base Fare         | 50      |
| Per-KM Rate       | 15      |
| Eco Mode Discount | 10% off |
| Electric Vehicle  | 5% off  |

Discounts are applied multiplicatively. Passengers also earn eco score points for choosing eco-friendly options:
- Eco Mode enabled: distance x 2 points
- Electric vehicle: distance x 3 points

---

## Ride Lifecycle

```
REQUESTED  -->  ACCEPTED  -->  COMPLETED
    |               |
    v               v
CANCELLED       CANCELLED
```

1. Passenger requests a ride. Status is set to REQUESTED and fare is calculated.
2. An available driver accepts the ride. Status changes to ACCEPTED and the driver is marked as BUSY.
3. The driver completes the ride. Status changes to COMPLETED, a payment record is created, the driver becomes AVAILABLE, and eco points are awarded.
4. Either party can cancel a pending or accepted ride. If the ride was accepted, the driver is freed.

Business rules enforced:
- A passenger cannot have more than one active ride at a time
- A driver cannot accept a new ride while already on one
- Only drivers with AVAILABLE status can accept rides

---

## Security

- Password hashing using bcrypt
- JWT token-based authentication with configurable expiry
- Role-based middleware restricting endpoint access by user role
- Parameterized SQL queries to prevent SQL injection
- CORS enabled for cross-origin requests
- HTTPS with self-signed SSL certificate in development

---

## Environment Configuration

The application supports multiple environments controlled by the `FLASK_ENV` variable:

| Environment | Debug Mode | JWT Token Expiry | Database          |
|-------------|------------|------------------|-------------------|
| development | Enabled    | 12 hours         | CabBookingDB      |
| production  | Disabled   | 1 hour           | CabBookingDB      |
| testing     | Enabled    | 12 hours         | CabBookingDB_Test |

```bash
set FLASK_ENV=production
python run.py
```

---

## Dependencies

| Package            | Version | Purpose                       |
|--------------------|---------|-------------------------------|
| Flask              | 3.1.3   | Web framework                 |
| Flask-JWT-Extended | 4.7.1   | JWT authentication            |
| Flask-CORS         | 5.0.0   | Cross-origin resource sharing |
| pyodbc             | 5.3.0   | SQL Server database driver    |
| bcrypt             | 5.0.0   | Password hashing              |
| python-dotenv      | 1.2.1   | Environment variable loading  |
| flasgger           | 0.9.7.1 | Swagger API documentation     |
| waitress           | 3.0.2   | Production WSGI server        |

