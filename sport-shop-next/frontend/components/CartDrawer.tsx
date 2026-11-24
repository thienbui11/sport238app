"use client";
import { useEffect, useRef, useState } from "react";
import { links, money } from "@/lib/shop";
import { useShop } from "./Providers";

export default function CartDrawer() {
  const { site, items, total, change, clear, open, setOpen, orderText, toast } = useShop();
  const l = links(site);
  const taRef = useRef<HTMLTextAreaElement>(null);
  const [msg, setMsg] = useState<{ ok: boolean; where: string } | null>(null);
  const has = items.length > 0;
  const text = has ? orderText() : "";

  useEffect(() => {
    const k = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    document.addEventListener("keydown", k);
    return () => document.removeEventListener("keydown", k);
  }, [setOpen]);
  useEffect(() => setMsg(null), [items.length, total]);

  // Sao chép chắc chắn: dùng Clipboard API, nếu trình duyệt không cho thì chọn chữ trong khung và dùng lệnh copy cũ
  const copyText = async (t: string): Promise<boolean> => {
    const legacy = () => {
      const a = taRef.current;
      if (!a) return false;
      try { a.focus(); a.select(); a.setSelectionRange(0, t.length); const ok = document.execCommand("copy"); a.blur(); return ok; } catch { return false; }
    };
    if (navigator.clipboard && window.isSecureContext) {
      try { await navigator.clipboard.writeText(t); return true; } catch { return legacy(); }
    }
    return legacy();
  };
  const run = async (where: string) => {
    const ok = await copyText(text);
    setMsg({ ok, where });
    toast(ok ? "Đã sao chép đơn hàng" : "Chưa sao chép được, hãy sao chép thủ công");
  };

  return (
    <>
      <div className={"veil" + (open ? " on" : "")} id="veil" onClick={() => setOpen(false)} />
      <aside className={"drawer" + (open ? " on" : "")} id="dr" aria-label="Giỏ hàng">
        <div className="dh"><h3>Giỏ hàng của bạn</h3><button id="dx" onClick={() => setOpen(false)} aria-label="Đóng giỏ hàng">✕</button></div>
        <div className="dl" id="dl">
          {!has && <p className="empty" style={{ padding: "40px 0", textAlign: "center", color: "var(--muted)" }}>Giỏ hàng đang trống. Chọn vài món để bắt đầu nhé.</p>}
          {items.map((i, k) => (
            <div className="ci" key={i.id}>
              <div><b>{i.name}</b><span>{money(i.price)}{i.lb && ` · ${i.lb}`}</span></div>
              <div className="qty">
                <button data-q="-1" data-k={k} onClick={() => change(i.id, -1)} aria-label="Giảm">−</button>{i.qty}<button data-q="1" data-k={k} onClick={() => change(i.id, 1)} aria-label="Tăng">+</button>
              </div>
            </div>
          ))}
        </div>
        <div className="df">
          <div className="sum"><span>Tạm tính</span><b id="dt">{money(total)}</b></div>
          <div className="ordbox" id="ordbox" hidden={!has}>
            <div className="ordh"><b>Tin nhắn gửi cho shop</b><button type="button" className="cpb" id="cp" onClick={() => run("")}>📋 Sao chép đơn hàng</button></div>
            <textarea ref={taRef} id="ordtxt" readOnly rows={6} value={text} aria-label="Nội dung đơn hàng" />
            <div className={"cpok " + (msg ? (msg.ok ? "ok" : "bad") : "")} id="cpok" role="status" hidden={!msg}>
              {msg && (msg.ok
                ? `✓ Đã sao chép đơn hàng. ${msg.where ? `Trong ${msg.where}, bấm vào khung chat, dán (Ctrl+V hoặc bấm giữ rồi chọn Dán) và gửi cho shop.` : "Mở Zalo hoặc Messenger, dán vào khung chat rồi gửi cho shop."}`
                : "Chưa sao chép được tự động. Hãy bấm vào khung tin nhắn ở trên, chọn hết (Ctrl+A), sao chép (Ctrl+C) rồi dán vào chat.")}
            </div>
          </div>
          <div className="pick" id="dpick">📍 Ghé shop nhận hàng: {site.address}. Shop sẽ nhắn xác nhận và giữ hàng cho bạn ❤️</div>
          <a className="btn" id="zs" href={l.zalo} target="_blank" rel="noopener" onClick={() => { if (has) void run("Zalo"); }}>{has ? "📋 Sao chép đơn & mở Zalo" : "💬 Nhắn Zalo cho shop"}</a>
          <a className="btn ghost" id="fs" href={l.messenger} target="_blank" rel="noopener" onClick={() => { if (has) void run("Messenger"); }}>{has ? "Sao chép đơn & mở Messenger" : "Nhắn Messenger"}</a>
          <button className="rm" id="cc" onClick={clear}>Xóa giỏ hàng</button>
        </div>
      </aside>
    </>
  );
}
