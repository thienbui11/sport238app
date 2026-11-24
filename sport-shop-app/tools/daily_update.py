#!/usr/bin/env python3
"""Cập nhật hằng ngày (một nút: cap-nhat-web.bat):
  1. Lấy file Excel Sapo mới nhất trong thư mục Tải về (CHÉP vào inbox, không đụng file gốc).
  2. Kiểm tra file (đủ cột Sapo; số SP không giảm bất thường) → sai thì dừng, không nhập.
  3. Sao lưu dữ liệu (data/sao-luu/) → nhập vào trang quản trị → báo cáo thay đổi (bao-cao/*.html).
  4. Xuất web tĩnh (Next.js, lỗi thì bản HTML) → (tùy chọn) đưa lên hosting.
Trang quản trị chưa chạy thì tự bật tạm rồi tắt khi xong.

Cách dùng:  python tools/daily_update.py              chạy đủ các bước
            python tools/daily_update.py --export-only   chỉ xuất lại web từ dữ liệu hiện có (vd sau khi thêm ảnh)
            python tools/daily_update.py --force         vẫn nhập dù số SP giảm mạnh (đã kiểm tra file đúng)
            python tools/daily_update.py --tu-dong       chạy theo lịch (không hỏi gì; bất thường thì dừng)
            python tools/daily_update.py --mo-bao-cao    mở báo cáo thay đổi sau khi nhập
Cài đặt qua tệp .env cùng thư mục với package.json (hoặc biến môi trường):
  ADMIN_PASSWORD   mật khẩu quản trị (bắt buộc)
  SERVER_URL       mặc định http://localhost:<PORT>
  INBOX            thư mục chứa file Excel, mặc định inbox
  TAI_VE           thư mục Tải về để tự lấy file Sapo (mặc định Downloads của máy; đặt TAI_VE=khong để tắt)
  DATA_DIR         thư mục dữ liệu của trang quản trị (mặc định data) – nơi sao lưu
  SITE_URL         địa chỉ web thật, vd https://sport238.vn (để chia sẻ Facebook/Zalo có logo)
  DEPLOY_CMD       lệnh đưa dist lên hosting, vd: npx wrangler pages deploy dist --project-name=sport238
  XUAT_WEB=html    luôn xuất bằng bản HTML dự phòng
Cần: pip install pandas openpyxl"""
import datetime, json, os, pathlib, shutil, subprocess, sys, time, urllib.parse, urllib.request

HERE = pathlib.Path(__file__).resolve().parent
APP = HERE.parent
sys.path.insert(0, str(HERE))
LOG = APP / "daily_update.log"


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
    with open(LOG, "a", encoding="utf-8") as f:
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


def _path(env, key, default):
    p = pathlib.Path(env.get(key) or default)
    return p if p.is_absolute() else APP / p


def _get(server, path, cookie):
    with urllib.request.urlopen(urllib.request.Request(server + path, headers={"Cookie": cookie}), timeout=60) as r:
        return json.load(r)


def _song(server):
    try:
        urllib.request.urlopen(server + "/api/config", timeout=5); return True
    except Exception:
        return False


def bat_may_chu(server, env):
    """Trang quản trị chưa chạy (và là máy này) → tự bật tạm. Trả về tiến trình (để tắt khi xong) hoặc None."""
    host = urllib.parse.urlparse(server).hostname
    if host not in ("localhost", "127.0.0.1"): return None
    if not shutil.which("node"):
        log("Máy chưa cài Node.js nên không tự bật được trang quản trị."); return None
    log("Trang quản trị chưa chạy: tự bật tạm …")
    port = str(urllib.parse.urlparse(server).port or 80)
    keep = {k: v for k, v in env.items() if k in ("ADMIN_PASSWORD", "DATA_DIR")}
    p = subprocess.Popen(["node", "--disable-warning=ExperimentalWarning", "--env-file-if-exists=.env", "src/server.js"], cwd=APP,
                         env={**os.environ, **keep, "PORT": port}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(100):
        if _song(server): return p
        if p.poll() is not None: break
        time.sleep(0.2)
    p.terminate(); return None


def hoi(cau):
    """Hỏi có/không khi có người ngồi máy; chạy theo lịch thì coi là Không."""
    if not sys.stdin or not sys.stdin.isatty(): return False
    try:
        return input(cau + " Gõ c rồi Enter để nhập, chỉ Enter để dừng: ").strip().lower() in ("c", "co", "có", "y", "yes")
    except EOFError:
        return False


def nhap(env, server, inbox, data_dir, args):
    """Bước 1–3. Trả về mã lỗi (0 = xong hoặc không có gì để nhập)."""
    import nhap_an_toan as an
    tai_ve = env.get("TAI_VE", str(pathlib.Path.home() / "Downloads")).strip()
    co_tai_ve = bool(tai_ve) and tai_ve.lower() != "khong"
    if co_tai_ve:
        chep = an.lay_tu_tai_ve(tai_ve, inbox, data_dir, env.get("MAU_FILE") or an.MAU_FILE)
        if chep: log(f"Đã chép file mới từ {tai_ve}: {chep.name} (file gốc giữ nguyên).")
    files = sorted([f for f in inbox.glob("*.xlsx") if not f.name.startswith("~$")], key=lambda f: f.stat().st_mtime, reverse=True)
    if not files:
        log(f"Không có file Excel mới (thư mục {inbox}{' và ' + tai_ve if co_tai_ve else ''}): giữ nguyên dữ liệu hàng, chỉ xuất lại web (để ảnh và mô tả vừa sửa lên mạng).")
        return 0
    latest = files[0]
    log(f"Kiểm tra {latest.name} …")
    loi = an.kiem_tra_file(latest)
    if loi:
        bad = inbox / "loi"; bad.mkdir(exist_ok=True); shutil.move(str(latest), str(bad / latest.name))
        log("FILE KHÔNG DÙNG ĐƯỢC, KHÔNG NHẬP: " + " | ".join(loi) + f" (đã để file sang {bad})")
        return 1
    import sapo_xlsx_to_json as conv
    products, dropped = conv.build_catalog(str(latest))
    if not products:
        log("File không có sản phẩm thể thao nào, bỏ qua (không thay đổi gì)."); return 1
    cookie = login(server, env["ADMIN_PASSWORD"])
    truoc = _get(server, "/api/admin/products", cookie)["products"]
    canh_bao = an.bat_thuong([p for p in truoc if p.get("active", 1)], products)
    if canh_bao and "--force" not in args:
        log("DỪNG, CHƯA NHẬP: " + canh_bao + " Có thể đã xuất nhầm (đang lọc theo loại/kho trong Sapo).")
        if "--tu-dong" in args or not hoi("Anh/chị đã kiểm tra, file này đúng?"):
            log("Hãy xuất lại file đầy đủ từ Sapo. Nếu chắc chắn file đúng: chạy cap-nhat-web.bat rồi gõ c khi được hỏi.")
            return 3
    bk = an.sao_luu(data_dir) if data_dir.exists() else None
    log(f"Đã sao lưu dữ liệu: {bk.name}" if bk else f"Không tìm thấy dữ liệu trang quản trị trong {data_dir} để sao lưu (máy chủ ở nơi khác?).")
    req = urllib.request.Request(server + "/api/admin/import", data=json.dumps({"products": products}, ensure_ascii=False).encode(),
                                 headers={"Content-Type": "application/json", "Cookie": cookie})
    with urllib.request.urlopen(req, timeout=120) as r:
        res = json.load(r)
    log(f"Đã nhập vào trang quản trị: {res['products']} sản phẩm, {res['variants']} phiên bản (bỏ {dropped} phiên bản giá 0).")
    sau = _get(server, "/api/admin/products", cookie)["products"]
    rp, tom = an.bao_cao(truoc, sau, _path(env, "BAO_CAO", "bao-cao") / f"cap-nhat-{datetime.datetime.now():%Y%m%d-%H%M%S}.html", latest.name,
                         "Đã nhập dù số sản phẩm giảm mạnh (người dùng xác nhận)." if canh_bao else "")
    log(f"Thay đổi: {tom}. Báo cáo: {rp}")
    if "--mo-bao-cao" in args and hasattr(os, "startfile"):
        try: os.startfile(rp)
        except OSError: pass
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "last_import.txt").write_text(datetime.date.today().strftime("%d/%m/%Y"), encoding="utf-8")
    an.ghi_da_nhap(data_dir, latest)
    done = inbox / "da-xu-ly"; done.mkdir(exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    for f in files:
        shutil.move(str(f), str(done / f"{stamp}_{f.name}"))
    return 0


def main(args=None):
    args = sys.argv[1:] if args is None else args
    env = load_env()
    export_only = "--export-only" in args
    server = (env.get("SERVER_URL") or f"http://localhost:{env.get('PORT', '3000')}").rstrip("/")
    inbox = _path(env, "INBOX", "inbox")
    data_dir = _path(env, "DATA_DIR", "data")
    if not env.get("ADMIN_PASSWORD") and not export_only:
        log("Thiếu ADMIN_PASSWORD (đặt trong tệp .env)."); return 2
    tam = None
    if not _song(server):
        tam = bat_may_chu(server, env)
        if tam is None:
            log(f"Không kết nối được trang quản trị tại {server}. Hãy chạy chay-quan-tri.bat (hoặc npm start) trước."); return 2
    try:
        if not export_only:
            rc = nhap(env, server, inbox, data_dir, args)
            if rc: return rc
        # ngày ghi trên web = ngày nhập Excel gần nhất (không phải ngày hôm nay nếu hôm nay chưa nhập)
        st = data_dir / "last_import.txt"
        updated = st.read_text(encoding="utf-8").strip() if st.exists() else datetime.date.today().strftime("%d/%m/%Y")
        out, kind = xuat_web(env, server, updated, env.get("THU_MUC_XUAT") or "dist")
        log(f"Đã xuất web tĩnh ({kind}) vào {out} (tồn kho ngày {updated}).")
    finally:
        if tam: tam.terminate(); tam.wait(10)
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
