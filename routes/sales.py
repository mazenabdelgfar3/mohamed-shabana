from flask import Blueprint, request, session
from services.sales_service import create_sales_order, get_sales_orders
from utils.helpers import json_response, error_response, success_response, parse_int
from utils.decorators import login_required, require_permission, get_json_body

sales_bp = Blueprint('sales', __name__, url_prefix='/api/sales')


@sales_bp.route('/orders', methods=['GET'])
@login_required
@require_permission('SALES_READ')
def list_orders():
    status = request.args.get('Status')
    customer_id = request.args.get('CustomerId')
    from_date = request.args.get('FromDate')
    to_date = request.args.get('ToDate')
    limit = parse_int(request.args.get('limit', 50))
    orders = get_sales_orders(limit=limit, status=status,
                               customer_id=parse_int(customer_id) if customer_id else None,
                               from_date=from_date, to_date=to_date)
    return json_response(orders)


@sales_bp.route('/orders', methods=['POST'])
@login_required
@require_permission('SALES_CREATE')
def create_order():
    data = get_json_body()
    if not data.get('Items'):
        return error_response('يجب إضافة عنصر واحد على الأقل')

    employee_id = session.get('EmployeeId')
    store_id = parse_int(data.get('StoreId', 1))
    customer_id = parse_int(data.get('CustomerId')) or None

    try:
        order = create_sales_order(
            store_id=store_id,
            customer_id=customer_id,
            employee_id=employee_id,
            items=data['Items'],
            payment_method=data.get('PaymentMethod'),
            paid_amount=parse_int(data.get('PaidAmount', 0)),
            notes=data.get('Notes'),
            customer_name=data.get('CustomerName'),
            customer_phone=data.get('CustomerPhone'),
        )
        return success_response('تم إنشاء الفاتورة', order, 201)
    except ValueError as e:
        return error_response(str(e))


@sales_bp.route('/orders/<int:order_id>', methods=['GET'])
@login_required
def get_order(order_id):
    from database.connection import get_db
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT so.*, c.FullName AS CustomerName, c.Phone AS CustomerPhone, e.FullName AS EmployeeName,
               s.Name AS StoreName
        FROM SalesOrder so
        LEFT JOIN Customer c ON c.CustomerId = so.CustomerId
        LEFT JOIN Employee e ON e.EmployeeId = so.EmployeeId
        LEFT JOIN Store s ON s.StoreId = so.StoreId
        WHERE so.SalesOrderId = ?
    """, (order_id,))
    order = cur.fetchone()
    if not order:
        conn.close()
        return error_response('الفاتورة غير موجودة', 404)
    order = dict(order)

    cur.execute("""
        SELECT soi.*, p.Name AS ProductName, p.SKU,
               sn.SerialNumber
        FROM SalesOrderItem soi
        JOIN Product p ON p.ProductId = soi.ProductId
        LEFT JOIN SerialNumber sn ON sn.SerialNumberId = soi.SerialNumberId
        WHERE soi.SalesOrderId = ?
    """, (order_id,))
    order['Items'] = [dict(r) for r in cur.fetchall()]
    conn.close()
    return json_response(order)


@sales_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@login_required
@require_permission('SALES_WRITE')
def change_order_status(order_id):
    data = get_json_body()
    new_status = data.get('Status')
    if not new_status:
        return error_response('الحالة الجديدة مطلوبة')

    employee_id = session.get('EmployeeId')
    try:
        from services.sales_service import update_sales_order_status
        result = update_sales_order_status(order_id, new_status, employee_id)
        return success_response('تم تحديث حالة الفاتورة بنجاح', result)
    except ValueError as e:
        return error_response(str(e))
