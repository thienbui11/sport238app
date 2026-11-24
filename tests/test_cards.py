import os
OUTDIR=os.path.join(os.path.dirname(os.path.abspath(__file__)),"out");os.makedirs(OUTDIR,exist_ok=True)
import json,re,sys,urllib.request
from playwright.sync_api import sync_playwright
B=sys.argv[1] if len(sys.argv)>1 else "http://localhost:3000"
try: api=json.load(urllib.request.urlopen(B+"/api/products"))
except Exception: api=json.load(urllib.request.urlopen(B+"/products.json"))
prods=api["products"];fails=[];errs=[]
def ok(c,m):
    print(("  ✓ " if c else "  ✗ ")+m)
    if not c:fails.append(m)
def colors(p):
    u=[]
    for v in p["variants"]:
        if v["option2"] not in u:u.append(v["option2"])
    return u
def cs(p,c):return sum(v["inventory_quantity"] for v in p["variants"] if v["option2"]==c)
def dflt(p):
    return next((c for c in colors(p) if cs(p,c)>0),colors(p)[0])
def money(n):return f"{n:,}".replace(",",".")+"đ"
tot=lambda p:sum(v["inventory_quantity"] for v in p["variants"])
multi_sized=next(p for p in prods if len(colors(p))>1 and any(v["option1"] for v in p["variants"]) and tot(p)>0 and sum(1 for c in colors(p) if any(v["option2"]==c and v["inventory_quantity"]>0 and v["option1"] for v in p["variants"]))>=2)
multi_nosz=next((p for p in prods if len(colors(p))>1 and not any(v["option1"] for v in p["variants"]) and sum(1 for c in colors(p) if cs(p,c)>0)>=2),None)
one_left=next(p for p in prods if len(colors(p))==1 and any(v["inventory_quantity"]==1 for v in p["variants"]))
v1=next(v for v in one_left["variants"] if v["inventory_quantity"]==1)
oos=next(p for p in prods if tot(p)==0)
def run(label,vp,touch=False):
    print("\n=====",label,"=====")
    with sync_playwright() as pw:
        b=pw.chromium.launch();ctx=b.new_context(viewport=vp,has_touch=touch);pg=ctx.new_page();pg.on("pageerror",lambda e:errs.append(str(e)))
        pg.goto(B+"/");pg.wait_for_selector("#grid .card")
        # --- A. mọi thẻ đều có dòng tồn kho đúng số liệu ---
        rows=pg.evaluate("[...document.querySelectorAll('#grid .card')].map(c=>[c.dataset.pid,(c.querySelector('.stk')||{}).textContent||'',(c.querySelector('.stk b')||{}).textContent||''])")
        byid={p["id"]:p for p in prods};bad=[]
        for pid,txt,num in rows:
            p=byid[pid];c=dflt(p);exp=cs(p,c)
            if exp>0 and str(exp)!=num:bad.append((p["title"],exp,num))
            if exp==0 and "Tạm hết hàng" not in txt:bad.append((p["title"],"hết",txt))
        ok(len(rows)==len(prods) and not bad,f"{len(rows)} thẻ đều hiện tồn kho đúng số liệu (sai: {bad[:2]})")
        # --- B. sản phẩm nhiều màu có size ---
        p=multi_sized;cols=colors(p);pg.fill("#q",p["title"][:24]);pg.wait_for_timeout(200)
        card=pg.locator(f"#grid .card[data-pid='{p['id']}']");card.scroll_into_view_if_needed()
        ok(card.locator(".clb").count()==len(cols),f"thẻ '{p['title']}' hiện đủ {len(cols)} nút màu: {cols}")
        ok(card.locator(".clb[aria-pressed='true']").inner_text()==dflt(p),"màu mặc định là màu còn hàng đầu tiên: "+dflt(p))
        ok(re.search(r"Tồn kho (?:màu|loại) này: (\d+) sản phẩm",card.locator(".stk").inner_text()) and int(re.search(r"(\d+)",card.locator(".stk").inner_text()).group(1))==cs(p,dflt(p)),"dòng tồn kho đúng theo màu: "+card.locator(".stk").inner_text())
        c2=next(c for c in cols if c!=dflt(p) and any(v["option2"]==c and v["inventory_quantity"]>0 and v["option1"] for v in p["variants"]))
        card.locator(".clb",has_text=c2).first.click();pg.wait_for_timeout(150)
        card=pg.locator(f"#grid .card[data-pid='{p['id']}']")
        ok(card.locator(".clb[aria-pressed='true']").inner_text()==c2,"bấm màu khác → màu được chọn: "+c2)
        okdis=all(card.locator(f".szb[data-sz='{sz}']").is_disabled()==(not any(v["option2"]==c2 and v["option1"]==sz and v["inventory_quantity"]>0 for v in p["variants"])) for sz in {v["option1"] for v in p["variants"] if v["option1"]})
        ok(okdis,"các size cập nhật còn/hết đúng theo màu vừa chọn")
        ok(int(re.search(r"(\d+)",card.locator(".stk").inner_text()).group(1))==cs(p,c2),"tồn kho cập nhật theo màu mới: "+card.locator(".stk").inner_text())
        v=next(v for v in p["variants"] if v["option2"]==c2 and v["option1"] and v["inventory_quantity"]>0)
        card.locator(f".szb[data-sz='{v['option1']}']").click();pg.wait_for_timeout(120)
        card=pg.locator(f"#grid .card[data-pid='{p['id']}']");st=card.locator(".stk").inner_text()
        ok(f"Size {v['option1']}" in st and str(v["inventory_quantity"]) in st,"chọn size → hiện tồn kho của đúng size: "+st)
        ok(money(v["price"]) in card.locator(".price").inner_text(),"giá theo phiên bản đã chọn: "+card.locator(".price").inner_text())
        card.locator("[data-quick]").click();pg.wait_for_timeout(150);ok(pg.inner_text("#cn")=="1","thêm vào giỏ từ thẻ nhiều màu")
        pg.click("#cb");pg.wait_for_timeout(250);row=pg.locator(".ci").first.inner_text()
        ok(f"Màu {c2}" in row and f"Size {v['option1']}" in row,"giỏ ghi đúng màu và size: "+row.replace("\n"," | ")[:80]);pg.click("#dx")
        # --- C. nhiều màu, không có size ---
        if multi_nosz:
            q=multi_nosz;cc=[c for c in colors(q) if cs(q,c)>0][1];pg.fill("#q",q["title"][:20]);pg.wait_for_timeout(200)
            cd=pg.locator(f"#grid .card[data-pid='{q['id']}']");cd.locator(".clb",has_text=cc).first.click();pg.wait_for_timeout(120)
            cd=pg.locator(f"#grid .card[data-pid='{q['id']}']");cd.locator("[data-quick]").click();pg.wait_for_timeout(120)
            pg.click("#cb");pg.wait_for_timeout(250);ok((f"Màu {cc}" in pg.locator(".ci").last.inner_text() or f"Loại {cc}" in pg.locator(".ci").last.inner_text()),f"'{q['title']}' không có size: chọn màu {cc} rồi thêm giỏ");pg.click("#dx")
        # --- D. không vượt quá tồn kho ---
        pg.evaluate("localStorage.removeItem('cart5')");pg.reload();pg.wait_for_selector("#grid .card")
        pg.fill("#q",one_left["title"][:24]);pg.wait_for_timeout(200)
        def add_once():
            cd=pg.locator(f"#grid .card[data-pid='{one_left['id']}']")
            if len(colors(one_left))>=1 and v1["option1"]:cd.locator(f".szb[data-sz='{v1['option1']}']").click();cd=pg.locator(f"#grid .card[data-pid='{one_left['id']}']")
            cd.locator("[data-quick]").click();pg.wait_for_timeout(120)
        add_once();add_once()
        ok(pg.inner_text("#cn")=="1" and "Chỉ còn 1" in pg.inner_text("#toast"),"chỉ còn 1: thêm lần 2 bị chặn và báo '"+pg.inner_text("#toast")[:45]+"'")
        # --- E. hết hàng ---
        pg.fill("#q",oos["title"][:24]);pg.wait_for_timeout(200)
        cd=pg.locator(f"#grid .card[data-pid='{oos['id']}']");lk=cd.locator("a.btn")
        ok(lk.inner_text()=="Xem chi tiết" and "Tạm hết hàng" in cd.locator(".stk").inner_text(),"sản phẩm hết hàng: thẻ ghi 'Tạm hết hàng' và có nút Xem chi tiết")
        lk.click();pg.wait_for_selector(".det h1");ok(oos["title"][:10] in pg.inner_text(".det h1"),"bấm Xem chi tiết → mở trang sản phẩm")
        # --- F. trang chi tiết hiện số lượng ---
        pg.goto(B+"/#p-"+p["id"]);pg.wait_for_selector(".det h1")
        small=pg.eval_on_selector_all(".opt[data-sz] small","e=>e.map(x=>x.textContent)");ok(len(small)>0 and all(re.fullmatch(r"còn \d+|hết",s) for s in small),f"mỗi size hiện số lượng còn: {small[:5]}")
        pg.click(f".opt[data-col='{c2}']");pg.click(f".opt[data-sz='{v['option1']}']");pg.wait_for_timeout(100)
        ok(f"Còn {v['inventory_quantity']} sản phẩm" in pg.inner_text(".st"),"trạng thái ghi đúng số lượng: "+pg.inner_text(".st"))
        ok(not pg.evaluate("document.documentElement.scrollWidth>document.documentElement.clientWidth"),"không tràn ngang")
        pg.goto(B+"/");pg.wait_for_selector("#grid .card");pg.fill("#q","CV VEX");pg.wait_for_timeout(250)
        pg.locator("#grid .card").first.scroll_into_view_if_needed();pg.locator("#grid .card").first.screenshot(path=f"{OUTDIR}/k_{label}.png")
        b.close()
run("desktop",{"width":1280,"height":860});run("mobile",{"width":390,"height":844},touch=True)
print("\nLỖI JS:",errs[:3]);print("KẾT QUẢ:",len(fails),"lỗi");print(fails)
