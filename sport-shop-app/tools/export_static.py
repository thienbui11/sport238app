#!/usr/bin/env python3
"""Xuất WEB TĨNH (thư mục dist/) từ trang quản trị đang chạy. Thư mục dist đưa lên hosting là xong, không cần backend.

Cách dùng:  python tools/export_static.py [--server http://localhost:3000] [--out dist] [--site-url https://ten-mien.vn] [--updated 14/11/2026]
Chỉ dùng thư viện có sẵn của Python.

dist/ gồm: index.html, products.json, config.json, logo.png, uploads/ (ảnh sản phẩm), _headers, robots.txt
Dữ liệu lấy qua API công khai của trang quản trị nên không bao giờ có giá nhập, giá vốn hay giá buôn."""
import argparse, datetime, json, pathlib, shutil, sys, urllib.request

APP = pathlib.Path(__file__).resolve().parent.parent
HEADERS = """/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
/products.json
  Cache-Control: public, max-age=300
/config.json
  Cache-Control: public, max-age=300
/logo.png
  Cache-Control: public, max-age=86400
/uploads/*
  Cache-Control: public, max-age=31536000, immutable
"""


def fetch_json(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)


def export(server="http://localhost:3000", out="dist", site_url="", updated=None, quiet=False):
    server = server.rstrip("/")
    out = pathlib.Path(out) if pathlib.Path(out).is_absolute() else APP / out
    products = fetch_json(server + "/api/products")
    config = fetch_json(server + "/api/config")
    if not products.get("products"):
        raise SystemExit("Không có sản phẩm nào để xuất. Hãy nhập dữ liệu từ Sapo vào trang quản trị trước.")
    products["updated"] = updated or datetime.date.today().strftime("%d/%m/%Y")

    html = (APP / "public" / "index.html").read_text(encoding="utf-8")
    for old, new in [('get("/api/config")', 'get("config.json")'), ('get("/api/products")', 'get("products.json?v=%d")' % int(datetime.datetime.now().timestamp()))]:
        if html.count(old) != 1:
            raise SystemExit(f"index.html không có đoạn {old}, không xuất được")
        html = html.replace(old, new)
    extra = ""
    if site_url:
        u = site_url.rstrip("/")
        extra = f'<meta property="og:url" content="{u}/"><meta property="og:image" content="{u}/logo.png">'
    html = html.replace("<!--OG_EXTRA-->", extra)

    if out.exists():
        shutil.rmtree(out)
    (out / "uploads").mkdir(parents=True)
    (out / "index.html").write_text(html, encoding="utf-8")
    (out / "products.json").write_text(json.dumps(products, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (out / "config.json").write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")
    shutil.copy(APP / "public" / "logo.png", out / "logo.png")
    (out / "_headers").write_text(HEADERS, encoding="utf-8")
    robots = "User-agent: *\nAllow: /\n" + (f"Sitemap: {site_url.rstrip('/')}/sitemap.xml\n" if site_url else "")
    (out / "robots.txt").write_text(robots, encoding="utf-8")
    if site_url:
        (out / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{site_url.rstrip("/")}/</loc></url></urlset>', encoding="utf-8")

    # chỉ chép những ảnh đang được dùng
    n_img, big = 0, []
    src_up = APP / "data" / "uploads"
    for urls in products.get("images", {}).values():
        for u in urls:
            if u.startswith("/uploads/") and (src_up / u[len("/uploads/"):]).is_file():
                f = src_up / u[len("/uploads/"):]
                shutil.copy(f, out / "uploads" / f.name); n_img += 1
                if f.stat().st_size > 600_000: big.append(f.name)
    if not quiet:
        size = sum(p.stat().st_size for p in out.rglob("*") if p.is_file())
        print(f"Đã xuất web tĩnh vào {out}: {len(products['products'])} sản phẩm, {n_img} ảnh, {size/1024/1024:.1f} MB. Tồn kho ghi ngày {products['updated']}.")
        if big:
            print(f"⚠ {len(big)} ảnh lớn hơn 600KB (web sẽ tải chậm trên điện thoại). Tải ảnh qua trang quản trị sẽ tự thu nhỏ.")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", default="http://localhost:3000"); ap.add_argument("--out", default="dist")
    ap.add_argument("--site-url", default=""); ap.add_argument("--updated", default=None)
    a = ap.parse_args()
    export(a.server, a.out, a.site_url, a.updated)
