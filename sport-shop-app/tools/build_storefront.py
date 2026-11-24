#!/usr/bin/env python3
"""Dựng lại public/index.html (cửa hàng một tệp) từ: tools/storefront.template.html + CSS dùng chung + logo.
CSS dùng chung nằm ở sport-shop-next/frontend/app/globals.css (cả bản Next.js lẫn bản này cùng dùng một CSS).
Cách dùng:  python sport-shop-app/tools/build_storefront.py     (cần: pip install pillow)"""
import base64, io, pathlib
from PIL import Image

APP = pathlib.Path(__file__).resolve().parent.parent
CSS = APP.parent / "sport-shop-next" / "frontend" / "app" / "globals.css"
logo = Image.open(APP / "public" / "logo.png")


def data_uri(px):
    b = io.BytesIO(); logo.resize((px, px), Image.LANCZOS).save(b, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()


html = (APP / "tools" / "storefront.template.html").read_text(encoding="utf-8")
html = (html.replace("/*CSS*/", CSS.read_text(encoding="utf-8")).replace("/*LOGO48*/", data_uri(48))
        .replace("/*LOGO96*/", data_uri(96)).replace("/*LOGO200*/", data_uri(200)))
(APP / "public" / "index.html").write_text(html, encoding="utf-8")
print(f"Đã dựng public/index.html ({len(html)//1024} KB)")
