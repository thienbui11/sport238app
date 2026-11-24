"""Kiểm thử lọc theo size còn hàng, giá, hãng (A6) và Yêu thích (C1) – chỉ bản Next.js.
Số lượng mong đợi tính độc lập từ products.json, so với lưới sản phẩm trên trình duyệt thật.
Chạy:  py tests/test_loc.py http://localhost:3602      (in "KẾT QUẢ: N lỗi")"""
import json, pathlib, sys, urllib.request
from playwright.sync_api import sync_playwright

B = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3602").rstrip("/")
AXE = pathlib.Path(__file__).resolve().parent / "node_modules" / "axe-core" / "axe.min.js"
prods = json.load(urllib.request.urlopen(B + "/products.json"))["products"]
fails, errs = [], []
RANGES = {"duoi-100": (0, 99_999), "100-150": (100_000, 149_999), "150-200": (150_000, 199_999), "200-400": (200_000, 399_999), "tren-400": (400_000, 10**12)}


def ok(c, m):
    print(("  ✓ " if c else "  ✗ ") + m)
    if not c: fails.append(m)


def show_all(pg):
    while pg.locator("#more").is_visible(): pg.click("#more button"); pg.wait_for_timeout(40)


def ids(pg):
    show_all(pg); return set(pg.eval_on_selector_all("#grid .card", "e=>e.map(x=>x.dataset.pid)"))


def want(size="", price="", brand="", cat=None):
    lo, hi = RANGES.get(price, (None, None))
    return {p["id"] for p in prods
            if (not cat or p["category"] == cat)
            and (not size or any(v["option1"] == size and v["inventory_quantity"] > 0 for v in p["variants"]))
            and (not price or any(lo <= v["price"] <= hi for v in p["variants"]))
            and (not brand or (p.get("vendor") or "") == brand)}


def axe(pg, where):
    if not AXE.exists(): return
    pg.add_script_tag(path=str(AXE))
    v = pg.evaluate("async()=>(await axe.run(document,{resultTypes:['violations']})).violations.filter(x=>['critical','serious'].includes(x.impact)).map(x=>x.id+': '+x.nodes.slice(0,2).map(n=>n.target.join(' ')).join(', '))")
    ok(not v, f"{where}: axe 0 lỗi nặng ({v[:3]})")


with sync_playwright() as pw:
    b = pw.chromium.launch()
    print("\n===== Máy tính: lọc =====")
    ctx = b.new_context(viewport={"width": 1366, "height": 860}); pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(B + "/"); pg.evaluate("localStorage.clear()"); pg.reload(); pg.wait_for_selector("#grid .card")
    ok(pg.locator("#fpanel #fsz").is_visible() and not pg.locator("#flt").is_visible(), "máy tính: ô lọc hiện sẵn, không cần nút Lọc thêm")
    pg.select_option("#fsz", "42"); pg.wait_for_timeout(150)
    ok(ids(pg) == want(size="42"), f"size 42 còn hàng: đúng {len(want(size='42'))} SP")
    ok("còn size 42" in pg.inner_text("#cnt"), "dòng đếm ghi rõ đang lọc size: " + pg.inner_text("#cnt"))
    pg.select_option("#fsz", ""); pg.select_option("#fgia", "100-150"); pg.wait_for_timeout(150)
    ok(ids(pg) == want(price="100-150"), f"giá 100.000–150.000đ: đúng {len(want(price='100-150'))} SP")
    pg.click(".chip[data-c='Quần áo CLB/Đội tuyển']"); pg.wait_for_timeout(150)
    opts = pg.eval_on_selector_all("#fhang option", "e=>e.map(o=>o.value).filter(Boolean)")
    ok("Just Play" in opts, f"danh sách hãng theo danh mục đang xem ({opts[:5]})")
    pg.select_option("#fhang", "Just Play"); pg.wait_for_timeout(150)
    w = want(price="100-150", brand="Just Play", cat="Quần áo CLB/Đội tuyển")
    ok(ids(pg) == w and len(w) > 0, f"kết hợp danh mục + giá + hãng: đúng {len(w)} SP")
    szs = pg.eval_on_selector_all("#fsz option", "e=>e.map(o=>o.value).filter(Boolean)")
    ok(szs and all(any(v["option1"] == s and v["inventory_quantity"] > 0 for p in prods if p["category"] == "Quần áo CLB/Đội tuyển" for v in p["variants"]) for s in szs),
       f"chỉ gợi ý các size đang còn hàng trong danh mục ({szs[:8]})")
    pg.click("#fclear"); pg.wait_for_timeout(150)
    ok(pg.input_value("#fgia") == "" and pg.input_value("#fhang") == "" and ids(pg) == want(cat="Quần áo CLB/Đội tuyển"), "Xóa lọc: bỏ hết lọc phụ, giữ danh mục")
    pg.click(".chip[data-c='Tất cả']")
    print("\n===== Yêu thích =====")
    first = pg.eval_on_selector_all("#grid .card", "e=>e.slice(0,2).map(x=>x.dataset.pid)")
    for pid in first: pg.click(f"#grid .card[data-pid='{pid}'] .fav"); pg.wait_for_timeout(80)
    ok(all(pg.get_attribute(f"#grid .card[data-pid='{pid}'] .fav", "aria-pressed") == "true" for pid in first), "bấm trái tim → đã lưu (aria-pressed)")
    ok("Yêu thích (2)" in pg.inner_text("#ffav"), "nút lọc Yêu thích đếm đúng 2")
    pg.click("#ffav"); pg.wait_for_timeout(150)
    ok(ids(pg) == set(first), "lọc Yêu thích: chỉ hiện đúng 2 SP đã lưu")
    pg.reload(); pg.wait_for_selector("#grid .card")
    ok("Yêu thích (2)" in pg.inner_text("#ffav"), "tải lại trang: vẫn nhớ Yêu thích")
    pg.goto(f"{B}/san-pham/{first[0]}/"); pg.wait_for_selector(".det h1")
    ok(pg.get_attribute(".acts .fav", "aria-pressed") == "true", "trang SP: trái tim đã bật cho SP đã lưu")
    pg.click(".acts .fav"); pg.wait_for_timeout(100)
    ok(pg.get_attribute(".acts .fav", "aria-pressed") == "false", "trang SP: bấm lại → bỏ khỏi Yêu thích")
    pg.goto(B + "/"); pg.wait_for_selector("#grid .card"); pg.click("#ffav"); pg.wait_for_timeout(150)
    ok(ids(pg) == {first[1]}, "danh sách Yêu thích còn đúng 1 SP")
    pg.evaluate("localStorage.setItem('yeuthich','{hỏng')"); pg.reload(); pg.wait_for_selector("#grid .card")
    ok("Yêu thích (0)" in pg.inner_text("#ffav"), "dữ liệu Yêu thích hỏng: không lỗi, về 0")
    pg.click("#ffav"); pg.wait_for_timeout(150)
    ok("chưa lưu sản phẩm nào" in pg.inner_text("#grid"), "chưa có Yêu thích: hướng dẫn bấm trái tim")
    ctx.close()

    for scheme in ("light", "dark"):
        print(f"\n===== Điện thoại 390 px – {'tối' if scheme == 'dark' else 'sáng'} =====")
        ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, color_scheme=scheme); pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(B + "/"); pg.wait_for_selector("#grid .card")
        ok(pg.locator("#flt").is_visible() and pg.locator("#fpanel").is_hidden(), "điện thoại: nút Lọc thêm, ô lọc ẩn cho gọn")
        pg.click("#flt"); pg.wait_for_timeout(100)
        ok(pg.locator("#fsz").is_visible() and pg.get_attribute("#flt", "aria-expanded") == "true", "bấm Lọc thêm → mở ô lọc")
        pg.select_option("#fsz", "XL"); pg.wait_for_timeout(150)
        ok(pg.inner_text("#flt .cnt").strip() == "1" and ids(pg) == want(size="XL"), "đang lọc 1 mục: nút ghi số 1, kết quả đúng")
        box = pg.locator("#grid .card .fav").first.bounding_box()
        ok(box and box["width"] >= 43.5 and box["height"] >= 43.5, "nút trái tim ≥ 44 px")
        ok(pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth"), "không tràn ngang")
        pg.evaluate("document.getElementById('san-pham').scrollIntoView()"); axe(pg, f"danh sách có ô lọc ({scheme})")
        ctx.close()
    b.close()

print("\nLỖI JS:", errs[:3]); print("KẾT QUẢ:", len(fails) + len(errs), "lỗi"); print(fails)
