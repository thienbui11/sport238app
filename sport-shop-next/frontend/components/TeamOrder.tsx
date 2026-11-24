"use client";
/* B2: Đặt đồng phục đội — chọn mẫu, màu, số lượng theo size, danh sách in tên + số, logo đội → tin nhắn gửi shop.
   Giá in tên + số do chủ shop xác nhận (24/11/2026): từ 5 bộ 15.000đ/bộ, từ 10 bộ 10.000đ/bộ; dưới 5 bộ shop báo giá.
   Logo đội: shop báo giá. Không thanh toán online; ghé shop nhận hàng. */
import { useMemo, useState } from "react";
import { colorStock, defaultColor, links, money, mText, PRINT_PRICES, type Product } from "@/lib/shop";
import { copyText } from "./Extras";
import { Icon } from "./Icons";
import { useShop } from "./Providers";

type Player = { name: string; num: string; size: string };
const MAX_NAME = 15;

/** Giá in tên + số mỗi bộ theo tổng số bộ; null = shop báo giá */
export function printPrice(sets: number): number | null {
  const t = PRINT_PRICES.find((x) => sets >= x.min);
  return t ? t.price : null;
}

export default function TeamOrder({ products }: { products: Product[] }) {
  const { site, toast } = useShop();
  const l = links(site);
  const [pid, setPid] = useState("");
  const p = products.find((x) => x.id === pid);
  const [color, setColor] = useState("");
  const [qty, setQty] = useState<Record<string, number>>({});
  const [print, setPrint] = useState(true);
  const [players, setPlayers] = useState<Player[]>([]);
  const [logo, setLogo] = useState(false);
  const [team, setTeam] = useState("");
  const [who, setWho] = useState("");
  const [note, setNote] = useState("");
  const [msg, setMsg] = useState<{ ok: boolean; where: string } | null>(null);

  const choose = (id: string) => {
    const x = products.find((y) => y.id === id);
    setPid(id); setColor(x ? defaultColor(x) : ""); setQty({}); setMsg(null);
  };
  const sizes = p ? p.sizes.filter(Boolean) : [];
  const variantOf = (s: string) => p?.variants.find((v) => v.color === color && v.size === s);
  const sets = sizes.reduce((a, s) => a + (qty[s] || 0), 0);
  const shirt = sizes.reduce((a, s) => a + (qty[s] || 0) * (variantOf(s)?.price ?? 0), 0);
  const unit = print ? printPrice(sets) : 0;
  const printTotal = print && unit ? unit * sets : 0;
  const over = sizes.filter((s) => (qty[s] || 0) > (variantOf(s)?.stock ?? 0));
  const named = players.filter((x) => x.name.trim() || x.num.trim());
  const dupNums = [...new Set(named.map((x) => x.num.trim()).filter((n, i, a) => n && a.indexOf(n) !== i))];

  const text = useMemo(() => {
    if (!p) return "";
    const v0 = p.variants.find((v) => v.color === color);
    const lines = [
      "Chào shop, đội mình muốn đặt đồng phục:",
      `Mẫu: ${p.name}${p.colors.length > 1 || color !== "Mặc định" ? ` – màu ${color}` : ""} [${v0?.sku ?? p.id}]`,
      `Số lượng: ${sizes.filter((s) => qty[s]).map((s) => `${s} × ${qty[s]}`).join(", ") || "chưa chọn"} (tổng ${sets} bộ)`,
      `Tiền áo (tạm tính): ${money(shirt)}`,
      print ? `In tên + số: có – ${unit ? `${sets} bộ × ${money(unit)} = ${money(printTotal)}` : "dưới 5 bộ, nhờ shop báo giá"}` : "In tên + số: không",
      ...(print && named.length ? ["Danh sách in:", ...named.map((x, i) => `${i + 1}. ${x.name.trim() || "(không tên)"} – số ${x.num.trim() || "?"} – size ${x.size || "?"}`)] : []),
      `Logo đội: ${logo ? "có (mình gửi file logo qua Zalo, nhờ shop báo giá)" : "không"}`,
      `Tạm tính: ${money(shirt + printTotal)}${(print && !unit) || logo ? " (chưa gồm phần shop báo giá)" : ""}`,
      ...(over.length ? [`Lưu ý: size ${over.join(", ")} vượt tồn kho trên web, nhờ shop kiểm tra lại.`] : []),
      ...(team.trim() ? [`Tên đội: ${team.trim()}`] : []),
      ...(who.trim() ? [`Người liên hệ: ${who.trim()}`] : []),
      ...(note.trim() ? [`Ghi chú: ${note.trim()}`] : []),
      "Mình sẽ ghé shop nhận hàng. Shop xác nhận giúp mình nhé!",
    ];
    return lines.join(String.fromCharCode(10));
  }, [p, color, qty, sets, shirt, print, unit, printTotal, named, logo, team, who, note, over, sizes]);

  const send = async (where: string) => {
    const ok = await copyText(text);
    setMsg({ ok, where });
    toast(ok ? "Đã sao chép đơn đặt đội" : "Chưa sao chép được, hãy sao chép thủ công");
  };
  const setP = (i: number, k: keyof Player, val: string) => setPlayers((a) => a.map((x, j) => (j === i ? { ...x, [k]: val } : x)));
  const groups = ["Quần áo không logo", "Quần áo CLB/Đội tuyển", "Quần áo trẻ em"].map((c) => [c, products.filter((x) => x.cat === c)] as const);

  return (
    <div className="team">
      <ol className="steps2">
        <li>
          <h2>1. Chọn mẫu áo</h2>
          <label className="fld"><span>Mẫu áo</span>
            <select className="sel" id="tm-sp" value={pid} onChange={(e) => choose(e.target.value)}>
              <option value="">— Chọn mẫu áo —</option>
              {groups.map(([c, list]) => list.length > 0 && <optgroup key={c} label={c}>{list.map((x) => <option key={x.id} value={x.id}>{x.name} – {money(x.min)}{x.stock > 0 ? "" : " (tạm hết)"}</option>)}</optgroup>)}
            </select>
          </label>
          <p className="muted small">Không thấy mẫu ưng ý? Nhắn shop để được tư vấn thêm mẫu.</p>
          {p && p.colors.length > 1 && (
            <div className="grp"><div className="lab">Màu: <small>{color}</small></div>
              <div className="opts">{p.colors.map((c) => <button key={c} type="button" className="opt" data-tcol={c} aria-pressed={c === color} onClick={() => { setColor(c); setMsg(null); }}>{c}<small> còn {colorStock(p, c)}</small></button>)}</div>
            </div>
          )}
        </li>
        {p && (
          <li>
            <h2>2. Số lượng theo size</h2>
            {sizes.length ? (
              <div className="qgrid">
                {sizes.map((s) => {
                  const v = variantOf(s), st = v?.stock ?? 0;
                  return (
                    <label key={s} className="qcell"><span>Size {s} <small>{st ? `còn ${st}` : "hết"}</small></span>
                      <input className="inp" type="number" inputMode="numeric" min={0} max={999} data-tq={s} value={qty[s] || ""} placeholder="0"
                        onChange={(e) => { const n = Math.max(0, Math.min(999, Math.floor(Number(e.target.value) || 0))); setQty((q) => ({ ...q, [s]: n })); setMsg(null); }} />
                    </label>
                  );
                })}
              </div>
            ) : <p className="note">Mẫu này chưa có thông tin size. Nhắn shop để được tư vấn.</p>}
            {over.length > 0 && <p className="ow" id="tm-over"><Icon n="warn" />Size {over.join(", ")} vượt tồn kho trên web, shop sẽ kiểm tra lại khi chốt đơn.</p>}
          </li>
        )}
        {p && (
          <li>
            <h2>3. In tên, số áo và logo</h2>
            <label className="ck"><input type="checkbox" id="tm-in" checked={print} onChange={(e) => setPrint(e.target.checked)} />In tên và số áo</label>
            {print && (
              <>
                <p className="muted small" id="tm-gia-in">Giá in tên + số: từ 5 bộ {money(PRINT_PRICES.find((x) => x.min === 5)!.price)}/bộ, từ 10 bộ {money(PRINT_PRICES.find((x) => x.min === 10)!.price)}/bộ; dưới 5 bộ shop báo giá.</p>
                <div className="plist">
                  {players.map((x, i) => (
                    <div className="prow" key={i}>
                      <label className="fld"><span>Tên in (tối đa {MAX_NAME} ký tự)</span><input className="inp" data-pn={i} maxLength={MAX_NAME} value={x.name} onChange={(e) => setP(i, "name", e.target.value.toUpperCase())} /></label>
                      <label className="fld sm"><span>Số áo</span><input className="inp" data-pnum={i} inputMode="numeric" value={x.num} onChange={(e) => setP(i, "num", e.target.value.replace(/\D/g, "").slice(0, 2))} /></label>
                      <label className="fld sm"><span>Size</span>
                        <select className="sel" data-psz={i} value={x.size} onChange={(e) => setP(i, "size", e.target.value)}><option value="">–</option>{sizes.map((s) => <option key={s}>{s}</option>)}</select>
                      </label>
                      <button type="button" className="rmi" aria-label={`Xóa cầu thủ thứ ${i + 1}`} onClick={() => setPlayers((a) => a.filter((_, j) => j !== i))}><Icon n="trash" /></button>
                    </div>
                  ))}
                </div>
                <button type="button" className="btn ghost sm" id="tm-them" onClick={() => setPlayers((a) => [...a, { name: "", num: "", size: "" }])}><Icon n="plus" />Thêm cầu thủ</button>
                {named.length > 0 && named.length !== sets && <p className="ow" id="tm-lech"><Icon n="warn" />Danh sách in có {named.length} người, số lượng áo là {sets} bộ.</p>}
                {dupNums.length > 0 && <p className="ow" id="tm-trung"><Icon n="warn" />Trùng số áo: {dupNums.join(", ")}.</p>}
              </>
            )}
            <label className="ck"><input type="checkbox" id="tm-logo" checked={logo} onChange={(e) => setLogo(e.target.checked)} />In logo đội (gửi file logo cho shop qua Zalo; shop báo giá)</label>
          </li>
        )}
        {p && (
          <li>
            <h2>4. Thông tin đội và gửi đơn</h2>
            <div className="frow">
              <label className="fld"><span>Tên đội (không bắt buộc)</span><input className="inp" id="tm-doi" value={team} onChange={(e) => setTeam(e.target.value)} /></label>
              <label className="fld"><span>Người liên hệ (không bắt buộc)</span><input className="inp" id="tm-ten" value={who} onChange={(e) => setWho(e.target.value)} /></label>
            </div>
            <label className="fld"><span>Ghi chú (không bắt buộc)</span><textarea className="inp ta" id="tm-gc" rows={2} value={note} onChange={(e) => setNote(e.target.value)} /></label>
            <div className="tsum" aria-live="polite">
              <p><span>Tổng số bộ</span><b id="tm-bo">{sets}</b></p>
              <p><span>Tiền áo (tạm tính)</span><b id="tm-ao">{money(shirt)}</b></p>
              {print && <p><span>In tên + số</span><b id="tm-in-tien">{sets === 0 ? "–" : unit ? `${money(unit)} × ${sets} = ${money(printTotal)}` : "Shop báo giá (dưới 5 bộ)"}</b></p>}
              <p className="tt"><span>Tạm tính</span><b id="tm-tong">{money(shirt + printTotal)}</b></p>
            </div>
            <textarea className="inp ta" id="tm-msg" readOnly rows={8} value={text} aria-label="Tin nhắn đặt đồng phục gửi shop" />
            {msg && <p className={"cpok " + (msg.ok ? "ok" : "bad")} role="status">{msg.ok ? (msg.where === "Messenger" ? "Messenger đã điền sẵn đơn, bạn chỉ cần bấm Gửi. Nếu khung chat trống: bấm giữ rồi chọn Dán." : `Đã sao chép. ${msg.where ? `Trong ${msg.where}, dán vào khung chat rồi gửi cho shop.` : "Mở Zalo hoặc Messenger, dán rồi gửi."}`) : "Chưa sao chép được tự động. Hãy chọn hết chữ trong khung trên, sao chép rồi dán vào chat."}</p>}
            <div className="tact">
              <a className="btn" id="tm-zalo" data-zl href={l.zalo} target="_blank" rel="noopener" onClick={(e) => { if (!sets) { e.preventDefault(); toast("Bạn chưa nhập số lượng"); return; } void send("Zalo"); }}><Icon n="chat" />Sao chép đơn & mở Zalo</a>
              <a className="btn ghost" id="tm-mess" href={sets ? mText(l.messenger, text) : l.messenger} target="_blank" rel="noopener" onClick={(e) => { if (!sets) { e.preventDefault(); toast("Bạn chưa nhập số lượng"); return; } void send("Messenger"); }}><Icon n="messenger" />Mở Messenger (đơn điền sẵn)</a>
            </div>
          </li>
        )}
      </ol>
    </div>
  );
}
