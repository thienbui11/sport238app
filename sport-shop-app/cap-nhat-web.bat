@echo off
chcp 65001 >nul
cd /d "%~dp0"
rem Mot nut: lay file Excel Sapo moi nhat trong Tai ve (chep, khong xoa file goc), kiem tra, sao luu, nhap, bao cao thay doi, xuat web.
echo Dang cap nhat web tu file Excel Sapo...
set "PY=python"
py --version >nul 2>nul && set "PY=py"
%PY% tools\daily_update.py --mo-bao-cao %*
pause
