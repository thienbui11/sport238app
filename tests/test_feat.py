import os
OUTDIR=os.path.join(os.path.dirname(os.path.abspath(__file__)),"out");os.makedirs(OUTDIR,exist_ok=True)
import json,sys,urllib.request
from playwright.sync_api import sync_playwright
B=sys.argv[1] if len(sys.argv)>1 else "http://localhost:3000"
try:
    api=json.load(urllib.request.urlopen(B+"/api/products"))
except Exception:
    api=json.load(urllib.request.urlopen(B+"/products.json"))   # web tĩnh
prods=api["products"]
fails=[];errs=[]
def ok(c,m):
    print(("  ✓ " if c else "  ✗ ")+m)
    if not c:fails.append(m)
def clipboard(pg):
    # Windows trả clipboard với \r\n thay cho \n: nội dung vẫn như nhau
    return pg.evaluate("navigator.clipboard.readText()").replace("\r\n","\n")
def pick(pred):
    return next(p for p in prods if pred(p))
single_sized=pick(lambda p:len({v["option2"] for v in p["variants"]})==1 and any(v["option1"] for v in p["variants"]) and any(v["inventory_quantity"]>=3 for v in p["variants"]))
size_ok=[v for v in single_sized["variants"] if v["inventory_quantity"]>=3][0]
size_out=[v for v in single_sized["variants"] if v["inventory_quantity"]<=0]
nosz=pick(lambda p:not any(v["option1"] for v in p["variants"]) and len(p["variants"])==1 and p["variants"][0]["inventory_quantity"]>0)
def run(label,viewport,touch=False):
    print("\n=====",label,"=====")
    with sync_playwright() as p:
        b=p.chromium.launch()
        ctx=b.new_context(viewport=viewport,has_touch=touch,permissions=["clipboard-read","clipboard-write"])
        ctx.route("https://zalo.me/**",lambda r:r.fulfill(body="zalo"));ctx.route("https://m.me/**",lambda r:r.fulfill(body="messenger"))
        pg=ctx.new_page();pg.on("pageerror",lambda e:errs.append(str(e)))
        pg.goto(B+"/");pg.wait_for_selector("#grid .card")
        # --- 1. chọn size ngay trên thẻ ---
        pg.fill("#q",single_sized["title"][:18]);pg.wait_for_timeout(150)
        card=pg.locator(f"#grid .card[data-pid='{single_sized['id']}']")
        card.scroll_into_view_if_needed()
        ok(card.locator(".szb").count()==len({v["option1"] for v in single_sized["variants"] if v["option1"]}),"thẻ hiện các nút size bấm được")
        card.locator("[data-quick]").click();pg.wait_for_timeout(100)
        ok("need" in card.get_attribute("class"),"chưa chọn size mà bấm Thêm vào giỏ → thẻ báo thiếu size")
        ok(pg.inner_text("#toast").startswith("Bạn chưa chọn size"),"có thông báo 'Bạn chưa chọn size'")
        ok(pg.is_hidden("#cn"),"giỏ vẫn trống")
        if size_out:
            ok(card.locator(f".szb[data-sz='{size_out[0]['option1']}']").is_disabled(),"size hết hàng bị khóa")
        card.locator(f".szb[data-sz='{size_ok['option1']}']").click()
        ok(card.locator(f".szb[data-sz='{size_ok['option1']}']").get_attribute("aria-pressed")=="true","bấm vào size → size được chọn")
        ok("need" not in card.get_attribute("class"),"hết báo lỗi sau khi chọn size")
        card.locator("[data-quick]").click();pg.wait_for_timeout(100)
        ok(pg.inner_text("#cn")=="1","thêm vào giỏ từ thẻ: giỏ có 1 món")
        # --- 2. thêm từ trang chi tiết ---
        pg.goto(B+"/#p-"+single_sized["id"]);pg.wait_for_selector(".det h1")
        pg.click("#ad");ok("chưa chọn size" in pg.inner_text("#toast").lower() or "Bạn chưa chọn size" in pg.inner_text("#toast"),"trang chi tiết: chưa chọn size → báo lỗi")
        pg.click(f".opt[data-sz='{size_ok['option1']}']");pg.click("#ad");pg.wait_for_timeout(100)
        ok(pg.inner_text("#cn")=="2","trang chi tiết: chọn size rồi thêm → giỏ có 2 món")
        # sản phẩm không có size thêm thẳng
        pg.goto(B+"/");pg.wait_for_selector("#grid .card");pg.fill("#q",nosz["title"][:20]);pg.wait_for_timeout(150)
        c2=pg.locator(f"#grid .card[data-pid='{nosz['id']}']")
        if c2.count():
            c2.locator("[data-quick]").click();pg.wait_for_timeout(100);ok(pg.inner_text("#cn")=="3","sản phẩm không có size: thêm thẳng vào giỏ")
        # --- 3. giỏ hàng ---
        pg.click("#cb");pg.wait_for_timeout(300)
        rows=pg.locator(".ci").count();ok(rows>=2,f"giỏ hiện {rows} dòng")
        first_qty=pg.locator(".ci .qty").first.inner_text()
        pg.locator(".ci [data-q='1']").first.click();pg.wait_for_timeout(100)
        ok(int(pg.locator(".ci .qty").first.inner_text().replace("−","").replace("+","").strip())==int(first_qty.replace("−","").replace("+","").strip())+1,"nút + tăng số lượng")
        txt=pg.input_value("#ordtxt")
        print("\n----- TIN NHẮN -----\n"+txt+"\n--------------------")
        ok("Chào shop, mình muốn đặt" in txt and "Size "+size_ok["option1"] in txt and size_ok["sku"] in txt,"tin nhắn có tên, size, mã SKU")
        ok("Tổng:" in txt and "ghé shop nhận hàng" in txt,"tin nhắn có tổng tiền và dòng nhận hàng tại shop")
        ok(not any(w in txt.lower() for w in ["ship","giao hàng","phí giao"]),"tin nhắn không có chữ ship/giao hàng")
        ok(pg.is_visible("#ordbox") and pg.is_visible("#cp"),"có khung tin nhắn và nút 'Sao chép đơn hàng'")
        # --- 4. sao chép đơn ---
        pg.evaluate("navigator.clipboard.writeText('x')")
        pg.click("#cp");pg.wait_for_timeout(300)
        clip=clipboard(pg)
        ok(clip==txt,"bấm 'Sao chép đơn hàng' → clipboard đúng nội dung tin nhắn")
        ok(pg.is_visible("#cpok") and "Đã sao chép" in pg.inner_text("#cpok"),"hiện thông báo 'Đã sao chép' trong giỏ hàng")
        # --- 5. mở Zalo ---
        pg.evaluate("navigator.clipboard.writeText('x')")
        with ctx.expect_page() as pi: pg.click("#zs")
        z=pi.value;z.wait_for_load_state("commit");pg.wait_for_timeout(300)
        ok(z.url.startswith("https://zalo.me/0962374770"),"mở Zalo: "+z.url)
        ok(clipboard(pg)==txt,"bấm 'Sao chép đơn & mở Zalo' → đã sao chép đơn")
        ok("Zalo" in pg.inner_text("#cpok") and "Đã sao chép" in pg.inner_text("#cpok"),"thông báo hướng dẫn dán vào Zalo")
        z.close()
        # --- 6. mở Messenger ---
        pg.evaluate("navigator.clipboard.writeText('x')")
        with ctx.expect_page() as pi: pg.click("#fs")
        m=pi.value;m.wait_for_load_state("commit");pg.wait_for_timeout(300)
        ok(m.url.startswith("https://m.me/Sport238"),"mở Messenger: "+m.url)
        ok(clipboard(pg)==txt,"bấm 'Sao chép đơn & mở Messenger' → đã sao chép đơn")
        ok("Messenger" in pg.inner_text("#cpok"),"thông báo hướng dẫn dán vào Messenger")
        m.close()
        # --- 7. dự phòng khi trình duyệt không cho dùng clipboard ---
        pg2=ctx.new_page();pg2.add_init_script("Object.defineProperty(navigator,'clipboard',{value:undefined});window.__ec=[];const o=document.execCommand.bind(document);document.execCommand=function(c){const r=o(c);window.__ec.push([c,r]);return r}")
        pg2.goto(B+"/");pg2.wait_for_selector("#grid .card")
        pg2.evaluate("localStorage.setItem('cart5',JSON.stringify([{id:%s,lb:'Size %s',qty:1}]))"%(json.dumps(size_ok["id"]),size_ok["option1"]));pg2.reload();pg2.wait_for_selector("#grid .card")
        pg2.click("#cb");pg2.wait_for_timeout(300);pg2.click("#cp");pg2.wait_for_timeout(300)
        ec=pg2.evaluate("window.__ec");sel=pg2.evaluate("(()=>{const a=document.querySelector('#ordtxt');return a.value.substring(a.selectionStart,a.selectionEnd).length})()")
        ok(any(c=="copy" for c,_ in ec),"không có clipboard API → dùng cách dự phòng (execCommand)")
        ok(sel>20,"khung tin nhắn được bôi đen để bạn Ctrl+C nếu cần")
        ok(pg2.is_visible("#cpok"),"vẫn hiện thông báo kết quả: "+pg2.inner_text("#cpok")[:70])
        pg2.close()
        # --- 8. giỏ trống ---
        pg.click("#cc");pg.wait_for_timeout(150)
        ok(pg.is_hidden("#ordbox"),"giỏ trống: ẩn khung tin nhắn")
        ok("Nhắn Zalo cho shop" in pg.inner_text("#zs"),"giỏ trống: nút Zalo chỉ để nhắn hỏi shop")
        # tràn ngang
        ok(not pg.evaluate("document.documentElement.scrollWidth>document.documentElement.clientWidth"),"không tràn ngang")
        pg.screenshot(path=f"{OUTDIR}/f_{label}.png")
        b.close()
run("desktop",{"width":1280,"height":860})
run("mobile",{"width":390,"height":844},touch=True)
print("\nLỖI JS:",errs[:3]);print("KẾT QUẢ:",len(fails),"lỗi");print(fails)
