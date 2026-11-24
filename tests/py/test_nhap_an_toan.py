"""Kiểm thử nhập hàng hằng ngày an toàn (G1): lấy file từ Tải về (chép, không xóa), kiểm tra cột, số SP giảm bất thường,
sao lưu / khôi phục, báo cáo thay đổi, nút cập nhật tự bật trang quản trị. Mọi dữ liệu ở thư mục tạm."""
import hashlib, json, os, pathlib, shutil, socket, sqlite3, subprocess, time, urllib.request

import pandas as pd
import pytest

import daily_update
import khoi_phuc
import nhap_an_toan as an
from conftest import APP, PASSWORD, free_port

REAL = pathlib.Path.home() / "Downloads" / "danh_sach_san_pham_14.11.2026_7dcf063c851a56535e5688c4e0180807.xlsx"
COLS = an.COT_CAN + ["LC_CN1_Tồn kho ban đầu*", "PL_Giá nhập"]


def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def excel(path, cols=COLS):
    row = {c: "" for c in cols}
    row.update({"Tên sản phẩm*": "Quần áo Thử", "Mã SKU*": "T1", "PL_Giá bán lẻ": 150000, "LC_CN1_Tồn kho ban đầu*": 3, "PL_Giá nhập": 90000})
    pd.DataFrame([{c: row[c] for c in cols}]).to_excel(path, index=False)
    return path


@pytest.fixture(autouse=True)
def log_tam(tmp_path, monkeypatch):
    monkeypatch.setattr(daily_update, "LOG", tmp_path / "nhat-ky.log")


# ---------- kiểm tra file ----------
def test_file_du_cot(tmp_path):
    assert an.kiem_tra_file(excel(tmp_path / "a.xlsx")) == []


def test_thieu_cot_gia_ban(tmp_path):
    loi = an.kiem_tra_file(excel(tmp_path / "a.xlsx", [c for c in COLS if c != "PL_Giá bán lẻ"]))
    assert any("PL_Giá bán lẻ" in x for x in loi)


def test_thieu_cot_ton_kho(tmp_path):
    loi = an.kiem_tra_file(excel(tmp_path / "a.xlsx", [c for c in COLS if not c.startswith("LC_")]))
    assert any("tồn kho" in x for x in loi)


def test_file_hong(tmp_path):
    f = tmp_path / "hong.xlsx"; f.write_text("không phải excel", encoding="utf-8")
    assert "Không mở được" in an.kiem_tra_file(f)[0]


# ---------- lấy file từ Tải về ----------
def test_lay_tu_tai_ve_chep_khong_xoa(tmp_path):
    dl, inbox, data = tmp_path / "dl", tmp_path / "inbox", tmp_path / "data"; dl.mkdir()
    cu = excel(dl / "danh_sach_san_pham_13.11.2026_a.xlsx"); os.utime(cu, (time.time() - 3600,) * 2)
    moi = excel(dl / "danh_sach_san_pham_14.11.2026_b.xlsx", COLS[:-1])
    khac = excel(dl / "bao-gia.xlsx"); os.utime(khac, (time.time() + 60,) * 2)      # file Excel khác, mới hơn: bỏ qua
    h = {f: sha(f) for f in (cu, moi, khac)}
    got = an.lay_tu_tai_ve(dl, inbox, data)
    assert got == inbox / moi.name and sha(got) == h[moi]
    assert all(f.exists() and sha(f) == h[f] for f in h), "file gốc trong Tải về phải còn nguyên"
    assert an.lay_tu_tai_ve(dl, inbox, data) is None, "đã có trong inbox thì không chép lại"
    (inbox / "da-xu-ly").mkdir(); shutil.move(got, inbox / "da-xu-ly" / got.name); an.ghi_da_nhap(data, inbox / "da-xu-ly" / got.name)
    assert an.lay_tu_tai_ve(dl, inbox, data) is None, "đã nhập rồi thì không chép lại"


# ---------- số SP giảm bất thường ----------
def sp(n, v=3): return [{"id": f"P{i}", "variants": [{}] * v} for i in range(n)]


def test_bat_thuong():
    assert "giảm mạnh" in an.bat_thuong(sp(175), sp(100))
    assert "phiên bản" in an.bat_thuong(sp(175, 5), sp(170, 2))
    assert an.bat_thuong(sp(175), sp(168)) is None
    assert an.bat_thuong([], sp(175)) is None, "lần nhập đầu (chưa có dữ liệu) không chặn"


# ---------- báo cáo ----------
def test_bao_cao(tmp_path):
    v = lambda i, s, c, p, q: {"id": i, "option1": s, "option2": c, "price": p, "inventory_quantity": q}
    truoc = [{"id": "A", "title": "Áo A", "active": 1, "variants": [v("A1", "M", "Đỏ", 150000, 2), v("A2", "L", "Đỏ", 150000, 0)]},
             {"id": "B", "title": "Giày <B>", "active": 1, "variants": [v("B1", "40", "Mặc định", 300000, 1)]},
             {"id": "Z", "title": "Cũ đã ẩn", "active": 0, "variants": [v("Z1", "", "Mặc định", 1, 1)]}]
    sau = [{"id": "A", "title": "Áo A", "active": 1, "variants": [v("A1", "M", "Đỏ", 160000, 0), v("A2", "L", "Đỏ", 150000, 4)]},
           {"id": "B", "title": "Giày <B>", "active": 0, "variants": [v("B1", "40", "Mặc định", 300000, 1)]},
           {"id": "C", "title": "Vớ C", "category": "Vớ/tất ống đồng", "active": 1, "variants": [v("C1", "", "Mặc định", 20000, 9)]}]
    f, tom = an.bao_cao(truoc, sau, tmp_path / "bc.html", "danh_sach_san_pham.xlsx")
    h = f.read_text(encoding="utf-8")
    assert tom.startswith("1 SP mới, 1 SP không còn trong file, 1 phiên bản đổi giá, 1 vừa hết hàng, 1 có hàng lại, 2 phiên bản đổi số tồn")
    assert "Vớ C" in h and "Giày &lt;B&gt;" in h and "<B>" not in h, "tên được thoát ký tự HTML"
    assert "150.000đ" in h and "160.000đ" in h and "M / Đỏ" in h and "Cũ đã ẩn" not in h
    assert "khoi-phuc.bat" in h


# ---------- sao lưu, khôi phục ----------
def test_sao_luu_giu_so_ban(tmp_path):
    c = sqlite3.connect(tmp_path / "shop.db"); c.execute("CREATE TABLE products(id TEXT, active INTEGER)"); c.execute("INSERT INTO products VALUES('A',1)"); c.commit(); c.close()
    for _ in range(5): an.sao_luu(tmp_path, giu=3)
    ds = an.danh_sach_sao_luu(tmp_path)
    assert len(ds) == 3 and all(n == 1 for _, n, _ in ds)
    assert an.sao_luu(tmp_path / "khong-co") is None


def bat(data, port):
    p = subprocess.Popen(["node", "--disable-warning=ExperimentalWarning", "src/server.js"], cwd=APP,
                         env=dict(os.environ, DATA_DIR=str(data), PORT=str(port), ADMIN_PASSWORD=PASSWORD), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(100):
        try: urllib.request.urlopen(f"http://127.0.0.1:{port}/api/config", timeout=1); return p
        except OSError: time.sleep(0.1)
    raise RuntimeError("không bật được máy chủ")


def tat(p): p.terminate(); p.wait(10)


def mo_ta(data, pid):
    c = sqlite3.connect(data / "shop.db"); r = c.execute("SELECT description FROM products WHERE id=?", (pid,)).fetchone()[0]; c.close(); return r


def test_khoi_phuc(tmp_path, monkeypatch):
    data = tmp_path / "data"; data.mkdir(); shutil.copy(APP / "data" / "seed-products.json", data)
    port = free_port(); p = bat(data, port)
    srv = {"url": f"http://127.0.0.1:{port}", "password": PASSWORD}
    pid = json.loads((data / "seed-products.json").read_text(encoding="utf-8"))["products"][0]["id"]
    an.sao_luu(data)
    req = urllib.request.Request(srv["url"] + "/api/admin/login", data=json.dumps({"password": PASSWORD}).encode(), headers={"Content-Type": "application/json"})
    ck = urllib.request.urlopen(req).headers["Set-Cookie"].split(";")[0]
    urllib.request.urlopen(urllib.request.Request(srv["url"] + "/api/admin/products/" + pid, method="PUT", headers={"Content-Type": "application/json", "Cookie": ck},
                                                  data=json.dumps({"description": "đã sửa nhầm", "display_title": "", "hidden": False, "featured": False, "category": ""}).encode()))
    monkeypatch.setenv("DATA_DIR", str(data)); monkeypatch.setenv("SERVER_URL", srv["url"])
    assert khoi_phuc.main(["--chon", "1", "--dong-y"]) == 2, "trang quản trị đang chạy thì không khôi phục"
    tat(p)
    assert mo_ta(data, pid) == "đã sửa nhầm"
    assert khoi_phuc.main(["--chon", "1", "--dong-y"]) == 0
    assert mo_ta(data, pid) == ""
    truoc = [f for f, _, _ in an.danh_sach_sao_luu(data) if "truoc-khoi-phuc" in f.name]
    assert len(truoc) == 1
    c = sqlite3.connect(truoc[0]); assert c.execute("SELECT description FROM products WHERE id=?", (pid,)).fetchone()[0] == "đã sửa nhầm"; c.close()
    p = bat(data, port)       # máy chủ chạy lại bình thường trên dữ liệu đã khôi phục
    try:
        assert len(json.load(urllib.request.urlopen(srv["url"] + "/api/products"))["products"]) == 175
    finally:
        tat(p)


# ---------- cả quy trình với file Excel thật (chỉ chép, không đụng file gốc) ----------
def dang_ban(data):
    c = sqlite3.connect(data / "shop.db"); n = c.execute("SELECT COUNT(*) FROM products WHERE active=1").fetchone()[0]; c.close(); return n


@pytest.mark.skipif(not REAL.exists(), reason="không có file Excel thật 14/11 trong Tải về")
def test_quy_trinh_hang_ngay(server, tmp_path, monkeypatch):
    dl, inbox, out, bc = tmp_path / "dl", tmp_path / "inbox", tmp_path / "dist", tmp_path / "bc"; dl.mkdir()
    f = dl / REAL.name; shutil.copy(REAL, f); goc = sha(f)
    for k, v in {"ADMIN_PASSWORD": server["password"], "SERVER_URL": server["url"], "INBOX": str(inbox), "TAI_VE": str(dl), "DATA_DIR": str(server["data"]),
                 "XUAT_WEB": "html", "THU_MUC_XUAT": str(out), "BAO_CAO": str(bc), "DEPLOY_CMD": ""}.items():
        monkeypatch.setenv(k, v)
    assert daily_update.main([]) == 0
    assert f.exists() and sha(f) == goc, "file trong Tải về còn nguyên"
    assert [x.name.split("_", 1)[1] for x in (inbox / "da-xu-ly").iterdir()] == [REAL.name]
    assert len(an.danh_sach_sao_luu(server["data"])) == 1 and (out / "index.html").exists()
    rp = list(bc.glob("*.html")); assert len(rp) == 1
    assert "0 SP mới, 0 SP không còn trong file, 0 phiên bản đổi giá" in rp[0].read_text(encoding="utf-8"), "dữ liệu mẫu = file 14/11 nên không có thay đổi"
    log = daily_update.LOG.read_text(encoding="utf-8")
    assert "Đã nhập vào trang quản trị: 175 sản phẩm, 953 phiên bản (bỏ 68" in log
    # chạy lại: file đã nhập → không nhập lại, vẫn xuất web, không sao lưu thêm
    assert daily_update.main([]) == 0 and len(an.danh_sach_sao_luu(server["data"])) == 1
    assert "Không có file Excel mới" in daily_update.LOG.read_text(encoding="utf-8")
    # file xuất thiếu (chỉ 1/3 số dòng) → dừng, không nhập, không mất dữ liệu
    df = pd.read_excel(REAL); thieu = dl / "danh_sach_san_pham_15.11.2026_thieu.xlsx"; df.head(len(df) // 3).to_excel(thieu, index=False)
    assert daily_update.main(["--tu-dong"]) == 3
    assert dang_ban(server["data"]) == 175 and len(an.danh_sach_sao_luu(server["data"])) == 1 and (inbox / thieu.name).exists()
    assert "DỪNG, CHƯA NHẬP: Số phiên bản (size/màu) giảm mạnh: đang có 953" in daily_update.LOG.read_text(encoding="utf-8")
    # người dùng xác nhận file đúng → nhập, có sao lưu, báo cáo ghi SP không còn
    assert daily_update.main(["--force"]) == 0
    assert dang_ban(server["data"]) < 175 and len(an.danh_sach_sao_luu(server["data"])) == 2
    assert thieu.exists(), "file gốc trong Tải về còn nguyên"
    # file thiếu cột → để sang inbox/loi, không nhập
    excel(inbox / "sai.xlsx", [c for c in COLS if c != "Mã SKU*"])
    assert daily_update.main([]) == 1 and (inbox / "loi" / "sai.xlsx").exists()
    assert "Thiếu cột \"Mã SKU*\"" in daily_update.LOG.read_text(encoding="utf-8")


def test_tu_bat_may_chu(tmp_path, monkeypatch):
    data = tmp_path / "data"; data.mkdir(); shutil.copy(APP / "data" / "seed-products.json", data)
    port = free_port()
    for k, v in {"ADMIN_PASSWORD": PASSWORD, "SERVER_URL": f"http://127.0.0.1:{port}", "INBOX": str(tmp_path / "inbox"), "TAI_VE": "khong", "DATA_DIR": str(data),
                 "XUAT_WEB": "html", "THU_MUC_XUAT": str(tmp_path / "dist"), "DEPLOY_CMD": ""}.items():
        monkeypatch.setenv(k, v)
    assert daily_update.main([]) == 0
    assert "tự bật tạm" in daily_update.LOG.read_text(encoding="utf-8")
    assert len(json.loads((tmp_path / "dist" / "products.json").read_text(encoding="utf-8"))["products"]) == 175
    with socket.socket() as s:
        assert s.connect_ex(("127.0.0.1", port)) != 0, "xong thì tắt máy chủ đã bật tạm"
