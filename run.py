import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import webbrowser
from app import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 55)
    print("  Computer Store ERP - Backend Server")
    print("=" * 55)
    print()
    print(f"  Server:    http://localhost:5000")
    print(f"  API:       http://localhost:5000/api/")
    print()
    print(f"  Login:     admin@store.com / admin123")
    print()
    print("  Press Ctrl+C to stop")
    print("=" * 55)
    webbrowser.open('http://localhost:5000')
    app.run(host='0.0.0.0', port=5000, debug=True)
