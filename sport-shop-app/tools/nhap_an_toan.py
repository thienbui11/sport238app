"""Nhập hàng hằng ngày an toàn (dùng trong daily_update.py, khoi_phuc.py):
- lay_tu_tai_ve: lấy file Excel Sapo mới nhất trong thư mục Tải về → CHÉP vào inbox (không chuyển, không xóa file gốc).
- kiem_tra_file: file có đủ cột Sapo cần dùng không (thiếu cột → dừng, không nhập).
- bat_thuong: số sản phẩm/phiên bản giảm mạnh so với đang có (vd xuất nhầm bộ lọc trong Sapo) → dừng, hỏi lại.
- sao_luu: chép cơ sở dữ liệu trước khi nhập (giữ 30 bản gần nhất) để quay lại được.
- bao_cao: trang HTML liệt kê thay đổi (SP mới, SP không còn, đổi giá, hết hàng, có hàng lại).
Chỉ đọc giá bán lẻ và tồn kho như bộ đọc Excel; không đọc giá nhập/giá vốn."""
import datetime, hashlib, html, json, pathlib, shutil, sqlite3

# Cột Sapo mà bộ đọc Excel dùng (sapo_xlsx_to_json.build_catalog)
COT_CAN = ["Tên sản phẩm*", "Mã SKU*", "Loại sản phẩm", "Nhãn hiệu", "PL_Giá bán lẻ",
           "Thuộc tính 1", "Giá trị thuộc tính 1", "Thuộc tính 2", "Giá trị thuộc tính 2", "Thuộc tính 3", "Giá trị thuộc tính 3"]
MAU_FILE = "danh_sach_san_pham*.xlsx"      # tên file khi bấm "Xuất file" danh sách sản phẩm trong Sapo
NGUONG_GIAM = 0.7                           # còn dưới 70% số SP/phiên bản đang có → coi là bất thường
GIU_SAO_LUU = 30


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()


def doc_da_nhap(data_dir):
    f = pathlib.Path(data_dir) / "da-nhap.json"
    try: return json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError): return {}


def ghi_da_nhap(data_dir, path):
    d = doc_da_nhap(data_dir)
    d[sha256(path)] = {"ten": pathlib.Path(path).name, "luc": f"{datetime.datetime.now():%d/%m/%Y %H:%M}"}
    f = pathlib.Path(data_dir) / "da-nhap.json"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def lay_tu_tai_ve(tai_ve, inbox, data_dir, mau=MAU_FILE):
    """File Excel Sapo mới nhất trong Tải về, chưa từng nhập, chưa có trong inbox → chép vào inbox. Trả về đường dẫn bản chép hoặc None.
    Không bao giờ chuyển hay xóa file gốc."""
    tai_ve, inbox = pathlib.Path(tai_ve), pathlib.Path(inbox)
    if not tai_ve.is_dir(): return None
    files = sorted((f for f in tai_ve.glob(mau) if f.is_file() and not f.name.startswith("~$")), key=lambda f: f.stat().st_mtime, reverse=True)
    if not files: return None
    moi = files[0]
    h = sha256(moi)
    if h in doc_da_nhap(data_dir): return None
    inbox.mkdir(parents=True, exist_ok=True)
    if any(sha256(f) == h for f in inbox.glob("*.xlsx")): return None
    dich = inbox / moi.name
    shutil.copy2(moi, dich)
    return dich


def kiem_tra_file(path):
    """Danh sách lỗi (rỗng = dùng được). Chỉ đọc dòng tiêu đề."""
    import pandas as pd
    try:
        cols = [str(c).strip() for c in pd.read_excel(path, nrows=0).columns]
    except Exception as e:      # file hỏng, đang tải dở, không phải Excel
        return [f"Không mở được file Excel ({type(e).__name__}). File có thể đang tải dở hoặc bị hỏng: hãy xuất lại từ Sapo."]
    loi = [f"Thiếu cột \"{c}\"" for c in COT_CAN if c not in cols]
    if not any(c.startswith("LC_") and "Tồn kho ban đầu" in c for c in cols):
        loi.append("Thiếu cột tồn kho (\"LC_… Tồn kho ban đầu\")")
    if loi:
        loi.append("Có thể đây không phải file \"Danh sách sản phẩm\" xuất từ Sapo (nút Xuất file → Tất cả sản phẩm), hoặc Sapo đã đổi mẫu file.")
    return loi


def bat_thuong(cu, moi, nguong=NGUONG_GIAM):
    """cu: sản phẩm đang có trên web (đang bán), moi: sản phẩm đọc từ file. Trả về câu cảnh báo hoặc None."""
    sp_cu, sp_moi = len(cu), len(moi)
    pb_cu, pb_moi = sum(len(p["variants"]) for p in cu), sum(len(p["variants"]) for p in moi)
    if sp_cu >= 10 and sp_moi < sp_cu * nguong:
        return f"Số sản phẩm giảm mạnh: đang có {sp_cu}, file mới chỉ có {sp_moi}."
    if pb_cu >= 20 and pb_moi < pb_cu * nguong:
        return f"Số phiên bản (size/màu) giảm mạnh: đang có {pb_cu}, file mới chỉ có {pb_moi}."
    return None


def sao_luu(data_dir, ten="truoc-nhap", giu=GIU_SAO_LUU):
    """Chép shop.db (an toàn cả khi trang quản trị đang chạy) vào data/sao-luu/. Trả về đường dẫn bản sao hoặc None nếu chưa có dữ liệu."""
    data_dir = pathlib.Path(data_dir)
    src = data_dir / "shop.db"
    if not src.exists(): return None
    d = data_dir / "sao-luu"; d.mkdir(parents=True, exist_ok=True)
    dst = d / f"shop-{datetime.datetime.now():%Y%m%d-%H%M%S}-{ten}.db"
    n = 1
    while dst.exists(): dst = d / f"shop-{datetime.datetime.now():%Y%m%d-%H%M%S}-{ten}-{n}.db"; n += 1
    a = sqlite3.connect(f"file:{src.as_posix()}?mode=ro", uri=True); b = sqlite3.connect(dst)
    try: a.backup(b)
    finally: a.close(); b.close()
    cu = sorted(d.glob("shop-*.db"), key=lambda f: f.name, reverse=True)
    for f in cu[giu:]: f.unlink()
    return dst


def danh_sach_sao_luu(data_dir):
    """[(đường dẫn, số SP đang bán, thời điểm)] mới nhất trước."""
    out = []
    for f in sorted((pathlib.Path(data_dir) / "sao-luu").glob("shop-*.db"), key=lambda f: f.name, reverse=True):
        try:
            c = sqlite3.connect(f"file:{f.as_posix()}?mode=ro", uri=True)
            n = c.execute("SELECT COUNT(*) FROM products WHERE active=1").fetchone()[0]; c.close()
        except sqlite3.Error:
            n = None
        s = f.stem.split("-")
        luc = f"{s[1][6:8]}/{s[1][4:6]}/{s[1][:4]} {s[2][:2]}:{s[2][2:4]}" if len(s) > 2 and len(s[1]) == 8 else f.stem
        out.append((f, n, luc))
    return out


def khoi_phuc(data_dir, ban):
    """Ghi đè shop.db bằng bản sao lưu `ban`. Trang quản trị PHẢI đang tắt. Sao lưu dữ liệu hiện tại trước (tên ...-truoc-khoi-phuc)."""
    data_dir = pathlib.Path(data_dir)
    truoc = sao_luu(data_dir, "truoc-khoi-phuc", giu=10 ** 6)
    a = sqlite3.connect(f"file:{pathlib.Path(ban).as_posix()}?mode=ro", uri=True); b = sqlite3.connect(data_dir / "shop.db")
    try:
        a.backup(b)
        b.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    finally: a.close(); b.close()
    return truoc


def _money(n): return f"{n:,}".replace(",", ".") + "đ"


def _bien_the(p):
    return {v["id"]: v for v in p["variants"]}


def thay_doi(truoc, sau):
    """truoc/sau: danh sách SP từ /api/admin/products (đủ cả SP ẩn, không còn trong Sapo). So sánh SP đang bán (active)."""
    A = {p["id"]: p for p in truoc if p.get("active", 1)}
    B = {p["id"]: p for p in sau if p.get("active", 1)}
    ten = lambda p: p.get("display_title") or p["title"]
    nhan = lambda v: " / ".join(x for x in [v.get("option1"), v.get("option2")] if x and x != "Mặc định") or "—"
    r = {"moi": [B[i] for i in B if i not in A], "mat": [A[i] for i in A if i not in B], "gia": [], "het": [], "lai": [], "ton": 0}
    for i in B.keys() & A.keys():
        va, vb = _bien_the(A[i]), _bien_the(B[i])
        for k in va.keys() & vb.keys():
            x, y = va[k], vb[k]
            if x["price"] != y["price"]: r["gia"].append((ten(B[i]), nhan(y), x["price"], y["price"]))
            qx, qy = max(0, x["inventory_quantity"]), max(0, y["inventory_quantity"])
            if qx != qy: r["ton"] += 1
            if qx > 0 and qy == 0: r["het"].append((ten(B[i]), nhan(y)))
            if qx == 0 and qy > 0: r["lai"].append((ten(B[i]), nhan(y), qy))
    r["ten"] = ten
    return r


def bao_cao(truoc, sau, out_path, ten_file="", ghi_chu=""):
    """Ghi trang HTML liệt kê thay đổi sau khi nhập. Trả về (đường dẫn, tóm tắt một dòng)."""
    r = thay_doi(truoc, sau); ten = r["ten"]; e = html.escape
    tom = f"{len(r['moi'])} SP mới, {len(r['mat'])} SP không còn trong file, {len(r['gia'])} phiên bản đổi giá, {len(r['het'])} vừa hết hàng, {len(r['lai'])} có hàng lại, {r['ton']} phiên bản đổi số tồn"

    def bang(tieu_de, dau, dong, trong="Không có"):
        body = "".join("<tr>" + "".join(f"<td>{e(str(c))}</td>" for c in d) + "</tr>" for d in dong)
        return f"<h2>{e(tieu_de)} ({len(dong)})</h2>" + (f"<div class=t><table><thead><tr>{''.join(f'<th>{e(h)}</th>' for h in dau)}</tr></thead><tbody>{body}</tbody></table></div>" if dong else f"<p class=m>{trong}</p>")
    noi = (bang("Sản phẩm mới", ["Mã", "Tên", "Danh mục", "Tồn"], [(p["id"], ten(p), p.get("category", ""), sum(max(0, v["inventory_quantity"]) for v in p["variants"])) for p in r["moi"]])
           + bang("Không còn trong file Sapo (đã ẩn khỏi web)", ["Mã", "Tên"], [(p["id"], ten(p)) for p in r["mat"]])
           + bang("Đổi giá bán", ["Sản phẩm", "Size / màu", "Giá cũ", "Giá mới"], [(a, b, _money(c), _money(d)) for a, b, c, d in r["gia"]])
           + bang("Vừa hết hàng", ["Sản phẩm", "Size / màu"], r["het"])
           + bang("Có hàng lại", ["Sản phẩm", "Size / màu", "Tồn"], r["lai"]))
    page = f"""<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Báo cáo cập nhật hàng {datetime.datetime.now():%d/%m/%Y %H:%M}</title><style>
:root{{color-scheme:light dark;--ac:#a3122a;--ln:#ddd}}@media(prefers-color-scheme:dark){{:root{{--ac:#ff8a9a;--ln:#444}}}}
body{{font:15px/1.5 system-ui,sans-serif;max-width:980px;margin:0 auto;padding:16px}}h1{{color:var(--ac);font-size:22px}}h2{{font-size:18px;margin-top:28px}}
.t{{overflow-x:auto}}table{{border-collapse:collapse;width:100%}}th,td{{text-align:left;padding:6px 8px;border-bottom:1px solid var(--ln)}}th{{font-size:13px}}.m{{opacity:.75}}
.box{{border:1px solid var(--ln);border-radius:12px;padding:12px 14px}}</style></head><body>
<h1>Báo cáo cập nhật hàng – {datetime.datetime.now():%d/%m/%Y %H:%M}</h1>
<div class=box><p><b>File:</b> {e(ten_file)}</p><p><b>Tóm tắt:</b> {e(tom)}.</p>{f"<p>{e(ghi_chu)}</p>" if ghi_chu else ""}
<p class=m>Ảnh, tên hiển thị, mô tả, danh mục chọn tay được giữ nguyên. Muốn quay lại dữ liệu trước lần nhập này: tắt trang quản trị rồi bấm <b>khoi-phuc.bat</b>.</p></div>
{noi}</body></html>"""
    out_path = pathlib.Path(out_path); out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(page, encoding="utf-8")
    return out_path, tom
