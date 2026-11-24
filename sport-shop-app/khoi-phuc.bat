@echo off
chcp 65001 >nul
cd /d "%~dp0"
rem Quay lai du lieu truoc mot lan nhap Excel. Dong cua so trang quan tri truoc khi chay.
set "PY=python"
py --version >nul 2>nul && set "PY=py"
%PY% tools\khoi_phuc.py
pause
