@echo off
cd /d "%~dp0"
echo Dang cap nhat web tu file Excel Sapo...
python tools\daily_update.py
pause
