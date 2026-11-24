"""Kiểm thử trang quản trị (B6 + N2): giao diện mới, lọc nhanh, sửa hàng loạt, sửa 1 sản phẩm, tải ảnh WebP, điện thoại, chế độ tối, axe.
Tự bật máy chủ quản trị Node riêng với dữ liệu mẫu trong thư mục tạm (không đụng dữ liệu thật của shop).
Kết quả lọc, sửa hàng loạt được đối chiếu với API /api/admin/products (không tin vào giao diện).
Chạy:  py tests/test_admin.py      (in "KẾT QUẢ: N lỗi")"""
import io, json, os, pathlib, shutil, socket, subprocess, tempfile, time, urllib.request
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
APP = ROOT / "sport-shop-app"
AXE = pathlib.Path(__file__).resolve().parent / "node_modules" / "axe-core" / "axe.min.js"
PW = "mat-khau-kiem-thu"
fails, errs = [], []


def ok(c, m):
    print(("  ✓ " if c else "  ✗ ") + m)
    if not c: fails.append(m)


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0)); return s.getsockname()[1]


def axe(pg, where):
    if not AXE.exists(): print("  (chưa cài axe-core: cd tests && npm install)"); return
    pg.add_script_tag(path=str(AXE))
    v = pg.evaluate("async()=>(await axe.run(document,{resultTypes:['violations']})).violations.filter(x=>['critical','serious'].includes(x.impact)).map(x=>x.id+': '+x.nodes.slice(0,2).map(n=>n.target.join(' ')).join(', '))")
    ok(not v, f"{where}: axe 0 lỗi nặng ({v[:3]})")


ok((APP / "public" / "admin.html").read_bytes() == (ROOT / "sport-shop-next/frontend/public/admin/index.html").read_bytes(),
   "hai bản trang quản trị giống hệt (Node và Next.js/Spring Boot)")

tmp = pathlib.Path(tempfile.mkdtemp(prefix="qt-"))
(tmp / "data").mkdir()
shutil.copy(APP / "data" / "seed-products.json", tmp / "data" / "seed-products.json")
port = free_port(); B = f"http://127.0.0.1:{port}"
srv = subprocess.Popen(["node", "--disable-warning=ExperimentalWarning", "src/server.js"], cwd=APP,
                       env=dict(os.environ, DATA_DIR=str(tmp / "data"), PORT=str(port), ADMIN_PASSWORD=PW),
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(100):
    try: urllib.request.urlopen(B + "/api/config", timeout=1); break
    except OSError: time.sleep(0.1)


def stock(p): return sum(max(0, v["inventory_quantity"]) for v in p["variants"])


def login(pg):
    pg.goto(B + "/admin"); pg.wait_for_selector("#pw", state="visible")
    pg.fill("#pw", PW); pg.click("#lb"); pg.wait_for_selector("#tb tr.r")


def api(ctx):
    return {p["id"]: p for p in ctx.request.get(B + "/api/admin/products").json()["products"]}


def put(ctx, p, **kw):
    info = {"display_title": p["display_title"], "description": p["description"], "hidden": p["hidden"], "featured": p["featured"], "category": p["category_override"]}
    info.update(kw)
    ctx.request.put(B + "/api/admin/products/" + p["id"], data=json.dumps(info), headers={"Content-Type": "application/json"})


def chip_count(pg, k):
    return int(pg.inner_text(f"[data-ch='{k}']").rsplit("(", 1)[1].rstrip(")"))


def wait_bulk(pg):
    pg.wait_for_function("document.getElementById('bulk').hidden&&!document.querySelector('#bulk button:disabled')", timeout=20000)


try:
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        print("\n===== Máy tính: lọc nhanh, sửa hàng loạt =====")
        ctx = b.new_context(viewport={"width": 1366, "height": 860}); pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("dialog", lambda d: d.accept())
        login(pg)
        P = api(ctx); ids = list(P)
        # chuẩn bị: 1 SP có mô tả, 1 SP đặt tay danh mục (để kiểm tra sửa hàng loạt không xóa mất)
        keep = P[ids[0]]; put(ctx, keep, description="Vải thun lạnh, form rộng", display_title="Tên riêng");
        put(ctx, P[ids[1]], category="Cầu lông")
        pg.reload(); pg.wait_for_selector("#tb tr.r"); P = api(ctx)
        ok(pg.locator("#tb tr.r").count() == len(P), f"danh sách hiện đủ {len(P)} sản phẩm")
        exp = {"all": len(P), "noimg": len(P), "out": sum(1 for p in P.values() if stock(p) <= 0),
               "nodesc": sum(1 for p in P.values() if not p["description"].strip()), "hidden": 0, "feat": sum(1 for p in P.values() if p["featured"])}
        got = {k: chip_count(pg, k) for k in exp}
        ok(got == exp, f"số trên các nút lọc đúng với dữ liệu ({got})")
        pg.click("[data-ch='out']")
        ok(pg.locator("#tb tr.r").count() == exp["out"] and all(stock(P[i]) <= 0 for i in pg.eval_on_selector_all("#tb tr.r", "r=>r.map(x=>x.dataset.id)")),
           f"lọc 'Hết hàng': đúng {exp['out']} sản phẩm hết hàng")
        pg.click("[data-ch='nodesc']")
        ok(pg.locator("#tb tr.r").count() == exp["nodesc"] and pg.locator(f"#tb tr.r[data-id='{keep['id']}']").count() == 0, "lọc 'Chưa có mô tả': bỏ SP đã có mô tả")
        pg.click("[data-ch='noimg']"); pg.select_option("#so", "sd")
        st = [stock(P[i]) for i in pg.eval_on_selector_all("#tb tr.r", "r=>r.map(x=>x.dataset.id)")]
        ok(len(st) == len(P) and st == sorted(st, reverse=True), "Chưa có ảnh + 'Tồn nhiều trước': xếp đúng theo tồn kho giảm dần")
        pg.select_option("#so", "sa"); st = [stock(P[i]) for i in pg.eval_on_selector_all("#tb tr.r", "r=>r.map(x=>x.dataset.id)")]
        ok(st == sorted(st), "'Tồn ít trước' xếp tăng dần")
        pg.select_option("#so", ""); pg.click("[data-ch='all']")
        ok(pg.eval_on_selector_all("#tb tr.r", "r=>r.map(x=>x.dataset.id)") == ids, "'Thứ tự như Sapo' trả về đúng thứ tự ban đầu")

        # chọn 3 SP → ẩn
        pick = ids[:3]
        for i in pick: pg.check(f"input.sel[data-id='{i}']")
        ok(pg.is_visible("#bulk") and "Đã chọn 3" in pg.inner_text("#bn"), "chọn 3 sản phẩm: hiện thanh sửa hàng loạt 'Đã chọn 3 sản phẩm'")
        pg.click("[data-b='hide']"); wait_bulk(pg); P2 = api(ctx)
        ok(all(P2[i]["hidden"] for i in pick) and sum(1 for p in P2.values() if p["hidden"]) == 3, "Ẩn khỏi web: đúng 3 SP bị ẩn, SP khác không đổi")
        ok(P2[keep["id"]]["description"] == "Vải thun lạnh, form rộng" and P2[keep["id"]]["display_title"] == "Tên riêng" and P2[ids[1]]["category_override"] == "Cầu lông",
           "sửa hàng loạt giữ nguyên tên riêng, mô tả, danh mục đặt tay")
        pub = {p["id"] for p in ctx.request.get(B + "/api/products").json()["products"]}
        ok(not (set(pick) & pub), "SP đã ẩn không còn trên web khách")
        ok(chip_count(pg, "hidden") == 3 and "Đã ẩn 3 sản phẩm" in pg.inner_text("#cnt"), "báo 'Đã ẩn 3 sản phẩm', nút lọc 'Đang ẩn (3)'")
        ok(not pg.is_visible("#bulk") and pg.locator("input.sel:checked").count() == 0, "xong thì bỏ chọn, ẩn thanh sửa hàng loạt")

        # lọc Đang ẩn → chọn tất cả → bật nổi bật rồi hiện lại
        pg.click("[data-ch='hidden']"); pg.check("#all")
        ok("Đã chọn 3" in pg.inner_text("#bn"), "'Chọn tất cả' chỉ chọn các SP đang hiện trong danh sách lọc")
        pg.click("[data-b='feat']"); wait_bulk(pg); P3 = api(ctx)
        ok(all(P3[i]["featured"] and P3[i]["hidden"] for i in pick) and sum(1 for p in P3.values() if p["featured"]) == 3, "Bật nổi bật: đúng 3 SP, vẫn giữ trạng thái ẩn")
        pg.click("[data-ch='hidden']"); pg.check("#all"); pg.click("[data-b='show']"); wait_bulk(pg); P4 = api(ctx)
        ok(not any(p["hidden"] for p in P4.values()) and all(P4[i]["featured"] for i in pick), "Hiện lại: hết SP ẩn, vẫn giữ nổi bật")

        # đổi danh mục hàng loạt, rồi trả về Tự động
        pg.click("[data-ch='feat']"); pg.check("#all"); pg.select_option("#bcat", "Vớ/tất ống đồng"); wait_bulk(pg); P5 = api(ctx)
        ok(all(P5[i]["category_override"] == "Vớ/tất ống đồng" and P5[i]["category"] == "Vớ/tất ống đồng" for i in pick), "Đổi danh mục hàng loạt: 3 SP sang 'Vớ/tất ống đồng'")
        pg.click("[data-ch='feat']"); pg.check("#all"); pg.select_option("#bcat", "__auto"); wait_bulk(pg); P6 = api(ctx)
        ok(all(P6[i]["category_override"] == "" and P6[i]["category"] == P6[i]["category_auto"] for i in pick), "Đổi danh mục 'Tự động': bỏ danh mục đặt tay")
        pg.click("[data-ch='feat']"); pg.check("#all"); pg.click("[data-b='unfeat']"); wait_bulk(pg)
        ok(not any(p["featured"] for p in api(ctx).values()), "Tắt nổi bật hàng loạt")
        pg.click("[data-ch='all']")

        print("\n===== Sửa 1 sản phẩm, tải ảnh WebP =====")
        tgt = ids[5]
        pg.fill("#s", tgt); pg.wait_for_timeout(100)
        ok(pg.locator("#tb tr.r").count() >= 1, "tìm theo mã sản phẩm")
        pg.click(f"[data-open='{tgt}']"); pg.wait_for_selector("#dg[open]")
        pg.fill("#f2", "Mô tả thử nghiệm")
        big = io.BytesIO(); Image.new("RGB", (2400, 1200), (163, 18, 42)).save(big, "PNG")
        pg.locator("[data-up]").first.set_input_files(files=[{"name": "anh.png", "mimeType": "image/png", "buffer": big.getvalue()}])
        pg.wait_for_function("document.getElementById('dm').textContent.indexOf('Đã tải lên')>-1", timeout=15000)
        src = pg.get_attribute("#imgs .th img", "src") or ""
        im = Image.open(io.BytesIO(ctx.request.get(B + src).body()))
        ok(src.endswith(".webp") and im.format == "WEBP" and max(im.size) == 1400, f"ảnh tải lên được đổi WebP, thu nhỏ còn 1400 px ({src}, {im.format} {im.size})")
        pg.click("#sv"); pg.wait_for_function("document.getElementById('dm').textContent==='Đã lưu'")
        p = api(ctx)[tgt]; imgs = ctx.request.get(B + "/api/admin/products").json()["images"]
        ok(p["description"] == "Mô tả thử nghiệm" and any(src in v for k, v in imgs.items() if k == tgt or k.startswith(tgt + ":")), "Lưu: mô tả và ảnh vào đúng sản phẩm")
        pg.click("#cl"); pg.fill("#s", ""); pg.wait_for_timeout(100)
        ok(chip_count(pg, "noimg") == len(P) - 1, "lọc 'Chưa có ảnh' bớt 1 sau khi thêm ảnh")
        axe(pg, "danh sách (máy tính, sáng)")
        pg.click(f"[data-open='{tgt}']"); pg.wait_for_selector("#dg[open]"); axe(pg, "hộp sửa SP (máy tính, sáng)")
        ctx.close()

        for scheme in ("light", "dark"):
            print(f"\n===== Điện thoại 390 px – {'tối' if scheme == 'dark' else 'sáng'} =====")
            ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, color_scheme=scheme)
            pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto(B + "/admin"); pg.wait_for_selector("#pw", state="visible")
            axe(pg, f"đăng nhập ({scheme})")
            pg.fill("#pw", PW); pg.click("#lb"); pg.wait_for_selector("#tb tr.r")
            ok(pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth"), "không tràn ngang 390 px")
            # mỗi SP là 1 thẻ: tên, danh mục, tồn, trạng thái đều nằm trong màn hình
            cut = pg.evaluate("""()=>[...document.querySelectorAll('#tb tr.r')].slice(0,12).flatMap(r=>[...r.querySelectorAll('td')].filter(td=>{const b=td.getBoundingClientRect();return b.width>0&&(b.right>innerWidth+1||b.left<-1)}).map(td=>r.dataset.id+'.'+td.className))""")
            ok(not cut, f"thẻ sản phẩm không bị cắt cột trạng thái ({cut[:3]})")
            small = pg.evaluate("""()=>[...document.querySelectorAll('.tabs button,.chips button,.top button,#tb .hit,#bulk button,label.ck')].filter(e=>{const b=e.getBoundingClientRect();return b.width>0&&b.height<40}).map(e=>e.textContent.trim().slice(0,20)||e.className)""")
            ok(not small, f"nút bấm đủ lớn cho ngón tay ({small[:4]})")
            dark = pg.evaluate("getComputedStyle(document.body).backgroundColor")
            ok((dark == "rgb(18, 17, 19)") == (scheme == "dark"), f"nền theo chế độ {scheme} ({dark})")
            pg.locator("#tb .hit").first.click()
            ok(pg.is_visible("#bulk") and not pg.is_visible("#dg"), "bấm ô chọn trên điện thoại: chọn SP, không mở hộp sửa")
            bb = pg.evaluate("(()=>{const r=document.getElementById('bulk').getBoundingClientRect();return [r.top,r.bottom,innerHeight]})()")
            ok(abs(bb[1] - bb[2]) < 2 and bb[1] - bb[0] < 200, f"thanh sửa hàng loạt nằm gọn ở đáy màn hình điện thoại ({bb[1]-bb[0]:.0f} px)")
            axe(pg, f"danh sách điện thoại ({scheme})")
            pg.locator("#tb .lnk").first.click(); pg.wait_for_selector("#dg[open]")
            w = pg.evaluate("document.getElementById('dg').getBoundingClientRect().width")
            ok(w >= 385 and pg.is_visible("#sv"), f"hộp sửa SP chiếm cả màn hình điện thoại ({w:.0f} px), thấy nút Lưu")
            axe(pg, f"hộp sửa SP điện thoại ({scheme})")
            pg.click("#cl")
            if scheme == "light":
                ctx2 = b.new_context(viewport={"width": 320, "height": 700}, is_mobile=True, has_touch=True); p2 = ctx2.new_page()
                p2.goto(B + "/admin"); p2.wait_for_selector("#pw", state="visible"); p2.fill("#pw", PW); p2.click("#lb"); p2.wait_for_selector("#tb tr.r")
                ok(p2.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth"), "không tràn ngang 320 px")
                ctx2.close()
            pg.click("#out"); pg.wait_for_load_state("load"); pg.wait_for_timeout(500)
            ok(pg.is_visible("#login") and ctx.request.get(B + "/api/admin/products").status == 401, "Đăng xuất: về màn hình đăng nhập, phiên cũ hết hiệu lực")
            ctx.close()
        b.close()
finally:
    srv.terminate(); srv.wait(10); shutil.rmtree(tmp, ignore_errors=True)

print("\nLỖI JS:", errs[:3]); print("KẾT QUẢ:", len(fails) + len(errs), "lỗi"); print(fails)
