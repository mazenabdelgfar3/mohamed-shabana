import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    # SQLite fallback (not used when Supabase is configured)
    if os.getenv('VERCEL'):
        DATABASE_PATH = '/tmp/erp.db'
    else:
        DATABASE_PATH = os.path.join(BASE_DIR, os.getenv('DATABASE_PATH', 'database/erp.db'))
    DEBUG = os.getenv('FLASK_DEBUG', '0') == '1'
    PORT = int(os.getenv('FLASK_PORT', 5000))

    # Supabase / PostgreSQL configuration
    DB_HOST     = os.getenv('DB_HOST', 'db.tkzddmpcuompatgolfgo.supabase.co')
    DB_PORT     = int(os.getenv('DB_PORT', 5432))
    DB_NAME     = os.getenv('DB_NAME', 'postgres')
    DB_USER     = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_SSLMODE  = os.getenv('DB_SSLMODE', 'require')

    # Use PostgreSQL if DB_PASSWORD is set, else fallback to SQLite
    USE_POSTGRES = bool(DB_PASSWORD)
