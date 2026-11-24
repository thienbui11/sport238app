"""Kiểm thử máy chủ quản trị Node: lỗi L14 (đường dẫn lỗi mã hóa), L17 (nhận nhầm tệp Excel)."""
import json, urllib.error, urllib.request

from playwright.sync_api import sync_playwright


def status(url, **kw):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, **kw)) as r:
            return r.status, json.load(r) if "json" in r.headers.get("Content-Type", "") else None
    except urllib.error.HTTPError as e:
        return e.code, json.load(e)


def test_l14_duong_dan_loi_ma_hoa_tra_400(server):
    assert status(server["url"] + "/%E0")[0] == 400
    assert status(server["url"] + "/api/%E0%A4%A")[0] == 400
    assert status(server["url"] + "/")[0] == 200


def test_l17_tep_excel_bao_ro_tren_trang_quan_tri(server):
    code, body = status(server["url"] + "/api/admin/import", data=b"--x\r\n", method="POST",
                        headers={"Content-Type": "multipart/form-data; boundary=x"})
    assert code in (401, 415)   # chưa đăng nhập thì 401
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        pg.goto(server["url"] + "/admin")
        pg.fill("#pw", server["password"])
        pg.click("#lb")
        pg.wait_for_selector("#app:not([hidden])")
        pg.click("[data-t=t2]")
        pg.set_input_files("#imp", files=[{"name": "danh_sach.xlsx", "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "buffer": b"PK\x03\x04 gia"}])
        pg.wait_for_function("document.querySelector('#im').textContent.length>20")
        msg = pg.inner_text("#im")
        # tệp JSON hợp lệ vẫn nhập được như cũ
        pg.set_input_files("#imp", files=[{"name": "sp.json", "mimeType": "application/json",
                                           "buffer": json.dumps({"products": [{"id": "T1", "title": "Áo thử", "variants": [{"id": "T1", "option1": "M", "option2": "Đỏ", "price": 100000, "inventory_quantity": 2}]}]}).encode()}])
        pg.wait_for_function("document.querySelector('#im').textContent.startsWith('Xong')")
        b.close()
    assert "chưa đọc trực tiếp file Excel" in msg and "cap-nhat-web.bat" in msg, msg
