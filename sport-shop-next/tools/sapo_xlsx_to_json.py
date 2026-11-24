#!/usr/bin/env python3
"""Đọc file Excel xuất từ Sapo POS, phân loại sản phẩm vào 8 danh mục và ghi ra JSON cho web.
Cách dùng:  python tools/sapo_xlsx_to_json.py danh_sach_san_pham.xlsx [frontend/data/products.json]
Cần:        pip install pandas openpyxl
Chỉ đọc giá bán lẻ và tồn kho. Giá nhập, giá vốn, giá buôn KHÔNG được đọc nên không thể lên web."""
import sys, re, json, datetime, collections
import pandas as pd

DEFAULT_DEST = "frontend/data/products.json"

CATS = ["Cờ, Cúp, Huy Chương", "Giày bóng đá", "Quần áo CLB/Đội tuyển", "Quần áo không logo",
        "Quần áo trẻ em", "Phụ kiện thể thao", "Vớ/tất ống đồng", "Cầu lông"]
CUP, SHOE, CLUB, PLAIN, KIDS, ACC, SOCK, BAD = CATS

# Loại sản phẩm trong Sapo được đưa lên web. Shop còn bán đồ mẹ và bé nên các loại khác bị bỏ qua.
WEB_TYPES = {"Quần áo bóng đá", "Giày bóng đá", "Phụ kiện thể thao"}
# Sản phẩm thể thao chưa được gán loại trong Sapo: nhận theo tên
UNTYPED_SPORT = re.compile(r"^(giày|giầy|quần áo|quần cụt|áo cầu lông|vớ lexis|dây giày|áo bóng đá)", re.I)

_TEAMS = ["mu", "man u", "manu", "real", "barca", "bayern", "liverpool", "chelsea", "arsenal", "psg", "inter", "milan",
          "tottenham", "wolves", "mc", "tây ban nha", "argentina", "hà lan", "brazil", "bồ đào nha", "pháp", "đức", "nhật",
          "hàn quốc", "mỹ", "bỉ", "vn", "việt nam", "croatia", "uruguay", "tuyển", "bulls", "anh"]
TEAM_RE = re.compile(r"(?:^|[\s\-(])(?:" + "|".join(_TEAMS) + r")(?=$|[\s\-)\d])")
CUP_RE = re.compile(r"huy chương|cúp|(?:^|\s)cờ(?:\s|$)|kỷ niệm chương")
BAD_RE = re.compile(r"cầu lông|vợt|bông cầu|shuttle")
SOCK_RE = re.compile(r"ống đồng|(?:^|\s)(?:vớ|tất)(?:\s|$)")
KIDS_RE = re.compile(r"trẻ em|kids|\bqa trẻ")


def classify(name, ptype, sizes=()):
    """Trả về tên danh mục, hoặc None nếu sản phẩm không đưa lên web."""
    ptype = (ptype or "").strip()
    n = " ".join(name.lower().split())
    if ptype not in WEB_TYPES and not (ptype == "" and UNTYPED_SPORT.match(n)):
        return None
    if CUP_RE.search(n): return CUP
    if BAD_RE.search(n): return BAD
    if SOCK_RE.search(n): return SOCK
    if ptype == "Phụ kiện thể thao" or n.startswith("dây giày"): return ACC
    if re.match(r"(giày|giầy)", n): return SHOE
    real = [s for s in sizes if s]
    if KIDS_RE.search(n) or (real and all(s.isdigit() for s in real)): return KIDS
    if TEAM_RE.search(n): return CLUB
    return PLAIN


SIZE_NAME = re.compile(r"kích thước|kích cỡ|\bcỡ\b|\bsize\b|^số$")
SIZE_VAL = re.compile(r"^(xxs|xs|s|m|l|xl|xxl|xxxl|xxxxl|[2-6]xl|free ?size|f|\d{1,3}(?:[.,]5)?)$", re.I)


# Nhiều sản phẩm trong Sapo mỗi size là một sản phẩm riêng, size nằm trong tên ("Giày X - Size 42", "Quần áo Y- XL").
# Tách size ra khỏi tên rồi gộp thành một sản phẩm có nhiều size.
_NB = r"(?<![A-Za-z0-9])"
SHOE_TAIL = re.compile(r"^(?P<base>.*?)[\s\-–]*" + _NB + r"(?:(?i:size)\s*)?(?P<size>3\d|4\d)\s*$", re.I)
LETTER_TAIL = re.compile(r"^(?P<base>.*?)[\s\-–]*" + _NB + r"(?:(?i:size)\s*)?(?P<size>XXXXL|XXXL|XXL|XL|L|M|S)\s*$")
LETTER_MID = re.compile(r"^(?P<a>.*?)\s*[-–]\s*(?P<size>XXXXL|XXXL|XXL|XL|L|M|S)\s*[-–]\s*(?P<b>.+)$")


def split_size(title):
    """Trả về (tên gốc, size) nếu tên có chứa size, ngược lại None."""
    m = LETTER_MID.match(title)
    if m: return f"{m['a']} - {m['b']}".strip(), m["size"]
    for rx in (SHOE_TAIL, LETTER_TAIL):
        m = rx.match(title)
        if m and m["base"].strip(): return m["base"].strip(" -–"), m["size"].upper()
    return None


def merge_key(cat, title):
    t = re.sub(r"\s*[-–]\s*", "-", " ".join(title.lower().split())).strip("-")
    return cat, t


def size_key(s):
    return (0, int(s)) if s.isdigit() else (1, ["XXS", "XS", "S", "M", "L", "XL", "XXL", "XXXL", "XXXXL"].index(s) if s in ["XXS", "XS", "S", "M", "L", "XL", "XXL", "XXXL", "XXXXL"] else 99)


def nc(v):
    """Chuẩn hóa màu: bỏ khoảng trắng thừa quanh dấu gạch ngang ("Navy- tím nhạt" = "Navy-tím nhạt")"""
    return re.sub(r"\s*-\s*", "-", " ".join(v.split()))


def label_duplicates(variants):
    """Các biến thể trùng cả size lẫn màu (Sapo không đặt tên phân biệt) được gắn nhãn theo giá để khách chọn được."""
    groups = collections.defaultdict(list)
    for v in variants: groups[(v["option1"], v["option2"])].append(v)
    for (_, color), vs in groups.items():
        if len(vs) < 2: continue
        for v in vs:
            price = f'{v["price"]:,}'.replace(",", ".") + "đ"
            v["option2"] = price if color == "Mặc định" else f"{color} ({price})"
        again = collections.Counter((v["option1"], v["option2"]) for v in vs)
        for v in vs:
            if again[(v["option1"], v["option2"])] > 1: v["option2"] += f' [{v["sku"]}]'


def clean(v): return "" if pd.isna(v) else str(v).strip()
def num(v):
    try: return float(v)
    except Exception: return 0.0
def norm(v):
    """'Size 1' -> '1'; 'Mặc định' -> '' (không có size)"""
    v = re.sub(r"^\s*size\s*", "", v, flags=re.I).strip()
    return "" if v.lower() == "mặc định" else v


def build_catalog(xlsx):
    """Đọc file Excel Sapo, trả về (danh sách sản phẩm đã phân loại và gộp size, số phiên bản giá 0 bị bỏ)."""
    df = pd.read_excel(xlsx); df.columns = [c.strip() for c in df.columns]
    stock_cols = [c for c in df.columns if re.match(r"^LC_.*Tồn kho ban đầu", c)]
    groups = []
    for _, r in df.iterrows():
        if clean(r["Tên sản phẩm*"]): groups.append({"head": r, "rows": []})
        if groups: groups[-1]["rows"].append(r)

    out, dropped, used, by_key = [], 0, set(), {}
    for g in groups:
        h = g["head"]; title = clean(h["Tên sản phẩm*"]); ptype = clean(h["Loại sản phẩm"])
        attr = [clean(h[f"Thuộc tính {i}"]).lower() for i in (1, 2, 3)]
        vals = [[norm(clean(r[f"Giá trị thuộc tính {i}"])) for r in g["rows"]] for i in (1, 2, 3)]
        role, has_size = [], False
        for i in range(3):
            ne = [v for v in vals[i] if v]
            if "màu" in attr[i]: role.append("color")
            elif not has_size and (SIZE_NAME.search(attr[i]) or (ne and all(SIZE_VAL.match(v) for v in ne))):
                role.append("size"); has_size = True
            else: role.append("other")
        variants = []
        for k, r in enumerate(g["rows"]):
            size, color, other = "", "", []
            for i in range(3):
                v = vals[i][k]
                if not v: continue
                if role[i] == "size": size = v
                elif role[i] == "color": color = nc(v)
                else: other.append(nc(v))
            price = round(num(r["PL_Giá bán lẻ"]))
            if price <= 0: dropped += 1; continue
            sku = clean(r["Mã SKU*"]); vid, n = sku, 2
            while vid in used: vid, n = f"{sku}-{n}", n + 1      # SKU trùng thì thêm hậu tố để không mất phiên bản
            used.add(vid)
            variants.append({"id": vid, "sku": sku, "option1": size, "option2": " / ".join([x for x in [color] + other if x]) or "Mặc định",
                             "price": price, "inventory_quantity": max(0, int(round(sum(num(r[c]) for c in stock_cols))))})
        if not variants: continue
        label_duplicates(variants)
        cat = classify(title, ptype, [v["option1"] for v in variants])
        if cat is None: continue
        merged = False
        if len(variants) == 1 and not variants[0]["option1"] and cat in (SHOE, CLUB, PLAIN, KIDS, BAD):
            sp = split_size(title)
            if sp and (sp[1].isdigit() == (cat == SHOE)):      # giày dùng size số, quần áo dùng size chữ
                title, variants[0]["option1"] = sp[0], sp[1]
                cat = classify(title, ptype, [sp[1]]) or cat
                merged = True
        prod = {"id": variants[0]["id"], "title": title, "product_type": ptype, "vendor": clean(h["Nhãn hiệu"]), "category": cat, "variants": variants}
        key = merge_key(cat, title) if merged else None
        if key and key in by_key:      # cùng sản phẩm, khác size: gộp vào sản phẩm đã có
            t = by_key[key]
            t["variants"] += variants
            t["vendor"] = t["vendor"] or prod["vendor"]
        else:
            out.append(prod)
            if key: by_key[key] = prod
    for p in out:
        if len({v["option1"] for v in p["variants"]}) > 1 or any(v["option1"] for v in p["variants"]):
            p["variants"].sort(key=lambda v: size_key(v["option1"]) if v["option1"] else (2, 0))
        p["id"] = p["variants"][0]["id"]

    return out, dropped


def main():
    xlsx = sys.argv[1]; dest = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_DEST
    out, dropped = build_catalog(xlsx)
    json.dump({"products": out, "images": {}, "updated": datetime.date.today().strftime("%d/%m/%Y")}, open(dest, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"Đã ghi {len(out)} sản phẩm, {sum(len(p['variants']) for p in out)} phiên bản vào {dest}. Bỏ qua {dropped} phiên bản có giá bán lẻ = 0.")
    for c in CATS: print(f"  {c}: {sum(1 for p in out if p['category'] == c)}")


if __name__ == "__main__":
    main()
