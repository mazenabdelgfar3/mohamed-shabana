import re


def validate_email(email):
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_required(data, fields):
    missing = []
    for field in fields:
        if field not in data or data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
            missing.append(field)
    return missing


def validate_positive_int(value, name='Value'):
    try:
        v = int(value)
        if v <= 0:
            return f"{name} must be greater than 0"
    except (TypeError, ValueError):
        return f"{name} must be a valid integer"
    return None


def validate_non_negative_int(value, name='Value'):
    try:
        v = int(value)
        if v < 0:
            return f"{name} must be 0 or greater"
    except (TypeError, ValueError):
        return f"{name} must be a valid integer"
    return None
