from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database.db_connection import get_db_cursor
from app.utils.response_handler import success_response, error_response
from app.utils.logger import setup_logger

payment_bp = Blueprint("payments", __name__)
logger = setup_logger(__name__)

@payment_bp.route("/ride/<int:ride_id>", methods=["GET"])
@jwt_required()
def get_payment_status(ride_id):
    """
    Get payment status for a ride
    ---
    tags:
      - Payments
    security:
      - Bearer: []
    parameters:
      - in: path
        name: ride_id
        type: integer
        required: true
        description: ID of the ride
        example: 101
    responses:
      200:
        description: Payment status retrieved
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            data:
              type: object
              properties:
                payment:
                  type: object
      401:
        description: Unauthorized
      404:
        description: Payment not found
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT p.payment_id, p.ride_id, p.amount, p.payment_status, p.payment_date
                FROM Payments p
                WHERE p.ride_id = ?
            """, (ride_id,))
            payment = cursor.fetchone()
            
            if not payment:
                return error_response("Payment not found", 404)
            
            payment_data = {
                "payment_id": payment[0],
                "ride_id": payment[1],
                "amount": float(payment[2]),
                "payment_status": payment[3],
                "payment_date": str(payment[4])
            }
        
        return success_response("Payment status retrieved", {"payment": payment_data})
    except Exception as e:
        logger.error(f"Get payment status error: {e}")
        return error_response("Failed to get payment status", 500)

@payment_bp.route("/history", methods=["GET"])
@jwt_required()
def get_payment_history():
    """
    Get user's payment history
    ---
    tags:
      - Payments
    security:
      - Bearer: []
    responses:
      200:
        description: Payment history retrieved
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            data:
              type: object
              properties:
                payments:
                  type: array
                  items:
                    type: object
      401:
        description: Unauthorized
    """
    try:
        user_id = get_jwt_identity()
        
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT p.payment_id, p.ride_id, p.amount, p.payment_status, p.payment_date
                FROM Payments p
                JOIN Rides r ON p.ride_id = r.ride_id
                WHERE r.user_id = ?
                ORDER BY p.payment_date DESC
            """, (user_id,))
            payments = cursor.fetchall()
            
            payment_list = [
                {
                    "payment_id": p[0],
                    "ride_id": p[1],
                    "amount": float(p[2]),
                    "payment_status": p[3],
                    "payment_date": str(p[4])
                } for p in payments
            ]
        
        return success_response("Payment history retrieved", {"payments": payment_list})
    except Exception as e:
        logger.error(f"Get payment history error: {e}")
        return error_response("Failed to get payment history", 500)
