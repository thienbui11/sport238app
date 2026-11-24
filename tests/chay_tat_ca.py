"""Chạy toàn bộ kiểm thử giao diện một lần, tóm tắt kết quả, trả mã lỗi ≠ 0 nếu có bài không đạt (dùng trên máy và trong CI).

    py tests/chay_tat_ca.py --node http://localhost:3000 --web http://localhost:3602 --out <thư mục xuất tĩnh> --site https://vidu.vn [--lighthouse] [--pytest]

--node : máy chủ quản trị Node (bản HTML dự phòng + đăng xuất quản trị; cần dữ liệu mẫu sạch): 4 bài cơ bản
--web  : web tĩnh bản Next.js (bản chính): 4 bài cơ bản + giao diện, axe, bảng size, trang SP, lọc, đặt đội, PWA/ảnh
--out/--site : thư mục web tĩnh và địa chỉ đã dùng khi xuất (--site-url) để kiểm tra SEO
Luôn chạy test_admin (tự bật máy chủ riêng). Nhật ký từng bài: tests/out/chay-tat-ca/<tên>.log"""
import argparse, os, pathlib, re, subprocess, sys, time

HERE = pathlib.Path(__file__).resolve().parent
LOGS = HERE / "out" / "chay-tat-ca"
CO_BAN = ["test_all", "test_feat", "test_cards", "test_mobile"]
NEXT = CO_BAN + ["test_giao_dien", "test_a11y", "test_bang_size", "test_trang_sp", "test_loc", "test_dat_doi", "test_pwa_anh", "test_gui_don"]


def chay(ten, args, nhan):
    LOGS.mkdir(parents=True, exist_ok=True)
    t = time.time()
    r = subprocess.run([sys.executable, *args], cwd=HERE.parent, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    out = r.stdout + ("\n--- stderr ---\n" + r.stderr if r.stderr.strip() else "")
    (LOGS / (re.sub(r"[^\w.-]+", "-", nhan).strip("-") + ".log")).write_text(out, encoding="utf-8")
    m = re.findall(r"KẾT QUẢ:\s*(\d+)\s*lỗi", r.stdout)
    if args[0] == "-m":              # pytest: "N passed", "M failed"
        loi = 0 if r.returncode == 0 else max(1, sum(int(x) for x in re.findall(r"(\d+) (?:failed|error)", r.stdout)))
    else:
        loi = int(m[-1]) if m else None      # không in KẾT QUẢ = bài bị dừng giữa chừng
    print(f"  {'✓' if loi == 0 else '✗'} {nhan:<34} {('lỗi: ' + str(loi)) if loi is not None else 'DỪNG GIỮA CHỪNG (xem log)':<28} {time.time() - t:5.0f} s", flush=True)
    return loi == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--node"); ap.add_argument("--web"); ap.add_argument("--out"); ap.add_argument("--site", default="")
    ap.add_argument("--lighthouse", action="store_true"); ap.add_argument("--pytest", action="store_true")
    a = ap.parse_args()
    viec = []
    if a.pytest: viec.append(("pytest", ["-m", "pytest", "-q"], "pytest"))
    if a.node: viec += [(t, [f"tests/{t}.py", a.node.rstrip("/")], f"{t} (Node/HTML)") for t in CO_BAN]
    if a.web: viec += [(t, [f"tests/{t}.py", a.web.rstrip("/")], f"{t} (Next tĩnh)") for t in NEXT]
    if a.out: viec.append(("test_seo", ["tests/test_seo.py", a.out] + ([a.site] if a.site else []), "test_seo"))
    viec.append(("test_admin", ["tests/test_admin.py"], "test_admin"))
    if a.lighthouse and a.web: viec.append(("lighthouse", ["tests/lighthouse.py", a.web.rstrip("/")], "lighthouse (Next tĩnh)"))
    print(f"Chạy {len(viec)} bài kiểm thử …")
    hong = [n for _, args, n in viec if not chay(_, args, n)]
    print(f"\nTỔNG: {len(viec) - len(hong)}/{len(viec)} bài đạt." + (f" Không đạt: {', '.join(hong)}. Nhật ký: {LOGS}" if hong else ""))
    return 1 if hong else 0


if __name__ == "__main__":
    sys.exit(main())
