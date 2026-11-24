"use client";
import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from "react";
import { money, type Site } from "@/lib/shop";

export type Item = { id: string; name: string; label: string; sku: string; price: number; qty: number; stock?: number };
type Ctx = {
  site: Site; items: Item[]; count: number; total: number;
  add: (i: Omit<Item, "qty">) => void; change: (id: string, d: number) => void; clear: () => void;
  open: boolean; setOpen: (v: boolean) => void; toast: (t: string) => void; orderText: () => string;
};
const C = createContext<Ctx | null>(null);
export const useShop = () => {
  const c = useContext(C);
  if (!c) throw new Error("useShop phải nằm trong <Providers>");
  return c;
};

export default function Providers({ site, children }: { site: Site; children: ReactNode }) {
  const [items, setItems] = useState<Item[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [open, setOpen] = useState(false);
  const [msg, setMsg] = useState("");
  const timer = useRef<ReturnType<typeof setTimeout>>(undefined);

  useEffect(() => {
    try { setItems(JSON.parse(localStorage.getItem("cart-s238") ?? "[]")); } catch {}
    setLoaded(true);
  }, []);
  useEffect(() => {
    if (loaded) try { localStorage.setItem("cart-s238", JSON.stringify(items)); } catch {}
  }, [items, loaded]);

  const toast = useCallback((t: string) => {
    setMsg(t);
    clearTimeout(timer.current);
    timer.current = setTimeout(() => setMsg(""), 1900);
  }, []);
  const add = (i: Omit<Item, "qty">) => {
    const cur = items.find((x) => x.id === i.id), n = i.stock ?? Infinity;
    if (n <= 0) { toast("Sản phẩm này tạm hết hàng"); return; }
    if (cur && cur.qty >= n) { toast(`Chỉ còn ${n} sản phẩm, trong giỏ đã có đủ. Nhắn shop nếu cần nhiều hơn.`); return; }
    setItems((list) => (list.some((x) => x.id === i.id) ? list.map((x) => (x.id === i.id ? { ...x, qty: x.qty + 1, stock: i.stock } : x)) : [...list, { ...i, qty: 1 }]));
    toast("Đã thêm vào giỏ hàng");
  };
  const change = (id: string, d: number) => {
    const cur = items.find((x) => x.id === id);
    if (cur && d > 0 && cur.qty >= (cur.stock ?? Infinity)) { toast(`Chỉ còn ${cur.stock} sản phẩm trong kho`); return; }
    setItems((list) => list.map((x) => (x.id === id ? { ...x, qty: x.qty + d } : x)).filter((x) => x.qty > 0));
  };
  const total = items.reduce((a, i) => a + i.price * i.qty, 0);
  const orderText = () =>
    items.length === 0
      ? "Chào shop, mình muốn hỏi về sản phẩm ạ."
      : `Chào shop, mình muốn đặt:\n${items.map((i, n) => `${n + 1}. ${i.name}${i.label ? " – " + i.label : ""} [${i.sku}] x${i.qty} = ${money(i.price * i.qty)}`).join("\n")}\nTổng: ${money(total)}\nMình sẽ ghé shop nhận hàng. Shop giữ hàng giúp mình nhé!`;

  return (
    <C.Provider value={{ site, items, count: items.reduce((a, i) => a + i.qty, 0), total, add, change, clear: () => setItems([]), open, setOpen, toast, orderText }}>
      {children}
      <div className={"toast" + (msg ? " on" : "")} role="status">{msg}</div>
    </C.Provider>
  );
}
