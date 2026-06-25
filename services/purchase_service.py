import uuid
from database.connection import get_db
from services.stock_engine import record_movement


def create_purchase_order(store_id, supplier_id, employee_id, items, notes=None):
    if not items:
        raise ValueError("Purchase order must have at least one item")

    conn = get_db()
    cur = conn.cursor()

    order_number = f"PO-{uuid.uuid4().hex[:8].upper()}"

    sub_total = 0
    total_tax = 0

    line_items = []
    for item in items:
        cur.execute("""
            SELECT p.ProductId, p.TaxId, t.Rate AS TaxRate
            FROM Product p
            LEFT JOIN Tax t ON t.TaxId = p.TaxId
            WHERE p.ProductId = ?
        """, (item['ProductId'],))
        product = cur.fetchone()
        if not product:
            conn.close()
            raise ValueError(f"Product {item['ProductId']} not found")

        qty = item['Quantity']
        unit_cost = item['UnitCost']
        tax_rate = product['TaxRate'] or 0

        tax_amt = int(unit_cost * qty * tax_rate / 100)
        line_total = unit_cost * qty + tax_amt

        sub_total += unit_cost * qty
        total_tax += tax_amt

        line_items.append({
            'ProductId': product['ProductId'],
            'Quantity': qty,
            'UnitCost': unit_cost,
            'TaxPercent': tax_rate,
            'TaxAmount': tax_amt,
            'LineTotal': line_total,
        })

    grand_total = sub_total + total_tax

    cur.execute("""
        INSERT INTO PurchaseOrder
            (OrderNumber, StoreId, SupplierId, EmployeeId,
             OrderDate, SubTotal, TaxAmount, GrandTotal,
             Status, Notes, CreatedBy, UpdatedBy)
        VALUES (?, ?, ?, ?, datetime('now'),
                ?, ?, ?, 'DRAFT', ?, ?, ?)
    """, (order_number, store_id, supplier_id, employee_id,
          sub_total, total_tax, grand_total,
          notes, employee_id, employee_id))

    purchase_order_id = cur.lastrowid

    for li in line_items:
        cur.execute("""
            INSERT INTO PurchaseOrderItem
                (PurchaseOrderId, ProductId, Quantity, UnitCost,
                 TaxPercent, TaxAmount, LineTotal)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (purchase_order_id, li['ProductId'], li['Quantity'], li['UnitCost'],
              li['TaxPercent'], li['TaxAmount'], li['LineTotal']))

    cur.execute("SELECT * FROM PurchaseOrder WHERE PurchaseOrderId = ?", (purchase_order_id,))
    order = dict(cur.fetchone())
    cur.execute("SELECT * FROM PurchaseOrderItem WHERE PurchaseOrderId = ?", (purchase_order_id,))
    order['Items'] = [dict(r) for r in cur.fetchall()]

    conn.commit()
    conn.close()
    return order


def receive_purchase_order(purchase_order_id, employee_id, warehouse_id=1):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT Status FROM PurchaseOrder WHERE PurchaseOrderId = ?
    """, (purchase_order_id,))
    po = cur.fetchone()
    if not po:
        conn.close()
        raise ValueError("Purchase order not found")
    if po['Status'] in ('RECEIVED', 'CANCELLED'):
        conn.close()
        raise ValueError(f"Order is already {po['Status']}")

    cur.execute("SELECT * FROM PurchaseOrderItem WHERE PurchaseOrderId = ?",
                (purchase_order_id,))
    items = cur.fetchall()

    for item in items:
        remaining = item['Quantity'] - item['ReceivedQuantity']
        if remaining > 0:
            record_movement(
                warehouse_id=warehouse_id,
                product_id=item['ProductId'],
                movement_type='PURCHASE_IN',
                quantity=remaining,
                unit_cost=item['UnitCost'],
                reference_type='PurchaseOrder',
                reference_id=purchase_order_id,
                reference_line_id=item['PurchaseOrderItemId'],
                created_by=employee_id,
                notes=f"Receipt for PO #{purchase_order_id}",
                _conn=conn,
            )
            cur.execute("""
                UPDATE PurchaseOrderItem
                SET ReceivedQuantity = Quantity
                WHERE PurchaseOrderItemId = ?
            """, (item['PurchaseOrderItemId'],))

    cur.execute("""
        UPDATE PurchaseOrder SET Status = 'RECEIVED', UpdatedAt = datetime('now')
        WHERE PurchaseOrderId = ?
    """, (purchase_order_id,))

    record_number = f"FR-{uuid.uuid4().hex[:8].upper()}"
    cur.execute("""
        INSERT INTO FinancialRecord
            (RecordNumber, StoreId, RecordDate, RecordType, Category,
             Amount, ReferenceType, ReferenceId, Description, CreatedBy)
        VALUES (?, 1, datetime('now'), 'EXPENSE', 'مشتريات',
                (SELECT GrandTotal FROM PurchaseOrder WHERE PurchaseOrderId = ?),
                'PurchaseOrder', ?, ?, ?)
    """, (record_number, purchase_order_id, purchase_order_id,
          f"استلام مشتريات #PO-{purchase_order_id}", employee_id))

    conn.commit()
    conn.close()
    return {"message": "Purchase order received successfully"}


def get_purchase_orders(limit=50, status=None, supplier_id=None):
    conn = get_db()
    cur = conn.cursor()
    query = """
        SELECT po.*, s.CompanyName AS SupplierName, e.FullName AS EmployeeName
        FROM PurchaseOrder po
        LEFT JOIN Supplier s ON s.SupplierId = po.SupplierId
        LEFT JOIN Employee e ON e.EmployeeId = po.EmployeeId
        WHERE 1=1
    """
    params = []
    if status:
        query += " AND po.Status = ?"
        params.append(status)
    if supplier_id:
        query += " AND po.SupplierId = ?"
        params.append(supplier_id)
    query += " ORDER BY po.CreatedAt DESC LIMIT ?"
    params.append(limit)
    cur.execute(query, params)
    return [dict(r) for r in cur.fetchall()]
