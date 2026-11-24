"use client";
/* Chức năng thêm ở trang sản phẩm và trang chủ:
   A4 hỏi shop (sao chép sẵn câu hỏi), B5 chia sẻ, A5 bản đồ tải khi bấm, B4 sản phẩm cùng loại + đã xem gần đây. */
import Link from "next/link";
import { useEffect, useState } from "react";
import { hexesIn, ICON_OF } from "@/lib/shop";
import { Art, Icon } from "./Icons";
import { useShop } from "./Providers";

/** Sao chép chữ: Clipboard API, không được thì dùng ô chữ tạm + lệnh copy cũ */
export async function copyText(t: string): Promise<boolean> {
  if (navigator.clipboard && window.isSecureContext) {
    try { await navigator.clipboard.writeText(t); return true; } catch { /* dùng cách dự phòng */ }
  }
  const a = document.createElement("textarea");
  a.value = t; a.setAttribute("readonly", ""); a.style.cssText = "position:fixed;top:0;left:0;opacity:0";
  document.body.appendChild(a); a.select();
  let ok = false;
  try { ok = document.execCommand("copy"); } catch { ok = false; }
  a.remove();
  return ok;
}

/** A4: hỏi shop về sản phẩm — sao chép sẵn câu hỏi (tên, mã, size, màu, link) rồi mở Zalo/Messenger */
export function AskShop({ question }: { question: () => string }) {
  const { site, toast } = useShop();
  const go = async (where: string) => {
    const ok = await copyText(question());
    toast(ok ? `Đã sao chép câu hỏi. Trong ${where}, dán vào khung chat rồi gửi.` : `Chưa sao chép được, hãy gõ câu hỏi trong ${where}.`);
  };
  return (
    <div className="ask" role="group" aria-label="Hỏi shop về sản phẩm này">
      <a className="btn ghost" id="askz" href={`https://zalo.me/${site.zalo}`} target="_blank" rel="noopener" onClick={() => void go("Zalo")}><Icon n="chat" />Hỏi qua Zalo</a>
      <a className="btn ghost" id="askm" data-fb href={`https://m.me/${site.messenger}`} target="_blank" rel="noopener" onClick={() => void go("Messenger")}><Icon n="messenger" />Hỏi qua Messenger</a>
    </div>
  );
}

/** B5: chia sẻ sản phẩm — nút chia sẻ của điện thoại; máy không hỗ trợ thì sao chép link */
export function ShareButton({ title, text }: { title: string; text: string }) {
  const { toast } = useShop();
  const share = async () => {
    const url = location.href.split("#")[0];
    if (navigator.share) {
      try { await navigator.share({ title, text, url }); return; } catch (e) { if ((e as Error)?.name === "AbortError") return; }
    }
    toast((await copyText(url)) ? "Đã sao chép link sản phẩm. Dán vào Zalo hoặc Facebook để gửi." : "Chưa sao chép được link.");
  };
  return <button type="button" className="ib share" id="share" onClick={() => void share()} aria-label="Chia sẻ sản phẩm này"><Icon n="share" /></button>;
}

/** A5: bản đồ Google chỉ tải khi khách bấm (không làm chậm trang, không gọi Google khi chưa cần) */
export function MapEmbed({ address }: { address: string }) {
  const [on, setOn] = useState(false);
  return on
    ? <div className="map"><iframe title={`Bản đồ đường tới shop: ${address}`} src={`https://maps.google.com/maps?q=${encodeURIComponent(address)}&z=15&output=embed`} loading="lazy" referrerPolicy="no-referrer-when-downgrade" /></div>
    : <button type="button" className="btn ghost sm mapbtn" id="mapbtn" onClick={() => setOn(true)}><Icon n="map" />Xem bản đồ</button>;
}

/** Thẻ nhỏ (sản phẩm cùng loại, đã xem gần đây) */
export type Mini = { id: string; name: string; cat: string; price: string; color: string; img?: string };
export function MiniCard({ m }: { m: Mini }) {
  const hx = hexesIn(m.color).length ? hexesIn(m.color) : hexesIn(m.name);
  return (
    <Link className="mini" href={`/san-pham/${encodeURIComponent(m.id)}`} data-mini={m.id}>
      <span className="mt">{m.img ? <img src={m.img} alt="" width={160} height={160} loading="lazy" decoding="async" /> : <span className="ph"><Art kind={ICON_OF[m.cat] ?? "bag"} c1={hx[0]} c2={hx[1]} /></span>}</span>
      <span className="mn">{m.name}</span>
      <span className="mp">{m.price}</span>
    </Link>
  );
}
export function MiniRow({ id, title, items }: { id: string; title: string; items: Mini[] }) {
  if (!items.length) return null;
  return (
    <section className="minis" id={id} aria-labelledby={`${id}-h`}>
      <h2 id={`${id}-h`}>{title}</h2>
      <div className="mrow">{items.map((m) => <MiniCard key={m.id} m={m} />)}</div>
    </section>
  );
}

/** B4: đã xem gần đây — lưu trên máy khách (localStorage "daxem"), tối đa 8 sản phẩm */
const KEY = "daxem";
const readSeen = (): Mini[] => { try { const a = JSON.parse(localStorage.getItem(KEY) ?? "[]"); return Array.isArray(a) ? a.filter((x) => x && x.id && x.name) : []; } catch { return []; } };
export function useRecordView(m: Mini) {
  useEffect(() => {
    try { localStorage.setItem(KEY, JSON.stringify([m, ...readSeen().filter((x) => x.id !== m.id)].slice(0, 8))); } catch { /* máy chặn lưu trữ */ }
  }, [m]);
}
export function RecentlyViewed({ exclude, title = "Bạn đã xem gần đây" }: { exclude?: string; title?: string }) {
  const [items, setItems] = useState<Mini[]>([]);
  useEffect(() => { setItems(readSeen().filter((x) => x.id !== exclude)); }, [exclude]);
  return <MiniRow id="daxem" title={title} items={items} />;
}
