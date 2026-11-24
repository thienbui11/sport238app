"use client";
import { useEffect, useRef, useState } from "react";
import { HOURS, links, money, mText, OVER } from "@/lib/shop";
import { Icon } from "./Icons";
import { shareLink } from "./Extras";
import { useShop } from "./Providers";

export default function CartDrawer() {
  const { site, items, total, change, clear, open, setOpen, orderText, toast, cartLink, incoming, takeIncoming } = useShop();
  const l = links(site);
  const taRef = useRef<HTMLTextAreaElement>(null);
  const dr = useRef<HTMLDivElement>(null);
  const opener = useRef<HTMLElement | null>(null);
  const [msg, setMsg] = useState<{ ok: boolean; where: string; shared?: boolean } | null>(null);
  const [ask, setAsk] = useState(false);
  const has = items.length > 0;
  const text = has ? orderText() : "";
  const count = items.reduce((a, i) => a + i.qty, 0);

  useEffect(() => {
    const k = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
      // Tab quay vòng trong giỏ khi giỏ đang mở
      if (e.key === "Tab" && open && dr.current) {
        const f = [...dr.current.querySelectorAll<HTMLElement>("button:not([disabled]), a[href], textarea")].filter((x) => x.offsetParent !== null);
        if (!f.length) return;
        if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus(); }
        else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus(); }
      }
    };
    document.addEventListener("keydown", k);
    return () => document.removeEventListener("keydown", k);
  }, [setOpen, open]);
  useEffect(() => setMsg(null), [items.length, total]);
  useEffect(() => { if (!has) setAsk(false); }, [has]);

  // Khi giỏ mở: phần còn lại của trang không bấm/Tab được; con trỏ vào giỏ; đóng thì trả con trỏ về chỗ cũ
  useEffect(() => {
    const d = dr.current;
    if (!d) return;
    d.inert = !open;
    document.querySelectorAll<HTMLElement>("body > *").forEach((e) => { if (e !== d && e.id !== "toast" && e.id !== "veil" && e.tagName !== "SCRIPT") e.inert = open; });
    if (open) { opener.current = document.activeElement as HTMLElement; d.querySelector<HTMLElement>("#dx")?.focus(); }
    else { setAsk(false); opener.current?.focus?.(); opener.current = null; }
  }, [open]);

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
  // N1 + "không cần dán": trên điện thoại, nút Chia sẻ của máy đưa sẵn chữ đơn (và ảnh từng món nếu có) vào Zalo/Messenger,
  // khách chỉ chọn Zalo → chọn shop → Gửi. Web không thể tự dán vào khung chat Zalo (Zalo không cho), nên đây là cách gần nhất.
  // Chép chữ trước: một số ứng dụng bỏ chữ khi nhận ảnh.
  const [canShare, setCanShare] = useState(false);
  const [canFiles, setCanFiles] = useState(false);
  useEffect(() => {
    setCanShare(typeof navigator.share === "function" && matchMedia("(pointer: coarse)").matches);
    try { setCanFiles(!!navigator.canShare?.({ files: [new File([new Blob(["x"])], "a.jpg", { type: "image/jpeg" })] })); } catch { setCanFiles(false); }
  }, []);
  const withImg = canFiles ? items.filter((i) => i.img) : [];
  const shareOrder = async () => {
    const ok = await copyText(text);
    try {
      const files = await Promise.all([...new Map(withImg.map((i) => [i.img!, i])).values()].map(async (i) => {
        const b = await (await fetch(i.img!)).blob();
        return new File([b], `${i.sku}.${(b.type.split("/")[1] || "jpg").replace("jpeg", "jpg")}`, { type: b.type || "image/jpeg" });
      }));
      await navigator.share(files.length ? { files, text } : { text });
      setMsg({ ok, where: "", shared: true });
    } catch (e) {
      if ((e as Error)?.name !== "AbortError") toast("Máy chưa chia sẻ được. Hãy dùng nút Sao chép đơn & mở Zalo.");
    }
  };

  return (
    <>
      <div className={"veil" + (open ? " on" : "")} id="veil" onClick={() => setOpen(false)} />
      <div className={"drawer" + (open ? " on" : "")} id="dr" ref={dr} role="dialog" aria-modal="true" aria-labelledby="drh">
        <div className="dh">
          <h3 id="drh">Giỏ hàng {has && <small>({count} món)</small>}</h3>
          <button className="ib" id="dx" type="button" onClick={() => setOpen(false)} aria-label="Đóng giỏ hàng"><Icon n="close" /></button>
        </div>
        <div className="dl" id="dl">
          {incoming && (
            <div className="inc" id="inc" role="group" aria-labelledby="inch">
              <b id="inch"><Icon n="share" />Giỏ hàng được chia sẻ cho bạn</b>
              <ul>{incoming.items.map((i) => <li key={i.id}>{i.name}{i.lb ? ` – ${i.lb}` : ""} × {i.qty}</li>)}</ul>
              {incoming.missing > 0 && <p className="muted small">{incoming.missing} món trong link không còn bán trên web.</p>}
              <p className="small">Giỏ của bạn đang có {count} món. Bạn muốn:</p>
              <div className="incb">
                <button type="button" className="btn" id="incr" onClick={() => takeIncoming("replace")}>Thay giỏ của tôi</button>
                <button type="button" className="btn ghost" id="incm" onClick={() => takeIncoming("merge")}>Gộp vào giỏ</button>
                <button type="button" className="rm" id="incx" onClick={() => takeIncoming("skip")}>Bỏ qua</button>
              </div>
            </div>
          )}
          {!has && (
            <div className="dempty">
              <Icon n="cart" />
              <p className="empty">Giỏ hàng đang trống. Chọn size, màu rồi bấm “Thêm vào giỏ” để bắt đầu.</p>
            </div>
          )}
          {items.map((i, k) => (
            <div className="ci" key={i.id}>
              <div>
                <b>{i.name}</b>
                {i.lb && <span>{i.lb}</span>}
                <span className="lp">{money(i.price)}</span>
                {i.qty > i.stock && <div className="ow"><Icon n="warn" />{OVER} (web ghi còn {i.stock}).</div>}
              </div>
              <div className="qty">
                <button type="button" data-q="-1" data-k={k} onClick={() => change(i.id, -1)} aria-label={`Giảm số lượng ${i.name}`}><Icon n="minus" /></button>
                <span aria-label={`Số lượng ${i.qty}`}>{i.qty}</span>
                <button type="button" data-q="1" data-k={k} onClick={() => change(i.id, 1)} aria-label={`Tăng số lượng ${i.name}`}><Icon n="plus" /></button>
              </div>
              <button type="button" className="rmi" data-rm={k} onClick={() => change(i.id, -i.qty)} aria-label={`Bỏ ${i.name}${i.lb ? ` (${i.lb})` : ""} khỏi giỏ`} title="Bỏ khỏi giỏ"><Icon n="trash" /></button>
            </div>
          ))}
          {has && (
            <div className="dtools">
              {/* M8: gửi link giỏ hàng cho bạn bè, đồng đội hoặc shop (mở link là thấy đúng giỏ) */}
              <button type="button" className="rm lk" id="sharecart" hidden={ask} onClick={() => void shareLink(cartLink(), "Giỏ hàng SPORT 238 của mình", toast)}><Icon n="share" />Gửi link giỏ hàng</button>
              {/* Hỏi lại trước khi xóa giỏ */}
              <button className="rm" id="cc" type="button" hidden={ask} onClick={() => { setAsk(true); setTimeout(() => document.getElementById("ccn")?.focus(), 0); }}>Xóa giỏ hàng</button>
              <div className="ccq" id="ccq" role="group" aria-label="Xác nhận xóa giỏ hàng" hidden={!ask}>
                <span id="ccm">Xóa hết {count} món trong giỏ hàng?</span>
                <button type="button" id="ccn" onClick={() => { setAsk(false); setTimeout(() => document.getElementById("cc")?.focus(), 0); }}>Giữ lại</button>
                <button type="button" className="yes" id="ccy" onClick={() => { clear(); setAsk(false); toast("Đã xóa giỏ hàng"); document.getElementById("dx")?.focus(); }}>Xóa hết</button>
              </div>
            </div>
          )}
          <div className="ordbox" id="ordbox" hidden={!has}>
            <div className="ordh"><b>Tin nhắn gửi shop</b><button type="button" className="cpb" id="cp" onClick={() => run("")} aria-label="Sao chép đơn hàng"><Icon n="copy" />Sao chép</button></div>
            <textarea ref={taRef} id="ordtxt" readOnly rows={5} value={text} aria-label="Nội dung đơn hàng" />
            <div className={"cpok " + (msg ? (msg.ok ? "ok" : "bad") : "")} id="cpok" role="status" hidden={!msg}>
              {msg && <Icon n={msg.ok ? "check" : "warn"} />}
              <span>{msg && (msg.shared
                ? "Đơn đã được điền sẵn trong ứng dụng bạn chọn. Chọn Sport 238 rồi bấm Gửi."
                : msg.ok
                ? msg.where === "Messenger"
                  ? "Messenger đã điền sẵn đơn vào khung chat, bạn chỉ cần bấm Gửi. Nếu khung chat trống: bấm giữ rồi chọn Dán (đơn đã được sao chép)."
                  : `Đã sao chép đơn hàng. ${msg.where ? `Trong ${msg.where}, bấm vào khung chat, dán (Ctrl+V hoặc bấm giữ rồi chọn Dán) và gửi cho shop.` : "Mở Zalo hoặc Messenger, dán vào khung chat rồi gửi cho shop."}`
                : "Chưa sao chép được tự động. Hãy bấm vào khung tin nhắn ở trên, chọn hết (Ctrl+A), sao chép (Ctrl+C) rồi dán vào chat.")}</span>
            </div>
          </div>
          <div className="pick" id="dpick"><Icon n="store" /><span>Ghé shop nhận hàng: {site.address}. Mở cửa {HOURS.time} hằng ngày. Shop sẽ nhắn xác nhận và giữ hàng cho bạn.</span></div>
        </div>
        <div className="df">
          <div className="sum" hidden={!has}><span>Tạm tính</span><b id="dt">{money(total)}</b></div>
          <a className="btn" id="zs" href={l.zalo} target="_blank" rel="noopener" onClick={() => { if (has) void run("Zalo"); }}><Icon n="chat" />{has ? "Sao chép đơn & mở Zalo" : "Nhắn Zalo cho shop"}</a>
          <a className="btn ghost" id="fs" href={has ? mText(l.messenger, text) : l.messenger} target="_blank" rel="noopener" onClick={() => { if (has) void run("Messenger"); }}><Icon n="messenger" />{has ? "Mở Messenger (đơn điền sẵn)" : "Nhắn Messenger"}</a>
          {has && canShare && <button type="button" className="btn ghost" id="shareimg" onClick={() => void shareOrder()}><Icon n="share" />{withImg.length ? `Gửi đơn kèm ảnh (${withImg.length} ảnh)` : "Gửi đơn qua Zalo, Messenger… (điền sẵn)"}</button>}
        </div>
      </div>
    </>
  );
}
