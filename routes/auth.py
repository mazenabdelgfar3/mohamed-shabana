from flask import Blueprint, request, session
from services.auth_service import authenticate, get_employee_permissions
from utils.helpers import json_response, error_response
from utils.decorators import login_required, get_json_body

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/login', methods=['POST'])
def login():
    data = get_json_body()
    email = data.get('Email', '').strip()
    password = data.get('Password', '')

    if not email or not password:
        return error_response('البريد الإلكتروني وكلمة المرور مطلوبان')

    employee = authenticate(email, password)
    if not employee:
        return error_response('بيانات الدخول غير صحيحة', 401)

    permissions = get_employee_permissions(employee['EmployeeId'])
    session['EmployeeId'] = employee['EmployeeId']
    session['FullName'] = employee['FullName']
    session['Email'] = employee['Email']
    session['Permissions'] = permissions

    return json_response({
        'message': 'تم تسجيل الدخول بنجاح',
        'employee': employee,
        'permissions': permissions,
    })


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return json_response({'message': 'تم تسجيل الخروج'})


@auth_bp.route('/me', methods=['GET'])
@login_required
def me():
    return json_response({
        'EmployeeId': session.get('EmployeeId'),
        'FullName': session.get('FullName'),
        'Email': session.get('Email'),
        'Permissions': session.get('Permissions', {}),
    })
