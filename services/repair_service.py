import uuid
import json
from datetime import datetime
from database.connection import get_db


def create_repair_order(store_id, customer_id, employee_id, device_info, reported_issue, notes=None, customer_name=None, customer_phone=None, technician_name=None, technician_phone=None):
    conn = get_db()
    cur = conn.cursor()

    if not customer_id:
        if customer_phone and customer_phone.strip():
            phone_clean = customer_phone.strip()
            cur.execute("SELECT CustomerId FROM Customer WHERE Phone = ? AND IsDeleted = 0 LIMIT 1", (phone_clean,))
            row = cur.fetchone()
            if row:
                customer_id = row['CustomerId']
            else:
                name_clean = customer_name.strip() if customer_name else "عميل جديد"
                uid = str(uuid.uuid4())
                code = f"CUS-{uuid.uuid4().hex[:8].upper()}"
                cur.execute("""
                    INSERT INTO Customer (CustomerUid, CustomerCode, FullName, Phone)
                    VALUES (?, ?, ?, ?)
                """, (uid, code, name_clean, phone_clean))
                customer_id = cur.lastrowid
        else:
            raise ValueError("العميل مطلوب")

    repair_number = f"RPR-{uuid.uuid4().hex[:8].upper()}"

    cur.execute("""
        SELECT w.WarrantyId, w.Status, w.EndDate
        FROM Warranty w
        JOIN SerialNumber sn ON sn.SerialNumberId = w.SerialNumberId
        WHERE sn.SerialNumber = ? AND w.Status = 'ACTIVE' AND w.EndDate >= datetime('now')
        ORDER BY w.EndDate DESC LIMIT 1
    """, (device_info.get('SerialNumber', ''),))
    warranty = cur.fetchone()

    warranty_id = warranty['WarrantyId'] if warranty else None

    cur.execute("""
        INSERT INTO RepairOrder
            (RepairNumber, StoreId, CustomerId, EmployeeId, WarrantyId,
             DeviceType, DeviceBrand, DeviceModel, SerialNumber,
             ReportedIssue, Status, Diagnosis, StatusHistory, Notes,
             TechnicianName, TechnicianPhone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'RECEIVED', '[]', '[]', ?, ?, ?)
    """, (repair_number, store_id, customer_id, employee_id, warranty_id,
          device_info.get('DeviceType', ''), device_info.get('DeviceBrand', ''),
          device_info.get('DeviceModel', ''), device_info.get('SerialNumber', ''),
          reported_issue, notes, technician_name, technician_phone))

    repair_order_id = cur.lastrowid

    now_str = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    history = json.dumps([{
        'FromStatus': None,
        'ToStatus': 'RECEIVED',
        'ChangedBy': employee_id,
        'ChangedAt': now_str,
        'Notes': 'تم استلام الجهاز'
    }])
    cur.execute("UPDATE RepairOrder SET StatusHistory = ? WHERE RepairOrderId = ?",
                (history, repair_order_id))

    cur.execute("SELECT * FROM RepairOrder WHERE RepairOrderId = ?", (repair_order_id,))
    order = dict(cur.fetchone())
    order['UnderWarranty'] = warranty is not None

    conn.commit()
    conn.close()
    return order


def update_repair_status(repair_order_id, new_status, employee_id, notes=None):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT Status, StatusHistory FROM RepairOrder WHERE RepairOrderId = ?",
                (repair_order_id,))
    order = cur.fetchone()
    if not order:
        conn.close()
        raise ValueError("Repair order not found")

    old_status = order['Status']
    history = json.loads(order['StatusHistory']) if order['StatusHistory'] else []

    now_str = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    history.append({
        'FromStatus': old_status,
        'ToStatus': new_status,
        'ChangedBy': employee_id,
        'ChangedAt': now_str,
        'Notes': notes or '',
    })

    update_fields = "Status = ?, StatusHistory = ?, UpdatedAt = datetime('now')"
    if new_status == 'COMPLETED':
        update_fields += ", CompletedDate = datetime('now')"

    cur.execute(f"""
        UPDATE RepairOrder SET {update_fields} WHERE RepairOrderId = ?
    """, (new_status, json.dumps(history), repair_order_id))

    if new_status == 'COMPLETED' and notes:
        pass

    conn.commit()
    conn.close()
    return {"message": f"Status updated to {new_status}"}


def add_repair_part(repair_order_id, product_id, quantity, unit_price, notes=None, serial_number_id=None):
    from services.stock_engine import record_movement
    from flask import session

    conn = get_db()
    cur = conn.cursor()

    # Get product details for stock deduction
    cur.execute("SELECT CostPrice, Name FROM Product WHERE ProductId = ?", (product_id,))
    prod = cur.fetchone()
    if not prod:
        conn.close()
        raise ValueError("المنتج غير موجود")

    # Record stock movement (deduct from inventory)
    try:
        record_movement(
            warehouse_id=1,
            product_id=product_id,
            movement_type='ADJUSTMENT_OUT',
            quantity=-quantity,
            unit_cost=prod['CostPrice'],
            notes=notes or f"استخدام في الصيانة لطلب #{repair_order_id}",
            created_by=session.get('EmployeeId') if session else None,
            _conn=conn,
            product_name=prod['Name']
        )
    except ValueError as e:
        conn.close()
        raise ValueError(str(e))

    line_total = quantity * unit_price
    cur.execute("""
        INSERT INTO RepairPart
            (RepairOrderId, ProductId, SerialNumberId, Quantity, UnitPrice, LineTotal, Notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (repair_order_id, product_id, serial_number_id, quantity, unit_price, line_total, notes))

    cur.execute("""
        UPDATE RepairOrder SET PartsCost = (
            SELECT COALESCE(SUM(LineTotal), 0) FROM RepairPart WHERE RepairOrderId = ?
        ), GrandTotal = DiagnosisFee + LaborFee + (
            SELECT COALESCE(SUM(LineTotal), 0) FROM RepairPart WHERE RepairOrderId = ?
        ) WHERE RepairOrderId = ?
    """, (repair_order_id, repair_order_id, repair_order_id))

    conn.commit()
    conn.close()
    return {"message": "Part added to repair"}


def get_repair_orders(limit=50, status=None, customer_id=None):
    conn = get_db()
    cur = conn.cursor()
    query = """
        SELECT ro.*, c.FullName AS CustomerName, e.FullName AS EmployeeName,
               w.Status AS WarrantyStatus
        FROM RepairOrder ro
        LEFT JOIN Customer c ON c.CustomerId = ro.CustomerId
        LEFT JOIN Employee e ON e.EmployeeId = ro.EmployeeId
        LEFT JOIN Warranty w ON w.WarrantyId = ro.WarrantyId
        WHERE 1=1
    """
    params = []
    if status:
        query += " AND ro.Status = ?"
        params.append(status)
    if customer_id:
        query += " AND ro.CustomerId = ?"
        params.append(customer_id)
    query += " ORDER BY ro.CreatedAt DESC LIMIT ?"
    params.append(limit)
    cur.execute(query, params)
    return [dict(r) for r in cur.fetchall()]
