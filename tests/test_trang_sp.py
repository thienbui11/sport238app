"""Kiểm thử chức năng thêm ở trang sản phẩm (A4, A5, B4, B5) – chỉ bản Next.js.
- A4 Hỏi shop: bấm "Hỏi qua Zalo/Messenger" → sao chép sẵn câu hỏi (tên, mã, size, màu nếu có, link), mở đúng Zalo/Messenger.
- B5 Chia sẻ: có nút chia sẻ của máy thì dùng (đúng link); không có thì sao chép link.
- A5 Bản đồ: chưa bấm thì KHÔNG tải Google Maps; bấm "Xem bản đồ" mới hiện bản đồ đúng địa chỉ.
- B4 Sản phẩm cùng loại (cùng danh mục, không trùng chính nó, ≤ 8) và đã xem gần đây (lưu trên máy, mới nhất trước, không lỗi khi dữ liệu hỏng).
- axe 0 lỗi nặng, không tràn ngang 390 px, sáng và tối.
Chạy:  py tests/test_trang_sp.py http://localhost:3602      (in "KẾT QUẢ: N lỗi")"""
import json, pathlib, sys, urllib.parse, urllib.request
from playwright.sync_api import sync_playwright

B = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3602").rstrip("/")
AXE = pathlib.Path(__file__).resolve().parent / "node_modules" / "axe-core" / "axe.min.js"
prods = json.load(urllib.request.urlopen(B + "/products.json"))["products"]
byid = {p["id"]: p for p in prods}
fails, errs = [], []


def ok(c, m):
    print(("  ✓ " if c else "  ✗ ") + m)
    if not c: fails.append(m)


def axe(pg, where):
    if not AXE.exists(): return
    pg.add_script_tag(path=str(AXE))
    v = pg.evaluate("async()=>(await axe.run(document,{resultTypes:['violations']})).violations.filter(x=>['critical','serious'].includes(x.impact)).map(x=>x.id+': '+x.nodes.slice(0,2).map(n=>n.target.join(' ')).join(', '))")
    ok(not v, f"{where}: axe 0 lỗi nặng ({v[:3]})")


def colors(p):
    u = []
    for v in p["variants"]:
        if v["option2"] not in u: u.append(v["option2"])
    return u


sized = next(p for p in prods if len(colors(p)) > 1 and any(v["option1"] and v["inventory_quantity"] > 0 for v in p["variants"]))
other = next(p for p in prods if p["id"] != sized["id"] and p["category"] == sized["category"])
google = []

with sync_playwright() as pw:
    b = pw.chromium.launch()
    for scheme in ("light", "dark"):
        print(f"\n===== Điện thoại 390 px – {'tối' if scheme == 'dark' else 'sáng'} =====")
        ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, color_scheme=scheme, permissions=["clipboard-read", "clipboard-write"])
        ctx.route("https://zalo.me/**", lambda r: r.fulfill(body="zalo")); ctx.route("https://m.me/**", lambda r: r.fulfill(body="messenger"))
        ctx.route("https://maps.google.com/**", lambda r: (google.append(r.request.url), r.fulfill(body="<html><body>ban do</body></html>", content_type="text/html")))
        pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(B + "/"); pg.evaluate("localStorage.clear()")
        url = f"{B}/san-pham/{sized['id']}/"
        pg.goto(url); pg.wait_for_selector(".det h1"); pg.wait_for_timeout(300)
        if scheme == "light":
            # A4
            v = next(v for v in sized["variants"] if v["option1"] and v["inventory_quantity"] > 0)
            if pg.locator(f".opt[data-col='{v['option2']}']").count(): pg.click(f".opt[data-col='{v['option2']}']")
            pg.click(f".opt[data-sz='{v['option1']}']")
            pg.evaluate("navigator.clipboard.writeText('x')")
            with ctx.expect_page() as pi: pg.click("#askz")
            z = pi.value; z.wait_for_load_state("commit"); pg.wait_for_timeout(300)
            clip = pg.evaluate("navigator.clipboard.readText()")
            name = sized.get("display_title") or sized["title"]
            ok(z.url.startswith("https://zalo.me/"), "Hỏi qua Zalo: mở Zalo")
            ok(name in clip and f"Mã {v['sku']}" in clip and f"size {v['option1']}" in clip and v["option2"] in clip and f"/san-pham/{sized['id']}/" in clip,
               f"câu hỏi sao chép sẵn có tên, mã, size, màu, link ({clip!r})")
            ok("Đã sao chép câu hỏi" in pg.inner_text("#toast"), "báo đã sao chép câu hỏi")
            z.close()
            ok((pg.get_attribute("#askm", "href") or "").startswith("https://m.me/"), "Hỏi qua Messenger: link m.me")
            # B5: không có nút chia sẻ của máy → sao chép link
            pg.evaluate("navigator.clipboard.writeText('x')"); pg.evaluate("Object.defineProperty(navigator,'share',{value:undefined,configurable:true})")
            pg.click("#share"); pg.wait_for_timeout(250)
            ok(pg.evaluate("navigator.clipboard.readText()") == url, "chia sẻ (máy không hỗ trợ): sao chép đúng link sản phẩm")
            # B5: có nút chia sẻ của máy → gọi đúng link
            pg.evaluate("window.__sh=null;Object.defineProperty(navigator,'share',{value:(d)=>{window.__sh=d;return Promise.resolve()},configurable:true})")
            pg.click("#share"); pg.wait_for_timeout(200)
            sh = pg.evaluate("window.__sh")
            ok(bool(sh) and sh.get("url") == url and name in sh.get("title", ""), f"chia sẻ (điện thoại): dùng nút chia sẻ của máy, đúng link ({sh})")
            # A5
            ok(not google and pg.locator(".visit2 iframe").count() == 0, "chưa bấm: không tải Google Maps")
            pg.click(".visit2 #mapbtn"); pg.wait_for_timeout(600)
            src = pg.get_attribute(".visit2 iframe", "src") or ""
            ok("maps.google.com" in src and urllib.parse.quote("238 ấp Thuận Điền") in src, "bấm Xem bản đồ → hiện bản đồ đúng địa chỉ")
            mw = pg.evaluate("(()=>{const m=document.querySelector('.visit2 .map'),p=m.parentElement;return [m.getBoundingClientRect().width,p.clientWidth]})()")
            ok(abs(mw[0] - mw[1]) < 2, f"bản đồ rộng hết khung ({mw})")
            hs = pg.evaluate("[...document.querySelectorAll('.ask .btn')].map(e=>Math.round(e.getBoundingClientRect().height))")
            ok(all(h <= 52 for h in hs), f"nút hỏi shop không xuống dòng ({hs})")
        # B4: sản phẩm cùng loại
        rel = pg.eval_on_selector_all("#lienquan .mini", "e=>e.map(x=>x.dataset.mini)")
        ok(1 <= len(rel) <= 8 and sized["id"] not in rel and all(byid[i]["category"] == sized["category"] for i in rel), f"sản phẩm cùng loại: {len(rel)} SP cùng danh mục, không trùng chính nó")
        ok(pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth"), "không tràn ngang")
        axe(pg, f"trang SP ({scheme})")
        # B4: đã xem gần đây
        pg.goto(f"{B}/san-pham/{other['id']}/"); pg.wait_for_selector(".det h1"); pg.wait_for_timeout(300)
        seen = pg.eval_on_selector_all("#daxem .mini", "e=>e.map(x=>x.dataset.mini)")
        ok(seen[:1] == [sized["id"]] and other["id"] not in seen, f"trang SP thứ hai: 'đã xem gần đây' có SP trước, không có chính nó ({seen})")
        pg.goto(B + "/"); pg.wait_for_selector("#grid .card"); pg.wait_for_timeout(300)
        seen = pg.eval_on_selector_all("#daxem .mini", "e=>e.map(x=>x.dataset.mini)")
        ok(seen[:2] == [other["id"], sized["id"]], f"trang chủ: đã xem gần đây, mới nhất trước ({seen})")
        pg.evaluate("localStorage.setItem('daxem','{hỏng')"); pg.reload(); pg.wait_for_selector("#grid .card"); pg.wait_for_timeout(300)
        ok(pg.locator("#daxem").count() == 0, "dữ liệu 'đã xem' hỏng: không lỗi, không hiện")
        ctx.close()
    b.close()

print("\nLỖI JS:", errs[:3]); print("KẾT QUẢ:", len(fails) + len(errs), "lỗi"); print(fails)
