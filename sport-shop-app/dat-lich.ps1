# Đặt lịch cho máy tự cập nhật web mỗi ngày (Windows Task Scheduler).
# Cách chạy: bấm chuột phải vào tệp này → "Run with PowerShell". Chạy lại để đổi giờ. Gỡ lịch: .\dat-lich.ps1 -Go
# Máy phải đang bật (không ngủ) vào giờ đã đặt. Trước giờ đó, bấm "Xuất file" danh sách sản phẩm trong Sapo
# (file tự vào thư mục Tải về); công cụ sẽ tự chép, kiểm tra, sao lưu, nhập và xuất web. File bất thường thì dừng, không nhập.
param(
  [string]$Gio = "21:15",          # sau giờ đóng cửa 21:00
  [switch]$Go
)
$ErrorActionPreference = "Stop"
$ten = "SPORT238 cap nhat web"
if ($Go) {
  Unregister-ScheduledTask -TaskName $ten -Confirm:$false -ErrorAction SilentlyContinue
  Write-Host "Đã gỡ lịch '$ten'."
  exit 0
}
$thuMuc = $PSScriptRoot
$py = (Get-Command py -ErrorAction SilentlyContinue).Source
if (-not $py) { $py = (Get-Command python -ErrorAction SilentlyContinue).Source }
if (-not $py) { Write-Host "Chưa tìm thấy Python. Cài Python trước (python.org)."; exit 1 }
$viec = New-ScheduledTaskAction -Execute $py -Argument "tools\daily_update.py --tu-dong" -WorkingDirectory $thuMuc
$luc = New-ScheduledTaskTrigger -Daily -At $Gio
$caiDat = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 1)
Register-ScheduledTask -TaskName $ten -Action $viec -Trigger $luc -Settings $caiDat -Description "Nhập file Excel Sapo mới nhất và xuất web SPORT 238" -Force | Out-Null
Write-Host "Đã đặt lịch: mỗi ngày lúc $Gio máy tự cập nhật web. Nhật ký: $thuMuc\daily_update.log ; báo cáo thay đổi: $thuMuc\bao-cao\"
