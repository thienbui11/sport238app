"""Kiểm tra truy cập (accessibility) bằng axe-core trên trình duyệt thật.
Quét: trang chủ, danh sách đã lọc + tìm kiếm, trang chi tiết, giỏ hàng đang mở (có hàng), menu điện thoại đang mở;
ở máy tính 1366 px và điện thoại 390 px; chế độ sáng và tối.
Cần: cd tests && npm install (một lần).   Chạy: python tests/test_a11y.py http://localhost:3000
Đạt khi không có vi phạm mức "critical" hoặc "serious"; in "KẾT QUẢ: N lỗi"."""
import collections, json, pathlib, sys, urllib.request
from playwright.sync_api import sync_playwright

B = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000").rstrip("/")
AXE = pathlib.Path(__file__).resolve().parent / "node_modules" / "axe-core" / "axe.min.js"
if not AXE.exists():
    raise SystemExit("Chưa cài axe-core: cd tests && npm install")
try: api = json.load(urllib.request.urlopen(B + "/api/products"))
except Exception: api = json.load(urllib.request.urlopen(B + "/products.json"))
prods = api["products"]
pid = next(p["id"] for p in prods if any(v["option1"] for v in p["variants"]) and any(v["inventory_quantity"] > 0 for v in p["variants"]))
bad, info = [], collections.Counter()

RUN = """async () => { const r = await axe.run(document, {resultTypes: ['violations']});
  return r.violations.map(v => ({id: v.id, impact: v.impact, help: v.help, nodes: v.nodes.slice(0, 3).map(n => n.target.join(' '))})) }"""


def scan(pg, where):
    pg.add_script_tag(path=str(AXE))
    for v in pg.evaluate(RUN):
        key = f"{v['impact']:8} {v['id']}: {v['help']}"
        if v["impact"] in ("critical", "serious"):
            bad.append(f"[{where}] {key} → {v['nodes']}")
        else:
            info[key] += 1


with sync_playwright() as pw:
    b = pw.chromium.launch()
    for dev, vp, mob in [("máy tính", {"width": 1366, "height": 860}, False), ("điện thoại", {"width": 390, "height": 844}, True)]:
        for scheme in ("light", "dark"):
            tag = f"{dev}, {'tối' if scheme == 'dark' else 'sáng'}"
            ctx = b.new_context(viewport=vp, is_mobile=mob, has_touch=mob, color_scheme=scheme, locale="vi-VN")
            pg = ctx.new_page()
            pg.goto(B + "/"); pg.wait_for_selector("#grid .card"); pg.wait_for_timeout(300)
            scan(pg, f"trang chủ – {tag}")
            pg.locator(".chip").nth(2).click(); pg.fill("#q", "ao"); pg.wait_for_timeout(250)
            scan(pg, f"danh sách đã lọc – {tag}")
            if mob and pg.locator("#mb").is_visible():
                pg.evaluate("scrollTo(0,0)"); pg.click("#mb"); pg.wait_for_timeout(200)
                scan(pg, f"menu điện thoại – {tag}"); pg.keyboard.press("Escape")
            pg.goto(B + "/#p-" + pid); pg.wait_for_selector(".det h1"); pg.wait_for_timeout(300)
            scan(pg, f"trang chi tiết – {tag}")
            pg.locator(".opt[data-sz]:not(.out)").first.click(); pg.click("#ad"); pg.wait_for_timeout(150)
            pg.click("#cb"); pg.wait_for_timeout(450)
            scan(pg, f"giỏ hàng – {tag}")
            ctx.close()
    b.close()

if info:
    print("Vi phạm nhẹ (minor/moderate, không tính lỗi):")
    for k, n in info.most_common(): print(f"  · {k} ({n} lần)")
for x in bad: print("  ✗", x)
print("\nKẾT QUẢ:", len(bad), "lỗi")
