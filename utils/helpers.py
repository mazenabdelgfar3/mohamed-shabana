import json
from flask import make_response


def json_response(data, status=200):
    resp = make_response(json.dumps(data, ensure_ascii=False, default=str), status)
    resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    return resp


def error_response(message, status=400):
    return json_response({'error': message}, status)


def parse_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def parse_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def success_response(message, data=None, status=200):
    resp = {'message': message}
    if data:
        resp['data'] = data
    return json_response(resp, status)
