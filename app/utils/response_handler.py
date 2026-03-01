from flask import jsonify

def success_response(message, data=None, status=200):
    response = {"success": True, "message": message}
    if data:
        response["data"] = data
    return jsonify(response), status

def error_response(message, status=400):
    return jsonify({"success": False, "error": message}), status
