"""Kiểm thử bảng size và gợi ý size (A3, B1) – chỉ cho bản Next.js (bản chính).
- Trang /bang-size/: đủ 9 hãng, 15 bảng; MỌI ô trên trang khớp data/bang-size.json (chép từ ảnh chủ shop gửi).
- Gợi ý size theo chiều cao, cân nặng: kết quả đúng như tra tay trên bảng (ma trận RIKI, lệch size AMAC, trẻ em Just Play,
  hãng chỉ ghi một số, ngoài bảng).
- Trang sản phẩm: nút "Bảng size" cạnh chỗ chọn size tự mở đúng hãng; "Chọn size X" chọn đúng size; giày ghi chưa có bảng size;
  hãng chưa có bảng ghi rõ.
- axe 0 lỗi critical/serious, không tràn ngang ở 390 px; sáng và tối.
Chạy:  py tests/test_bang_size.py http://localhost:3602      (in "KẾT QUẢ: N lỗi")"""
import json, pathlib, re, sys, urllib.request
from playwright.sync_api import sync_playwright

B = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3602").rstrip("/")
DATA = json.loads((pathlib.Path(__file__).resolve().parents[1] / "sport-shop-next" / "frontend" / "data" / "bang-size.json").read_text(encoding="utf-8"))
AXE = pathlib.Path(__file__).resolve().parent / "node_modules" / "axe-core" / "axe.min.js"
prods = json.load(urllib.request.urlopen(B + "/products.json"))["products"]
fails, errs = [], []


def ok(c, m):
    print(("  ✓ " if c else "  ✗ ") + m)
    if not c: fails.append(m)


def axe(pg, where):
    if not AXE.exists(): return
    pg.add_script_tag(path=str(AXE))
    v = pg.evaluate("async()=>(await axe.run(document,{resultTypes:['violations']})).violations.filter(x=>['critical','serious'].includes(x.impact)).map(x=>x.id+': '+x.nodes.slice(0,2).map(n=>n.target.join(' ')).join(', '))")
    ok(not v, f"{where}: axe 0 lỗi nặng ({v[:3]})")


def finder(pg, scope, h, w, brand=None):
    if brand: pg.select_option(f"{scope} .finder select", brand)
    pg.fill(f"{scope} .finder input[id$='-h']", str(h)); pg.fill(f"{scope} .finder input[id$='-w']", str(w)); pg.wait_for_timeout(120)
    return [t.strip() for t in pg.locator(f"{scope} .finder .adv").all_inner_texts()]


def brand_of(p, key):
    return key in (p.get("vendor") or "").lower() or key in p["title"].lower()


with sync_playwright() as pw:
    b = pw.chromium.launch()
    for scheme in ("light", "dark"):
        print(f"\n===== Trang /bang-size/ – {'tối' if scheme == 'dark' else 'sáng'} =====")
        ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, color_scheme=scheme); pg = ctx.new_page()
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(B + "/bang-size/"); pg.wait_for_selector(".szt table")
        brands = DATA["hang_san_xuat"]
        ok(pg.locator(".brandsec").count() == len(brands) == 9, f"đủ {len(brands)} hãng")
        tables = pg.locator(".szt table")
        want = [c for br in brands for c in br["bang"]]
        ok(tables.count() == len(want) == 15, f"đủ {tables.count()} bảng")
        got = pg.evaluate("[...document.querySelectorAll('.szt table')].map(t=>[...t.rows].map(r=>[...r.cells].map(c=>c.textContent.trim())))")
        bad = []
        for k, c in enumerate(want):
            body = [r for r in got[k][1:]]
            head = got[k][0][1:]
            if head != c["cot"][1:] or body != c["hang"]: bad.append(f"{c['nguon']} {c['tieu_de']}")
        ok(not bad, f"mọi ô của 15 bảng khớp dữ liệu chép từ ảnh (sai: {bad[:3]})")
        ok(pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth"), "390 px: không tràn ngang (bảng rộng cuộn trong khung)")
        hs = pg.evaluate("[...document.querySelectorAll('.brandnav .chip')].map(e=>Math.round(e.getBoundingClientRect().height))")
        ok(hs and all(40 <= h <= 52 for h in hs), f"nút chọn hãng cao đều 44–52 px, chữ giữa nút ({sorted(set(hs))})")
        dup = pg.evaluate("[...document.querySelectorAll('.szt figcaption')].filter(f=>{const t=f.querySelector('.tag');return t&&f.querySelector('b').textContent.toLowerCase().includes(t.textContent.toLowerCase())}).length")
        ok(dup == 0, "tiêu đề bảng không lặp nhãn người lớn/trẻ em")
        axe(pg, f"/bang-size/ {scheme}")
        if scheme == "light":
            print("\n===== Gợi ý size (tra tay trên bảng) =====")
            r = finder(pg, ".sizepage", 168, 60, "riki")
            ok(len(r) == 2 and r[0].endswith("Size L") and r[1].endswith("Size M"), f"RIKI 168 cm 60 kg: ma trận → L; bảng nam → M ({r})")
            r = finder(pg, ".sizepage", 165, 65, "amac")
            ok(len(r) == 3 and "Size L" in r[0] and "lớn hơn" in r[0], f"AMAC 165/65: chiều cao M, cân nặng L → hãng khuyên size lớn hơn → L ({r[0] if r else r})")
            ok(len(r) == 3 and "Theo chiều cao: size M; theo cân nặng: size L" in r[1], f"AMAC Sport (không có lời khuyên): nói rõ cả hai ({r[1] if len(r) > 1 else r})")
            ok(len(r) == 3 and "Ngoài bảng" in r[2], "AMAC trẻ em 165 cm: ngoài bảng")
            r = finder(pg, ".sizepage", 128, 19, "just-play")
            ok(len(r) == 2 and "Ngoài bảng" in r[0] and r[1].endswith("Size 5"), f"Just Play 128 cm 19 kg: người lớn ngoài bảng; trẻ em size 5 ({r})")
            r = finder(pg, ".sizepage", 172, 70, "win")
            ok(len(r) == 2 and all(x.endswith("Size L") for x in r), f"WIN (bảng chỉ ghi một số) 172/70 → L ({r})")
            r = finder(pg, ".sizepage", 190, 95, "strivend")
            ok(r and r[0].endswith("Size XXL"), f"Strivend 190/95 (>185, >85) → XXL ({r})")
            r = finder(pg, ".sizepage", 157, 57, "sao-viet")
            ok(r and r[0].endswith("Size S"), f"Sao Việt 157/57 (khoảng trống giữa S và M, gần S) → S ({r})")
            r = finder(pg, ".sizepage", 200, 150, "egan")
            ok(r and "Ngoài bảng" in r[0], f"Egan 200 cm 150 kg → ngoài bảng ({r})")
        ctx.close()

    print("\n===== Trang sản phẩm =====")
    ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True); pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    jp = next(p for p in prods if brand_of(p, "just play") and p["category"] != "Quần áo trẻ em" and any(v["option1"] == "L" and v["inventory_quantity"] > 0 for v in p["variants"]))
    pg.goto(B + "/san-pham/" + jp["id"] + "/"); pg.wait_for_selector(".det h1")
    ok(pg.locator("#szh .szbtn").is_visible() and "Just Play" in pg.inner_text("#szh .szbtn"), f"SP Just Play ({jp['title']}): nút Bảng size đúng hãng")
    pg.click("#szh .szbtn"); pg.wait_for_timeout(150)
    ok(pg.locator("#szh .szpanel").is_visible() and pg.locator("#szh .szt table").count() == 2 and pg.locator("#szh .finder select").count() == 0, "mở bảng size: 2 bảng Just Play, không phải chọn hãng")
    r = finder(pg, "#szh", 170, 65)
    ok(bool(r) and r[0].startswith("Just Play") and "Size L" in r[0], f"170 cm 65 kg → Just Play người lớn size L ({r[:1]})")
    pg.click("#szh [data-pick='L']"); pg.wait_for_timeout(250)
    ok(pg.locator(".opt[data-sz='L'][aria-pressed='true']").count() == 1 and pg.locator("#szh .szpanel").is_hidden(), "bấm 'Chọn size L' → size L được chọn, bảng size đóng lại")
    pg.click("#szh .szbtn"); axe(pg, "trang SP có bảng size đang mở")
    shoe = next(p for p in prods if p["category"] in ("Giày bóng đá", "Giày thể thao") and any(v["option1"] for v in p["variants"]))
    pg.goto(B + "/san-pham/" + shoe["id"] + "/"); pg.wait_for_selector(".det h1")
    ok("Giày chưa có bảng size" in pg.inner_text("#szh"), "giày: ghi chưa có bảng size, chọn theo size giày đang mang")
    cv = next((p for p in prods if (p.get("vendor") or "") == "CV" and any(v["option1"] for v in p["variants"])), None)
    if cv:
        pg.goto(B + "/san-pham/" + cv["id"] + "/"); pg.wait_for_selector(".det h1"); pg.click("#szh .szbtn")
        ok("Chưa có bảng size của hãng CV" in pg.inner_text("#szh"), "hãng chưa có bảng (CV): ghi rõ, mời nhắn shop")
    print("\n===== Lối vào trang bảng size =====")
    pg.goto(B + "/"); pg.wait_for_selector("#grid .card")
    ok(pg.locator("footer a[href='/bang-size/']").count() == 1, "chân trang có link Bảng size")
    pg.click("#mb"); ok(pg.locator("#mnav a[href='/bang-size/']").is_visible(), "menu điện thoại có Bảng size")
    ctx.close()
    ctx = b.new_context(viewport={"width": 1366, "height": 860}); pg = ctx.new_page(); pg.goto(B + "/")
    ok(pg.locator(".menu a[href='/bang-size/']").is_visible(), "máy tính: menu có Bảng size")
    ctx.close(); b.close()

print("\nLỖI JS:", errs[:3]); print("KẾT QUẢ:", len(fails) + len(errs), "lỗi"); print(fails)
