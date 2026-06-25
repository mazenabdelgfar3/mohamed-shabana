import os
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from flask_session import Session
from config import Config
from database.connection import init_db, close_db, run_migrations, is_postgres
from database.seed import seed_data


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = os.path.join(os.path.dirname(__file__), 'flask_session')
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    Session(app)
    CORS(app, supports_credentials=True)
    app.teardown_appcontext(close_db)

    @app.errorhandler(500)
    def handle_500(e):
        return jsonify({'error': 'خطأ داخلي في الخادم', 'details': str(e)}), 500

    # -----------------------------------------------------------------------
    # Database initialisation
    # -----------------------------------------------------------------------
    with app.app_context():
        init_db()     # IF NOT EXISTS – safe to run every time
        run_migrations()
        try:
            seed_data()  # internal check: only seeds if Store table is empty
        except Exception as exc:
            print(f"[startup] Seed warning: {exc}")

    # -----------------------------------------------------------------------
    # Register blueprints
    # -----------------------------------------------------------------------
    from routes.auth      import auth_bp
    from routes.products  import products_bp
    from routes.customers import customers_bp
    from routes.suppliers import suppliers_bp
    from routes.sales     import sales_bp
    from routes.purchases import purchases_bp
    from routes.inventory import inventory_bp
    from routes.repairs   import repairs_bp
    from routes.employees import employees_bp
    from routes.reports   import reports_bp
    from routes.audit     import audit_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(purchases_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(repairs_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(audit_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api/health')
    def health():
        db_type = 'Supabase (PostgreSQL)' if is_postgres() else 'SQLite (local)'
        return jsonify({'status': 'ok', 'db': db_type,
                        'message': 'CompuManager ERP API is running'})

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)
