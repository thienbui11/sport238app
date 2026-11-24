#!/usr/bin/env python3
"""Xuất WEB TĨNH bằng bản Next.js (sport-shop-next/frontend): mỗi sản phẩm có trang riêng /san-pham/<MÃ>/
(tiêu đề, mô tả, ảnh khi chia sẻ Zalo/Facebook, dữ liệu cho Google), kèm sitemap.xml khi có địa chỉ web thật.

Dữ liệu lấy lúc build từ trang quản trị đang chạy (giống export_static.py), nên KHÔNG bao giờ có giá nhập, giá vốn.
Cách dùng:  python tools/export_next.py [--server http://localhost:3000] [--out dist] [--site-url https://ten-mien.vn] [--updated 24/11/2026]
Cần: Node.js và thư mục sport-shop-next/frontend/node_modules (chạy "npm install" một lần trong thư mục đó).
Lần build cần mạng để tải phông chữ Be Vietnam Pro; mất mạng thì công cụ báo lỗi (cập nhật hằng ngày sẽ tự dùng bản HTML dự phòng)."""
import argparse, datetime, json, os, pathlib, shutil, subprocess, sys, urllib.request

APP = pathlib.Path(__file__).resolve().parent.parent
FRONT = APP.parent / "sport-shop-next" / "frontend"
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from export_static import HEADERS  # noqa: E402

PUBLIC_VARIANT_KEYS = {"id", "sku", "option1", "option2", "price", "inventory_quantity"}


def available():
    """Có đủ điều kiện để xuất bằng Next.js không (đã cài thư viện)."""
    return (FRONT / "node_modules" / "next").is_dir() and shutil.which("npm") is not None


def check_public(products_json):
    """Chặn lộ dữ liệu nội bộ: mỗi phiên bản chỉ được có các trường công khai."""
    d = json.loads(products_json.read_text(encoding="utf-8"))
    for p in d.get("products", []):
        for v in p.get("variants", []):
            extra = set(v) - PUBLIC_VARIANT_KEYS
            if extra:
                raise SystemExit(f"products.json có trường không được công khai: {sorted(extra)}")
    low = products_json.read_text(encoding="utf-8").lower()
    for bad in ("giá nhập", "giá vốn", "giá buôn", "cost_price", "costprice"):
        if bad in low:
            raise SystemExit(f"products.json có chữ '{bad}', dừng xuất web")
    return d


def export(server="http://localhost:3000", out="dist", site_url="", updated=None, quiet=False):
    server = server.rstrip("/")
    out = pathlib.Path(out) if pathlib.Path(out).is_absolute() else APP / out
    if not available():
        raise SystemExit("Chưa cài thư viện cho bản Next.js: mở sport-shop-next/frontend và chạy 'npm install'.")
    with urllib.request.urlopen(server + "/api/products", timeout=30) as r:
        if not json.load(r).get("products"):
            raise SystemExit("Không có sản phẩm nào để xuất. Hãy nhập dữ liệu từ Sapo vào trang quản trị trước.")
    env = dict(os.environ, XUAT_TINH="1", API_URL=server, SITE_URL=(site_url or "").rstrip("/"),
               CAP_NHAT_NGAY=updated or datetime.date.today().strftime("%d/%m/%Y"), NEXT_TELEMETRY_DISABLED="1")
    shutil.rmtree(FRONT / ".next", ignore_errors=True)   # tránh lẫn bản build cũ
    shutil.rmtree(FRONT / "out", ignore_errors=True)
    t = datetime.datetime.now()
    r = subprocess.run("npm run build", cwd=FRONT, env=env, shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise SystemExit("Build Next.js thất bại:\n" + (r.stdout + r.stderr)[-3000:])
    src = FRONT / "out"
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(src, out)
    shutil.rmtree(out / "admin", ignore_errors=True)       # trang quản trị KHÔNG đưa lên mạng
    data = check_public(out / "products.json")
    (out / "_headers").write_text(HEADERS + "/_next/static/*\n  Cache-Control: public, max-age=31536000, immutable\n", encoding="utf-8")
    # chép ảnh sản phẩm đang dùng
    up_src = pathlib.Path(os.environ.get("DATA_DIR") or APP / "data") / "uploads"
    (out / "uploads").mkdir(exist_ok=True)
    n_img = 0
    for urls in data.get("images", {}).values():
        for u in urls:
            f = up_src / u[len("/uploads/"):] if u.startswith("/uploads/") else None
            if f and f.is_file():
                shutil.copy(f, out / "uploads" / f.name)
                n_img += 1
    if not quiet:
        size = sum(p.stat().st_size for p in out.rglob("*") if p.is_file())
        print(f"Đã xuất web tĩnh (Next.js) vào {out}: {len(data['products'])} sản phẩm, {n_img} ảnh, "
              f"{size / 1024 / 1024:.1f} MB, build {(datetime.datetime.now() - t).seconds} giây.")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", default="http://localhost:3000"); ap.add_argument("--out", default="dist")
    ap.add_argument("--site-url", default=""); ap.add_argument("--updated", default=None)
    a = ap.parse_args()
    export(a.server, a.out, a.site_url, a.updated)
