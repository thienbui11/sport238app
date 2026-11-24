#!/usr/bin/env python3
"""Quay lại dữ liệu trước một lần nhập Excel (bản sao lưu trong data/sao-luu/, tự tạo mỗi lần cập nhật).
Phải TẮT trang quản trị trước (đóng cửa sổ chay-quan-tri.bat). Dữ liệu hiện tại được sao lưu lại trước khi ghi đè,
nên khôi phục nhầm vẫn quay lại được.

Cách dùng:  python tools/khoi_phuc.py              liệt kê các bản sao lưu, hỏi chọn số
            python tools/khoi_phuc.py --chon 1 --dong-y   khôi phục bản mới nhất, không hỏi"""
import pathlib, sys, urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import nhap_an_toan as an
from daily_update import APP, load_env, _path


def dang_chay(env):
    url = (env.get("SERVER_URL") or f"http://localhost:{env.get('PORT', '3000')}").rstrip("/")
    try:
        urllib.request.urlopen(url + "/api/config", timeout=3); return url
    except Exception:
        return None


def main(args=None):
    args = sys.argv[1:] if args is None else args
    env = load_env()
    data = _path(env, "DATA_DIR", "data")
    ds = an.danh_sach_sao_luu(data)
    if not ds:
        print(f"Chưa có bản sao lưu nào trong {data / 'sao-luu'} (bản sao lưu được tạo mỗi lần cập nhật hàng)."); return 1
    print("Các bản sao lưu (mới nhất ở trên):")
    for i, (f, n, luc) in enumerate(ds, 1):
        print(f"  {i:>2}. {luc}  –  {n if n is not None else '?'} sản phẩm đang bán  ({f.name})")
    url = dang_chay(env)
    if url:
        print(f"\nTrang quản trị đang chạy ({url}). Hãy đóng cửa sổ trang quản trị trước rồi chạy lại khôi phục."); return 2
    chon = args[args.index("--chon") + 1] if "--chon" in args else None
    if chon is None:
        try: chon = input("\nGõ số bản muốn quay lại rồi Enter (chỉ Enter để thoát): ").strip()
        except EOFError: chon = ""
    if not chon: print("Không khôi phục gì."); return 0
    if not chon.isdigit() or not 1 <= int(chon) <= len(ds):
        print("Số không hợp lệ."); return 1
    f, n, luc = ds[int(chon) - 1]
    if "--dong-y" not in args:
        try: ok = input(f"Quay lại dữ liệu lúc {luc} ({n} sản phẩm)? Gõ c rồi Enter để đồng ý: ").strip().lower() in ("c", "co", "có", "y")
        except EOFError: ok = False
        if not ok: print("Không khôi phục gì."); return 0
    truoc = an.khoi_phuc(data, f)
    print(f"Đã quay lại dữ liệu lúc {luc}. Dữ liệu trước khi khôi phục được giữ ở {truoc.name if truoc else '(không có)'}.")
    print("Bật lại trang quản trị (chay-quan-tri.bat), kiểm tra, rồi bấm cap-nhat-web.bat để xuất lại web.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
