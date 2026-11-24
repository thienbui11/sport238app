"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { HOURS, links, phone } from "@/lib/shop";
import { useShop } from "./Providers";

const MENU: [string, string][] = [["top", "Trang chủ"], ["danh-muc", "Danh mục"], ["san-pham", "Sản phẩm"], ["ve-shop", "Về shop"], ["cach-mua", "Cách mua"]];
const MOBILE_MENU: [string, string][] = [["top", "🏠 Trang chủ"], ["danh-muc", "🗂️ Danh mục"], ["san-pham", "👕 Sản phẩm"], ["ve-shop", "🏬 Về shop"], ["cach-mua", "🛍️ Cách mua"]];

export const cartLabel = (n: number) => (n ? `Mở giỏ hàng, đang có ${n} món` : "Mở giỏ hàng, đang trống");

export default function Header() {
  const { site, count, setOpen } = useShop();
  const path = usePathname();
  const [active, setActive] = useState("top");
  const [menu, setMenu] = useState(false);
  const hdr = useRef<HTMLElement>(null);
  const btn = useRef<HTMLButtonElement>(null);
  const l = links(site);

  useEffect(() => {
    if (path !== "/") { setActive(""); return; }
    const io = new IntersectionObserver((es) => es.forEach((e) => e.isIntersecting && setActive(e.target.id)), { rootMargin: "-45% 0px -50% 0px" });
    MENU.forEach(([id]) => { const el = document.getElementById(id); if (el) io.observe(el); });
    return () => io.disconnect();
  }, [path]);

  // Menu điện thoại: đóng khi bấm ra ngoài, bấm Esc, đổi trang hoặc màn hình rộng ra
  useEffect(() => {
    if (!menu) return;
    const click = (e: MouseEvent) => { if (!hdr.current?.contains(e.target as Node)) setMenu(false); };
    const key = (e: KeyboardEvent) => { if (e.key === "Escape") { setMenu(false); btn.current?.focus(); } };
    const size = () => { if (window.innerWidth > 1000) setMenu(false); };
    document.addEventListener("click", click); document.addEventListener("keydown", key); window.addEventListener("resize", size);
    return () => { document.removeEventListener("click", click); document.removeEventListener("keydown", key); window.removeEventListener("resize", size); };
  }, [menu]);
  useEffect(() => setMenu(false), [path]);

  return (
    <>
      <div className="strip"><div className="wrap">
        <span className="addr" id="sad">📍 {site.address}</span>
        <span className="hrs" id="shr">🕗 {HOURS.time} hằng ngày</span>
        <a href={l.page} id="sfb" target="_blank" rel="noopener">Facebook</a>
        <a href={l.zalo} id="szl" target="_blank" rel="noopener">Zalo {phone(site.zalo)}</a>
      </div></div>
      <header className="nav" id="hdr" ref={hdr}>
        <div className="wrap">
          <Link className="logo" href="/#top"><img src="/logo.png" alt="" width={42} height={42} />{site.name}</Link>
          <nav className="menu" aria-label="Điều hướng">
            {MENU.map(([id, t]) => <Link key={id} data-s={id} href={`/#${id}`} className={active === id ? "on" : ""}>{t}</Link>)}
          </nav>
          <a className="hz" id="hz" data-zl href={l.zalo} target="_blank" rel="noopener">💬 Zalo</a>
          <button className="cartbtn" id="cb" type="button" onClick={() => setOpen(true)} aria-label={cartLabel(count)}>🛒<b id="cn" hidden={!count}>{count}</b></button>
          <button className="mbtn" id="mb" type="button" ref={btn} aria-expanded={menu} aria-controls="mnav" aria-label={menu ? "Đóng menu" : "Mở menu"} onClick={() => setMenu(!menu)}>{menu ? "✕" : "☰"}</button>
        </div>
        <nav className="mnav" id="mnav" aria-label="Menu" hidden={!menu}>
          {MOBILE_MENU.map(([id, t]) => <Link key={id} href={`/#${id}`} onClick={() => setMenu(false)}>{t}</Link>)}
          <a className="mz" data-zl href={l.zalo} target="_blank" rel="noopener" onClick={() => setMenu(false)}><span>💬 Nhắn Zalo <span className="zph">{phone(site.zalo)}</span></span></a>
          <p id="mhr">📍 {site.address} · 🕗 Mở cửa {HOURS.time} hằng ngày</p>
        </nav>
      </header>
    </>
  );
}

/** Thanh dưới cùng trên điện thoại (thay cho nút Zalo nổi, không che nút nào) */
export function BottomBar() {
  const { site, count, setOpen } = useShop();
  return (
    <div className="bbar" id="bbar">
      <a data-zl href={links(site).zalo} target="_blank" rel="noopener">💬 Nhắn Zalo</a>
      <button type="button" id="bc" onClick={() => setOpen(true)} aria-label={cartLabel(count)}>🛒 Giỏ hàng <b id="bcn" hidden={!count}>{count}</b></button>
    </div>
  );
}
