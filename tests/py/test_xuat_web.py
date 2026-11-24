"""Kiểm thử bước xuất web của nút cập nhật hằng ngày: Next.js là bản chính, lỗi thì tự dùng bản HTML dự phòng."""
import json

import pytest

import daily_update
import export_next


def test_luon_dung_html_khi_dat_xuat_web_html(server, tmp_path):
    out, kind = daily_update.xuat_web({"XUAT_WEB": "html"}, server["url"], "24/11/2026", out=str(tmp_path / "dist"))
    assert kind == "HTML" and (out / "index.html").exists() and not (out / "san-pham").exists()


def test_next_loi_thi_dung_html(server, tmp_path, monkeypatch):
    def hong(*a, **k):
        raise SystemExit("Build Next.js thất bại: giả lập mất mạng")
    monkeypatch.setattr(export_next, "available", lambda: True)
    monkeypatch.setattr(export_next, "export", hong)
    out, kind = daily_update.xuat_web({}, server["url"], "24/11/2026", out=str(tmp_path / "dist"))
    assert kind == "HTML" and (out / "products.json").exists()


@pytest.mark.skipif(not export_next.available(), reason="chưa cài thư viện Next.js")
def test_next_la_ban_chinh(server, tmp_path):
    out, kind = daily_update.xuat_web({"SITE_URL": "https://vidu.vn"}, server["url"], "24/11/2026", out=str(tmp_path / "dist"))
    assert kind == "Next.js"
    assert (out / "san-pham").is_dir() and not (out / "admin").exists()
    d = json.loads((out / "products.json").read_text(encoding="utf-8"))
    assert d["updated"] == "24/11/2026" and len(d["products"]) == len(list((out / "san-pham").iterdir()))
    assert "https://vidu.vn/sitemap.xml" in (out / "robots.txt").read_text(encoding="utf-8")
