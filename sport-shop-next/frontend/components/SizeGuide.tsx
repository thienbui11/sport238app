"use client";
import Link from "next/link";
import { useId, useMemo, useState } from "react";
import { fold } from "@/lib/shop";
import { advise, APPAREL_CATS, BRANDS, brandFor, chartName, SHOE_CATS, type Brand, type Chart } from "@/lib/sizes";
import { Icon } from "./Icons";

/** Một bảng size, đúng như hãng in (bảng dọc, bảng ngang hoặc ma trận chiều cao × cân nặng) */
export function SizeTable({ b, c }: { b: Brand; c: Chart }) {
  const corner = c.kieu === "ma-tran" ? "Chiều cao / Cân nặng (kg)" : c.cot[0];
  const name = chartName(b, c), aud = c.doi_tuong === "tre-em" ? "Trẻ em" : "Người lớn";
  return (
    <figure className="szt">
      <figcaption><b>{name}</b>{!fold(name).includes(fold(aud)) && <span className="tag">{aud}</span>}</figcaption>
      <div className="szt-scroll" tabIndex={0} role="region" aria-label={`Bảng size ${chartName(b, c)}, vuốt ngang nếu bảng rộng`}>
        <table>
          <thead><tr>{[corner, ...c.cot.slice(1)].map((h, i) => <th key={i} scope="col">{h}</th>)}</tr></thead>
          <tbody>{c.hang.map((r, i) => <tr key={i}><th scope="row">{r[0]}</th>{r.slice(1).map((x, k) => <td key={k}>{x}</td>)}</tr>)}</tbody>
        </table>
      </div>
      {c.ghi_chu.length > 0 && <ul className="szt-notes">{c.ghi_chu.map((g) => <li key={g}>{g}</li>)}</ul>}
    </figure>
  );
}

/** Gợi ý size theo chiều cao, cân nặng: tra bảng của hãng (không dùng AI) */
export function SizeFinder({ brand, onPick, sizes }: { brand?: Brand; onPick?: (s: string) => void; sizes?: string[] }) {
  const id = useId();
  const [bid, setBid] = useState(brand?.id ?? BRANDS[0].id);
  const [h, setH] = useState("");
  const [w, setW] = useState("");
  const b = brand ?? BRANDS.find((x) => x.id === bid)!;
  const hv = Number(h), wv = Number(w);
  const valid = hv >= 60 && hv <= 230 && wv >= 8 && wv <= 200;
  const res = useMemo(() => (valid ? b.bang.map((c) => advise(c, hv, wv)) : []), [b, hv, wv, valid]);
  return (
    <div className="finder">
      <p className="fh"><Icon n="ruler" /><b>Gợi ý size theo chiều cao, cân nặng</b></p>
      <div className="frow">
        {!brand && (
          <label className="fld"><span>Hãng</span>
            <select className="sel" id={`${id}-b`} value={bid} onChange={(e) => setBid(e.target.value)}>{BRANDS.map((x) => <option key={x.id} value={x.id}>{x.ten}</option>)}</select>
          </label>
        )}
        <label className="fld"><span>Chiều cao (cm)</span><input className="inp" id={`${id}-h`} type="number" inputMode="numeric" min={60} max={230} placeholder="vd 168" value={h} onChange={(e) => setH(e.target.value)} /></label>
        <label className="fld"><span>Cân nặng (kg)</span><input className="inp" id={`${id}-w`} type="number" inputMode="numeric" min={8} max={200} placeholder="vd 62" value={w} onChange={(e) => setW(e.target.value)} /></label>
      </div>
      <div className="fres" aria-live="polite">
        {!valid && <p className="muted">Nhập chiều cao và cân nặng để xem size gợi ý của hãng {b.ten}.</p>}
        {res.map((r) => {
          const can = r.ok && r.size && sizes?.includes(r.size);
          return (
            <p key={r.chart.nguon + r.chart.tieu_de} className={"adv" + (r.ok ? " ok" : "")}>
              <span className="who">{chartName(b, r.chart)}:</span> <b>{r.text}</b>
              {can && onPick && <button type="button" className="btn sm ghost" data-pick={r.size} onClick={() => onPick(r.size!)}>Chọn size {r.size}</button>}
            </p>
          );
        })}
        {valid && <p className="muted small">Số đo trên bảng của hãng mang tính tham khảo. Phân vân thì nhắn shop để được tư vấn.</p>}
      </div>
    </div>
  );
}

/** Khối "Bảng size" ở trang sản phẩm: nút mở/đóng ngay cạnh chỗ chọn size, tự chọn đúng hãng */
export function SizeHelp({ cat, vendor, name, sizes, onPick }: { cat: string; vendor: string; name: string; sizes: string[]; onPick: (s: string) => void }) {
  const [open, setOpen] = useState(false);
  const pid = useId();
  if (SHOE_CATS.includes(cat)) return <p className="shoe-note" id="szh">Giày chưa có bảng size: bạn chọn theo size giày đang mang. Phân vân thì nhắn shop để được tư vấn.</p>;
  if (!APPAREL_CATS.includes(cat)) return null;
  const b = brandFor(vendor, name);
  return (
    <div className="szhelp" id="szh">
      <button type="button" className="szbtn" aria-expanded={open} aria-controls={pid} onClick={() => setOpen(!open)}>
        <Icon n="ruler" />Bảng size{b ? ` ${b.ten}` : ""} và gợi ý size
      </button>
      <div id={pid} className="szpanel" hidden={!open}>
        {b ? (
          <>
            <SizeFinder brand={b} sizes={sizes} onPick={(s) => { onPick(s); setOpen(false); }} />
            {b.bang.map((c) => <SizeTable key={c.nguon + c.tieu_de} b={b} c={c} />)}
          </>
        ) : (
          <p className="nochart">Chưa có bảng size của hãng {vendor || "này"}. Nhắn shop để được tư vấn size.</p>
        )}
        <p className="small"><Link href="/bang-size/">Xem bảng size của tất cả các hãng</Link></p>
      </div>
    </div>
  );
}
