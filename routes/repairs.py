import json
from flask import Blueprint, request, session
from services.repair_service import create_repair_order, update_repair_status, add_repair_part, get_repair_orders
from services.warranty_service import validate_repair_warranty
from utils.helpers import json_response, error_response, success_response, parse_int
from utils.decorators import login_required, get_json_body, require_permission

repairs_bp = Blueprint('repairs', __name__, url_prefix='/api/repairs')


@repairs_bp.route('/orders', methods=['GET'])
@login_required
@require_permission('REPAIR_READ')
def list_orders():
    status = request.args.get('Status')
    customer_id = request.args.get('CustomerId')
    limit = parse_int(request.args.get('limit', 50))
    orders = get_repair_orders(limit=limit, status=status,
                                customer_id=parse_int(customer_id) if customer_id else None)
    return json_response(orders)


@repairs_bp.route('/orders', methods=['POST'])
@login_required
@require_permission('REPAIR_WRITE')
def create_order():
    data = get_json_body()
    if not data.get('DeviceInfo') or not data.get('ReportedIssue'):
        return error_response('بيانات الجهاز والمشكلة مطلوبة')

    employee_id = session.get('EmployeeId')
    store_id = parse_int(data.get('StoreId', 1))
    customer_id = parse_int(data.get('CustomerId')) or None

    try:
        device_info = data['DeviceInfo']
        if isinstance(device_info, str):
            device_info = json.loads(device_info)
        order = create_repair_order(
            store_id=store_id,
            customer_id=customer_id,
            employee_id=employee_id,
            device_info=device_info,
            reported_issue=data['ReportedIssue'],
            notes=data.get('Notes'),
            customer_name=data.get('CustomerName'),
            customer_phone=data.get('CustomerPhone'),
            technician_name=data.get('TechnicianName'),
            technician_phone=data.get('TechnicianPhone'),
        )
        return success_response('تم تسجيل طلب الصيانة', order, 201)
    except (ValueError, json.JSONDecodeError) as e:
        return error_response(str(e))


@repairs_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@login_required
@require_permission('REPAIR_WRITE')
def change_status(order_id):
    data = get_json_body()
    new_status = data.get('Status')
    if not new_status:
        return error_response('الحالة الجديدة مطلوبة')

    employee_id = session.get('EmployeeId')
    try:
        result = update_repair_status(order_id, new_status, employee_id, data.get('Notes'))
        return success_response('تم تحديث الحالة', result)
    except ValueError as e:
        return error_response(str(e))


@repairs_bp.route('/orders/<int:order_id>/parts', methods=['POST'])
@login_required
@require_permission('REPAIR_WRITE')
def add_part(order_id):
    data = get_json_body()
    product_id = parse_int(data.get('ProductId'))
    quantity = parse_int(data.get('Quantity', 1))
    unit_price = parse_int(data.get('UnitPrice', 0))

    if not product_id or quantity <= 0:
        return error_response('المنتج والكمية مطلوبان')

    result = add_repair_part(order_id, product_id, quantity, unit_price,
                              notes=data.get('Notes'))
    return success_response('تم إضافة القطعة', result)


@repairs_bp.route('/orders/<int:order_id>', methods=['GET'])
@login_required
@require_permission('REPAIR_READ')
def get_order(order_id):
    from database.connection import get_db
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT ro.*, c.FullName AS CustomerName, e.FullName AS EmployeeName,
               w.Status AS WarrantyStatus
        FROM RepairOrder ro
        LEFT JOIN Customer c ON c.CustomerId = ro.CustomerId
        LEFT JOIN Employee e ON e.EmployeeId = ro.EmployeeId
        LEFT JOIN Warranty w ON w.WarrantyId = ro.WarrantyId
        WHERE ro.RepairOrderId = ?
    """, (order_id,))
    order = cur.fetchone()
    if not order:
        conn.close()
        return error_response('طلب الصيانة غير موجود', 404)
    order = dict(order)

    cur.execute("""
        SELECT rp.*, p.Name AS ProductName, p.SKU
        FROM RepairPart rp
        JOIN Product p ON p.ProductId = rp.ProductId
        WHERE rp.RepairOrderId = ?
    """, (order_id,))
    order['Parts'] = [dict(r) for r in cur.fetchall()]
    conn.close()
    return json_response(order)


@repairs_bp.route('/warranty-check', methods=['POST'])
@login_required
@require_permission('REPAIR_WRITE')
def warranty_check():
    data = get_json_body()
    serial_number = data.get('SerialNumber')
    if not serial_number:
        return error_response('الرقم التسلسلي مطلوب')
    result = validate_repair_warranty(serial_number)
    return json_response(result)
