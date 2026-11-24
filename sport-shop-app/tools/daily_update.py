#!/usr/bin/env python3
"""Cập nhật hằng ngày: file Excel mới nhất trong thư mục inbox -> nhập vào trang quản trị -> xuất web tĩnh -> (tùy chọn) đưa lên hosting.

Cách dùng:  python tools/daily_update.py            chạy đủ các bước
            python tools/daily_update.py --export-only   chỉ xuất lại web từ dữ liệu hiện có (vd sau khi thêm ảnh)
Cài đặt qua tệp .env cùng thư mục với package.json (hoặc biến môi trường):
  ADMIN_PASSWORD   mật khẩu quản trị (bắt buộc)
  SERVER_URL       mặc định http://localhost:<PORT>
  INBOX            thư mục chứa file Excel, mặc định inbox
  SITE_URL         địa chỉ web thật, vd https://sport238.vn (để chia sẻ Facebook/Zalo có logo)
  DEPLOY_CMD       lệnh đưa dist lên hosting, vd: npx wrangler pages deploy dist --project-name=sport238
Cần: pip install pandas openpyxl   và trang quản trị đang chạy (npm start)."""
import datetime, json, os, pathlib, shutil, subprocess, sys, urllib.request

HERE = pathlib.Path(__file__).resolve().parent
APP = HERE.parent
STATE = APP / "data" / "last_import.txt"
sys.path.insert(0, str(HERE))


def load_env():
    env = dict(os.environ)
    f = APP / ".env"
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env.setdefault(k.strip(), v.strip().strip('"'))
    return env


def log(msg):
    line = f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line)
    with open(APP / "daily_update.log", "a", encoding="utf-8") as f:
        f.write(line + "\n")


def login(server, password):
    req = urllib.request.Request(server + "/api/admin/login", data=json.dumps({"password": password}).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.headers.get("Set-Cookie", "").split(";")[0]


def xuat_web(env, server, updated, out="dist"):
    """Xuất web tĩnh. Bản chính: Next.js (mỗi sản phẩm một trang riêng cho Google, Zalo, Facebook).
    Máy chưa cài thư viện Next.js, hoặc build lỗi (ví dụ mất mạng khi tải phông chữ) → tự dùng bản HTML dự phòng.
    Đặt XUAT_WEB=html trong .env để luôn dùng bản HTML."""
    import export_static
    site = env.get("SITE_URL", "")
    if env.get("XUAT_WEB", "").strip().lower() != "html":
        import export_next
        if export_next.available():
            try:
                return export_next.export(server, out, site, updated, quiet=True), "Next.js"
            except SystemExit as e:
                log(f"Xuất bằng Next.js lỗi, dùng bản HTML dự phòng. Chi tiết: {str(e)[-600:]}")
        else:
            log("Chưa cài thư viện Next.js (sport-shop-next/frontend: npm install), dùng bản HTML.")
    return export_static.export(server, out, site, updated, quiet=True), "HTML"


def main():
    env = load_env()
    export_only = "--export-only" in sys.argv
    server = (env.get("SERVER_URL") or f"http://localhost:{env.get('PORT', '3000')}").rstrip("/")
    inbox = pathlib.Path(env.get("INBOX", "inbox"))
    inbox = inbox if inbox.is_absolute() else APP / inbox
    if not env.get("ADMIN_PASSWORD") and not export_only:
        log("Thiếu ADMIN_PASSWORD (đặt trong tệp .env)."); return 2
    try:
        urllib.request.urlopen(server + "/api/config", timeout=10)
    except Exception:
        log(f"Không kết nối được trang quản trị tại {server}. Hãy chạy 'npm start' trước."); return 2

    latest = None
    if not export_only:
        files = sorted([f for f in inbox.glob("*.xlsx") if not f.name.startswith("~$")], key=lambda f: f.stat().st_mtime, reverse=True)
        latest = files[0] if files else None
        if latest is None:
            log(f"Không có file Excel mới trong {inbox}: giữ nguyên dữ liệu hàng, chỉ xuất lại web (để ảnh và mô tả vừa sửa lên mạng).")
    if not export_only and latest is not None:
        log(f"Đọc {latest.name} …")
        import sapo_xlsx_to_json as conv
        products, dropped = conv.build_catalog(str(latest))
        if not products:
            log("File không có sản phẩm thể thao nào, bỏ qua (không thay đổi gì)."); return 1
        cookie = login(server, env["ADMIN_PASSWORD"])
        req = urllib.request.Request(server + "/api/admin/import", data=json.dumps({"products": products}, ensure_ascii=False).encode(), headers={"Content-Type": "application/json", "Cookie": cookie})
        with urllib.request.urlopen(req, timeout=120) as r:
            res = json.load(r)
        log(f"Đã nhập vào trang quản trị: {res['products']} sản phẩm, {res['variants']} phiên bản (bỏ {dropped} phiên bản giá 0).")
        STATE.parent.mkdir(exist_ok=True); STATE.write_text(datetime.date.today().strftime("%d/%m/%Y"), encoding="utf-8")
        done = inbox / "da-xu-ly"; done.mkdir(exist_ok=True)
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        for f in files:
            shutil.move(str(f), str(done / f"{stamp}_{f.name}"))

    # ngày ghi trên web = ngày nhập Excel gần nhất (không phải ngày hôm nay nếu hôm nay chưa nhập)
    updated = STATE.read_text(encoding="utf-8").strip() if STATE.exists() else datetime.date.today().strftime("%d/%m/%Y")
    out, kind = xuat_web(env, server, updated)
    log(f"Đã xuất web tĩnh ({kind}) vào {out} (tồn kho ngày {updated}).")
    cmd = env.get("DEPLOY_CMD", "").strip()
    if cmd:
        log(f"Đưa lên hosting: {cmd}")
        r = subprocess.run(cmd, shell=True, cwd=APP)
        log("Đưa lên hosting " + ("thành công." if r.returncode == 0 else f"THẤT BẠI (mã {r.returncode})."))
        return r.returncode
    log("Chưa đặt DEPLOY_CMD: hãy tải thư mục dist lên hosting (xem HUONG-DAN-DUA-LEN-MANG.md).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
