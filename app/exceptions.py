class AppException(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code

class NotFoundError(AppException):
    def __init__(self, message="Resource not found"):
        super().__init__(message, 404)

class ForbiddenError(AppException):
    def __init__(self, message="Access denied"):
        super().__init__(message, 403)

class ConflictError(AppException):
    def __init__(self, message="Resource already exists"):
        super().__init__(message, 409)
