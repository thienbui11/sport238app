/* Bảng size và gợi ý size theo chiều cao, cân nặng (A3, B1).
   Dữ liệu: data/bang-size.json — chép nguyên văn từ ảnh bảng size chủ shop gửi (tai-lieu/bang-size-goc), KHÔNG tự thêm số liệu.
   Gợi ý size chỉ tra bảng (không dùng AI). Hãng không có bảng / giày: báo rõ, mời nhắn shop. */
import raw from "../data/bang-size.json";
import { fold } from "./shop";

export type ChartKind = "bang" | "ngang" | "ma-tran";
export type Chart = { nguon: string; mau: string; doi_tuong: "nguoi-lon" | "tre-em"; tieu_de: string; kieu: ChartKind; cot: string[]; hang: string[][]; ghi_chu: string[] };
export type Brand = { id: string; ten: string; khop: string[]; bang: Chart[] };

export const BRANDS = (raw as unknown as { hang_san_xuat: Brand[] }).hang_san_xuat;
export const SHOE_CATS = ["Giày bóng đá", "Giày thể thao"];
/** Danh mục quần áo có thể có bảng size */
export const APPAREL_CATS = ["Quần áo CLB/Đội tuyển", "Quần áo không logo", "Quần áo trẻ em"];

/** Hãng của sản phẩm: theo trường hãng (vendor) trước, rồi theo tên sản phẩm (nguyên chữ, không dấu) */
export function brandFor(vendor: string, name: string): Brand | undefined {
  const has = (text: string, k: string) => new RegExp(`(^|[^a-z0-9])${fold(k).replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}($|[^a-z0-9])`).test(fold(text));
  return BRANDS.find((b) => b.khop.some((k) => vendor && has(vendor, k))) ?? BRANDS.find((b) => b.khop.some((k) => has(name, k)));
}

/* ---------- đọc số liệu như in trên bảng ---------- */
type Range = [number, number];
const INF = Number.POSITIVE_INFINITY;

/** Chiều cao về cm: "1m65" → 165, "1M6" → 160, "160" / "160cm" → 160, "1,65" / "1.65" → 165 */
function heights(s: string): number[] {
  const t = s.toLowerCase();
  const out: number[] = [];
  const re = /(\d)\s*m\s*(\d{1,2})?|(\d)[.,](\d{2})(?!\d)|(\d{2,3})/g;
  for (let m; (m = re.exec(t)); ) {
    if (m[1]) out.push(+m[1] * 100 + (m[2] ? (m[2].length === 1 ? +m[2] * 10 : +m[2]) : 0));
    else if (m[3]) out.push(+m[3] * 100 + +m[4]);
    else out.push(+m[5]);
  }
  return out;
}
const weights = (s: string) => (s.match(/\d+(?:[.,]\d+)?/g) ?? []).map((x) => +x.replace(",", "."));

/** Chuỗi trên bảng → khoảng [từ, đến] (gồm cả hai đầu), hoặc số đơn lẻ (point) */
function parse(s: string, kind: "h" | "w"): { range?: Range; point?: number } | null {
  const t = fold(s);
  const n = kind === "h" ? heights(s) : weights(s);
  if (!n.length) return null;
  if (n.length >= 2) return { range: [Math.min(n[0], n[1]), Math.max(n[0], n[1])] };
  const x = n[0];
  if (/<|duoi/.test(t)) return { range: [-INF, x] };
  if (/>|tren|tro len/.test(t)) return { range: [x, INF] };
  return { point: x };
}

/** Danh sách số đơn lẻ (vd WIN: 160, 165, 170) → khoảng: ranh giới là điểm giữa hai số liền nhau */
function pointsToRanges(pts: (number | undefined)[]): (Range | undefined)[] {
  const idx = pts.map((p, i) => [p, i] as const).filter(([p]) => p !== undefined).sort((a, b) => a[0]! - b[0]!);
  const out: (Range | undefined)[] = pts.map(() => undefined);
  idx.forEach(([p, i], k) => {
    const lo = k ? (idx[k - 1][0]! + p!) / 2 : -INF, hi = k < idx.length - 1 ? (p! + idx[k + 1][0]!) / 2 : INF;
    out[i] = [lo, hi];
  });
  return out;
}

function toRanges(cells: string[], kind: "h" | "w"): (Range | undefined)[] {
  const ps = cells.map((c) => parse(c, kind));
  if (ps.some((p) => p?.point !== undefined) && !ps.some((p) => p?.range && isFinite(p.range[0]) && isFinite(p.range[1]))) {
    return pointsToRanges(ps.map((p) => p?.point ?? (p?.range ? (isFinite(p.range[0]) ? p.range[0] : p.range[1]) : undefined)));
  }
  return ps.map((p) => p?.range ?? (p?.point !== undefined ? [p.point, p.point] : undefined));
}

type Row = { size: string; h?: Range; w?: Range };
const isH = (s: string) => /chieu cao|height/.test(fold(s));
const isW = (s: string) => /can nang|weight/.test(fold(s));

/** Đưa bảng (dạng dọc hoặc ngang) về danh sách size + khoảng chiều cao + khoảng cân nặng */
export function rowsOf(c: Chart): Row[] {
  if (c.kieu === "bang") {
    const hi = c.cot.findIndex(isH), wi = c.cot.findIndex(isW);
    const hs = hi >= 0 ? toRanges(c.hang.map((r) => r[hi]), "h") : [], ws = wi >= 0 ? toRanges(c.hang.map((r) => r[wi]), "w") : [];
    return c.hang.map((r, k) => ({ size: r[0], h: hs[k], w: ws[k] }));
  }
  if (c.kieu === "ngang") {
    const hr = c.hang.find((r) => isH(r[0])), wr = c.hang.find((r) => isW(r[0]));
    const hs = hr ? toRanges(hr.slice(1), "h") : [], ws = wr ? toRanges(wr.slice(1), "w") : [];
    return c.cot.slice(1).map((size, k) => ({ size, h: hs[k], w: ws[k] }));
  }
  return [];
}

/* ---------- gợi ý ---------- */
const TOL = 3;   // lệch tối đa (cm hoặc kg) khi số đo rơi vào khoảng trống giữa hai size trên bảng
const dist = (r: Range, x: number) => (x < r[0] ? r[0] - x : x > r[1] ? x - r[1] : 0);
function fit(ranges: (Range | undefined)[], x: number): number[] {
  const ds = ranges.map((r) => (r ? dist(r, x) : INF));
  const best = Math.min(...ds);
  return best > TOL ? [] : ds.flatMap((d, i) => (d === best ? [i] : []));
}

export type Advice = { chart: Chart; size?: string; text: string; ok: boolean };
/** Hãng có ghi lời khuyên "phân vân thì chọn size lớn hơn" (AMAC, Just Play) */
const prefersLarger = (c: Chart) => c.ghi_chu.some((g) => /lon hon/.test(fold(g)));

export function advise(c: Chart, h: number, w: number): Advice {
  if (c.kieu === "ma-tran") {
    const ri = fit(c.hang.map((r) => parse(r[0], "h")?.range), h), ci = fit(c.cot.slice(1).map((x) => parse(x, "w")?.range), w);
    if (!ri.length || !ci.length) return { chart: c, ok: false, text: "Ngoài bảng size của hãng. Nhắn shop để được tư vấn." };
    const cell = c.hang[ri[ri.length - 1]][ci[ci.length - 1] + 1];
    return cell && cell !== "-" ? { chart: c, ok: true, size: cell, text: `Size ${cell}` } : { chart: c, ok: false, text: "Bảng không có size cho số đo này. Nhắn shop để được tư vấn." };
  }
  const rows = rowsOf(c);
  const byH = rows.some((r) => r.h) ? fit(rows.map((r) => r.h), h) : null;
  const byW = rows.some((r) => r.w) ? fit(rows.map((r) => r.w), w) : null;
  if ((byH && !byH.length) || (byW && !byW.length) || (!byH && !byW))
    return { chart: c, ok: false, text: "Ngoài bảng size của hãng. Nhắn shop để được tư vấn." };
  const both = byH && byW ? byH.filter((i) => byW.includes(i)) : (byH ?? byW)!;
  const name = (i: number) => rows[i].size;
  if (both.length === 1) return { chart: c, ok: true, size: name(both[0]), text: `Size ${name(both[0])}` };
  const pool = both.length ? both : [...new Set([...(byH ?? []), ...(byW ?? [])])].sort((a, b) => a - b);
  if (prefersLarger(c)) { const i = pool[pool.length - 1]; return { chart: c, ok: true, size: name(i), text: `Size ${name(i)} (hãng khuyên phân vân thì chọn size lớn hơn)` }; }
  if (!both.length && byH && byW) return { chart: c, ok: false, text: `Theo chiều cao: size ${byH.map(name).join("/")}; theo cân nặng: size ${byW.map(name).join("/")}. Nhắn shop để được tư vấn.` };
  return { chart: c, ok: false, text: `Size ${pool.map(name).join(" hoặc ")}. Phân vân thì nhắn shop để được tư vấn.` };
}

export const chartName = (b: Brand, c: Chart) => [b.ten, c.mau && c.mau !== b.ten ? c.mau : "", c.doi_tuong === "tre-em" && !/tre em/.test(fold(c.mau)) ? "trẻ em" : ""].filter(Boolean).join(" · ");
