"""Kiểm thử cài web như ứng dụng (C3) và gửi đơn kèm ảnh (N1) – chỉ bản Next.js.
- manifest.webmanifest: tên, start_url, display standalone, màu; biểu tượng 192/512/maskable đúng kích thước; trang có link manifest, apple-touch-icon.
- Giỏ hàng: món có ảnh → tin nhắn có dòng "Ảnh: <link đầy đủ>"; máy chia sẻ được tệp → nút "Gửi đơn kèm ảnh" gửi đúng ảnh + chữ đơn;
  không có ảnh → nút chỉ gửi chữ đơn (điền sẵn); máy tính không có bảng chia sẻ → không hiện nút.
(Chưa có ảnh thật nên bài này gắn tạm ảnh /icon-192.png cho 1 sản phẩm bằng cách chặn products.json.)
Chạy:  py tests/test_pwa_anh.py http://localhost:3602      (in "KẾT QUẢ: N lỗi")"""
import io, json, sys, urllib.request
from PIL import Image
from playwright.sync_api import sync_playwright

B = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3602").rstrip("/")
raw = urllib.request.urlopen(B + "/products.json").read()
data = json.loads(raw)
fails, errs = [], []


def ok(c, m):
    print(("  ✓ " if c else "  ✗ ") + m)
    if not c: fails.append(m)


print("\n===== Cài như ứng dụng =====")
man = json.load(urllib.request.urlopen(B + "/manifest.webmanifest"))
ok(man.get("short_name") == "SPORT 238" and man.get("start_url") == "/" and man.get("display") == "standalone" and man.get("lang") == "vi", "manifest: tên, start_url, display, lang")
for ic in man["icons"]:
    im = Image.open(io.BytesIO(urllib.request.urlopen(B + ic["src"]).read()))
    w = int(ic["sizes"].split("x")[0])
    ok(im.size == (w, w), f"biểu tượng {ic['src']} đúng {ic['sizes']} ({ic['purpose']})")
ok(any(i["purpose"] == "maskable" for i in man["icons"]), "có biểu tượng maskable (điện thoại cắt tròn không mất logo)")
ok(urllib.request.urlopen(B + "/favicon.ico").status == 200, "có favicon.ico (trình duyệt tự tìm; thiếu thì báo lỗi 404 trong console)")

pid = next(p for p in data["products"] if any(v["inventory_quantity"] > 0 for v in p["variants"]))
vid = next(v["id"] for v in pid["variants"] if v["inventory_quantity"] > 0)
with_img = dict(data); with_img["images"] = {**data.get("images", {}), pid["id"]: ["/icon-192.png"]}
body = json.dumps(with_img, ensure_ascii=False)
MOCK = """window.__sh=null;
Object.defineProperty(navigator,'canShare',{value:(d)=>!!(d&&d.files),configurable:true});
Object.defineProperty(navigator,'share',{value:(d)=>{window.__sh={text:d.text,files:(d.files||[]).map(f=>[f.name,f.type,f.size])};return Promise.resolve()},configurable:true});"""

with sync_playwright() as pw:
    b = pw.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, permissions=["clipboard-read", "clipboard-write"])
    pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(B + "/"); pg.wait_for_selector("#grid .card")
    ok(pg.locator("link[rel='manifest']").count() == 1 and pg.locator("link[rel='apple-touch-icon']").count() >= 1, "trang có link manifest và apple-touch-icon")
    ok(pg.locator("meta[name='theme-color']").count() >= 1, "có màu chủ đạo cho thanh trình duyệt")

    print("\n===== Gửi đơn kèm ảnh =====")
    # 1) món chưa có ảnh: không có dòng Ảnh, không có nút gửi kèm ảnh (dù máy chia sẻ được)
    pg.add_init_script(MOCK)
    pg.evaluate("id=>localStorage.setItem('cart5',JSON.stringify([{id,lb:'',qty:1}]))", vid)
    pg.reload(); pg.wait_for_selector("#grid .card"); pg.click("#bc"); pg.wait_for_timeout(500)
    ok("Ảnh:" not in pg.input_value("#ordtxt") and "ảnh)" not in pg.inner_text("#shareimg"), "món chưa có ảnh: không có dòng Ảnh; nút chia sẻ chỉ gửi chữ (không ghi số ảnh)")
    # 2) món có ảnh
    pg.route("**/products.json*", lambda r: r.fulfill(body=body, content_type="application/json"))
    pg.reload(); pg.wait_for_selector("#grid .card"); pg.click("#bc"); pg.wait_for_timeout(600)
    txt = pg.input_value("#ordtxt")
    ok(f"Ảnh: {B}/icon-192.png" in txt, "tin nhắn có link ảnh đầy đủ của món")
    ok(pg.locator("#shareimg").is_visible() and "1 ảnh" in pg.inner_text("#shareimg"), "máy chia sẻ được tệp: hiện nút 'Gửi đơn kèm ảnh (1 ảnh)'")
    pg.evaluate("navigator.clipboard.writeText('x')")
    pg.click("#shareimg"); pg.wait_for_timeout(600)
    sh = pg.evaluate("window.__sh")
    ok(bool(sh) and len(sh["files"]) == 1 and sh["files"][0][1] == "image/png" and sh["files"][0][2] > 1000, f"chia sẻ đúng 1 ảnh PNG ({sh and sh['files']})")
    ok(bool(sh) and sh["text"] == txt, "chia sẻ kèm đúng chữ của đơn")
    ok(pg.evaluate("navigator.clipboard.readText()").replace("\r\n", "\n") == txt, "chữ đơn cũng đã được sao chép (phòng ứng dụng bỏ chữ khi nhận ảnh)")
    ctx.close()
    # 3) máy không chia sẻ được tệp: không hiện nút
    ctx = b.new_context(viewport={"width": 1366, "height": 860}); pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script("Object.defineProperty(navigator,'canShare',{value:undefined,configurable:true})")
    pg.route("**/products.json*", lambda r: r.fulfill(body=body, content_type="application/json"))
    pg.goto(B + "/"); pg.evaluate("id=>localStorage.setItem('cart5',JSON.stringify([{id,lb:'',qty:1}]))", vid)
    pg.reload(); pg.wait_for_selector("#grid .card"); pg.click("#cb"); pg.wait_for_timeout(500)
    ok(pg.locator("#shareimg").count() == 0 and "Ảnh:" in pg.input_value("#ordtxt"), "máy tính không chia sẻ được tệp: không hiện nút, tin nhắn vẫn có link ảnh")
    ctx.close(); b.close()

print("\nLỖI JS:", errs[:3]); print("KẾT QUẢ:", len(fails) + len(errs), "lỗi"); print(fails)
