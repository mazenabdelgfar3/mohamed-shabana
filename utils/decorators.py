import functools
import json
from flask import request, session
from utils.helpers import error_response


def login_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if 'EmployeeId' not in session:
            return error_response('Unauthorized. Please login.', 401)
        return f(*args, **kwargs)
    return decorated


def require_permission(permission):
    def decorator(f):
        @functools.wraps(f)
        def decorated(*args, **kwargs):
            if 'EmployeeId' not in session:
                return error_response('Unauthorized. Please login.', 401)
            perms = session.get('Permissions', {})
            if permission not in perms or not perms.get(permission):
                return error_response('Forbidden: insufficient permissions', 403)
            return f(*args, **kwargs)
        return decorated
    return decorator


def get_json_body():
    try:
        return request.get_json(force=True) or {}
    except Exception:
        return {}
