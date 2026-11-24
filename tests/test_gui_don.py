"""Kiểm thử yêu cầu 24/11 tối (chỉ bản Next.js; khẩu hiệu kiểm thêm bản HTML nếu truyền địa chỉ máy chủ Node):
- Khẩu hiệu "Áo bóng đá đẹp, chọn size vừa ý, đặt ngay tại Sport 238!" ở tiêu đề lớn trang chủ.
- Thứ tự danh mục: quần áo, giày trước "Cờ, Cúp, Huy Chương" (ô danh mục và nút lọc).
- Lọc giá luôn hiện (cả điện thoại, không cần mở "Lọc thêm"), kết quả đúng theo products.json.
- Gửi đơn không cần dán: Messenger điền sẵn (m.me/...?text=đúng nội dung đơn), giỏ, hỏi shop, đặt đội;
  điện thoại có nút Chia sẻ của máy → chữ đơn điền sẵn (không ảnh thì chỉ gửi chữ); máy tính không có nút này.
Chạy:  py tests/test_gui_don.py http://localhost:3602 [http://localhost:3000]      (in "KẾT QUẢ: N lỗi")"""
import json, sys, urllib.parse, urllib.request
from playwright.sync_api import sync_playwright

B = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3602").rstrip("/")
NODE = sys.argv[2].rstrip("/") if len(sys.argv) > 2 else ""
SLOGAN = "Áo bóng đá đẹp, chọn size vừa ý, đặt ngay tại Sport 238!"
ORDER = ["Quần áo CLB/Đội tuyển", "Quần áo không logo", "Quần áo trẻ em", "Giày bóng đá", "Giày thể thao",
         "Cờ, Cúp, Huy Chương", "Phụ kiện thể thao", "Vớ/tất ống đồng", "Cầu lông"]
prods = json.load(urllib.request.urlopen(B + "/products.json"))["products"]
fails, errs = [], []
MOCK = """window.__sh=null;
Object.defineProperty(navigator,'canShare',{value:(d)=>!!d,configurable:true});
Object.defineProperty(navigator,'share',{value:(d)=>{window.__sh={text:d.text,files:(d.files||[]).length};return Promise.resolve()},configurable:true});"""


def ok(c, m):
    print(("  ✓ " if c else "  ✗ ") + m)
    if not c: fails.append(m)


def text_of(href):
    q = urllib.parse.urlparse(href).query
    return urllib.parse.parse_qs(q).get("text", [""])[0]


def instock(p): return [v for v in p["variants"] if v["inventory_quantity"] > 0]


one = next(p for p in prods if p["category"] == "Phụ kiện thể thao" and len(p["variants"]) == 1 and instock(p))

with sync_playwright() as pw:
    b = pw.chromium.launch()
    print("\n===== Khẩu hiệu, thứ tự danh mục =====")
    ctx = b.new_context(viewport={"width": 1366, "height": 860}, permissions=["clipboard-read", "clipboard-write"])
    ctx.route("https://m.me/**", lambda r: r.fulfill(body="messenger")); ctx.route("https://zalo.me/**", lambda r: r.fulfill(body="zalo"))
    pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(B + "/"); pg.wait_for_selector("#grid .card")
    ok(pg.inner_text("h1").strip() == SLOGAN, f"tiêu đề lớn là khẩu hiệu mới ({pg.inner_text('h1')!r})")
    ok("ghé shop nhận hàng" in pg.inner_text(".hero"), "phần mở đầu vẫn ghi 'ghé shop nhận hàng'")
    tiles = pg.eval_on_selector_all(".cat[data-go]", "e=>e.map(x=>x.dataset.go)")
    ok(tiles == ORDER, f"ô danh mục: quần áo, giày trước Cờ cúp ({tiles[:6]})")
    chips = pg.eval_on_selector_all(".chips [data-c]", "e=>e.map(x=>x.dataset.c)")
    ok(chips == ["Tất cả"] + ORDER, "nút lọc danh mục cùng thứ tự")

    print("\n===== Máy tính: Messenger điền sẵn =====")
    v = instock(one)[0]
    pg.evaluate("id=>localStorage.setItem('cart5',JSON.stringify([{id,lb:'',qty:2}]))", v["id"])
    pg.reload(); pg.wait_for_selector("#grid .card"); pg.click("#cb"); pg.wait_for_timeout(400)
    txt = pg.input_value("#ordtxt"); href = pg.get_attribute("#fs", "href") or ""
    ok(href.startswith("https://m.me/Sport238?text=") and text_of(href) == txt, "nút Messenger mang sẵn đúng nội dung đơn (m.me/…?text=)")
    ok("điền sẵn" in pg.inner_text("#fs"), "nút ghi rõ 'đơn điền sẵn'")
    ok(pg.locator("#shareimg").count() == 0, "máy tính không có nút Chia sẻ của máy")
    with ctx.expect_page() as pi: pg.click("#fs")
    m = pi.value; m.wait_for_load_state("commit"); pg.wait_for_timeout(300)
    ok(text_of(m.url) == txt and pg.evaluate("navigator.clipboard.readText()").replace("\r\n", "\n") == txt, "mở Messenger có đơn điền sẵn, đơn vẫn được sao chép phòng khi khung chat trống")
    ok("bấm Gửi" in pg.inner_text("#cpok"), "hướng dẫn: Messenger đã điền sẵn, chỉ cần bấm Gửi")
    m.close()
    pg.evaluate("localStorage.removeItem('cart5')"); pg.reload(); pg.wait_for_selector("#grid .card")
    ok(pg.get_attribute("#fs", "href") == "https://m.me/Sport238", "giỏ trống: link Messenger bình thường")

    print("\n===== Hỏi shop, đặt đội: Messenger điền sẵn =====")
    pg.goto(f"{B}/san-pham/{one['id']}/"); pg.wait_for_selector("#askm"); pg.wait_for_timeout(300)
    q = text_of(pg.get_attribute("#askm", "href") or "")
    ok((one.get("display_title") or one["title"]) in q and one["id"] in q and f"/san-pham/{one['id']}" in q, "Hỏi qua Messenger: điền sẵn câu hỏi có tên, mã, link sản phẩm")
    kit = next(p for p in prods if p["category"] == "Quần áo không logo" and any(x["option1"] and x["inventory_quantity"] > 0 for x in p["variants"]))
    pg.goto(B + "/dat-doi/"); pg.wait_for_selector("#tm-sp"); pg.select_option("#tm-sp", kit["id"]); pg.wait_for_selector("[data-tq]")
    pg.locator("[data-tq]").first.fill("5"); pg.wait_for_timeout(150)
    ok(text_of(pg.get_attribute("#tm-mess", "href") or "") == pg.input_value("#tm-msg"), "Đặt đội: Messenger điền sẵn đúng tin nhắn đặt đội")
    ctx.close()

    for scheme in ("light", "dark"):
        print(f"\n===== Điện thoại 390 px – {'tối' if scheme == 'dark' else 'sáng'} =====")
        ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, color_scheme=scheme, permissions=["clipboard-read", "clipboard-write"])
        pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); pg.add_init_script(MOCK)
        pg.goto(B + "/"); pg.wait_for_selector("#grid .card")
        ok(pg.is_visible("#fgia") and pg.locator("#fpanel").is_hidden(), "lọc giá hiện sẵn trên điện thoại (không cần mở Lọc thêm)")
        pg.select_option("#fgia", "duoi-100"); pg.wait_for_timeout(200)
        while pg.is_visible("#moreb"): pg.click("#moreb"); pg.wait_for_timeout(100)
        ids = pg.eval_on_selector_all("#grid .card", "e=>e.map(x=>x.dataset.pid)")
        want = [p["id"] for p in prods if min(x["price"] for x in p["variants"]) < 100_000]
        ok(sorted(ids) == sorted(want) and len(ids) > 0, f"lọc 'Dưới 100.000đ': đúng {len(want)} sản phẩm theo giá thấp nhất")
        ok("giá dưới 100.000đ" in pg.inner_text("#cnt"), "dòng đếm ghi rõ đang lọc giá")
        ok(pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth"), "không tràn ngang")
        pg.select_option("#fgia", "")
        pg.evaluate("id=>localStorage.setItem('cart5',JSON.stringify([{id,lb:'',qty:1}]))", v["id"])
        pg.reload(); pg.wait_for_selector("#grid .card"); pg.click("#bc"); pg.wait_for_timeout(400)
        ok(pg.is_visible("#shareimg") and "điền sẵn" in pg.inner_text("#shareimg"), "điện thoại: có nút 'Gửi đơn qua Zalo, Messenger… (điền sẵn)'")
        h = pg.evaluate("(()=>{const r=document.getElementById('shareimg').getBoundingClientRect();return r.height})()")
        ok(h >= 44, f"nút đủ lớn ({h:.0f} px)")
        pg.click("#shareimg"); pg.wait_for_timeout(400)
        sh = pg.evaluate("window.__sh")
        ok(bool(sh) and sh["text"] == pg.input_value("#ordtxt") and sh["files"] == 0, "bấm: bảng chia sẻ nhận đúng chữ đơn (chưa có ảnh nên chỉ gửi chữ)")
        ok("điền sẵn" in pg.inner_text("#cpok"), "hướng dẫn: đơn đã điền sẵn, chọn shop rồi Gửi")
        ctx.close()

    if NODE:
        print("\n===== Bản HTML dự phòng (máy chủ Node) =====")
        ctx = b.new_context(); pg = ctx.new_page()
        pg.goto(NODE + "/"); pg.wait_for_selector("#grid .card")
        ok(" ".join(pg.inner_text("h1").split()) .replace(" ,", ",") == SLOGAN, f"bản HTML: khẩu hiệu mới ({pg.inner_text('h1')!r})")
        tiles = pg.eval_on_selector_all(".cat[data-go]", "e=>e.map(x=>x.dataset.go)")
        ok(tiles == ORDER, "bản HTML: thứ tự danh mục mới")
        ctx.close()
    b.close()

print("\nLỖI JS:", errs[:3]); print("KẾT QUẢ:", len(fails) + len(errs), "lỗi"); print(fails)
