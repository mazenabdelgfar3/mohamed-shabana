from flask import Blueprint, request
from database.connection import get_db
from services.stock_engine import get_stock, get_movement_history, record_movement
from utils.helpers import json_response, error_response, success_response, parse_int
from utils.decorators import login_required, require_permission, get_json_body

inventory_bp = Blueprint('inventory', __name__, url_prefix='/api/inventory')


@inventory_bp.route('/stock', methods=['GET'])
@login_required
@require_permission('INVENTORY_READ')
def list_stock():
    conn = get_db()
    cur = conn.cursor()
    search = request.args.get('search', '')
    warehouse_id = request.args.get('WarehouseId')
    low_stock = request.args.get('low_stock', '0') == '1'

    query = """
        SELECT i.*, p.Name AS ProductName, p.SKU, p.Barcode,
               p.MinStockLevel, p.MaxStockLevel, p.CostPrice, p.SellingPrice,
               w.Name AS WarehouseName, c.Name AS CategoryName
        FROM Inventory i
        JOIN Product p ON p.ProductId = i.ProductId
        JOIN Warehouse w ON w.WarehouseId = i.WarehouseId
        LEFT JOIN Category c ON c.CategoryId = p.CategoryId
        WHERE p.IsDeleted = 0
    """
    params = []
    if warehouse_id:
        query += " AND i.WarehouseId = ?"
        params.append(parse_int(warehouse_id))
    if search:
        query += " AND (p.Name LIKE ? OR p.SKU LIKE ? OR p.Barcode LIKE ?)"
        params.extend([f'%{search}%'] * 3)
    if low_stock:
        query += " AND i.Quantity <= p.MinStockLevel"
    query += " ORDER BY p.Name ASC"
    cur.execute(query, params)
    stock = [dict(r) for r in cur.fetchall()]
    conn.close()
    return json_response(stock)


@inventory_bp.route('/stock/<int:product_id>', methods=['GET'])
@login_required
def get_product_stock(product_id):
    stock = get_stock(product_id)
    return json_response(stock)


@inventory_bp.route('/movements', methods=['GET'])
@login_required
def list_movements():
    product_id = request.args.get('ProductId')
    warehouse_id = request.args.get('WarehouseId')
    limit = parse_int(request.args.get('limit', 100))
    movements = get_movement_history(
        product_id=parse_int(product_id) if product_id else None,
        warehouse_id=parse_int(warehouse_id) if warehouse_id else None,
        limit=limit
    )
    return json_response(movements)


@inventory_bp.route('/adjust', methods=['POST'])
@login_required
@require_permission('INVENTORY_WRITE')
def adjust_stock():
    from flask import session
    data = get_json_body()
    product_id = parse_int(data.get('ProductId'))
    warehouse_id = parse_int(data.get('WarehouseId', 1))
    quantity = parse_int(data.get('Quantity'))
    reason = data.get('Reason', 'ADJUSTMENT_OUT' if quantity < 0 else 'ADJUSTMENT_IN')
    notes = data.get('Notes', '')
    employee_id = session.get('EmployeeId')

    if not product_id or quantity == 0:
        return error_response('ProductId و Quantity مطلوبان')

    movement_type = 'ADJUSTMENT_IN' if quantity > 0 else 'ADJUSTMENT_OUT'

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT CostPrice FROM Product WHERE ProductId = ?", (product_id,))
    product = cur.fetchone()
    if not product:
        conn.close()
        return error_response('المنتج غير موجود', 404)

    try:
        movement_number = record_movement(
            warehouse_id=warehouse_id,
            product_id=product_id,
            movement_type=movement_type,
            quantity=quantity,
            unit_cost=product['CostPrice'],
            notes=notes,
            created_by=employee_id,
            _conn=conn,
        )
        conn.commit()
        conn.close()
        return success_response('تم تعديل المخزون', {'MovementNumber': movement_number})
    except ValueError as e:
        conn.rollback()
        conn.close()
        return error_response(str(e))


@inventory_bp.route('/warehouses', methods=['GET'])
@login_required
def list_warehouses():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Warehouse WHERE IsDeleted = 0")
    warehouses = [dict(r) for r in cur.fetchall()]
    conn.close()
    return json_response(warehouses)


@inventory_bp.route('/stock/<int:inventory_id>', methods=['DELETE'])
@login_required
@require_permission('INVENTORY_WRITE')
def delete_inventory(inventory_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT InventoryId, ProductId, Quantity FROM Inventory WHERE InventoryId = ?", (inventory_id,))
    inv = cur.fetchone()
    if not inv:
        conn.close()
        return error_response('السجل غير موجود', 404)
    from services.stock_engine import record_movement
    if inv['Quantity'] > 0:
        from flask import session
        cur.execute("SELECT CostPrice FROM Product WHERE ProductId = ?", (inv['ProductId'],))
        p = cur.fetchone()
        record_movement(
            warehouse_id=1, product_id=inv['ProductId'],
            movement_type='ADJUSTMENT_OUT', quantity=-inv['Quantity'],
            unit_cost=p['CostPrice'] if p else 0,
            notes='حذف سجل مخزون', created_by=session.get('EmployeeId'),
            _conn=conn,
        )
    cur.execute("DELETE FROM Inventory WHERE InventoryId = ?", (inventory_id,))
    conn.commit()
    conn.close()
    return success_response('تم حذف سجل المخزون')


@inventory_bp.route('/stock-count', methods=['POST'])
@login_required
def create_stock_count():
    from flask import session
    import uuid
    import json
    data = get_json_body()
    warehouse_id = parse_int(data.get('WarehouseId', 1))
    items = data.get('Items', [])
    notes = data.get('Notes', '')
    employee_id = session.get('EmployeeId')

    if not items:
        return error_response('يجب إضافة عنصر واحد على الأقل')

    conn = get_db()
    cur = conn.cursor()
    count_number = f"SC-{uuid.uuid4().hex[:8].upper()}"

    cur.execute("""
        INSERT INTO StockCount (CountNumber, WarehouseId, CountDate, Status, Items, Notes, CreatedBy)
        VALUES (?, ?, datetime('now'), 'COMPLETED', ?, ?, ?)
    """, (count_number, warehouse_id, json.dumps(items, ensure_ascii=False), notes, employee_id))

    for item in items:
        pid = parse_int(item.get('ProductId'))
        system_qty = parse_int(item.get('SystemQuantity', 0))
        counted_qty = parse_int(item.get('CountedQuantity', 0))
        diff = counted_qty - system_qty

        if diff != 0:
            cur.execute("SELECT CostPrice FROM Product WHERE ProductId = ?", (pid,))
            p = cur.fetchone()
            record_movement(
                warehouse_id=warehouse_id,
                product_id=pid,
                movement_type='ADJUSTMENT_IN' if diff > 0 else 'ADJUSTMENT_OUT',
                quantity=diff,
                unit_cost=p['CostPrice'] if p else 0,
                notes=f"جرد: {notes}",
                created_by=employee_id,
                _conn=conn,
            )

    conn.commit()
    conn.close()
    return success_response('تم إتمام الجرد', {'CountNumber': count_number})
