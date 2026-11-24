"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";
import { scrollMode, colorStock, defaultColor, HOURS, imgsFor, links, money, NEED_SIZE, optLabel, phone, priceText, sizeGroup, type Product } from "@/lib/shop";
import { cartLabel } from "./Header";
import { Icon } from "./Icons";
import { useShop } from "./Providers";
import { FavButton, Placeholder, swatch } from "./Shop";
import { SizeHelp } from "./SizeGuide";
import { AskShop, MapEmbed, MiniRow, RecentlyViewed, ShareButton, useRecordView, type Mini } from "./Extras";

/** Thư viện ảnh: vuốt ngang (scroll-snap) + ảnh nhỏ bên dưới. Chưa có ảnh thì hiện hình minh họa. */
function Gallery({ p, color }: { p: Product; color: string }) {
  const imgs = imgsFor(p, color);
  const track = useRef<HTMLDivElement>(null);
  const [i, setI] = useState(0);
  useEffect(() => { setI(0); track.current?.scrollTo({ left: 0 }); }, [color]);
  const go = (k: number) => { const t = track.current; if (t) t.scrollTo({ left: k * t.clientWidth, behavior: scrollMode() }); setI(k); };
  const onScroll = () => { const t = track.current; if (t && t.clientWidth) setI(Math.round(t.scrollLeft / t.clientWidth)); };
  return (
    <div className="gal">
      <div className={"track" + (imgs.length ? "" : " noimg")} ref={track} onScroll={imgs.length > 1 ? onScroll : undefined} tabIndex={imgs.length > 1 ? 0 : undefined}
        role={imgs.length > 1 ? "region" : undefined} aria-label={imgs.length > 1 ? `Ảnh ${p.name}, vuốt để xem thêm` : undefined}>
        {imgs.length
          ? imgs.map((u, k) => <div className="slide" key={u}><img src={u} alt={k ? `${p.name} – ảnh ${k + 1}` : p.name} width={800} height={800} loading={k ? "lazy" : "eager"} decoding="async" /></div>)
          : <div className="slide"><Placeholder p={p} color={color} /></div>}
      </div>
      {imgs.length > 1 && (
        <>
          <div className="dots" aria-hidden="true">{imgs.map((u, k) => <span key={u} className={k === i ? "on" : ""} />)}</div>
          <div className="thumbs">
            {imgs.map((u, k) => <button key={u} type="button" data-i={k} aria-pressed={k === i} aria-label={`Xem ảnh ${k + 1}`} onClick={() => go(k)}><img src={u} alt="" width={68} height={68} loading="lazy" /></button>)}
          </div>
        </>
      )}
      {!imgs.length && <p className="phnote">Hình minh họa, chưa có ảnh thật. Nhắn shop để xem ảnh sản phẩm.</p>}
    </div>
  );
}

export default function ProductDetail({ p, updated, related = [] }: { p: Product; updated: string; related?: Mini[] }) {
  const { site, add, toast, picks, setPick, ret, count, setOpen } = useShop();
  const router = useRouter();
  const l = links(site);
  const needSize = p.sizes.some(Boolean);
  const multi = p.colors.length > 1, lbl = optLabel(p);
  // Giữ màu, size khách đã chọn trên thẻ sản phẩm
  const init = picks[p.id];
  const [color, setColor] = useState(init?.c ?? defaultColor(p));
  const [size, setSize] = useState<string | null>(() => (needSize ? (init?.s && p.variants.some((x) => x.color === (init?.c ?? defaultColor(p)) && x.size === init.s) ? init.s : null) : ""));
  const [need, setNeed] = useState(false);
  const sizeBox = useRef<HTMLDivElement>(null);

  const v = p.variants.find((x) => x.color === color && x.size === size);
  const groups: Record<string, string[]> = {};
  p.sizes.filter(Boolean).forEach((s) => (groups[sizeGroup(p.cat, s)] ??= []).push(s));
  const isOut = (s: string) => { const x = p.variants.find((y) => y.color === color && y.size === s); return !x || x.stock <= 0; };
  const anyOut = p.sizes.filter(Boolean).some(isOut);
  const keep = (c: string, s: string | null) => setPick(p.id, { c, s: needSize && s && p.variants.some((x) => x.color === c && x.size === s && x.stock > 0) ? s : null });

  const pickColor = (c: string) => {
    let s = size;
    setColor(c);
    if (needSize && !p.variants.some((x) => x.color === c && x.size === size && x.stock > 0)) { s = null; setSize(null); }
    keep(c, s);
  };
  const pickSize = (s: string) => { setSize(s); setNeed(false); keep(color, s); };
  const addToCart = () => {
    if (!v) {
      if (needSize) { setNeed(true); sizeBox.current?.scrollIntoView({ behavior: scrollMode(), block: "center" }); }
      return toast(needSize ? "Bạn chưa chọn size" : "Sản phẩm tạm hết hàng");
    }
    if (v.stock <= 0) return;
    const label = [v.size && `Size ${v.size}`, multi && `${lbl} ${v.color}`].filter(Boolean).join(" · ");
    add({ id: v.id, name: p.name, label, sku: v.sku, price: v.price, stock: v.stock });
  };
  const status = !v ? (needSize ? `Tồn kho${multi ? ` ${lbl.toLowerCase()} này` : ""}: ${colorStock(p, color)} sản phẩm. Chọn size để xem từng size.` : "Tạm hết hàng")
    : v.stock <= 0 ? "Tạm hết hàng. Nhắn shop để hỏi khi nào có hàng." : `Còn ${v.stock} sản phẩm`;
  // B4: ghi lại "đã xem gần đây" (lưu trên máy khách)
  const mini = useMemo<Mini>(() => ({ id: p.id, name: p.name, cat: p.cat, price: priceText(p), color: defaultColor(p), img: imgsFor(p, defaultColor(p))[0] }), [p]);
  useRecordView(mini);
  // A4: câu hỏi sao chép sẵn cho shop
  const question = () => [
    `Chào shop, mình muốn hỏi về sản phẩm: ${p.name}`,
    [v ? `Mã ${v.sku}` : `Mã ${p.id}`, size ? `size ${size}` : "", multi ? `${lbl.toLowerCase()} ${color}` : ""].filter(Boolean).join(", "),
    location.href.split("#")[0],
  ].join(String.fromCharCode(10));
  const bad = (!!v && v.stock <= 0) || (!v && !needSize) || (!v && colorStock(p, color) <= 0);

  return (
    <div className="wrap">
      {/* Đến từ danh sách thì quay lại đúng chỗ đang xem; mở thẳng link thì về danh sách sản phẩm */}
      <Link className="back" id="bk" href="/#san-pham" onClick={(e) => { if (ret.current) { e.preventDefault(); router.back(); } }}><Icon n="left" />Tất cả sản phẩm</Link>
      <div className="det">
        <Gallery p={p} color={color} />
        <div className="pinfo">
          <div className="ttl">
            <p className="crumb"><span className="pill">{p.cat}</span>{p.brand && <span>Hãng {p.brand}</span>}</p>
            <span className="acts"><FavButton id={p.id} name={p.name} className="ib" /><ShareButton title={`${p.name} | SPORT 238`} text={`${p.name} – ${priceText(p)} tại SPORT 238`} /></span>
          </div>
          <h1>{p.name}</h1>
          <div className="bigp">{v ? money(v.price) : priceText(p)}</div>
          {multi ? (
            <div className="grp">
              <div className="lab">{lbl === "Màu" ? "Màu sắc" : "Phân loại"}: <small>{color}</small></div>
              <div className="opts">{p.colors.map((c) => {
                const n = colorStock(p, c);
                return <button key={c} type="button" className="opt" data-col={c} style={swatch(c)} aria-pressed={c === color} onClick={() => pickColor(c)}>{c}<small> {n ? `còn ${n}` : "hết"}</small></button>;
              })}</div>
            </div>
          ) : p.colors[0] !== "Mặc định" && <div className="grp"><div className="lab">{lbl === "Màu" ? "Màu sắc" : "Phân loại"}: <small>{p.colors[0]}</small></div></div>}
          {needSize && (
            <div className={"grp" + (need ? " need" : "")} ref={sizeBox}>
              {Object.entries(groups).map(([g, list]) => (
                <div key={g} className="sg">
                  <div className="lab">{g ? `Size ${g.toLowerCase()}` : "Chọn size"}</div>
                  <div className="opts">
                    {list.map((s) => {
                      const x = p.variants.find((y) => y.color === color && y.size === s), o = !x || x.stock <= 0;
                      return (
                        <button key={s} type="button" className={"opt" + (o ? " out" : "")} data-sz={s} aria-pressed={size === s} title={o ? "Tạm hết hàng" : undefined} onClick={() => pickSize(s)}>
                          {s}<small> {o ? "hết" : `còn ${x!.stock}`}</small>
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}
              {anyOut && <div className="legend">Size gạch chéo là tạm hết hàng. Bạn vẫn có thể nhắn shop để hỏi.</div>}
              <SizeHelp cat={p.cat} vendor={p.brand} name={p.name} sizes={p.sizes.filter(Boolean)} onPick={(s) => { pickSize(s); sizeBox.current?.scrollIntoView({ behavior: scrollMode(), block: "center" }); }} />
            </div>
          )}
          {!needSize && NEED_SIZE.includes(p.cat) && <div className="note">Chưa có thông tin size của sản phẩm này. Vui lòng nhắn shop để được tư vấn size.</div>}
          <div className={"st" + (bad ? " out" : "")} role="status">{status}{v && ` · Mã ${v.sku}`}</div>
          {/* Điện thoại: khối này thành thanh cố định ở đáy màn hình (Zalo, giỏ hàng, Thêm vào giỏ) */}
          <div className="buy">
            <a className="ib" data-zl href={l.zalo} target="_blank" rel="noopener" aria-label="Nhắn Zalo cho shop"><Icon n="chat" /></a>
            <button className="ib" type="button" onClick={() => setOpen(true)} aria-label={cartLabel(count)}><Icon n="cart" /><b className="cnt" hidden={!count}>{count}</b></button>
            <button className="btn" id="ad" type="button" onClick={addToCart} disabled={!!v && v.stock <= 0}><Icon n="cart" />{!!v && v.stock <= 0 ? "Tạm hết hàng" : "Thêm vào giỏ"}</button>
          </div>
          <AskShop question={question} />
          {p.desc && <p className="desc">{p.desc}</p>}
          <p className="upd">{updated && `Tồn kho cập nhật ngày ${updated}. `}Shop xác nhận còn hàng khi chốt đơn.</p>
          <section className="visit2" aria-labelledby="gs-h">
            <h2 id="gs-h"><Icon n="store" />Ghé shop nhận hàng</h2>
            <ul className="info">
              <li><Icon n="pin" /><span>{site.address}</span></li>
              <li><Icon n="clock" /><span>Mở cửa {HOURS.time}, {HOURS.days}</span></li>
              <li><Icon n="chat" /><span>Zalo {phone(site.zalo)}</span></li>
            </ul>
            <div className="row">
              <a className="btn ghost sm" data-map href={l.map} target="_blank" rel="noopener"><Icon n="map" />Chỉ đường Google Maps</a>
              <MapEmbed address={site.address} />
            </div>
          </section>
        </div>
      </div>
      <MiniRow id="lienquan" title="Sản phẩm cùng loại" items={related} />
      <RecentlyViewed exclude={p.id} />
    </div>
  );
}
