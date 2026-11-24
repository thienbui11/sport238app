"""Chụp các màn hình chính của cửa hàng (để so sánh trước–sau, D7).
Chạy:  py tests/chup_anh.py <địa chỉ web> <thư mục ra>
   vd: py tests/chup_anh.py http://localhost:3602 screenshots/after
Ảnh JPG nén (chất lượng 80); ảnh rộng hơn 1000 px được thu còn 3/4. Tên tệp cố định để trang screenshots/so-sanh.html dùng:
  01-trangchu-dt-{light,dark}   02-man-hinh-thu-2-dt-{light,dark}   03-luoi-sanpham-dt-{light,dark}   04-menu-dt-light
  05-tim-giay-khong-dau-dt-light   06-chitiet-dt-{light,dark}   07-giohang-dt-{light,dark}   08-bam-xoa-gio-dt-light
  09-trangchu-pc   10-luoi-pc   11-chitiet-pc   12-trangchu-pc-dark
(dt = điện thoại 390 px, pc = máy tính 1366 px; light/dark = chế độ sáng/tối)"""
import io, pathlib, sys
from PIL import Image
from playwright.sync_api import sync_playwright

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000").rstrip("/")
OUT = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "screenshots/after"); OUT.mkdir(parents=True, exist_ok=True)
MULTI = "PVN3632"   # giày nhiều loại + nhiều size
CART = "JSON.stringify([{id:'PVN3939',lb:'Size 39',qty:1},{id:'PVN3944',lb:'',qty:1}])"


def save(pg, name, **kw):
    im = Image.open(io.BytesIO(pg.screenshot(**kw))).convert("RGB")
    if im.width > 1000:
        im = im.resize((im.width * 3 // 4, im.height * 3 // 4), Image.LANCZOS)
    im.save(OUT / f"{name}.jpg", "JPEG", quality=80, optimize=True, progressive=True)
    print("  ", name)


def prep(pg):
    # ảnh tĩnh, không bắt dính giữa chừng một hiệu ứng
    pg.add_style_tag(content="html{scroll-behavior:auto!important}*{animation:none!important;transition:none!important}")


def home(pg):
    pg.goto(BASE + "/", wait_until="networkidle"); pg.wait_for_selector("#grid .card"); prep(pg); pg.wait_for_timeout(300)


def detail(pg):
    pg.goto(BASE + "/#p-" + MULTI); pg.wait_for_selector(".det h1"); prep(pg); pg.wait_for_timeout(300)


with sync_playwright() as pw:
    b = pw.chromium.launch()
    for theme in ["light", "dark"]:
        ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, device_scale_factor=2, color_scheme=theme, locale="vi-VN")
        pg = ctx.new_page(); t = "dt-" + theme
        home(pg); save(pg, f"01-trangchu-{t}")
        pg.evaluate("window.scrollBy(0, 844)"); pg.wait_for_timeout(200); save(pg, f"02-man-hinh-thu-2-{t}")
        pg.evaluate("document.querySelector('#grid .card').scrollIntoView({block:'start'});window.scrollBy(0,-90)"); pg.wait_for_timeout(200)
        save(pg, f"03-luoi-sanpham-{t}")
        if theme == "light":
            pg.evaluate("scrollTo(0,0)"); pg.click("#mb"); pg.wait_for_timeout(200); save(pg, "04-menu-dt-light"); pg.keyboard.press("Escape")
            pg.evaluate("document.getElementById('san-pham').scrollIntoView()"); pg.fill("#q", "giay"); pg.wait_for_timeout(250)
            pg.evaluate("document.getElementById('q').scrollIntoView({block:'start'});window.scrollBy(0,-90)"); pg.wait_for_timeout(150)
            save(pg, "05-tim-giay-khong-dau-dt-light"); pg.fill("#q", "")
        detail(pg)
        pg.evaluate("document.querySelector('.det h1').scrollIntoView({block:'start'});window.scrollBy(0,-100)"); pg.wait_for_timeout(150)
        save(pg, f"06-chitiet-{t}")
        pg.evaluate(f"localStorage.setItem('cart5',{CART})")   # giỏ có 2 món
        home(pg); pg.click("#cb"); pg.wait_for_timeout(400)
        save(pg, f"07-giohang-{t}")
        if theme == "light":
            pg.click("#cc"); pg.wait_for_timeout(250); save(pg, "08-bam-xoa-gio-dt-light")
        pg.evaluate("localStorage.removeItem('cart5')")
        ctx.close()
    for theme in ["light", "dark"]:
        ctx = b.new_context(viewport={"width": 1366, "height": 860}, color_scheme=theme, locale="vi-VN"); pg = ctx.new_page()
        home(pg)
        if theme == "dark":
            save(pg, "12-trangchu-pc-dark"); ctx.close(); continue
        save(pg, "09-trangchu-pc")
        pg.evaluate("document.querySelector('#grid .card').scrollIntoView({block:'start'});window.scrollBy(0,-260)"); pg.wait_for_timeout(200)
        save(pg, "10-luoi-pc")
        detail(pg); pg.evaluate("scrollTo(0,0)"); pg.wait_for_timeout(150); save(pg, "11-chitiet-pc")
        ctx.close()
    b.close()
print("xong:", OUT)
