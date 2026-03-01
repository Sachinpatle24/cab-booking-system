import bcrypt
from flask_jwt_extended import create_access_token
from app.database.db_connection import get_db_cursor
from app.utils.validators import validate_email, validate_password, validate_role
from app.utils.response_handler import success_response, error_response
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

def register_user(data):
    try:
        name = data.get("name", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        role = data.get("role", "PASSENGER").upper()

        if not all([name, email, password]):
            return error_response("Name, email, and password are required")

        if not validate_email(email):
            return error_response("Invalid email format")

        if not validate_password(password):
            return error_response("Password must be at least 8 characters")

        if not validate_role(role):
            return error_response("Invalid role")

        # Validate driver-specific fields
        if role == "DRIVER":
            license_number = data.get("license_number", "").strip()
            vehicle_number = data.get("vehicle_number", "").strip()
            vehicle_type = data.get("vehicle_type", "").strip()
            
            if not all([license_number, vehicle_number, vehicle_type]):
                return error_response("License number, vehicle number, and vehicle type are required for drivers")

        with get_db_cursor() as cursor:
            cursor.execute("SELECT user_id FROM Users WHERE email = ?", (email,))
            if cursor.fetchone():
                return error_response("Email already registered", 409)

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute(
                "INSERT INTO Users (name, email, password, role) VALUES (?, ?, ?, ?)",
                (name, email, hashed_password, role)
            )
            
            # Get the newly created user_id
            cursor.execute("SELECT @@IDENTITY")
            user_id = cursor.fetchone()[0]
            
            # If role is DRIVER, create driver and cab records
            if role == "DRIVER":
                # Create driver record
                cursor.execute(
                    "INSERT INTO Drivers (user_id, license_number, availability_status) VALUES (?, ?, 'AVAILABLE')",
                    (user_id, license_number)
                )
                
                # Get driver_id
                cursor.execute("SELECT @@IDENTITY")
                driver_id = cursor.fetchone()[0]
                
                # Create cab record
                is_electric = 1 if data.get("is_electric", False) else 0
                cursor.execute(
                    "INSERT INTO Cabs (driver_id, vehicle_number, vehicle_type, is_electric) VALUES (?, ?, ?, ?)",
                    (driver_id, vehicle_number, vehicle_type, is_electric)
                )
                
                logger.info(f"Driver and vehicle registered for user {user_id}")

        logger.info(f"User registered: {email}")
        return success_response("User registered successfully", status=201)

    except Exception as e:
        logger.error(f"Registration error: {e}")
        return error_response("Registration failed", 500)

def login_user(data):
    try:
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not email or not password:
            return error_response("Email and password are required")

        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT user_id, password, role, name FROM Users WHERE email = ?",
                (email,)
            )
            user = cursor.fetchone()

            if not user:
                return error_response("Invalid credentials", 401)

            user_id, stored_password, role, name = user

            if not bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                return error_response("Invalid credentials", 401)

            access_token = create_access_token(
                identity=str(user_id),
                additional_claims={"role": role}
            )

        logger.info(f"User logged in: {email}")
        return success_response("Login successful", {
            "access_token": access_token,
            "user": {"id": user_id, "name": name, "role": role}
        })

    except Exception as e:
        logger.error(f"Login error: {e}")
        return error_response("Login failed", 500)
