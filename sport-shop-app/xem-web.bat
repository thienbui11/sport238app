@echo off
chcp 65001 >nul
cd /d "%~dp0"
rem Xem truoc web dung nhu khach se thay (thu muc dist do cap-nhat-web.bat tao ra). Dong cua so nay la tat.
rem Luu y: http://localhost:3000 (trang quan tri dang chay) hien ban HTML du phong, KHONG phai ban chinh.
if not exist dist\index.html (
  echo Chua co thu muc dist. Hay bam cap-nhat-web.bat truoc.
  pause
  exit /b 1
)
if not exist dist\_next echo LUU Y: dist dang la ban HTML du phong. Bam cap-nhat-web.bat de xuat ban chinh (Next.js) roi mo lai.
set "PY=python"
py --version >nul 2>nul && set "PY=py"
echo Dang mo http://localhost:8080 ... (dong cua so nay de tat)
start "" http://localhost:8080/
%PY% -m http.server 8080 --directory dist
