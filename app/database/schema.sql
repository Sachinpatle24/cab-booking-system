CREATE TABLE Users (
    user_id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(100) NOT NULL,
    email NVARCHAR(100) UNIQUE NOT NULL,
    password NVARCHAR(255) NOT NULL,
    role NVARCHAR(20) CHECK (role IN ('ADMIN', 'DRIVER', 'PASSENGER')) NOT NULL,
    eco_score INT DEFAULT 0,
    created_at DATETIME DEFAULT GETDATE()
);

CREATE TABLE Drivers (
    driver_id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT UNIQUE,
    license_number NVARCHAR(50) NOT NULL,
    availability_status NVARCHAR(20) DEFAULT 'OFFLINE',
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE Cabs (
    cab_id INT PRIMARY KEY IDENTITY(1,1),
    driver_id INT,
    vehicle_number NVARCHAR(20) NOT NULL,
    vehicle_type NVARCHAR(50),
    is_electric BIT DEFAULT 0,
    FOREIGN KEY (driver_id) REFERENCES Drivers(driver_id)
);

CREATE TABLE Rides (
    ride_id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT,
    driver_id INT,
    pickup_location NVARCHAR(255),
    drop_location NVARCHAR(255),
    distance FLOAT,
    fare DECIMAL(10,2),
    ride_status NVARCHAR(20) DEFAULT 'REQUESTED',
    eco_mode_enabled BIT DEFAULT 0,
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (driver_id) REFERENCES Drivers(driver_id)
);

CREATE TABLE Payments (
    payment_id INT PRIMARY KEY IDENTITY(1,1),
    ride_id INT,
    amount DECIMAL(10,2),
    payment_status NVARCHAR(20) DEFAULT 'PENDING',
    payment_date DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (ride_id) REFERENCES Rides(ride_id)
);