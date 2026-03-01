from app.database.db_connection import get_db_cursor
from app.services.fare_service import calculate_fare
from app.services.eco_service import update_eco_score, calculate_eco_points
from app.utils.response_handler import success_response, error_response
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

def request_ride(user_id, data):
    try:
        pickup = data.get('pickup_location', '').strip()
        drop = data.get('drop_location', '').strip()
        distance = float(data.get('distance', 0))
        eco_mode = data.get('eco_mode_enabled', False)

        if not pickup or not drop:
            return error_response("Pickup and drop locations are required")

        if distance <= 0:
            return error_response("Invalid distance")

        fare = calculate_fare(distance, eco_mode)

        with get_db_cursor() as cursor:
            cursor.execute(
                """INSERT INTO Rides (user_id, pickup_location, drop_location, distance, fare, eco_mode_enabled, ride_status) 
                   VALUES (?, ?, ?, ?, ?, ?, 'REQUESTED')""",
                (user_id, pickup, drop, distance, fare, eco_mode)
            )
            cursor.execute("SELECT @@IDENTITY")
            ride_id = cursor.fetchone()[0]

        logger.info(f"Ride requested: {ride_id} by user {user_id}")
        return success_response("Ride requested successfully", {
            "ride_id": ride_id,
            "estimated_fare": fare
        })

    except ValueError:
        return error_response("Invalid distance value")
    except Exception as e:
        logger.error(f"Request ride error: {e}")
        return error_response("Failed to request ride", 500)

def accept_ride(user_id, ride_id):
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT driver_id FROM Drivers WHERE user_id = ?",
                (user_id,)
            )
            driver = cursor.fetchone()
            
            if not driver:
                return error_response("User is not a driver", 403)
            
            driver_id = driver[0]
            
            cursor.execute(
                "SELECT ride_status FROM Rides WHERE ride_id = ?",
                (ride_id,)
            )
            ride = cursor.fetchone()

            if not ride:
                return error_response("Ride not found", 404)

            if ride[0] != "REQUESTED":
                return error_response("Ride is no longer available", 400)

            cursor.execute(
                "SELECT availability_status FROM Drivers WHERE driver_id = ?",
                (driver_id,)
            )
            driver_status = cursor.fetchone()
            
            if not driver_status or driver_status[0] != 'AVAILABLE':
                return error_response("You must be AVAILABLE to accept rides", 400)

            cursor.execute(
                "UPDATE Rides SET ride_status = 'ACCEPTED', driver_id = ? WHERE ride_id = ?",
                (driver_id, ride_id)
            )
            cursor.execute(
                "UPDATE Drivers SET availability_status = 'BUSY' WHERE driver_id = ?",
                (driver_id,)
            )

        logger.info(f"Ride {ride_id} accepted by driver {driver_id}")
        return success_response("Ride accepted successfully")

    except Exception as e:
        logger.error(f"Accept ride error: {e}")
        return error_response("Failed to accept ride", 500)

def complete_ride(ride_id):
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT user_id, driver_id, distance, eco_mode_enabled, fare, ride_status FROM Rides WHERE ride_id = ?",
                (ride_id,)
            )
            ride = cursor.fetchone()

            if not ride:
                return error_response("Ride not found", 404)

            user_id, driver_id, distance, eco_mode, fare, status = ride

            if status != 'ACCEPTED':
                return error_response("Only accepted rides can be completed", 400)

            cursor.execute(
                "UPDATE Rides SET ride_status = 'COMPLETED' WHERE ride_id = ?",
                (ride_id,)
            )
            cursor.execute(
                "INSERT INTO Payments (ride_id, amount, payment_status) VALUES (?, ?, 'COMPLETED')",
                (ride_id, fare)
            )

            if driver_id:
                cursor.execute(
                    "UPDATE Drivers SET availability_status = 'AVAILABLE' WHERE driver_id = ?",
                    (driver_id,)
                )

            eco_points = calculate_eco_points(distance, eco_mode, False)
            if eco_points > 0:
                update_eco_score(user_id, eco_points)

        logger.info(f"Ride {ride_id} completed")
        return success_response("Ride completed successfully", {
            "fare": float(fare),
            "eco_points": eco_points
        })

    except Exception as e:
        logger.error(f"Complete ride error: {e}")
        return error_response("Failed to complete ride", 500)

def cancel_ride(user_id, ride_id):
    try:
        # Convert user_id to int for comparison
        user_id = int(user_id)
        
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT user_id, ride_status, driver_id FROM Rides WHERE ride_id = ?",
                (ride_id,)
            )
            ride = cursor.fetchone()

            if not ride:
                return error_response("Ride not found", 404)

            ride_user_id, ride_status, driver_id = ride

            if ride_user_id != user_id:
                return error_response("You can only cancel your own rides", 403)

            if ride_status not in ['REQUESTED', 'ACCEPTED']:
                return error_response("Only pending or accepted rides can be cancelled", 400)

            cursor.execute(
                "UPDATE Rides SET ride_status = 'CANCELLED' WHERE ride_id = ?",
                (ride_id,)
            )
            
            # If ride was accepted, make driver available again
            if ride_status == 'ACCEPTED' and driver_id:
                cursor.execute(
                    "UPDATE Drivers SET availability_status = 'AVAILABLE' WHERE driver_id = ?",
                    (driver_id,)
                )

        logger.info(f"Ride {ride_id} cancelled by user {user_id}")
        return success_response("Ride cancelled successfully")

    except Exception as e:
        logger.error(f"Cancel ride error: {e}")
        return error_response("Failed to cancel ride", 500)
