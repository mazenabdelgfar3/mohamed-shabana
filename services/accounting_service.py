import uuid
from database.connection import get_db


def record_transaction(store_id, record_type, category, amount, payment_method=None,
                       reference_type=None, reference_id=None, description=None, created_by=None):
    if amount == 0:
        raise ValueError("Amount must be non-zero")

    conn = get_db()
    cur = conn.cursor()
    record_number = f"FR-{uuid.uuid4().hex[:8].upper()}"

    cur.execute("""
        INSERT INTO FinancialRecord
            (RecordNumber, StoreId, RecordDate, RecordType, Category,
             Amount, PaymentMethod, ReferenceType, ReferenceId, Description, CreatedBy)
        VALUES (?, ?, datetime('now'), ?, ?, ?, ?, ?, ?, ?, ?)
    """, (record_number, store_id, record_type, category, amount,
          payment_method, reference_type, reference_id, description, created_by))

    record_id = cur.lastrowid
    conn.commit()
    conn.close()
    return record_id


def get_cash_flow(from_date=None, to_date=None):
    conn = get_db()
    cur = conn.cursor()
    query = """
        SELECT RecordType, COALESCE(SUM(Amount), 0) AS Total
        FROM FinancialRecord
        WHERE IsDeleted = 0
    """
    params = []
    if from_date:
        query += " AND RecordDate >= ?"
        params.append(from_date)
    if to_date:
        query += " AND RecordDate <= ?"
        params.append(to_date)
    query += " GROUP BY RecordType"
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    result = {'INCOME': 0, 'EXPENSE': 0, 'TRANSFER': 0}
    for r in rows:
        result[r['RecordType']] = r['Total']
    result['NET'] = result['INCOME'] - result['EXPENSE']
    return result


def get_financial_records(limit=100, record_type=None, from_date=None, to_date=None):
    conn = get_db()
    cur = conn.cursor()
    query = """
        SELECT fr.*, e.FullName AS CreatedByName
        FROM FinancialRecord fr
        LEFT JOIN Employee e ON e.EmployeeId = fr.CreatedBy
        WHERE fr.IsDeleted = 0
    """
    params = []
    if record_type:
        query += " AND fr.RecordType = ?"
        params.append(record_type)
    if from_date:
        query += " AND fr.RecordDate >= ?"
        params.append(from_date)
    if to_date:
        query += " AND fr.RecordDate <= ?"
        params.append(to_date)
    query += " ORDER BY fr.CreatedAt DESC LIMIT ?"
    params.append(limit)
    cur.execute(query, params)
    return [dict(r) for r in cur.fetchall()]
