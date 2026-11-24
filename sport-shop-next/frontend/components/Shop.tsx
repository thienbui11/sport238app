"use client";
import Link from "next/link";
import { useEffect, useMemo, useRef, useState, type CSSProperties } from "react";
import { artColors, CATEGORIES, scrollMode, PRICE_RANGES, sizeKey, colorStock, defaultColor, fold, hexesIn, ICON_OF, imgsFor, links, money, optLabel, PAGE, stockStatus, unpack, type Packed, type Product } from "@/lib/shop";
import { focusSearch, searchIntent } from "./Header";
import { Art, CatIcon, Icon } from "./Icons";
import { useShop } from "./Providers";

/** Ô giữ chỗ khi CHƯA có ảnh thật: hình minh họa theo danh mục, tô theo màu đang chọn (nếu biết) */
export function Placeholder({ p, color }: { p: Product; color: string }) {
  const [c1, c2] = artColors(p, color);
  return <div className="ph"><Art kind={ICON_OF[p.cat] ?? "bag"} c1={c1} c2={c2} /></div>;
}
/** Chấm màu cạnh tên màu (chỉ khi tên màu nhận ra được) */
export const swatch = (c: string): CSSProperties | undefined => { const h = hexesIn(c)[0]; return h ? ({ "--sw": h } as CSSProperties) : undefined; };

/** Ghi nhớ vị trí đang xem trước khi mở trang chi tiết, để bấm quay lại thì về đúng chỗ */
function useRemember() {
  const { ret } = useShop();
  return () => { ret.current = { y: window.scrollY, url: location.pathname + location.hash }; };
}

/** C1: nút yêu thích (lưu trên máy khách) */
export function FavButton({ id, name, className = "" }: { id: string; name: string; className?: string }) {
  const { favs, toggleFav } = useShop();
  const on = favs.includes(id);
  return (
    <button type="button" className={"fav " + className} data-fav={id} aria-pressed={on} aria-label={on ? `Bỏ ${name} khỏi Yêu thích` : `Lưu ${name} vào Yêu thích`} onClick={() => toggleFav(id, name)}>
      <Icon n={on ? "heart-on" : "heart"} />
    </button>
  );
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
      {/* ảnh là link trùng với tên SP: ẩn với trình đọc màn hình, không dừng phím Tab */}
      <Link className="thumb" href={href} aria-hidden="true" tabIndex={-1} onClick={remember}>
        {(cls || p.feat) && (
          <span className="badges">
            {cls && <span className={`badge ${cls}`}>{st}</span>}
            {p.feat && <span className="badge r">Nổi bật</span>}
          </span>
        )}
        {first ? <img src={first} alt={p.name} loading="lazy" decoding="async" width={400} height={400} /> : <Placeholder p={p} color={color} />}
      </Link>
      <FavButton id={p.id} name={p.name} />
      <div className="cinfo">
        <small className={p.brand ? "hb" : undefined}><span className="mc">{p.cat}</span>{p.brand && <span className="mbr"><span className="sep"> · </span>{p.brand}</span>}</small>
        <h3><Link href={href} className="nm" onClick={remember}>{p.name}</Link></h3>
        <div className="price">{(lo !== hi ? "Từ " : "") + money(lo)}</div>
        {multi && (
          <div className="cl" role="group" aria-label={`Chọn ${lbl.toLowerCase()}`}>
            {p.colors.map((c) => (
              <button key={c} type="button" className={"clb" + (colorStock(p, c) ? "" : " x")} data-col={c} style={swatch(c)} aria-pressed={c === color} onClick={() => pickColor(c)}>{c}</button>
            ))}
          </div>
        )}
        {hasSize && (
          <div className="sz" role="group" aria-label="Chọn size">
            {sizes.map((s) => {
              const v = ofColor.find((x) => x.size === s), ok = !!v && v.stock > 0;
              return (
                <button key={s} type="button" className={"szb" + (ok ? "" : " x")} data-sz={s} aria-pressed={size === s} disabled={!ok} title={ok ? undefined : "Hết hàng"}
                  aria-label={ok ? `Size ${s}` : `Size ${s}, hết hàng`} onClick={() => { setPick(p.id, { c: color, s }); setNeed(false); }}>{s}</button>
              );
            })}
          </div>
        )}
        <div className={"stk" + (out ? " out" : "")}>
          {chosen
            ? chosen.stock > 0 ? <>{chosen.size && `Size ${chosen.size} · `}Còn <b>{chosen.stock}</b> sản phẩm</> : "Tạm hết hàng"
            : tot > 0 ? <>Tồn kho{multi && ` ${lbl.toLowerCase()} này`}: <b>{tot}</b> sản phẩm</> : "Tạm hết hàng"}
        </div>
        {p.stock <= 0 ? <Link className="btn ghost" href={href} onClick={remember}>Xem chi tiết</Link>
          : <button type="button" className="btn" data-quick="1" onClick={addQuick}><Icon n="cart" />Thêm vào giỏ</button>}
      </div>
    </article>
  );
}

/** Danh mục + toàn bộ sản phẩm (lọc, tìm không cần dấu, xem thêm) + khối đồng phục đội */
export default function Storefront({ data, updated }: { data: Packed; updated: string }) {
  const { site, list: S, setList, ret, favs } = useShop();
  const [fopen, setFopen] = useState(false);
  const products = useMemo(() => unpack(data), [data]);
  const l = links(site);
  const grid = useRef<HTMLDivElement>(null);
  const focusFrom = useRef(-1);

  const range = PRICE_RANGES.find((r) => r.id === S.price);
  // A6: lựa chọn lọc theo danh mục đang xem: size đang còn hàng, hãng (kèm số SP)
  const inCat = useMemo(() => products.filter((p) => S.cat === "Tất cả" || p.cat === S.cat), [products, S.cat]);
  const sizeOpts = useMemo(() => [...new Set(inCat.flatMap((p) => p.variants.filter((v) => v.size && v.stock > 0).map((v) => v.size)))].sort((a, b) => sizeKey(a) - sizeKey(b) || a.localeCompare(b)), [inCat]);
  const brandOpts = useMemo(() => Object.entries(inCat.reduce<Record<string, number>>((a, p) => { if (p.brand) a[p.brand] = (a[p.brand] ?? 0) + 1; return a; }, {})).sort((a, b) => b[1] - a[1]), [inCat]);
  const nFilter = [S.size, S.price, S.brand, S.fav].filter(Boolean).length;
  const found = useMemo(() => {
    const words = fold(S.q).split(/\s+/).filter(Boolean);
    return products
      .filter((p) => (S.cat === "Tất cả" || p.cat === S.cat) && (!S.st || (S.st === "in") === p.stock > 0) && words.every((w) => p.key.includes(w))
        && (!S.size || p.variants.some((v) => v.size === S.size && v.stock > 0))
        && (!range || p.variants.some((v) => v.price >= range.lo && v.price <= range.hi))
        && (!S.brand || p.brand === S.brand) && (!S.fav || favs.includes(p.id)))
      .sort((a, b) => (S.sort === "asc" ? a.min - b.min : S.sort === "desc" ? b.min - a.min : Number(b.feat) - Number(a.feat) || Number(b.stock > 0) - Number(a.stock > 0)));
  }, [products, S.cat, S.q, S.st, S.sort, S.size, S.brand, S.fav, range, favs]);
  const shown = found.slice(0, S.limit), rest = found.length - shown.length, q = S.q.trim();
  const perCat = useMemo(() => Object.fromEntries(CATEGORIES.map((c) => [c.name, products.filter((p) => p.cat === c.name).length])), [products]);

  // Quay lại từ trang chi tiết: về đúng chỗ đang xem
  useEffect(() => {
    const r = ret.current;
    ret.current = null;
    if (!r || r.url !== location.pathname + location.hash) return;
    const go = () => window.scrollTo({ top: r.y, left: 0, behavior: "instant" as ScrollBehavior });
    go(); requestAnimationFrame(go); const t = setTimeout(go, 80);
    return () => clearTimeout(t);
  }, [ret]);
  // Bấm nút tìm ở đầu trang khi đang ở trang khác: tới đây rồi đặt con trỏ vào ô tìm
  useEffect(() => {
    const fresh = searchIntent.at && Date.now() - searchIntent.at < 3000;
    searchIntent.at = 0;
    if (!fresh) return;
    const t = setTimeout(focusSearch, 60);
    return () => clearTimeout(t);
  }, []);
  // Bấm "Xem thêm": đưa con trỏ bàn phím tới sản phẩm đầu tiên vừa hiện
  useEffect(() => {
    if (focusFrom.current < 0) return;
    (grid.current?.children[focusFrom.current]?.querySelector("a.nm") as HTMLElement | null)?.focus();
    focusFrom.current = -1;
  }, [S.limit]);

  const set = (patch: Partial<typeof S>) => setList((s) => ({ ...s, ...patch, limit: PAGE }));
  const goCat = (c: string) => { set({ cat: c }); document.getElementById("san-pham")?.scrollIntoView({ behavior: scrollMode() }); };

  return (
    <>
      <section id="danh-muc" className="sec wrap" aria-labelledby="dm-h">
        <div className="sh"><div><h2 id="dm-h">Danh mục</h2><p className="sub">Chọn nhanh loại hàng bạn cần.</p></div></div>
        <div className="cats">
          {CATEGORIES.map((c) => (
            <button key={c.name} type="button" className="cat" data-go={c.name} onClick={() => goCat(c.name)}>
              <i><CatIcon n={c.icon} /></i><b>{c.name}</b><span>{perCat[c.name] ? `${perCat[c.name]} sản phẩm` : "Đang cập nhật"}</span>
            </button>
          ))}
        </div>
      </section>

      <section id="san-pham" className="sec wrap" aria-labelledby="sp-h">
        <div className="sh"><div><h2 id="sp-h">Sản phẩm đang bán</h2><p className="sub">Chọn size, màu rồi thêm vào giỏ.{updated && ` Tồn kho cập nhật ngày ${updated}.`}</p></div></div>
        <div className="tools">
          <label className="search"><Icon n="search" /><input id="q" type="search" placeholder="Tìm: giày, áo, tất, mã SP…" aria-label="Tìm sản phẩm" value={S.q} onChange={(e) => set({ q: e.target.value })} /></label>
          <select className="sel" id="st" aria-label="Tình trạng" value={S.st} onChange={(e) => set({ st: e.target.value })}>
            <option value="">Mọi tình trạng</option><option value="in">Còn hàng</option><option value="out">Hết hàng</option>
          </select>
          <select className="sel" id="so" aria-label="Sắp xếp" value={S.sort} onChange={(e) => set({ sort: e.target.value })}>
            <option value="">Sắp xếp</option><option value="asc">Giá thấp → cao</option><option value="desc">Giá cao → thấp</option>
          </select>
        </div>
        <div className="filters">
          <button type="button" className="fbtn" id="flt" aria-expanded={fopen} aria-controls="fpanel" onClick={() => setFopen(!fopen)}>
            <Icon n="filter" />Lọc thêm{nFilter > 0 && <b className="cnt">{nFilter}</b>}
          </button>
          <div className="fpanel" id="fpanel" data-open={fopen}>
            <select className="sel" id="fsz" aria-label="Lọc theo size còn hàng" value={S.size} onChange={(e) => set({ size: e.target.value })}>
              <option value="">Mọi size</option>{sizeOpts.map((s) => <option key={s} value={s}>Size {s} còn hàng</option>)}
            </select>
            <select className="sel" id="fgia" aria-label="Lọc theo giá" value={S.price} onChange={(e) => set({ price: e.target.value })}>
              <option value="">Mọi mức giá</option>{PRICE_RANGES.map((r) => <option key={r.id} value={r.id}>{r.label}</option>)}
            </select>
            <select className="sel" id="fhang" aria-label="Lọc theo hãng" value={S.brand} onChange={(e) => set({ brand: e.target.value })}>
              <option value="">Mọi hãng</option>{brandOpts.map(([b, n]) => <option key={b} value={b}>{b} ({n})</option>)}
            </select>
            <button type="button" className="chip" id="ffav" aria-pressed={S.fav} onClick={() => set({ fav: !S.fav })}><Icon n={S.fav ? "heart-on" : "heart"} />Yêu thích ({favs.length})</button>
            {nFilter > 0 && <button type="button" className="clr" id="fclear" onClick={() => set({ size: "", price: "", brand: "", fav: false })}>Xóa lọc</button>}
          </div>
        </div>
        <div className="chips" role="group" aria-label="Lọc theo danh mục">
          {["Tất cả", ...CATEGORIES.map((c) => c.name)].map((c) => (
            <button key={c} type="button" className="chip" data-c={c} aria-pressed={c === S.cat} onClick={() => set({ cat: c })}>{c}</button>
          ))}
        </div>
        <p className="count" id="cnt" aria-live="polite">{rest > 0 && `Đang xem ${shown.length}/`}{found.length} sản phẩm{S.cat !== "Tất cả" && ` trong “${S.cat}”`}{q && ` cho “${q}”`}{S.size && `, còn size ${S.size}`}{range && `, giá ${range.label.toLowerCase()}`}{S.brand && `, hãng ${S.brand}`}{S.fav && ", trong Yêu thích"}</p>
        <div className="grid" id="grid" ref={grid}>
          {shown.length ? shown.map((p) => <Card key={p.id} p={p} />) : <p className="empty">{S.fav && !favs.length ? "Bạn chưa lưu sản phẩm nào vào Yêu thích. Bấm hình trái tim trên sản phẩm để lưu." : <>Không tìm thấy sản phẩm phù hợp{q && ` với “${q}”`}. Thử bỏ bớt bộ lọc, hoặc nhắn shop để hỏi nhé.</>}</p>}
        </div>
        <div className="more" id="more" hidden={rest <= 0}>
          <button type="button" className="btn ghost" id="moreb" onClick={() => { focusFrom.current = shown.length; setList((s) => ({ ...s, limit: s.limit + PAGE })); }}>
            Xem thêm {Math.min(PAGE, rest)} sản phẩm (còn {rest})
          </button>
        </div>
      </section>

      <section className="sec wrap" aria-labelledby="dp-h">
        <div className="promo">
          <div>
            <h2 id="dp-h">Đồng phục đội nhóm, công ty</h2>
            <p>Chọn mẫu, số lượng theo size, danh sách in tên số rồi gửi đơn cho shop. In tên + số từ 5 bộ 15.000đ/bộ, từ 10 bộ 10.000đ/bộ.</p>
            <div className="hbtns2">
              <Link className="btn" href="/dat-doi/" id="go-dat-doi"><Icon n="tag" />Đặt đồng phục đội</Link>
              <a className="btn ghost light" data-zl href={l.zalo} target="_blank" rel="noopener"><Icon n="chat" />Nhắn Zalo tư vấn</a>
            </div>
          </div>
          <div className="kit" aria-hidden="true"><Art kind="tee" c1="#c4283f" c2="#f2f0ee" /><Art kind="tee" c1="#f5f5f3" c2="#a3122a" /></div>
        </div>
      </section>
    </>
  );
}
