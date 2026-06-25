import json
from database.connection import get_db


def log_action(table_name, record_id, action, employee_id, old_values=None, new_values=None, _conn=None):
    if _conn:
        conn = _conn
        cur = conn.cursor()
        external_conn = True
    else:
        conn = get_db()
        cur = conn.cursor()
        external_conn = False
    cur.execute("""
        INSERT INTO AuditLog (TableName, RecordId, Action, EmployeeId, OldValues, NewValues)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        table_name,
        record_id,
        action,
        employee_id,
        json.dumps(old_values, ensure_ascii=False, default=str) if old_values else None,
        json.dumps(new_values, ensure_ascii=False, default=str) if new_values else None,
    ))
    if not external_conn:
        conn.commit()
        conn.close()


def get_audit_logs(table_name=None, record_id=None, action=None, limit=100):
    conn = get_db()
    cur = conn.cursor()
    query = """
        SELECT al.*, e.FullName AS EmployeeName
        FROM AuditLog al
        LEFT JOIN Employee e ON e.EmployeeId = al.EmployeeId
        WHERE 1=1
    """
    params = []
    if table_name:
        query += " AND al.TableName = ?"
        params.append(table_name)
    if record_id:
        query += " AND al.RecordId = ?"
        params.append(record_id)
    if action:
        query += " AND al.Action = ?"
        params.append(action)
    query += " ORDER BY al.ChangedAt DESC LIMIT ?"
    params.append(limit)
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]
