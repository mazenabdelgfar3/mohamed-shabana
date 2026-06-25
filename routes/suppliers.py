import uuid
from flask import Blueprint, request
from database.connection import get_db
from utils.helpers import json_response, error_response, success_response, parse_int
from utils.decorators import login_required, get_json_body, require_permission

suppliers_bp = Blueprint('suppliers', __name__, url_prefix='/api/suppliers')


@suppliers_bp.route('', methods=['GET'])
@login_required
@require_permission('SUPPLIER_READ')
def list_suppliers():
    conn = get_db()
    cur = conn.cursor()
    search = request.args.get('search', '')
    query = """
        SELECT s.*,
            (SELECT COUNT(*) FROM PurchaseOrder WHERE SupplierId = s.SupplierId) AS OrderCount,
            (SELECT COALESCE(SUM(GrandTotal), 0) FROM PurchaseOrder WHERE SupplierId = s.SupplierId) AS TotalPurchases
        FROM Supplier s WHERE s.IsDeleted = 0
    """
    params = []
    if search:
        query += " AND (s.CompanyName LIKE ? OR s.Phone LIKE ? OR s.SupplierCode LIKE ?)"
        params.extend([f'%{search}%'] * 3)
    query += " ORDER BY s.CompanyName ASC"
    cur.execute(query, params)
    suppliers = [dict(r) for r in cur.fetchall()]
    conn.close()
    return json_response(suppliers)


@suppliers_bp.route('/<int:supplier_id>', methods=['GET'])
@login_required
@require_permission('SUPPLIER_READ')
def get_supplier(supplier_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.*,
            (SELECT COUNT(*) FROM PurchaseOrder WHERE SupplierId = s.SupplierId) AS OrderCount
        FROM Supplier s WHERE s.SupplierId = ?
    """, (supplier_id,))
    supplier = cur.fetchone()
    conn.close()
    if not supplier:
        return error_response('المورد غير موجود', 404)
    return json_response(dict(supplier))


@suppliers_bp.route('', methods=['POST'])
@login_required
@require_permission('SUPPLIER_WRITE')
def create_supplier():
    data = get_json_body()
    if not data.get('CompanyName'):
        return error_response('اسم الشركة مطلوب')

    conn = get_db()
    cur = conn.cursor()
    code = data.get('SupplierCode') or f"SUP-{uuid.uuid4().hex[:8].upper()}"
    uid = str(uuid.uuid4())

    cur.execute("""
        INSERT INTO Supplier
            (SupplierUid, SupplierCode, CompanyName, ContactPerson, Phone, Email, TaxNumber, PaymentTerms, Notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (uid, code, data['CompanyName'], data.get('ContactPerson'),
          data.get('Phone'), data.get('Email'), data.get('TaxNumber'),
          data.get('PaymentTerms'), data.get('Notes')))

    supplier_id = cur.lastrowid
    conn.commit()
    conn.close()
    return success_response('تم إنشاء المورد', {'SupplierId': supplier_id, 'SupplierCode': code}, 201)


@suppliers_bp.route('/<int:supplier_id>', methods=['PUT'])
@login_required
@require_permission('SUPPLIER_WRITE')
def update_supplier(supplier_id):
    data = get_json_body()
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT SupplierId FROM Supplier WHERE SupplierId = ?", (supplier_id,))
    if not cur.fetchone():
        conn.close()
        return error_response('المورد غير موجود', 404)

    updates = []
    params = []
    for f in ['CompanyName', 'ContactPerson', 'Phone', 'Email', 'TaxNumber', 'PaymentTerms', 'Notes']:
        if f in data:
            updates.append(f"{f} = ?")
            params.append(data[f])
    if updates:
        updates.append("UpdatedAt = datetime('now')")
        cur.execute(f"UPDATE Supplier SET {', '.join(updates)} WHERE SupplierId = ?",
                    params + [supplier_id])
        conn.commit()
    conn.close()
    return success_response('تم تحديث المورد')


@suppliers_bp.route('/<int:supplier_id>', methods=['DELETE'])
@login_required
@require_permission('SUPPLIER_DELETE')
def delete_supplier(supplier_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE Supplier SET IsDeleted = 1, UpdatedAt = datetime('now') WHERE SupplierId = ?",
                (supplier_id,))
    conn.commit()
    conn.close()
    return success_response('تم حذف المورد')
