import uuid
from flask import Blueprint, request
from database.connection import get_db
from utils.helpers import json_response, error_response, success_response, parse_int
from utils.decorators import login_required, get_json_body, require_permission

customers_bp = Blueprint('customers', __name__, url_prefix='/api/customers')


@customers_bp.route('', methods=['GET'])
@login_required
@require_permission('CUSTOMER_READ')
def list_customers():
    conn = get_db()
    cur = conn.cursor()
    search = request.args.get('search', '')
    query = """
        SELECT c.*,
            (SELECT COUNT(*) FROM SalesOrder WHERE CustomerId = c.CustomerId AND IsDeleted = 0) AS OrderCount,
            (SELECT COALESCE(SUM(GrandTotal), 0) FROM SalesOrder WHERE CustomerId = c.CustomerId AND IsDeleted = 0) AS TotalPurchases
        FROM Customer c
        WHERE c.IsDeleted = 0
    """
    params = []
    if search:
        query += " AND (c.FullName LIKE ? OR c.Phone LIKE ? OR c.CustomerCode LIKE ?)"
        params.extend([f'%{search}%'] * 3)
    query += " ORDER BY c.FullName ASC"
    cur.execute(query, params)
    customers = [dict(r) for r in cur.fetchall()]
    conn.close()
    return json_response(customers)


@customers_bp.route('/<int:customer_id>', methods=['GET'])
@login_required
@require_permission('CUSTOMER_READ')
def get_customer(customer_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.*,
            (SELECT COUNT(*) FROM SalesOrder WHERE CustomerId = c.CustomerId AND IsDeleted = 0) AS OrderCount,
            (SELECT COUNT(*) FROM RepairOrder WHERE CustomerId = c.CustomerId) AS RepairCount
        FROM Customer c WHERE c.CustomerId = ?
    """, (customer_id,))
    customer = cur.fetchone()
    conn.close()
    if not customer:
        return error_response('العميل غير موجود', 404)
    return json_response(dict(customer))


@customers_bp.route('', methods=['POST'])
@login_required
@require_permission('CUSTOMER_WRITE')
def create_customer():
    data = get_json_body()
    if not data.get('FullName'):
        return error_response('اسم العميل مطلوب')

    conn = get_db()
    cur = conn.cursor()
    phone = data.get('Phone')
    if phone:
        cur.execute("SELECT CustomerId FROM Customer WHERE Phone = ? AND IsDeleted = 0 LIMIT 1", (phone.strip(),))
        if cur.fetchone():
            conn.close()
            return error_response('رقم الهاتف مسجل بالفعل لعميل آخر')

    code = data.get('CustomerCode') or f"CUS-{uuid.uuid4().hex[:8].upper()}"
    uid = str(uuid.uuid4())

    cur.execute("""
        INSERT INTO Customer
            (CustomerUid, CustomerCode, FullName, Phone, Email, Notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (uid, code, data['FullName'], phone,
          data.get('Email'), data.get('Notes')))

    customer_id = cur.lastrowid
    conn.commit()
    conn.close()
    return success_response('تم إنشاء العميل', {'CustomerId': customer_id, 'CustomerCode': code}, 201)


@customers_bp.route('/<int:customer_id>', methods=['PUT'])
@login_required
@require_permission('CUSTOMER_WRITE')
def update_customer(customer_id):
    data = get_json_body()
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT CustomerId FROM Customer WHERE CustomerId = ?", (customer_id,))
    if not cur.fetchone():
        conn.close()
        return error_response('العميل غير موجود', 404)

    phone = data.get('Phone')
    if phone:
        cur.execute("SELECT CustomerId FROM Customer WHERE Phone = ? AND CustomerId != ? AND IsDeleted = 0 LIMIT 1", (phone.strip(), customer_id))
        if cur.fetchone():
            conn.close()
            return error_response('رقم الهاتف مسجل بالفعل لعميل آخر')

    updates = []
    params = []
    for f in ['FullName', 'Phone', 'Email', 'Notes']:
        if f in data:
            updates.append(f"{f} = ?")
            params.append(data[f])
    if updates:
        updates.append("UpdatedAt = datetime('now')")
        cur.execute(f"UPDATE Customer SET {', '.join(updates)} WHERE CustomerId = ?",
                    params + [customer_id])
        conn.commit()
    conn.close()
    return success_response('تم تحديث العميل')


@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
@login_required
@require_permission('CUSTOMER_DELETE')
def delete_customer(customer_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE Customer SET IsDeleted = 1, UpdatedAt = datetime('now') WHERE CustomerId = ?",
                (customer_id,))
    conn.commit()
    conn.close()
    return success_response('تم حذف العميل')



