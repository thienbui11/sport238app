"use client";
import { useRouter } from "next/navigation";
import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from "react";
import { money, type Site } from "@/lib/shop";

/** Giỏ lưu giống hệt bản HTML thuần: localStorage "cart5" = [{id, lb, qty}]. Tên, mã, giá, tồn lấy từ danh mục (VM). */
type Saved = { id: string; lb: string; qty: number };
type Info = { name: string; sku: string; price: number; stock: number };
export type Item = Saved & Info;
type Ctx = {
  site: Site; items: Item[]; count: number; total: number;
  add: (i: Info & { id: string; label: string }) => void; change: (id: string, d: number) => void; clear: () => void;
  open: boolean; setOpen: (v: boolean) => void; toast: (t: string) => void; orderText: () => string;
};
const C = createContext<Ctx | null>(null);
export const useShop = () => {
  const c = useContext(C);
  if (!c) throw new Error("useShop phải nằm trong <Providers>");
  return c;
};
const KEY = "cart5";

type ApiCatalog = { products: { title: string; display_title?: string; variants: { id: string; sku?: string; price: number; inventory_quantity: number }[] }[] };
const toVM = (d: ApiCatalog) => {
  const vm: Record<string, Info> = {};
  for (const p of d.products) for (const v of p.variants) vm[v.id] = { name: p.display_title || p.title, sku: v.sku || v.id, price: v.price, stock: Math.max(0, v.inventory_quantity) };
  return vm;
};

export default function Providers({ site, children }: { site: Site; children: ReactNode }) {
  const router = useRouter();
  const [cart, setCart] = useState<Saved[]>([]);
  const [vm, setVm] = useState<Record<string, Info> | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [open, setOpen] = useState(false);
  const [msg, setMsg] = useState("");
  const [on, setOn] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout>>(undefined);

  // Đọc giỏ đã lưu, rồi lấy danh mục mới nhất để có giá, tồn kho; bỏ các món không còn bán
  useEffect(() => {
    let saved: Saved[] = [];
    try { saved = JSON.parse(localStorage.getItem(KEY) ?? "[]"); } catch {}
    if (!Array.isArray(saved)) saved = [];
    setCart(saved);
    setLoaded(true);
    fetch("/products.json").then((r) => (r.ok ? r.json() : Promise.reject())).then((d: ApiCatalog) => {
      const m = toVM(d);
      setVm((old) => ({ ...m, ...Object.fromEntries(Object.entries(old ?? {}).filter(([k]) => !m[k])) }));
      setCart((c) => c.filter((i) => m[i.id]));
    }).catch(() => setVm((old) => old ?? {}));
  }, []);
  useEffect(() => {
    if (loaded) try { localStorage.setItem(KEY, JSON.stringify(cart)); } catch {}
  }, [cart, loaded]);

  // Đường dẫn kiểu cũ của bản HTML thuần (/#p-MÃ) chuyển sang trang sản phẩm riêng
  useEffect(() => {
    const go = () => {
      const m = location.hash.match(/^#p-([\w%-]+)$/);
      if (m) router.replace(`/san-pham/${encodeURIComponent(decodeURIComponent(m[1]))}`);
    };
    go();
    window.addEventListener("hashchange", go);
    return () => window.removeEventListener("hashchange", go);
  }, [router]);

  const toast = useCallback((t: string) => {
    setMsg(t); setOn(true);
    clearTimeout(timer.current);
    timer.current = setTimeout(() => setOn(false), 1900);
  }, []);

  const info = (id: string) => vm?.[id];
  const items: Item[] = cart.flatMap((i) => { const x = info(i.id); return x ? [{ ...i, ...x }] : []; });
  const stockOf = (id: string) => info(id)?.stock ?? 0;

  const add = (i: Info & { id: string; label: string }) => {
    setVm((old) => ({ ...(old ?? {}), [i.id]: { ...(old?.[i.id] ?? {}), name: i.name, sku: i.sku, price: i.price, stock: i.stock } }));
    const cur = cart.find((x) => x.id === i.id), n = i.stock;
    if (n <= 0) { toast("Sản phẩm này tạm hết hàng"); return; }
    if (cur && cur.qty >= n) { toast(`Chỉ còn ${n} sản phẩm, trong giỏ đã có đủ. Nhắn shop nếu cần nhiều hơn.`); return; }
    setCart((list) => (list.some((x) => x.id === i.id) ? list.map((x) => (x.id === i.id ? { ...x, qty: x.qty + 1 } : x)) : [...list, { id: i.id, lb: i.label, qty: 1 }]));
    toast("Đã thêm vào giỏ hàng");
  };
  const change = (id: string, d: number) => {
    const cur = cart.find((x) => x.id === id), n = stockOf(id);
    if (cur && d > 0 && cur.qty >= n) { toast(`Chỉ còn ${n} sản phẩm trong kho`); return; }
    setCart((list) => list.map((x) => (x.id === id ? { ...x, qty: x.qty + d } : x)).filter((x) => x.qty > 0));
  };
  const total = items.reduce((a, i) => a + i.price * i.qty, 0);
  const orderText = () =>
    items.length === 0
      ? "Chào shop, mình muốn hỏi về sản phẩm ạ."
      : `Chào shop, mình muốn đặt:\n${items.map((i, n) => `${n + 1}. ${i.name}${i.lb ? " – " + i.lb : ""} [${i.sku}] x${i.qty} = ${money(i.price * i.qty)}`).join("\n")}\nTổng: ${money(total)}\nMình sẽ ghé shop nhận hàng. Shop giữ hàng giúp mình nhé!`;

  return (
    <C.Provider value={{ site, items, count: cart.reduce((a, i) => a + i.qty, 0), total, add, change, clear: () => setCart([]), open, setOpen, toast, orderText }}>
      {children}
      <div className={"toast" + (on ? " on" : "")} id="toast" role="status">{msg}</div>
    </C.Provider>
  );
}
