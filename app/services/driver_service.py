from flask import jsonify
from app.database.db_connection import get_db_connection

def update_driver_status(driver_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE Drivers SET availability_status = ? WHERE driver_id = ?",
        (status, driver_id)
    )
    conn.commit()
    conn.close()
    
    return jsonify({"message": f"Status updated to {status}"}), 200

def get_available_drivers():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT d.driver_id, u.name, c.vehicle_number FROM Drivers d JOIN Users u ON d.user_id = u.user_id LEFT JOIN Cabs c ON d.driver_id = c.driver_id WHERE d.availability_status = 'AVAILABLE'"
    )
    drivers = cursor.fetchall()
    conn.close()
    
    return [{"driver_id": d[0], "name": d[1], "vehicle": d[2]} for d in drivers]
