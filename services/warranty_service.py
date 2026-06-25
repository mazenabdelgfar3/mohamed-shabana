import uuid
from database.connection import get_db


def create_warranty(product_id, sales_order_item_id, customer_id, serial_number_id=None,
                    warranty_days=365, warranty_type='STORE'):
    conn = get_db()
    cur = conn.cursor()

    warranty_number = f"WRN-{uuid.uuid4().hex[:8].upper()}"

    cur.execute("""
        INSERT INTO Warranty
            (WarrantyNumber, ProductId, SerialNumberId, SalesOrderItemId, CustomerId,
             StartDate, EndDate, Status, WarrantyType, OriginalDuration)
        VALUES (?, ?, ?, ?, ?,
                datetime('now'), datetime('now', '+' || ? || ' days'),
                'ACTIVE', ?, ?)
    """, (warranty_number, product_id, serial_number_id, sales_order_item_id, customer_id,
          warranty_days, warranty_type, warranty_days))

    warranty_id = cur.lastrowid

    if serial_number_id:
        cur.execute("""
            UPDATE SerialNumber
            SET WarrantyStart = datetime('now'),
                WarrantyEnd = datetime('now', '+' || ? || ' days'),
                WarrantyStatus = 'ACTIVE'
            WHERE SerialNumberId = ?
        """, (warranty_days, serial_number_id))

    conn.commit()
    conn.close()
    return warranty_id


def check_warranty(serial_number=None, product_id=None, customer_id=None):
    conn = get_db()
    cur = conn.cursor()
    query = """
        SELECT w.*, p.Name AS ProductName, c.FullName AS CustomerName,
               sn.SerialNumber AS SerialNumberValue
        FROM Warranty w
        JOIN Product p ON p.ProductId = w.ProductId
        JOIN Customer c ON c.CustomerId = w.CustomerId
        LEFT JOIN SerialNumber sn ON sn.SerialNumberId = w.SerialNumberId
        WHERE w.Status = 'ACTIVE' AND w.EndDate >= datetime('now')
    """
    params = []
    if serial_number:
        query += " AND sn.SerialNumber = ?"
        params.append(serial_number)
    if product_id:
        query += " AND w.ProductId = ?"
        params.append(product_id)
    if customer_id:
        query += " AND w.CustomerId = ?"
        params.append(customer_id)
    cur.execute(query, params)
    return [dict(r) for r in cur.fetchall()]


def validate_repair_warranty(serial_number):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT w.*, p.Name AS ProductName
        FROM Warranty w
        JOIN Product p ON p.ProductId = w.ProductId
        JOIN SerialNumber sn ON sn.SerialNumberId = w.SerialNumberId
        WHERE sn.SerialNumber = ? AND w.Status = 'ACTIVE' AND w.EndDate >= datetime('now')
        ORDER BY w.EndDate DESC LIMIT 1
    """, (serial_number,))
    row = cur.fetchone()
    conn.close()
    if row:
        result = dict(row)
        result['IsValid'] = True
        return result
    return {'IsValid': False, 'Message': 'No active warranty found'}
