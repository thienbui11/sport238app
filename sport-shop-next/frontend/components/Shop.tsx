"use client";
import Link from "next/link";
import { useMemo, useState, type CSSProperties } from "react";
import { CATEGORIES, colorStock, defaultColor, EMO, hueOf, imgsFor, links, money, optLabel, stockStatus, type Product } from "@/lib/shop";
import { useShop } from "./Providers";

export function Placeholder({ p }: { p: Product }) {
  const h = hueOf(p.id);
  return <div className="ph" style={{ background: `linear-gradient(135deg,hsl(${h},70%,88%),hsl(${(h + 35) % 360},65%,72%))` }}>{EMO[p.cat]}</div>;
}

function Card({ p }: { p: Product }) {
  const { add, toast } = useShop();
  const [color, setColor] = useState(() => defaultColor(p));
  const [size, setSize] = useState<string | null>(null);
  const [need, setNeed] = useState(false);
  const [st, cls] = stockStatus(p);
  const sizes = p.sizes.filter(Boolean);
  const hasSize = sizes.length > 0, multi = p.colors.length > 1, lbl = optLabel(p);
  const href = `/san-pham/${encodeURIComponent(p.id)}`;
  const ofColor = p.variants.filter((v) => v.color === color);
  const chosen = hasSize ? (size ? ofColor.find((v) => v.size === size) : undefined) : ofColor[0];
  const tot = colorStock(p, color), out = chosen ? chosen.stock <= 0 : tot <= 0;
  const prices = (chosen ? [chosen] : ofColor).map((v) => v.price), lo = Math.min(...prices), hi = Math.max(...prices);
  const first = imgsFor(p, color)[0];
  const pickColor = (c: string) => {
    setColor(c); setNeed(false);
    if (size && !p.variants.some((v) => v.color === c && v.size === size && v.stock > 0)) setSize(null);
  };
  const addQuick = () => {
    if (hasSize && !size) { setNeed(true); toast("Bạn chưa chọn size. Bấm vào một size ở trên thẻ."); return; }
    if (!chosen || chosen.stock <= 0) { toast(multi ? `${lbl} này tạm hết hàng, hãy chọn ${lbl.toLowerCase()} khác` : "Sản phẩm tạm hết hàng"); return; }
    const label = [chosen.size && `Size ${chosen.size}`, multi && `${lbl} ${chosen.color}`].filter(Boolean).join(" · ");
    add({ id: chosen.id, name: p.name, label, sku: chosen.sku, price: chosen.price, stock: chosen.stock });
  };
  return (
    <article className={"card" + (need ? " need" : "")}>
      <Link className="thumb" href={href} aria-label={`Xem ${p.name}`}>
        <span className={`badge l ${cls}`}>{st}</span>
        {p.feat && <span className="badge r">Nổi bật</span>}
        {first ? <img src={first} alt={p.name} loading="lazy" /> : <Placeholder p={p} />}
      </Link>
      <div className="cinfo">
        <small>{p.cat}{p.brand && ` · ${p.brand}`}</small>
        <h3><Link href={href} className="nm">{p.name}</Link></h3>
        {multi && (
          <div className="cl" role="group" aria-label={`Chọn ${lbl.toLowerCase()}`}>
            {p.colors.map((c) => (
              <button key={c} type="button" className={"clb" + (colorStock(p, c) ? "" : " x")} aria-pressed={c === color} onClick={() => pickColor(c)}>{c}</button>
            ))}
          </div>
        )}
        {hasSize && (
          <div className="sz" role="group" aria-label="Chọn size">
            {sizes.map((s) => {
              const v = ofColor.find((x) => x.size === s), ok = !!v && v.stock > 0;
              return (
                <button key={s} type="button" className={"szb" + (ok ? "" : " x")} aria-pressed={size === s} disabled={!ok} title={ok ? undefined : "Hết hàng"}
                  onClick={() => { setSize(s); setNeed(false); }}>{s}</button>
              );
            })}
          </div>
        )}
        <div className={"stk" + (out ? " out" : "")}>
          {chosen
            ? chosen.stock > 0 ? <>{chosen.size && `Size ${chosen.size} · `}Còn <b>{chosen.stock}</b> sản phẩm</> : "Tạm hết hàng"
            : tot > 0 ? <>Tồn kho{multi && ` ${lbl.toLowerCase()} này`}: <b>{tot}</b> sản phẩm</> : "Tạm hết hàng"}
        </div>
        <div className="price">{(lo !== hi ? "Từ " : "") + money(lo)}</div>
        {p.stock <= 0 ? <Link className="btn ghost" href={href}>Xem chi tiết</Link>
          : <button type="button" className="btn" onClick={addQuick}>+ Thêm vào giỏ</button>}
      </div>
    </article>
  );
}

/** Danh mục + hàng có sẵn + banner đồng phục + toàn bộ sản phẩm (lọc, tìm kiếm, sắp xếp) */
export default function Storefront({ products, updated }: { products: Product[]; updated: string }) {
  const { site } = useShop();
  const l = links(site);
  const [cat, setCat] = useState("Tất cả");
  const [q, setQ] = useState("");
  const [st, setSt] = useState("");
  const [sort, setSort] = useState("");

  const list = useMemo(() => {
    const k = q.trim().toLowerCase();
    return products
      .filter((p) => (cat === "Tất cả" || p.cat === cat) && (!st || (st === "in") === p.stock > 0) && p.name.toLowerCase().includes(k))
      .sort((a, b) => (sort === "asc" ? a.min - b.min : sort === "desc" ? b.min - a.min : Number(b.feat) - Number(a.feat) || Number(b.stock > 0) - Number(a.stock > 0)));
  }, [products, cat, q, st, sort]);

  const fresh = useMemo(() => products.filter((p) => p.stock > 0).slice(0, 10), [products]);
  const goCat = (c: string) => { setCat(c); document.getElementById("san-pham")?.scrollIntoView({ behavior: "smooth" }); };

  return (
    <>
      <section id="danh-muc" className="sec wrap">
        <span className="eyebrow">DANH MỤC</span>
        <h2>Bạn đang tìm gì?</h2>
        <p className="sub">Chọn một danh mục để xem sản phẩm.</p>
        <div className="cats">
          {CATEGORIES.map((c) => {
            const n = products.filter((p) => p.cat === c.name).length;
            return (
              <button key={c.name} className="cat" style={{ "--c1": c.c1, "--c2": c.c2 } as CSSProperties} onClick={() => goCat(c.name)}>
                <i>{c.emoji}</i><b>{c.name}</b><span>{n ? `${n} sản phẩm` : "Đang cập nhật"}</span>
              </button>
            );
          })}
        </div>
      </section>

      {fresh.length > 0 && (
        <section id="moi" className="sec wrap">
          <span className="eyebrow">MỚI CẬP NHẬT</span>
          <h2>Hàng đang có sẵn</h2>
          <p className="sub">Vuốt sang để xem thêm.</p>
          <div className="rail">{fresh.map((p) => <Card key={p.id} p={p} />)}</div>
        </section>
      )}

      <section className="sec wrap">
        <div className="promo">
          <div>
            <h2>Đồng phục đội nhóm, công ty</h2>
            <p>Nhắn shop để được tư vấn mẫu áo, in tên số và báo giá theo số lượng.</p>
            <a className="btn" href={l.zalo} target="_blank" rel="noopener">💬 Nhắn Zalo tư vấn</a>
          </div>
          <div className="big" aria-hidden="true">🎽</div>
        </div>
      </section>

      <section id="san-pham" className="sec wrap">
        <span className="eyebrow">TẤT CẢ SẢN PHẨM</span>
        <h2>Sản phẩm đang bán</h2>
        <p className="sub">Chọn size, màu rồi thêm vào giỏ; gửi danh sách cho shop qua Zalo hoặc Messenger.{updated && ` Tồn kho cập nhật ngày ${updated}.`}</p>
        <div className="tools">
          <label className="search">🔍<input type="search" placeholder="Tìm sản phẩm (vd: giày, áo, tất…)" aria-label="Tìm sản phẩm" value={q} onChange={(e) => setQ(e.target.value)} /></label>
          <select className="sel" aria-label="Tình trạng" value={st} onChange={(e) => setSt(e.target.value)}>
            <option value="">Mọi tình trạng</option><option value="in">Còn hàng</option><option value="out">Hết hàng</option>
          </select>
          <select className="sel" aria-label="Sắp xếp" value={sort} onChange={(e) => setSort(e.target.value)}>
            <option value="">Sắp xếp: Mặc định</option><option value="asc">Giá thấp → cao</option><option value="desc">Giá cao → thấp</option>
          </select>
        </div>
        <div className="chips">
          {["Tất cả", ...CATEGORIES.map((c) => c.name)].map((c) => (
            <button key={c} className="chip" aria-pressed={c === cat} onClick={() => setCat(c)}>{c === "Tất cả" ? "✨" : EMO[c]} {c}</button>
          ))}
        </div>
        <p className="count">{list.length} sản phẩm{cat !== "Tất cả" && ` trong “${cat}”`}</p>
        <div className="grid">
          {list.length ? list.map((p) => <Card key={p.id} p={p} />) : <p className="empty">Không tìm thấy sản phẩm phù hợp. Thử từ khóa khác nhé.</p>}
        </div>
      </section>
    </>
  );
}
