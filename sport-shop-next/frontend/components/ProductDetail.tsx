"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { colorStock, defaultColor, HOURS, imgsFor, links, money, NEED_SIZE, optLabel, priceText, sizeGroup, type Product } from "@/lib/shop";
import { useShop } from "./Providers";
import { Placeholder } from "./Shop";

export default function ProductDetail({ p, updated }: { p: Product; updated: string }) {
  const { site, add, toast, picks, setPick, ret } = useShop();
  const router = useRouter();
  const l = links(site);
  const needSize = p.sizes.some(Boolean);
  // Giữ màu, size khách đã chọn trên thẻ sản phẩm
  const init = picks[p.id];
  const [color, setColor] = useState(init?.c ?? defaultColor(p));
  const [size, setSize] = useState<string | null>(() => (needSize ? (init?.s && p.variants.some((x) => x.color === (init?.c ?? defaultColor(p)) && x.size === init.s) ? init.s : null) : ""));
  const [i, setI] = useState(0);

  const v = p.variants.find((x) => x.color === color && x.size === size);
  const imgs = imgsFor(p, color);
  const groups: Record<string, string[]> = {};
  p.sizes.filter(Boolean).forEach((s) => (groups[sizeGroup(p.cat, s)] ??= []).push(s));
  const isOut = (s: string) => { const x = p.variants.find((y) => y.color === color && y.size === s); return !x || x.stock <= 0; };
  const anyOut = p.sizes.filter(Boolean).some(isOut);
  const keep = (c: string, s: string | null) => setPick(p.id, { c, s: needSize && s && p.variants.some((x) => x.color === c && x.size === s && x.stock > 0) ? s : null });

  const pickColor = (c: string) => {
    let s = size;
    setColor(c); setI(0);
    if (needSize && !p.variants.some((x) => x.color === c && x.size === size && x.stock > 0)) { s = null; setSize(null); }
    keep(c, s);
  };
  const pickSize = (s: string) => { setSize(s); keep(color, s); };
  const addToCart = () => {
    if (!v) return toast(needSize ? "Bạn chưa chọn size" : "Sản phẩm tạm hết hàng");
    if (v.stock <= 0) return;
    const label = [v.size && `Size ${v.size}`, p.colors.length > 1 && `${optLabel(p)} ${v.color}`].filter(Boolean).join(" · ");
    add({ id: v.id, name: p.name, label, sku: v.sku, price: v.price, stock: v.stock });
  };
  const status = !v ? (needSize ? `Tồn kho${p.colors.length > 1 ? ` ${optLabel(p).toLowerCase()} này` : ""}: ${colorStock(p, color)} sản phẩm. Chọn size để xem từng size.` : "Tạm hết hàng")
    : v.stock <= 0 ? "Tạm hết hàng. Nhắn shop để hỏi khi nào có hàng." : `Còn ${v.stock} sản phẩm`;
  const bad = (!!v && v.stock <= 0) || (!v && !needSize);

  return (
    <div className="wrap">
      {/* Đến từ danh sách thì quay lại đúng chỗ đang xem; mở thẳng link thì về danh sách sản phẩm */}
      <Link className="back" id="bk" href="/#san-pham" onClick={(e) => { if (ret.current) { e.preventDefault(); router.back(); } }}>← Tất cả sản phẩm</Link>
      <div className="det">
        <div className="gal">
          <div className="main">{imgs.length ? <img src={imgs[i] ?? imgs[0]} alt={p.name} /> : <Placeholder p={p} />}</div>
          {imgs.length > 1 && (
            <div className="thumbs">
              {imgs.map((u, k) => <button key={u} data-i={k} aria-pressed={k === i} aria-label={`Ảnh ${k + 1}`} onClick={() => setI(k)}><img src={u} alt="" /></button>)}
            </div>
          )}
        </div>
        <div>
          <span className="pill">{p.cat}{p.brand && ` · ${p.brand}`}</span>
          <h1>{p.name}</h1>
          <div className="bigp">{v ? money(v.price) : priceText(p)}</div>
          {p.colors.length > 1 ? (
            <>
              <div className="lab">{optLabel(p) === "Màu" ? "Màu sắc" : "Phân loại"}: <small>{color}</small></div>
              <div className="opts">{p.colors.map((c) => {
                const n = colorStock(p, c);
                return <button key={c} className="opt" data-col={c} aria-pressed={c === color} onClick={() => pickColor(c)}>{c}<small> {n ? `còn ${n}` : "hết"}</small></button>;
              })}</div>
            </>
          ) : p.colors[0] !== "Mặc định" && <div className="lab">{optLabel(p) === "Màu" ? "Màu sắc" : "Phân loại"}: <small>{p.colors[0]}</small></div>}
          {Object.entries(groups).map(([g, list]) => (
            <div key={g}>
              <div className="lab">{g || "Chọn size"}</div>
              <div className="opts">
                {list.map((s) => {
                  const x = p.variants.find((y) => y.color === color && y.size === s), o = !x || x.stock <= 0;
                  return (
                    <button key={s} className={"opt" + (o ? " out" : "")} data-sz={s} aria-pressed={size === s} title={o ? "Tạm hết hàng" : undefined} onClick={() => pickSize(s)}>
                      {s}<small> {o ? "hết" : `còn ${x!.stock}`}</small>
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
          {anyOut && <div className="legend">Size gạch chéo là tạm hết hàng. Bạn vẫn có thể nhắn shop để hỏi.</div>}
          {!needSize && NEED_SIZE.includes(p.cat) && <div className="note">Chưa có thông tin size của sản phẩm này. Vui lòng nhắn shop để được tư vấn size.</div>}
          <div className={"st" + (bad ? " out" : "")}>{status}{v && ` · Mã ${v.sku}`}</div>
          {p.desc && <p className="desc" style={{ margin: "0 0 12px", color: "var(--ink)" }}>{p.desc}</p>}
          <p className="desc" style={{ fontSize: 13 }}>{updated && `Tồn kho cập nhật ngày ${updated}. `}Shop xác nhận còn hàng khi chốt đơn.</p>
          <button className="btn" id="ad" onClick={addToCart} disabled={!!v && v.stock <= 0}>+ Thêm vào giỏ hàng</button>
          <a className="btn ghost" data-fb href={l.messenger} target="_blank" rel="noopener">Hỏi shop về sản phẩm này</a>
          <div className="pick" style={{ marginTop: 14 }}>📍 Ghé shop nhận hàng: {site.address}<br />🕗 Mở cửa {HOURS.time}, {HOURS.days}</div>
        </div>
      </div>
    </div>
  );
}
