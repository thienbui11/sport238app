"""Chấm điểm Lighthouse (giả lập điện thoại) cho trang chủ và một trang sản phẩm.
Cần: cd tests && npm install (một lần); trang phải chạy trên máy chủ HTTP thật (web tĩnh + python -m http.server).
Chạy: python tests/lighthouse.py http://localhost:3602 [--min 90]
In điểm 4 mục (hiệu năng, truy cập, thực hành tốt, SEO); lưu báo cáo HTML/JSON vào tests/out/lighthouse/.
Đạt khi mọi mục ≥ min; in "KẾT QUẢ: N lỗi"."""
import argparse, glob, json, os, pathlib, subprocess, sys, urllib.request

HERE = pathlib.Path(__file__).resolve().parent
CLI = HERE / "node_modules" / "lighthouse" / "cli" / "index.js"
OUT = HERE / "out" / "lighthouse"
NAMES = {"performance": "Hiệu năng", "accessibility": "Truy cập", "best-practices": "Thực hành tốt", "seo": "SEO"}


def chrome():
    c = sorted(glob.glob(os.path.expanduser("~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe")) +
               glob.glob(os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome")))
    if not c:
        raise SystemExit("Không tìm thấy Chromium của Playwright (python -m playwright install chromium)")
    return c[-1]


def product_url(base):
    d = json.load(urllib.request.urlopen(base + "/products.json"))
    pid = d["products"][0]["id"]
    try:
        urllib.request.urlopen(f"{base}/san-pham/{pid}/")
        return f"{base}/san-pham/{pid}/"            # bản Next.js: trang riêng
    except Exception:
        return f"{base}/#p-{pid}"                   # bản HTML: trang chi tiết qua #p-MÃ


def run(url, name):
    OUT.mkdir(parents=True, exist_ok=True)
    cmd = ["node", str(CLI), url, "--quiet", "--output=json", "--output=html", f"--output-path={OUT / name}",
           f"--chrome-path={chrome()}", "--chrome-flags=--headless=new --no-sandbox",
           "--only-categories=performance,accessibility,best-practices,seo"]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    rep = OUT / f"{name}.report.json"
    if not rep.exists():
        raise SystemExit("Lighthouse lỗi:\n" + r.stderr[-2000:])
    d = json.loads(rep.read_text(encoding="utf-8"))
    scores = {k: round(d["categories"][k]["score"] * 100) for k in NAMES}
    worst = sorted((a for a in d["audits"].values() if a.get("score") is not None and a["score"] < 0.9 and a.get("scoreDisplayMode") in ("binary", "numeric", "metricSavings")),
                   key=lambda a: a["score"])[:8]
    return scores, [f"{a['id']} ({a['score']:.2f}): {a['title']}" + (f" — {a['displayValue']}" if a.get("displayValue") else "") for a in worst]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("url"); ap.add_argument("--min", type=int, default=90)
    a = ap.parse_args()
    base = a.url.rstrip("/")
    fails = []
    for name, url in [("trang-chu", base + "/"), ("trang-san-pham", product_url(base))]:
        s, worst = run(url, name)
        print(f"\n{name}: {url}")
        for k, v in s.items():
            mark = "✓" if v >= a.min else "✗"
            print(f"  {mark} {NAMES[k]}: {v}")
            if v < a.min: fails.append(f"{name} {NAMES[k]} {v}")
        if worst:
            print("  Cần cải thiện:"); [print("   ·", w) for w in worst]
    print(f"\nBáo cáo: {OUT}")
    print("KẾT QUẢ:", len(fails), "lỗi"); print(fails)
