from functools import wraps
from flask_jwt_extended import get_jwt, jwt_required
from app.utils.response_handler import error_response

def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if claims.get("role") not in roles:
                return error_response("Access denied", 403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator
