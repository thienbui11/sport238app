"use client";
import { useRouter } from "next/navigation";
import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from "react";
import { money, OVER, PAGE, type Site } from "@/lib/shop";

/** Giỏ lưu giống hệt bản HTML thuần: localStorage "cart5" = [{id, lb, qty}]. Tên, mã, giá, tồn lấy từ danh mục (VM). */
type Saved = { id: string; lb: string; qty: number };
/** img: ảnh của món (theo màu), dùng để gửi đơn kèm ảnh (N1) */
type Info = { name: string; sku: string; price: number; stock: number; img?: string };
export type Item = Saved & Info;
/** Màu, size khách đã chọn cho từng sản phẩm: dùng chung cho thẻ và trang chi tiết */
export type Pick = { c: string; s: string | null };
/** Bộ lọc danh sách sản phẩm: giữ lại khi sang trang chi tiết rồi quay về */
/** size: chỉ SP còn size này · price: mã khoảng giá (PRICE_RANGES) · brand: hãng · fav: chỉ SP yêu thích */
export type ListState = { cat: string; q: string; st: string; sort: string; limit: number; size: string; price: string; brand: string; fav: boolean };
type Ctx = {
  site: Site; items: Item[]; count: number; total: number;
  add: (i: Info & { id: string; label: string }) => void; change: (id: string, d: number) => void; clear: () => void;
  open: boolean; setOpen: (v: boolean) => void; toast: (t: string) => void; orderText: () => string;
  picks: Record<string, Pick>; setPick: (id: string, p: Pick) => void;
  list: ListState; setList: (f: (s: ListState) => ListState) => void;
  /** C1: sản phẩm yêu thích (lưu trên máy khách, localStorage "yeuthich") */
  favs: string[]; toggleFav: (id: string, name: string) => void;
  /** vị trí cuộn của trang danh sách trước khi mở trang chi tiết (để quay lại đúng chỗ) */
  ret: React.MutableRefObject<{ y: number; url: string } | null>;
};
const C = createContext<Ctx | null>(null);
export const useShop = () => {
  const c = useContext(C);
  if (!c) throw new Error("useShop phải nằm trong <Providers>");
  return c;
};
const KEY = "cart5", FAV = "yeuthich";

type ApiCatalog = { products: { id: string; title: string; display_title?: string; variants: { id: string; sku?: string; option2?: string; price: number; inventory_quantity: number }[] }[]; images?: Record<string, string[]> };
const toVM = (d: ApiCatalog) => {
  const vm: Record<string, Info> = {}, im = d.images ?? {};
  for (const p of d.products) for (const v of p.variants) {
    const img = (im[`${p.id}:${v.option2}`] ?? im[p.id] ?? [])[0];
    vm[v.id] = { name: p.display_title || p.title, sku: v.sku || v.id, price: v.price, stock: Math.max(0, v.inventory_quantity), ...(img ? { img } : {}) };
  }
  return vm;
};
/** Đường dẫn ảnh đầy đủ (để shop bấm mở được từ tin nhắn) */
export const absUrl = (u: string) => (/^https?:/.test(u) || typeof window === "undefined" ? u : location.origin + u);

export default function Providers({ site, children }: { site: Site; children: ReactNode }) {
  const router = useRouter();
  const [cart, setCart] = useState<Saved[]>([]);
  const [vm, setVm] = useState<Record<string, Info> | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [open, setOpen] = useState(false);
  const [msg, setMsg] = useState("");
  const [on, setOn] = useState(false);
  const [picks, setPicks] = useState<Record<string, Pick>>({});
  const [list, setListState] = useState<ListState>({ cat: "Tất cả", q: "", st: "", sort: "", limit: PAGE, size: "", price: "", brand: "", fav: false });
  const [favs, setFavs] = useState<string[]>([]);
  const ret = useRef<{ y: number; url: string } | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout>>(undefined);

  // Đọc giỏ đã lưu, rồi lấy danh mục mới nhất để có giá, tồn kho; bỏ các món không còn bán.
  // Giỏ trống thì không tải danh mục (đỡ ~130 KB cho lần ghé đầu tiên): món thêm vào giỏ đã mang sẵn giá, tồn kho.
  useEffect(() => {
    let saved: Saved[] = [];
    try { saved = JSON.parse(localStorage.getItem(KEY) ?? "[]"); } catch {}
    if (!Array.isArray(saved)) saved = [];
    setCart(saved);
    setLoaded(true);
    if (!saved.length) { setVm((old) => old ?? {}); return; }
    fetch("/products.json").then((r) => (r.ok ? r.json() : Promise.reject())).then((d: ApiCatalog) => {
      const m = toVM(d);
      setVm((old) => ({ ...m, ...Object.fromEntries(Object.entries(old ?? {}).filter(([k]) => !m[k])) }));
      setCart((c) => c.filter((i) => m[i.id]));
    }).catch(() => setVm((old) => old ?? {}));
  }, []);
  useEffect(() => {
    if (loaded) try { localStorage.setItem(KEY, JSON.stringify(cart)); } catch {}
  }, [cart, loaded]);
  useEffect(() => {
    try { const a = JSON.parse(localStorage.getItem(FAV) ?? "[]"); if (Array.isArray(a)) setFavs(a.filter((x) => typeof x === "string")); } catch {}
  }, []);

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
    timer.current = setTimeout(() => setOn(false), t.length > 40 ? 3800 : 1900);
  }, []);

  const info = (id: string) => vm?.[id];
  const items: Item[] = cart.flatMap((i) => { const x = info(i.id); return x ? [{ ...i, ...x }] : []; });
  const stockOf = (id: string) => info(id)?.stock ?? 0;

  // Không chặn khi vượt tồn kho: vẫn thêm, cảnh báo rõ. Chỉ chặn hàng đã hết hẳn (tồn 0).
  const add = (i: Info & { id: string; label: string }) => {
    setVm((old) => ({ ...(old ?? {}), [i.id]: { ...(old?.[i.id] ?? {}), name: i.name, sku: i.sku, price: i.price, stock: i.stock, ...(i.img ? { img: i.img } : {}) } }));
    if (i.stock <= 0) { toast("Sản phẩm này tạm hết hàng"); return; }
    const qty = (cart.find((x) => x.id === i.id)?.qty ?? 0) + 1;
    setCart((list) => (list.some((x) => x.id === i.id) ? list.map((x) => (x.id === i.id ? { ...x, qty: x.qty + 1 } : x)) : [...list, { id: i.id, lb: i.label, qty: 1 }]));
    toast(qty > i.stock ? OVER : "Đã thêm vào giỏ hàng");
  };
  const change = (id: string, d: number) => {
    const cur = cart.find((x) => x.id === id);
    if (cur && d > 0 && cur.qty + d > stockOf(id)) toast(OVER);
    setCart((list) => list.map((x) => (x.id === id ? { ...x, qty: x.qty + d } : x)).filter((x) => x.qty > 0));
  };
  const total = items.reduce((a, i) => a + i.price * i.qty, 0);
  const orderText = () => {
    if (items.length === 0) return "Chào shop, mình muốn hỏi về sản phẩm ạ.";
    const over = items.some((i) => i.qty > i.stock);
    const lines = items.map((i, n) => `${n + 1}. ${i.name}${i.lb ? " – " + i.lb : ""} [${i.sku}] x${i.qty} = ${money(i.price * i.qty)}${i.qty > i.stock ? ` (vượt tồn kho trên web, web ghi còn ${i.stock})` : ""}${i.img ? `\n   Ảnh: ${absUrl(i.img)}` : ""}`);
    return `Chào shop, mình muốn đặt:\n${lines.join("\n")}${over ? "\nLưu ý: có món số lượng vượt tồn kho trên web, nhờ shop kiểm tra lại khi chốt đơn." : ""}\nTổng: ${money(total)}\nMình sẽ ghé shop nhận hàng. Shop giữ hàng giúp mình nhé!`;
  };
  const setPick = useCallback((id: string, p: Pick) => setPicks((o) => ({ ...o, [id]: p })), []);
  const setList = useCallback((f: (s: ListState) => ListState) => setListState(f), []);
  const toggleFav = (id: string, name: string) => {
    const has = favs.includes(id), next = has ? favs.filter((x) => x !== id) : [id, ...favs];
    setFavs(next);
    try { localStorage.setItem(FAV, JSON.stringify(next)); } catch {}
    toast(has ? `Đã bỏ ${name} khỏi Yêu thích` : `Đã lưu ${name} vào Yêu thích`);
  };

  return (
    <C.Provider value={{ site, items, count: cart.reduce((a, i) => a + i.qty, 0), total, add, change, clear: () => setCart([]), open, setOpen, toast, orderText, picks, setPick, list, setList, ret, favs, toggleFav }}>
      {children}
      <div className={"toast" + (on ? " on" : "")} id="toast" role="status">{msg}</div>
    </C.Provider>
  );
}
