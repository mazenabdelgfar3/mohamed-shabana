import uuid
import json
from database.connection import get_db
from services.audit_service import log_action


def check_stock_for_sale(warehouse_id, items):
    """Validate that all items have sufficient stock before creating a sale.
    Returns None if ok, or raises ValueError with product name if stock insufficient.
    Uses get_db() which reuses the g.db connection; caller must NOT close it."""
    conn = get_db()
    cur = conn.cursor()
    for item in items:
        product_id = item['ProductId']
        qty_needed = item['Quantity']
        cur.execute("""
            SELECT i.Quantity, p.Name FROM Inventory i
            JOIN Product p ON p.ProductId = i.ProductId
            WHERE i.WarehouseId = ? AND i.ProductId = ?
        """, (warehouse_id, product_id))
        row = cur.fetchone()
        available = row['Quantity'] if row else 0
        product_name = row['Name'] if row else 'غير معروف'
        if available < qty_needed:
            raise ValueError(
                f"عذراً، المنتج {product_name} غير متوفر بالكمية المطلوبة "
                f"(المتوفر: {available}، المطلوب: {qty_needed})"
            )


def record_movement(warehouse_id, product_id, movement_type, quantity, unit_cost,
                    reference_type=None, reference_id=None, reference_line_id=None,
                    notes=None, created_by=None, serial_number_id=None,
                    _conn=None, product_name=None):
    if quantity == 0:
        raise ValueError("Quantity must be non-zero")

    if _conn:
        conn = _conn
        cur = conn.cursor()
        external_conn = True
    else:
        conn = get_db()
        cur = conn.cursor()
        external_conn = False
    movement_number = f"SM-{uuid.uuid4().hex[:8].upper()}"

    cur.execute("""
        INSERT INTO StockMovement
            (MovementNumber, WarehouseId, ProductId, SerialNumberId,
             MovementType, Quantity, UnitCost,
             ReferenceType, ReferenceId, ReferenceLineId,
             Notes, CreatedBy)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (movement_number, warehouse_id, product_id, serial_number_id,
          movement_type, quantity, unit_cost,
          reference_type, reference_id, reference_line_id,
          notes, created_by))

    cur.execute("""
        SELECT Quantity FROM Inventory
        WHERE WarehouseId = ? AND ProductId = ?
    """, (warehouse_id, product_id))
    row = cur.fetchone()

    pname = product_name or 'المنتج'

    if row:
        new_qty = row['Quantity'] + quantity
        if new_qty < 0:
            if not external_conn:
                conn.rollback()
                conn.close()
            raise ValueError(
                f"عذراً، المنتج {pname} غير متوفر بالكمية المطلوبة "
                f"(المتوفر: {row['Quantity']}، المطلوب: {-quantity})"
            )
        cur.execute("""
            UPDATE Inventory
            SET Quantity = ?, AvailableQuantity = ? - ReservedQuantity,
                UpdatedAt = datetime('now')
            WHERE WarehouseId = ? AND ProductId = ?
        """, (new_qty, new_qty, warehouse_id, product_id))
    else:
        if quantity < 0:
            if not external_conn:
                conn.rollback()
                conn.close()
            raise ValueError(
                f"عذراً، المنتج {pname} غير متوفر بالكمية المطلوبة "
                f"(المتوفر: 0، المطلوب: {-quantity})"
            )
        cur.execute("""
            INSERT INTO Inventory (WarehouseId, ProductId, Quantity, AvailableQuantity, ReservedQuantity, UpdatedAt)
            VALUES (?, ?, ?, ?, 0, datetime('now'))
        """, (warehouse_id, product_id, quantity, quantity))

    log_action('Inventory', product_id, 'UPDATE', created_by, new_values={
        'MovementNumber': movement_number, 'MovementType': movement_type,
        'Quantity': quantity, 'WarehouseId': warehouse_id
    }, _conn=conn)
    if not external_conn:
        conn.commit()
        conn.close()
    return movement_number


def get_stock(product_id, warehouse_id=None):
    conn = get_db()
    cur = conn.cursor()
    if warehouse_id:
        cur.execute("""
            SELECT i.Quantity, i.AvailableQuantity, i.ReservedQuantity,
                   w.Name AS WarehouseName, p.Name AS ProductName
            FROM Inventory i
            JOIN Warehouse w ON w.WarehouseId = i.WarehouseId
            JOIN Product p ON p.ProductId = i.ProductId
            WHERE i.ProductId = ? AND i.WarehouseId = ?
        """, (product_id, warehouse_id))
    else:
        cur.execute("""
            SELECT i.Quantity, i.AvailableQuantity, i.ReservedQuantity,
                   w.Name AS WarehouseName, w.WarehouseId
            FROM Inventory i
            JOIN Warehouse w ON w.WarehouseId = i.WarehouseId
            WHERE i.ProductId = ?
        """, (product_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_movement_history(product_id=None, warehouse_id=None, limit=100):
    conn = get_db()
    cur = conn.cursor()
    query = """
        SELECT sm.*, p.Name AS ProductName, p.SKU,
               w.Name AS WarehouseName,
               e.FullName AS CreatedByName
        FROM StockMovement sm
        JOIN Product p ON p.ProductId = sm.ProductId
        JOIN Warehouse w ON w.WarehouseId = sm.WarehouseId
        LEFT JOIN Employee e ON e.EmployeeId = sm.CreatedBy
        WHERE 1=1
    """
    params = []
    if product_id:
        query += " AND sm.ProductId = ?"
        params.append(product_id)
    if warehouse_id:
        query += " AND sm.WarehouseId = ?"
        params.append(warehouse_id)
    query += " ORDER BY sm.CreatedAt DESC LIMIT ?"
    params.append(limit)
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]
