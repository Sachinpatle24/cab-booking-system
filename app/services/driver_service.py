from app.database.db_connection import get_db_cursor
from app.utils.response_handler import success_response, error_response
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

def update_status(user_id, status):
    try:
        if status not in ['AVAILABLE', 'BUSY', 'OFFLINE']:
            return error_response("Invalid status. Must be AVAILABLE, BUSY, or OFFLINE")

        with get_db_cursor() as cursor:
            cursor.execute("SELECT driver_id FROM Drivers WHERE user_id = ?", (user_id,))
            driver = cursor.fetchone()

            if not driver:
                return error_response("User is not a driver", 403)

            cursor.execute(
                "UPDATE Drivers SET availability_status = ? WHERE user_id = ?",
                (status, user_id)
            )

        logger.info(f"Driver (user {user_id}) status updated to {status}")
        return success_response(f"Status updated to {status}")
    except Exception as e:
        logger.error(f"Update status error: {e}")
        return error_response("Failed to update status", 500)

def get_driver_rides(user_id):
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT driver_id FROM Drivers WHERE user_id = ?", (user_id,))
            driver = cursor.fetchone()

            if not driver:
                return error_response("User is not a driver", 403)

            cursor.execute("""
                SELECT r.ride_id, r.pickup_location, r.drop_location,
                       r.distance, r.fare, r.ride_status, r.created_at, u.name
                FROM Rides r
                JOIN Users u ON r.user_id = u.user_id
                WHERE r.driver_id = ?
                ORDER BY r.created_at DESC
            """, (driver[0],))
            rides = cursor.fetchall()

            ride_list = [
                {
                    "ride_id": r[0],
                    "pickup_location": r[1],
                    "drop_location": r[2],
                    "distance": r[3],
                    "fare": float(r[4]) if r[4] else 0,
                    "ride_status": r[5],
                    "created_at": str(r[6]),
                    "passenger_name": r[7]
                } for r in rides
            ]

        return success_response("Driver rides retrieved", {"rides": ride_list})
    except Exception as e:
        logger.error(f"Get driver rides error: {e}")
        return error_response("Failed to get driver rides", 500)

def get_driver_earnings(user_id):
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT driver_id FROM Drivers WHERE user_id = ?", (user_id,))
            driver = cursor.fetchone()

            if not driver:
                return error_response("User is not a driver", 403)

            cursor.execute("""
                SELECT COUNT(*), ISNULL(SUM(fare), 0)
                FROM Rides
                WHERE driver_id = ? AND ride_status = 'COMPLETED'
            """, (driver[0],))
            result = cursor.fetchone()

        return success_response("Earnings retrieved", {
            "completed_rides": result[0],
            "total_earnings": float(result[1])
        })
    except Exception as e:
        logger.error(f"Get earnings error: {e}")
        return error_response("Failed to get earnings", 500)

def get_available_drivers():
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT d.driver_id, u.name, c.vehicle_number, c.vehicle_type
                FROM Drivers d
                JOIN Users u ON d.user_id = u.user_id
                LEFT JOIN Cabs c ON d.driver_id = c.driver_id
                WHERE d.availability_status = 'AVAILABLE'
            """)
            drivers = cursor.fetchall()

            driver_list = [
                {
                    "driver_id": d[0],
                    "name": d[1],
                    "vehicle_number": d[2],
                    "vehicle_type": d[3]
                } for d in drivers
            ]

        return success_response("Available drivers retrieved", {"drivers": driver_list})
    except Exception as e:
        logger.error(f"Get available drivers error: {e}")
        return error_response("Failed to get drivers", 500)

def get_driver_profile(user_id):
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT d.driver_id, u.name, u.email, d.license_number,
                       d.availability_status, c.vehicle_number, c.vehicle_type, d.rating, d.total_ratings
                FROM Drivers d
                JOIN Users u ON d.user_id = u.user_id
                LEFT JOIN Cabs c ON d.driver_id = c.driver_id
                WHERE d.user_id = ?
            """, (user_id,))
            driver = cursor.fetchone()

            if not driver:
                return error_response("User is not a driver", 403)

            profile = {
                "driver_id": driver[0],
                "name": driver[1],
                "email": driver[2],
                "license_number": driver[3],
                "availability_status": driver[4],
                "vehicle_number": driver[5],
                "vehicle_type": driver[6],
                "rating": float(driver[7]) if driver[7] else 0.0,
                "total_ratings": driver[8] if driver[8] else 0
            }

        return success_response("Profile retrieved", {"profile": profile})
    except Exception as e:
        logger.error(f"Get driver profile error: {e}")
        return error_response("Failed to get profile", 500)
