import re

def validate_email(email):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None

def validate_password(password):
    return len(password) >= 8

def validate_role(role):
    return role in ['ADMIN', 'DRIVER', 'PASSENGER']
