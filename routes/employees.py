import uuid
from flask import Blueprint, request
from database.connection import get_db
from services.auth_service import hash_password
from utils.helpers import json_response, error_response, success_response, parse_int
from utils.decorators import login_required, get_json_body, require_permission

employees_bp = Blueprint('employees', __name__, url_prefix='/api/employees')


@employees_bp.route('', methods=['GET'])
@login_required
@require_permission('EMPLOYEE_READ')
def list_employees():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT e.*, s.Name AS StoreName,
               GROUP_CONCAT(r.RoleName) AS RoleNames
        FROM Employee e
        LEFT JOIN Store s ON s.StoreId = e.StoreId
        LEFT JOIN EmployeeRole er ON er.EmployeeId = e.EmployeeId
        LEFT JOIN Role r ON r.RoleId = er.RoleId
        WHERE e.IsDeleted = 0
        GROUP BY e.EmployeeId
        ORDER BY e.FullName ASC
    """)
    employees = [dict(r) for r in cur.fetchall()]
    conn.close()
    return json_response(employees)


@employees_bp.route('', methods=['POST'])
@login_required
@require_permission('EMPLOYEE_WRITE')
def create_employee():
    data = get_json_body()
    if not data.get('FullName') or not data.get('Email') or not data.get('Password'):
        return error_response('الاسم والبريد الإلكتروني وكلمة المرور مطلوبة')

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT EmployeeId FROM Employee WHERE Email = ?", (data['Email'],))
    if cur.fetchone():
        conn.close()
        return error_response('البريد الإلكتروني موجود بالفعل')

    uid = str(uuid.uuid4())
    code = data.get('EmployeeCode') or f"EMP-{uuid.uuid4().hex[:8].upper()}"
    pwd_hash = hash_password(data['Password'])

    cur.execute("""
        INSERT INTO Employee
            (EmployeeUid, StoreId, EmployeeCode, FullName, Phone, Email, PasswordHash)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (uid, parse_int(data.get('StoreId', 1)), code, data['FullName'],
          data.get('Phone'), data['Email'], pwd_hash))
    employee_id = cur.lastrowid

    role_id = parse_int(data.get('RoleId'))
    if role_id:
        cur.execute("INSERT INTO EmployeeRole (EmployeeId, RoleId) VALUES (?, ?)",
                    (employee_id, role_id))

    conn.commit()
    conn.close()
    return success_response('تم إنشاء الموظف', {'EmployeeId': employee_id}, 201)


@employees_bp.route('/roles', methods=['GET'])
@login_required
@require_permission('EMPLOYEE_READ')
def list_roles():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Role WHERE IsActive = 1")
    roles = [dict(r) for r in cur.fetchall()]
    conn.close()
    return json_response(roles)
