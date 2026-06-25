@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo   نظام إدارة متجر الكمبيوتر - ERP
echo   Computer Store ERP System
echo ============================================
echo.
echo جاري تثبيت الاعتماديات...
pip install -r requirements.txt
echo.
echo جاري تشغيل الخادم...
echo افتح المتصفح على: http://localhost:5000
echo.
echo بيانات الدخول:
echo   البريد: admin@store.com
echo   كلمة المرور: admin123
echo.
python run.py
pause
