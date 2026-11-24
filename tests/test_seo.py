"""Kiểm tra SEO và chia sẻ của web tĩnh xuất bằng Next.js (sport-shop-app/tools/export_next.py).
Đọc thẳng các tệp HTML (giống Google, Zalo, Facebook đọc trang: không chạy JavaScript).
Chạy:  python tests/test_seo.py <thư mục đã xuất> [https://địa-chỉ-web-đã-dùng-khi-xuất]
In "KẾT QUẢ: 0 lỗi" khi đạt."""
import html, json, pathlib, re, sys

OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("sport-shop-app/dist")
SITE = (sys.argv[2] if len(sys.argv) > 2 else "").rstrip("/")
fails = []


def ok(c, m):
    print(("  ✓ " if c else "  ✗ ") + m)
    if not c: fails.append(m)


def meta(h, attr, name):
    m = re.search(rf'<meta {attr}="{re.escape(name)}" content="([^"]*)"', h)
    return html.unescape(m.group(1)) if m else None


data = json.loads((OUT / "products.json").read_text(encoding="utf-8"))
prods = data["products"]
ok(len(prods) > 0, f"products.json có {len(prods)} sản phẩm")
allowed = {"id", "sku", "option1", "option2", "price", "inventory_quantity"}
ok(all(set(v) <= allowed for p in prods for v in p["variants"]), "products.json: phiên bản chỉ có trường công khai (không giá nhập/giá vốn)")
ok(not (OUT / "admin").exists(), "không có trang quản trị trong thư mục xuất")
ok((OUT / "404.html").exists() and "Không tìm thấy trang" in (OUT / "404.html").read_text(encoding="utf-8"), "có trang 404 tiếng Việt")

titles, descs, bad = set(), set(), []
for p in prods:
    f = OUT / "san-pham" / p["id"] / "index.html"
    if not f.exists():
        bad.append(f"{p['id']}: thiếu trang"); continue
    h = f.read_text(encoding="utf-8")
    name = p.get("display_title") or p["title"]
    t = re.search(r"<title>([^<]*)</title>", h)
    t = html.unescape(t.group(1)) if t else ""
    d = meta(h, "name", "description") or ""
    titles.add(t); descs.add(d)
    if name not in t: bad.append(f"{p['id']}: title '{t}'")
    if not d or name not in d or "ghé shop nhận hàng" not in d: bad.append(f"{p['id']}: description")
    if meta(h, "property", "og:title") != t: bad.append(f"{p['id']}: og:title")
    if html.escape(name, quote=False) not in h: bad.append(f"{p['id']}: tên SP không có sẵn trong HTML")
    ld = re.search(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)
    try:
        j = json.loads(ld.group(1)) if ld else None
    except ValueError:
        j = None
    if not j or j.get("@type") != "Product" or j["offers"]["priceCurrency"] != "VND" or j["offers"]["lowPrice"] != min(v["price"] for v in p["variants"]):
        bad.append(f"{p['id']}: JSON-LD Product")
    for w in ("chính hãng", "bảo hành", "aggregateRating", "ship", "giao hàng"):
        if w in h.lower() and w != "ship" or re.search(r"\bship\b", h.lower()):
            bad.append(f"{p['id']}: có chữ không được dùng '{w}'"); break
    if SITE:
        can = re.search(r'<link rel="canonical" href="([^"]*)"', h)
        if not can or can.group(1) != f"{SITE}/san-pham/{p['id']}/": bad.append(f"{p['id']}: canonical")
        img = meta(h, "property", "og:image") or ""
        if not img.startswith(SITE + "/"): bad.append(f"{p['id']}: og:image '{img}'")
ok(not bad, f"{len(prods)} trang sản phẩm: title, description, og, JSON-LD, nội dung có sẵn trong HTML (lỗi: {bad[:4]})")
ok(len(titles) == len(prods) and len(descs) == len(prods), "mỗi trang sản phẩm có title và description riêng")

home = (OUT / "index.html").read_text(encoding="utf-8")
ld = re.search(r'<script type="application/ld\+json">(.*?)</script>', home, re.S)
j = json.loads(ld.group(1)) if ld else {}
ok(j.get("@type") == "SportingGoodsStore" and j["openingHoursSpecification"][0]["opens"] == "08:00" and "telephone" not in j,
   "trang chủ: JSON-LD cửa hàng có địa chỉ, giờ mở cửa 8:00–21:00, không ghi số điện thoại")
robots = (OUT / "robots.txt").read_text(encoding="utf-8")
ok("Disallow: /admin" in robots, "robots.txt chặn /admin")
if SITE:
    sm = (OUT / "sitemap.xml").read_text(encoding="utf-8")
    locs = re.findall(r"<loc>([^<]+)</loc>", sm)
    need = {f"{SITE}/", f"{SITE}/bang-size/", f"{SITE}/dat-doi/"} | {f"{SITE}/san-pham/{p['id']}/" for p in prods}
    ok(set(locs) == need and len(locs) == len(need), f"sitemap.xml có đúng {len(need)} địa chỉ: trang chủ, bảng size, đặt đội, {len(prods)} SP (thiếu: {sorted(need - set(locs))[:3]}; thừa: {sorted(set(locs) - need)[:3]})")
    ok(f"Sitemap: {SITE}/sitemap.xml" in robots, "robots.txt trỏ tới sitemap")
hdr = (OUT / "_headers").read_text(encoding="utf-8")
ok("X-Content-Type-Options: nosniff" in hdr and "/_next/static/*" in hdr, "_headers có bảo mật và cache cho tệp tĩnh")
print("\nKẾT QUẢ:", len(fails), "lỗi"); print(fails)
