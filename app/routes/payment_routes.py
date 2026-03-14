from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.payment_service import get_payment_status, get_payment_history

payment_bp = Blueprint("payments", __name__)

@payment_bp.route("/ride/<int:ride_id>", methods=["GET"])
@jwt_required()
def payment_status(ride_id):
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
    responses:
      200:
        description: Payment status retrieved
      401:
        description: Unauthorized
      404:
        description: Payment not found
    """
    user_id = get_jwt_identity()
    return get_payment_status(user_id, ride_id)

@payment_bp.route("/history", methods=["GET"])
@jwt_required()
def payment_history():
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
      401:
        description: Unauthorized
    """
    user_id = get_jwt_identity()
    return get_payment_history(user_id)
