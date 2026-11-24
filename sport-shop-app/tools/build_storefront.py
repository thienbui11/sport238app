#!/usr/bin/env python3
"""Dựng lại public/index.html (cửa hàng một tệp) từ: tools/storefront.template.html + CSS riêng (tools/storefront.css) + logo.
CSS riêng của bản dự phòng: tools/storefront.css (chốt từ globals.css ngày 24/11/2026).
Cách dùng:  python sport-shop-app/tools/build_storefront.py     (cần: pip install pillow)"""
import base64, io, pathlib
from PIL import Image

APP = pathlib.Path(__file__).resolve().parent.parent
# Bản HTML là bản DỰ PHÒNG (giao diện chính là Next.js): dùng CSS riêng đã chốt, không theo globals.css của Next nữa
CSS = APP / "tools" / "storefront.css"
logo = Image.open(APP / "public" / "logo.png")


def data_uri(px):
    b = io.BytesIO(); logo.resize((px, px), Image.LANCZOS).save(b, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()


html = (APP / "tools" / "storefront.template.html").read_text(encoding="utf-8")
html = (html.replace("/*CSS*/", CSS.read_text(encoding="utf-8")).replace("/*LOGO48*/", data_uri(48))
        .replace("/*LOGO96*/", data_uri(96)).replace("/*LOGO200*/", data_uri(200)))
(APP / "public" / "index.html").write_text(html, encoding="utf-8")
print(f"Đã dựng public/index.html ({len(html)//1024} KB)")
