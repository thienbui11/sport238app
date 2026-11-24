"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { links, phone } from "@/lib/shop";
import { useShop } from "./Providers";

const MENU: [string, string][] = [["top", "Trang chủ"], ["danh-muc", "Danh mục"], ["san-pham", "Sản phẩm"], ["ve-shop", "Về shop"], ["cach-mua", "Cách mua"]];

export default function Header() {
  const { site, count, setOpen } = useShop();
  const path = usePathname();
  const [active, setActive] = useState("top");
  const l = links(site);

  useEffect(() => {
    if (path !== "/") { setActive(""); return; }
    const io = new IntersectionObserver((es) => es.forEach((e) => e.isIntersecting && setActive(e.target.id)), { rootMargin: "-45% 0px -50% 0px" });
    MENU.forEach(([id]) => { const el = document.getElementById(id); if (el) io.observe(el); });
    return () => io.disconnect();
  }, [path]);

  return (
    <>
      <div className="strip"><div className="wrap">
        <span className="addr" id="sad">📍 {site.address}</span>
        <a href={l.page} id="sfb" target="_blank" rel="noopener">Facebook</a>
        <a href={l.zalo} id="szl" target="_blank" rel="noopener">Zalo {phone(site.zalo)}</a>
      </div></div>
      <header className="nav"><div className="wrap">
        <Link className="logo" href="/#top"><img src="/logo.png" alt="" width={42} height={42} />{site.name}</Link>
        <nav className="menu" aria-label="Điều hướng">
          {MENU.map(([id, t]) => <Link key={id} data-s={id} href={`/#${id}`} className={active === id ? "on" : ""}>{t}</Link>)}
        </nav>
        <button className="cartbtn" id="cb" onClick={() => setOpen(true)} aria-label="Mở giỏ hàng">🛒<b id="cn" hidden={!count}>{count}</b></button>
      </div></header>
    </>
  );
}
