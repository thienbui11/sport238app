"""Kiểm thử chống tái phát các lỗi đã sửa ở Giai đoạn 1 (điện thoại, tìm kiếm, quay lại, nút nổi, cỡ nút, giữ màu,
hỏi lại khi xóa giỏ, vượt tồn kho, giờ mở cửa, bàn phím trong giỏ, đăng xuất quản trị).
Chạy:  python tests/test_mobile.py http://localhost:3000     (in "KẾT QUẢ: 0 lỗi" khi đạt)"""
import json, os, re, sys, urllib.request
from playwright.sync_api import sync_playwright

OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"); os.makedirs(OUTDIR, exist_ok=True)
B = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000"
try: api = json.load(urllib.request.urlopen(B + "/api/products")); HAS_API = True
except Exception: api = json.load(urllib.request.urlopen(B + "/products.json")); HAS_API = False
prods = api["products"]; fails = []; errs = []
PAGE = 20

def ok(c, m):
    print(("  ✓ " if c else "  ✗ ") + m)
    if not c: fails.append(m)

def colors(p):
    u = []
    for v in p["variants"]:
        if v["option2"] not in u: u.append(v["option2"])
    return u

def fold(s):
    import unicodedata
    s = unicodedata.normalize("NFD", s.lower()); return "".join(c for c in s if unicodedata.category(c) != "Mn").replace("đ", "d")

multi = next(p for p in prods if sum(1 for c in colors(p) if any(v["option2"] == c and v["option1"] and v["inventory_quantity"] > 0 for v in p["variants"])) >= 2)
one_left = next(p for p in prods if len(colors(p)) == 1 and any(v["inventory_quantity"] == 1 for v in p["variants"]))
v1 = next(v for v in one_left["variants"] if v["inventory_quantity"] == 1)
shoe = next(p for p in prods if p["category"] == "Giày bóng đá" and any(v["inventory_quantity"] > 0 for v in p["variants"]))

def settle(pg, expr):
    # chờ trang cuộn mượt xong rồi mới đo
    last = None
    for _ in range(30):
        pg.wait_for_timeout(150); v = round(pg.evaluate(expr))
        if v == last: return v
        last = v
    return last

def show_all(pg):
    while pg.locator("#more").is_visible(): pg.click("#more button"); pg.wait_for_timeout(60)

def go_detail_from_card(pg, nth):
    card = pg.locator("#grid .card").nth(nth); card.scroll_into_view_if_needed(); pg.wait_for_timeout(150)
    y = settle(pg, "scrollY"); card.locator("a.thumb").click(); pg.wait_for_selector(".det h1"); pg.wait_for_timeout(250)
    return y

CONTRAST = r"""(sels)=>{const lum=c=>{const m=c.match(/[\d.]+/g).map(Number);const [r,g,b]=m.slice(0,3).map(v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)});return .2126*r+.7152*g+.0722*b};
  const bg=e=>{for(;e;e=e.parentElement){const s=getComputedStyle(e),m=s.backgroundColor.match(/[\d.]+/g);if(m&&(m[3]===undefined||+m[3]>.9))return s.backgroundColor}return getComputedStyle(document.body).backgroundColor};
  const bad=[];document.querySelectorAll(sels).forEach(e=>{const r=e.getBoundingClientRect();if(!r.width||e.disabled)return;const cs=getComputedStyle(e),a=lum(cs.color),b=lum(bg(e)),cr=(Math.max(a,b)+.05)/(Math.min(a,b)+.05);
  const big=parseFloat(cs.fontSize)>=18.6&&+cs.fontWeight>=700;if(cr<(big?3:4.5))bad.push((e.id||e.className)+' '+e.textContent.trim().slice(0,14)+' '+cr.toFixed(2))});return bad}"""

def mobile(b, scheme="light"):
    print(f"\n===== ĐIỆN THOẠI 390 px – chế độ {'tối' if scheme == 'dark' else 'sáng'} =====")
    ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, device_scale_factor=2, locale="vi-VN", color_scheme=scheme)
    pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(B + "/"); pg.wait_for_selector("#grid .card"); pg.wait_for_timeout(300)
    # 1. lưới 2 cột, sản phẩm gần đầu trang, trang không còn dài hàng trăm màn hình
    cols = pg.evaluate("getComputedStyle(document.getElementById('grid')).gridTemplateColumns.split(' ').length")
    ok(cols == 2, f"lưới sản phẩm 2 cột trên điện thoại (đang {cols})")
    y0 = pg.evaluate("Math.round(document.querySelector('#grid .card').getBoundingClientRect().top+scrollY)")
    ok(y0 < 1700, f"sản phẩm đầu tiên ở {y0} px (trước đây 3.908 px; yêu cầu < 1.700 px, khoảng 2 màn hình)")
    n = pg.locator("#grid .card").count(); h = pg.evaluate("document.documentElement.scrollHeight")
    ok(n == min(PAGE, len(prods)), f"hiện {n} sản phẩm đầu tiên, có nút Xem thêm")
    ok(h < 20000, f"chiều cao trang {h} px (trước đây 119.543 px)")
    pg.click("#more button"); pg.wait_for_timeout(150)
    ok(pg.locator("#grid .card").count() == min(2 * PAGE, len(prods)), "bấm Xem thêm → hiện thêm 20 sản phẩm")
    ok("/" in pg.inner_text("#cnt"), "dòng đếm ghi đang xem bao nhiêu/tổng: " + pg.inner_text("#cnt"))
    # 2. menu điện thoại
    lowc = pg.evaluate(CONTRAST, "#bbar a, #bbar button, #grid .szb, #grid .clb, #grid .btn, #moreb, .chip, #cnt")
    ok(not lowc, f"tương phản chữ đạt chuẩn (thanh dưới, nút size/màu, Xem thêm) (chưa đạt: {lowc[:3]})")
    pg.evaluate("scrollTo(0,0)")
    clip = pg.evaluate("[...document.querySelectorAll('.strip .wrap > *')].filter(e=>e.offsetParent).some(e=>{const r=e.getBoundingClientRect();return r.left<0||r.right>innerWidth})")
    ok(not clip, "thanh trên cùng (giờ mở cửa, Zalo) không bị cắt mép")
    over = pg.evaluate("[...document.querySelectorAll('.cat')].filter(c=>{const i=c.querySelector('i').getBoundingClientRect(),b=c.querySelector('b').getBoundingClientRect();return i.bottom>b.top+2&&i.left<b.right&&i.right>b.left}).map(c=>c.querySelector('b').textContent)")
    ok(not over, f"ô danh mục: hình không đè lên chữ (bị đè: {over[:2]})")
    ok(pg.is_visible("#mb"), "có nút menu ☰ trên điện thoại")
    pg.click("#mb"); pg.wait_for_timeout(150)
    ok(pg.is_visible("#mnav") and pg.get_attribute("#mb", "aria-expanded") == "true", "bấm ☰ → mở menu")
    lowc = pg.evaluate(CONTRAST, "#mnav a, #mnav p"); ok(not lowc, f"menu: tương phản chữ đạt chuẩn (chưa đạt: {lowc[:3]})")
    zl = pg.inner_text("#mnav .mz"); ok(re.search(r"Zalo \d", zl) is not None, f"menu: số Zalo cách chữ: '{zl.strip()}'")
    pg.locator("#mnav a", has_text="Về shop").click(); top = settle(pg, "document.getElementById('ve-shop').getBoundingClientRect().top")
    ok(pg.is_hidden("#mnav") and -5 < top < 300, f"chọn 'Về shop' → đóng menu và tới mục Về shop (cách đầu màn hình {round(top)} px)")
    pg.click("#mb"); pg.keyboard.press("Escape"); pg.wait_for_timeout(100); ok(pg.is_hidden("#mnav"), "phím Esc đóng menu")
    # 3. tìm kiếm không dấu, theo mã
    pg.evaluate("document.getElementById('san-pham').scrollIntoView()")
    def count(q):
        pg.fill("#q", q); pg.wait_for_timeout(150); show_all(pg); return pg.locator("#grid .card").count()
    a, c = count("giày"), count("giay")
    want = sum(1 for p in prods if "giay" in fold(p.get("display_title") or p["title"]) or "giay" in fold(p["category"]))
    ok(a == c and a > 0, f"tìm 'giay' (không dấu) ra {c}, bằng 'giày' ra {a}")
    ok(c >= want, f"tìm 'giay' tìm thấy đủ các sản phẩm có chữ giày ({c} ≥ {want})")
    sku = shoe["variants"][0]["sku"]
    ok(count(sku) >= 1 and pg.locator(f"#grid .card[data-pid='{shoe['id']}']").count() == 1, f"tìm theo mã {sku} ra đúng sản phẩm")
    ok(count("xyz khong co") == 0 and pg.is_visible("#grid .empty"), "từ khóa không có → báo không tìm thấy")
    pg.fill("#q", ""); pg.wait_for_timeout(150)
    # 4. quay lại giữ đúng chỗ
    pg.click("#more button"); pg.wait_for_timeout(150)
    before = go_detail_from_card(pg, 30); pg.go_back(); pg.wait_for_selector("#grid .card"); pg.wait_for_timeout(700)
    after = settle(pg, "scrollY")
    ok(abs(after - before) < 80, f"nút Back của trình duyệt → về đúng chỗ ({before} → {after})")
    before = go_detail_from_card(pg, 30); pg.click("a.back"); pg.wait_for_selector("#grid .card"); pg.wait_for_timeout(700)
    after = settle(pg, "scrollY")
    ok(abs(after - before) < 80, f"nút '← Tất cả sản phẩm' → về đúng chỗ ({before} → {after})")
    # 5. không có nút nổi che nút khác
    ok(not pg.is_visible("#fab"), "điện thoại: không còn nút Zalo nổi đè lên sản phẩm")
    ok(pg.is_visible("#bbar"), "điện thoại: có thanh dưới (Nhắn Zalo, Giỏ hàng)")
    covered = pg.evaluate("""()=>{const bar=document.getElementById('bbar').getBoundingClientRect();const bad=[];
      [...document.querySelectorAll('#grid .card .btn, #grid .card .szb:not(:disabled), #grid .card .clb')].slice(0,60).forEach(e=>{
        e.scrollIntoView({block:'end',behavior:'instant'});const r=e.getBoundingClientRect(),x=r.left+r.width/2,y=r.top+r.height/2,t=document.elementFromPoint(x,y);
        if(!t||!(t===e||e.contains(t)))bad.push(e.className+' '+e.textContent.trim().slice(0,12))});return bad}""")
    ok(not covered, f"bấm được mọi nút trên thẻ, không bị thanh dưới che (bị che: {covered[:3]})")
    pg.evaluate("scrollTo(0,document.documentElement.scrollHeight)"); pg.wait_for_timeout(200)
    gap = pg.evaluate("document.getElementById('bbar').getBoundingClientRect().top-document.querySelector('footer').getBoundingClientRect().bottom")
    ok(gap >= -1, f"cuộn hết trang: chân trang nằm trên thanh dưới (khoảng cách {round(gap)} px)")
    # 6. nút đủ lớn cho ngón tay (44 px)
    def small(sel_list):
        return pg.evaluate("""(sels)=>{const r=[];document.querySelectorAll(sels).forEach(e=>{const b=e.getBoundingClientRect();
          if(b.width>0&&b.height>0&&getComputedStyle(e).visibility!=='hidden'&&(b.height<43.5||b.width<43.5))r.push((e.className||e.id||e.tagName)+' '+e.textContent.trim().slice(0,10)+' '+Math.round(b.width)+'x'+Math.round(b.height))});return r}""", sel_list)
    pg.evaluate("scrollTo(0,0)")
    s1 = small("#grid .szb, #grid .clb, #grid .btn, .chip, .cat, #mb, #cb, #bbar a, #bbar button, .sel, #more button")
    ok(not s1, f"trang chủ: nút size, màu, thêm giỏ, danh mục, menu ≥ 44 px (nhỏ hơn: {s1[:4]})")
    # 7. giữ màu, size đã chọn khi sang trang chi tiết
    pg.goto(B + "/"); pg.wait_for_selector("#grid .card"); pg.fill("#q", multi["title"][:24]); pg.wait_for_timeout(200)
    card = pg.locator(f"#grid .card[data-pid='{multi['id']}']"); card.scroll_into_view_if_needed()
    c2 = [c for c in colors(multi) if any(v["option2"] == c and v["option1"] and v["inventory_quantity"] > 0 for v in multi["variants"])]
    pick = next(c for c in c2 if c != card.locator(".clb[aria-pressed='true']").inner_text())
    card.locator(".clb", has_text=pick).first.click(); pg.wait_for_timeout(120)
    vs = next(v for v in multi["variants"] if v["option2"] == pick and v["option1"] and v["inventory_quantity"] > 0)
    pg.locator(f"#grid .card[data-pid='{multi['id']}'] .szb[data-sz='{vs['option1']}']").click(); pg.wait_for_timeout(120)
    pg.locator(f"#grid .card[data-pid='{multi['id']}'] a.thumb").click(); pg.wait_for_selector(".det h1"); pg.wait_for_timeout(200)
    col = pg.locator(".opt[data-col][aria-pressed='true']").first.inner_text().split("\n")[0]
    szp = pg.locator(".opt[data-sz][aria-pressed='true']")
    ok(col == pick, f"chọn '{pick}' trên thẻ → trang chi tiết cũng chọn '{col}'")
    ok(szp.count() == 1 and szp.get_attribute("data-sz") == vs["option1"], f"size {vs['option1']} đã chọn trên thẻ được giữ ở trang chi tiết")
    s2 = small(".opt, #ad, .det .btn, a.back")
    ok(not s2, f"trang chi tiết: nút ≥ 44 px (nhỏ hơn: {s2[:4]})")
    # 8. vượt tồn kho: vẫn cho thêm, có cảnh báo
    pg.evaluate("localStorage.removeItem('cart5')"); pg.goto(B + "/"); pg.wait_for_selector("#grid .card")
    pg.fill("#q", one_left["title"][:24]); pg.wait_for_timeout(200)
    for _ in range(2):
        cd = pg.locator(f"#grid .card[data-pid='{one_left['id']}']")
        if v1["option1"]: cd.locator(f".szb[data-sz='{v1['option1']}']").click(); cd = pg.locator(f"#grid .card[data-pid='{one_left['id']}']")
        cd.locator("[data-quick]").click(); pg.wait_for_timeout(150)
    ok(pg.inner_text("#cn") == "2", "còn 1 mà thêm 2 → vẫn thêm được (không chặn cứng)")
    ok("vượt tồn kho" in pg.inner_text("#toast"), "thông báo: " + pg.inner_text("#toast")[:70])
    pg.click("#bbar button"); pg.wait_for_timeout(350)
    ok(pg.locator(".ci .ow").count() == 1 and "shop sẽ kiểm tra lại khi chốt đơn" in pg.inner_text(".ci .ow"), "giỏ hàng ghi rõ cảnh báo vượt tồn kho")
    lowc = pg.evaluate(CONTRAST, ".ci .ow, #dpick, #cc, .ci b, .ci span")
    ok(not lowc, f"giỏ hàng: tương phản chữ đạt chuẩn (chưa đạt: {lowc[:3]})")
    txt = pg.input_value("#ordtxt")
    ok("vượt tồn kho trên web" in txt and "kiểm tra lại khi chốt đơn" in txt, "tin nhắn gửi shop có ghi chú vượt tồn kho")
    # 9. bàn phím trong giỏ: focus vào giỏ, Tab không ra ngoài
    ok(pg.evaluate("!!document.activeElement.closest('#dr')"), "mở giỏ → con trỏ bàn phím vào trong giỏ")
    out = []
    for _ in range(12):
        pg.keyboard.press("Tab"); out.append(pg.evaluate("!!document.activeElement.closest('#dr')"))
    ok(all(out), "Tab chỉ đi trong giỏ khi giỏ đang mở")
    s3 = small("#dr button, #dr .btn")
    ok(not s3, f"giỏ hàng: nút ≥ 44 px (nhỏ hơn: {s3[:4]})")
    ok("8:00–21:00" in pg.inner_text("#dpick") and ") (" not in pg.inner_text("#dpick"), "giỏ hàng ghi giờ mở cửa, câu gọn: " + pg.inner_text("#dpick")[-60:])
    # 10. hỏi lại trước khi xóa giỏ
    pg.click("#cc"); pg.wait_for_timeout(100)
    ok(pg.is_visible("#ccq") and pg.locator(".ci").count() == 1, "bấm Xóa giỏ hàng → hỏi lại, chưa xóa")
    lowc = pg.evaluate(CONTRAST, "#ccq span, #ccq button"); ok(not lowc, f"hỏi lại xóa giỏ: tương phản đạt chuẩn (chưa đạt: {lowc[:3]})")
    pg.click("#ccn"); pg.wait_for_timeout(100); ok(pg.locator(".ci").count() == 1 and pg.is_visible("#cc"), "bấm Giữ lại → giỏ còn nguyên")
    pg.click("#cc"); pg.click("#ccy"); pg.wait_for_timeout(150)
    ok(pg.locator(".ci").count() == 0 and pg.is_hidden("#cn"), "bấm Xóa hết → giỏ trống")
    pg.keyboard.press("Escape"); pg.wait_for_timeout(300)
    ok(pg.evaluate("document.getElementById('dr').inert===true||document.getElementById('dr').hasAttribute('inert')"), "giỏ đóng → các nút trong giỏ không nằm trong thứ tự phím Tab")
    ok("8:00–21:00" in pg.inner_text("footer"), "chân trang ghi giờ mở cửa")
    ok(not pg.evaluate("document.documentElement.scrollWidth>document.documentElement.clientWidth"), "không tràn ngang")
    ctx.close()

def desktop(b):
    print("\n===== MÁY TÍNH =====")
    for w in (1366, 1066):
        ctx = b.new_context(viewport={"width": w, "height": 860}, locale="vi-VN"); pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(B + "/"); pg.wait_for_selector("#grid .card"); pg.wait_for_timeout(200)
        fab = pg.is_visible("#fab")
        if fab:
            hit = pg.evaluate("""()=>{const f=document.getElementById('fab').getBoundingClientRect(),g=document.getElementById('grid').getBoundingClientRect();return f.left<g.right+4}""")
            ok(not hit, f"{w} px: nút Zalo nổi nằm ngoài vùng sản phẩm")
        else:
            ok(pg.is_visible("#hz"), f"{w} px: không có nút nổi đè sản phẩm, nút Zalo nằm trên thanh đầu trang")
        ok(pg.locator("#grid .card").count() == min(PAGE, len(prods)) and pg.is_visible("#more"), f"{w} px: hiện 20 sản phẩm + nút Xem thêm")
        ok("8:00–21:00" in pg.inner_text(".strip") or "8:00–21:00" in pg.inner_text("footer"), f"{w} px: có giờ mở cửa")
        ctx.close()

def admin(b):
    if not HAS_API: print("\n(web tĩnh: bỏ qua phần trang quản trị)"); return
    print("\n===== QUẢN TRỊ: ĐĂNG XUẤT =====")
    ctx = b.new_context(); pg = ctx.new_page()
    pg.goto(B + "/admin"); pg.wait_for_selector("#pw", state="visible")
    pg.fill("#pw", os.environ.get("ADMIN_PASSWORD") or "admin123"); pg.click("#lb"); pg.wait_for_selector("#app:not([hidden])")
    ok(ctx.request.get(B + "/api/admin/products").status == 200, "đăng nhập được")
    pg.click("#out"); pg.wait_for_load_state("load"); pg.wait_for_timeout(600)
    ok(pg.is_visible("#login") and pg.is_hidden("#app"), "bấm Đăng xuất → về màn hình đăng nhập")
    pg.reload(); pg.wait_for_timeout(600)
    ok(pg.is_visible("#login"), "tải lại trang vẫn phải đăng nhập lại")
    ok(ctx.request.get(B + "/api/admin/products").status == 401, "phiên cũ không còn dùng được")
    ctx.close()

with sync_playwright() as pw:
    b = pw.chromium.launch()
    mobile(b, "light"); mobile(b, "dark"); desktop(b); admin(b)
    b.close()
print("\nLỖI JS:", errs[:3]); print("KẾT QUẢ:", len(fails) + len(errs), "lỗi"); print(fails)
