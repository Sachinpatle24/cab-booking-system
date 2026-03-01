from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database.db_connection import get_db_cursor
from app.utils.response_handler import success_response, error_response

admin_bp = Blueprint("admin", __name__)

def is_admin(user_id):
    with get_db_cursor() as cursor:
        cursor.execute("SELECT role FROM Users WHERE user_id = ?", (int(user_id),))
        user = cursor.fetchone()
        return user and user[0] == 'ADMIN'

@admin_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_stats():
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return error_response("Admin access required", 403)
    
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM Users WHERE role = 'PASSENGER'")
            total_passengers = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM Users WHERE role = 'DRIVER'")
            total_drivers = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM Rides")
            total_rides = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM Rides WHERE ride_status = 'COMPLETED'")
            completed_rides = cursor.fetchone()[0]
            
            cursor.execute("SELECT ISNULL(SUM(fare), 0) FROM Rides WHERE ride_status = 'COMPLETED'")
            total_revenue = float(cursor.fetchone()[0])
            
            cursor.execute("SELECT COUNT(*) FROM Drivers WHERE availability_status = 'AVAILABLE'")
            active_drivers = cursor.fetchone()[0]
            
        return success_response("Stats retrieved", {
            "total_passengers": total_passengers,
            "total_drivers": total_drivers,
            "total_rides": total_rides,
            "completed_rides": completed_rides,
            "total_revenue": total_revenue,
            "active_drivers": active_drivers
        })
    except Exception as e:
        return error_response("Failed to get stats", 500)

@admin_bp.route("/users", methods=["GET"])
@jwt_required()
def get_all_users():
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return error_response("Admin access required", 403)
    
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT user_id, name, email, role, eco_score, created_at
                FROM Users
                ORDER BY created_at DESC
            """)
            users = cursor.fetchall()
            
            user_list = [{
                "user_id": u[0],
                "name": u[1],
                "email": u[2],
                "role": u[3],
                "eco_score": u[4],
                "created_at": str(u[5])
            } for u in users]
        
        return success_response("Users retrieved", {"users": user_list})
    except Exception as e:
        return error_response("Failed to get users", 500)

@admin_bp.route("/rides", methods=["GET"])
@jwt_required()
def get_all_rides():
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return error_response("Admin access required", 403)
    
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT r.ride_id, u.name as passenger, d_user.name as driver,
                       r.pickup_location, r.drop_location, r.distance, r.fare,
                       r.ride_status, r.created_at
                FROM Rides r
                JOIN Users u ON r.user_id = u.user_id
                LEFT JOIN Drivers d ON r.driver_id = d.driver_id
                LEFT JOIN Users d_user ON d.user_id = d_user.user_id
                ORDER BY r.created_at DESC
            """)
            rides = cursor.fetchall()
            
            ride_list = [{
                "ride_id": r[0],
                "passenger": r[1],
                "driver": r[2] or "Not assigned",
                "pickup": r[3],
                "drop": r[4],
                "distance": r[5],
                "fare": float(r[6]),
                "status": r[7],
                "created_at": str(r[8])
            } for r in rides]
        
        return success_response("Rides retrieved", {"rides": ride_list})
    except Exception as e:
        return error_response("Failed to get rides", 500)
