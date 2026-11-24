"use client";
import Link from "next/link";
import { useEffect, useMemo, useRef, useState, type CSSProperties } from "react";
import { CATEGORIES, colorStock, defaultColor, EMO, fold, hueOf, imgsFor, links, money, optLabel, PAGE, stockStatus, type Product } from "@/lib/shop";
import { useShop } from "./Providers";

export function Placeholder({ p }: { p: Product }) {
  const h = hueOf(p.id);
  return <div className="ph" style={{ background: `linear-gradient(135deg,hsl(${h},70%,88%),hsl(${(h + 35) % 360},65%,72%))` }}>{EMO[p.cat]}</div>;
}

/** Ghi nhớ vị trí đang xem trước khi mở trang chi tiết, để bấm quay lại thì về đúng chỗ */
function useRemember() {
  const { ret } = useShop();
  return () => { ret.current = { y: window.scrollY, url: location.pathname + location.hash }; };
}

function Card({ p }: { p: Product }) {
  const { add, toast, picks, setPick } = useShop();
  const remember = useRemember();
  const pk = picks[p.id];
  const color = pk?.c ?? defaultColor(p), size = pk?.s ?? null;
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
    setNeed(false);
    setPick(p.id, { c, s: size && p.variants.some((v) => v.color === c && v.size === size && v.stock > 0) ? size : null });
  };
  const addQuick = () => {
    if (hasSize && !size) { setNeed(true); toast("Bạn chưa chọn size. Bấm vào một size ở trên thẻ."); return; }
    if (!chosen || chosen.stock <= 0) { toast(multi ? `${lbl} này tạm hết hàng, hãy chọn ${lbl.toLowerCase()} khác` : "Sản phẩm tạm hết hàng"); return; }
    const label = [chosen.size && `Size ${chosen.size}`, multi && `${lbl} ${chosen.color}`].filter(Boolean).join(" · ");
    add({ id: chosen.id, name: p.name, label, sku: chosen.sku, price: chosen.price, stock: chosen.stock });
  };
  return (
    <article className={"card" + (need ? " need" : "")} data-pid={p.id}>
      <Link className="thumb" href={href} aria-label={`Xem ${p.name}`} onClick={remember}>
        <span className={`badge l ${cls}`}>{st}</span>
        {p.feat && <span className="badge r">Nổi bật</span>}
        {first ? <img src={first} alt={p.name} loading="lazy" /> : <Placeholder p={p} />}
      </Link>
      <div className="cinfo">
        <small>{p.cat}{p.brand && ` · ${p.brand}`}</small>
        <h3><Link href={href} className="nm" onClick={remember}>{p.name}</Link></h3>
        {multi && (
          <div className="cl" role="group" aria-label={`Chọn ${lbl.toLowerCase()}`}>
            {p.colors.map((c) => (
              <button key={c} type="button" className={"clb" + (colorStock(p, c) ? "" : " x")} data-col={c} aria-pressed={c === color} onClick={() => pickColor(c)}>{c}</button>
            ))}
          </div>
        )}
        {hasSize && (
          <div className="sz" role="group" aria-label="Chọn size">
            {sizes.map((s) => {
              const v = ofColor.find((x) => x.size === s), ok = !!v && v.stock > 0;
              return (
                <button key={s} type="button" className={"szb" + (ok ? "" : " x")} data-sz={s} aria-pressed={size === s} disabled={!ok} title={ok ? undefined : "Hết hàng"}
                  onClick={() => { setPick(p.id, { c: color, s }); setNeed(false); }}>{s}</button>
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
        {p.stock <= 0 ? <Link className="btn ghost" href={href} onClick={remember}>Xem chi tiết</Link>
          : <button type="button" className="btn" data-quick="1" onClick={addQuick}>+ Thêm vào giỏ</button>}
      </div>
    </article>
  );
}

/** Danh mục + toàn bộ sản phẩm (lọc, tìm không cần dấu, xem thêm) + banner đồng phục */
export default function Storefront({ products, updated }: { products: Product[]; updated: string }) {
  const { site, list: S, setList, ret } = useShop();
  const l = links(site);
  const grid = useRef<HTMLDivElement>(null);
  const focusFrom = useRef(-1);

  const found = useMemo(() => {
    const words = fold(S.q).split(/\s+/).filter(Boolean);
    return products
      .filter((p) => (S.cat === "Tất cả" || p.cat === S.cat) && (!S.st || (S.st === "in") === p.stock > 0) && words.every((w) => p.key.includes(w)))
      .sort((a, b) => (S.sort === "asc" ? a.min - b.min : S.sort === "desc" ? b.min - a.min : Number(b.feat) - Number(a.feat) || Number(b.stock > 0) - Number(a.stock > 0)));
  }, [products, S.cat, S.q, S.st, S.sort]);
  const shown = found.slice(0, S.limit), rest = found.length - shown.length, q = S.q.trim();

  // Quay lại từ trang chi tiết: về đúng chỗ đang xem
  useEffect(() => {
    const r = ret.current;
    ret.current = null;
    if (!r || r.url !== location.pathname + location.hash) return;
    const go = () => window.scrollTo({ top: r.y, left: 0, behavior: "instant" as ScrollBehavior });
    go(); requestAnimationFrame(go); const t = setTimeout(go, 80);
    return () => clearTimeout(t);
  }, [ret]);
  // Bấm "Xem thêm": đưa con trỏ bàn phím tới sản phẩm đầu tiên vừa hiện
  useEffect(() => {
    if (focusFrom.current < 0) return;
    (grid.current?.children[focusFrom.current]?.querySelector("a.thumb") as HTMLElement | null)?.focus();
    focusFrom.current = -1;
  }, [S.limit]);

  const set = (patch: Partial<typeof S>) => setList((s) => ({ ...s, ...patch, limit: PAGE }));
  const goCat = (c: string) => { set({ cat: c }); document.getElementById("san-pham")?.scrollIntoView({ behavior: "smooth" }); };

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
              <button key={c.name} className="cat" data-go={c.name} style={{ "--c1": c.c1, "--c2": c.c2 } as CSSProperties} onClick={() => goCat(c.name)}>
                <i>{c.emoji}</i><b>{c.name}</b><span>{n ? `${n} sản phẩm` : "Đang cập nhật"}</span>
              </button>
            );
          })}
        </div>
      </section>

      <section id="san-pham" className="sec wrap">
        <span className="eyebrow">TẤT CẢ SẢN PHẨM</span>
        <h2>Sản phẩm đang bán</h2>
        <p className="sub">Chọn size, màu rồi thêm vào giỏ; gửi danh sách cho shop qua Zalo hoặc Messenger.{updated && ` Tồn kho cập nhật ngày ${updated}.`}</p>
        <div className="tools">
          <label className="search">🔍<input id="q" type="search" placeholder="Tìm sản phẩm (vd: giày, áo, tất…)" aria-label="Tìm sản phẩm" value={S.q} onChange={(e) => set({ q: e.target.value })} /></label>
          <select className="sel" id="st" aria-label="Tình trạng" value={S.st} onChange={(e) => set({ st: e.target.value })}>
            <option value="">Mọi tình trạng</option><option value="in">Còn hàng</option><option value="out">Hết hàng</option>
          </select>
          <select className="sel" id="so" aria-label="Sắp xếp" value={S.sort} onChange={(e) => set({ sort: e.target.value })}>
            <option value="">Sắp xếp: Mặc định</option><option value="asc">Giá thấp → cao</option><option value="desc">Giá cao → thấp</option>
          </select>
        </div>
        <div className="chips">
          {["Tất cả", ...CATEGORIES.map((c) => c.name)].map((c) => (
            <button key={c} className="chip" data-c={c} aria-pressed={c === S.cat} onClick={() => set({ cat: c })}>{c === "Tất cả" ? "✨" : EMO[c]} {c}</button>
          ))}
        </div>
        <p className="count" id="cnt" aria-live="polite">{rest > 0 && `Đang xem ${shown.length}/`}{found.length} sản phẩm{S.cat !== "Tất cả" && ` trong “${S.cat}”`}{q && ` cho “${q}”`}</p>
        <div className="grid" id="grid" ref={grid}>
          {shown.length ? shown.map((p) => <Card key={p.id} p={p} />) : <p className="empty">Không tìm thấy sản phẩm phù hợp{q && ` với “${q}”`}. Thử từ khóa khác, hoặc nhắn shop để hỏi nhé.</p>}
        </div>
        <div className="more" id="more" hidden={rest <= 0}>
          <button type="button" className="btn ghost" id="moreb" onClick={() => { focusFrom.current = shown.length; setList((s) => ({ ...s, limit: s.limit + PAGE })); }}>
            Xem thêm {Math.min(PAGE, rest)} sản phẩm (còn {rest})
          </button>
        </div>
      </section>

      <section className="sec wrap">
        <div className="promo">
          <div>
            <h2>Đồng phục đội nhóm, công ty</h2>
            <p>Nhắn shop để được tư vấn mẫu áo, in tên số và báo giá theo số lượng.</p>
            <a className="btn" data-zl href={l.zalo} target="_blank" rel="noopener">💬 Nhắn Zalo tư vấn</a>
          </div>
          <div className="big" aria-hidden="true">🎽</div>
        </div>
      </section>
    </>
  );
}
