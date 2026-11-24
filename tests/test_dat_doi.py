"""Kiểm thử đặt đồng phục đội (B2) – chỉ bản Next.js.
Giá in tên + số (chủ shop xác nhận 24/11/2026): từ 5 bộ 15.000đ/bộ, từ 10 bộ 10.000đ/bộ, dưới 5 bộ shop báo giá.
Tiền áo tính độc lập từ products.json. Tin nhắn sao chép đúng, mở Zalo/Messenger; cảnh báo vượt tồn, trùng số, lệch số người.
Chạy:  py tests/test_dat_doi.py http://localhost:3602      (in "KẾT QUẢ: N lỗi")"""
import json, pathlib, re, sys, urllib.request
from playwright.sync_api import sync_playwright

B = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3602").rstrip("/")
AXE = pathlib.Path(__file__).resolve().parent / "node_modules" / "axe-core" / "axe.min.js"
prods = json.load(urllib.request.urlopen(B + "/products.json"))["products"]
fails, errs = [], []
money = lambda n: f"{n:,}".replace(",", ".") + "đ"


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


def dflt(p):
    return next((c for c in colors(p) if sum(max(0, v["inventory_quantity"]) for v in p["variants"] if v["option2"] == c) > 0), colors(p)[0])


kit = next(p for p in prods if p["category"] == "Quần áo không logo" and sum(1 for v in p["variants"] if v["option2"] == dflt(p) and v["option1"] and v["inventory_quantity"] > 0) >= 2)
col = dflt(kit)
vs = [v for v in kit["variants"] if v["option2"] == col and v["option1"]]
instock = [v for v in vs if v["inventory_quantity"] > 0]
a, b2 = instock[0], instock[1]
price = {v["option1"]: v["price"] for v in vs}

with sync_playwright() as pw:
    b = pw.chromium.launch()
    for scheme in ("light", "dark"):
        print(f"\n===== Điện thoại 390 px – {'tối' if scheme == 'dark' else 'sáng'} =====")
        ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, color_scheme=scheme, permissions=["clipboard-read", "clipboard-write"])
        ctx.route("https://zalo.me/**", lambda r: r.fulfill(body="zalo")); ctx.route("https://m.me/**", lambda r: r.fulfill(body="messenger"))
        pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        if scheme == "light":
            pg.goto(B + "/"); pg.wait_for_selector("#grid .card"); pg.click("#go-dat-doi"); pg.wait_for_selector("#tm-sp")
            ok(pg.url.rstrip("/").endswith("/dat-doi"), "trang chủ: nút 'Đặt đồng phục đội' mở trang đặt đội")
        else:
            pg.goto(B + "/dat-doi/"); pg.wait_for_selector("#tm-sp")
        pg.select_option("#tm-sp", kit["id"]); pg.wait_for_selector("[data-tq]")
        if len(colors(kit)) > 1: pg.click(f"[data-tcol='{col}']")

        def setq(s, n):
            pg.fill(f"[data-tq='{s}']", str(n)); pg.wait_for_timeout(60)

        setq(a["option1"], 2); setq(b2["option1"], 2)
        shirt = 2 * price[a["option1"]] + 2 * price[b2["option1"]]
        ok(pg.inner_text("#tm-bo") == "4" and pg.inner_text("#tm-ao") == money(shirt), f"4 bộ: tiền áo {money(shirt)} đúng theo giá từng size")
        ok("Shop báo giá" in pg.inner_text("#tm-in-tien") and pg.inner_text("#tm-tong") == money(shirt), "dưới 5 bộ: tiền in để shop báo giá, tạm tính chỉ gồm tiền áo")
        setq(b2["option1"], 3); shirt += price[b2["option1"]]
        ok(pg.inner_text("#tm-in-tien") == f"15.000đ × 5 = 75.000đ" and pg.inner_text("#tm-tong") == money(shirt + 75_000), "5 bộ: in tên số 15.000đ/bộ")
        setq(b2["option1"], 8); shirt += 5 * price[b2["option1"]]
        ok(pg.inner_text("#tm-in-tien") == f"10.000đ × 10 = 100.000đ" and pg.inner_text("#tm-tong") == money(shirt + 100_000), "10 bộ: in tên số 10.000đ/bộ")
        if scheme == "light":
            pg.click("#tm-them"); pg.click("#tm-them")
            pg.fill("[data-pn='0']", "nguyễn văn an dài quá mức"); pg.fill("[data-pnum='0']", "1a0"); pg.select_option("[data-psz='0']", a["option1"])
            pg.fill("[data-pn='1']", "Bình"); pg.fill("[data-pnum='1']", "10")
            ok(len(pg.input_value("[data-pn='0']")) == 15 and pg.input_value("[data-pn='0']") == pg.input_value("[data-pn='0']").upper(), "tên in tối đa 15 ký tự, viết hoa")
            ok(pg.input_value("[data-pnum='0']") == "10", "số áo chỉ nhận chữ số")
            ok(pg.locator("#tm-trung").is_visible() and "10" in pg.inner_text("#tm-trung"), "báo trùng số áo")
            ok(pg.locator("#tm-lech").is_visible() and "2 người" in pg.inner_text("#tm-lech"), "báo số người in khác số bộ")
            pg.check("#tm-logo"); pg.fill("#tm-doi", "FC KCN"); pg.fill("#tm-ten", "Anh Tuấn")
            over = next((v for v in vs if v["inventory_quantity"] < 50), None)
            setq(over["option1"], over["inventory_quantity"] + 5 if over["inventory_quantity"] > 0 else 3)
            ok(pg.locator("#tm-over").is_visible(), "số lượng vượt tồn kho: cảnh báo (không chặn)")
            txt = pg.input_value("#tm-msg")
            ok(all(s in txt for s in ["đội mình muốn đặt đồng phục", kit.get("display_title") or kit["title"], "In tên + số: có", "Danh sách in:", "Logo đội: có", "Tên đội: FC KCN", "Người liên hệ: Anh Tuấn", "vượt tồn kho", "ghé shop nhận hàng"]),
               "tin nhắn đủ: mẫu, số lượng, in tên số, danh sách, logo, đội, liên hệ, lưu ý tồn, ghé shop nhận")
            ok(not re.search(r"(?i)\bship\b|giao hàng|phí giao|gửi hàng", txt), "tin nhắn không có chữ ship/giao hàng")
            pg.evaluate("navigator.clipboard.writeText('x')")
            with ctx.expect_page() as pi: pg.click("#tm-zalo")
            z = pi.value; z.wait_for_load_state("commit"); pg.wait_for_timeout(300)
            ok(z.url.startswith("https://zalo.me/") and pg.evaluate("navigator.clipboard.readText()").replace("\r\n", "\n") == txt, "Sao chép đơn & mở Zalo: đúng nội dung, mở Zalo")
            z.close()
            ok((pg.get_attribute("#tm-mess", "href") or "").startswith("https://m.me/"), "nút Messenger mở m.me")
        ok(pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth"), "không tràn ngang 390 px")
        axe(pg, f"/dat-doi/ ({scheme})")
        ctx.close()
    ctx = b.new_context(viewport={"width": 320, "height": 700}, is_mobile=True, has_touch=True); pg = ctx.new_page()
    pg.goto(B + "/dat-doi/"); pg.wait_for_selector("#tm-sp"); pg.select_option("#tm-sp", kit["id"]); pg.click("#tm-them")
    ok(pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth"), "không tràn ngang 320 px")
    pg.click("#tm-zalo"); pg.wait_for_timeout(200)
    ok("chưa nhập số lượng" in pg.inner_text("#toast"), "chưa nhập số lượng mà bấm gửi: nhắc nhập số lượng")
    ctx.close(); b.close()

print("\nLỖI JS:", errs[:3]); print("KẾT QUẢ:", len(fails) + len(errs), "lỗi"); print(fails)
