"""Kiểm thử công cụ nạp ảnh hàng loạt theo mã SKU (sport-shop-app/tools/nap_anh.py)."""
import io, json

from PIL import Image

import nap_anh
from conftest import admin_get, admin_post


def colors(p):
    out = []
    for v in p["variants"]:
        if v["option2"] not in out:
            out.append(v["option2"])
    return out


def img(path, size=(800, 600), color=(200, 30, 40), orientation=None, fmt=None):
    im = Image.new("RGB", size, color)
    kw = {}
    if orientation:
        ex = Image.Exif()
        ex[0x0112] = orientation
        kw["exif"] = ex
    im.save(path, fmt or path.suffix.lstrip(".").replace("jpg", "jpeg").upper(), **kw)


def pick(server):
    cat = admin_get(server, "/api/admin/products")
    multi = next(p for p in cat["products"] if len(colors(p)) > 1)
    single = next(p for p in cat["products"] if len(colors(p)) == 1)
    c1, c2 = colors(multi)[:2]
    v1 = next(v for v in multi["variants"] if v["option2"] == c1)
    v2 = next(v for v in multi["variants"] if v["option2"] == c2)
    return multi, single, c1, c2, v1["sku"], v2["sku"], single["variants"][0]["sku"]


def test_nap_anh_dung_san_pham_mau_giu_anh_cu(server, tmp_path):
    multi, single, c1, c2, sku1, sku2, sku_s = pick(server)
    admin_post(server, "/api/admin/images", {"product_id": single["id"], "color": "", "urls": ["https://example.com/anh-cu.jpg"]})
    d = tmp_path / "anh"
    d.mkdir()
    img(d / f"{sku1}.jpg", (3000, 2000), orientation=6)          # ảnh lớn, chụp xoay
    img(d / f"{sku1.lower()}-1.png", (500, 500), (10, 120, 200))   # chữ thường + ảnh phụ
    img(d / f"{sku1} (2).webp", (400, 300), (0, 0, 0), fmt="WEBP")
    img(d / f"{sku2}_1.jpg", (600, 600), (30, 160, 60))
    img(d / f"{sku_s}.jpeg", (900, 700), (90, 90, 90))
    (d / f"{sku1}-9.jpg").write_bytes((d / f"{sku1}.jpg").read_bytes())  # trùng nội dung với ảnh chính
    img(d / "KHONGCOMA123.jpg")
    (d / "ghi-chu.txt").write_text("x")
    (d / f"{sku2}.jpg").write_bytes(b"khong phai anh")
    state = tmp_path / "state.json"
    rep = tmp_path / "bc.html"

    r = nap_anh.run(d, server["url"], server["password"], report_path=rep, state_path=state, quiet=True)
    cat = admin_get(server, "/api/admin/products")
    im = cat["images"]
    a1, a2, s = im.get(f"{multi['id']}:{c1}", []), im.get(f"{multi['id']}:{c2}", []), im.get(single["id"], [])
    assert len(a1) == 3, a1                      # chính, -1, (2); bản trùng -9 bị bỏ
    assert len(a2) == 1                          # chỉ _1; tệp hỏng bị báo lỗi
    assert s[0] == "https://example.com/anh-cu.jpg" and len(s) == 2   # giữ ảnh cũ, thêm sau
    assert multi["id"] not in im                 # SP nhiều màu: ảnh theo màu, không có ảnh chung
    assert r["skipped"] == 1 and "KHONGCOMA123.jpg" in r["unmatched"] and "ghi-chu.txt" in r["unsupported"]
    assert [e[0] for e in r["errors"]] == [f"{sku2}.jpg"]

    # ảnh trên máy chủ là WebP, cạnh dài ≤ 1400, đã xoay đúng chiều (3000×2000 xoay 90° → dọc)
    up = server["data"] / "uploads" / a1[0].split("/")[-1]
    with Image.open(up) as w:
        assert w.format == "WEBP" and max(w.size) <= 1400 and w.size[1] > w.size[0]

    html = rep.read_text(encoding="utf-8")
    for t in ["Ảnh đã nạp", "Tệp không khớp mã", "Tệp lỗi hoặc không hỗ trợ", "Sản phẩm còn thiếu ảnh", "KHONGCOMA123.jpg"]:
        assert t in html

    # chạy lại: không nạp trùng
    r2 = nap_anh.run(d, server["url"], server["password"], report_path=rep, state_path=state, quiet=True)
    assert r2["done"] == [] and r2["skipped"] >= 5
    assert admin_get(server, "/api/admin/products")["images"][f"{multi['id']}:{c1}"] == a1


def test_xem_truoc_khong_tai_len(server, tmp_path):
    multi, single, c1, c2, sku1, sku2, sku_s = pick(server)
    d = tmp_path / "anh"
    d.mkdir()
    img(d / f"{sku_s}.jpg")
    r = nap_anh.run(d, server["url"], server["password"], dry=True, report_path=tmp_path / "bc.html", state_path=tmp_path / "s.json", quiet=True)
    assert len(r["done"]) == 1
    assert single["id"] not in admin_get(server, "/api/admin/products")["images"]
    assert not list((server["data"] / "uploads").iterdir())


def test_sai_mat_khau_bao_ro(server, tmp_path):
    (tmp_path / "anh").mkdir()
    try:
        nap_anh.run(tmp_path / "anh", server["url"], "sai", quiet=True, report_path=tmp_path / "b.html", state_path=tmp_path / "s.json")
    except SystemExit as e:
        assert "Sai mật khẩu" in str(e)
    else:
        raise AssertionError("phải báo sai mật khẩu")
