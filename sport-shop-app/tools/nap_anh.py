#!/usr/bin/env python3
"""Nạp ảnh sản phẩm hàng loạt từ một thư mục, đặt tên tệp theo MÃ SKU (mã phiên bản trong Sapo).

Quy ước tên tệp:
  PVN3939.jpg            ảnh chính
  PVN3939-1.jpg, -2 ...  ảnh phụ (cũng nhận PVN3939_1.jpg và "PVN3939 (1).jpg")
Không phân biệt chữ hoa thường. Nhận .jpg .jpeg .png .webp.

Mã SKU là mã của PHIÊN BẢN nên công cụ tự biết ảnh thuộc sản phẩm nào và màu nào:
sản phẩm nhiều màu → ảnh gắn theo màu; sản phẩm một màu → ảnh chung.
Ảnh được xoay đúng chiều, thu nhỏ (cạnh dài tối đa 1400 px), đổi sang WebP rồi tải lên trang quản trị.
Ảnh cũ được GIỮ, ảnh mới thêm vào sau; tệp đã nạp rồi (cùng nội dung) sẽ bỏ qua.

Cách dùng (trang quản trị phải đang chạy: chay-quan-tri.bat hoặc npm start):
  python tools/nap_anh.py "D:/anh-san-pham"            nạp thật
  python tools/nap_anh.py "D:/anh-san-pham" --dry-run  chỉ xem trước, không tải lên
Mật khẩu quản trị lấy từ ADMIN_PASSWORD trong tệp .env (giống công cụ cập nhật hằng ngày).
Kết quả: báo cáo HTML trong thư mục bao-cao/ (tự mở nếu có --open)."""
import argparse, datetime, hashlib, html, io, json, pathlib, re, sys, urllib.error, urllib.request, webbrowser

from PIL import Image, ImageOps

HERE = pathlib.Path(__file__).resolve().parent
APP = HERE.parent
sys.path.insert(0, str(HERE))
from daily_update import load_env  # noqa: E402

EXTS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_SIDE = 1400
QUALITY = 82
SUFFIX = re.compile(r"^(?P<sku>.+?)(?:[-_ ]\(?(?P<n>\d{1,3})\)?|\s*\((?P<p>\d{1,3})\))$")


# ---------- máy chủ quản trị ----------
class Admin:
    def __init__(self, server, password):
        self.server, self.cookie = server.rstrip("/"), ""
        self.password = password

    def _req(self, path, data=None, ctype="application/json", method=None):
        h = {"Cookie": self.cookie} if self.cookie else {}
        if data is not None:
            h["Content-Type"] = ctype
        req = urllib.request.Request(self.server + path, data=data, headers=h, method=method)
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.headers, json.load(r)

    def login(self):
        hdr, _ = self._req("/api/admin/login", json.dumps({"password": self.password}).encode())
        self.cookie = (hdr.get("Set-Cookie") or "").split(";")[0]

    def products(self):
        return self._req("/api/admin/products")[1]

    def upload(self, data):
        return self._req("/api/admin/upload", data, "application/octet-stream")[1]["url"]

    def set_images(self, pid, color, urls):
        self._req("/api/admin/images", json.dumps({"product_id": pid, "color": color, "urls": urls}).encode())


# ---------- đọc thư mục ảnh ----------
def parse_name(stem, skus):
    """Trả (sku, thứ tự) hoặc None. thứ tự 0 là ảnh chính."""
    s = stem.strip()
    if s.upper() in skus:
        return skus[s.upper()], 0
    m = SUFFIX.match(s)
    if m:
        base = m.group("sku").strip().upper()
        if base in skus:
            return skus[base], int(m.group("n") or m.group("p"))
    return None


def to_webp(path):
    with Image.open(path) as im:
        im = ImageOps.exif_transpose(im)
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA")
            bg = Image.new("RGB", im.size, (255, 255, 255))
            bg.paste(im, mask=im.split()[-1])
            im = bg
        else:
            im = im.convert("RGB")
        im.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
        out = io.BytesIO()
        im.save(out, "WEBP", quality=QUALITY, method=6)
        return out.getvalue(), im.size


def plan(folder, catalog):
    """Ghép tệp ảnh với sản phẩm/màu. Trả (kế hoạch theo khóa ảnh, tệp không khớp, tệp không hỗ trợ)."""
    by_sku = {}
    for p in catalog["products"]:
        colors = []
        for v in p["variants"]:
            if v["option2"] not in colors:
                colors.append(v["option2"])
        for v in p["variants"]:
            by_sku[str(v["sku"]).upper()] = {"product": p, "color": v["option2"] if len(colors) > 1 else "", "sku": v["sku"]}
    groups, unmatched, unsupported = {}, [], []
    for f in sorted(pathlib.Path(folder).iterdir(), key=lambda x: x.name.lower()):
        if not f.is_file():
            continue
        if f.suffix.lower() not in EXTS:
            unsupported.append(f.name)
            continue
        hit = parse_name(f.stem, by_sku)
        if not hit:
            unmatched.append(f.name)
            continue
        info, order = hit
        key = (info["product"]["id"], info["color"])
        groups.setdefault(key, {"product": info["product"], "color": info["color"], "files": []})["files"].append((order, f.name, f))
    for g in groups.values():
        g["files"].sort(key=lambda x: (x[0], x[1].lower()))
    return groups, unmatched, unsupported


# ---------- báo cáo ----------
def report(path, res, catalog, dry):
    e = html.escape
    imgs = catalog.get("images", {})

    def has_img(p):
        return any(k == p["id"] or k.startswith(p["id"] + ":") for k in imgs if imgs[k])

    missing = sorted((p for p in catalog["products"] if not has_img(p)), key=lambda p: -sum(max(0, v["inventory_quantity"]) for v in p["variants"]))
    rows = "".join(f"<tr><td>{e(f)}</td><td>{e(n)}</td><td>{e(c) or '–'}</td><td>{e(s)}</td></tr>" for f, n, c, s in res["done"])
    miss = "".join(
        f"<tr><td>{e(p.get('display_title') or p['title'])}</td><td>{sum(max(0, v['inventory_quantity']) for v in p['variants'])}</td>"
        f"<td>{e(', '.join(sorted({str(v['sku']) for v in p['variants']})[:6]))}{' …' if len(p['variants']) > 6 else ''}</td></tr>" for p in missing)
    lst = lambda xs: "".join(f"<li>{e(x)}</li>" for x in xs) or "<li>Không có</li>"
    doc = f"""<!DOCTYPE html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Báo cáo nạp ảnh – SPORT 238</title><style>
:root{{--bg:#faf6f6;--sf:#fff;--ink:#1f1d1e;--mu:#6b6264;--ln:#ecdfe1;--ac:#a3122a;--bad:#b45309}}
@media(prefers-color-scheme:dark){{:root{{--bg:#151213;--sf:#1f1a1b;--ink:#f3eeee;--mu:#b3a8aa;--ln:#3a2b2e;--ac:#ff9aa6;--bad:#fbbf24}}}}
body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,sans-serif;padding:20px 16px}}main{{max-width:960px;margin:0 auto}}
h1{{margin:0 0 4px}}h2{{margin:26px 0 8px;font-size:18px}}.mu{{color:var(--mu)}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:16px 0}}.c{{background:var(--sf);border:1px solid var(--ln);border-radius:12px;padding:12px}}.c b{{display:block;font-size:26px;color:var(--ac)}}
.t{{overflow-x:auto;background:var(--sf);border:1px solid var(--ln);border-radius:12px}}table{{border-collapse:collapse;width:100%}}th,td{{text-align:left;padding:7px 10px;border-bottom:1px solid var(--ln);vertical-align:top}}
ul{{background:var(--sf);border:1px solid var(--ln);border-radius:12px;padding:10px 10px 10px 30px}}.warn{{color:var(--bad);font-weight:600}}</style></head><body><main>
<h1>Báo cáo nạp ảnh{' (xem trước, chưa tải lên)' if dry else ''}</h1><p class="mu">{e(res['when'])} · Thư mục: {e(res['folder'])}</p>
<div class="cards"><div class="c"><b>{len(res['done'])}</b>ảnh {'sẽ nạp' if dry else 'đã nạp'}</div><div class="c"><b>{res['skipped']}</b>ảnh đã có, bỏ qua</div>
<div class="c"><b>{len(res['unmatched'])}</b>tệp không khớp mã</div><div class="c"><b>{len(res['errors']) + len(res['unsupported'])}</b>tệp lỗi / không hỗ trợ</div><div class="c"><b>{len(missing)}</b>sản phẩm còn thiếu ảnh</div></div>
<h2>Ảnh {'sẽ nạp' if dry else 'đã nạp'}</h2><div class="t"><table><thead><tr><th>Tệp</th><th>Sản phẩm</th><th>Màu</th><th>Kích thước</th></tr></thead><tbody>{rows or '<tr><td colspan="4">Không có</td></tr>'}</tbody></table></div>
<h2>Tệp không khớp mã sản phẩm nào</h2><p class="mu">Đổi tên tệp đúng theo mã SKU trong Sapo (ví dụ PVN3939.jpg, PVN3939-1.jpg) rồi chạy lại.</p><ul>{lst(res['unmatched'])}</ul>
<h2>Tệp lỗi hoặc không hỗ trợ</h2><p class="mu">Chỉ nhận ảnh JPG, PNG, WEBP. Ảnh HEIC của iPhone: mở bằng máy tính rồi lưu lại dạng JPG.</p><ul>{lst(res['unsupported'] + [f'{a}: {b}' for a, b in res['errors']])}</ul>
<h2>Sản phẩm còn thiếu ảnh <span class="mu">(xếp theo tồn kho, nhiều trước)</span></h2><p class="mu">Cột "Mã" là các mã SKU dùng để đặt tên tệp ảnh.</p>
<div class="t"><table><thead><tr><th>Sản phẩm</th><th>Tồn</th><th>Mã</th></tr></thead><tbody>{miss or '<tr><td colspan="3">Tất cả sản phẩm đã có ảnh 🎉</td></tr>'}</tbody></table></div>
</main></body></html>"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(doc, encoding="utf-8")


# ---------- chạy ----------
def run(folder, server=None, password=None, dry=False, report_path=None, state_path=None, quiet=False):
    env = load_env()
    server = (server or env.get("SERVER_URL") or f"http://localhost:{env.get('PORT', '3000')}").rstrip("/")
    password = password if password is not None else env.get("ADMIN_PASSWORD", "")
    folder = pathlib.Path(folder)
    if not folder.is_dir():
        raise SystemExit(f"Không tìm thấy thư mục ảnh: {folder}")
    if not password:
        raise SystemExit("Thiếu ADMIN_PASSWORD (đặt trong tệp sport-shop-app/.env).")
    adm = Admin(server, password)
    try:
        adm.login()
    except urllib.error.HTTPError as e:
        raise SystemExit("Sai mật khẩu quản trị." if e.code == 401 else f"Đăng nhập thất bại (mã {e.code}).")
    except urllib.error.URLError:
        raise SystemExit(f"Không kết nối được trang quản trị tại {server}. Hãy bật trang quản trị (chay-quan-tri.bat) trước.")
    cat = adm.products()
    groups, unmatched, unsupported = plan(folder, cat)
    state_path = pathlib.Path(state_path) if state_path else APP / "data" / "anh-da-nap.json"
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        state = {}
    res = {"when": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"), "folder": str(folder), "done": [], "skipped": 0,
           "unmatched": unmatched, "unsupported": unsupported, "errors": []}
    for (pid, color), g in groups.items():
        key = f"{pid}:{color}" if color else pid
        current = list(cat.get("images", {}).get(key, []))
        added = []
        for _, name, f in g["files"]:
            try:
                raw = f.read_bytes()
                h = hashlib.sha256(raw).hexdigest()
                if state.get(h) in current + added:  # tệp này (hoặc bản giống hệt) đã nạp vào đúng chỗ rồi
                    res["skipped"] += 1
                    continue
                data, size = to_webp(f)
            except Exception:  # ảnh hỏng, không đọc được
                res["errors"].append((name, "không đọc được ảnh (tệp hỏng hoặc không phải ảnh)"))
                continue
            if not dry:
                url = adm.upload(data)
                state[h] = url
                added.append(url)
            res["done"].append((name, g["product"].get("display_title") or g["product"]["title"], color, f"{size[0]}×{size[1]}"))
        if added:
            adm.set_images(pid, color, current + added)
            cat.setdefault("images", {})[key] = current + added
    if not dry:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=0), encoding="utf-8")
    report_path = pathlib.Path(report_path) if report_path else APP / "bao-cao" / f"nap-anh-{datetime.datetime.now():%Y%m%d-%H%M%S}.html"
    report(report_path, res, cat, dry)
    if not quiet:
        print(f"{'Sẽ nạp' if dry else 'Đã nạp'} {len(res['done'])} ảnh; bỏ qua {res['skipped']} ảnh đã có; "
              f"{len(unmatched)} tệp không khớp mã; {len(unsupported) + len(res['errors'])} tệp lỗi/không hỗ trợ.")
        print(f"Báo cáo: {report_path}")
        if not dry and res["done"]:
            print("Nhớ xuất lại web (cap-nhat-web.bat) để ảnh lên trang bán hàng.")
    res["report"] = str(report_path)
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Nạp ảnh sản phẩm hàng loạt theo mã SKU")
    ap.add_argument("folder", help="thư mục chứa ảnh, tên tệp theo mã SKU")
    ap.add_argument("--dry-run", action="store_true", help="chỉ xem trước, không tải lên")
    ap.add_argument("--server", help="địa chỉ trang quản trị, mặc định http://localhost:3000")
    ap.add_argument("--report", help="nơi lưu báo cáo HTML")
    ap.add_argument("--open", action="store_true", help="mở báo cáo sau khi xong")
    a = ap.parse_args()
    r = run(a.folder, a.server, dry=a.dry_run, report_path=a.report)
    if a.open:
        webbrowser.open(pathlib.Path(r["report"]).resolve().as_uri())
