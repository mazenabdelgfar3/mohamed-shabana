"""
database/connection.py
======================
Unified database connection layer.
- When DB_PASSWORD is set  → connects to Supabase (PostgreSQL) via psycopg2.
- Otherwise               → falls back to local SQLite (development only).

The PostgreSQL wrapper translates SQLite idioms automatically so every
service/route file continues to work WITHOUT modification:
  ?           → %s          (parameter placeholder)
  datetime('now')           → NOW()
  date('now')               → CURRENT_DATE
  datetime('now','-N days') → NOW() - INTERVAL 'N days'
  strftime(...)             → NOW()
  conn.row_factory          → psycopg2 DictCursor (supports both row['col'] and row[0])
  cur.lastrowid             → captured via RETURNING clause
"""

import os
import re
import time
import sqlite3

from flask import g
from config import Config

# ---------------------------------------------------------------------------
# Try to import psycopg2; fall back gracefully if not installed yet
# ---------------------------------------------------------------------------
try:
    import psycopg2
    import psycopg2.extras
    _PSYCOPG2_AVAILABLE = True
except ImportError:
    _PSYCOPG2_AVAILABLE = False

_USE_POSTGRES = Config.USE_POSTGRES and _PSYCOPG2_AVAILABLE

def is_postgres():
    return _USE_POSTGRES


# ============================================================
# SECTION A: PostgreSQL wrapper (Supabase)
# ============================================================

_DATETIME_NOW_RE       = re.compile(r"datetime\('now'\)", re.IGNORECASE)
_DATE_NOW_RE           = re.compile(r"date\('now'\)", re.IGNORECASE)
_DATETIME_OFFSET_RE    = re.compile(
    r"datetime\('now',\s*'([+-]?\d+)\s+(\w+)'\)", re.IGNORECASE
)
_DATETIME_OFFSET_RE2   = re.compile(
    r"datetime\('now',\s*'([+-])(\d+)\s+(\w+)'\)", re.IGNORECASE
)
_STRFTIME_NOW_RE       = re.compile(r"strftime\('[^']*',\s*'now'\)", re.IGNORECASE)


def _translate_sql(sql: str) -> str:
    """Translate SQLite SQL dialect to PostgreSQL."""
    # strftime('...', 'now') → NOW()
    sql = _STRFTIME_NOW_RE.sub("NOW()", sql)

    # datetime('now', '-N unit') → NOW() - INTERVAL 'N unit'
    def _offset_repl(m):
        val  = m.group(1)   # e.g. '-30' or '+7'
        unit = m.group(2)   # e.g. 'days'
        sign = '-' if val.startswith('-') else '+'
        num  = val.lstrip('+-')
        return f"NOW() {sign} INTERVAL '{num} {unit}'"

    sql = _DATETIME_OFFSET_RE.sub(_offset_repl, sql)

    # datetime('now') → NOW()
    sql = _DATETIME_NOW_RE.sub("NOW()", sql)

    # date('now') → CURRENT_DATE
    sql = _DATE_NOW_RE.sub("CURRENT_DATE", sql)

    # ? → %s  (SQLite uses ?, PostgreSQL uses %s)
    sql = sql.replace('?', '%s')

    return sql


class PGCursorWrapper:
    """
    Wraps a psycopg2 DictCursor to expose a sqlite3-compatible interface.
    Key features:
      - Translates SQL on every execute() call.
      - Captures lastrowid via RETURNING on INSERT statements.
      - Supports row[0] and row['ColName'] access (DictCursor).
    """

    def __init__(self, raw_cursor):
        self._cur       = raw_cursor
        self._lastrowid = None
        self._insert_row = None   # full row returned by RETURNING

    # ------------------------------------------------------------------
    @property
    def lastrowid(self):
        return self._lastrowid

    @property
    def rowcount(self):
        return self._cur.rowcount

    @property
    def description(self):
        return self._cur.description

    # ------------------------------------------------------------------
    def execute(self, sql, params=None):
        sql = _translate_sql(sql)
        stripped = sql.strip().upper()

        if stripped.startswith('INSERT'):
            # Add RETURNING * so we can harvest the PK
            sql_ret = sql.rstrip().rstrip(';') + ' RETURNING *'
            self._cur.execute(sql_ret, params or [])
            row = self._cur.fetchone()
            if row:
                # First column is always the SERIAL PK
                self._lastrowid = row[0]
                self._insert_row = row
            else:
                self._lastrowid = None
                self._insert_row = None
        else:
            self._cur.execute(sql, params or [])
            self._insert_row = None

    def executemany(self, sql, seq_of_params):
        sql = _translate_sql(sql)
        self._cur.executemany(sql, seq_of_params)

    # ------------------------------------------------------------------
    def fetchone(self):
        return self._cur.fetchone()

    def fetchall(self):
        return self._cur.fetchall()

    def fetchmany(self, size=None):
        return self._cur.fetchmany(size) if size else self._cur.fetchmany()

    def __iter__(self):
        return iter(self._cur)

    def close(self):
        self._cur.close()


class PGConnectionWrapper:
    """
    Wraps a psycopg2 connection to expose a sqlite3-compatible interface.
    Tracks whether the underlying connection has been closed so get_db()
    can reopen it transparently (some services call conn.close() explicitly).
    """

    def __init__(self, raw_conn):
        self._conn   = raw_conn
        self._closed = False

    # ------------------------------------------------------------------
    @property
    def closed(self):
        return self._closed or bool(getattr(self._conn, 'closed', False))

    def cursor(self):
        raw = self._conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        return PGCursorWrapper(raw)

    def execute(self, sql, params=None):
        """Allow connection-level execute (sqlite3 compatibility)."""
        cur = self.cursor()
        cur.execute(sql, params)
        return cur

    def commit(self):
        if not self.closed:
            self._conn.commit()

    def rollback(self):
        if not self.closed:
            self._conn.rollback()

    def close(self):
        if not self.closed:
            try:
                self._conn.close()
            except Exception:
                pass
            self._closed = True

    # context-manager support
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.close()


def _open_pg_connection() -> PGConnectionWrapper:
    """Open a fresh connection to Supabase / PostgreSQL."""
    raw = psycopg2.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        dbname=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        sslmode=Config.DB_SSLMODE,
        connect_timeout=15,
    )
    # Autocommit OFF so we control transactions explicitly
    raw.autocommit = False
    return PGConnectionWrapper(raw)


# ============================================================
# SECTION B: SQLite connection (fallback / local dev)
# ============================================================

def _open_sqlite_connection():
    """Open a SQLite connection with WAL mode and row_factory."""
    db_path = Config.DATABASE_PATH
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Remove stale WAL/SHM files
    for ext in ('-wal', '-shm'):
        f = db_path + ext
        if os.path.exists(f):
            try:
                os.remove(f)
            except PermissionError:
                pass

    for attempt in range(3):
        try:
            conn = sqlite3.connect(db_path, timeout=30)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA cache_size = -8000")
            conn.execute("PRAGMA synchronous = NORMAL")
            conn.execute("PRAGMA temp_store = MEMORY")
            conn.execute("PRAGMA busy_timeout = 30000")
            return conn
        except sqlite3.OperationalError:
            if attempt < 2:
                time.sleep(0.5 * (attempt + 1))
                continue
            raise


# ============================================================
# SECTION C: Public API  (used by all routes/services)
# ============================================================

def get_db():
    """
    Return the per-request database connection (stored in Flask's g).
    Automatically reopens the connection if a service closed it explicitly.
    """
    global _USE_POSTGRES
    if 'db' in g:
        db = g.db
        # Check if the connection was closed by service code
        if _USE_POSTGRES:
            if not db.closed:
                return db
        else:
            try:
                db.execute("SELECT 1")
                return db
            except Exception:
                pass
        # Stale – reopen below
        g.pop('db', None)

    if _USE_POSTGRES:
        try:
            conn = _open_pg_connection()
        except Exception as e:
            print(f"[Database] PostgreSQL connection failed: {e}. Falling back to SQLite.")
            _USE_POSTGRES = False
            conn = _open_sqlite_connection()
    else:
        conn = _open_sqlite_connection()

    g.db = conn
    return conn



def close_db(error=None):
    """Flask teardown – close the DB connection at end of every request."""
    db = g.pop('db', None)
    if db is None:
        return
    try:
        if _USE_POSTGRES:
            if not db.closed:
                db.commit()   # commit any unflushed writes
                db.close()
        else:
            db.close()
    except Exception:
        pass


def run_migrations():
    """Apply schema migrations (placeholder for future use)."""
    pass


def init_db():
    """Create all tables (idempotent – uses IF NOT EXISTS)."""
    global _USE_POSTGRES
    if _USE_POSTGRES:
        schema_file = os.path.join(os.path.dirname(__file__), 'schema_postgres.sql')
        try:
            raw = psycopg2.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                dbname=Config.DB_NAME,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                sslmode=Config.DB_SSLMODE,
                connect_timeout=15,
            )
            raw.autocommit = False
            try:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    ddl = f.read()
                with raw.cursor() as cur:
                    cur.execute(ddl)
                raw.commit()
                print("[init_db] Supabase schema initialised successfully.")
            except Exception as e:
                raw.rollback()
                print(f"[init_db] Schema init failed: {e}")
                raise
            finally:
                raw.close()
        except Exception as e:
            print(f"[init_db] PostgreSQL connection failed: {e}. Falling back to SQLite.")
            _USE_POSTGRES = False  # ensure we use SQLite for seed_data etc.
            # Fall back to SQLite initialization
            schema_file = os.path.join(os.path.dirname(__file__), 'schema.sql')
            db = _open_sqlite_connection()
            with open(schema_file, 'r', encoding='utf-8') as f:
                db.executescript(f.read())
            db.commit()
            db.close()
            print("[init_db] SQLite schema initialised as fallback.")
    else:
        # SQLite path
        schema_file = os.path.join(os.path.dirname(__file__), 'schema.sql')
        db = _open_sqlite_connection()
        with open(schema_file, 'r', encoding='utf-8') as f:
            db.executescript(f.read())
        db.commit()
        db.close()
        print("[init_db] ✅ SQLite schema initialised.")




