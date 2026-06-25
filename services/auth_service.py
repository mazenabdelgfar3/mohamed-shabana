import hashlib
import secrets
from database.connection import get_db


def hash_password(password):
    salt = secrets.token_hex(16)
    h = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"$sha256${salt}${h}"


def verify_password(password, stored):
    parts = stored.split('$')
    if len(parts) != 4 or parts[1] != 'sha256':
        return False
    _, _, salt, expected = parts
    h = hashlib.sha256((salt + password).encode()).hexdigest()
    return h == expected


def authenticate(email, password):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT EmployeeId, FullName, Email, PasswordHash, IsActive, IsDeleted
        FROM Employee WHERE Email = ?
    """, (email,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    if not row['IsActive'] or row['IsDeleted']:
        return None
    if not verify_password(password, row['PasswordHash']):
        return None
    return {
        'EmployeeId': row['EmployeeId'],
        'FullName': row['FullName'],
        'Email': row['Email'],
    }


def get_employee_permissions(employee_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT r.Permissions
        FROM EmployeeRole er
        JOIN Role r ON r.RoleId = er.RoleId
        WHERE er.EmployeeId = ?
    """, (employee_id,))
    merged = {}
    for row in cur.fetchall():
        if row['Permissions']:
            import json
            merged.update(json.loads(row['Permissions']))
    conn.close()
    return merged
