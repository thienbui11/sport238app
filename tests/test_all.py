import os
OUTDIR=os.path.join(os.path.dirname(os.path.abspath(__file__)),"out");os.makedirs(OUTDIR,exist_ok=True)
import json,re,sys,urllib.request
from playwright.sync_api import sync_playwright
B=sys.argv[1] if len(sys.argv)>1 else "http://localhost:3000"
try:
    api=json.load(urllib.request.urlopen(B+"/api/products"))
except Exception:
    api=json.load(urllib.request.urlopen(B+"/products.json"))   # web tĩnh
prods=api["products"]
print("API:",len(prods),"sản phẩm")
fails=[];errs=[]
def show_all(pg):
    # danh sách hiện 20 sản phẩm mỗi lần; bấm "Xem thêm" cho tới hết
    while pg.locator("#more").is_visible(): pg.click("#more button"); pg.wait_for_timeout(40)
def fail(m):
    fails.append(m); print("  ✗",m)
with sync_playwright() as p:
    b=p.chromium.launch();ctx=b.new_context(viewport={"width":1066,"height":800});pg=ctx.new_page()
    pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.on("console",lambda m:errs.append(m.text) if m.type=="error" and "ERR_NAME_NOT_RESOLVED" not in m.text and "Failed to load resource" not in m.text else None)
    pg.goto(B+"/");pg.wait_for_selector(".cats .cat")
    # 1. trang chủ
    n=pg.eval_on_selector(".stats .stat b","e=>e.textContent");print("Hero thống kê:",n)
    if int(n)!=len(prods):fail(f"số sản phẩm hero {n} != {len(prods)}")
    lines=pg.evaluate("(()=>{const h=document.querySelector('.hero h1');return Math.round(h.getBoundingClientRect().height/parseFloat(getComputedStyle(h).lineHeight))})()")
    print("Số dòng tiêu đề hero:",lines)
    if lines>3:fail(f"tiêu đề hero {lines} dòng")
    tiles=pg.eval_on_selector_all(".cat","els=>els.map(e=>[e.querySelector('b').textContent,e.querySelector('span').textContent])")
    print("Ô danh mục:",tiles)
    if len(tiles)!=8:fail("không đủ 8 ô danh mục")
    # 2. không có chữ ship/giao hàng
    html=pg.content()
    bad=re.findall(r"(?i)\bship\b|giao hàng|phí giao|gửi hàng|vận chuyển",pg.inner_text("body"))
    pg.click("#cb");txt=pg.inner_text("#dr");bad+=re.findall(r"(?i)\bship\b|giao hàng|phí giao|gửi hàng",txt);pg.click("#dx")
    if bad:fail(f"còn chữ giao/ship: {bad}")
    # 3. link Facebook
    for sel,want in [("#sfb","https://www.facebook.com/Sport238"),("#ff","https://www.facebook.com/Sport238"),("#fs","https://m.me/Sport238"),("[data-fp]","https://www.facebook.com/Sport238"),("[data-fb]","https://m.me/Sport238"),("#fab","https://zalo.me/0962374770")]:
        got=pg.get_attribute(sel,"href")
        print(" ",sel,"→",got)
        if got!=want:fail(f"{sel}: {got} != {want}")
    # 4. lọc theo danh mục
    for c in ["Cờ, Cúp, Huy Chương","Giày bóng đá","Quần áo CLB/Đội tuyển","Quần áo không logo","Quần áo trẻ em","Phụ kiện thể thao","Vớ/tất ống đồng","Cầu lông"]:
        pg.click(f".cat[data-go='{c}']");pg.wait_for_timeout(120);show_all(pg)
        got=pg.eval_on_selector_all("#grid .card","e=>e.length");want=sum(1 for x in prods if x["category"]==c)
        if got!=want:fail(f"danh mục {c}: hiện {got}, đúng {want}")
    pg.click(".chip[data-c='Tất cả']");pg.wait_for_timeout(100);show_all(pg)
    if pg.eval_on_selector_all("#grid .card","e=>e.length")!=len(prods):fail("chip Tất cả sai số lượng")
    # 6. chip size trên thẻ
    withsz=sum(1 for x in prods if any(v["option1"] for v in x["variants"]))
    cards_sz=pg.eval_on_selector_all("#grid .card","els=>els.filter(e=>e.querySelector('.sz')).length")
    print("Sản phẩm có size:",withsz,"| thẻ hiện chip size:",cards_sz)
    if withsz!=cards_sz:fail("thẻ sản phẩm thiếu chip size")
    # 5. từng trang chi tiết
    errs.clear();checked=0
    for x in prods:
        pg.goto(B+"/#p-"+x["id"]);pg.wait_for_selector(".det h1")
        sizes=sorted({v["option1"] for v in x["variants"] if v["option1"]})
        got=pg.eval_on_selector_all(".opt[data-sz]","e=>e.map(b=>b.dataset.sz)")
        if sorted(got)!=sizes:fail(f"{x['title']}: size hiện {got} khác {sizes}");continue
        if sizes:
            # chọn size còn hàng nếu có
            colors={v["option2"] for v in x["variants"]}
            instock=[v for v in x["variants"] if v["inventory_quantity"]>0]
            if instock:
                v=instock[0]
                if len(colors)>1:pg.click(f"[data-col='{v['option2']}']")
                pg.click(f"[data-sz='{v['option1']}']")
                pg.click("#ad");pg.wait_for_timeout(30)
            else:
                pg.click(f"[data-sz='{sizes[0]}']")
                if not pg.is_disabled("#ad"):fail(f"{x['title']}: hết hàng nhưng nút thêm vẫn bật")
        elif x["category"] in("Giày bóng đá","Quần áo CLB/Đội tuyển","Quần áo không logo","Quần áo trẻ em"):
            if not pg.query_selector(".note"):fail(f"{x['title']}: thiếu ghi chú chưa có size")
        checked+=1
    print("Đã kiểm tra",checked,"trang chi tiết")
    if errs:fail(f"lỗi JS: {errs[:3]}")
    pg.goto(B+"/#p-"+prods[0]["id"]);pg.wait_for_selector(".det h1");pg.click(".menu a[data-s='san-pham']");pg.wait_for_selector("#grid .card")
    print("Bấm menu 'Sản phẩm' từ trang chi tiết →",pg.url.split('/')[-1],"| thấy lưới sản phẩm:",pg.query_selector('#grid') is not None)
    # 7. giỏ hàng
    pg.goto(B+"/");pg.wait_for_selector(".cat");pg.wait_for_timeout(300)
    saved=pg.evaluate("JSON.parse(localStorage.getItem('cart5')||'[]')")
    price={v["id"]:v["price"] for x in prods for v in x["variants"]}
    want=sum(price[i["id"]]*i["qty"] for i in saved)
    n=pg.eval_on_selector("#cn","e=>e.textContent");print("Giỏ sau khi tải lại trang:",n,"món")
    pg.click("#cb");pg.wait_for_timeout(300)
    rows=pg.eval_on_selector_all(".ci","e=>e.length");total=pg.inner_text("#dt");print("Dòng trong giỏ:",rows,"| Tạm tính:",total)
    if rows!=len(saved):fail(f"giỏ hiện {rows} dòng, đã lưu {len(saved)}")
    if total.replace(".","").replace("đ","")!=str(want):fail(f"tạm tính {total} != {want}")
    first=pg.query_selector(".ci [data-q='1']")
    if first:first.click()
    ot=pg.evaluate("document.querySelector('#dpick').textContent");print("Ghi chú nhận hàng:",ot[:60],"…")
    pg.screenshot(path=OUTDIR+"/t_cart.png")
    pg.click("#cc");pg.click("#ccy");pg.wait_for_timeout(100)
    # 8. điện thoại
    m=b.new_context(viewport={"width":390,"height":844}).new_page()
    m.goto(B+"/");m.wait_for_selector(".cat")
    ov=m.evaluate("document.documentElement.scrollWidth>document.documentElement.clientWidth")
    print("Điện thoại: tràn ngang trang chủ =",ov)
    if ov:fail("trang chủ bị tràn ngang trên điện thoại")
    m.screenshot(path=OUTDIR+"/t_m1.png")
    m.goto(B+"/#p-"+[x for x in prods if x["category"]=="Giày bóng đá"][0]["id"]);m.wait_for_selector(".det h1")
    if m.evaluate("document.documentElement.scrollWidth>document.documentElement.clientWidth"):fail("trang chi tiết bị tràn ngang trên điện thoại")
    m.screenshot(path=OUTDIR+"/t_m2.png")
    pg.goto(B+"/");pg.wait_for_selector(".cat");pg.screenshot(path=OUTDIR+"/t_home.png")
    pg.evaluate("document.getElementById('danh-muc').scrollIntoView()");pg.wait_for_timeout(300);pg.screenshot(path=OUTDIR+"/t_cats.png")
    pg.goto(B+"/#p-"+[x for x in prods if x["id"]=="PVN3967"][0]["id"]);pg.wait_for_selector(".det h1");pg.screenshot(path=OUTDIR+"/t_detail.png")
    b.close()
print("\nKẾT QUẢ:",len(fails),"lỗi");print(fails[:10])
