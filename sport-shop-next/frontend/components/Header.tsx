"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { HOURS, links, phone, scrollMode } from "@/lib/shop";
import { Icon } from "./Icons";
import { useShop } from "./Providers";

const MENU: [string, string][] = [["top", "Trang chủ"], ["danh-muc", "Danh mục"], ["san-pham", "Sản phẩm"], ["ve-shop", "Về shop"], ["cach-mua", "Cách mua"]];

export const cartLabel = (n: number) => (n ? `Mở giỏ hàng, đang có ${n} món` : "Mở giỏ hàng, đang trống");

/** Lối tắt tìm kiếm: về danh sách sản phẩm và đặt con trỏ vào ô tìm.
    "at" = thời điểm bấm; quá 3 giây mà chưa tới trang chủ thì bỏ (tránh tự nhảy vào ô tìm ở lần vào sau). */
export const searchIntent = { at: 0 };
export function focusSearch() {
  const q = document.getElementById("q") as HTMLInputElement | null;
  if (!q) return false;
  document.getElementById("san-pham")?.scrollIntoView({ behavior: scrollMode() });
  q.focus({ preventScroll: true });
  return true;
}

export default function Header() {
  const { site, count, setOpen } = useShop();
  const path = usePathname();
  const router = useRouter();
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

  const search = () => {
    setMenu(false);
    if (!focusSearch()) { searchIntent.at = Date.now(); router.push("/#san-pham"); }
  };

  return (
    <>
      <aside className="strip" aria-label="Giờ mở cửa và liên hệ"><div className="wrap">
        <span className="addr" id="sad"><Icon n="pin" /> {site.address}</span>
        <span className="hrs" id="shr"><Icon n="clock" /> {HOURS.time} hằng ngày</span>
        <a href={l.page} id="sfb" target="_blank" rel="noopener">Facebook</a>
        <a href={l.zalo} id="szl" target="_blank" rel="noopener">Zalo {phone(site.zalo)}</a>
      </div></aside>
      <header className="nav" id="hdr" ref={hdr}>
        <div className="wrap">
          <Link className="logo" href="/#top" aria-label={`${site.name} – Trang chủ`}><img src="/logo-96.webp" alt="" width={42} height={42} /><span>{site.name}</span></Link>
          <nav className="menu" aria-label="Điều hướng">
            {MENU.map(([id, t]) => <Link key={id} data-s={id} href={`/#${id}`} className={active === id ? "on" : ""} aria-current={active === id ? "true" : undefined}>{t}</Link>)}
            <Link href="/bang-size/" className={path === "/bang-size/" || path === "/bang-size" ? "on" : ""}>Bảng size</Link>
          </nav>
          <div className="acts">
            <button className="ib" id="hs" type="button" onClick={search} aria-label="Tìm sản phẩm"><Icon n="search" /></button>
            <a className="hz" id="hz" data-zl href={l.zalo} target="_blank" rel="noopener"><Icon n="chat" />Nhắn Zalo</a>
            <button className="ib cartbtn" id="cb" type="button" onClick={() => setOpen(true)} aria-label={cartLabel(count)}><Icon n="cart" /><b className="cnt" id="cn" hidden={!count}>{count}</b></button>
            <button className="ib mbtn" id="mb" type="button" ref={btn} aria-expanded={menu} aria-controls="mnav" aria-label={menu ? "Đóng menu" : "Mở menu"} onClick={() => setMenu(!menu)}><Icon n={menu ? "close" : "menu"} /></button>
          </div>
        </div>
        <nav className="mnav" id="mnav" aria-label="Menu" hidden={!menu}>
          {MENU.map(([id, t]) => <Link key={id} href={`/#${id}`} onClick={() => setMenu(false)}>{t}<Icon n="right" /></Link>)}
          <Link href="/bang-size/" onClick={() => setMenu(false)}>Bảng size<Icon n="right" /></Link>
          <a className="mz" data-zl href={l.zalo} target="_blank" rel="noopener" onClick={() => setMenu(false)}><Icon n="chat" /><span>Nhắn Zalo {phone(site.zalo)}</span></a>
          <p id="mhr"><Icon n="pin" /><span>{site.address}<br />Mở cửa {HOURS.time}, {HOURS.days}</span></p>
        </nav>
      </header>
    </>
  );
}

/** Thanh dưới cùng trên điện thoại (thay cho nút Zalo nổi, không che nút nào). Trang chi tiết dùng thanh "Thêm vào giỏ" thay thế. */
export function BottomBar() {
  const { site, count, setOpen } = useShop();
  return (
    <div className="bbar" id="bbar" role="region" aria-label="Nhắn shop và giỏ hàng">
      <a data-zl href={links(site).zalo} target="_blank" rel="noopener"><Icon n="chat" />Nhắn Zalo</a>
      <button type="button" id="bc" onClick={() => setOpen(true)} aria-label={cartLabel(count)}><Icon n="cart" />Giỏ hàng <b id="bcn" hidden={!count}>{count}</b></button>
    </div>
  );
}
