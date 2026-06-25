from flask import Blueprint, request, session
from services.purchase_service import create_purchase_order, receive_purchase_order, get_purchase_orders
from utils.helpers import json_response, error_response, success_response, parse_int
from utils.decorators import login_required, get_json_body, require_permission

purchases_bp = Blueprint('purchases', __name__, url_prefix='/api/purchases')


@purchases_bp.route('/orders', methods=['GET'])
@login_required
@require_permission('PURCHASE_READ')
def list_orders():
    status = request.args.get('Status')
    supplier_id = request.args.get('SupplierId')
    limit = parse_int(request.args.get('limit', 50))
    orders = get_purchase_orders(limit=limit, status=status,
                                  supplier_id=parse_int(supplier_id) if supplier_id else None)
    return json_response(orders)


@purchases_bp.route('/orders', methods=['POST'])
@login_required
@require_permission('PURCHASE_CREATE')
def create_order():
    data = get_json_body()
    if not data.get('Items'):
        return error_response('يجب إضافة عنصر واحد على الأقل')

    employee_id = session.get('EmployeeId')
    store_id = parse_int(data.get('StoreId', 1))
    supplier_id = parse_int(data.get('SupplierId'))

    if not supplier_id:
        return error_response('المورد مطلوب')

    try:
        order = create_purchase_order(
            store_id=store_id,
            supplier_id=supplier_id,
            employee_id=employee_id,
            items=data['Items'],
            notes=data.get('Notes'),
        )
        return success_response('تم إنشاء أمر الشراء', order, 201)
    except ValueError as e:
        return error_response(str(e))


@purchases_bp.route('/orders/<int:order_id>/receive', methods=['POST'])
@login_required
@require_permission('PURCHASE_CREATE')
def receive_order(order_id):
    employee_id = session.get('EmployeeId')
    warehouse_id = parse_int(request.json.get('WarehouseId', 1)) if request.json else 1
    try:
        result = receive_purchase_order(order_id, employee_id, warehouse_id)
        return success_response('تم استلام الطلب', result)
    except ValueError as e:
        return error_response(str(e))


@purchases_bp.route('/orders/<int:order_id>', methods=['GET'])
@login_required
@require_permission('PURCHASE_READ')
def get_order(order_id):
    from database.connection import get_db
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT po.*, s.CompanyName AS SupplierName, e.FullName AS EmployeeName
        FROM PurchaseOrder po
        LEFT JOIN Supplier s ON s.SupplierId = po.SupplierId
        LEFT JOIN Employee e ON e.EmployeeId = po.EmployeeId
        WHERE po.PurchaseOrderId = ?
    """, (order_id,))
    order = cur.fetchone()
    if not order:
        conn.close()
        return error_response('أمر الشراء غير موجود', 404)
    order = dict(order)

    cur.execute("""
        SELECT poi.*, p.Name AS ProductName, p.SKU
        FROM PurchaseOrderItem poi
        JOIN Product p ON p.ProductId = poi.ProductId
        WHERE poi.PurchaseOrderId = ?
    """, (order_id,))
    order['Items'] = [dict(r) for r in cur.fetchall()]
    conn.close()
    return json_response(order)
