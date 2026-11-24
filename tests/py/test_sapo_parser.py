"""Kiểm thử bộ đọc Excel Sapo bản Python (sport-shop-app/tools/sapo_xlsx_to_json.py)."""
import json, pathlib, shutil, subprocess, sys

import pytest

import sapo_xlsx_to_json as P

REAL = pathlib.Path.home() / "Downloads" / "danh_sach_san_pham_14.11.2026_7dcf063c851a56535e5688c4e0180807.xlsx"
TOOL = pathlib.Path(__file__).resolve().parents[2] / "sport-shop-app" / "tools" / "sapo_xlsx_to_json.py"


@pytest.mark.parametrize("name,ptype,sizes,cat", [
    ("Cúp iWin G1507", "Phụ kiện thể thao", [], P.CUP),
    ("Giày bóng đá Hunter", "Giày bóng đá", ["40"], P.SHOE),
    ("Giày Mira Lux 2.6 TF", "Giày bóng đá", [], P.SHOE),
    ("Giày thể thao CP-005", "Giày bóng đá", ["39"], P.SPORT_SHOE),
    ("Giày vải - Đế bằng", "Giày bóng đá", [], P.SPORT_SHOE),
    ("Giày vải", "", [], P.SPORT_SHOE),
    ("Quần áo HD 2026- MU - Mẫu Mới", "Quần áo bóng đá", ["S", "M"], P.CLUB),
    ("Quần áo AMAC- Blur", "Quần áo bóng đá", ["S", "M"], P.PLAIN),
    ("Quần áo Strivend", "Quần áo bóng đá", ["1", "3", "5"], P.KIDS),
    ("Túi rút", "Phụ kiện thể thao", [], P.ACC),
    ("Tất Dệt Kim IZI", "Phụ kiện thể thao", [], P.SOCK),
    ("Áo cầu lông vicky - Size M", "", ["M"], P.BAD),
    ("Bình sữa", "Đồ cho bé", [], None),          # đồ mẹ và bé bị loại
])
def test_phan_loai(name, ptype, sizes, cat):
    assert P.classify(name, ptype, sizes) == cat


def test_du_9_danh_muc():
    assert len(P.CATS) == 9 and "Giày thể thao" in P.CATS


@pytest.mark.parametrize("title,want", [
    ("Giày X - Size 42", ("Giày X", "42")),
    ("Giày Wika 41", ("Giày Wika", "41")),
    ("Quần áo Y- XL", ("Quần áo Y", "XL")),
    ("Quần áo Z - M - Đỏ", ("Quần áo Z - Đỏ", "M")),
    ("Quần áo không size", None),
])
def test_tach_size(title, want):
    assert P.split_size(title) == want


@pytest.mark.skipif(not REAL.exists(), reason="không có file Excel thật trên máy")
def test_file_that_ra_dung_moc_so_lieu(tmp_path):
    src = tmp_path / "sapo.xlsx"
    shutil.copy(REAL, src)                     # đọc bản chép, không đụng file thật
    out = tmp_path / "out.json"
    log = subprocess.run([sys.executable, str(TOOL), str(src), str(out)], capture_output=True, text=True, encoding="utf-8")
    assert log.returncode == 0, log.stderr
    d = json.loads(out.read_text(encoding="utf-8"))
    ps = d["products"]
    assert len(ps) == 175 and sum(len(p["variants"]) for p in ps) == 953
    _, dropped = P.build_catalog(str(src))
    assert dropped == 68                         # phiên bản giá bán lẻ = 0 bị bỏ
    import pandas as pd
    df = pd.read_excel(src)
    names = df[df.columns[[c.strip() for c in df.columns].index("Tên sản phẩm*")]].dropna().astype(str).str.strip()
    assert int((names != "").sum()) == 632       # số sản phẩm trong file (cả đồ mẹ và bé)
    assert sum(p["category"] == "Giày thể thao" for p in ps) == 3
    allowed_v = {"id", "sku", "option1", "option2", "price", "inventory_quantity"}
    for p in ps:
        assert set(p["variants"][0]) <= allowed_v       # không có giá nhập, giá vốn, giá buôn
        assert all(v["price"] > 0 and v["inventory_quantity"] >= 0 for v in p["variants"])
    text = out.read_text(encoding="utf-8").lower()
    for bad in ["giá nhập", "giá vốn", "giá buôn", "cost"]:
        assert bad not in text
    seed = json.loads((TOOL.parents[1] / "data" / "seed-products.json").read_text(encoding="utf-8"))
    assert seed["products"] == ps                # dữ liệu mẫu đúng bằng kết quả bộ đọc
