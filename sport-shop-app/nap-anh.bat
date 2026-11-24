@echo off
chcp 65001 >nul
cd /d "%~dp0"
rem Nap anh hang loat: keo tha thu muc anh vao tep nay (ten tep anh theo ma SKU, vd PVN3939.jpg, PVN3939-1.jpg)
set "PY=python"
py --version >nul 2>nul && set "PY=py"
set "DIR=%~1"
if "%DIR%"=="" set /p "DIR=Keo tha thu muc anh vao day roi bam Enter: "
%PY% tools\nap_anh.py "%DIR%" --open
pause
