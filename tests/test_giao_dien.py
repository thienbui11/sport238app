"""Kiểm thử chống tái phát cho giao diện mới (D1–D4, 24/11/2026), trên trình duyệt thật.
- Không có emoji làm hình trang trí (ô danh mục, ô giữ chỗ ảnh, nút, thanh trên/dưới, chân trang, CSS); ô danh mục và ô giữ chỗ dùng SVG.
- Điện thoại: thanh "Thêm vào giỏ" ở trang chi tiết dính đáy màn hình, thay cho thanh dưới (không chồng 2 thanh),
  không che nút/link nào, bấm được, chân trang không bị che.
- Không tràn ngang ở 320 / 390 / 768 / 1366 px (trang chủ, trang chi tiết, menu, giỏ hàng).
- Không có chuyển động lặp vô hạn, không dùng backdrop-filter; bật "giảm chuyển động" thì tắt hiệu ứng.
- Tương phản chữ đạt WCAG AA (4,5:1; chữ lớn 3:1) cho các thành phần mới, chế độ sáng và tối.
- Ảnh/ô giữ chỗ có khung vuông cố định (không giật bố cục); ô giữ chỗ tô theo màu sản phẩm.
Chạy:  py tests/test_giao_dien.py http://localhost:3602      (in "KẾT QUẢ: N lỗi")"""
import json, re, sys, urllib.request
from playwright.sync_api import sync_playwright

B = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000").rstrip("/")
try: api = json.load(urllib.request.urlopen(B + "/api/products"))
except Exception: api = json.load(urllib.request.urlopen(B + "/products.json"))
prods = api["products"]; fails = []; errs = []


def ok(c, m):
    print(("  ✓ " if c else "  ✗ ") + m)
    if not c: fails.append(m)


def colors(p):
    u = []
    for v in p["variants"]:
        if v["option2"] not in u: u.append(v["option2"])
    return u


# sản phẩm có size, nhiều màu/loại, còn hàng (để thử thanh "Thêm vào giỏ")
SIZED = next(p for p in prods if len(colors(p)) > 1 and any(v["option1"] and v["inventory_quantity"] > 0 for v in p["variants"]))
EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿⬀-⯿️‼⁉™ℹ⌚-⏿]")
UI = ".strip, .nav, #mnav, .hero, .perks, .sh, .cat, .chips, .tools, .thumb, .badge, .cinfo .btn, .stk, .promo, #ve-shop, #cach-mua, footer, #bbar, .back, .gal, .crumb, .lab, .legend, .note, .st, .buy, .ask, .visit2, #dr"

CONTRAST = r"""(sels)=>{const lum=c=>{const m=c.match(/[\d.]+/g).map(Number);const [r,g,b]=m.slice(0,3).map(v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)});return .2126*r+.7152*g+.0722*b};
  const bg=e=>{for(;e;e=e.parentElement){const s=getComputedStyle(e),m=s.backgroundColor.match(/[\d.]+/g);if(m&&(m[3]===undefined||+m[3]>.9))return s.backgroundColor}return getComputedStyle(document.body).backgroundColor};
  const bad=[];document.querySelectorAll(sels).forEach(e=>{const r=e.getBoundingClientRect();if(!r.width||e.disabled||!e.textContent.trim())return;const cs=getComputedStyle(e);if(cs.visibility==='hidden')return;const a=lum(cs.color),b=lum(bg(e)),cr=(Math.max(a,b)+.05)/(Math.min(a,b)+.05);
  const big=parseFloat(cs.fontSize)>=24||(parseFloat(cs.fontSize)>=18.6&&+cs.fontWeight>=700);if(cr<(big?3:4.5))bad.push((e.id||e.className||e.tagName)+' "'+e.textContent.trim().slice(0,16)+'" '+cr.toFixed(2))});return bad}"""

HOME_TXT = (".strip span, .strip a, .logo, .kick, .hero h1, .hero h1 em, .hero .lead, .hbtns .btn, .stat b, .stat span, .perks b, .perks small, "
            ".sh h2, .sh .sub, .cat b, .cat span, .chip, #cnt, .cinfo small, .cinfo h3 a, .price, .stk, .badge, .szb, .clb, #grid .btn, #moreb, "
            ".promo h2, .promo p, .promo .btn, .panel p, .tags span, .info li span, .links .btn, .step i, .step b, .step p, .cta .btn, "
            "footer p, footer li span, footer a, #bbar a, #bbar button, .menu a, .hz, .visit b, .visit span, .visit .btn")
DET_TXT = ".back, .pill, .crumb span, .det h1, .bigp, .lab, .lab small, .opt, .opt small, .legend, .note, .st, #ad, .ask, .upd, .phnote, .visit2 h2, .visit2 li span, .visit2 .btn"
CART_TXT = ".dh h3, .dh h3 small, .ci b, .ci span, .qty span, .rm, .ordh b, .cpb, .pick span, .sum span, #dt, #zs, #fs, .dempty p"


def overflow(pg):
    return pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")


def home(pg):
    pg.goto(B + "/"); pg.wait_for_selector("#grid .card"); pg.wait_for_timeout(250)


def detail(pg, pid):
    pg.goto(B + "/#p-" + pid); pg.wait_for_selector(".det h1"); pg.wait_for_timeout(250)


def no_emoji(pg, where):
    txt = pg.evaluate("(s)=>[...document.querySelectorAll(s)].map(e=>e.innerText||'').join('\\n')", UI)
    found = sorted(set(EMOJI.findall(txt)))
    ok(not found, f"{where}: không có emoji trang trí trong giao diện (thấy: {found[:6]})")


with sync_playwright() as pw:
    b = pw.chromium.launch()

    print("\n===== 1. Biểu tượng SVG, không emoji =====")
    ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, locale="vi-VN")
    pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
    home(pg)
    no_emoji(pg, "trang chủ")
    cats = pg.evaluate("[...document.querySelectorAll('.cat')].map(c=>[!!c.querySelector('i svg'),(c.querySelector('i').textContent||'').trim()])")
    ok(len(cats) == 9 and all(s and not t for s, t in cats), "9 ô danh mục: biểu tượng là SVG, không có chữ/emoji trong ô hình")
    ph = pg.evaluate("[...document.querySelectorAll('#grid .card .thumb')].map(t=>!!t.querySelector('img')||(!!t.querySelector('.ph svg use')&&!(t.querySelector('.ph').textContent||'').trim()))")
    ok(ph and all(ph), f"{len(ph)} thẻ: có ảnh thật hoặc ô giữ chỗ bằng SVG (không emoji, không chữ)")
    css = pg.evaluate("[...document.styleSheets].map(s=>{try{return [...s.cssRules].map(r=>r.cssText).join('\\n')}catch(e){return ''}}).join('\\n')")
    ok(not EMOJI.search(css), "CSS không chèn emoji (content: …)")
    red = next((p for p in prods if len(colors(p)) == 1 and re.search(r"(?i)\bđỏ\b", p.get("display_title") or p["title"]) and not re.search(r"(?i)đô", p.get("display_title") or p["title"])), None)
    if red:
        pg.fill("#q", red["id"]); pg.wait_for_timeout(200)
        fill = pg.evaluate("(id)=>{const s=document.querySelector(`#grid .card[data-pid='${id}'] .ph svg`);return s&&s.style.getPropertyValue('--a')}", red["id"])
        ok(fill == "#d0202e", f"ô giữ chỗ tô theo màu sản phẩm: '{red['title']}' → {fill}")
        pg.fill("#q", "")
    detail(pg, SIZED["id"]); no_emoji(pg, "trang chi tiết")
    pg.click("#cb"); pg.wait_for_timeout(300); no_emoji(pg, "giỏ hàng"); pg.keyboard.press("Escape")
    ctx.close()

    print("\n===== 2. Chuyển động, backdrop-filter =====")
    ctx = b.new_context(viewport={"width": 1366, "height": 860}, locale="vi-VN"); pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
    for name, go in [("trang chủ", lambda: home(pg)), ("trang chi tiết", lambda: detail(pg, SIZED["id"]))]:
        go()
        inf = pg.evaluate("document.getAnimations().filter(a=>a.effect&&a.effect.getTiming().iterations===Infinity).length")
        loops = pg.evaluate("[...document.querySelectorAll('*')].filter(e=>{const s=getComputedStyle(e);return s.animationName!=='none'&&s.animationIterationCount==='infinite'}).length")
        bf = pg.evaluate("[...document.querySelectorAll('*')].filter(e=>{const s=getComputedStyle(e);return (s.backdropFilter&&s.backdropFilter!=='none')||(s.webkitBackdropFilter&&s.webkitBackdropFilter!=='none')}).length")
        ok(inf == 0 and loops == 0, f"{name}: không có chuyển động lặp vô hạn ({inf} hoạt ảnh, {loops} phần tử)")
        ok(bf == 0, f"{name}: không dùng backdrop-filter ({bf})")
    css = pg.evaluate("[...document.styleSheets].map(s=>{try{return [...s.cssRules].map(r=>r.cssText).join('\\n')}catch(e){return ''}}).join('\\n')")
    ok("infinite" not in css and "backdrop-filter" not in css, "CSS không có 'infinite' và 'backdrop-filter'")
    ctx.close()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, reduced_motion="reduce"); pg = ctx.new_page()
    home(pg)
    rm = pg.evaluate("(()=>{const s=getComputedStyle(document.querySelector('#grid .btn')),h=getComputedStyle(document.documentElement);return [s.transitionDuration,h.scrollBehavior]})()")
    ok(all(d in ("0s", "0") for d in rm[0].split(", ")) and rm[1] == "auto", f"bật giảm chuyển động: tắt hiệu ứng, cuộn tức thì ({rm})")
    ctx.close()

    print("\n===== 3. Không tràn ngang =====")
    for w in (320, 390, 768, 1366):
        mob = w < 800
        ctx = b.new_context(viewport={"width": w, "height": 800}, is_mobile=mob, has_touch=mob, locale="vi-VN"); pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        res = []
        home(pg); res.append(("trang chủ", overflow(pg)))
        pg.evaluate("scrollTo(0,document.documentElement.scrollHeight)"); pg.wait_for_timeout(150); res.append(("cuối trang", overflow(pg)))
        if pg.locator("#mb").is_visible():
            pg.evaluate("scrollTo(0,0)"); pg.click("#mb"); pg.wait_for_timeout(150); res.append(("menu", overflow(pg))); pg.keyboard.press("Escape")
        detail(pg, SIZED["id"]); res.append(("chi tiết", overflow(pg)))
        pg.locator(".opt[data-sz]:not(.out)").first.click(); pg.click("#ad"); pg.wait_for_timeout(150)
        pg.click("#cb"); pg.wait_for_timeout(300); res.append(("giỏ hàng", overflow(pg)))
        dw = pg.evaluate("(()=>{const r=document.getElementById('dr').getBoundingClientRect();return [Math.round(r.left),Math.round(r.right),innerWidth]})()")
        bad = [f"{n} +{o}px" for n, o in res if o > 0]
        ok(not bad and dw[0] >= 0 and dw[1] <= dw[2], f"{w} px: không tràn ngang (trang chủ, menu, chi tiết, giỏ) {bad}")
        ctx.close()

    print("\n===== 4. Điện thoại: thanh 'Thêm vào giỏ' dính đáy màn hình =====")
    for w in (390, 320):
        ctx = b.new_context(viewport={"width": w, "height": 720}, is_mobile=True, has_touch=True, locale="vi-VN"); pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        detail(pg, SIZED["id"])
        bar = pg.evaluate("(()=>{const e=document.querySelector('.buy'),r=e.getBoundingClientRect(),a=document.getElementById('ad').getBoundingClientRect();return {pos:getComputedStyle(e).position,top:r.top,bottom:r.bottom,h:innerHeight,ad:[a.top,a.bottom,a.width,a.height]}})()")
        ok(bar["pos"] == "fixed" and abs(bar["bottom"] - bar["h"]) <= 1, f"{w} px: thanh cố định sát đáy màn hình (đáy {round(bar['bottom'])} / {bar['h']})")
        ok(bar["ad"][0] >= bar["top"] and bar["ad"][1] <= bar["h"] and bar["ad"][3] >= 44, f"{w} px: nút 'Thêm vào giỏ' thấy ngay khi mở trang, cao {round(bar['ad'][3])} px")
        ok(pg.is_hidden("#bbar"), f"{w} px: trang chi tiết không chồng thêm thanh dưới (Zalo, giỏ nằm trong thanh mới)")
        one = pg.evaluate("(()=>{const t=document.querySelector('#ad').innerText.trim();const r=document.getElementById('ad').getBoundingClientRect();return [t,Math.round(r.height)]})()")
        ok(one[1] <= 52, f"{w} px: chữ trên nút không xuống dòng ('{one[0]}', cao {one[1]} px)")
        small = pg.evaluate("[...document.querySelectorAll('.buy a, .buy button')].filter(e=>e.offsetParent).map(e=>{const r=e.getBoundingClientRect();return r.width<44||r.height<44?e.className+' '+Math.round(r.width)+'x'+Math.round(r.height):''}).filter(Boolean)")
        ok(not small, f"{w} px: các nút trên thanh ≥ 44 px ({small})")
        covered = pg.evaluate("""()=>{const bad=[];const bar=document.querySelector('.buy');
          [...document.querySelectorAll('main a[href], main button:not(:disabled)')].filter(e=>!bar.contains(e)&&e.offsetParent).forEach(e=>{
            e.scrollIntoView({block:'end',behavior:'instant'});const r=e.getBoundingClientRect(),x=r.left+r.width/2,y=r.top+r.height/2,t=document.elementFromPoint(x,y);
            if(!t||!(t===e||e.contains(t)))bad.push((e.id||e.className)+' '+e.textContent.trim().slice(0,14))});return bad}""")
        ok(not covered, f"{w} px: cuộn tới đâu cũng bấm được mọi nút/link, thanh không che (bị che: {covered[:3]})")
        pg.evaluate("scrollTo(0,document.documentElement.scrollHeight)"); pg.wait_for_timeout(150)
        gap = pg.evaluate("document.querySelector('.buy').getBoundingClientRect().top-document.querySelector('footer').getBoundingClientRect().bottom")
        ok(gap >= -1, f"{w} px: cuộn hết trang, chân trang nằm trên thanh (khoảng cách {round(gap)} px)")
        # bấm "Thêm vào giỏ" khi chưa chọn size: báo lỗi, đưa khung size ra giữa màn hình
        pg.evaluate("scrollTo(0,0)"); pg.click("#ad"); pg.wait_for_timeout(700)
        need = pg.evaluate("(()=>{const g=document.querySelector('.grp.need');if(!g)return null;const r=g.getBoundingClientRect(),b=document.querySelector('.buy').getBoundingClientRect();return r.top>=0&&r.top<b.top})()")
        ok("chưa chọn size" in pg.inner_text("#toast").lower() and need, f"{w} px: chưa chọn size → báo lỗi và đưa khung chọn size ra trước mắt")
        v = next(x for x in SIZED["variants"] if x["option1"] and x["inventory_quantity"] > 0)
        if len(colors(SIZED)) > 1: pg.click(f".opt[data-col='{v['option2']}']")
        pg.click(f".opt[data-sz='{v['option1']}']"); pg.click("#ad"); pg.wait_for_timeout(200)
        ok(pg.inner_text("#cn") == "1" and pg.inner_text(".buy .cnt") == "1", f"{w} px: bấm 'Thêm vào giỏ' trên thanh → giỏ có 1 món (số trên thanh và đầu trang)")
        pg.click(".buy button.ib"); pg.wait_for_timeout(350)
        ok(pg.is_visible("#dr") and pg.locator(".ci").count() == 1, f"{w} px: nút giỏ trên thanh mở giỏ hàng")
        ctx.close()
    ctx = b.new_context(viewport={"width": 1366, "height": 860}); pg = ctx.new_page()
    detail(pg, SIZED["id"])
    st = pg.evaluate("(()=>[getComputedStyle(document.querySelector('.buy')).position,[...document.querySelectorAll('.buy .ib')].filter(e=>e.offsetParent).length])()")
    ok(st[0] != "fixed" and st[1] == 0, f"máy tính: nút 'Thêm vào giỏ' nằm trong cột thông tin, không có thanh dính ({st})")
    ctx.close()

    print("\n===== 5. Tương phản chữ (sáng, tối) =====")
    for scheme in ("light", "dark"):
        for w, mob in ((390, True), (1366, False)):
            tag = f"{'tối' if scheme == 'dark' else 'sáng'}, {w} px"
            ctx = b.new_context(viewport={"width": w, "height": 844}, is_mobile=mob, has_touch=mob, color_scheme=scheme, locale="vi-VN"); pg = ctx.new_page()
            home(pg)
            if scheme == "dark":
                bgc = pg.evaluate("getComputedStyle(document.body).backgroundColor")
                ok(sum(int(x) for x in re.findall(r"\d+", bgc)[:3]) < 120, f"chế độ tối: nền trang tối ({bgc})")
            low = pg.evaluate(CONTRAST, HOME_TXT); ok(not low, f"trang chủ ({tag}): tương phản đạt (chưa đạt: {low[:4]})")
            if mob:
                pg.evaluate("scrollTo(0,0)"); pg.click("#mb"); pg.wait_for_timeout(150)
                low = pg.evaluate(CONTRAST, "#mnav a, #mnav p span"); ok(not low, f"menu ({tag}): tương phản đạt (chưa đạt: {low[:4]})"); pg.keyboard.press("Escape")
            detail(pg, SIZED["id"])
            pg.locator(".opt[data-sz]:not(.out)").first.click(); pg.wait_for_timeout(100)
            low = pg.evaluate(CONTRAST, DET_TXT); ok(not low, f"trang chi tiết ({tag}): tương phản đạt (chưa đạt: {low[:4]})")
            pg.click("#ad"); pg.click("#cb"); pg.wait_for_timeout(350)
            low = pg.evaluate(CONTRAST, CART_TXT); ok(not low, f"giỏ hàng ({tag}): tương phản đạt (chưa đạt: {low[:4]})")
            pg.click("#cc"); pg.wait_for_timeout(100)
            low = pg.evaluate(CONTRAST, "#ccq span, #ccq button"); ok(not low, f"hỏi lại xóa giỏ ({tag}): tương phản đạt (chưa đạt: {low[:4]})")
            ctx.close()

    print("\n===== 6. Không giật bố cục (ảnh có khung cố định) =====")
    ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True); pg = ctx.new_page()
    pg.add_init_script("window.__cls=0;new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__cls+=e.value}).observe({type:'layout-shift',buffered:true})")
    home(pg); pg.wait_for_timeout(800)
    sq = pg.evaluate("[...document.querySelectorAll('#grid .thumb')].every(t=>{const r=t.getBoundingClientRect();return Math.abs(r.width-r.height)<1.5})")
    imgs = pg.evaluate("[...document.querySelectorAll('main img')].filter(i=>!(i.getAttribute('width')&&i.getAttribute('height'))).map(i=>i.src)")
    cls = pg.evaluate("window.__cls")
    ok(sq, "khung ảnh/ô giữ chỗ trên thẻ luôn vuông")
    ok(not imgs, f"mọi ảnh có width/height (không giật bố cục) {imgs[:2]}")
    ok(cls < 0.05, f"độ giật bố cục khi tải trang chủ (CLS) = {cls:.3f} (< 0,05)")
    ctx.close()

    print("\n===== 7. Nút tìm nhanh ở đầu trang =====")
    for w in (390, 1366):
        ctx = b.new_context(viewport={"width": w, "height": 800}); pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        home(pg); pg.click("#hs"); pg.wait_for_timeout(900)
        a = pg.evaluate("[document.activeElement.id,Math.round(document.getElementById('q').getBoundingClientRect().top)]")
        ok(a[0] == "q" and 0 <= a[1] < 400, f"{w} px, trang chủ: bấm nút tìm → con trỏ vào ô tìm, ô tìm trong màn hình ({a})")
        detail(pg, SIZED["id"]); pg.click("#hs"); pg.wait_for_selector("#grid .card"); pg.wait_for_timeout(1200)
        a = pg.evaluate("[document.activeElement.id,Math.round(document.getElementById('q').getBoundingClientRect().top)]")
        ok(a[0] == "q" and 0 <= a[1] < 400, f"{w} px, trang chi tiết: bấm nút tìm → về danh sách, con trỏ vào ô tìm ({a})")
        ctx.close()

    print("\n===== 8. Sửa sau rà soát (24/11/2026) =====")
    # 8a. "Giảm chuyển động": cuộn tức thì, không cuộn mượt (lệnh cuộn trong mã không được ép "smooth")
    ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, reduced_motion="reduce"); pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
    home(pg); pg.locator(".cat[data-go]").first.click(); pg.wait_for_timeout(60)
    y1 = pg.evaluate("scrollY"); pg.wait_for_timeout(1200); y2 = pg.evaluate("scrollY")
    ok(y1 > 300 and abs(y2 - y1) < 5, f"giảm chuyển động: bấm danh mục → tới danh sách ngay, không cuộn mượt ({y1} → {y2})")
    # 8b. vào trang chủ bình thường: không tự đưa con trỏ vào ô tìm
    home(pg); pg.wait_for_timeout(300)
    ok(pg.evaluate("document.activeElement.id") != "q", "vào trang chủ bình thường: con trỏ không tự nhảy vào ô tìm")
    # 8c. hình minh họa không in số (dễ tưởng áo thật có số); nút Zalo ở phần mở đầu ẩn trên điện thoại (thanh dưới đã có)
    ok(pg.evaluate("document.querySelectorAll('svg text').length") == 0, "hình minh họa không in chữ/số lên áo")
    ok(not pg.locator(".hbtns [data-zl]").first.is_visible(), "điện thoại: phần mở đầu không lặp nút Zalo (thanh dưới đã có)")
    # 8d. dòng nhỏ trên tên: SP có hãng chỉ hiện hãng, không bị cắt
    bad = pg.evaluate("""()=>[...document.querySelectorAll('#grid .cinfo small')].filter(s=>s.scrollWidth>s.clientWidth+1).map(s=>s.innerText)""")
    hb = pg.evaluate("""()=>[...document.querySelectorAll('#grid .cinfo small.hb')].map(s=>s.innerText.trim())""")
    ok(not bad and hb and all("·" not in t for t in hb), f"điện thoại: dòng hãng/danh mục trên thẻ không bị cắt (bị cắt: {bad[:2]}; mẫu: {hb[:3]})")
    # 8e. size hết hàng trên thẻ: viền nét đứt, chữ không mờ
    st = pg.evaluate("(()=>{const e=document.querySelector('#grid .szb:disabled');if(!e)return null;const s=getComputedStyle(e);return [s.borderTopStyle,s.opacity]})()")
    ok(st is not None and st[0] == "dashed" and float(st[1]) == 1, f"size hết hàng trên thẻ: viền nét đứt, không làm mờ ({st})")
    # 8f. giỏ hàng: nút bỏ từng món (≥ 44 px, có nhãn đọc màn hình)
    two = [v["id"] for p in prods for v in p["variants"] if v["inventory_quantity"] > 0][:2]
    pg.evaluate("ids=>localStorage.setItem('cart5',JSON.stringify(ids.map(id=>({id,lb:'',qty:2}))))", two)
    pg.reload(); pg.wait_for_selector("#grid .card"); pg.click("#bc" if pg.locator("#bc").is_visible() else "#cb"); pg.wait_for_timeout(400)
    rm = pg.locator(".ci .rmi")
    lab = rm.first.get_attribute("aria-label") or ""
    box = rm.first.bounding_box()
    ok(rm.count() == 2 and lab.startswith("Bỏ ") and box and box["width"] >= 43.5 and box["height"] >= 43.5, f"giỏ: mỗi món có nút bỏ khỏi giỏ ≥ 44 px ('{lab}')")
    rm.first.click(); pg.wait_for_timeout(200)
    ok(pg.locator(".ci").count() == 1 and pg.inner_text("#cn").strip() == "2", "bấm nút bỏ → món đó ra khỏi giỏ (cả số lượng), món kia còn nguyên")
    ctx.close()
    # 8g. máy tính: thẻ "Ghé shop" không lặp ý với dải lợi ích
    ctx = b.new_context(viewport={"width": 1366, "height": 860}); pg = ctx.new_page(); home(pg)
    ok("giữ đúng size" not in pg.inner_text(".visit"), "máy tính: thẻ Ghé shop chỉ có địa chỉ, giờ, nút (không lặp ý)")
    ok(pg.locator(".hbtns [data-zl]").first.is_visible(), "máy tính: phần mở đầu vẫn có nút Nhắn Zalo")
    ctx.close()
    b.close()

print("\nLỖI JS:", errs[:3]); print("KẾT QUẢ:", len(fails) + len(errs), "lỗi"); print(fails)
